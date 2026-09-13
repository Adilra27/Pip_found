import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"

def render_region(path, x0, x1, y0, y1, block=1, thresh=38):
    img = Image.open(path).convert("L")
    bg = img.filter(ImageFilter.GaussianBlur(radius=30))
    diff = ImageChops.subtract(bg, img)
    px = diff.load()
    cols = (x1 - x0) // block
    rows = max(2, (y1 - y0) // block)
    lines = []
    for r in range(rows):
        line = []
        for c in range(cols):
            found = False
            for yy in range(y0 + r * block, min(y0 + (r + 1) * block, y1)):
                for xx in range(x0 + c * block, min(x0 + (c + 1) * block, x1)):
                    if px[xx, yy] > thresh:
                        found = True
                        break
                if found:
                    break
            line.append("#" if found else " ")
        lines.append("".join(line).rstrip())
    return "\n".join(lines)

f = os.path.join(BASE, "Certificate of Appriciation.png")
print("==== y700-880  x0-560 ====")
print(render_region(f, 0, 560, 700, 880))
print("==== y700-880  x980-1536 ====")
print(render_region(f, 980, 1536, 700, 880))