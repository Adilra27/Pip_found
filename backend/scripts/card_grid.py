import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..", "media", "certificate_templates")
OUT = os.path.join(os.path.dirname(__file__), "..", "previews")

path = os.path.join(BASE, "volunteer card.png")
img = Image.open(path).convert("RGB")
w, h = img.size
d = ImageDraw.Draw(img)
font = ImageFont.load_default()

step = 80
# x guide lines
for x in range(0, w + 1, step):
    d.line([(x, 0), (x, h)], fill=(0, 255, 0), width=1)
    d.text((x + 2, 2), f"x{x}", fill=(0, 200, 0), font=font)
# y guide lines
for y in range(0, h + 1, step):
    d.line([(0, y), (w, y)], fill=(255, 0, 255), width=1)
    d.text((2, y + 2), f"y{y}", fill=(200, 0, 200), font=font)

# face divider
d.line([(w // 2, 0), (w // 2, h)], fill=(255, 0, 0), width=3)
d.text((w // 2 - 40, 30), "FRONT", fill=(255, 0, 0), font=font)
d.text((w // 2 + 10, 30), "BACK", fill=(255, 0, 0), font=font)

out = os.path.join(OUT, "card_grid.png")
img.save(out)
print("saved", out, "size", (w, h))