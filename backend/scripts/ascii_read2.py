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
        lines.append("".join(line).rstrip().rstrip("#"))
    return "\n".join(lines)

f = r"media\certificate_templates\Certificate of Appriciation.png"
r = render_region(f, 250, 760, 340, 384, block=1, thresh=38)
print("===== APPRECIATION y354 (x250-760, 1px) =====")
print(r)