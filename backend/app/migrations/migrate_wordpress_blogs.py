"""
Migrate blog posts from the Piplad Welfare Foundation WordPress site
into the local SQLite Blog table.

Source:
https://pipladfoundation.in/wp-json/wp/v2/posts

Features:
- Fetches all published WordPress posts using pagination
- Uses _embed to retrieve featured images
- Preserves WordPress HTML content
- Converts excerpts to clean text summaries
- Stores original WordPress URL
- Stores WordPress slug
- Uses slug to prevent duplicate records
- Updates existing posts when re-run
- Can safely be executed multiple times
"""

import sys
import re
import html
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Make backend/app importable when this script is executed directly
# ---------------------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database import Base, SessionLocal, engine
from app.models import Blog


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORDPRESS_API_URL = (
    "https://pipladfoundation.in/wp-json/wp/v2/posts"
)

PER_PAGE = 100

REQUEST_TIMEOUT = 30

# WordPress returns posts with status=publish when requested this way.
WORDPRESS_STATUS = "publish"


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def clean_html_to_text(value: Optional[str]) -> str:
    """
    Convert HTML into clean readable plain text.

    Used primarily for the WordPress excerpt/summary.
    """

    if not value:
        return ""

    soup = BeautifulSoup(value, "html.parser")

    # Get readable text while preserving natural spacing.
    text = soup.get_text(" ", strip=True)

    # Decode HTML entities.
    text = html.unescape(text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def parse_wordpress_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    Convert WordPress ISO datetime into a Python datetime.

    Example:
        2025-10-21T16:06:43

    WordPress commonly returns dates without an explicit timezone.
    We store the resulting datetime as a naive UTC-compatible datetime
    because the existing SQLAlchemy model uses DateTime without timezone.
    """

    if not value:
        return None

    try:
        # WordPress example:
        # 2025-10-21T16:06:43
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

        # Our SQLAlchemy model currently uses DateTime without timezone.
        # Convert timezone-aware values to UTC and then remove timezone info.
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

        return dt

    except ValueError:
        print(f"WARNING: Could not parse date: {value}")
        return None


def get_featured_image(post: dict) -> Optional[str]:
    """
    Extract the featured image URL from WordPress _embedded data.

    WordPress response structure is generally:

    _embedded
        wp:featuredmedia
            [0]
                source_url
    """

    embedded = post.get("_embedded") or {}

    featured_media = embedded.get("wp:featuredmedia") or []

    if not featured_media:
        return None

    media = featured_media[0]

    # Preferred URL.
    source_url = media.get("source_url")

    if source_url:
        return source_url

    # Fallbacks in case source_url is unavailable.
    media_details = media.get("media_details") or {}
    sizes = media_details.get("sizes") or {}

    # Prefer large image.
    for size_name in ("large", "medium_large", "medium", "thumbnail"):
        size_data = sizes.get(size_name)

        if size_data and size_data.get("source_url"):
            return size_data["source_url"]

    return None


def get_summary(post: dict) -> str:
    """
    Get the best available summary for a WordPress post.

    Priority:
        1. excerpt.rendered
        2. first ~300 characters of content
    """

    excerpt = post.get("excerpt") or {}
    excerpt_html = excerpt.get("rendered")

    summary = clean_html_to_text(excerpt_html)

    if summary:
        # WordPress excerpts sometimes contain an ellipsis.
        summary = summary.replace("[&hellip;]", "…")
        summary = summary.replace("[…]", "…")

        return summary

    # Fallback to content.
    content_html = (post.get("content") or {}).get("rendered", "")

    content_text = clean_html_to_text(content_html)

    if not content_text:
        return ""

    # Keep summary reasonably short.
    max_length = 300

    if len(content_text) <= max_length:
        return content_text

    shortened = content_text[:max_length].rsplit(" ", 1)[0]

    return shortened + "…"


def normalize_content(post: dict) -> str:
    """
    Return the complete WordPress HTML content.

    We intentionally preserve the HTML because the frontend can render
    headings, paragraphs, lists, images, links, etc.
    """

    content = post.get("content") or {}

    rendered = content.get("rendered")

    if not rendered:
        return ""

    return rendered.strip()


# ---------------------------------------------------------------------------
# WordPress API
# ---------------------------------------------------------------------------

def fetch_wordpress_posts() -> list[dict]:
    """
    Fetch every published WordPress post using pagination.
    """

    all_posts = []

    page = 1

    print()
    print("=" * 70)
    print("Fetching Piplad WordPress blog posts")
    print("=" * 70)
    print()

    while True:

        params = {
            "per_page": PER_PAGE,
            "page": page,
            "_embed": "1",
            "status": WORDPRESS_STATUS,
        }

        print(f"Fetching page {page}...")

        try:
            response = requests.get(
                WORDPRESS_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Failed to connect to WordPress API: {exc}"
            ) from exc

        # WordPress returns 400 when a requested page doesn't exist.
        if response.status_code == 400 and page > 1:
            print("No more pages.")
            break

        if not response.ok:
            raise RuntimeError(
                f"WordPress API returned HTTP "
                f"{response.status_code}: {response.text[:500]}"
            )

        try:
            posts = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "WordPress API did not return valid JSON."
            ) from exc

        if not isinstance(posts, list):
            raise RuntimeError(
                "Unexpected WordPress API response format."
            )

        print(f"  Posts returned: {len(posts)}")

        if not posts:
            break

        all_posts.extend(posts)

        # WordPress tells us the total number of pages in this header.
        total_pages_header = response.headers.get("X-WP-TotalPages")

        if total_pages_header:
            try:
                total_pages = int(total_pages_header)

                if page >= total_pages:
                    break

            except ValueError:
                pass

        # If fewer than PER_PAGE posts were returned, this is the last page.
        if len(posts) < PER_PAGE:
            break

        page += 1

    print()
    print(f"Total WordPress posts fetched: {len(all_posts)}")
    print()

    return all_posts


# ---------------------------------------------------------------------------
# Database migration
# ---------------------------------------------------------------------------

def migrate_posts(posts: list[dict]) -> tuple[int, int, int]:
    """
    Insert or update WordPress posts in the local database.

    Returns:
        created_count
        updated_count
        skipped_count
    """

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    created_count = 0
    updated_count = 0
    skipped_count = 0

    try:

        print("=" * 70)
        print("Migrating posts into SQLite")
        print("=" * 70)
        print()

        for index, post in enumerate(posts, start=1):

            wordpress_id = post.get("id")

            title = (
                (post.get("title") or {}).get("rendered")
                or "Untitled Post"
            )

            slug = post.get("slug")

            source_url = post.get("link")

            content = normalize_content(post)

            summary = get_summary(post)

            image_url = get_featured_image(post)

            published_date = parse_wordpress_datetime(
                post.get("date")
            )

            modified_date = parse_wordpress_datetime(
                post.get("modified")
            )

            # ---------------------------------------------------------------
            # Basic validation
            # ---------------------------------------------------------------

            if not slug:
                print(
                    f"[{index}/{len(posts)}] SKIPPED: "
                    f'"{title}" has no slug.'
                )

                skipped_count += 1
                continue

            if not content:
                print(
                    f"[{index}/{len(posts)}] WARNING: "
                    f'"{title}" has no content.'
                )

            # ---------------------------------------------------------------
            # Find existing post by slug
            # ---------------------------------------------------------------

            existing_post = (
                db.query(Blog)
                .filter(Blog.slug == slug)
                .first()
            )

            # ---------------------------------------------------------------
            # CREATE
            # ---------------------------------------------------------------

            if existing_post is None:

                new_post = Blog(
                    title=title,
                    slug=slug,
                    summary=summary,
                    content=content,
                    image_url=image_url,
                    source_url=source_url,
                    published_date=published_date,
                )

                db.add(new_post)

                created_count += 1

                print(
                    f"[{index}/{len(posts)}] CREATED  | "
                    f"{title}"
                )

            # ---------------------------------------------------------------
            # UPDATE
            # ---------------------------------------------------------------

            else:

                changed = False

                if existing_post.title != title:
                    existing_post.title = title
                    changed = True

                if existing_post.summary != summary:
                    existing_post.summary = summary
                    changed = True

                if existing_post.content != content:
                    existing_post.content = content
                    changed = True

                if existing_post.image_url != image_url:
                    existing_post.image_url = image_url
                    changed = True

                if existing_post.source_url != source_url:
                    existing_post.source_url = source_url
                    changed = True

                if existing_post.published_date != published_date:
                    existing_post.published_date = published_date
                    changed = True

                if changed:
                    updated_count += 1

                    print(
                        f"[{index}/{len(posts)}] UPDATED  | "
                        f"{title}"
                    )

                else:
                    skipped_count += 1

                    print(
                        f"[{index}/{len(posts)}] UNCHANGED | "
                        f"{title}"
                    )

        # Commit everything only after all posts have been processed.
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return created_count, updated_count, skipped_count


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    print()
    print("=" * 70)
    print("PIPLAD WELFARE FOUNDATION")
    print("WordPress → SQLite Blog Migration")
    print("=" * 70)
    print()

    try:

        # ---------------------------------------------------------------
        # 1. Fetch WordPress posts
        # ---------------------------------------------------------------

        posts = fetch_wordpress_posts()

        if not posts:
            print("No WordPress posts found.")
            return

        # ---------------------------------------------------------------
        # 2. Migrate into SQLite
        # ---------------------------------------------------------------

        created, updated, skipped = migrate_posts(posts)

        # ---------------------------------------------------------------
        # 3. Final report
        # ---------------------------------------------------------------

        print()
        print("=" * 70)
        print("MIGRATION COMPLETED")
        print("=" * 70)
        print()
        print(f"WordPress posts fetched : {len(posts)}")
        print(f"Posts created           : {created}")
        print(f"Posts updated           : {updated}")
        print(f"Posts unchanged/skipped : {skipped}")
        print()
        print("=" * 70)
        print()

    except KeyboardInterrupt:

        print()
        print("Migration cancelled by user.")
        sys.exit(1)

    except Exception as exc:

        print()
        print("=" * 70)
        print("MIGRATION FAILED")
        print("=" * 70)
        print()
        print(str(exc))
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()