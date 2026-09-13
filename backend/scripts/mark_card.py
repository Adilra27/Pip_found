import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..", "media", "certificate_templates")
OUT = os.path.join(os.path.dirname(__file__), "..", "previews")

def ink_map(rgb):
    bg = rgb.filter(ImageFilter.GaussianBlur(radius=25))
    chans = rgb.split(); bgchans = bg.split()
    maxdiff = Image.new("L", rgb.size, 0)
    for c, b in zip(chans, bgchans):
        m = ImageChops.lighter(ImageChops.subtract(b, c), ImageChops.subtract(c, b))
        maxdiff = ImageChops.lighter(maxdiff, m)
    return maxdiff

path = os.path.join(BASE, "volunteer card.png")
rgb = Image.open(path).convert("RGB")
w, h = rgb.size
ink = ink_map(rgb)
px = ink.load()
X0, X1 = 560, w - 10
Y0, Y1 = 40, h - 110
rows = []
for y in range(Y0, Y1):
    s = 0
    for x in range(X0, X1, 2):
        if px[x, y] > 55:
            s += 1
    rows.append(s)
lines = []
cur = None
for i, s in enumerate(rows):
    y = Y0 + i
    if s >= 12:
        if cur is None: cur = [y, y]
        else: cur[1] = y
    else:
        if cur and cur[1] - cur[0] >= 6:
            lines.append(tuple(cur))
        cur = None
if cur and cur[1] - cur[0] >= 6:
    lines.append(tuple(cur))
cys = [(a + b) // 2 for a, b in lines]
print("card right-half lines:", cys)

img = Image.open(path).convert("RGB")
d = ImageDraw.Draw(img)
font = ImageFont.load_default()
for (a, b), cy in zip(lines, cys):
    d.line([(X0, cy), (w - 8, cy)], fill=(255, 0, 0), width=2)
    d.rectangle([(X0, max(0, cy - 12)), (X0 + 120, cy)], outline=(255, 0, 0), width=1)
    d.text((X0 + 2, max(0, cy - 12)), "R%d" % cy, fill=(255, 0, 0), font=font)
out = os.path.join(OUT, "marked_volunteer_card_right.png")
img.save(out)
print("saved", out)