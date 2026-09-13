import os
from PIL import Image, ImageFilter, ImageChops

BASE = r"media\certificate_templates"
CHARS = " .,:;irsXA253hMHGS#9B&@"

def band(path, y0, y1, cols=480, vs=2):
    img = Image.open(path).convert("L")
    w, h = img.size
    bg = img.filter(ImageFilter.GaussianBlur(radius=15))
    diff = ImageChops.subtract(bg, img)
    crop = diff.crop((0, y0, w, y1))
    ch = y1 - y0
    rows = max(2, int(cols * ch / w * 0.5 * vs))
    hp = crop.resize((cols, rows))
    px = hp.load()
    vals = [px[x, y] for y in range(rows) for x in range(cols)]
    mx = max(vals) if vals else 0
    out = []
    for y in range(rows):
        line = "".join(CHARS[min(px[x, y] * (len(CHARS) - 1) // mx, len(CHARS) - 1)] if mx else " " for x in range(cols))
        out.append(line)
    return "\n".join(out)

def show(title, path, y0, y1):
    print("\n" + "-" * 20 + f"{title}  y {y0}-{y1}" + "-" * 20)
    print(band(path, y0, y1))

show("APPRECIATION", os.path.join(BASE, "Certificate of Appriciation.png"), 330, 470)
show("APPRECIATION", os.path.join(BASE, "Certificate of Appriciation.png"), 500, 680)