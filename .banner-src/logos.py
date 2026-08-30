"""Rasterise three logo shapes to point clouds of ~900 dots each, on the same 300x340 grid."""
import numpy as np
from PIL import Image, ImageDraw

CW, CH = 300, 340
SS = 4                                   # supersample then threshold, keeps curves smooth
W, H = CW*SS, CH*SS
N_DOTS = 900

def sample(mask_img, n=N_DOTS):
    """Blue-noise-ish sample: take filled pixels, keep n of them spread by a grid stride."""
    a = np.asarray(mask_img.resize((CW, CH), Image.LANCZOS)) > 110
    ys, xs = np.where(a)
    if len(ys) <= n:
        return np.stack([xs, ys], 1).astype(float)
    idx = np.random.default_rng(7).choice(len(ys), n, replace=False)
    return np.stack([xs[idx], ys[idx]], 1).astype(float)

def canvas():
    im = Image.new("L", (W, H), 0)
    return im, ImageDraw.Draw(im)

# ---- 1. Go gopher: rounded body, ears, eyes, snout ----
im, d = canvas()
cx, cy = W//2, int(H*0.52); bw, bh = int(W*0.42), int(H*0.34)
d.ellipse([cx-bw, cy-bh, cx+bw, cy+bh], fill=255)                       # body
d.ellipse([cx-bw, cy-bh-int(H*0.10), cx-int(bw*0.42), cy-bh+int(H*0.06)], fill=255)  # L ear
d.ellipse([cx+int(bw*0.42), cy-bh-int(H*0.10), cx+bw, cy-bh+int(H*0.06)], fill=255)  # R ear
for sx in (-1, 1):                                                       # eye whites
    ex = cx + sx*int(bw*0.40)
    d.ellipse([ex-int(bw*0.30), cy-int(bh*0.62), ex+int(bw*0.30), cy-int(bh*0.02)], fill=0)
    d.ellipse([ex-int(bw*0.11), cy-int(bh*0.44), ex+int(bw*0.11), cy-int(bh*0.20)], fill=255)
d.ellipse([cx-int(bw*0.20), cy+int(bh*0.10), cx+int(bw*0.20), cy+int(bh*0.42)], fill=0)  # snout
go = sample(im)

# ---- 2. React atom: nucleus + three ellipse orbits ----
im, d = canvas()
cx, cy = W//2, H//2
ring_w, ring_h = int(W*0.44), int(H*0.155)
stroke = int(W*0.030)
for ang in (0, 60, 120):
    layer = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(layer)
    ld.ellipse([cx-ring_w, cy-ring_h, cx+ring_w, cy+ring_h], outline=255, width=stroke)
    im.paste(Image.new("L",(W,H),255), (0,0), layer.rotate(ang, center=(cx,cy)))
d.ellipse([cx-int(W*0.055), cy-int(W*0.055), cx+int(W*0.055), cy+int(W*0.055)], fill=255)
react = sample(im)

# ---- 3. </> glyph ----
im, d = canvas()
cx, cy = W//2, H//2; s = int(W*0.26); t = int(W*0.055); gap = int(W*0.30)
d.line([(cx-gap+s, cy-s), (cx-gap-s//2, cy), (cx-gap+s, cy+s)], fill=255, width=t, joint="curve")
d.line([(cx+gap-s, cy-s), (cx+gap+s//2, cy), (cx+gap-s, cy+s)], fill=255, width=t, joint="curve")
d.line([(cx+int(s*0.42), cy-int(s*1.15)), (cx-int(s*0.42), cy+int(s*1.15))], fill=255, width=t)
code = sample(im)

for name, pts in (("go", go), ("react", react), ("code", code)):
    print(name, len(pts))
    np.save(f"logo_{name}.npy", pts)
    prev = np.zeros((CH, CW), bool); prev[pts[:,1].astype(int), pts[:,0].astype(int)] = True
    Image.fromarray((~prev*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save(f"prev_logo_{name}.png")
