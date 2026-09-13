import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"

CHARS = " .,:;irsXA253hMHGS#9B&@"

def ascii_art(path, cols=140):
    img = Image.open(path).convert("L")
    w, h = img.size
    bg = img.filter(ImageFilter.GaussianBlur(radius=25))
    diff = ImageChops.subtract(bg, img)
    rows = max(2, int(cols * h / w * 0.5))
    hp = diff.resize((cols, rows))
    px = hp.load()
    vals = [px[x, y] for y in range(rows) for x in range(cols)]
    mx = max(vals) if vals else 0
    out = []
    for y in range(rows):
        line = "".join(CHARS[min(px[x, y] * (len(CHARS) - 1) // mx, len(CHARS) - 1)] if mx else " " for x in range(cols))
        out.append(line)
    return "\n".join(out)

for f in sorted(os.listdir(BASE)):
    print("\n" + "=" * 36 + f + "=" * 36)
    print(ascii_art(os.path.join(BASE, f), cols=140))