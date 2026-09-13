import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"
CHARS = " .,:;irsXA253hMHGS#9B&@"

def ascii_zoom(path, y0, y1, cols=240):
    img = Image.open(path).convert("L")
    w, h = img.size
    bg = img.filter(ImageFilter.GaussianBlur(radius=25))
    diff = ImageChops.subtract(bg, img)
    crop = diff.crop((0, y0, w, y1))
    ch = y1 - y0
    rows = max(2, int(cols * ch / w * 0.5))
    hp = crop.resize((cols, rows))
    px = hp.load()
    vals = [px[x, y] for y in range(rows) for x in range(cols)]
    mx = max(vals) if vals else 0
    out = []
    for y in range(rows):
        line = "".join(CHARS[min(px[x, y] * (len(CHARS) - 1) // mx, len(CHARS) - 1)] if mx else " " for x in range(cols))
        col = "L" if y0 + (y + 1) * ch // rows < y0 else "M"
        out.append(f"{y0 + y * ch // rows:4d} {line}")
    return "\n".join(out)

def zoom_all(path):
    w, h = Image.open(path).size
    print("\n" + "=" * 30 + path + f" ({w}x{h})" + "=" * 30)
    y0 = 0
    while y0 < h:
        y1 = min(y0 + 170, h)
        print(ascii_zoom(path, y0, y1, cols=170))
        y0 = y1

zoom_all(os.path.join(BASE, "volunteer card.png"))