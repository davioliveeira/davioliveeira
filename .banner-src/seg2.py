from PIL import Image
import numpy as np
from scipy import ndimage

im = Image.open("/Users/davioliveeira/Downloads/perfil.jpeg").convert("RGB")
a = np.asarray(im).astype(float)
h, w, _ = a.shape
R, G, B = a[:,:,0], a[:,:,1], a[:,:,2]
mx = a.max(2); mn = a.min(2)
sat = np.where(mx > 0, (mx-mn)/np.maximum(mx,1), 0)
val = mx/255.0

blue_bg = (B > R + 40) & (B > G + 40) & (sat > 0.40)
red_bg  = (R > B + 30) & (R > G + 60) & (sat > 0.55) & (G < 90)
dark_bg = val < 0.05
# extra: anything saturated at all that isn't skin-ish
neon = (sat > 0.60) & ~((R > G) & (G > B) & (val > 0.25))
bg = blue_bg | red_bg | dark_bg | neon

fg = ndimage.binary_closing(~bg, np.ones((11,11)))
fg = ndimage.binary_opening(fg, np.ones((7,7)))
lab, n = ndimage.label(fg)
fg = lab == (np.argmax(ndimage.sum(fg, lab, range(1,n+1)))+1)
fg = ndimage.binary_fill_holes(fg)

# head+shoulders crop: top of subject, height ~= 2.05x head-ish; use bbox top
ys, xs = np.where(fg)
top = ys.min()
# subject horizontal center from a band just below the head
band = fg[top+300:top+700]
bxs = np.where(band.any(0))[0]
cx = int((bxs.min()+bxs.max())/2)

CH = 340; CW = 300           # target grid
ch_px = 1000                  # crop height in source px (head + shoulders)
cw_px = int(ch_px * CW/CH)
y0 = max(0, top - 90)
y1 = min(h, y0 + ch_px)
x0 = max(0, cx - cw_px//2); x1 = min(w, x0 + cw_px)

crop_rgb = a[y0:y1, x0:x1]
crop_fg  = fg[y0:y1, x0:x1]
print("crop", crop_rgb.shape, "fg frac", round(crop_fg.mean(),3))

np.save("crop_rgb.npy", crop_rgb); np.save("crop_fg.npy", crop_fg)
p = crop_rgb.copy(); p[~crop_fg] = [255,0,255]
Image.fromarray(p.astype(np.uint8)).save("crop_preview.png")
