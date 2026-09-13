import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"

def read(path, y0, y1, block=4, thresh=42):
    img = Image.open(path).convert("L")
    w, h = img.size
    bg = img.filter(ImageFilter.GaussianBlur(radius=30))
    diff = ImageChops.subtract(bg, img)  # dark-on-bg becomes positive
    px = diff.load()
    cols = w // block
    rows = max(2, (y1 - y0) // block)
    out = []
    for r in range(rows):
        line = []
        for c in range(cols):
            found = False
            for yy in range(y0 + r * block, min(y0 + (r + 1) * block, y1)):
                for xx in range(c * block, min((c + 1) * block, w)):
                    if px[xx, yy] > thresh:
                        found = True
                        break
                if found:
                    break
            line.append("#" if found else " ")
        out.append("".join(line).rstrip())
    return "\n".join(out)

cases = [
    ("APPRECIATION title", "Certificate of Appriciation.png", 235, 300),
    ("APPRECIATION lines 1-4", "Certificate of Appriciation.png", 330, 470),
    ("APPRECIATION lines 5-8", "Certificate of Appriciation.png", 500, 675),
]

for title, f, y0, y1 in cases:
    print("\n======== " + title + f"  (y {y0}-{y1}, block=4) ========")
    print(read(os.path.join(BASE, f), y0, y1, block=4))