import os
import sys
from PIL import Image, ImageFilter, ImageChops, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), "..", "media", "certificate_templates")
OUT = os.path.join(os.path.dirname(__file__), "..", "previews")
os.makedirs(OUT, exist_ok=True)

def ink_map(rgb):
    bg = rgb.filter(ImageFilter.GaussianBlur(radius=25))
    chans = rgb.split()
    bgchans = bg.split()
    maxdiff = Image.new("L", rgb.size, 0)
    for c, b in zip(chans, bgchans):
        d = ImageChops.subtract(b, c)  # darker-than-bg
        e = ImageChops.subtract(c, b)  # lighter-than-bg
        m = ImageChops.lighter(d, e)
        try:
            maxdiff = ImageChops.lighter(maxdiff, m)
        except Exception:
            maxdiff = m
    return maxdiff

def text_lines(path):
    rgb = Image.open(path).convert("RGB")
    w, h = rgb.size
    ink = ink_map(rgb)
    px = ink.load()
    X0, X1 = 8, w - 8
    Y0, Y1 = 60, h - 90
    rowsum = []
    for y in range(Y0, Y1):
        s = 0
        for x in range(X0, X1, 3):
            if px[x, y] > 60:
                s += 1
        rowsum.append(s)
    lines = []
    cur = None
    for i, s in enumerate(rowsum):
        y = Y0 + i
        if s >= 24:
            if cur is None:
                cur = [y, y]
            else:
                cur[1] = y
        else:
            if cur and cur[1] - cur[0] >= 4:
                lines.append(tuple(cur))
            cur = None
    if cur and cur[1] - cur[0] >= 4:
        lines.append(tuple(cur))
    return w, h, lines

def make_marked(path):
    name = os.path.basename(path)
    w, h, lines = text_lines(path)
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, (y0, y1) in enumerate(lines):
        cy = (y0 + y1) // 2
        d.line([(0, cy), (w, cy)], fill=(255, 0, 0), width=2)
        d.rectangle([(0, max(0, cy - 12)), (120, cy)], outline=(255, 0, 0), width=1)
        d.text((2, max(0, cy - 12)), f"{cy}", fill=(255, 0, 0), font=font)
    base = os.path.splitext(name)[0].replace(" ", "_")
    out = os.path.join(OUT, "marked_" + base + ".png")
    img.save(out)
    return name, os.path.basename(out), [(y0 + y1) // 2 for y0, y1 in lines]

for f in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, f)
    if os.path.isfile(p):
        name, out, cys = make_marked(p)
        print(f"{name:45s} -> {out}   lines at y: {cys}")