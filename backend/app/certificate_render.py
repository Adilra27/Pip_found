"""Generic certificate renderer backed by an admin-managed template image.

A ``CertificateTemplate`` row stores the background image URL plus a JSON
``layout``. Each text field (name / date / topic) is an anchor with:

    x, y, font_size, max_width, color, box

where ``box`` is an optional (left, top, right, bottom) pixel rectangle that
is blanked out (filled with the sampled surrounding background) before the
real text is stamped. This mirrors the behaviour of the original volunteer
certificate renderer, but for arbitrary uploaded templates.
"""

import io
import logging
import mimetypes
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/georgiab.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
]

_FONT_CACHE = {}


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont
    for path in _FONT_CANDIDATES:
        if Path(path).is_file():
            try:
                font = ImageFont.truetype(path, size)
                _FONT_CACHE[size] = font
                return font
            except Exception:
                continue
    try:
        font = ImageFont.load_default(size=size)
    except TypeError:
        font = ImageFont.load_default()
    _FONT_CACHE[size] = font
    return font


def _clean(value) -> str:
    return str(value or "").replace("\n", " ").strip()


def _blank_region(image: Image.Image, box) -> None:
    if not box:
        return
    left, top, right, bottom = [int(x) for x in box]
    sample_coords = [
        (left - 5, top - 5), (right + 5, top - 5),
        (left - 5, bottom + 5), (right + 5, bottom + 5),
        ((left + right) // 2, top - 8), ((left + right) // 2, bottom + 8),
    ]
    r_sum = g_sum = b_sum = 0
    count = 0
    w, h = image.size
    for sx, sy in sample_coords:
        if 0 <= sx < w and 0 <= sy < h:
            pr, pg, pb = image.getpixel((sx, sy))[:3]
            r_sum += pr
            g_sum += pg
            b_sum += pb
            count += 1
    if count == 0:
        avg = (255, 255, 255)
    else:
        avg = (r_sum // count, g_sum // count, b_sum // count)
    ImageDraw.Draw(image).rectangle(box, fill=avg)


def _hex_color(value) -> tuple[int, int, int]:
    text = _clean(value)
    try:
        text = text.lstrip("#")
        if len(text) == 6:
            return tuple(int(text[i:i + 2], 16) for i in (0, 2, 4))
        if len(text) == 3:
            return tuple(int(c * 2, 16) for c in text)
    except (TypeError, ValueError):
        pass
    return (31, 41, 55)


def _draw_anchor(
    draw: ImageDraw.ImageDraw,
    anchor,
    text: str,
) -> None:
    if not anchor or not text:
        return
    x = float(anchor.get("x", 0))
    y = float(anchor.get("y", 0))
    size = int(anchor.get("font_size", 24) or 24)
    color = _hex_color(anchor.get("color"))
    max_width = int(anchor.get("max_width", 800) or 800)

    font = _load_font(size)
    while size > 10 and draw.textlength(text, font=font) > max_width:
        size -= 1
        font = _load_font(size)
    draw.text((x, y), text, font=font, fill=color, anchor="mm")


def load_background_image(image_url: str | None) -> Image.Image:
    """Load a template image from a local /media path or an http(s) URL."""
    if not image_url:
        raise FileNotFoundError("Certificate template has no background image.")

    if image_url.startswith(("/media/", "media/")):
        relative = image_url.removeprefix("/media/")
        candidate = Path(__file__).resolve().parents[1] / "media" / relative
        if not candidate.is_file():
            raise FileNotFoundError(f"Template image not found on disk: {image_url}")
        return Image.open(candidate).convert("RGB")

    if image_url.startswith(("http://", "https://", "res.cloudinary.com/")):
        import requests

        url = image_url if "://" in image_url else f"https://{image_url}"
        response = requests.get(url, timeout=(3.05, 15))
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGB")

    if Path(image_url).is_file():
        return Image.open(image_url).convert("RGB")

    raise FileNotFoundError(f"Template image could not be loaded: {image_url}")


def normalize_layout(layout) -> dict:
    """Accept a raw dict or list-of-dicts layout and return the dict form."""
    if not layout:
        return {}
    if hasattr(layout, "model_dump"):
        layout = layout.model_dump()
    return layout


def build_certificate_image(
    *,
    image_url: str | None,
    layout=None,
    recipient_name: str = "",
    event_topic: str = "",
    event_date=None,
) -> bytes:
    """Render name / topic / date onto the template and return JPEG bytes."""
    layout = normalize_layout(layout)
    image = load_background_image(image_url)

    name_anchor = layout.get("name") or {}
    date_anchor = layout.get("date")
    topic_anchor = layout.get("topic")

    _blank_region(image, name_anchor.get("box"))
    if date_anchor:
        _blank_region(image, date_anchor.get("box"))
    if topic_anchor:
        _blank_region(image, topic_anchor.get("box"))

    draw = ImageDraw.Draw(image)

    name = _clean(recipient_name).upper()
    if name_anchor:
        _draw_anchor(draw, name_anchor, name)

    topic = _clean(event_topic)
    if topic_anchor:
        _draw_anchor(draw, topic_anchor, topic)

    if date_anchor:
        date_text = _clean(event_date) or ""
        _draw_anchor(draw, date_anchor, date_text)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()