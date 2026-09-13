import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"

def render(path, y0, y1, block=2, thresh=40):
    img = Image.open(path).convert("L")
    w, h = img.size
    bg = img.filter(ImageFilter.GaussianBlur(radius=30))
    diff = ImageChops.subtract(bg, img)
    px = diff.load()
    cols = w // block
    rows = max(2, (y1 - y0) // block)
    lines = []
    for r in range(rows):
        line = []
        for c in range(cols):
            found = False
            y0b = y0 + r * block
            y1b = min(y0 + (r + 1) * block, y1)
            x0b = c * block
            x1b = min((c + 1) * block, w)
            for yy in range(y0b, y1b):
                for xx in range(x0b, x1b, 1):
                    if px[xx, yy] > thresh:
                        found = True
                        break
                if found:
                    break
            line.append("#" if found else " ")
        lines.append("".join(line).rstrip())
    return "\n".join(lines)

def show(name, y0, y1):
    f = os.path.join(BASE, name)
    print("\n==== %s y%d-%d (2px/char) ====" % (name, y0, y1))
    print(render(f, y0, y1))

show("Certificate of Appriciation.png", 340, 382)
show("Certificate of Appriciation.png", 405, 450)