import sys, glob
from PIL import Image, ImageDraw, ImageFont
ts = sys.argv[1].split(',')
out = sys.argv[2]
pw, ph = 270, 480
cols = min(len(ts), 6)
rows = (len(ts) + cols - 1) // cols
im = Image.new('RGB', (cols * (pw + 10) + 10, rows * (ph + 36) + 10), (20, 20, 24))
d = ImageDraw.Draw(im)
f = ImageFont.truetype('/home/claude/test/fonts/Oswald[wght].ttf', 22)
for i, t in enumerate(ts):
    r, k = divmod(i, cols)
    fr = Image.open(f'stills/s_{float(t):05.2f}.png').resize((pw, ph), Image.LANCZOS)
    x, y = 10 + k * (pw + 10), 10 + r * (ph + 36)
    im.paste(fr, (x, y + 28))
    d.text((x, y), t, font=f, fill=(216, 179, 92))
im.save(out)
