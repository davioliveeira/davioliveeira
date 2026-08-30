import numpy as np
from PIL import Image, ImageOps, ImageFilter

CW, CH = 300, 340
rgb_full = np.load("crop_rgb.npy").astype(np.uint8)
fg_full  = np.load("crop_fg.npy")
top = np.where(fg_full)[0].min()

H_SRC = 560                       # variant A framing: head + collar
w_src = int(H_SRC * CW / CH)
band = fg_full[top+200:top+500]
bxs  = np.where(band.any(0))[0]
cx   = int((bxs.min() + bxs.max()) / 2)
y0 = max(0, top - 30); y1 = min(fg_full.shape[0], y0 + H_SRC)
x0 = max(0, cx - w_src//2); x1 = min(fg_full.shape[1], x0 + w_src)

img = Image.fromarray(rgb_full[y0:y1, x0:x1]).convert("L").resize((CW, CH), Image.LANCZOS)
m   = np.asarray(Image.fromarray((fg_full[y0:y1, x0:x1]*255).astype(np.uint8))
                 .resize((CW, CH), Image.LANCZOS)) > 127

img = ImageOps.autocontrast(img, cutoff=1)
img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
g = np.clip(128 + (np.asarray(img).astype(float) - 128) * 1.3, 0, 255)

def fs(src, mask=None):
    """Floyd-Steinberg, serpentine. mask=None diffuses everywhere; otherwise error is
    hard-cleared outside the subject so it can't bleed past the silhouette edge."""
    a = src.copy(); H, W = a.shape
    out = np.zeros((H, W), bool)
    for y in range(H):
        rng = range(W) if y % 2 == 0 else range(W-1, -1, -1)
        d = 1 if y % 2 == 0 else -1
        for x in rng:
            old = a[y, x]; new = 255.0 if old >= 128 else 0.0
            out[y, x] = new > 0
            err = old - new
            if mask is not None and not mask[y, x]: continue
            if 0 <= x+d < W:      a[y, x+d]   += err*7/16
            if y+1 < H:
                if 0 <= x-d < W:  a[y+1, x-d] += err*3/16
                a[y+1, x]                     += err*5/16
                if 0 <= x+d < W:  a[y+1, x+d] += err*1/16
    return out

dark  = fs(np.where(m, g, 0.0), m) & m      # dark mode: dots draw the lit subject
light = fs(np.where(m, 255.0 - g, 255.0), m) & m   # light mode: same silhouette, dots draw the dark parts

print("dark dots", int(dark.sum()), "light dots", int(light.sum()))
np.save("dark.npy", dark); np.save("light.npy", light); np.save("mask_grid.npy", m)
Image.fromarray((~dark*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save("prev_dark.png")
Image.fromarray((~light*255).astype(np.uint8)).resize((CW*2, CH*2), Image.NEAREST).save("prev_light.png")
