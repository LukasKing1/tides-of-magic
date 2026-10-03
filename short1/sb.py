"""Storyboard for Short 1 - nine key frames at 1080x1920, assembled into a sheet.
python3 sb.py            -> frames/sb_1..9.png + storyboard.png
"""
import math, os, sys
import numpy as np
import skia
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/claude/rig')
from starseer import Starseer, Pose, smooth_path, paint, rgb, ROBE, ROBE_DK, ROBE_LT, TRIM, SKIN, SKIN_DK

W, H = 1080, 1920
FD = '/home/claude/test/fonts/'
os.makedirs('/home/claude/short1/frames', exist_ok=True)

# palette
KOHLE = (28, 29, 32)
BONE = (230, 223, 208)
SLATE = (94, 102, 96)
ICE = (158, 211, 228)
GLUT = (196, 83, 46)
GOLD = (216, 179, 92)
INK = (40, 32, 28)
GREEN = (120, 226, 104)


def C(t, a=255):
    return rgb(t[0], t[1], t[2], a)


def typeface(name, wght=None):
    tf = skia.Typeface.MakeFromFile(FD + name)
    if wght:
        co = skia.FontArguments.VariationPosition.Coordinate(0x77676874, float(wght))
        fa = skia.FontArguments()
        fa.setVariationDesignPosition(skia.FontArguments.VariationPosition(skia.FontArguments.VariationPosition.Coordinates([co])))
        tf = tf.makeClone(fa)
    return tf


TF_CINZEL = typeface('Cinzel[wght].ttf', 500)
TF_CINZEL_B = typeface('Cinzel[wght].ttf', 800)
TF_OSWALD = typeface('Oswald[wght].ttf', 500)
TF_CORM_I = typeface('CormorantGaramond-Italic[wght].ttf', 600)
TF_FELL_SC = skia.Typeface.MakeFromFile(FD + 'IMFeENsc28P.ttf')


def text(c, s, x, y, tf, size, col, align='left', alpha=255, rot=0, shadow=False):
    f = skia.Font(tf, size)
    w = f.measureText(s)
    ox = {'left': 0, 'center': -w / 2, 'right': -w}[align]
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if shadow:
        sp = paint(rgb(0, 0, 0, 170))
        sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
        c.drawString(s, ox + 2, 3, f, sp)
    c.drawString(s, ox, 0, f, paint(C(col, alpha)))
    c.restore()
    return w


def blur_paint(col, sigma):
    p = paint(col)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def poly(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def shadowed(c, path, col, off=(7, 9), sigma=7, alpha=80):
    sh = skia.Path(path)
    sh.offset(*off)
    c.drawPath(sh, blur_paint(rgb(20, 12, 8, alpha), sigma))
    c.drawPath(path, paint(col))


# ------------------------------------------------------------------ parchment
def parchment(w, h, seed=1, base=(228, 208, 168)):
    rng = np.random.default_rng(seed)

    def snoise(cx, cy):
        r = rng.random((cy, cx))
        return np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    n1, n2 = snoise(w // 90 + 2, h // 90 + 2), snoise(w // 14, h // 14)
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    col = np.array(base, np.float32)[None, None] * (0.94 + 0.06 * n1[..., None]) * (0.975 + 0.025 * n2[..., None]) + fine[..., None] * 2.5
    a = np.full((h, w, 1), 255, np.float32)
    return skia.Image.fromarray(np.clip(np.concatenate([col, a], 2), 0, 255).astype(np.uint8))


PARCH_IMG = parchment(W, H, 3)

# ------------------------------------------------------------------ book world
PAGE = [(196, 250), (560, 238), (982, 246), (990, 760), (986, 1268), (560, 1276), (196, 1266)]
LPAGE = [(-60, 268), (80, 256), (196, 250), (196, 1266), (80, 1270), (-60, 1280)]


def page_path(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    p.quadTo(pts[1][0], pts[1][1] - 10, *pts[2])
    p.lineTo(*pts[3]); p.lineTo(*pts[4])
    p.quadTo(pts[5][0], pts[5][1] + 10, *pts[6])
    p.close()
    return p


def background_book(c, warm=1.0):
    g = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [rgb(16, 16, 20), rgb(44, 28, 20)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=g))
    glow = skia.GradientShader.MakeRadial(skia.Point(W * 0.62, H * 1.02), 1300, [rgb(170, 80, 30, int(90 * warm)), rgb(0, 0, 0, 0)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=glow, BlendMode=skia.BlendMode.kPlus))


def lap(c):
    # robe folds below the book
    c.drawPath(smooth_path([(-40, 1300), (300, 1330), (700, 1320), (1120, 1300), (1120, 1960), (-40, 1960)]), paint(ROBE_DK))
    for k, x in enumerate((180, 430, 700, 930)):
        c.drawPath(smooth_path([(x - 30, 1330), (x + 20, 1500), (x - 10, 1700), (x + 30, 1960), (x + 60, 1960), (x + 40, 1700), (x + 60, 1480), (x + 20, 1330)]),
                   paint(rgb(34, 38, 52)))


def book(c, burn=None):
    # leather cover
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-80, 226, 1010, 1296), 18, 18), paint(rgb(74, 44, 30)))
    for pts in (LPAGE, PAGE):
        path = page_path(pts) if pts is PAGE else poly(pts)
        c.save()
        c.clipPath(path, doAntiAlias=True)
        c.drawImage(PARCH_IMG, 0, 0)
        # gutter shadow
        gx = 196
        sh = skia.GradientShader.MakeLinear([skia.Point(gx - 90, 0), skia.Point(gx + 120, 0)],
                                            [rgb(60, 40, 20, 0), rgb(60, 36, 18, 120), rgb(60, 40, 20, 0)], [0.0, 90 / 210, 1.0])
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=sh))
        c.restore()
    # stacked page edges on the right
    for k in range(4):
        c.drawLine(990 + k * 3, 252 + k * 2, 994 + k * 3, 1262 - k * 2, paint(rgb(200, 180, 140), stroke=1.5))


def running_head(c):
    text(c, 'N° 01  ·  THE TIDES OF MAGIC', 250, 336, TF_CINZEL, 27, INK, alpha=220)
    pts = [(812, 350), (832, 306), (882, 342), (900, 306), (930, 336)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint(C(INK, 200), stroke=3))
    c.drawCircle(882, 342, 7, paint(C(GOLD)))
    c.drawLine(250, 356, 930, 356, paint(C(INK, 90), stroke=1.5))


def egg_path(cx, cy, w, h):
    pts = []
    for i in range(48):
        t = 2 * math.pi * i / 48
        f = 0.86 + 0.14 * (-math.cos(t))
        pts.append((cx + w / 2 * math.sin(t) * f, cy - h / 2 * math.cos(t)))
    return smooth_path(pts)


def egg(c, cx, cy, w=170, h=220, glow=0.0, crack=0.0, base=True):
    if base:
        c.drawOval(skia.Rect(cx - w * 0.62, cy + h * 0.40, cx + w * 0.62, cy + h * 0.56), blur_paint(rgb(30, 18, 10, 110), 8))
        c.drawPath(poly([(cx - w * 0.36, cy + h * 0.47), (cx + w * 0.36, cy + h * 0.47), (cx + w * 0.30, cy + h * 0.53), (cx - w * 0.42, cy + h * 0.53)]), paint(rgb(196, 172, 128)))
    path = egg_path(cx, cy, w, h)
    sh = skia.GradientShader.MakeRadial(skia.Point(cx - w * 0.22, cy - h * 0.2), h * 0.75, [rgb(168, 166, 158), rgb(110, 112, 108), rgb(58, 60, 62)], [0, 0.5, 1])
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh))
    c.save(); c.clipPath(path, doAntiAlias=True)
    for k in range(7):
        y = cy - h * 0.38 + k * h * 0.13
        for j in range(5):
            x = cx - w * 0.5 + j * w * 0.25 + (k % 2) * w * 0.12
            c.drawArc(skia.Rect(x - 18, y - 12, x + 18, y + 12), 20, 140, False, paint(rgb(64, 66, 66, 150), stroke=2.2))
    if glow > 0:
        gl = skia.GradientShader.MakeRadial(skia.Point(cx, cy + h * 0.1), h * 0.8, [rgb(255, 214, 120, int(200 * glow)), rgb(216, 150, 60, int(120 * glow)), rgb(120, 50, 20, 0)])
        c.drawRect(skia.Rect(cx - w, cy - h, cx + w, cy + h), skia.Paint(Shader=gl, BlendMode=skia.BlendMode.kPlus))
    c.restore()
    c.drawPath(path, paint(rgb(40, 38, 36, 200), stroke=2.5))
    if crack > 0:
        cr = [(cx - w * 0.42, cy - h * 0.02), (cx - w * 0.2, cy - h * 0.12), (cx - w * 0.05, cy + h * 0.02), (cx + w * 0.12, cy - h * 0.16),
              (cx + w * 0.3, cy - h * 0.04), (cx + w * 0.44, cy - h * 0.12)]
        pp = skia.Path(); pp.moveTo(*cr[0])
        for q in cr[1:]:
            pp.lineTo(*q)
        c.drawPath(pp, blur_paint(rgb(255, 200, 90, 230), 10))
        c.drawPath(pp, paint(rgb(255, 244, 200), stroke=5))
        for (a, b) in (((cx + w * 0.12, cy - h * 0.16), (cx + w * 0.08, cy - h * 0.34)), ((cx - w * 0.05, cy + h * 0.02), (cx - w * 0.1, cy + h * 0.2))):
            c.drawLine(*a, *b, paint(rgb(255, 238, 190), stroke=4))


def hands_hold(c, right=True, left=True):
    if left:
        c.drawPath(poly([(-40, 1960), (230, 1960), (170, 1330), (40, 1300)]), paint(ROBE_LT))
        c.drawPath(poly([(40, 1300), (170, 1330), (174, 1370), (36, 1342)]), paint(TRIM))
        c.drawPath(smooth_path([(52, 1300), (84, 1236), (130, 1226), (168, 1262), (172, 1320), (110, 1334)]), paint(SKIN))
        c.drawPath(smooth_path([(120, 1236), (150, 1196), (176, 1204), (160, 1250)]), paint(SKIN_DK))
    if right:
        c.drawPath(poly([(870, 1960), (1120, 1960), (1080, 1300), (930, 1320)]), paint(ROBE_LT))
        c.drawPath(poly([(930, 1320), (1080, 1300), (1084, 1344), (926, 1360)]), paint(TRIM))
        c.drawPath(smooth_path([(930, 1322), (940, 1250), (990, 1224), (1044, 1240), (1060, 1300), (1000, 1330)]), paint(SKIN))
        c.drawPath(smooth_path([(950, 1250), (930, 1206), (952, 1192), (976, 1236)]), paint(SKIN_DK))


def caption(c, s):
    text(c, s, W / 2, 1368, TF_OSWALD, 44, BONE, align='center', shadow=True)


def tally(c, n=10, x0=920, y0=430):
    for g in range(math.ceil(n / 5)):
        y = y0 + g * 80
        k = min(5, n - g * 5)
        for i in range(min(k, 4)):
            c.drawLine(x0 + i * 12, y, x0 + i * 12 + 2, y + 52, paint(C(INK, 210), stroke=3.5))
        if k == 5:
            c.drawLine(x0 - 8, y + 44, x0 + 50, y + 8, paint(C(INK, 210), stroke=3.5))


def stamp_mark(c, x, y, alpha=225):
    c.save(); c.translate(x, y); c.rotate(-9)
    f = skia.Font(TF_CINZEL_B, 64)
    w = f.measureText('FAILED')
    c.drawRoundRect(skia.Rect(-w / 2 - 22, -64, w / 2 + 22, 18), 8, 8, paint(C(GLUT, alpha), stroke=6))
    c.drawString('FAILED', -w / 2, 0, f, paint(C(GLUT, alpha)))
    # worn ink speckles
    rng = np.random.default_rng(5)
    for _ in range(70):
        c.drawCircle(rng.uniform(-w / 2 - 20, w / 2 + 20), rng.uniform(-60, 14), rng.uniform(1, 3.2), paint(rgb(228, 208, 168, 150)))
    c.restore()


def sparkle(c, x, y, r, col, a=255):
    p = skia.Path()
    for k in range(8):
        ang = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.3
        (p.moveTo if k == 0 else p.lineTo)(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
    p.close()
    c.drawPath(p, paint(C(col, a)))


def puff(c, x, y, r, a=110):
    for dx, dy, rr in ((0, 0, 1.0), (-0.7, 0.3, 0.7), (0.7, 0.25, 0.75), (0.1, -0.5, 0.6)):
        c.drawCircle(x + dx * r, y + dy * r, rr * r, blur_paint(rgb(150, 144, 136, a), 4))


def mage(c, x, y, s, col, arms=True):
    robe = smooth_path([(x - 30 * s, y), (x - 18 * s, y - 60 * s), (x - 10 * s, y - 92 * s), (x + 10 * s, y - 92 * s), (x + 18 * s, y - 60 * s), (x + 30 * s, y)])
    shadowed(c, robe, C(col), off=(5, 5), sigma=4, alpha=60)
    c.drawCircle(x, y - 104 * s, 17 * s, paint(rgb(max(col[0] - 20, 0), max(col[1] - 20, 0), max(col[2] - 20, 0))))
    c.drawPath(poly([(x - 18 * s, y - 100 * s), (x, y - 138 * s), (x + 18 * s, y - 100 * s)]), paint(rgb(50, 50, 64)))
    if arms:
        c.drawLine(x - 14 * s, y - 70 * s, x - 34 * s, y - 112 * s, paint(rgb(60, 60, 76), stroke=8 * s))
        c.drawLine(x + 14 * s, y - 70 * s, x + 34 * s, y - 112 * s, paint(rgb(60, 60, 76), stroke=8 * s))


def flames(c, x, y, w, h, cols=((196, 83, 46), (238, 150, 64), (252, 222, 160)), n=3, seed=0, a=255):
    rng = np.random.default_rng(seed)
    for k, col in enumerate(cols):
        sc = 1.0 - 0.28 * k
        for j in range(n):
            ox = (j - (n - 1) / 2) * w / n * 1.05 * sc
            hh = h * sc * rng.uniform(0.65, 1.05)
            ww = w / n * 0.9 * sc
            sway = rng.uniform(-0.25, 0.25) * ww
            pts = [(x + ox - ww, y), (x + ox - ww * 0.55 + sway * 0.3, y - hh * 0.45), (x + ox + sway, y - hh),
                   (x + ox + ww * 0.55 + sway * 0.3, y - hh * 0.5), (x + ox + ww, y)]
            c.drawPath(smooth_path(pts), paint(C(col, a)))


def additive_glow(c, x, y, r, col, a):
    g = skia.GradientShader.MakeRadial(skia.Point(x, y), r, [C(col, a), C(col, 0)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=g, BlendMode=skia.BlendMode.kPlus))


def plank(c, x0, y0, x1, y1, wdt=22, col=(150, 104, 62)):
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang) * wdt / 2, math.cos(ang) * wdt / 2
    p = poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
    shadowed(c, p, C(col), off=(4, 5), sigma=3, alpha=70)
    c.drawLine(x0 + nx * 0.2, y0 + ny * 0.2, x1 + nx * 0.2, y1 + ny * 0.2, paint(rgb(118, 80, 46, 160), stroke=1.6))
    for u in (0.12, 0.88):
        c.drawCircle(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, 4, paint(rgb(70, 70, 76)))


def dashed(c, pts, col, w=2.5, dash=(14, 10), closed=False):
    p = smooth_path(pts, closed=closed)
    pp = paint(col, stroke=w)
    pp.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawPath(p, pp)


def label_box(c, s, x, y, col=INK):
    f = skia.Font(TF_OSWALD, 26)
    w = f.measureText(s)
    c.drawRoundRect(skia.Rect(x - w / 2 - 12, y - 28, x + w / 2 + 12, y + 10), 6, 6, paint(rgb(236, 222, 190)))
    c.drawRoundRect(skia.Rect(x - w / 2 - 12, y - 28, x + w / 2 + 12, y + 10), 6, 6, paint(C(col, 220), stroke=2.5))
    c.drawString(s, x - w / 2, y, f, paint(C(col)))


def hatchling(c, x, y, s, flip=False, wing=0.0, accent=GLUT, rot=0):
    # warm halo so the small dark creature reads against the night
    c.drawCircle(x, y - 10 * s, 95 * s, blur_paint(C(accent, 70), 30 * s))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(-s if flip else s, s)
    body = rgb(84, 64, 60)
    # far wing
    w_up = -60 - 50 * wing
    c.drawPath(poly([(-6, -8), (-40, w_up + 6), (-4, w_up - 20), (30, -14)]), paint(rgb(70, 52, 50)))
    # tail
    c.drawPath(smooth_path([(-30, 4), (-70, 18), (-100, 6), (-116, -8), (-96, 14), (-66, 30), (-26, 18)]), paint(body))
    c.drawPath(poly([(-116, -8), (-128, -20), (-120, 2)]), paint(C(accent)))
    # body
    c.drawOval(skia.Rect(-40, -24, 34, 26), paint(body))
    c.drawOval(skia.Rect(-20, 0, 26, 24), paint(C(accent, 200)))
    # neck + head
    c.drawPath(smooth_path([(16, -10), (36, -38), (52, -52), (66, -50), (60, -34), (40, -12), (28, 8)]), paint(body))
    c.drawPath(smooth_path([(50, -60), (78, -62), (96, -52), (92, -42), (68, -40), (52, -44)]), paint(body))
    c.drawPath(poly([(54, -58), (44, -76), (62, -62)]), paint(C(accent)))
    c.drawCircle(70, -53, 4.5, paint(rgb(255, 214, 120)))
    # legs
    c.drawLine(-14, 20, -18, 40, paint(body, stroke=8)); c.drawLine(14, 20, 16, 40, paint(body, stroke=8))
    # near wing with fingers
    tip = (-10 - 20 * wing, w_up - 10)
    c.drawPath(poly([(0, -12), tip, (-50, w_up + 40), (-60, -6)]), paint(rgb(88, 62, 58)))
    c.drawLine(0, -12, *tip, paint(body, stroke=5))
    c.drawLine(*tip, -50, w_up + 40, paint(body, stroke=3))
    c.restore()


def finish(surf, name, grain=True):
    a = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.32 * np.clip(np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2) - 0.35, 0, 1) ** 1.4
    a = a * v[..., None]
    if grain:
        a += np.random.default_rng(len(name)).normal(0, 4, (H, W, 1))
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(f'/home/claude/short1/frames/{name}.png')


def new():
    s = skia.Surface(W, H)
    return s, s.getCanvas()


# ------------------------------------------------------------------ panels
def p1():
    s, c = new()
    background_book(c)
    lap(c)
    book(c)
    running_head(c)
    # page still flapping over on the left
    c.drawPath(smooth_path([(196, 250), (120, 330), (40, 520), (0, 760), (60, 700), (140, 520), (196, 420)]), paint(rgb(236, 220, 186)))
    for k in range(3):
        c.drawArc(skia.Rect(-60 - k * 30, 300 + k * 20, 200, 900 - k * 20), 200, 60, False, paint(rgb(236, 220, 186, 120 - 30 * k), stroke=3))
    text(c, '150 YEARS', 580, 520, TF_CINZEL_B, 108, INK, align='center')
    text(c, '0 DRAGONS', 580, 640, TF_CINZEL_B, 88, INK, align='center')
    c.drawLine(430, 672, 730, 672, paint(C(GLUT, 200), stroke=5))
    egg(c, 590, 920)
    # pop-up motion ticks
    for dx in (-130, 130):
        c.drawLine(590 + dx, 900, 590 + dx * 1.25, 860, paint(C(INK, 150), stroke=4))
    hands_hold(c)
    caption(c, 'For almost a hundred and fifty years,')
    finish(s, 'sb_1')


def p2():
    s, c = new()
    background_book(c)
    lap(c)
    book(c)
    running_head(c)
    text(c, '150 YEARS', 580, 520, TF_CINZEL_B, 108, INK, align='center', alpha=235)
    text(c, '0 DRAGONS', 580, 640, TF_CINZEL_B, 88, INK, align='center', alpha=235)
    c.drawLine(430, 672, 730, 672, paint(C(GLUT, 200), stroke=5))
    tally(c, 9, 910, 420)
    egg(c, 400, 990)
    for k in range(3):
        c.drawArc(skia.Rect(260 - k * 18, 850 - k * 18, 540 + k * 18, 1130 + k * 18), 190, 40, False, paint(C(INK, 140 - 35 * k), stroke=3))
        c.drawArc(skia.Rect(260 - k * 18, 850 - k * 18, 540 + k * 18, 1130 + k * 18), 310, 40, False, paint(C(INK, 140 - 35 * k), stroke=3))
    stamp_mark(c, 590, 1200)
    # the stamp, just lifted off the page
    sx, sy = 730, 1040
    c.drawOval(skia.Rect(sx - 120, sy + 40, sx + 120, sy + 70), blur_paint(rgb(30, 18, 10, 90), 10))
    c.drawRoundRect(skia.Rect(sx - 110, sy - 30, sx + 110, sy + 8), 8, 8, paint(rgb(120, 40, 26)))
    c.drawRoundRect(skia.Rect(sx - 120, sy - 60, sx + 120, sy - 28), 8, 8, paint(rgb(126, 88, 52)))
    c.drawPath(smooth_path([(sx - 26, sy - 60), (sx - 30, sy - 110), (sx - 46, sy - 140), (sx, sy - 172), (sx + 46, sy - 140), (sx + 30, sy - 110), (sx + 26, sy - 60)]), paint(rgb(150, 108, 64)))
    for k in range(3):
        c.drawLine(sx - 80 + k * 80, sy + 22, sx - 76 + k * 80, sy + 40, paint(C(INK, 150), stroke=3))
    # right arm reaching in from below, fist around the knob
    c.drawPath(poly([(880, 1960), (1120, 1960), (1120, 1480), (880, 930), (790, 990)]), paint(ROBE_LT))
    c.drawPath(poly([(770, 976), (872, 918), (896, 966), (792, 1030)]), paint(TRIM))
    c.drawPath(smooth_path([(700, 880), (730, 846), (790, 846), (826, 880), (820, 950), (770, 980), (712, 960)]), paint(SKIN))
    for k in range(3):
        c.drawLine(716, 878 + k * 24, 760, 880 + k * 24, paint(SKIN_DK, stroke=3))
    hands_hold(c, right=False)
    caption(c, 'Every single attempt failed.')
    finish(s, 'sb_2')


def waves(c, y0):
    cols = [(92, 112, 128), (112, 134, 148), (78, 98, 114)]
    for k, col in enumerate(cols):
        y = y0 + k * 46
        pts = [(196, y + 60)]
        for i in range(12):
            x = 196 + i * 72
            pts.append((x, y + (0 if i % 2 == 0 else 26)))
        pts += [(990, y + 20), (990, y + 90), (196, y + 90)]
        shadowed(c, smooth_path(pts), C(col), off=(0, -6), sigma=5, alpha=70)
    # pull tab
    c.drawPath(poly([(986, y0 + 40), (1060, y0 + 40), (1070, y0 + 62), (1060, y0 + 84), (986, y0 + 84)]), paint(rgb(214, 196, 158)))
    c.drawPath(poly([(1010, y0 + 52), (1040, y0 + 62), (1010, y0 + 72)]), paint(C(INK, 180)))


def ship(c, x, y, s=1.0):
    hull = smooth_path([(x - 110 * s, y - 40 * s), (x + 120 * s, y - 40 * s), (x + 80 * s, y + 10 * s), (x - 80 * s, y + 10 * s)])
    shadowed(c, hull, rgb(96, 62, 40), off=(5, 6), sigma=4)
    c.drawLine(x, y - 40 * s, x, y - 230 * s, paint(rgb(80, 54, 36), stroke=7 * s))
    sail = smooth_path([(x + 6 * s, y - 220 * s), (x + 110 * s, y - 190 * s), (x + 100 * s, y - 110 * s), (x + 6 * s, y - 70 * s)])
    shadowed(c, sail, rgb(236, 226, 204), off=(5, 6), sigma=4)


def p3():
    s, c = new()
    background_book(c)
    lap(c)
    book(c)
    running_head(c)
    tally(c, 9, 900, 420)
    waves(c, 1080)
    ship(c, 330, 1090, 0.9)
    cx, cy, rx, ry = 600, 890, 300, 84
    cols = [(70, 74, 92), (86, 80, 104), (64, 70, 84), (92, 86, 110), (74, 78, 98), (84, 76, 96), (68, 72, 90), (90, 84, 104), (78, 72, 94)]
    order = sorted(range(9), key=lambda i: math.sin(2 * math.pi * i / 9 + 0.4))
    drawn_egg = False
    for i in order:
        a = 2 * math.pi * i / 9 + 0.4
        if math.sin(a) > -0.05 and not drawn_egg:
            egg(c, cx, cy - 40)
            drawn_egg = True
        x, y = cx + rx * math.cos(a), cy + 40 + ry * math.sin(a)
        mage(c, x, y, 1.2 + 0.15 * math.sin(a), cols[i])
        sparkle(c, x - 40, y - 160, 16, GOLD, 210)
        sparkle(c, x + 42, y - 152, 11, GOLD, 160)
        puff(c, x + 4, y - 188, 20, 90)
    if not drawn_egg:
        egg(c, cx, cy - 40)
    hands_hold(c)
    caption(c, 'brought nine mages from across the sea.')
    finish(s, 'sb_3')


def wood_dragon(c, cx, cy, sag=0.0):
    col = (150, 104, 62)
    # legs
    for x in (cx - 170, cx - 90, cx + 90, cx + 170):
        plank(c, x, cy + 60, x + 6, cy + 190, 20)
    # body planks
    for k in range(3):
        plank(c, cx - 230, cy - 20 + k * 30, cx + 200, cy - 30 + k * 30, 26, (158 - k * 10, 110 - k * 6, 66))
    # neck + drooping head
    plank(c, cx + 180, cy - 20, cx + 290, cy - 250, 26)
    hx, hy = cx + 290, cy - 250
    head = poly([(hx - 10, hy - 30), (hx + 90, hy - 10 + sag * 50), (hx + 96, hy + 20 + sag * 60), (hx - 6, hy + 26)])
    shadowed(c, head, C(col), off=(4, 5), sigma=3)
    c.drawCircle(hx + 40, hy - 4 + sag * 20, 6, paint(rgb(40, 40, 44)))
    # tail
    plank(c, cx - 230, cy + 10, cx - 380, cy + 90, 20)
    # wings: sailcloth stretched over thin ribs, one sagging
    for (root, tip, rear, cloth, droop) in (((cx - 20, cy - 36), (cx + 40, cy - 380), (cx - 240, cy - 40), (170, 146, 110), 0),
                                            ((cx - 60, cy - 30), (cx - 190, cy - 330), (cx - 300, cy - 10), (150, 128, 96), 40)):
        tip = (tip[0], tip[1] + droop)
        n = 3
        sc = []
        for i in range(1, n + 1):
            u = i / (n + 1)
            sc.append((tip[0] + (rear[0] - tip[0]) * u, tip[1] + (rear[1] - tip[1]) * u))
        edge = [root, tip]
        prev = tip
        for q in sc + [rear]:
            mid = ((prev[0] + q[0]) / 2 + 18, (prev[1] + q[1]) / 2 + 30)
            edge += [mid, q]
            prev = q
        shadowed(c, poly(edge), C(cloth), off=(5, 7), sigma=5, alpha=70)
        for q in [tip] + sc:
            plank(c, root[0], root[1], q[0], q[1], 10, (128, 88, 54))
    # iron bands
    for x in (cx - 150, cx - 20, cx + 110):
        c.drawRect(skia.Rect(x, cy - 40, x + 18, cy + 60), paint(rgb(70, 72, 78)))
        for yy in (cy - 30, cy + 10, cy + 48):
            c.drawCircle(x + 9, yy, 4, paint(rgb(170, 172, 176)))


def p4():
    s, c = new()
    background_book(c)
    lap(c)
    book(c)
    running_head(c)
    tally(c, 9, 900, 420)
    # construction lines drawn by the candle smoke
    dashed(c, [(300, 900), (320, 780), (380, 660), (470, 560), (560, 520), (640, 540)], C(INK, 170), 3)
    dashed(c, [(360, 960), (600, 930), (840, 900), (900, 760), (880, 600)], C(INK, 150), 3)
    c.drawLine(420, 1110, 800, 1110, paint(C(INK, 150), stroke=2))
    c.drawLine(420, 1096, 420, 1124, paint(C(INK, 150), stroke=2)); c.drawLine(800, 1096, 800, 1124, paint(C(INK, 150), stroke=2))
    wood_dragon(c, 600, 930, sag=0.6)
    egg(c, 560, 1010, 150, 196)
    # candle, just blown out, smoke curling into the lines
    c.drawOval(skia.Rect(250, 1060, 370, 1090), paint(rgb(170, 130, 70)))
    c.drawRect(skia.Rect(290, 930, 330, 1072), paint(rgb(234, 226, 206)))
    c.drawLine(310, 930, 310, 910, paint(rgb(40, 34, 30), stroke=3))
    sm = skia.Path(); sm.moveTo(310, 905); sm.cubicTo(280, 860, 340, 830, 300, 780); sm.cubicTo(270, 740, 320, 700, 300, 900 - 250)
    c.drawPath(sm, blur_paint(rgb(160, 156, 150, 170), 3))
    c.drawPath(sm, paint(rgb(160, 156, 150, 190), stroke=6))
    label_box(c, 'OAK', 420, 690)
    label_box(c, 'IRON', 810, 1040)
    hands_hold(c)
    caption(c, 'built dragons out of wood and iron.')
    finish(s, 'sb_4')


def heap(c, cx, cy):
    rng = np.random.default_rng(4)
    for k in range(9):
        x0 = cx + rng.uniform(-150, 60); y0 = cy + rng.uniform(-40, 30)
        ang = rng.uniform(-0.6, 0.6)
        ln = rng.uniform(120, 220)
        plank(c, x0, y0, x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln, 22, (140 - k * 4, 96 - k * 3, 58))


def p5():
    s, c = new()
    background_book(c, 1.4)
    lap(c)
    book(c)
    running_head(c)
    tally(c, 9, 900, 420)
    heap(c, 380, 1040)
    egg(c, 610, 930, 150, 196)
    flames(c, 360, 1060, 260, 230, seed=2)
    flames(c, 430, 1040, 150, 200, cols=((60, 150, 60), (120, 226, 104), (210, 255, 190)), seed=3, a=235)
    # goblet
    gob = smooth_path([(780, 1120), (900, 1120), (870, 1100), (850, 1060), (848, 1010), (900, 960), (906, 900), (774, 900), (780, 960), (832, 1010), (830, 1060), (810, 1100)])
    shadowed(c, gob, rgb(170, 160, 150), off=(5, 6), sigma=4)
    c.drawOval(skia.Rect(774, 888, 906, 914), paint(rgb(60, 110, 60)))
    # green jet arcing into the heap
    jet = skia.Path(); jet.moveTo(840, 900); jet.cubicTo(800, 640, 560, 700, 450, 980)
    for wdt, col, sg in ((60, (70, 190, 80, 120), 18), (34, (120, 230, 110, 220), 8), (12, (225, 255, 210, 255), 3)):
        p = blur_paint(rgb(*col), sg); p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(wdt); p.setStrokeCap(skia.Paint.kRound_Cap)
        c.drawPath(jet, p)
    additive_glow(c, 450, 1000, 500, (90, 200, 90), 70)
    additive_glow(c, 380, 1050, 420, (230, 120, 50), 80)
    hands_hold(c)
    caption(c, 'Aerion drank wildfire, and burned.')
    finish(s, 'sb_5')


def wobbly(cx, cy, r, seed, n=40, amp=0.16):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 4)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + amp * (math.sin(3 * a + ph[0]) * 0.5 + math.sin(5 * a + ph[1]) * 0.3 + math.sin(9 * a + ph[2]) * 0.2))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 1.15))
    return smooth_path(pts)


def plate_summerhall(c, x0, y0, x1, y1):
    g = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [rgb(22, 16, 22), rgb(90, 36, 22), rgb(40, 20, 16)], [0, 0.62, 1])
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=g))
    cx = (x0 + x1) / 2
    base = y0 + (y1 - y0) * 0.72
    castle = [(x0, base + 30), (x0 + 60, base), (cx - 170, base), (cx - 170, base - 150), (cx - 140, base - 150), (cx - 140, base - 110),
              (cx - 60, base - 110), (cx - 60, base - 250), (cx - 20, base - 250), (cx - 20, base - 120), (cx + 50, base - 120),
              (cx + 50, base - 190), (cx + 90, base - 190), (cx + 90, base - 90), (cx + 170, base - 90), (cx + 170, base), (x1, base + 20), (x1, y1), (x0, y1)]
    flames(c, cx - 40, base - 60, 420, 360, seed=6, a=235)
    flames(c, cx + 140, base - 40, 200, 240, seed=7, a=220)
    c.drawPath(poly(castle), paint(rgb(18, 12, 12)))
    additive_glow(c, cx, base - 120, 380, (240, 120, 50), 90)
    c.drawRect(skia.Rect(x0, y0, x1, y1), paint(rgb(150, 110, 60), stroke=6))


def storyboard_tag(c, s, x, y):
    f = skia.Font(TF_OSWALD, 30)
    w = f.measureText(s)
    c.drawRoundRect(skia.Rect(x, y - 32, x + w + 28, y + 14), 22, 22, paint(rgb(158, 211, 228, 235)))
    c.drawString(s, x + 14, y, f, paint(rgb(20, 30, 40)))


def p6():
    s, c = new()
    background_book(c, 1.6)
    lap(c)
    book(c)
    hole = wobbly(590, 760, 330, 11)
    c.save(); c.clipPath(hole, doAntiAlias=True)
    c.drawRect(skia.Rect(0, 0, W, H), paint(rgb(12, 10, 10)))
    plate_summerhall(c, 290, 380, 890, 1130)
    c.drawRect(skia.Rect(350, 648, 830, 694), paint(rgb(222, 204, 164)))
    text(c, 'PLATE I  ·  SUMMERHALL, 259 AC', 590, 682, TF_FELL_SC, 30, INK, align='center')
    c.restore()
    # charred ring + glowing edge
    ring = paint(rgb(60, 30, 16, 230), stroke=34); c.drawPath(hole, blur_paint(rgb(50, 26, 14, 200), 14))
    c.drawPath(hole, ring)
    c.drawPath(hole, paint(rgb(255, 150, 60), stroke=7))
    ge = skia.Paint(AntiAlias=True, Color=rgb(255, 190, 90), Style=skia.Paint.kStroke_Style, StrokeWidth=16)
    ge.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    c.drawPath(hole, ge)
    for (x, y) in ((300, 620), (870, 560), (340, 980), (860, 1000), (560, 360)):
        flames(c, x, y, 90, 110, seed=int(x), a=230)
    egg(c, 590, 1150, 150, 196, base=False)
    rim = skia.GradientShader.MakeRadial(skia.Point(590, 900), 420, [rgb(255, 150, 70, 150), rgb(0, 0, 0, 0)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=rim, BlendMode=skia.BlendMode.kPlus))
    storyboard_tag(c, 'DEIN KI-BILD', 670, 1010)
    hands_hold(c)
    caption(c, 'the last attempt ended in flames.')
    finish(s, 'sb_6')


def plate_pyre(c, x0, y0, x1, y1):
    g = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [rgb(16, 16, 26), rgb(70, 34, 24), rgb(30, 22, 18)], [0, 0.66, 1])
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=g))
    cx = (x0 + x1) / 2
    base = y0 + (y1 - y0) * 0.74
    c.drawRect(skia.Rect(x0, base + 40, x1, y1), paint(rgb(26, 20, 18)))
    for k in range(6):
        c.drawRoundRect(skia.Rect(cx - 170 + k * 8, base - k * 26, cx + 170 - k * 8, base - k * 26 + 22), 8, 8, paint(rgb(70 + k * 4, 44, 30)))
    flames(c, cx, base - 120, 360, 420, seed=9)
    additive_glow(c, cx, base - 200, 360, (240, 130, 60), 100)
    # a figure seen from behind walking into the fire
    fx, fy = cx - 30, base + 34
    c.drawPath(smooth_path([(fx - 26, fy), (fx - 18, fy - 90), (fx - 8, fy - 130), (fx + 10, fy - 130), (fx + 20, fy - 90), (fx + 28, fy)]), paint(rgb(14, 10, 10)))
    c.drawCircle(fx + 1, fy - 146, 17, paint(rgb(14, 10, 10)))
    c.drawRect(skia.Rect(x0, y0, x1, y1), paint(rgb(150, 110, 60), stroke=6))


def p7():
    s, c = new()
    c.drawRect(skia.Rect(0, 0, W, H), paint(rgb(8, 8, 10)))
    # the ember that fell
    dashed(c, [(760, 0), (740, 120), (700, 240), (660, 320)], rgb(255, 170, 80, 150), 3, (10, 14))
    x0, y0, x1, y1 = 250, 380, 830, 1105
    plate_pyre(c, x0, y0, x1, y1)
    c.drawRect(skia.Rect(370, 968, 710, 1014), paint(rgb(222, 204, 164)))
    text(c, 'PLATE II  ·  THE PYRE', 540, 1002, TF_FELL_SC, 30, INK, align='center')
    # flames breaking out of the plate onto the page
    flames(c, 540, 400, 420, 260, seed=12, a=240)
    flames(c, 250, 700, 120, 170, seed=13, a=220)
    flames(c, 830, 760, 120, 190, seed=14, a=220)
    egg(c, 540, 1215, 140, 180, glow=1.0, crack=1.0, base=False)
    for k in range(10):
        a = -math.pi / 2 + (k - 4.5) * 0.28
        c.drawLine(540 + math.cos(a) * 118, 1205 + math.sin(a) * 118, 540 + math.cos(a) * 168, 1205 + math.sin(a) * 168, paint(rgb(255, 214, 120, 120), stroke=5))
    additive_glow(c, 540, 1210, 420, (255, 190, 90), 110)
    storyboard_tag(c, 'DEIN KI-BILD', 290, 460)
    caption(c, 'and walks out with three dragons.')
    finish(s, 'sb_7')


STARS = [(np.random.default_rng(i).uniform(0, W), np.random.default_rng(i + 500).uniform(0, 1250), np.random.default_rng(i + 900).uniform(1.2, 3.2)) for i in range(230)]


def night(c, horizon=1320):
    g = skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, horizon)], [rgb(10, 13, 24), rgb(46, 40, 58)])
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=g))
    for (x, y, r) in STARS:
        if y < horizon - 60:
            c.drawCircle(x, y, r, paint(rgb(230, 223, 208, 190)))
    c.drawPath(smooth_path([(-40, horizon - 30), (220, horizon - 90), (480, horizon - 50), (760, horizon - 110), (1120, horizon - 60), (1120, horizon + 200), (-40, horizon + 200)]), paint(rgb(34, 36, 48)))
    c.drawRect(skia.Rect(0, horizon + 60, W, H), paint(rgb(22, 22, 26)))
    c.drawPath(smooth_path([(-40, horizon + 90), (400, horizon + 40), (1120, horizon + 80), (1120, H + 10), (-40, H + 10)]), paint(rgb(22, 22, 26)))


def campfire(c, fx, fy, sc=1.0):
    additive_glow(c, fx, fy - 30, 700 * sc, (170, 76, 26), 120)
    for k in range(7):
        a = math.pi * (0.05 + 0.9 * k / 6)
        c.drawOval(skia.Rect(fx + math.cos(a) * 100 * sc - 28 * sc, fy + 10 * sc, fx + math.cos(a) * 100 * sc + 28 * sc, fy + 42 * sc), paint(rgb(58, 60, 66)))
    for ang in (-18, 16):
        c.save(); c.translate(fx, fy + 12 * sc); c.rotate(ang)
        c.drawRoundRect(skia.Rect(-100 * sc, -13 * sc, 100 * sc, 13 * sc), 10, 10, paint(rgb(70, 46, 32)))
        c.restore()
    flames(c, fx, fy + 6 * sc, 150 * sc, 240 * sc, seed=21)


def hand_pos(p, x, y, sc):
    def rot(v, deg):
        a = math.radians(deg)
        return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))
    sh = Starseer.SH_NEAR
    a1 = rot((108, 0), p.ua)
    a2 = rot((96, 0), p.ua + p.fa)
    loc = (sh[0] + a1[0] + a2[0], sh[1] + a1[1] + a2[1])
    loc = rot(loc, p.lean)
    return x + loc[0] * sc, y + loc[1] * sc


def small_book(c, x, y, label, rot=-12):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawRoundRect(skia.Rect(-46, -60, 46, 60), 6, 6, paint(rgb(110, 40, 30)))
    c.drawRect(skia.Rect(-40, -54, 40, 54), paint(rgb(140, 56, 40)))
    c.drawRect(skia.Rect(-12, -10, 12, 16), paint(C(GOLD)))
    c.restore()
    label_box(c, label, x, y - 84)


def p8():
    s, c = new()
    night(c, 1330)
    campfire(c, 820, 1520, 1.1)
    st = Starseer()
    p = Pose(lean=-8, head=-14, brow_y=1.1, brow_ang=0.7, eye_s=1.35, look=0.9, mouth=0.35, smile=0.0,
             ua=-58, fa=-38, hand=0, wrist=0, scroll=0.0, far_ua=74, far_fa=-80, wind=1.0, hair_sway=4)
    hx, hy, sc = 380, 1420, 1.25
    c.drawOval(skia.Rect(hx - 280, hy + 150, hx + 360, hy + 230), paint(rgb(8, 8, 10, 150)))
    # rock seat
    c.drawPath(smooth_path([(hx - 170, hy + 20), (hx - 60, hy - 10), (hx + 150, hy - 6), (hx + 230, hy + 40), (hx + 250, hy + 190), (hx - 190, hy + 196)]), paint(rgb(62, 66, 76)))
    c.saveLayer()
    st.draw(c, p, hx, hy, sc)
    fl = skia.Paint(BlendMode=skia.BlendMode.kSrcATop, Shader=skia.GradientShader.MakeRadial(skia.Point(820, 1440), 700, [rgb(255, 150, 70, 110), rgb(255, 120, 40, 0)]))
    c.drawRect(skia.Rect(0, 0, W, H), fl)
    c.restore()
    bx, by = hand_pos(p, hx, hy, sc)
    small_book(c, bx + 10, by - 30, 'KNOWLEDGE?')
    # throw arc
    dashed(c, [(bx + 60, by - 40), (bx + 220, by - 160), (760, 1200), (810, 1380)], rgb(230, 223, 208, 130), 3)
    # hatchlings circling the head
    headx, heady = hx + 50 * sc, hy - 330 * sc
    for (dx, dy, fl_, acc, sc2, rot) in ((-250, -60, True, GLUT, 1.45, -10), (200, -230, False, GOLD, 1.35, 8), (190, 130, False, BONE, 1.2, -18)):
        hatchling(c, headx + dx, heady + dy, sc2, flip=fl_, wing=0.8, accent=acc, rot=rot)
    orbit = skia.Rect(headx - 320, heady - 300, headx + 320, heady + 220)
    pp = paint(rgb(230, 223, 208, 90), stroke=3); pp.setPathEffect(skia.DashPathEffect.Make([18, 14], 0))
    c.drawOval(orbit, pp)
    caption(c, 'Not because she knew something they didn\'t.')
    finish(s, 'sb_8')


def p9():
    s, c = new()
    night(c, 1560)
    # constellation: the sawtooth tide
    pts = [(80, 1060), (170, 520), (330, 640), (520, 800), (690, 930), (760, 610), (820, 380)]
    labels = {1: 'LONG NIGHT', 4: '259 AC', 6: '298 AC'}
    for a, b in zip(pts[:-1], pts[1:]):
        c.drawLine(*a, *b, paint(rgb(216, 179, 92, 170), stroke=3))
    for i, (x, y) in enumerate(pts):
        c.drawCircle(x, y, 18, blur_paint(rgb(255, 230, 170, 120), 8))
        c.drawCircle(x, y, 6.5, paint(rgb(255, 244, 214)))
    text(c, 'LONG NIGHT', 190, 486, TF_CINZEL, 30, BONE, alpha=210)
    text(c, 'SUMMERHALL · 259 AC', 520, 1000, TF_CINZEL, 28, BONE, alpha=200)
    text(c, '298 AC', 790, 360, TF_CINZEL, 30, BONE, align='right', alpha=220)
    # comet on the rising flank
    hx, hy = 790, 500
    tx, ty = 1180, 150
    ang = math.atan2(ty - hy, tx - hx)
    nx, ny = -math.sin(ang), math.cos(ang)
    for k, (wd, col, al) in enumerate(((70, (200, 70, 50), 0.55), (40, (240, 150, 70), 0.75), (16, (255, 225, 170), 0.95))):
        path = poly([(hx + nx * wd * 0.5, hy + ny * wd * 0.5), (tx + nx * wd * 2.2, ty + ny * wd * 2.2), (tx - nx * wd * 0.6, ty - ny * wd * 0.6), (hx - nx * wd * 0.5, hy - ny * wd * 0.5)])
        sh_ = skia.GradientShader.MakeLinear([skia.Point(hx, hy), skia.Point(tx, ty)], [rgb(*col, int(255 * al)), rgb(*col, 0)])
        pp = skia.Paint(AntiAlias=True, Shader=sh_); pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8 + 4 * (2 - k)))
        c.drawPath(path, pp)
    additive_glow(c, hx, hy, 260, (255, 120, 60), 110)
    c.drawCircle(hx, hy, 16, blur_paint(rgb(255, 238, 205), 4))
    # the storyteller, small, looking up
    campfire(c, 800, 1760, 0.8)
    st = Starseer()
    p = Pose(lean=-4, head=-34, brow_y=0.6, eye_s=1.15, look=0.8, ua=-40, fa=-40, hand=1, scroll=0.0, wind=2.0)
    c.saveLayer()
    st.draw(c, p, 400, 1690, 0.78)
    fl = skia.Paint(BlendMode=skia.BlendMode.kSrcATop, Shader=skia.GradientShader.MakeRadial(skia.Point(800, 1700), 600, [rgb(255, 150, 70, 110), rgb(255, 120, 40, 0)]))
    c.drawRect(skia.Rect(0, 0, W, H), fl)
    c.restore()
    hatchling(c, 250, 1640, 0.7, flip=True, wing=0.1, accent=GLUT, rot=-12)
    hatchling(c, 580, 1630, 0.66, wing=0.3, accent=GOLD, rot=-24)
    caption(c, 'It was the world.')
    finish(s, 'sb_9')


PANELS = [('1', '0:01', p1), ('2', '0:06', p2), ('3', '0:09', p3), ('4', '0:13', p4), ('5', '0:16', p5),
          ('6', '0:18', p6), ('7', '0:24', p7), ('8', '0:26', p8), ('9', '0:37', p9)]


def sheet():
    pw, ph = 340, 604
    gut, lab = 24, 44
    cols, rows = 3, 3
    SW = cols * pw + (cols + 1) * gut
    SH = rows * (ph + lab) + (rows + 1) * gut
    im = Image.new('RGB', (SW, SH), (20, 21, 24))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FD + 'Oswald[wght].ttf', 26)
    for i, (n, tc, _) in enumerate(PANELS):
        r, k = divmod(i, cols)
        x = gut + k * (pw + gut)
        y = gut + r * (ph + lab + gut)
        fr = Image.open(f'/home/claude/short1/frames/sb_{n}.png').resize((pw, ph), Image.LANCZOS)
        im.paste(fr, (x, y + lab))
        d.text((x, y + 6), f'{n}', font=f, fill=(216, 179, 92))
        d.text((x + 26, y + 6), f'·  {tc}', font=f, fill=(170, 164, 150))
    im.save('/home/claude/short1/storyboard.png', optimize=True)
    print(im.size)


if __name__ == '__main__' and not (len(sys.argv) > 1 and sys.argv[1] == 'loop'):
    which = sys.argv[1].split(',') if len(sys.argv) > 1 else [p[0] for p in PANELS]
    for n, _, fn in PANELS:
        if n in which:
            fn()
    sheet()


def p10():
    """last second: the closed chronicle, hands lifting the cover -> cuts into p1"""
    s, c = new()
    background_book(c)
    lap(c)
    # pages peeking out under the lifting cover
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-60, 238, 1000, 1290), 14, 14), paint(rgb(214, 196, 158)))
    for k in range(6):
        c.drawLine(990 - k * 4, 250, 990 - k * 4, 1280, paint(rgb(190, 170, 130), stroke=1.5))
    # cover, right edge lifting a little
    cover = poly([(-80, 226), (1010, 206), (1030, 1276), (-80, 1296)])
    shadowed(c, cover, rgb(78, 46, 30), off=(0, 14), sigma=12, alpha=120)
    c.save(); c.clipPath(cover, doAntiAlias=True)
    lg = skia.GradientShader.MakeLinear([skia.Point(0, 226), skia.Point(1010, 1296)], [rgb(96, 58, 38), rgb(62, 36, 24)])
    c.drawRect(skia.Rect(-100, 200, 1100, 1300), skia.Paint(Shader=lg))
    c.restore()
    gold = C(GOLD, 230)
    c.drawRect(skia.Rect(60, 330, 920, 1180), paint(gold, stroke=4))
    c.drawRect(skia.Rect(84, 354, 896, 1156), paint(C(GOLD, 150), stroke=2))
    text(c, 'THE TIDES', 490, 640, TF_CINZEL_B, 96, GOLD, align='center')
    text(c, 'OF MAGIC', 490, 750, TF_CINZEL_B, 96, GOLD, align='center')
    pts = [(380, 900), (420, 830), (520, 890), (560, 820), (620, 870)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint(gold, stroke=6))
    c.drawCircle(520, 890, 11, paint(rgb(240, 214, 140)))
    text(c, 'N° 01', 490, 1010, TF_CINZEL, 44, GOLD, align='center')
    hands_hold(c)
    finish(s, 'sb_10')


def loop_strip():
    pw, ph = 420, 746
    gap = 120
    SW, SH = 2 * pw + gap + 2 * 36, ph + 120
    im = Image.new('RGB', (SW, SH), (20, 21, 24))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FD + 'Oswald[wght].ttf', 30)
    for i, (n, lab) in enumerate((('10', 'Ende · 0:43 · Hände heben den Deckel'), ('1', 'Anfang · 0:00 · Deckel fliegt auf'))):
        x = 36 + i * (pw + gap)
        fr = Image.open(f'/home/claude/short1/frames/sb_{n}.png').resize((pw, ph), Image.LANCZOS)
        im.paste(fr, (x, 70))
        d.text((x, 18), lab, font=f, fill=(216, 179, 92) if i == 0 else (170, 164, 150))
    # arrow across the seam
    ax0, ax1, ay = 36 + pw + 18, 36 + pw + gap - 18, 70 + ph // 2
    d.line([(ax0, ay), (ax1, ay)], fill=(216, 179, 92), width=6)
    d.polygon([(ax1 + 4, ay), (ax1 - 22, ay - 16), (ax1 - 22, ay + 16)], fill=(216, 179, 92))
    im.save('/home/claude/short1/loop.png', optimize=True)
    print(im.size)


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'loop':
    p10()
    loop_strip()
