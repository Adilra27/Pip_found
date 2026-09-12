"""Render the Piplad volunteer certificate image with the recipient's
details stamped onto the official design template.

The template is the official "piplad-volunteering certificate" design that
lives in frontend/dist. It is committed under backend/app/assets so it ships
with the backend build (frontend/dist itself is gitignored and not deployed).

The winner's name and the issue date are painted onto the JPEG using Pillow
and the result is returned as JPEG bytes, ready to attach to an email.
"""

import io
import logging
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ============================================================
# TUNE THESE COORDINATES TO FIT THE TEMPLATE (1136 x 804 px)
# ============================================================
NAME_CENTER_X = 568
NAME_CENTER_Y = 487          # vertical centre of the placeholder banner
NAME_FONT_SIZE = 44
NAME_COLOR = (31, 41, 55)    # dark slate ink
NAME_MAX_WIDTH = 460          # keep within the banner width

DATE_CENTER_X = 568
DATE_CENTER_Y = 668           # over the placeholder date lines
DATE_FONT_SIZE = 18
DATE_COLOR = (71, 85, 105)    # slate grey

# Regions on the template that contain placeholder text to blank out.
# Each entry is (left, top, right, bottom) in pixel coordinates.
# The area is filled with sampled background colours before stamping real text.
_NAME_PLACEHOLDER_BOX = (310, 452, 826, 522)     # "FIRST AND LAST NAME" banner
_DATE_PLACEHOLDER_BOX = (340, 638, 790, 690)      # "Date" + "From July..." lines

_TEMPLATE_PATH = (
    Path(__file__).resolve().parent / "assets" / "piplad-volunteering-certificate.jpg"
)

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


def _blank_region(image: Image.Image, box: tuple[int, int, int, int]) -> None:
    """Fill *box* (left, top, right, bottom) with the surrounding background.

    Samples pixels just outside the box edges and fills with the average,
    producing a clean slate that blends with the watercolour template.
    """
    left, top, right, bottom = box
    # Sample a few pixels from above, below, left and right of the box
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
            r_sum += pr; g_sum += pg; b_sum += pb
            count += 1
    if count == 0:
        avg = (138, 208, 96)  # fallback green
    else:
        avg = (r_sum // count, g_sum // count, b_sum // count)

    from PIL import ImageDraw as _ID
    draw = _ID.Draw(image)
    draw.rectangle(box, fill=avg)


def _format_date(value) -> str:
    if not value:
        return datetime.utcnow().strftime("%d %B %Y")
    if isinstance(value, datetime):
        return value.strftime("%d %B %Y")
    return str(value)


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_x: int,
    center_y: int,
    base_size: int,
    color,
    max_width: int,
) -> None:
    size = base_size
    font = _load_font(size)
    while size > 14 and draw.textlength(text, font=font) > max_width:
        size -= 2
        font = _load_font(size)
    draw.text((center_x, center_y), text, font=font, fill=color, anchor="mm")


def build_volunteer_certificate_image(
    *,
    full_name: str,
    certificate_date=None,
) -> bytes:
    """Stamp `full_name` and the issue date onto the official template.

    Returns the rendered JPEG bytes (no side effects on disk).
    Raises FileNotFoundError if the template is missing.
    """
    if not _TEMPLATE_PATH.is_file():
        raise FileNotFoundError(
            f"Certificate template not found: {_TEMPLATE_PATH}"
        )

    image = Image.open(_TEMPLATE_PATH).convert("RGB")

    # Blank out placeholder text baked into the template image
    _blank_region(image, _NAME_PLACEHOLDER_BOX)
    _blank_region(image, _DATE_PLACEHOLDER_BOX)

    draw = ImageDraw.Draw(image)

    name = _clean(full_name).upper()
    if name:
        _draw_centered(
            draw,
            name,
            NAME_CENTER_X,
            NAME_CENTER_Y,
            NAME_FONT_SIZE,
            NAME_COLOR,
            NAME_MAX_WIDTH,
        )

    date_text = _format_date(certificate_date)
    _draw_centered(
        draw,
        date_text,
        DATE_CENTER_X,
        DATE_CENTER_Y,
        DATE_FONT_SIZE,
        DATE_COLOR,
        600,
    )

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()