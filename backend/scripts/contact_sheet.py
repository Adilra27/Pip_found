import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(__file__).resolve().parents[1] / "previews"

FILES = [
    ("preview-appreciation.jpg", "APPRECIATION"),
    ("preview-completion.jpg", "COMPLETION"),
    ("preview-internship.jpg", "INTERNSHIP"),
    ("preview-participation.jpg", "PARTICIPATION"),
    ("preview-volunteer.jpg", "VOLUNTEER CARD"),
    ("card_grid.png", "CARD GRID (x694 = FRONT|BACK)"),
]

SCALE = 0.45
PAD = 20
HEADER = 34
COLS = 2

font = ImageFont.load_default()
try:
    font_b = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
except Exception:
    font_b = ImageFont.load_default()

imgs = []
for name, label in FILES:
    p = OUT_DIR / name
    if not p.is_file():
        print("MISSING", name)
        continue
    im = Image.open(p).convert("RGB")
    im = im.resize((int(im.width * SCALE), int(im.height * SCALE)), Image.LANCZOS)
    imgs.append((im, label))

cw = max(im.width for im, _ in imgs)
ch = max(im.height for im, _ in imgs)
rows = (len(imgs) + COLS - 1) // COLS
sheet_w = COLS * (cw + PAD) + PAD
sheet_h = rows * (HEADER + ch + PAD) + PAD

sheet = Image.new("RGB", (sheet_w, sheet_h), (38, 38, 48))
d = ImageDraw.Draw(sheet)
for i, (im, label) in enumerate(imgs):
    r, c = divmod(i, COLS)
    x = PAD + c * (cw + PAD)
    y = PAD + r * (HEADER + ch + PAD)
    d.rectangle((x - 4, y - 4, x + im.width + 4, y + HEADER + im.height + 4), outline=(90, 90, 110))
    d.text((x, y + 3), label, font=font_b, fill=(255, 200, 60))
    sheet.paste(im, (x, y + HEADER))

out = OUT_DIR / "ALL_PREVIEWS.png"
sheet.save(out)
print("saved", out, sheet.size)