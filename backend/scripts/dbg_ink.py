import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageFilter, ImageChops

path = r"..\media\certificate_templates\Certificate of Appriciation.png"
rgb = Image.open(path).convert("RGB")
w, h = rgb.size
bg = rgb.filter(ImageFilter.GaussianBlur(radius=25))
chans = rgb.split()
bgchans = bg.split()

maxdiff = Image.new("L", rgb.size, 0)
counts = []
for c, b in zip(chans, bgchans):
    d = ImageChops.subtract(b, c)
    e = ImageChops.subtract(c, b)
    m = ImageChops.lighter(d, e)
    maxdiff = ImageChops.lighter(maxdiff, m)
    counts.append((c.getextrema(), b.getextrema(), d.getextrema(), e.getextrema(), m.getextrema()))

print("chan stats (c, bg, d, e, m extrema per channel):")
for c in counts:
    print("  ", c)
print("maxdiff extrema:", maxdiff.getextrema())

px = maxdiff.load()
ys = [0] * h
for y in range(h):
    for x in range(0, w, 3):
        if px[x, y] > 45:
            ys[y] += 1
big = [(i, v) for i, v in enumerate(ys) if v >= 4]
print("rows with >=4 ink:", big[:60])