import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image

BASE = os.path.join(os.path.dirname(__file__), "..", "media", "certificate_templates")
path = os.path.join(BASE, "volunteer card.png")
img = Image.open(path).convert("L")

x0, x1 = 0, 694
y0, y1 = 0, 1133
block = 3
thresh = 150

w = (x1 - x0) // block
h = (y1 - y0) // block
for row in range(h):
    line = []
    for col in range(w):
        dark = 0
        for dy in range(block):
            for dx in range(block):
                if img.getpixel((x0 + col * block + dx, y0 + row * block + dy)) < thresh:
                    dark += 1
        line.append("#" if dark >= 3 * block else ("+" if dark > 0 else " "))
    print(f"{y0 + row * block:04d} " + "".join(line))