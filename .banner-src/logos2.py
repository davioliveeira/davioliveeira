"""Python and n8n logo point clouds, same 300x340 grid, ~900 dots each."""
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

CW, CH = 300, 340; SS = 4; W, H = CW*SS, CH*SS
rng = np.random.default_rng(7)

def sample(im, n=900):
    a = np.asarray(im.resize((CW, CH), Image.LANCZOS)) > 110
    ys, xs = np.where(a)
    idx = rng.choice(len(ys), min(n, len(ys)), replace=False)
    return np.stack([xs[idx], ys[idx]], 1).astype(float)

def outline(im, width=9):
    a = np.asarray(im) > 128
    return Image.fromarray(((a & ~ndimage.binary_erosion(a, np.ones((width, width))))*255).astype(np.uint8))

def rr(d, x0, y0, x1, y1, r, fill):
    d.rounded_rectangle([min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1)], radius=r, fill=fill)

# ---- Python: two interlocking hooks, 180-degree rotationally symmetric ----
im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
cx, cy = W//2, H//2
u = int(W*0.105); rad = int(u*0.5)

def hook(sx, sy):
    """One half: a vertical bar down the outer side, a horizontal bar across the middle,
    and a head lobe at the far end. sx/sy = +1 for the upper-left half, -1 for the mirror."""
    # head lobe (top bar)
    rr(d, cx - sx*u*2.1, cy - sy*u*2.9, cx + sx*u*0.9, cy - sy*u*1.1, rad, 255)
    # vertical shaft on the outer edge
    rr(d, cx - sx*u*2.1, cy - sy*u*2.9, cx - sx*u*0.9, cy + sy*u*0.35, rad, 255)
    # middle bar reaching across
    rr(d, cx - sx*u*2.1, cy - sy*u*0.9, cx + sx*u*2.1, cy + sy*u*0.35, rad, 255)
    # eye
    ex, ey = cx - sx*u*1.5, cy - sy*u*2.15
    d.ellipse([ex-u*0.2, ey-u*0.2, ex+u*0.2, ey+u*0.2], fill=0)

hook(1, 1); hook(-1, -1)
py_pts = sample(outline(im, 8))

# ---- n8n: linked nodes ----
im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
R  = int(W*0.070); sp = int(W*0.205)
nodes = [(cx-sp, cy-int(sp*0.60)), (cx, cy), (cx+sp, cy-int(sp*0.60)),
         (cx+sp, cy+int(sp*0.60)), (cx-sp, cy+int(sp*0.60))]
for a_, b_ in ((0,1), (1,2), (1,3), (4,1)):
    d.line([nodes[a_], nodes[b_]], fill=255, width=int(W*0.019))
for i, (nx, ny) in enumerate(nodes):
    r = R if i == 1 else int(R*0.76)
    d.ellipse([nx-r, ny-r, nx+r, ny+r], fill=255)
    d.ellipse([nx-int(r*0.44), ny-int(r*0.44), nx+int(r*0.44), ny+int(r*0.44)], fill=0)
n8n_pts = sample(im)

for name, pts in (("python", py_pts), ("n8n", n8n_pts)):
    print(name, len(pts)); np.save(f"logo_{name}.npy", pts)
    p = np.zeros((CH, CW), bool); p[pts[:,1].astype(int), pts[:,0].astype(int)] = True
    Image.fromarray((~p*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save(f"prev_logo_{name}.png")
