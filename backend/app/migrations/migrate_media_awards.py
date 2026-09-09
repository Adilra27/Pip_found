"""
PIPLAD MEDIA & AWARDS MIGRATION

Migrates the Media & Awards page from the existing WordPress website
into the local SQLite database.

Source:
    https://pipladfoundation.in/media

Migrates:
    1. Photo Gallery
    2. Video Gallery (only actual videos)
    3. Projects

IMPORTANT:
    The Photo Gallery is extracted using document order:

        Photo Gallery heading
                ↓
        gallery images
                ↓
        Video Gallery heading

    We DO NOT modify/extract nodes from BeautifulSoup while iterating.
    This prevents the infinite-loop / hanging problem caused by the
    previous get_gallery_scope() implementation.

Python:
    3.13

Run:
    py -3.13 -u -m app.migrations.migrate_media_awards
"""

from __future__ import annotations

import hashlib
import mimetypes
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine, Base
from app.models import GalleryItem


# ============================================================================
# CONFIGURATION
# ============================================================================

SOURCE_URL = "https://pipladfoundation.in/media"

BASE_URL = "https://pipladfoundation.in"

MEDIA_DIR = (
    Path(__file__).resolve().parents[2]
    / "media"
    / "gallery"
)

REQUEST_TIMEOUT = 30

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL + "/",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".gif",
    ".avif",
    ".bmp",
    ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".ogg",
    ".mov",
    ".m4v",
}

IGNORED_IMAGE_PARTS = (
    "logo",
    "mechanic-visitor-counter",
    "visitor-counter",
    "favicon",
    "gravatar",
)

IGNORED_IMAGE_URL_PARTS = (
    "/wp-content/plugins/",
    "/wp-content/themes/",
)

PROJECT_TITLES = [
    "My Journey from City to Village",
    "World Mental Health Crisis",
    "विकास की होड़ ने बाढ़ को आमंत्रित किया",
    "बाढ़ राहत अभियान",
    "Be the Change, Plant a Tree",
    "The Sacred Kanwar Yatra: A Journey of Devotion and Endurance",
]


# ============================================================================
# PRINT HELPERS
# ============================================================================

def line(char="=", length=70):
    print(char * length)


def heading(title):
    print()
    line("=")
    print(title)
    line("=")


def subheading(title):
    print()
    line("-")
    print(title)
    line("-")


# ============================================================================
# HTTP SESSION
# ============================================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================================
# GENERAL HELPERS
# ============================================================================

def clean_text(value: str | None) -> str:
    if not value:
        return ""

    value = unquote(str(value))

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_url(url: str | None) -> str | None:
    if not url:
        return None

    url = str(url).strip()

    if not url:
        return None

    # Handle escaped/HTML-ish values.
    url = url.replace("&amp;", "&")

    if url.startswith("//"):
        url = "https:" + url

    return urljoin(BASE_URL, url)


def is_image_url(url: str | None) -> bool:
    if not url:
        return False

    parsed = urlparse(url)

    path = parsed.path.lower()

    extension = Path(path).suffix.lower()

    if extension in IMAGE_EXTENSIONS:
        return True

    # WordPress upload URLs can sometimes have query parameters.
    if "/wp-content/uploads/" in path:
        return True

    return False


def is_video_url(url: str | None) -> bool:
    if not url:
        return False

    parsed = urlparse(url)

    extension = Path(
        parsed.path.lower()
    ).suffix.lower()

    return extension in VIDEO_EXTENSIONS


def is_ignored_image(url: str | None) -> bool:
    if not url:
        return True

    lowered = url.lower()

    for part in IGNORED_IMAGE_PARTS:
        if part in lowered:
            return True

    for part in IGNORED_IMAGE_URL_PARTS:
        if part in lowered:
            return True

    return False


# ============================================================================
# WORDPRESS IMAGE URL HELPERS
# ============================================================================

def remove_wordpress_size_suffix(url: str) -> str:
    """
    Converts:

        image-300x175.jpg

    into:

        image.jpg

    Also handles:

        image-1024x768.jpeg
        image-768x512-1.jpg
        image-scaled.jpg
    """

    if not url:
        return url

    parsed = urlparse(url)

    filename = Path(parsed.path).name

    # Remove -300x175, -768x512, etc.
    filename = re.sub(
        r"-\d{2,5}x\d{2,5}(?=\.[^.]+$)",
        "",
        filename,
        flags=re.IGNORECASE,
    )

    # Remove -scaled.
    filename = re.sub(
        r"-scaled(?=\.[^.]+$)",
        "",
        filename,
        flags=re.IGNORECASE,
    )

    directory = parsed.path.rsplit("/", 1)[0]

    new_path = f"{directory}/{filename}"

    return parsed._replace(
        path=new_path
    ).geturl()


def get_filename_from_url(url: str) -> str:
    parsed = urlparse(url)

    filename = Path(parsed.path).name

    filename = clean_text(filename)

    if not filename:
        filename = "gallery-image"

    return filename


def make_safe_slug(value: str) -> str:
    value = clean_text(value).lower()

    value = re.sub(
        r"[^\w\s-]",
        "",
        value,
        flags=re.UNICODE,
    )

    value = re.sub(
        r"[\s_-]+",
        "-",
        value,
    )

    value = value.strip("-")

    if not value:
        value = "gallery-image"

    return value


def unique_filename(
    title: str,
    source_url: str,
) -> str:

    extension = Path(
        urlparse(source_url).path
    ).suffix.lower()

    if extension not in IMAGE_EXTENSIONS:
        extension = ".jpg"

    slug = make_safe_slug(title)

    digest = hashlib.sha256(
        source_url.encode("utf-8")
    ).hexdigest()[:10]

    return f"{slug}-{digest}{extension}"


# ============================================================================
# SRCSET / IMAGE EXTRACTION
# ============================================================================

def extract_srcset_urls(
    srcset: str | None,
) -> list[str]:

    if not srcset:
        return []

    results = []

    for item in srcset.split(","):

        item = item.strip()

        if not item:
            continue

        parts = item.split()

        if not parts:
            continue

        url = normalize_url(parts[0])

        if url:
            results.append(url)

    return results


def extract_css_background_urls(
    style: str | None,
) -> list[str]:

    if not style:
        return []

    results = []

    # Handles:
    #
    # background-image:url(...)
    # background: url(...)
    #
    pattern = re.compile(
        r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)",
        flags=re.IGNORECASE,
    )

    for match in pattern.finditer(style):

        url = normalize_url(
            match.group(1)
        )

        if url:
            results.append(url)

    return results


def extract_image_candidates(
    img: Tag,
) -> list[str]:
    """
    Extract every possible image source from a WordPress <img>.
    """

    candidates = []

    attributes = [
        "src",
        "data-src",
        "data-lazy-src",
        "data-original",
        "data-image",
        "data-lazy",
        "data-url",
        "data-flickity-lazyload",
        "data-bg",
        "data-background-image",
    ]

    for attr in attributes:

        value = img.get(attr)

        if not value:
            continue

        url = normalize_url(value)

        if url:
            candidates.append(url)

    for attr in (
        "srcset",
        "data-srcset",
        "data-lazy-srcset",
    ):

        value = img.get(attr)

        candidates.extend(
            extract_srcset_urls(value)
        )

    # CSS background image on the image itself.
    candidates.extend(
        extract_css_background_urls(
            img.get("style")
        )
    )

    # Remove duplicates.
    unique = []
    seen = set()

    for url in candidates:

        if url in seen:
            continue

        seen.add(url)

        unique.append(url)

    return unique


def choose_best_image_url(
    candidates: list[str],
) -> str | None:

    if not candidates:
        return None

    cleaned = []

    for url in candidates:

        url = remove_wordpress_size_suffix(
            url
        )

        if is_ignored_image(url):
            continue

        if not is_image_url(url):
            continue

        if url not in cleaned:
            cleaned.append(url)

    if not cleaned:
        return None

    # Prefer original/full-size URL.
    for url in cleaned:

        filename = get_filename_from_url(
            url
        )

        if not re.search(
            r"-\d{2,5}x\d{2,5}\.",
            filename,
            flags=re.IGNORECASE,
        ):
            return url

    return cleaned[0]


# ============================================================================
# TITLE / DESCRIPTION HELPERS
# ============================================================================

def extract_text_from_element(
    element,
) -> str:

    if not element:
        return ""

    try:
        return clean_text(
            element.get_text(
                " ",
                strip=True,
            )
        )
    except Exception:
        return ""


def find_nearest_image_container(
    img: Tag,
):
    """
    Find a reasonably small Elementor/gallery/card container around
    the image.

    This function ONLY reads the DOM.
    It never extracts/removes nodes.
    """

    current = img

    for _ in range(8):

        if not current:
            break

        if not isinstance(
            current,
            Tag,
        ):
            current = getattr(
                current,
                "parent",
                None,
            )
            continue

        classes = " ".join(
            current.get("class", [])
        ).lower()

        element_id = (
            current.get("id", "") or ""
        ).lower()

        if any(
            token in classes
            for token in (
                "gallery-item",
                "gallery_item",
                "gallery",
                "portfolio-item",
                "portfolio_item",
                "image-box",
                "image_box",
                "elementor-widget-image",
                "elementor-image",
                "card",
                "figure",
            )
        ):
            return current

        if (
            "gallery" in element_id
            or "portfolio" in element_id
        ):
            return current

        current = current.parent

    return img.parent


def get_image_title(
    img: Tag,
    container=None,
) -> str:
    """
    Attempts to reproduce the text associated with the image/hover.

    Priority:
        1. title
        2. data-title
        3. data-caption
        4. data-name
        5. aria-label
        6. alt
        7. parent anchor attributes
        8. caption/title nodes
        9. filename
    """

    # ---------------------------------------------------------------
    # Image attributes
    # ---------------------------------------------------------------

    attributes = [
        "title",
        "data-title",
        "data-caption",
        "data-name",
        "aria-label",
        "alt",
    ]

    for attr in attributes:

        value = clean_text(
            img.get(attr)
        )

        if value:
            return value

    # ---------------------------------------------------------------
    # Parent / nearby anchor
    # ---------------------------------------------------------------

    parent = img.parent

    for _ in range(4):

        if not parent:
            break

        if isinstance(parent, Tag):

            for attr in (
                "title",
                "data-title",
                "data-caption",
                "aria-label",
            ):

                value = clean_text(
                    parent.get(attr)
                )

                if value:
                    return value

        parent = getattr(
            parent,
            "parent",
            None,
        )

    # ---------------------------------------------------------------
    # Container text
    # ---------------------------------------------------------------

    if container:

        selectors = [
            "figcaption",
            "[class*='title']",
            "[class*='caption']",
            "[class*='overlay']",
            "[class*='content']",
            ".elementor-image-box-title",
            ".elementor-heading-title",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]

        for selector in selectors:

            try:
                node = container.select_one(
                    selector
                )
            except Exception:
                node = None

            if not node:
                continue

            text_value = (
                extract_text_from_element(
                    node
                )
            )

            if text_value:
                return text_value

    # ---------------------------------------------------------------
    # Filename fallback
    # ---------------------------------------------------------------

    source = choose_best_image_url(
        extract_image_candidates(img)
    ) or ""

    filename = get_filename_from_url(
        source
    )

    filename = Path(filename).stem

    filename = re.sub(
        r"-\d{2,5}x\d{2,5}",
        "",
        filename,
        flags=re.IGNORECASE,
    )

    filename = filename.replace(
        "-",
        " ",
    )

    filename = clean_text(filename)

    if filename:
        return filename

    return "Piplad Gallery Image"


def get_image_description(
    img: Tag,
    container=None,
) -> str:

    if container:

        selectors = [
            "figcaption",
            "[class*='description']",
            "[class*='caption']",
        ]

        for selector in selectors:

            try:
                node = container.select_one(
                    selector
                )
            except Exception:
                node = None

            if not node:
                continue

            value = extract_text_from_element(
                node
            )

            if value:
                return value

    for attr in (
        "data-description",
        "data-caption",
        "aria-description",
    ):

        value = clean_text(
            img.get(attr)
        )

        if value:
            return value

    return ""


# ============================================================================
# HEADING DETECTION
# ============================================================================

def find_heading(
    soup: BeautifulSoup,
    text_to_find: str,
):
    """
    Finds the first heading containing text_to_find.

    Handles Elementor structures such as:

        <h2>
            Photo
            <b>Gallery</b>
        </h2>
    """

    wanted = clean_text(
        text_to_find
    ).lower()

    for tag in soup.find_all(
        [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]
    ):

        text_value = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        ).lower()

        if wanted in text_value:
            return tag

    return None


# ============================================================================
# PHOTO GALLERY EXTRACTION
# ============================================================================

def extract_photo_gallery(
    soup: BeautifulSoup,
) -> list[dict]:

    heading(
        "Extracting Photo Gallery"
    )

    photo_heading = find_heading(
        soup,
        "Photo Gallery",
    )

    video_heading = find_heading(
        soup,
        "Video Gallery",
    )

    if not photo_heading:

        print(
            "ERROR: Photo Gallery heading not found."
        )

        return []

    print(
        "Photo Gallery heading found."
    )

    if video_heading:
        print(
            "Video Gallery heading found."
        )
    else:
        print(
            "WARNING: Video Gallery heading "
            "not found. Using remainder of document."
        )

    # ------------------------------------------------------------------
    # IMPORTANT:
    #
    # We DO NOT extract/remove nodes.
    #
    # We first make a static list of all document elements and then
    # determine which <img> nodes occur after Photo Gallery and before
    # Video Gallery.
    # ------------------------------------------------------------------

    all_elements = soup.find_all(True)

    photo_index = None
    video_index = None

    for index, element in enumerate(
        all_elements
    ):

        if element is photo_heading:
            photo_index = index

        if (
            video_heading
            and element is video_heading
        ):
            video_index = index

    if photo_index is None:

        print(
            "ERROR: Could not determine Photo Gallery position."
        )

        return []

    if video_index is None:

        video_index = len(
            all_elements
        )

    if video_index <= photo_index:

        print(
            "ERROR: Invalid heading order."
        )

        return []

    print(
        f"Document range: "
        f"{photo_index} -> {video_index}"
    )

    # ------------------------------------------------------------------
    # Extract <img> nodes in that range.
    # ------------------------------------------------------------------

    candidate_images = []

    for element in all_elements[
        photo_index + 1 : video_index
    ]:

        if element.name == "img":

            candidate_images.append(
                element
            )

    print(
        f"Image tags found between "
        f"Photo Gallery and Video Gallery: "
        f"{len(candidate_images)}"
    )

    items = []

    seen_urls = set()

    seen_titles = {}

    for index, img in enumerate(
        candidate_images,
        start=1,
    ):

        candidates = (
            extract_image_candidates(img)
        )

        source_url = choose_best_image_url(
            candidates
        )

        # ---------------------------------------------------------------
        # If <img> itself does not have a usable URL, inspect its
        # nearest container for CSS background images.
        # ---------------------------------------------------------------

        container = find_nearest_image_container(
            img
        )

        if not source_url and container:

            background_urls = (
                extract_css_background_urls(
                    container.get("style")
                )
            )

            source_url = choose_best_image_url(
                background_urls
            )

        if not source_url:

            continue

        source_url = (
            remove_wordpress_size_suffix(
                source_url
            )
        )

        if is_ignored_image(
            source_url
        ):

            continue

        if source_url in seen_urls:

            continue

        seen_urls.add(
            source_url
        )

        # ---------------------------------------------------------------
        # Title / hover text.
        # ---------------------------------------------------------------

        title = get_image_title(
            img,
            container,
        )

        description = get_image_description(
            img,
            container,
        )

        if not title:
            title = (
                f"Piplad Gallery Image {index}"
            )

        # ---------------------------------------------------------------
        # If multiple images have exactly the same title, keep the title
        # but make it unique in the DB so one image doesn't get skipped.
        #
        # We don't change the first occurrence.
        # ---------------------------------------------------------------

        title_count = (
            seen_titles.get(title, 0)
            + 1
        )

        seen_titles[title] = title_count

        if title_count > 1:

            title_for_db = (
                f"{title} ({title_count})"
            )

        else:

            title_for_db = title

        item = {
            "title": title_for_db,
            "description": description,
            "source_url": source_url,
        }

        items.append(
            item
        )

        print(
            f"  [{len(items):02d}] {title_for_db}"
        )

        print(
            f"       {source_url}"
        )

    # ------------------------------------------------------------------
    # SECONDARY EXTRACTION:
    #
    # Some Elementor galleries can store image URLs in anchor hrefs
    # rather than directly in <img>.
    #
    # Only inspect anchors in the Photo Gallery -> Video Gallery range.
    # ------------------------------------------------------------------

    anchor_count = 0

    for element in all_elements[
        photo_index + 1 : video_index
    ]:

        if element.name != "a":
            continue

        href = normalize_url(
            element.get("href")
        )

        if not href:
            continue

        if not is_image_url(href):
            continue

        if is_ignored_image(href):
            continue

        href = remove_wordpress_size_suffix(
            href
        )

        if href in seen_urls:
            continue

        # ---------------------------------------------------------------
        # Only consider an anchor as a gallery image if it actually
        # contains an image or image-like child.
        # ---------------------------------------------------------------

        child_img = element.find("img")

        if not child_img:
            continue

        anchor_count += 1

        seen_urls.add(
            href
        )

        title = get_image_title(
            child_img,
            element,
        )

        description = get_image_description(
            child_img,
            element,
        )

        if not title:
            title = (
                f"Piplad Gallery Image "
                f"{len(items) + 1}"
            )

        title_count = (
            seen_titles.get(title, 0)
            + 1
        )

        seen_titles[title] = title_count

        if title_count > 1:
            title_for_db = (
                f"{title} ({title_count})"
            )
        else:
            title_for_db = title

        items.append(
            {
                "title": title_for_db,
                "description": description,
                "source_url": href,
            }
        )

        print(
            f"  [{len(items):02d}] {title_for_db}"
        )

        print(
            f"       {href}"
        )

    if anchor_count:
        print(
            f"Additional gallery images found "
            f"through anchor links: {anchor_count}"
        )

    print()
    print(
        f"Found {len(items)} unique Photo Gallery images"
    )

    return items


# ============================================================================
# VIDEO GALLERY EXTRACTION
# ============================================================================

def extract_video_gallery(
    soup: BeautifulSoup,
) -> list[dict]:

    heading(
        "Extracting Video Gallery"
    )

    video_heading = find_heading(
        soup,
        "Video Gallery",
    )

    if not video_heading:

        print(
            "Video Gallery heading not found."
        )

        return []

    all_elements = soup.find_all(True)

    video_index = None

    for index, element in enumerate(
        all_elements
    ):

        if element is video_heading:

            video_index = index

            break

    if video_index is None:
        return []

    # Look at the next portion of the document.
    # Stop at Projects heading if present.

    projects_heading = find_heading(
        soup,
        "Projects",
    )

    projects_index = len(
        all_elements
    )

    if projects_heading:

        for index, element in enumerate(
            all_elements
        ):

            if element is projects_heading:

                projects_index = index

                break

    videos = []

    seen = set()

    for element in all_elements[
        video_index + 1 : projects_index
    ]:

        if element.name not in (
            "video",
            "source",
            "iframe",
            "a",
        ):
            continue

        url = (
            element.get("src")
            or element.get("data-src")
            or element.get("href")
        )

        url = normalize_url(url)

        if not url:
            continue

        lowered = url.lower()

        if not (
            is_video_url(url)
            or "youtube.com" in lowered
            or "youtu.be" in lowered
            or "vimeo.com" in lowered
        ):
            continue

        if url in seen:
            continue

        seen.add(url)

        title = clean_text(
            element.get("title")
            or element.get("aria-label")
            or element.get_text(
                " ",
                strip=True,
            )
        )

        videos.append(
            {
                "title": (
                    title
                    or "Piplad Video"
                ),
                "description": "",
                "source_url": url,
            }
        )

    if videos:

        for item in videos:

            print(
                f"  Video: {item['title']} "
                f"| {item['source_url']}"
            )

    else:

        print(
            "No actual video items migrated."
        )

    return videos


# ============================================================================
# PROJECT EXTRACTION
# ============================================================================

def extract_projects(
    soup: BeautifulSoup,
) -> list[dict]:

    heading(
        "Extracting Projects"
    )

    projects_heading = find_heading(
        soup,
        "Projects",
    )

    if not projects_heading:

        print(
            "Projects heading not found."
        )

        return []

    all_elements = soup.find_all(True)

    projects_index = None

    for index, element in enumerate(
        all_elements
    ):

        if element is projects_heading:

            projects_index = index

            break

    if projects_index is None:
        return []

    project_map = {
        clean_text(title).lower(): title
        for title in PROJECT_TITLES
    }

    projects = []

    seen = set()

    # Search only after Projects heading.
    for element in all_elements[
        projects_index + 1 :
    ]:

        if element.name != "a":
            continue

        title = clean_text(
            element.get_text(
                " ",
                strip=True,
            )
        )

        if not title:
            continue

        normalized_title = title.lower()

        matched_title = None

        for key, canonical in (
            project_map.items()
        ):

            if (
                normalized_title == key
                or key in normalized_title
                or normalized_title in key
            ):

                matched_title = canonical

                break

        if not matched_title:
            continue

        if matched_title in seen:
            continue

        href = normalize_url(
            element.get("href")
        )

        seen.add(
            matched_title
        )

        projects.append(
            {
                "title": matched_title,
                "description": "",
                "page_url": href,
                "source_url": None,
            }
        )

    print(
        f"Found {len(projects)} actual projects"
    )

    for project in projects:

        print(
            f"  - {project['title']}"
        )

        print(
            f"    Link: {project['page_url']}"
        )

    return projects


# ============================================================================
# PROJECT IMAGE EXTRACTION
# ============================================================================

def extract_project_image(
    project: dict,
) -> str | None:

    page_url = project.get(
        "page_url"
    )

    if not page_url:
        return None

    try:

        response = session.get(
            page_url,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except Exception as exc:

        print(
            f"      Could not read project page: {exc}"
        )

        return None

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # ---------------------------------------------------------------
    # OpenGraph image.
    # ---------------------------------------------------------------

    og_image = soup.find(
        "meta",
        attrs={
            "property": "og:image"
        },
    )

    if og_image:

        value = normalize_url(
            og_image.get("content")
        )

        if (
            value
            and is_image_url(value)
            and not is_ignored_image(value)
        ):

            return remove_wordpress_size_suffix(
                value
            )

    # ---------------------------------------------------------------
    # Twitter image.
    # ---------------------------------------------------------------

    twitter_image = soup.find(
        "meta",
        attrs={
            "name": "twitter:image"
        },
    )

    if twitter_image:

        value = normalize_url(
            twitter_image.get("content")
        )

        if (
            value
            and is_image_url(value)
            and not is_ignored_image(value)
        ):

            return remove_wordpress_size_suffix(
                value
            )

    # ---------------------------------------------------------------
    # First useful content image.
    # ---------------------------------------------------------------

    for img in soup.find_all("img"):

        candidates = extract_image_candidates(
            img
        )

        image_url = choose_best_image_url(
            candidates
        )

        if not image_url:
            continue

        if is_ignored_image(
            image_url
        ):
            continue

        return image_url

    return None


# ============================================================================
# IMAGE DOWNLOAD
# ============================================================================

def download_image(
    source_url: str,
    title: str,
) -> str | None:

    if not source_url:
        return None

    MEDIA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_url = (
        remove_wordpress_size_suffix(
            source_url
        )
    )

    filename = unique_filename(
        title,
        source_url,
    )

    destination = (
        MEDIA_DIR / filename
    )

    relative_url = (
        "/media/gallery/"
        + filename
    )

    if destination.exists():

        print(
            f"      Already downloaded: "
            f"{destination.name}"
        )

        return relative_url

    print(
        f"      Downloading: {source_url}"
    )

    try:

        response = session.get(
            source_url,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )

        response.raise_for_status()

        content_type = (
            response.headers.get(
                "Content-Type",
                "",
            )
            .lower()
        )

        # Reject obvious HTML responses.
        if (
            "text/html" in content_type
            and not source_url.lower().endswith(
                ".svg"
            )
        ):

            print(
                "      ERROR: Server returned "
                "HTML instead of image."
            )

            return None

        total_bytes = 0

        with open(
            destination,
            "wb",
        ) as file:

            for chunk in response.iter_content(
                chunk_size=1024 * 64
            ):

                if chunk:

                    file.write(chunk)

                    total_bytes += len(chunk)

        if total_bytes == 0:

            print(
                "      ERROR: Empty image response."
            )

            try:
                destination.unlink()
            except Exception:
                pass

            return None

        print(
            f"      Saved: {destination}"
        )

        return relative_url

    except Exception as exc:

        print(
            f"      Download failed: {exc}"
        )

        if destination.exists():

            try:
                destination.unlink()
            except Exception:
                pass

        return None


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def ensure_description_column():

    inspector = inspect(
        engine
    )

    tables = (
        inspector.get_table_names()
    )

    if "gallery_items" not in tables:
        return

    columns = {
        column["name"]
        for column in inspector.get_columns(
            "gallery_items"
        )
    }

    if "description" not in columns:

        print(
            "Adding missing "
            "gallery_items.description column..."
        )

        with engine.begin() as connection:

            connection.execute(
                text(
                    "ALTER TABLE gallery_items "
                    "ADD COLUMN description TEXT"
                )
            )

        print(
            "Description column added."
        )


def ensure_database():

    heading(
        "Ensuring database tables exist..."
    )

    Base.metadata.create_all(
        bind=engine
    )

    ensure_description_column()


def find_existing_item(
    db,
    title: str,
    category: str,
):

    return (
        db.query(GalleryItem)
        .filter(
            GalleryItem.title == title,
            GalleryItem.category == category,
        )
        .first()
    )


def find_existing_by_image_url(
    db,
    image_url: str,
):

    if not image_url:
        return None

    return (
        db.query(GalleryItem)
        .filter(
            GalleryItem.image_url == image_url
        )
        .first()
    )


# ============================================================================
# DATABASE MIGRATION - PHOTO GALLERY
# ============================================================================

def migrate_photo_gallery(
    db,
    items: list[dict],
) -> dict:

    heading(
        "MIGRATING PHOTO GALLERY"
    )

    inserted = 0
    skipped = 0
    failed = 0

    for index, item in enumerate(
        items,
        start=1,
    ):

        title = (
            item.get("title")
            or f"Piplad Gallery Image {index}"
        )

        description = (
            item.get("description")
            or ""
        )

        source_url = item.get(
            "source_url"
        )

        print()
        print(
            f"[Photo Gallery] {title}"
        )

        # ---------------------------------------------------------------
        # Existing title.
        # ---------------------------------------------------------------

        existing = find_existing_item(
            db,
            title,
            "Photo Gallery",
        )

        if existing:

            print(
                "      Database record already "
                "exists - SKIPPED"
            )

            skipped += 1

            continue

        # ---------------------------------------------------------------
        # Download.
        # ---------------------------------------------------------------

        local_url = download_image(
            source_url,
            title,
        )

        if not local_url:

            print(
                "      Image download failed - FAILED"
            )

            failed += 1

            continue

        # ---------------------------------------------------------------
        # Duplicate local image.
        # ---------------------------------------------------------------

        existing_image = (
            find_existing_by_image_url(
                db,
                local_url,
            )
        )

        if existing_image:

            print(
                "      Same image already exists - SKIPPED"
            )

            skipped += 1

            continue

        # ---------------------------------------------------------------
        # Insert.
        # ---------------------------------------------------------------

        try:

            gallery_item = GalleryItem(
                title=title,
                image_url=local_url,
                category="Photo Gallery",
                description=description,
            )

            db.add(
                gallery_item
            )

            db.commit()

            print(
                "      Database record created"
            )

            inserted += 1

        except IntegrityError as exc:

            db.rollback()

            print(
                f"      Database error - {exc}"
            )

            failed += 1

        except Exception as exc:

            db.rollback()

            print(
                f"      Unexpected database error - {exc}"
            )

            failed += 1

    return {
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
    }


# ============================================================================
# DATABASE MIGRATION - PROJECTS
# ============================================================================

def migrate_projects(
    db,
    projects: list[dict],
) -> dict:

    heading(
        "MIGRATING PROJECTS"
    )

    inserted = 0
    skipped = 0
    failed = 0

    for project in projects:

        title = project["title"]

        print()
        print(
            f"[Projects] {title}"
        )

        existing = find_existing_item(
            db,
            title,
            "Projects",
        )

        if existing:

            print(
                "      Database record already "
                "exists - SKIPPED"
            )

            skipped += 1

            continue

        print(
            "      Reading project page: "
            f"{project.get('page_url')}"
        )

        image_url = extract_project_image(
            project
        )

        if not image_url:

            print(
                "      No project image found - SKIPPED"
            )

            skipped += 1

            continue

        print(
            f"      Found project image: {image_url}"
        )

        local_url = download_image(
            image_url,
            title,
        )

        if not local_url:

            print(
                "      Image download failed - FAILED"
            )

            failed += 1

            continue

        try:

            gallery_item = GalleryItem(
                title=title,
                image_url=local_url,
                category="Projects",
                description=project.get(
                    "description",
                    "",
                ),
            )

            db.add(
                gallery_item
            )

            db.commit()

            print(
                "      Database record created"
            )

            inserted += 1

        except IntegrityError as exc:

            db.rollback()

            print(
                f"      Database error - {exc}"
            )

            failed += 1

        except Exception as exc:

            db.rollback()

            print(
                f"      Unexpected database error - {exc}"
            )

            failed += 1

    return {
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
    }


# ============================================================================
# DATABASE MIGRATION - VIDEO GALLERY
# ============================================================================

def migrate_videos(
    db,
    videos: list[dict],
) -> dict:

    heading(
        "MIGRATING VIDEO GALLERY"
    )

    inserted = 0
    skipped = 0
    failed = 0

    for video in videos:

        title = (
            video.get("title")
            or "Piplad Video"
        )

        source_url = video.get(
            "source_url"
        )

        print()
        print(
            f"[Video Gallery] {title}"
        )

        print(
            f"      Source: {source_url}"
        )

        # Current GalleryItem model is image-oriented.
        # Do not force external video URLs into image_url.

        print(
            "      Video migration skipped "
            "(no dedicated video field in GalleryItem)"
        )

        skipped += 1

    return {
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
    }


# ============================================================================
# MAIN MIGRATION
# ============================================================================

def migrate():

    heading(
        "PIPLAD MEDIA & AWARDS MIGRATION"
    )

    ensure_database()

    # ------------------------------------------------------------------
    # DOWNLOAD SOURCE PAGE
    # ------------------------------------------------------------------

    heading(
        "Downloading source Media & Awards page"
    )

    try:

        response = session.get(
            SOURCE_URL,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

    except Exception as exc:

        print()
        print(
            "ERROR: Could not download source page."
        )

        print(
            exc
        )

        sys.exit(1)

    print(
        f"Source page downloaded: "
        f"{len(response.content)} bytes"
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # ------------------------------------------------------------------
    # BASIC PAGE DIAGNOSTICS
    # ------------------------------------------------------------------

    print()
    print(
        f"HTML <img> count: "
        f"{len(soup.find_all('img'))}"
    )

    print(
        f"HTML <a> count: "
        f"{len(soup.find_all('a'))}"
    )

    # ------------------------------------------------------------------
    # EXTRACT PHOTO GALLERY
    # ------------------------------------------------------------------

    photo_items = extract_photo_gallery(
        soup
    )

    # ------------------------------------------------------------------
    # EXTRACT VIDEO GALLERY
    # ------------------------------------------------------------------

    video_items = extract_video_gallery(
        soup
    )

    # ------------------------------------------------------------------
    # EXTRACT PROJECTS
    # ------------------------------------------------------------------

    projects = extract_projects(
        soup
    )

    # ------------------------------------------------------------------
    # PROJECT IMAGES
    # ------------------------------------------------------------------

    heading(
        "Resolving project images"
    )

    for project in projects:

        print()
        print(
            "Finding image for project: "
            f"{project['title']}"
        )

        image_url = extract_project_image(
            project
        )

        if image_url:

            project["source_url"] = (
                image_url
            )

            print(
                "      Found project image: "
                f"{image_url}"
            )

        else:

            print(
                "      No project image found"
            )

        time.sleep(0.2)

    # Only projects with actual images.
    projects = [
        project
        for project in projects
        if project.get("source_url")
    ]

    print()
    print(
        f"Found {len(projects)} actual projects"
    )

    # ------------------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------------------

    heading(
        "MIGRATION SUMMARY"
    )

    print(
        f"Photo Gallery images: "
        f"{len(photo_items)}"
    )

    print(
        f"Video Gallery items: "
        f"{len(video_items)}"
    )

    print(
        f"Projects: "
        f"{len(projects)}"
    )

    print(
        f"Total items: "
        f"{len(photo_items) + len(projects)}"
    )

    # ------------------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------------------

    db = SessionLocal()

    photo_result = {
        "inserted": 0,
        "skipped": 0,
        "failed": 0,
    }

    project_result = {
        "inserted": 0,
        "skipped": 0,
        "failed": 0,
    }

    video_result = {
        "inserted": 0,
        "skipped": 0,
        "failed": 0,
    }

    try:

        photo_result = migrate_photo_gallery(
            db,
            photo_items,
        )

        project_result = migrate_projects(
            db,
            projects,
        )

        video_result = migrate_videos(
            db,
            video_items,
        )

    finally:

        db.close()

    # ------------------------------------------------------------------
    # FINAL SUMMARY
    # ------------------------------------------------------------------

    heading(
        "MIGRATION COMPLETE"
    )

    inserted = (
        photo_result["inserted"]
        + project_result["inserted"]
        + video_result["inserted"]
    )

    skipped = (
        photo_result["skipped"]
        + project_result["skipped"]
        + video_result["skipped"]
    )

    failed = (
        photo_result["failed"]
        + project_result["failed"]
        + video_result["failed"]
    )

    print(
        f"Inserted : {inserted}"
    )

    print(
        f"Skipped  : {skipped}"
    )

    print(
        f"Failed   : {failed}"
    )

    print()
    print(
        "Images stored in:"
    )

    print(
        f"  {MEDIA_DIR}"
    )

    print()
    print(
        "Photo Gallery:"
    )

    print(
        f"  Inserted: "
        f"{photo_result['inserted']}"
    )

    print(
        f"  Skipped : "
        f"{photo_result['skipped']}"
    )

    print(
        f"  Failed  : "
        f"{photo_result['failed']}"
    )

    print()
    print(
        "Projects:"
    )

    print(
        f"  Inserted: "
        f"{project_result['inserted']}"
    )

    print(
        f"  Skipped : "
        f"{project_result['skipped']}"
    )

    print(
        f"  Failed  : "
        f"{project_result['failed']}"
    )

    print()
    print(
        "Video Gallery:"
    )

    print(
        f"  Inserted: "
        f"{video_result['inserted']}"
    )

    print(
        f"  Skipped : "
        f"{video_result['skipped']}"
    )

    print(
        f"  Failed  : "
        f"{video_result['failed']}"
    )


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    migrate()