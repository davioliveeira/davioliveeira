import numpy as np
from PIL import Image, ImageDraw

CW, CH = 300, 340; SS = 4; W, H = CW*SS, CH*SS
im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
cx, cy = W//2, H//2
t   = int(W*0.045)
ax  = int(W*0.105)
ay  = int(W*0.235)
off = int(W*0.255)

# "<" : vertex on the LEFT, arms opening to the right
lv = (cx-off-ax, cy)
d.line([(cx-off+ax, cy-ay), lv], fill=255, width=t)
d.line([(cx-off+ax, cy+ay), lv], fill=255, width=t)
# ">" : vertex on the RIGHT, arms opening to the left
rv = (cx+off+ax, cy)
d.line([(cx+off-ax, cy-ay), rv], fill=255, width=t)
d.line([(cx+off-ax, cy+ay), rv], fill=255, width=t)
# "/" slash through the middle
d.line([(cx+int(ax*0.55), cy-int(ay*1.25)), (cx-int(ax*0.55), cy+int(ay*1.25))], fill=255, width=t)

a = np.asarray(im.resize((CW, CH), Image.LANCZOS)) > 110
ys, xs = np.where(a)
idx = np.random.default_rng(7).choice(len(ys), min(900, len(ys)), replace=False)
pts = np.stack([xs[idx], ys[idx]], 1).astype(float)
np.save("logo_code.npy", pts); print("code", len(pts))
p = np.zeros((CH, CW), bool); p[pts[:,1].astype(int), pts[:,0].astype(int)] = True
Image.fromarray((~p*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save("prev_logo_code.png")
