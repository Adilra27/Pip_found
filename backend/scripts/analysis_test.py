import os
from PIL import Image

BASE = r"media\certificate_templates"
files = os.listdir(BASE)

def analyze(path, name):
    img = Image.open(path).convert("L")
    w, h = img.size
    px = img.load()
    rows = []
    for y in range(h):
        cnt = 0; xmin = w; xmax = -1
        for x in range(w):
            if px[x, y] < 85:
                cnt += 1
                if x < xmin: xmin = x
                if x > xmax: xmax = x
        if cnt > 0:
            rows.append((y, cnt, xmin, xmax))
    bands = []
    cur = None
    for y, cnt, xmin, xmax in rows:
        if cur and y - cur[1] <= 2:
            cur = (cur[0], y, cur[2] + cnt, min(cur[3], xmin), max(cur[4], xmax))
        else:
            if cur: bands.append(cur)
            cur = (y, y, cnt, xmin, xmax)
    if cur: bands.append(cur)
    bands.sort(key=lambda b: -b[2])
    print(f"\n=== {name} ({w}x{h}) --- darker text bands (<85) ===")
    for y0, y1, cnt, xmin, xmax in bands[:30]:
        print(f"  y {y0:4d}-{y1:4d}  dark={cnt:6d}  x {xmin:4d}-{xmax:4d}  w={xmax-xmin:4d}")

    # underlines: horizontal runs >= 70 px
    print("  --- long horizontal lines (>70px at <110) ---")
    shown = []
    for y in range(h):
        run = 0; best = 0; best_x0 = None; best_x1 = None
        x0 = None
        for x in range(w):
            if px[x, y] < 110:
                if x0 is None: x0 = x
                run += 1
            else:
                if run >= best: best, best_x0, best_x1 = run, x0, x
                run = 0; x0 = None
        if run >= 70 and (y not in shown or True):
            shown.append(y)
            print(f"    y={y:4d} len={best if best>=70 else run:3d} x {best_x0 if best>=70 else x0}-{best_x1 if best>=70 else x}")

for f in files:
    analyze(os.path.join(BASE, f), f)