import numpy as np
from PIL import Image
from scipy import ndimage

rgb = np.load("crop_rgb.npy"); fg0 = np.load("crop_fg.npy")
R,G,B = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
val = rgb.max(2)/255.0

# dark blue-cast background remnants: dark AND blue clearly above red
dark_blue = (val < 0.24) & (B > R + 12)
fg = fg0 & ~dark_blue
fg = ndimage.binary_opening(fg, np.ones((7,7)))
lab, n = ndimage.label(fg)
fg = lab == (np.argmax(ndimage.sum(fg, lab, range(1,n+1)))+1)
fg = ndimage.binary_closing(fg, np.ones((9,9)))
fg = ndimage.binary_fill_holes(fg)
print("fg", round(fg0.mean(),3), "->", round(fg.mean(),3))
np.save("crop_fg.npy", fg)
p = rgb.copy(); p[~fg] = [255,0,255]
Image.fromarray(p.astype(np.uint8)).save("crop_preview.png")
