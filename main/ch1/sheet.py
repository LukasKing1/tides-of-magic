import sys, glob
from PIL import Image
fs = sys.argv[2:]
cols = 3
ims = [Image.open(f).resize((640, 360)) for f in fs]
rows = (len(ims) + cols - 1) // cols
s = Image.new('RGB', (640 * cols, 360 * rows))
for k, im in enumerate(ims):
    s.paste(im, ((k % cols) * 640, (k // cols) * 360))
s.save(sys.argv[1])
