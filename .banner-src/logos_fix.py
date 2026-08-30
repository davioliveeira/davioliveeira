import numpy as np
from PIL import Image, ImageDraw

CW, CH = 300, 340
SS = 4; W, H = CW*SS, CH*SS
N = 900

def sample(im, n=N):
    a = np.asarray(im.resize((CW, CH), Image.LANCZOS)) > 110
    ys, xs = np.where(a)
    idx = np.random.default_rng(7).choice(len(ys), min(n, len(ys)), replace=False)
    return np.stack([xs[idx], ys[idx]], 1).astype(float)

def outline(fill_img, width):
    """Keep only the border band of a filled shape, so dots trace the silhouette."""
    from scipy import ndimage
    a = np.asarray(fill_img) > 128
    er = ndimage.binary_erosion(a, np.ones((width, width)))
    return Image.fromarray(((a & ~er)*255).astype(np.uint8))

# ---- gopher: filled silhouette, dots trace its outline + eyes ----
im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
cx, cy = W//2, int(H*0.55); bw, bh = int(W*0.34), int(H*0.30)
d.ellipse([cx-bw, cy-bh, cx+bw, cy+bh], fill=255)
for sx in (-1, 1):                                            # ears
    ex = cx + sx*int(bw*0.78)
    d.ellipse([ex-int(bw*0.26), cy-bh-int(H*0.075), ex+int(bw*0.26), cy-bh+int(H*0.025)], fill=255)
edge = outline(im, 9)
ed = ImageDraw.Draw(edge)
for sx in (-1, 1):                                            # eyes: rings + pupils
    ex = cx + sx*int(bw*0.42)
    ed.ellipse([ex-int(bw*0.27), cy-int(bh*0.60), ex+int(bw*0.27), cy-int(bh*0.06)], outline=255, width=8)
    ed.ellipse([ex-int(bw*0.09), cy-int(bh*0.40), ex+int(bw*0.09), cy-int(bh*0.24)], fill=255)
ed.ellipse([cx-int(bw*0.17), cy+int(bh*0.16), cx+int(bw*0.17), cy+int(bh*0.44)], outline=255, width=8)  # snout
ed.line([(cx-int(bw*0.05), cy+int(bh*0.24)), (cx+int(bw*0.05), cy+int(bh*0.24))], fill=255, width=10)   # nose
go = sample(edge)

# ---- </> : tighter chevrons, clear slash ----
im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
cx, cy = W//2, H//2
t = int(W*0.050); arm = int(W*0.20); off = int(W*0.26)
d.line([(cx-off+arm, cy-arm), (cx-off-arm, cy), (cx-off+arm, cy+arm)], fill=255, width=t, joint="curve")
d.line([(cx+off-arm, cy-arm), (cx+off+arm, cy), (cx+off-arm, cy+arm)], fill=255, width=t, joint="curve")
d.line([(cx+int(arm*0.46), cy-int(arm*1.32)), (cx-int(arm*0.46), cy+int(arm*1.32))], fill=255, width=t)
code = sample(im)

for name, pts in (("go", go), ("code", code)):
    print(name, len(pts)); np.save(f"logo_{name}.npy", pts)
    p = np.zeros((CH, CW), bool); p[pts[:,1].astype(int), pts[:,0].astype(int)] = True
    Image.fromarray((~p*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save(f"prev_logo_{name}.png")
