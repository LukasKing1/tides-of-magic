"""Short 1 - 'Why did every dragon egg fail for 150 years?'  (1080x1920, 30 fps, seamless loop)
python3 short1.py still 1.2,8.3,...      -> stills/s_XX.png
python3 short1.py range i0 i1 out.mp4    -> video frames [i0, i1)
"""
import math, os, sys, json, contextlib
import numpy as np
import skia
from PIL import Image

sys.path.insert(0, '/home/claude/rig')
sys.path.insert(0, '/home/claude/short1')
from starseer import Starseer, Pose, smooth_path, paint, rgb
import sb
from sb import (C, text, blur_paint, poly, shadowed, additive_glow, egg_path, sparkle, puff, mage, plank, dashed,
                label_box, hatchling, wobbly, stamp_mark, page_path, PAGE, LPAGE, PARCH_IMG,
                TF_CINZEL, TF_CINZEL_B, TF_OSWALD, TF_FELL_SC, BONE, GOLD, GLUT, INK)

W, H, FPS = 1080, 1920, 30
T_TOTAL = 53.0
D = '/home/claude/short1/'
P = skia.Point
R = skia.Rect


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ramp(t, a, b):
    return smooth((t - a) / (b - a)) if b > a else float(t >= a)


def eramp(t, a, b):
    return ease((t - a) / (b - a)) if b > a else float(t >= a)


def popout(u):
    u = clamp(u)
    c1 = 1.70158
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def popv(t, t0, dur=0.42, t1=None, d1=0.3):
    """pop-up height factor: unfolds with overshoot at t0, folds flat from t1"""
    if t < t0:
        return 0.0
    v = popout((t - t0) / dur)
    if t1 is not None and t > t1:
        v *= 1 - ease((t - t1) / d1)
    return max(v, 0.0)


@contextlib.contextmanager
def folded(c, ax, ay, s):
    c.save()
    c.translate(ax, ay)
    c.scale(1, max(s, 0.0001))
    c.translate(-ax, -ay)
    yield
    c.restore()


def flicker(t):
    return 1 + 0.08 * math.sin(t * 9.3) + 0.05 * math.sin(t * 15.1 + 1) + 0.04 * math.sin(t * 4.1)


def stroke(col, w, cap=True):
    p = paint(col, stroke=w)
    return p


# ------------------------------------------------------------------ assets
WORDS = json.load(open(D + 'words.json'))


def load_img(path):
    a = np.asarray(Image.open(path).convert('RGBA'))
    return skia.Image.fromarray(a.copy())


PLATE1 = load_img(D + 'plate1.png')
PLATE2 = load_img(D + 'plate2.png')


def charred_tex():
    rng = np.random.default_rng(31)

    def snoise(cx, cy):
        r = rng.random((cy, cx))
        return np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    n1, n2 = snoise(18, 32), snoise(90, 160)
    base = np.array([22, 16, 14], np.float32)
    col = base[None, None] * (0.7 + 0.6 * n1[..., None]) * (0.85 + 0.3 * n2[..., None]) + rng.normal(0, 1.6, (H, W, 1))
    a = np.full((H, W, 1), 255, np.float32)
    return skia.Image.fromarray(np.clip(np.concatenate([col, a], 2), 0, 255).astype(np.uint8))


CHAR_IMG = charred_tex()
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

# ------------------------------------------------------------------ Doreah (hands, lap, hair)
SKIN_D = (230, 192, 160)
SKIN_D2 = (204, 160, 128)
SILK = (98, 40, 46)
SILK_DK = (66, 26, 32)
SILK_LT = (132, 60, 64)
HAIR = (232, 212, 168)


def bg_book(c, t):
    g = skia.GradientShader.MakeLinear([P(0, 0), P(0, H)], [rgb(16, 15, 19), rgb(46, 28, 20)])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=g))
    fl = flicker(t)
    gl = skia.GradientShader.MakeRadial(P(W * 0.6, H * 1.03), 1300 * (0.96 + 0.04 * fl), [rgb(170, 80, 30, int(92 * fl)), rgb(0, 0, 0, 0)])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=gl, BlendMode=skia.BlendMode.kPlus))


def lap_d(c, t):
    c.drawPath(smooth_path([(-60, 1296), (300, 1318), (700, 1308), (1140, 1290), (1140, 1990), (-60, 1990)]), paint(C(SILK_DK)))
    for k, x in enumerate((90, 330, 600, 860)):
        sw = 8 * math.sin(t * 0.9 + k)
        c.drawPath(smooth_path([(x - 26, 1320), (x + 18 + sw, 1500), (x - 8, 1700), (x + 34 + sw, 1990), (x + 70, 1990),
                                (x + 46 + sw, 1700), (x + 64, 1480), (x + 24, 1320)]), paint(C(SILK, 230)))
        c.drawPath(smooth_path([(x + 6, 1340), (x + 30 + sw, 1520), (x + 20, 1720), (x + 44 + sw, 1990), (x + 52, 1990),
                                (x + 36 + sw, 1720), (x + 40, 1520), (x + 18, 1340)]), paint(C(SILK_LT, 120)))


def forearm(c, base, wrist, w0=120, w1=70, bangles=True):
    ang = math.atan2(wrist[1] - base[1], wrist[0] - base[0])
    nx, ny = -math.sin(ang), math.cos(ang)
    pts = [(base[0] + nx * w0 / 2, base[1] + ny * w0 / 2), (wrist[0] + nx * w1 / 2, wrist[1] + ny * w1 / 2),
           (wrist[0] - nx * w1 / 2, wrist[1] - ny * w1 / 2), (base[0] - nx * w0 / 2, base[1] - ny * w0 / 2)]
    c.drawPath(poly(pts), paint(C(SKIN_D)))
    # shading on one side
    c.drawPath(poly([pts[0], pts[1], lerp2(pts[1], pts[2], 0.3), lerp2(pts[0], pts[3], 0.3)]), paint(C(SKIN_D2, 120)))
    if bangles:
        for k in range(3):
            u = 0.80 + 0.055 * k
            cx, cy = lerp(base[0], wrist[0], u), lerp(base[1], wrist[1], u)
            ww = lerp(w0, w1, u) / 2 + 3
            c.drawLine(cx + nx * ww, cy + ny * ww, cx - nx * ww, cy - ny * ww, paint(C(GOLD), stroke=6 - k))
    # wide silk sleeve covering the upper part of the arm
    sl = 0.5
    s0 = (lerp(base[0], wrist[0], sl), lerp(base[1], wrist[1], sl))
    ws = lerp(w0, w1, sl) / 2 + 16
    ws = ws + 26
    c.drawPath(poly([(base[0] + nx * (w0 / 2 + 40), base[1] + ny * (w0 / 2 + 40)), (s0[0] + nx * ws, s0[1] + ny * ws),
                     (s0[0] - nx * ws, s0[1] - ny * ws), (base[0] - nx * (w0 / 2 + 40), base[1] - ny * (w0 / 2 + 40))]), paint(C(SILK)))
    c.drawPath(poly([(base[0] + nx * (w0 / 2 + 40), base[1] + ny * (w0 / 2 + 40)), (s0[0] + nx * ws, s0[1] + ny * ws),
                     lerp2((s0[0] + nx * ws, s0[1] + ny * ws), (s0[0] - nx * ws, s0[1] - ny * ws), 0.3),
                     lerp2((base[0] + nx * (w0 / 2 + 40), base[1] + ny * (w0 / 2 + 40)), (base[0] - nx * (w0 / 2 + 40), base[1] - ny * (w0 / 2 + 40)), 0.3)]),
               paint(C(SILK_LT, 150)))
    c.drawLine(s0[0] + nx * ws, s0[1] + ny * ws, s0[0] - nx * ws, s0[1] - ny * ws, paint(C(GOLD, 220), stroke=6))
    return ang


def hand_shape(c, wrist, ang, kind, s=1.0):
    """back of the hand seen from above; ang = direction of the forearm"""
    c.save()
    c.translate(*wrist)
    c.rotate(math.degrees(ang) + 90)  # local -y = along the arm direction
    c.scale(s, s)
    skin, dk = paint(C(SKIN_D)), paint(C(SKIN_D2))
    if kind == 'grip':  # fingers curled over the book edge, thumb on the page
        c.drawPath(smooth_path([(-36, 6), (-40, -40), (-20, -78), (20, -80), (40, -44), (36, 8)]), skin)
        for k in range(4):
            x = -27 + k * 18
            c.drawRoundRect(R(x - 8, -96, x + 8, -60), 8, 8, skin)
        c.drawPath(smooth_path([(-34, -20), (-62, -54), (-70, -84), (-56, -92), (-40, -66), (-24, -40)]), dk)
    elif kind == 'point':
        c.drawPath(smooth_path([(-34, 6), (-38, -40), (-18, -74), (20, -76), (38, -42), (34, 8)]), skin)
        c.drawRoundRect(R(-4, -150, 14, -62), 9, 9, skin)
        for k in range(3):
            x = -24 + k * 0 + (k - 1) * 16 + 6
            c.drawRoundRect(R(x - 22, -86, x - 6, -58), 8, 8, dk)
        c.drawPath(smooth_path([(-34, -18), (-56, -40), (-50, -56), (-28, -42)]), dk)
    else:  # fist (holding something)
        c.drawPath(smooth_path([(-38, 6), (-42, -36), (-24, -70), (24, -72), (42, -38), (38, 8)]), skin)
        for k in range(4):
            x = -28 + k * 19
            c.drawRoundRect(R(x - 9, -84, x + 9, -58), 8, 8, dk)
    c.restore()


def hands_d(c, t, right='grip', rpos=None, rkind='grip', lpos=None):
    """left hand near the spine, right hand at the bottom-right corner (or reaching to rpos)"""
    lw = lpos or (206, 1338)
    a = forearm(c, (-40, 1820), lw, 160, 86)
    hand_shape(c, lw, a, 'grip', 1.2)
    if right == 'none':
        return
    rw = rpos or (962, 1342)
    reach = 0.0 if rpos is None else clamp(math.hypot(rw[0] - 962, rw[1] - 1342) / 400)
    base = (lerp(1130, 1080, reach), lerp(1820, 1990, reach))
    a = forearm(c, base, rw, 164, 86)
    hand_shape(c, rw, a, rkind, 1.2)


HAIR_STRANDS = [(-30, 0.0, 70, 520, 9), (-10, 1.3, 110, 640, 7), (20, 2.1, 150, 460, 6), (-40, 2.9, 40, 760, 8), (5, 3.7, 90, 820, 5)]


def hair_strands(c, t):
    for (x0, ph, dx, ln, wd) in HAIR_STRANDS:
        sw = 26 * math.sin(t * 1.3 + ph) + 12 * math.sin(t * 2.7 + ph * 2)
        p = skia.Path()
        p.moveTo(x0, -40)
        p.cubicTo(x0 + dx * 0.4 + sw * 0.3, ln * 0.3, x0 + dx * 0.8 + sw, ln * 0.65, x0 + dx + sw * 1.4, ln)
        pp = paint(C(HAIR, 150), stroke=wd)
        pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
        c.drawPath(p, pp)


# ------------------------------------------------------------------ book geometry
SP = 196           # spine x
BT, BB = 230, 1290  # cover top / bottom
CL = 814           # cover width (closed: 196..1010)
PG = (196, 250, 990, 1270)  # right page rect


def parch_clip(c, path):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    c.drawImage(PARCH_IMG, 0, 0)
    c.restore()


def gutter_shadow(c, path):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    sh = skia.GradientShader.MakeLinear([P(SP - 110, 0), P(SP + 130, 0)], [rgb(60, 40, 20, 0), rgb(60, 36, 18, 125), rgb(60, 40, 20, 0)], [0.0, 110 / 240, 1.0])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=sh))
    c.restore()


def running_head(c, alpha=220):
    text(c, 'N° 01  ·  THE TIDES OF MAGIC', 250, 336, TF_CINZEL, 27, INK, alpha=alpha)
    pts = [(812, 350), (832, 306), (882, 342), (900, 306), (930, 336)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint(C(INK, int(alpha * 0.9)), stroke=3))
    c.drawCircle(882, 342, 7, paint(C(GOLD, alpha)))
    c.drawLine(250, 356, 930, 356, paint(C(INK, int(alpha * 0.4)), stroke=1.5))


def matrix_flap(phi, src, top, bot, x0=SP, L=None, bump=42):
    """perspective matrix mapping src rect (x0..x0+L, top..bot) onto a flap rotated by phi around the spine"""
    L = L if L is not None else src[2] - src[0]
    xe = x0 + L * math.cos(phi)
    b = bump * math.sin(phi)
    s = [P(src[0], src[1]), P(src[2], src[1]), P(src[2], src[3]), P(src[0], src[3])]
    if math.cos(phi) >= 0:
        d = [P(x0, top), P(xe, top - b), P(xe, bot + b), P(x0, bot)]
    else:
        d = [P(xe, top - b), P(x0, top), P(x0, bot), P(xe, bot + b)]
    m = skia.Matrix()
    m.setPolyToPoly(s, d)
    return m, xe


def cover_front(c):
    x0, y0, x1, y1 = SP, BT, SP + CL, BB
    lg = skia.GradientShader.MakeLinear([P(x0, y0), P(x1, y1)], [rgb(98, 60, 40), rgb(62, 36, 24)])
    c.drawRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 12, 12), skia.Paint(AntiAlias=True, Shader=lg))
    g = C(GOLD, 230)
    c.drawRect(R(x0 + 52, y0 + 84, x1 - 52, y1 - 84), paint(g, stroke=4))
    c.drawRect(R(x0 + 74, y0 + 106, x1 - 74, y1 - 106), paint(C(GOLD, 150), stroke=2))
    cx = (x0 + x1) / 2
    text(c, 'THE TIDES', cx, y0 + 430, TF_CINZEL_B, 92, GOLD, align='center')
    text(c, 'OF MAGIC', cx, y0 + 540, TF_CINZEL_B, 92, GOLD, align='center')
    pts = [(cx - 110, y0 + 700), (cx - 70, y0 + 630), (cx + 30, y0 + 690), (cx + 70, y0 + 620), (cx + 130, y0 + 670)]
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, paint(g, stroke=6))
    c.drawCircle(cx + 30, y0 + 690, 11, paint(rgb(240, 214, 140)))
    text(c, 'N° 01', cx, y0 + 810, TF_CINZEL, 44, GOLD, align='center')


def cover_back(c):
    """inside of the front cover: leather rim + endpaper"""
    x0, y0, x1, y1 = SP, BT, SP + CL, BB
    c.drawRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 12, 12), paint(rgb(78, 46, 30)))
    ep = R(x0 + 22, y0 + 20, x1 - 4, y1 - 20)
    c.save(); c.clipRect(ep, skia.ClipOp.kIntersect, True)
    c.drawImage(PARCH_IMG, 0, 0)
    c.drawRect(ep, paint(rgb(120, 90, 60, 40)))
    c.restore()


def page_back(c):
    path = poly([(PG[0], PG[1]), (PG[2], PG[1]), (PG[2], PG[3]), (PG[0], PG[3])])
    parch_clip(c, path)
    c.drawRect(R(*PG), paint(rgb(120, 96, 70, 30)))
    # faint show-through of ink
    for k in range(9):
        y = 420 + k * 70
        c.drawLine(PG[0] + 90, y, PG[2] - 120 - (k % 3) * 60, y, paint(rgb(80, 60, 40, 18), stroke=3))


def draw_flap(c, phi, front, back, src, top, bot, shade_k=0.35):
    if phi <= 0.0005:
        c.save(); front(c); c.restore()
        return
    if abs(math.cos(phi)) < 0.025:
        return
    m, xe = matrix_flap(phi, src, top, bot)
    c.save()
    c.concat(m)
    if math.cos(phi) >= 0:
        front(c)
        dark = shade_k * math.sin(phi)
    else:
        back(c)
        dark = shade_k * 0.6 * math.sin(phi)
    c.drawRect(R(src[0] - 20, src[1] - 20, src[2] + 20, src[3] + 20), paint(rgb(10, 6, 4, int(255 * dark))))
    c.restore()


def flap_shadow(c, phi, top, bot):
    """soft shadow the lifted flap casts next to its free edge"""
    if phi <= 0.01 or phi >= math.pi - 0.01:
        return
    xe = SP + CL * math.cos(phi)
    sgn = 1 if math.cos(phi) >= 0 else -1
    wdt = 110 * math.sin(phi)
    x1 = xe + sgn * wdt
    g = skia.GradientShader.MakeLinear([P(xe, 0), P(x1, 0)], [rgb(20, 10, 6, int(110 * math.sin(phi))), rgb(20, 10, 6, 0)])
    c.drawRect(R(min(xe, x1), top, max(xe, x1), bot), skia.Paint(Shader=g))


# ------------------------------------------------------------------ the egg (shared)
def egg_draw(c, cx, cy, w=170, h=220, glow=0.0, crack=0.0, rot=0.0, base=True, light=1.0, sh=1.0):
    if base and sh > 0:
        c.drawOval(R(cx - w * 0.62, cy + h * 0.40, cx + w * 0.62, cy + h * 0.56), blur_paint(rgb(30, 18, 10, int(110 * sh)), 8))
        c.drawPath(poly([(cx - w * 0.36, cy + h * 0.47), (cx + w * 0.36, cy + h * 0.47), (cx + w * 0.30, cy + h * 0.53), (cx - w * 0.42, cy + h * 0.53)]), paint(rgb(196, 172, 128)))
    c.save()
    c.translate(cx, cy + h * 0.45); c.rotate(rot); c.translate(-cx, -(cy + h * 0.45))
    path = egg_path(cx, cy, w, h)
    k = light
    shd = skia.GradientShader.MakeRadial(P(cx - w * 0.22, cy - h * 0.2), h * 0.75,
                                         [rgb(int(168 * k), int(166 * k), int(158 * k)), rgb(int(110 * k), int(112 * k), int(108 * k)), rgb(int(58 * k), int(60 * k), int(62 * k))], [0, 0.5, 1])
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=shd))
    c.save(); c.clipPath(path, doAntiAlias=True)
    for r_ in range(7):
        y = cy - h * 0.38 + r_ * h * 0.13
        for j in range(5):
            x = cx - w * 0.5 + j * w * 0.25 + (r_ % 2) * w * 0.12
            c.drawArc(R(x - 18 * w / 170, y - 12 * h / 220, x + 18 * w / 170, y + 12 * h / 220), 20, 140, False, paint(rgb(int(64 * k), int(66 * k), int(66 * k), 150), stroke=2.2))
    if glow > 0:
        gl = skia.GradientShader.MakeRadial(P(cx, cy + h * 0.1), h * 0.8, [rgb(255, 214, 120, int(200 * glow)), rgb(216, 150, 60, int(120 * glow)), rgb(120, 50, 20, 0)])
        c.drawRect(R(cx - w, cy - h, cx + w, cy + h), skia.Paint(Shader=gl, BlendMode=skia.BlendMode.kPlus))
    c.restore()
    c.drawPath(path, paint(rgb(40, 38, 36, 200), stroke=2.5))
    if crack > 0:
        cr = [(cx - w * 0.42, cy - h * 0.02), (cx - w * 0.2, cy - h * 0.12), (cx - w * 0.05, cy + h * 0.02), (cx + w * 0.12, cy - h * 0.16),
              (cx + w * 0.3, cy - h * 0.04), (cx + w * 0.44, cy - h * 0.12)]
        n = max(2, int(2 + crack * (len(cr) - 2) + 0.999))
        pts = cr[:n]
        pp = skia.Path(); pp.moveTo(*pts[0])
        for q in pts[1:]:
            pp.lineTo(*q)
        c.drawPath(pp, blur_paint(rgb(255, 200, 90, 230), 10))
        c.drawPath(pp, paint(rgb(255, 244, 200), stroke=5))
        if crack > 0.7:
            for (a, b) in (((cx + w * 0.12, cy - h * 0.16), (cx + w * 0.08, cy - h * 0.34)), ((cx - w * 0.05, cy + h * 0.02), (cx - w * 0.1, cy + h * 0.2))):
                c.drawLine(*a, *lerp2(a, b, (crack - 0.7) / 0.3), paint(rgb(255, 238, 190), stroke=4))
    c.restore()


def wobble(t, hits, amp=7.0):
    r = 0.0
    for (th, a) in hits:
        if t >= th:
            u = t - th
            r += a * amp * math.exp(-u * 5.5) * math.sin(u * 26)
    return r


# ------------------------------------------------------------------ page A (hook)
EGG_A = (590, 920)
TALLY_T = [2.85 + k * 0.24 for k in range(9)]


def write_on(c, t, t0, t1, rect, draw):
    u = clamp((t - t0) / (t1 - t0))
    if u <= 0:
        return
    c.save()
    c.clipRect(R(rect[0], rect[1], lerp(rect[0], rect[2], u), rect[3]))
    draw(c)
    c.restore()


def tally_marks(c, t, x0=910, y0=420):
    for k, tk in enumerate(TALLY_T):
        u = clamp((t - tk) / 0.12)
        if u <= 0:
            continue
        g, i = divmod(k, 5)
        y = y0 + g * 80
        if i < 4:
            xa, ya, xb, yb = x0 + i * 12, y, x0 + i * 12 + 2, y + 52
        else:
            xa, ya, xb, yb = x0 - 8, y + 44, x0 + 50, y + 8
        c.drawLine(xa, ya, lerp(xa, xb, u), lerp(ya, yb, u), paint(C(INK, 210), stroke=3.5))


def page_a(c, t, pristine=False, fold=1.0):
    """right page content of the hook; fold scales pop-ups (page turning)"""
    running_head(c)
    if pristine:
        egg_flat(c, EGG_A)
        return
    write_on(c, t, 0.45, 1.25, (270, 400, 910, 545), lambda c: text(c, '150 YEARS', 580, 520, TF_CINZEL_B, 108, INK, align='center'))
    write_on(c, t, 1.30, 1.95, (290, 550, 890, 670), lambda c: text(c, '0 DRAGONS', 580, 640, TF_CINZEL_B, 88, INK, align='center'))
    u = clamp((t - 1.95) / 0.25)
    if u > 0:
        c.drawLine(430, 672, lerp(430, 730, u), 672, paint(C(GLUT, 200), stroke=5))
    tally_marks(c, t)
    if t >= 7.62:
        a = int(225 * clamp((t - 7.62) / 0.06))
        stamp_mark(c, 610, 1200, alpha=a)
    s = popv(t, 0.32, 0.5) * fold
    rot = wobble(t, [(3.62, 1.0), (4.42, 1.1), (7.62, 0.5)])
    if s > 0.02:
        with folded(c, EGG_A[0], EGG_A[1] + 110, s):
            egg_draw(c, *EGG_A, rot=rot, sh=1.0)
    else:
        egg_flat(c, EGG_A)


def egg_flat(c, pos):
    cx, cy = pos
    c.drawPath(poly([(cx - 62, cy + 104), (cx + 62, cy + 104), (cx + 52, cy + 118), (cx - 72, cy + 118)]), paint(rgb(196, 172, 128)))


# ------------------------------------------------------------------ page B (the attempts)
EGG_B = (590, 860)
MAGE_RING = (600, 900, 300, 84)
MAGE_COLS = [(70, 74, 92), (86, 80, 104), (64, 70, 84), (92, 86, 110), (74, 78, 98), (84, 76, 96), (68, 72, 90), (90, 84, 104), (78, 72, 94)]
MAGE_T = [10.0 + 0.11 * k for k in (4, 7, 1, 8, 2, 5, 0, 6, 3)]


def waves(c, t, y0, s_list):
    cols = [(92, 112, 128), (112, 134, 148), (78, 98, 114)]
    for k, col in enumerate(cols):
        s = s_list[k]
        if s <= 0.01:
            continue
        y = y0 + k * 46
        ph = t * 2.2 + k * 1.3
        pts = [(196, y + 60)]
        for i in range(12):
            x = 196 + i * 72
            pts.append((x + 10 * math.sin(ph), y + (0 if i % 2 == 0 else 26) + 4 * math.sin(ph + i)))
        pts += [(990, y + 20), (990, y + 90), (196, y + 90)]
        with folded(c, 0, y + 90, s):
            shadowed(c, smooth_path(pts), C(col), off=(0, -6), sigma=5, alpha=70)


def pull_tab(c, y0, s, pull):
    if s <= 0.01:
        return
    x = 986 + 40 * (1 - pull)
    c.drawPath(poly([(986, y0 + 40), (x + 74, y0 + 40), (x + 84, y0 + 62), (x + 74, y0 + 84), (986, y0 + 84)]), paint(rgb(214, 196, 158)))
    c.drawPath(poly([(x + 24, y0 + 52), (x + 54, y0 + 62), (x + 24, y0 + 72)]), paint(C(INK, 180)))


def ship(c, x, y, s=0.9, bob=0.0):
    c.save(); c.translate(x, y); c.rotate(bob); c.translate(-x, -y)
    hull = smooth_path([(x - 110 * s, y - 40 * s), (x + 120 * s, y - 40 * s), (x + 80 * s, y + 10 * s), (x - 80 * s, y + 10 * s)])
    shadowed(c, hull, rgb(96, 62, 40), off=(5, 6), sigma=4)
    c.drawLine(x, y - 40 * s, x, y - 230 * s, paint(rgb(80, 54, 36), stroke=7 * s))
    sail = smooth_path([(x + 6 * s, y - 220 * s), (x + 110 * s, y - 190 * s), (x + 100 * s, y - 110 * s), (x + 6 * s, y - 70 * s)])
    shadowed(c, sail, rgb(236, 226, 204), off=(5, 6), sigma=4)
    c.restore()


def candle(c, t, x, base, s):
    if s <= 0.01:
        return
    with folded(c, x, base, s):
        c.drawOval(R(x - 60, base - 30, x + 60, base), paint(rgb(170, 130, 70)))
        c.drawRect(R(x - 20, base - 160, x + 20, base - 18), paint(rgb(234, 226, 206)))
        c.drawLine(x, base - 160, x, base - 180, paint(rgb(40, 34, 30), stroke=3))
    lit = clamp((t - 12.95) / 0.15) * (1 - clamp((t - 14.38) / 0.08))
    if lit > 0 and s > 0.9:
        fl = 1 + 0.15 * math.sin(t * 23) + 0.1 * math.sin(t * 37)
        fx, fy = x, base - 182
        c.drawPath(smooth_path([(fx - 11, fy), (fx - 7, fy - 22 * fl), (fx, fy - 46 * fl), (fx + 7, fy - 22 * fl), (fx + 11, fy)]), paint(rgb(255, 214, 120, int(255 * lit))))
        additive_glow(c, fx, fy - 20, 260, (255, 190, 90), int(70 * lit))


def light_cone(c, t, egg):
    """Baelor's prayer: golden light falls toward the egg and dies before it arrives"""
    u = clamp((t - 13.1) / 0.9)
    fade = 1 - clamp((t - 13.9) / 0.5)
    if u <= 0 or fade <= 0:
        return
    top = 380
    reach = lerp(top, egg[1] - 150, u)
    g = skia.GradientShader.MakeLinear([P(0, top), P(0, reach)], [rgb(255, 222, 140, 0), rgb(255, 222, 140, int(110 * fade)), rgb(255, 222, 140, 0)], [0.0, 0.35, 1.0])
    path = poly([(egg[0] - 40, top), (egg[0] + 40, top), (egg[0] + 120, reach), (egg[0] - 120, reach)])
    cp = skia.Paint(AntiAlias=True, Shader=g, BlendMode=skia.BlendMode.kPlus)
    cp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    c.drawPath(path, cp)
    for k in range(6):
        yy = lerp(top, reach, (k + 0.5) / 6 + 0.05 * math.sin(t * 3 + k))
        sparkle(c, egg[0] + 70 * math.sin(k * 2.1 + t), yy, 7, GOLD, int(160 * fade))


def smoke_curl(c, t, x, y):
    u = clamp((t - 14.42) / 1.0)
    if u <= 0 or t > 16.2:
        return
    a = 1 - clamp((t - 15.4) / 0.8)
    p = skia.Path(); p.moveTo(x, y)
    p.cubicTo(x - 30, y - 50, x + 30, y - 90, x - 10, y - 150)
    p.cubicTo(x - 40, y - 190, x + 10, y - 230, x - 10, y - 290)
    m = skia.PathMeasure(p, False)
    seg = skia.Path()
    m.getSegment(0, m.getLength() * u, seg, True)
    pp = paint(rgb(160, 156, 150, int(190 * a)), stroke=6)
    pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.5))
    c.drawPath(seg, pp)


def blueprint_lines(c, t):
    u = clamp((t - 14.95) / 0.9)
    a = 1 - clamp((t - 19.8) / 0.6)
    if u <= 0 or a <= 0:
        return
    col = C(INK, int(170 * a))
    for pts in ([(300, 900), (320, 780), (380, 660), (470, 560), (560, 520), (640, 540)],
                [(360, 960), (600, 930), (840, 900), (900, 760), (880, 600)]):
        path = smooth_path(pts, closed=False)
        m = skia.PathMeasure(path, False)
        seg = skia.Path(); m.getSegment(0, m.getLength() * u, seg, True)
        pp = paint(col, stroke=3); pp.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
        c.drawPath(seg, pp)
    if u >= 1:
        c.drawLine(420, 1110, 800, 1110, paint(col, stroke=2))
        c.drawLine(420, 1096, 420, 1124, paint(col, stroke=2)); c.drawLine(800, 1096, 800, 1124, paint(col, stroke=2))


# wood dragon planks: (x0, y0, x1, y1, width, colour, arrival time)
WCX, WCY = 600, 930


def _wd_planks():
    cx, cy = WCX, WCY
    out = []
    t = 15.30
    for x in (cx - 170, cx - 90, cx + 90, cx + 170):
        out.append([x, cy + 60, x + 6, cy + 190, 20, (150, 104, 62), t]); t += 0.09
    for k in range(3):
        out.append([cx - 230, cy - 20 + k * 30, cx + 200, cy - 30 + k * 30, 26, (158 - k * 10, 110 - k * 6, 66), t]); t += 0.12
    out.append([cx + 180, cy - 20, cx + 290, cy - 250, 26, (150, 104, 62), t]); t += 0.14
    out.append([cx - 230, cy + 10, cx - 380, cy + 90, 20, (150, 104, 62), t]); t += 0.1
    return out


WD_PLANKS = _wd_planks()
WD_WINGS = [((WCX - 20, WCY - 36), (WCX + 40, WCY - 380), (WCX - 240, WCY - 40), (170, 146, 110), 0, 16.55),
            ((WCX - 60, WCY - 30), (WCX - 190, WCY - 330), (WCX - 300, WCY - 10), (150, 128, 96), 40, 16.75)]
HEAP_RNG = np.random.default_rng(4)
HEAP = [(HEAP_RNG.uniform(-170, 60), HEAP_RNG.uniform(-30, 40), HEAP_RNG.uniform(-0.6, 0.6), HEAP_RNG.uniform(110, 210)) for _ in range(12)]
HEAP_C = (430, 1050)
T_COLLAPSE = 20.62


def wood_dragon(c, t):
    if t < 15.25 or t > 25.6:
        return
    sag = clamp((t - 17.7) / 0.9)
    col_u = ease(clamp((t - T_COLLAPSE) / 0.45))
    # wings (cloth + ribs) - assembled, sagging, then they fall
    if col_u < 1:
        for (root, tip, rear, cloth, droop, ta) in WD_WINGS:
            a = clamp((t - ta) / 0.3)
            if a <= 0:
                continue
            tip_ = (tip[0], tip[1] + droop + 60 * sag)
            tip_ = lerp2(root, tip_, popout(a))
            fall = col_u
            sc = []
            for i in range(1, 4):
                u = i / 4
                sc.append(lerp2(tip_, rear, u))
            edge = [root, tip_]
            prev = tip_
            for q in sc + [rear]:
                mid = ((prev[0] + q[0]) / 2 + 18, (prev[1] + q[1]) / 2 + 30)
                edge += [mid, q]
                prev = q
            c.save(); c.translate(0, 180 * fall * fall); c.rotate(-12 * fall)
            shadowed(c, poly(edge), C(cloth, int(255 * (1 - fall))), off=(5, 7), sigma=5, alpha=int(70 * (1 - fall)))
            for q in [tip_] + sc:
                plank(c, root[0], root[1], q[0], q[1], 10, (128, 88, 54))
            c.restore()
    for k, (x0, y0, x1, y1, w, col, ta) in enumerate(WD_PLANKS):
        a = clamp((t - ta) / 0.28)
        if a <= 0:
            continue
        # fly in from above-right with a little spin
        off = (1 - ease_out(a))
        dx, dy = 260 * off, -420 * off
        if k == 7:  # neck droops
            x1, y1 = x1 + 30 * sag, y1 + 70 * sag
        if col_u > 0:
            hx, hy, ang, ln = HEAP[k % len(HEAP)]
            hx0, hy0 = HEAP_C[0] + hx, HEAP_C[1] + hy
            tx0, ty0 = hx0, hy0
            tx1, ty1 = hx0 + math.cos(ang) * ln, hy0 + math.sin(ang) * ln
            x0, y0 = lerp(x0, tx0, col_u), lerp(y0, ty0, col_u)
            x1, y1 = lerp(x1, tx1, col_u), lerp(y1, ty1, col_u)
        plank(c, x0 + dx, y0 + dy, x1 + dx, y1 + dy, w, col)
    # head
    if t >= 16.1 and col_u < 1:
        a = popout((t - 16.1) / 0.3)
        hx, hy = WCX + 290 + 30 * sag, WCY - 250 + 70 * sag
        hx, hy = lerp(hx, HEAP_C[0] + 40, col_u), lerp(hy, HEAP_C[1] + 20, col_u)
        c.save(); c.translate(hx, hy); c.scale(a, a); c.rotate(28 * sag + 90 * col_u); c.translate(-hx, -hy)
        head = poly([(hx - 10, hy - 30), (hx + 90, hy - 10), (hx + 96, hy + 20), (hx - 6, hy + 26)])
        shadowed(c, head, C((150, 104, 62)), off=(4, 5), sigma=3)
        c.drawCircle(hx + 40, hy - 4, 6, paint(rgb(40, 40, 44)))
        c.restore()
    # iron bands
    if t >= 17.5 and col_u < 0.5:
        a = clamp((t - 17.5) / 0.25) * (1 - col_u * 2)
        for x in (WCX - 150, WCX - 20, WCX + 110):
            c.drawRect(R(x, WCY - 40, x + 18, WCY + 60), paint(rgb(70, 72, 78, int(255 * a))))
            for yy in (WCY - 30, WCY + 10, WCY + 48):
                c.drawCircle(x + 9, yy, 4, paint(rgb(170, 172, 176, int(255 * a))))


def aflames(c, x, y, w, h, t, seed=0, cols=((196, 83, 46), (238, 150, 64), (252, 222, 160)), n=3, a=255):
    rng = np.random.default_rng(seed)
    base = rng.uniform(0.65, 1.05, (len(cols), n))
    ph = rng.uniform(0, 6.28, (len(cols), n))
    for k, col in enumerate(cols):
        sc = 1.0 - 0.28 * k
        for j in range(n):
            ox = (j - (n - 1) / 2) * w / n * 1.05 * sc
            hh = h * sc * base[k, j] * (1 + 0.16 * math.sin(t * 7.3 + ph[k, j]) + 0.08 * math.sin(t * 13.1 + ph[k, j] * 2))
            ww = w / n * 0.9 * sc
            sway = 0.25 * ww * math.sin(t * 5.1 + ph[k, j])
            pts = [(x + ox - ww, y), (x + ox - ww * 0.55 + sway * 0.3, y - hh * 0.45), (x + ox + sway, y - hh),
                   (x + ox + ww * 0.55 + sway * 0.3, y - hh * 0.5), (x + ox + ww, y)]
            c.drawPath(smooth_path(pts), paint(C(col, a)))


GREENS = ((60, 150, 60), (120, 226, 104), (210, 255, 190))


def goblet(c, t):
    s = popv(t, 18.72, 0.4)
    if s <= 0.01:
        return
    with folded(c, 840, 1120, s):
        gob = smooth_path([(780, 1120), (900, 1120), (870, 1100), (850, 1060), (848, 1010), (900, 960), (906, 900), (774, 900), (780, 960), (832, 1010), (830, 1060), (810, 1100)])
        shadowed(c, gob, rgb(170, 160, 150), off=(5, 6), sigma=4)
        c.drawOval(R(774, 888, 906, 914), paint(rgb(60, 110, 60)))


def wildfire(c, t):
    if t < 19.55 or t > 25.6:
        return
    u = ease_out(clamp((t - 19.55) / 0.45))
    fade = 1 - clamp((t - 20.9) / 0.4)
    if fade > 0:
        jet = skia.Path(); jet.moveTo(840, 900); jet.cubicTo(800, 640, 560, 700, 450, 980)
        m = skia.PathMeasure(jet, False)
        seg = skia.Path(); m.getSegment(m.getLength() * max(0, u - 0.7) * (1 - fade) , m.getLength() * u, seg, True)
        for wdt, col, sg in ((60, (70, 190, 80, 120), 18), (34, (120, 230, 110, 220), 8), (12, (225, 255, 210, 255), 3)):
            p = blur_paint(rgb(col[0], col[1], col[2], int(col[3] * fade)), sg)
            p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(wdt); p.setStrokeCap(skia.Paint.kRound_Cap)
            c.drawPath(seg, p)
        additive_glow(c, 450, 1000, 500, (90, 200, 90), int(70 * fade * u))


def page_fire(c, t):
    """the dragon burns (green first, then orange), then fire spreads over the lower page"""
    if t < 19.95:
        return
    g = clamp((t - 19.95) / 0.5)
    o = clamp((t - 20.3) / 0.6)
    if t < T_COLLAPSE + 0.4:
        cx, cy = WCX - 40, WCY + 70
    else:
        cx, cy = HEAP_C[0] + 20, HEAP_C[1] + 60
    aflames(c, cx, cy, 300 * o, 260 * o, t, seed=2, a=int(240 * o))
    aflames(c, cx + 60, cy - 10, 170 * g, 220 * g, t, seed=3, cols=GREENS, a=int(230 * g * (1 - 0.5 * o)))
    additive_glow(c, cx, cy - 60, 460, (230, 120, 50), int(80 * o))
    sp = clamp((t - 21.0) / 1.2)
    for k, (x, s) in enumerate(((260, 0.7), (650, 0.8), (800, 0.6), (520, 0.9), (930, 0.5))):
        a = clamp(sp * 5 - k)
        if a > 0:
            aflames(c, x, 1240, 140 * s * a, 160 * s * a, t, seed=10 + k, a=int(230 * a))


def mages(c, t):
    if t < 9.9 or t > 13.0:
        return
    cx, cy, rx, ry = MAGE_RING
    order = sorted(range(9), key=lambda i: math.sin(2 * math.pi * i / 9 + 0.4))
    egg_done = False
    for i in order:
        a = 2 * math.pi * i / 9 + 0.4
        if math.sin(a) > -0.05 and not egg_done:
            yield_egg = True
            egg_done = True
            yield ('egg', None)
        x, y = cx + rx * math.cos(a), cy + 40 + ry * math.sin(a)
        s = popv(t, MAGE_T[i], 0.35, 12.3 + 0.03 * i, 0.3)
        yield ('mage', (i, x, y, s, a))
    if not egg_done:
        yield ('egg', None)


def draw_mage(c, t, i, x, y, s, a):
    if s <= 0.01:
        return
    sc = 1.2 + 0.15 * math.sin(a)
    arms = t > 10.85 + 0.03 * i
    with folded(c, x, y, s):
        mage(c, x, y, sc, MAGE_COLS[i], arms=arms)
    if arms and t < 12.3:
        u = (t - (10.95 + 0.07 * i)) % 0.55
        if t > 10.95 + 0.07 * i:
            k = clamp(u / 0.18)
            fz = clamp((u - 0.18) / 0.3)
            sparkle(c, x - 40 * sc / 1.2, y - 160 - 20 * k, 16 * (1 - fz) + 2, GOLD, int(220 * (1 - fz)))
            sparkle(c, x + 42 * sc / 1.2, y - 152 - 16 * k, 11 * (1 - fz) + 2, GOLD, int(170 * (1 - fz)))
            if fz > 0:
                puff(c, x + 4, y - 190 - 30 * fz, 14 + 10 * fz, int(90 * (1 - fz)))


def page_b(c, t, fold=1.0):
    running_head(c)
    egg_s = popv(t, 8.38, 0.45) * fold
    rot = wobble(t, [(9.55, 0.3), (17.6, 0.6), (T_COLLAPSE + 0.2, 1.0)])
    # waves + ship
    ws = [popv(t, 8.70 + 0.12 * k, 0.4, 12.45 + 0.05 * k, 0.3) * fold for k in range(3)]
    waves(c, t, 1080, ws)
    pull = ease(clamp((t - 9.0) / 1.0))
    pull_tab(c, 1080, max(ws), pull)
    ss = popv(t, 9.0, 0.35, 12.45, 0.3) * fold
    if ss > 0.01:
        sx = lerp(150, 380, ease(clamp((t - 9.0) / 1.2)))
        with folded(c, sx, 1100, ss):
            ship(c, sx, 1090, 0.9, bob=3 * math.sin(t * 3.1))
    # mages around the egg (egg drawn in depth order)
    if 9.9 <= t <= 13.0:
        for kind, d in mages(c, t):
            if kind == 'egg':
                draw_egg_b(c, t, egg_s, rot)
            else:
                draw_mage(c, t, *d)
    else:
        if t < 15.25:
            draw_egg_b(c, t, egg_s, rot)
    candle_s = popv(t, 12.72, 0.4, 15.6, 0.3) * fold
    candle(c, t, 300, 1080, candle_s)
    light_cone(c, t, EGG_B)
    smoke_curl(c, t, 300, 898)
    blueprint_lines(c, t)
    wood_dragon(c, t)
    if t >= 15.25:
        draw_egg_b(c, t, egg_s, rot)
    goblet(c, t)
    labels(c, t)
    page_fire(c, t)
    wildfire(c, t)


def draw_egg_b(c, t, s, rot):
    if t > 21.9:  # from here the egg is drawn on top of the burning page
        return
    if s > 0.02:
        with folded(c, EGG_B[0], EGG_B[1] + 110, s):
            egg_draw(c, *EGG_B, rot=rot)
    else:
        egg_flat(c, EGG_B)


def labels(c, t):
    for (s, x, y, t0) in (('OAK', 420, 690, 16.95), ('IRON', 810, 1040, 17.6)):
        a = popv(t, t0, 0.3, 19.6, 0.3)
        if a > 0.02:
            with folded(c, x, y + 10, a):
                label_box(c, s, x, y)


# ------------------------------------------------------------------ the burn + the pyre (behind the page)
HOLE_C = (590, 760)


def hole_radius(t):
    if t < 21.95:
        return 0.0
    r = 340 * ease_out(clamp((t - 21.95) / 1.25))
    r += 1400 * ease_in(clamp((t - 24.55) / 0.85))
    return r


PLATE1_R = (290, 320, 890, 1200)
PLATE2_R = (250, 330, 830, 1183)


def draw_plate(c, img, rect, t, k0, k1, fx=0.5, fy=0.5, label=None, alpha=255):
    x0, y0, x1, y1 = rect
    c.save()
    c.clipRect(R(*rect), skia.ClipOp.kIntersect, True)
    z = lerp(1.0, 1.07, clamp((t - k0) / (k1 - k0)))
    w, h = (x1 - x0) * z, (y1 - y0) * z
    cx, cy = lerp(x0, x1, fx), lerp(y0, y1, fy)
    dst = R(cx - (cx - x0) * z, cy - (cy - y0) * z, cx - (cx - x0) * z + w, cy - (cy - y0) * z + h)
    pp = skia.Paint(AntiAlias=True)
    pp.setAlphaf(alpha / 255)
    c.drawImageRect(img, R(0, 0, img.width(), img.height()), dst, SAMP, pp)
    c.restore()
    c.drawRect(R(*rect), paint(rgb(150, 110, 60, alpha), stroke=6))
    if label:
        lx = (x0 + x1) / 2
        f = skia.Font(TF_FELL_SC, 30)
        lw = f.measureText(label)
        ly = y0 + 46
        c.drawRect(R(lx - lw / 2 - 22, ly - 34, lx + lw / 2 + 22, ly + 12), paint(rgb(222, 204, 164, alpha)))
        text(c, label, lx, ly, TF_FELL_SC, 30, INK, align='center', alpha=alpha)


EMBERS = [dict(x=np.random.default_rng(i).uniform(0, W), t0=np.random.default_rng(i + 99).uniform(0, 4),
               sp=np.random.default_rng(i + 7).uniform(60, 160), r=np.random.default_rng(i + 3).uniform(1.6, 3.6),
               life=np.random.default_rng(i + 5).uniform(2.0, 4.0)) for i in range(70)]


def embers(c, t, x0, x1, ybase, strength=1.0, n=70):
    if strength <= 0:
        return
    for e in EMBERS[:n]:
        age = (t - e['t0']) % e['life']
        u = age / e['life']
        x = x0 + (e['x'] / W) * (x1 - x0) + 18 * math.sin(t * 2 + e['t0'] * 5)
        y = ybase - e['sp'] * age * 1.4
        a = int(255 * (1 - u) * strength * (0.6 + 0.4 * math.sin(t * 11 + e['t0'] * 9)))
        if a > 0:
            c.drawCircle(x, y, e['r'], paint(rgb(255, 170, 70, max(a, 0))))


def ember_fall(t):
    """the single ember: falls through the dark, lands on plate II at 'Then'"""
    u = clamp((t - 25.45) / (26.42 - 25.45))
    x = lerp(720, 520, ease(u)) + 26 * math.sin(u * 7)
    y = lerp(-40, 760, u ** 1.4)
    return x, y


def under_page(c, t, with_egg=True):
    """what lies behind the page: charred dark, plate I burning, the ember, plate II"""
    c.drawImage(CHAR_IMG, 0, 0)
    if 21.9 <= t <= 25.5:
        a = 1 - clamp((t - 24.9) / 0.5)
        if a > 0:
            draw_plate(c, PLATE1, PLATE1_R, t, 21.9, 25.4, 0.5, 0.45, 'PLATE I  ·  SUMMERHALL, 259 AC', alpha=int(255 * a))
            embers(c, t, 290, 890, 1150, a)
            additive_glow(c, 590, 760, 520, (240, 120, 50), int(60 * a))
    if 25.4 <= t < 26.5:
        ex, ey = ember_fall(t)
        if t < 26.42:
            c.drawCircle(ex, ey, 14, blur_paint(rgb(255, 170, 70, 200), 8))
            c.drawCircle(ex, ey, 5, paint(rgb(255, 230, 170)))
    if t >= 26.42:
        a = clamp((t - 26.42) / 0.3)
        fl = 1 - clamp((t - 26.42) / 0.6)
        heat = clamp((t - 27.2) / 3.3)
        draw_plate(c, PLATE2, PLATE2_R, t, 26.42, 32.4, 0.38, 0.7, 'PLATE II  ·  THE PYRE', alpha=int(255 * a))
        if fl > 0:
            additive_glow(c, 540, 700, 700, (255, 170, 80), int(160 * fl))
        # flames breaking out of the plate frame
        k = a * (0.55 + 0.45 * heat)
        aflames(c, 252, 900, 70 * k, 110 * k, t, seed=13, a=int(210 * a))
        aflames(c, 828, 930, 70 * k, 120 * k, t, seed=14, a=int(210 * a))
        aflames(c, 540, 1186, 200 * k, 70 * k, t, seed=12, a=int(200 * a))
        embers(c, t, 250, 830, 400, a * 0.8, 50)


# egg position + state across the burn and the pyre
def egg_state(t):
    if t < 25.0:
        pos, w, h = EGG_B, 170, 220
    else:
        u = ease(clamp((t - 25.0) / 1.0))
        pos = lerp2(EGG_B, (540, 1205), u)
        w, h = lerp(170, 150, u), lerp(220, 195, u)
    glow = 0.8 * clamp((t - 27.2) / 3.3) + 0.2 * clamp((t - 30.6) / 0.6)
    crack = clamp((t - 30.62) / 0.5)
    light = 1.0 if t < 21.9 else lerp(1.0, 0.55, clamp((t - 22.0) / 1.5)) + 0.45 * glow
    return pos, w, h, glow, crack, light


SHELL = [(np.cos(a), np.sin(a), np.random.default_rng(int(a * 100)).uniform(0.6, 1.2)) for a in np.linspace(0, 2 * np.pi, 9)[:-1]]
T_BURST = 31.25


def draw_egg_top(c, t):
    if t < 21.9 or t > 33.5:
        return
    pos, w, h, glow, crack, light = egg_state(t)
    if t < T_BURST:
        egg_draw(c, pos[0], pos[1], w, h, glow=glow, crack=crack, base=False, light=light)
        if 22.0 < t < 25.5:   # rim light from the fire behind
            rp = paint(rgb(255, 150, 60, int(110 * clamp((t - 22) / 1))), stroke=5)
            rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
            c.drawPath(egg_path(pos[0], pos[1], w, h), rp)
    else:
        u = clamp((t - T_BURST) / 0.9)
        for (dx, dy, sp) in SHELL:
            x = pos[0] + dx * 260 * ease_out(u) * sp
            y = pos[1] + dy * 200 * ease_out(u) * sp + 300 * u * u
            c.save(); c.translate(x, y); c.rotate(400 * u * sp)
            c.drawPath(smooth_path([(-22, -6), (0, -18), (22, -8), (14, 8), (-14, 10)]), paint(rgb(96, 96, 92, int(255 * (1 - u)))))
            c.drawPath(smooth_path([(-22, -6), (0, -18), (22, -8), (14, 8), (-14, 10)]), paint(rgb(255, 210, 120, int(200 * (1 - u))), stroke=2))
            c.restore()
        fl = 1 - clamp((t - T_BURST) / 0.6)
        if fl > 0:
            additive_glow(c, pos[0], pos[1], 520, (255, 210, 120), int(220 * fl))


# ------------------------------------------------------------------ book frame (0..25.4 and the end)
def phi_open(u):
    """cover angle across the seam: u in [-0.45, 0.45] (end of video = negative u)"""
    return math.pi * ease((u + 0.45) / 0.9)


def cover_phi(t):
    if t <= 0.45:
        return phi_open(t)
    if t >= T_TOTAL - 0.45:
        return phi_open(t - T_TOTAL)
    if 49.9 <= t <= 50.5:
        return math.pi * (1 - ease((t - 49.9) / 0.6))
    if 50.5 < t < T_TOTAL - 0.45:
        return 0.0
    return math.pi


def turn_phi(t):
    """page A turns over at 8.0..8.6"""
    return math.pi * ease((t - 8.0) / 0.6) if 8.0 <= t <= 8.6 else (math.pi if t > 8.6 else 0.0)


FLIPS = [47.0, 47.35, 47.7, 48.05, 48.45, 48.85]   # rewind: pages swing from left to right


def flip_page_content(c, k):
    """glimpses on the rewinding pages"""
    running_head(c, 180)
    rng = np.random.default_rng(k + 3)
    for j in range(int(rng.integers(5, 9))):
        y = 440 + j * 62
        c.drawLine(280, y, 280 + rng.uniform(300, 600), y, paint(rgb(60, 44, 30, 150), stroke=5))
    sk = [lambda c: egg_flat(c, (590, 1000)), lambda c: plate_sketch(c), lambda c: ship(c, 520, 1100, 0.6),
          lambda c: mage(c, 600, 1150, 0.9, (80, 80, 100)), lambda c: egg_flat(c, (560, 1050))]
    sk[k % len(sk)](c)


def plate_sketch(c):
    c.drawRect(R(380, 820, 780, 1180), paint(rgb(70, 50, 40)))
    c.drawRect(R(380, 820, 780, 1180), paint(rgb(150, 110, 60), stroke=5))


def book_frame(c, t, page_only=False):
    """over-the-shoulder book shot. page_only: just the book (texture for the wide shot)"""
    if not page_only:
        bg_book(c, t)
        lap_d(c, t)
    phi = cover_phi(t)
    # back cover + page block (right)
    c.drawRRect(skia.RRect.MakeRectXY(R(SP - 8, BT - 6, SP + CL + 4, BB + 8), 14, 14), paint(rgb(70, 42, 28)))
    page_path_r = page_path(PAGE)
    parch_clip(c, page_path_r)
    for k in range(4):
        c.drawLine(990 + k * 3, 252 + k * 2, 994 + k * 3, 1262 - k * 2, paint(rgb(200, 180, 140), stroke=1.5))
    # left side: lies open when the cover has swung over
    # right page content
    end_rewind = t >= 46.9
    c.save(); c.clipPath(page_path_r, doAntiAlias=True)
    if end_rewind:
        page_a(c, t, pristine=True)
    elif t < 8.0:
        page_a(c, t)
    elif t < 25.6:
        page_b(c, t)
    gutter_shadow(c, page_path_r)
    c.restore()
    # left side: cover inside lying open (drawn through the flap at phi=pi)
    if phi >= math.pi / 2:
        draw_flap(c, phi, cover_front, cover_back, (SP, BT, SP + CL, BB), BT, BB, shade_k=0.25)
        if phi >= math.pi - 0.001:
            # pages that were turned lie on top of the endpaper
            if 8.6 <= t < 46.9:
                draw_flap(c, math.pi, lambda c: None, page_back, PG, PG[1], PG[3])
            gutter_shadow(c, poly(LPAGE))
    # page A turning over
    if 8.0 <= t <= 8.6:
        ph = turn_phi(t)
        fold = clamp(1 - math.sin(ph) * 1.4) if ph < math.pi / 2 else 0.0
        flap_shadow(c, ph, PG[1], PG[3])
        draw_flap(c, ph, lambda c: (parch_clip(c, page_path_r), page_a(c, t, fold=fold)), page_back, PG, PG[1], PG[3])
    # rewind flips at the end (left -> right)
    if 46.9 <= t < 49.3:
        for k, t0 in enumerate(FLIPS):
            if t < t0:
                # still lying on the left
                draw_flap(c, math.pi, lambda c: None, page_back, PG, PG[1], PG[3])
                break
            if t0 <= t <= t0 + 0.32:
                ph = math.pi * (1 - ease((t - t0) / 0.32))
                flap_shadow(c, ph, PG[1], PG[3])
                draw_flap(c, ph, lambda c, k=k: (parch_clip(c, page_path_r), flip_page_content(c, k)), page_back, PG, PG[1], PG[3])
    # the cover in front (closing / closed / lifting)
    if phi < math.pi / 2:
        flap_shadow(c, phi, BT, BB)
        draw_flap(c, phi, cover_front, cover_back, (SP, BT, SP + CL, BB), BT, BB, shade_k=0.25)
    if page_only:
        return
    # hands
    if 5.5 <= t <= 8.37:
        draw_stamp_tool(c, t)
    rpos, rkind = right_hand(t)
    hands_d(c, t, rpos=rpos, rkind=rkind)


def right_hand(t):
    rest = (968, 1334)
    # finger taps the egg (3.62, 4.42)
    if 2.9 <= t <= 5.3:
        tap = (EGG_A[0] + 92, EGG_A[1] + 20)
        u = ease(clamp((t - 2.9) / 0.6)) * (1 - ease(clamp((t - 4.75) / 0.55)))
        p = lerp2(rest, tap, u)
        for th in (3.62, 4.42):
            d = t - th
            if -0.12 < d < 0.12:
                p = (p[0] - 22 * (1 - abs(d) / 0.12), p[1])
        return p, 'point' if u > 0.3 else 'grip'
    # stamp
    if 5.5 <= t <= 8.37:
        return stamp_hand(t), 'fist'
    return None, 'grip'


def stamp_hand(t):
    rest = (968, 1334)
    above = (690, 1010)
    press = (650, 1160)
    if t < 6.2:
        return lerp2(rest, above, ease((t - 5.5) / 0.7))
    if t < 7.62:
        u = ease((t - 7.27) / 0.35) if t > 7.27 else 0.0
        return lerp2(above, press, u ** 2)
    if t < 7.97:
        return lerp2(press, above, ease((t - 7.62) / 0.35))
    return lerp2(above, rest, ease((t - 7.97) / 0.4))


def draw_stamp_tool(c, t):
    hx, hy = stamp_hand(t)
    sx, sy = hx - 40, hy + 150
    c.drawOval(R(sx - 120, sy + 30, sx + 120, sy + 60), blur_paint(rgb(30, 18, 10, 70), 10))
    c.drawRoundRect(R(sx - 110, sy - 30, sx + 110, sy + 8), 8, 8, paint(rgb(120, 40, 26)))
    c.drawRoundRect(R(sx - 120, sy - 60, sx + 120, sy - 28), 8, 8, paint(rgb(126, 88, 52)))
    c.drawPath(smooth_path([(sx - 26, sy - 60), (sx - 30, sy - 110), (sx - 46, sy - 140), (sx, sy - 172), (sx + 46, sy - 140), (sx + 30, sy - 110), (sx + 26, sy - 60)]), paint(rgb(150, 108, 64)))


# ------------------------------------------------------------------ captions
def chunks():
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        txt = ' '.join(x['w'] for x in cur)
        end = w['w'][-1] in ',.'
        if end or len(cur) >= 3 or len(txt) >= 15:
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    res = []
    for i, ch in enumerate(out):
        s = ch[0]['s']
        e = ch[-1]['e'] + 0.25
        if i + 1 < len(out):
            e = min(e, out[i + 1][0]['s'])
        res.append((s, e, ' '.join(x['w'] for x in ch).rstrip(',.')))
    return res


CHUNKS = chunks()


def captions(c, t):
    for (s, e, txt) in CHUNKS:
        if s - 0.03 <= t < e:
            a = clamp((t - s + 0.03) / 0.08)
            text(c, txt, W / 2, 1368, TF_OSWALD, 50, BONE, align='center', alpha=int(255 * a), shadow=True)
            return


# ------------------------------------------------------------------ loop-safe ambient motion
def lsin(t, w, ph=0.0):
    """sine whose frequency is rounded so it repeats exactly over the whole video (seamless loop)"""
    k = max(1, round(w * T_TOTAL / (2 * math.pi)))
    return math.sin(2 * math.pi * k / T_TOTAL * t + ph)


def flicker(t):  # noqa: F811  (loop-safe version)
    return 1 + 0.08 * lsin(t, 9.3) + 0.05 * lsin(t, 15.1, 1) + 0.04 * lsin(t, 4.1)


def hair_strands(c, t):  # noqa: F811
    for (x0, ph, dx, ln, wd) in HAIR_STRANDS:
        sw = 26 * lsin(t, 1.3, ph) + 12 * lsin(t, 2.7, ph * 2)
        p = skia.Path()
        p.moveTo(x0, -40)
        p.cubicTo(x0 + dx * 0.4 + sw * 0.3, ln * 0.3, x0 + dx * 0.8 + sw, ln * 0.65, x0 + dx + sw * 1.4, ln)
        pp = paint(C(HAIR, 150), stroke=wd)
        pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
        c.drawPath(p, pp)


def lap_d(c, t):  # noqa: F811
    c.drawPath(smooth_path([(-60, 1296), (300, 1318), (700, 1308), (1140, 1290), (1140, 1990), (-60, 1990)]), paint(C(SILK_DK)))
    for k, x in enumerate((90, 330, 600, 860)):
        sw = 8 * lsin(t, 0.9, k)
        c.drawPath(smooth_path([(x - 26, 1320), (x + 18 + sw, 1500), (x - 8, 1700), (x + 34 + sw, 1990), (x + 70, 1990),
                                (x + 46 + sw, 1700), (x + 64, 1480), (x + 24, 1320)]), paint(C(SILK, 230)))
        c.drawPath(smooth_path([(x + 6, 1340), (x + 30 + sw, 1520), (x + 20, 1720), (x + 44 + sw, 1990), (x + 52, 1990),
                                (x + 36 + sw, 1720), (x + 40, 1520), (x + 18, 1340)]), paint(C(SILK_LT, 120)))


# ------------------------------------------------------------------ the wide world (Doreah at the fire)
S_MAP = 3.97
P_BOOK = (196.0, 250.0)
P_WIDE = (590.0, 1360.0)
RB = (0, 226, 1010, 1296)  # region of the book frame shown as the book on her lap


def f2w(p):
    return (P_WIDE[0] + (p[0] - P_BOOK[0]) / S_MAP, P_WIDE[1] + (p[1] - P_BOOK[1]) / S_MAP)


def w2f(p):
    return (P_BOOK[0] + (p[0] - P_WIDE[0]) * S_MAP, P_BOOK[1] + (p[1] - P_WIDE[1]) * S_MAP)


BOOK_WR = (*f2w((RB[0], RB[1])), *f2w((RB[2], RB[3])))
HORIZON = 900
FIRE_W = (700, 1175)
HIP = (300, 1640)
SH_R = (160, -300)
ARM_A, ARM_B = 235, 215


def ik(S, T, a, b, bend=1):
    dx, dy = T[0] - S[0], T[1] - S[1]
    d = min(math.hypot(dx, dy), a + b - 1)
    th = math.atan2(dy, dx)
    ca = clamp((a * a + d * d - b * b) / (2 * a * d), -1, 1)
    al = math.acos(ca)
    e_ang = th + bend * al
    E = (S[0] + a * math.cos(e_ang), S[1] + a * math.sin(e_ang))
    Hh = (S[0] + d * math.cos(th), S[1] + d * math.sin(th))
    return E, Hh


REST = (275, -30)
ARM_KEYS = [(32.0, REST), (33.55, REST), (34.15, (440, 10)), (34.45, (360, -70)), (34.8, (330, -600)), (35.25, (420, -420)), (35.9, REST),
            (36.15, REST), (36.75, (430, 20)), (37.05, (360, -70)), (37.35, (330, -600)), (37.8, (420, -420)), (38.3, REST),
            (38.75, REST), (39.45, (250, -720)), (41.6, (252, -716)), (42.2, REST)]


def key_interp(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1:
            u = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            return lerp2(v0, v1, u)
    return keys[-1][1]


def doreah_pose(t):
    p = {}
    rec = ramp(t, 32.45, 32.9) * (1 - ramp(t, 33.4, 34.0))
    p['dy'] = 22 * rec
    p['lean'] = -3 * rec
    shake = 0.0
    if 42.85 <= t <= 43.95:
        shake = 14 * math.sin((t - 42.85) / 1.1 * 4 * math.pi) * math.sin((t - 42.85) / 1.1 * math.pi)
    follow = 18 * math.sin((t - 32.5) * 2.1) * rec
    p['head_dx'] = shake + follow
    p['look'] = ramp(t, 43.9, 44.6) * (1 - ramp(t, 46.4, 47.3))
    tgt = key_interp(ARM_KEYS, t)
    if 39.45 < t < 41.6:
        tgt = (tgt[0] + 2 * math.sin(t * 13), tgt[1] + 2 * math.sin(t * 17))
    p['hand'] = tgt
    if 33.9 <= t < 34.8 or 36.5 <= t < 37.35:
        p['kind'] = 'fist'
    elif 39.1 <= t < 41.7:
        p['kind'] = 'point'
    else:
        p['kind'] = 'grip'
    p['hold'] = 'book' if 34.15 <= t < 34.8 else ('vial' if 36.75 <= t < 37.35 else None)
    p['wind'] = 1.0 + 1.5 * ramp(t, 46.3, 47.0) * (1 - ramp(t, 49.0, 49.6))
    return p


def l2w(p, local):
    a = math.radians(p['lean'])
    x, y = local
    xr, yr = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (HIP[0] + xr, HIP[1] + yr + p['dy'])


D_SILK = (64, 26, 32)
D_SILK2 = (84, 34, 40)
D_HAIR = (104, 86, 60)
D_SKIN = (112, 78, 62)


def _arm_paths(p):
    E, Hh = ik(SH_R, p['hand'], ARM_A, ARM_B, bend=1)
    paths = []
    for (a_, b_, w0, w1) in ((SH_R, E, 74, 54), (E, Hh, 50, 34)):
        ang = math.atan2(b_[1] - a_[1], b_[0] - a_[0])
        nx, ny = -math.sin(ang), math.cos(ang)
        paths.append(poly([(a_[0] + nx * w0 / 2, a_[1] + ny * w0 / 2), (b_[0] + nx * w1 / 2, b_[1] + ny * w1 / 2),
                           (b_[0] - nx * w1 / 2, b_[1] - ny * w1 / 2), (a_[0] - nx * w0 / 2, a_[1] - ny * w0 / 2)]))
    paths.append(skia.Path().addCircle(*E, 28))
    return E, Hh, paths


def _hand_path(Hh, ang, kind):
    m = skia.Matrix()
    m.setTranslate(*Hh)
    m.preRotate(math.degrees(ang))
    p = skia.Path().addOval(R(-6, -21, 38, 21))
    if kind == 'point':
        f = skia.Path().addRoundRect(R(-6, -70, 8, 0), 7, 7)
        mf = skia.Matrix(); mf.setRotate(-math.degrees(ang) - 90)
        f.transform(mf)
        p = skia.Op(p, f, skia.PathOp.kUnion_PathOp)
    p.transform(m)
    return p


def doreah_shapes(t, p):
    """all body paths in local coords: dict of name -> path (lap separate)"""
    w = p['wind']
    br = 1 + 0.01 * lsin(t, 1.6)
    sh = {}
    sh['skirt'] = smooth_path([(-150, -20), (-250, 70), (-330, 230), (-350, 380), (360, 380), (330, 200), (250, 60), (150, -20)])
    sh['larm'] = smooth_path([(-140, -318), (-188, -292), (-208, -200), (-206, -112), (-176, -96), (-160, -190), (-150, -270)])
    sh['torso'] = smooth_path([(-112, -30), (-136, -150 * br), (-160, -262 * br), (-170, -300 * br), (-138, -336 * br), (-60, -360 * br),
                               (-34, -382 * br), (34, -382 * br), (60, -360 * br), (138, -336 * br), (170, -300 * br), (160, -262 * br),
                               (136, -150 * br), (112, -30)])
    hx, hy = p['head_dx'], -462 + 18 * p['look']
    ry = 80 - 10 * p['look']
    sw = [9 * w * lsin(t, 1.1, k) + 5 * w * lsin(t, 2.3, k * 1.7) for k in range(7)]
    hair = [(hx - 58, hy - ry * 0.55), (hx - 70, hy + 10), (hx - 74, hy + 70), (-92 + sw[0] * 0.5, -330), (-102 + sw[1], -250),
            (-98 + sw[2], -170), (-84 + sw[3], -118), (-60 + sw[4], -140), (-40 + sw[5], -104), (-12 + sw[6], -128), (14 + sw[5], -98),
            (40 + sw[4], -126), (64 + sw[3], -106), (86 + sw[2], -150), (100 + sw[1], -236), (94 + sw[0] * 0.5, -326),
            (hx + 74, hy + 70), (hx + 70, hy + 10), (hx + 58, hy - ry * 0.55), (hx + 30, hy - ry * 0.95), (hx - 30, hy - ry * 0.95)]
    sh['hair'] = smooth_path(hair)
    E, Hh, arm = _arm_paths(p)
    ang = math.atan2(Hh[1] - E[1], Hh[0] - E[0])
    sh['rarm'] = arm
    sh['hand'] = _hand_path(Hh, ang, p['kind'])
    return sh, E, Hh, ang, (hx, hy, sw)


def doreah_lap(c, t, p):
    c.save()
    c.translate(HIP[0], HIP[1] + p['dy']); c.rotate(p['lean'])
    lap = smooth_path([(100, -20), (170, -190), (300, -232), (470, -226), (548, -150), (540, 20), (320, 64), (150, 44)])
    c.drawPath(lap, paint(C(D_SILK)))
    c.drawPath(smooth_path([(470, -226), (548, -150), (540, 20), (500, -40), (500, -170)]), paint(C(D_SILK2)))
    c.restore()


def doreah(c, t, p):
    """seen from behind, backlit by the fire in front of her: dark body, warm rim on the outer edge, soft bloom"""
    sh, E, Hh, ang, (hx, hy, sw) = doreah_shapes(t, p)
    union = skia.Path(sh['skirt'])
    for k in ('larm', 'torso', 'hair', 'hand'):
        union = skia.Op(union, sh[k], skia.PathOp.kUnion_PathOp)
    for ap in sh['rarm']:
        union = skia.Op(union, ap, skia.PathOp.kUnion_PathOp)
    fl = flicker(t)
    c.save()
    c.translate(HIP[0], HIP[1] + p['dy'])
    c.rotate(p['lean'])
    fx, fy = FIRE_W[0] - HIP[0], FIRE_W[1] - HIP[1] - p['dy']
    # bloom of firelight around her outline
    bloom = paint(rgb(255, 140, 60, int(70 * min(fl, 1.2))))
    bloom.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 26))
    c.drawPath(union, bloom)
    c.saveLayer()
    c.drawPath(sh['skirt'], paint(C(D_SILK)))
    c.drawPath(sh['larm'], paint(C(D_SILK2)))
    c.drawPath(sh['torso'], paint(C(D_SILK)))
    c.drawLine(-110, -64, 110, -64, paint(C(GOLD, 150), stroke=4))
    c.drawPath(sh['hair'], paint(C(D_HAIR)))
    for k in range(7):   # strands
        x0 = hx - 54 + k * 18
        st = skia.Path(); st.moveTo(x0, hy + 20)
        st.cubicTo(x0 * 1.1, -300, x0 * 1.05 + sw[k] * 0.6, -220, x0 * 0.95 + sw[k], -130 - (k % 3) * 14)
        c.drawPath(st, paint(rgb(132, 112, 80, 150), stroke=3))
    c.drawPath(sh['rarm'][0], paint(C(D_SILK2)))
    c.drawPath(sh['rarm'][2], paint(C(D_SILK2)))
    c.drawPath(sh['rarm'][1], paint(C(D_SKIN)))
    c.drawPath(sh['hand'], paint(C(D_SKIN)))
    for k in range(3):
        u = 0.78 + 0.06 * k
        bx, by = lerp(E[0], Hh[0], u), lerp(E[1], Hh[1], u)
        nx, ny = -math.sin(ang), math.cos(ang)
        c.drawLine(bx + nx * 19, by + ny * 19, bx - nx * 19, by - ny * 19, paint(C(GOLD, 230), stroke=4))
    # rim light on the outer silhouette, strongest toward the fire
    rim = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kSrcATop, Style=skia.Paint.kStroke_Style, StrokeWidth=12)
    rim.setShader(skia.GradientShader.MakeRadial(P(fx, fy), 950, [rgb(255, 196, 120, int(250 * min(fl, 1.1) / 1.1)), rgb(255, 150, 80, 120), rgb(255, 130, 60, 10)], [0, 0.5, 1]))
    rim.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.5))
    c.drawPath(union, rim)
    wash = skia.Paint(BlendMode=skia.BlendMode.kSrcATop, Shader=skia.GradientShader.MakeRadial(P(fx, fy), 760, [rgb(255, 150, 70, 60), rgb(255, 120, 40, 0)]))
    c.drawRect(R(-600, -900, 900, 600), wash)
    c.restore()
    c.restore()
    return l2w(p, E), l2w(p, Hh)


def sky(c, t):
    g = skia.GradientShader.MakeLinear([P(0, -1200), P(0, HORIZON)], [rgb(8, 10, 20), rgb(14, 17, 30), rgb(48, 40, 60)], [0, 0.6, 1])
    c.drawRect(R(-200, -1300, W + 200, HORIZON + 40), skia.Paint(Shader=g))
    for (x, y, r, ph) in WSTARS:
        a = int(150 + 80 * lsin(t, 1.3, ph))
        c.drawCircle(x, y, r, paint(rgb(230, 223, 208, a)))


_rs = np.random.default_rng(17)
WSTARS = [(_rs.uniform(-40, W + 40), _rs.uniform(-1250, HORIZON - 40), _rs.uniform(0.9, 2.6), _rs.uniform(0, 6.28)) for _ in range(420)]
CONST = [(80, 200), (170, -390), (330, -270), (520, -110), (690, 20), (760, -300), (830, -530)]
COMET_H = (785, -360)


def constellation(c, t):
    u = clamp((t - 45.09) / 0.85)
    if u <= 0:
        return
    nseg = len(CONST) - 1
    for i in range(nseg):
        a = clamp(u * nseg - i)
        if a <= 0:
            continue
        p0, p1 = CONST[i], CONST[i + 1]
        c.drawLine(*p0, *lerp2(p0, p1, a), blur_paint(rgb(255, 200, 110, 120), 6))
        c.drawLine(*p0, *lerp2(p0, p1, a), paint(rgb(236, 200, 120, 235), stroke=4))
    for i, (x, y) in enumerate(CONST):
        a = clamp(u * nseg - i + 1)
        if a > 0:
            c.drawCircle(x, y, 20, blur_paint(rgb(255, 230, 170, int(120 * a)), 8))
            c.drawCircle(x, y, 6.5, paint(rgb(255, 244, 214, int(255 * a))))
    la = clamp((t - 45.5) / 0.5)
    if la > 0:
        text(c, 'LONG NIGHT', 196, -428, TF_CINZEL_B, 34, BONE, alpha=int(240 * la), shadow=True)
        text(c, 'SUMMERHALL · 259 AC', 470, 92, TF_CINZEL_B, 30, BONE, alpha=int(235 * la), shadow=True)
        text(c, '298 AC', 800, -560, TF_CINZEL_B, 34, BONE, align='right', alpha=int(240 * la), shadow=True)


def comet(c, t):
    u = ease_out(clamp((t - 44.3) / 0.8))
    if u <= 0:
        return
    hx, hy = lerp2((1350, -1050), COMET_H, u)
    tx, ty = hx + 420, hy - 380
    ang = math.atan2(ty - hy, tx - hx)
    nx, ny = -math.sin(ang), math.cos(ang)
    for k, (wd, col, al) in enumerate(((70, (200, 70, 50), 0.55), (40, (240, 150, 70), 0.75), (16, (255, 225, 170), 0.95))):
        sh = 5 * lsin(t, 2.0, k)
        path = poly([(hx + nx * wd * 0.5, hy + ny * wd * 0.5), (tx + nx * (wd * 2.2 + sh), ty + ny * (wd * 2.2 + sh)),
                     (tx - nx * wd * 0.6, ty - ny * wd * 0.6), (hx - nx * wd * 0.5, hy - ny * wd * 0.5)])
        g = skia.GradientShader.MakeLinear([P(hx, hy), P(tx, ty)], [rgb(*col, int(255 * al)), rgb(*col, 0)])
        pp = skia.Paint(AntiAlias=True, Shader=g)
        pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8 + 4 * (2 - k)))
        c.drawPath(path, pp)
    additive_glow(c, hx, hy, 260, (255, 120, 60), 110)
    c.drawCircle(hx, hy, 16, blur_paint(rgb(255, 238, 205), 4))


STAR_SEER = Starseer()


def horizon_land(c, t):
    far = [(-40, 880), (140, 846), (300, 872), (470, 838), (620, 870), (760, 860), (900, 846), (1000, 852), (1120, 872), (1120, 960), (-40, 960)]
    c.drawPath(smooth_path(far), paint(rgb(32, 34, 46)))
    # the Starseer: a tiny figure with his telescope on the far hill (easter egg)
    c.drawCircle(968, 852, 26, blur_paint(rgb(255, 150, 70, 110), 9))
    c.drawCircle(968, 854, 3.5, paint(rgb(255, 190, 110)))
    pz = Pose(head=-30, look=0.8, ua=-60, fa=-30, hand=0, scroll=0.0, wind=t)
    c.saveLayer()
    STAR_SEER.draw(c, pz, 935, 850, 0.085)
    c.drawRect(R(880, 780, 990, 870), skia.Paint(BlendMode=skia.BlendMode.kSrcATop, Color=rgb(26, 26, 34)))
    c.restore()
    c.drawLine(944, 824, 918, 790, paint(rgb(26, 26, 34), stroke=3.5))
    c.drawRect(R(-40, HORIZON + 20, W + 40, 2000), paint(rgb(22, 21, 25)))
    g = skia.GradientShader.MakeLinear([P(0, HORIZON - 10), P(0, HORIZON + 260)], [rgb(30, 31, 40), rgb(22, 21, 25)])
    c.drawRect(R(-40, HORIZON - 10, W + 40, HORIZON + 260), skia.Paint(Shader=g))


def fire_flare(t):
    f = 1.0
    for t0 in (35.25, 37.8):
        if t >= t0:
            f += 0.75 * math.exp(-(t - t0) / 0.35)
    return f


def wide_fire(c, t):
    fx, fy = FIRE_W
    fl = flicker(t) * fire_flare(t)
    g = skia.GradientShader.MakeRadial(P(fx, fy - 30), 760 * (0.95 + 0.05 * fl), [rgb(130, 58, 20, int(min(170, 120 * fl))), rgb(60, 26, 8, 50), rgb(0, 0, 0, 0)], [0, 0.45, 1])
    c.drawRect(R(-200, -1300, W + 200, 2200), skia.Paint(Shader=g, BlendMode=skia.BlendMode.kPlus))
    sc = 1.1
    for k in range(7):
        a = math.pi * (0.05 + 0.9 * k / 6)
        c.drawOval(R(fx + math.cos(a) * 100 * sc - 28 * sc, fy + 10 * sc, fx + math.cos(a) * 100 * sc + 28 * sc, fy + 42 * sc), paint(rgb(58, 60, 66)))
    for ang in (-18, 16):
        c.save(); c.translate(fx, fy + 12 * sc); c.rotate(ang)
        c.drawRoundRect(R(-100 * sc, -13 * sc, 100 * sc, 13 * sc), 10, 10, paint(rgb(70, 46, 32)))
        c.restore()
    f2 = fire_flare(t)
    aflames(c, fx, fy + 8, 170 * sc * (0.9 + 0.1 * f2), 250 * sc * f2, t, seed=21)
    embers(c, t, fx - 140, fx + 140, fy - 60, 0.9 * min(f2, 1.4), 45)


def right_moment(c, t):
    a = clamp((t - 40.75) / 0.4) * (1 - clamp((t - 41.9) / 0.5))
    if a <= 0:
        return
    rise = 30 * clamp((t - 40.75) / 1.6)
    x, y = FIRE_W[0], FIRE_W[1] - 330 - rise
    f = skia.Font(TF_CINZEL_B, 50)
    s = 'THE RIGHT MOMENT'
    wd = f.measureText(s)
    x = min(x, W - 40 - wd / 2)
    gp = blur_paint(rgb(255, 190, 90, int(160 * a)), 12)
    c.drawString(s, x - wd / 2, y, f, gp)
    c.drawString(s, x - wd / 2, y, f, paint(rgb(255, 222, 150, int(255 * a))))
    for k in range(18):
        sx = x - wd / 2 + (k * 37 % int(wd))
        sy = y - 20 - ((t * 60 + k * 23) % 90)
        c.drawCircle(sx, sy, 2.2, paint(rgb(255, 200, 110, int(180 * a))))


def thrown(c, t, pose_hand):
    for (t0, t1, label, kind) in ((34.8, 35.25, 'KNOWLEDGE?', 'book'), (37.35, 37.8, 'BLOOD?', 'vial')):
        pick = 34.15 if kind == 'book' else 36.75
        if t < pick - 0.4 or t > t1:
            continue
        if t < pick:  # lying beside her, waiting
            pos = l2w(doreah_pose(t), (450, 20) if kind == 'book' else (440, 30))
            rot = -10
        elif t < t0:
            pos = pose_hand
            rot = -20
        else:
            u = (t - t0) / (t1 - t0)
            p0 = pose_hand_at(t0)
            p1 = (FIRE_W[0] + (10 if kind == 'book' else -20), FIRE_W[1] - 40)
            pos = (lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u) - 260 * math.sin(math.pi * u))
            rot = -20 + 540 * u
        c.save(); c.translate(*pos); c.rotate(rot)
        if kind == 'book':
            c.drawRoundRect(R(-30, -38, 30, 38), 5, 5, paint(rgb(110, 40, 30)))
            c.drawRect(R(-25, -33, 25, 33), paint(rgb(140, 56, 40)))
            c.drawRect(R(-8, -6, 8, 10), paint(C(GOLD)))
        else:
            c.drawPath(smooth_path([(-14, -30), (14, -30), (14, -14), (24, 6), (16, 30), (-16, 30), (-24, 6), (-14, -14)]), paint(rgb(170, 190, 200, 200)))
            c.drawPath(smooth_path([(-20, 8), (20, 8), (14, 28), (-14, 28)]), paint(rgb(150, 30, 34)))
            c.drawRect(R(-10, -42, 10, -28), paint(rgb(120, 90, 60)))
        c.restore()
        la = clamp((t - (pick - 0.3)) / 0.25) * (1 - clamp((t - (t1 - 0.12)) / 0.12))
        if la > 0:
            c.save(); c.translate(pos[0], pos[1] - 70)
            f = skia.Font(TF_OSWALD, 30)
            w = f.measureText(label)
            c.drawRoundRect(R(-w / 2 - 12, -30, w / 2 + 12, 10), 6, 6, paint(rgb(236, 222, 190, int(255 * la))))
            c.drawRoundRect(R(-w / 2 - 12, -30, w / 2 + 12, 10), 6, 6, paint(rgb(40, 32, 28, int(220 * la)), stroke=2.5))
            c.drawString(label, -w / 2, 0, f, paint(rgb(40, 32, 28, int(255 * la))))
            c.restore()


def pose_hand_at(t):
    p = doreah_pose(t)
    _, Hh = ik(SH_R, p['hand'], ARM_A, ARM_B, bend=1)
    return l2w(p, Hh)


# hatchlings: world-space states
EGG_W = f2w((540, 1205))
HATCH = [dict(acc=GLUT, out=(170, 1010), ph=0.0, land='arm', rest=(600, 1290), flip=True),
         dict(acc=GOLD, out=(640, 760), ph=2.1, land=(150, 1300), rest=(800, 1300), flip=False),
         dict(acc=BONE, out=(920, 1060), ph=4.2, land=(870, 1268), rest=(870, 1268), flip=False)]
ORB_C, ORB_R = (470, 980), (330, 150)


def bez(p0, p1, p2, u):
    return ((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0], (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1])


def orbit_pt(h, t):
    a = 1.15 * (t - 33.9) + h['ph']
    return (ORB_C[0] + ORB_R[0] * math.cos(a), ORB_C[1] + ORB_R[1] * math.sin(a)), a


def hatch_state(i, t):
    """(x, y, scale, rot, wing, flip, visible)"""
    h = HATCH[i]
    flap = 0.5 + 0.5 * math.sin(t * 15 + i * 1.7)
    if t < T_BURST:
        return None
    if t < 31.85:
        u = ease_out((t - T_BURST) / 0.6)
        off = [(-30, -40), (0, -60), (30, -40)][i]
        p = (EGG_W[0] + off[0] / S_MAP * u * 3, EGG_W[1] + off[1] / S_MAP * u * 3)
        return (p[0], p[1], lerp(0.08, 0.232, u), [-20, 0, 20][i], flap, h['flip'])
    if t < 33.9:
        u = ease((t - 31.85) / 2.05)
        start = (EGG_W[0] + [-30, 0, 30][i] / S_MAP * 3, EGG_W[1] - [40, 60, 40][i] / S_MAP * 3)
        target, _ = orbit_pt(h, 33.9)
        ctrl = (lerp(start[0], h['out'][0], 0.9), min(start[1], h['out'][1]) - 260)
        p = bez(start, ctrl, target, u)
        on_screen = lerp(0.92, 0.95, ease((t - 31.85) / 2.05))   # constant size on screen while the camera pulls back
        sc = on_screen / cam_state(t)[0]
        return (p[0], p[1], sc, 0, flap, h['flip'])
    if t < 38.9:
        p, a = orbit_pt(h, t)
        vx = -math.sin(a)
        depth = 0.95 + 0.1 * math.sin(a)
        return (p[0], p[1], depth, 8 * math.cos(a), flap, vx < 0)
    land = h['land']
    if t < 46.5:
        p0, _ = orbit_pt(h, 38.9)
        tgt = land
        if land == 'arm':
            pp = doreah_pose(t)
            E, Hh = ik(SH_R, pp['hand'], ARM_A, ARM_B, bend=1)
            tgt = l2w(pp, lerp2(E, Hh, 0.55))
            tgt = (tgt[0] + 10, tgt[1] - 40)
        u = ease(clamp((t - 38.9) / 1.3))
        p = (lerp(p0[0], tgt[0], u), lerp(p0[1], tgt[1], u) - 120 * math.sin(math.pi * u))
        wing = flap if u < 0.95 else 0.05 + 0.03 * math.sin(t * 2)
        return (p[0], p[1], 0.74, 0, wing, h['flip'] if u > 0.5 else HATCH[i]['flip'])
    # fly down to the fire and curl up
    pp = doreah_pose(46.5)
    if land == 'arm':
        E, Hh = ik(SH_R, pp['hand'], ARM_A, ARM_B, bend=1)
        p0 = l2w(pp, lerp2(E, Hh, 0.55)); p0 = (p0[0] + 10, p0[1] - 40)
    else:
        p0 = land
    u = ease(clamp((t - 46.5) / 1.1))
    p = (lerp(p0[0], h['rest'][0], u), lerp(p0[1], h['rest'][1], u) - 90 * math.sin(math.pi * u))
    wing = flap if 0.02 < u < 0.95 else 0.05
    return (p[0], p[1], 0.72, 0, wing, h['flip'])


def draw_hatchlings(c, t, mapper=None):
    for i, h in enumerate(HATCH):
        st = hatch_state(i, t)
        if st is None:
            continue
        x, y, s, rot, wing, flip = st
        if mapper:
            (x, y), s = mapper((x, y)), s * S_MAP
        hatchling(c, x, y, s, flip=flip, wing=wing, accent=h['acc'], rot=rot)


def wide_book(c, t, tex):
    x0, y0, x1, y1 = BOOK_WR
    outline = skia.RRect.MakeRectXY(R(x0 + 6, y0 - 2, x1 + 2, y1 + 4), 4, 4)
    c.drawRRect(skia.RRect.MakeRectXY(R(x0 + 4, y0 - 4, x1 + 4, y1 + 6), 5, 5), paint(rgb(70, 42, 28)))
    c.save()
    c.clipRRect(outline, skia.ClipOp.kIntersect, True)
    c.drawImageRect(tex, R(*RB), R(x0, y0, x1, y1), SAMP, None)
    # the page glows when it holds the burning plate
    if t < 46.9:
        g = skia.GradientShader.MakeRadial(P(*f2w((540, 760))), 160, [rgb(255, 150, 70, 60), rgb(255, 120, 40, 0)])
        c.drawRect(R(x0, y0, x1, y1), skia.Paint(Shader=g, BlendMode=skia.BlendMode.kPlus))
    c.restore()


def cam_state(t):
    """returns (scale, world point at screen centre)"""
    def from_map(s):
        return s, (P_WIDE[0] + (540 - P_BOOK[0]) / s, P_WIDE[1] + (960 - P_BOOK[1]) / s)
    Q = f2w((593, 760))          # page centre (world)
    q_map = (593.0, 760.0)       # its screen position in the book shot

    def zoom(u):
        s = math.exp(lerp(math.log(S_MAP), 0.0, u))
        q = lerp2(q_map, Q, u)   # default view: screen == world
        return s, (Q[0] - (q[0] - 540) / s, Q[1] - (q[1] - 960) / s)
    if t < 32.35:
        return from_map(S_MAP)
    if t < 33.9:
        return zoom(ease((t - 32.35) / 1.55))
    drift = 1 + 0.03 * ramp(t, 33.9, 43.7)
    if t < 43.7:
        return drift, (540, 960 + 10 * ramp(t, 33.9, 43.7))
    if t < 47.6:
        up = ease(clamp((t - 43.7) / 1.3)) * (1 - ease(clamp((t - 46.2) / 1.35)))
        return drift * (1 - 0.03 * ramp(t, 46.2, 47.5)), (540, 970 - 950 * up)
    return zoom(1 - ease((t - 47.6) / 1.8))


def wide_scene(c, t, tex):
    s, wc = cam_state(t)
    c.save()
    c.translate(540, 960)
    c.scale(s, s)
    c.translate(-wc[0], -wc[1])
    sky(c, t)
    comet(c, t)
    constellation(c, t)
    horizon_land(c, t)
    wide_fire(c, t)
    right_moment(c, t)
    p = doreah_pose(t)
    hand_w = pose_hand_at(t)
    thrown(c, t, hand_w)
    # her lap + book, then her figure
    doreah_lap(c, t, p)
    wide_book(c, t, tex)
    doreah(c, t, p)
    draw_hatchlings(c, t)
    # foreground grass
    for (x, sc) in ((960, 1.0), (1040, 0.8)):
        for k in range(6):
            a = -90 + (k - 2.5) * 12 + 4 * lsin(t, 1.0, k)
            ln = (90 + 30 * (k % 3)) * sc
            c.drawLine(x + k * 8, 1925, x + k * 8 + math.cos(math.radians(a)) * ln, 1925 + math.sin(math.radians(a)) * ln, paint(rgb(14, 14, 16), stroke=7 * sc))
    c.restore()


# ------------------------------------------------------------------ compositor
def burn_scene(c, t):
    under_page(c, t)
    r = hole_radius(t)
    c.saveLayer()
    book_frame(c, t)
    if r > 0:
        hp = hole_path(t, r)
        c.drawPath(hp, paint(rgb(54, 28, 16, 235), stroke=64))
        clr = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kClear)
        c.drawPath(hp, clr)
    c.restore()
    if r > 0:
        hp = hole_path(t, r)
        c.drawPath(hp, paint(rgb(255, 150, 60), stroke=7))
        ge = paint(rgb(255, 190, 90), stroke=18)
        ge.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        c.drawPath(hp, ge)
        m = skia.PathMeasure(hp, True)
        L = m.getLength()
        for k in range(12):
            pos, tan = m.getPosTan(L * (k + 0.5) / 12)
            if pos is None:
                continue
            fs = 0.7 + 0.3 * math.sin(k * 1.7)
            aflames(c, pos.x(), pos.y() + 16, 110 * fs, 120 * fs, t, seed=60 + k, a=220)


def hole_path(t, r):
    n = 48
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + 0.14 * math.sin(3 * a + 0.7 + 0.3 * t) + 0.08 * math.sin(5 * a + 2.1) + 0.05 * math.sin(9 * a + 1.3 + t))
        pts.append((HOLE_C[0] + math.cos(a) * rr, HOLE_C[1] + math.sin(a) * rr * 1.15))
    return smooth_path(pts)


def pyre_scene(c, t):
    under_page(c, t)
    draw_egg_top(c, t)
    draw_hatchlings(c, t, mapper=w2f)


def surface_img(fn, t):
    s = skia.Surface(W, H)
    fn(s.getCanvas(), t)
    return s.makeImageSnapshot()


def book_tex(t):
    if t < 46.9:
        return surface_img(lambda c, t: under_page(c, t), t)
    s = skia.Surface(W, H)
    book_frame(s.getCanvas(), t, page_only=True)
    return s.makeImageSnapshot()


def blend(c, fa, fb, u, t):
    fa(c, t)
    if u > 0:
        img = surface_img(fb, t)
        pp = skia.Paint(); pp.setAlphaf(clamp(u))
        c.drawImage(img, 0, 0, SAMP, pp)


def scene(c, t):
    if t < 21.95:
        book_frame(c, t)
    elif t < 25.5:
        burn_scene(c, t)
        draw_egg_top(c, t)
    elif t < 32.0:
        pyre_scene(c, t)
    elif t < 32.35:
        tex = book_tex(t)
        blend(c, pyre_scene, lambda c, t: wide_scene(c, t, tex), (t - 32.0) / 0.35, t)
    elif t < 49.4:
        wide_scene(c, t, book_tex(t))
    elif t < 49.7:
        tex = book_tex(t)
        blend(c, lambda c, t: wide_scene(c, t, tex), book_frame, (t - 49.4) / 0.3, t)
    else:
        book_frame(c, t)
    captions(c, t)


_r = np.random.default_rng(3)
GRAIN = [_r.normal(0, 4.2, (H, W, 1)).astype(np.float32) for _ in range(6)]
YY, XX = np.mgrid[0:H, 0:W]
VIGN = (1 - 0.3 * np.clip(np.sqrt(((XX - W / 2) / (W * 0.72)) ** 2 + ((YY - H / 2) / (H * 0.7)) ** 2) - 0.35, 0, 1) ** 1.4)[..., None].astype(np.float32)


def frame(t, idx=0):
    s = skia.Surface(W, H)
    scene(s.getCanvas(), t)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    a = a * VIGN + GRAIN[idx % 6]
    return np.clip(a, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    import subprocess
    if sys.argv[1] == 'still':
        os.makedirs(D + 'stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            Image.fromarray(frame(t, int(t * FPS))).save(D + f'stills/s_{t:05.2f}.png')
        print('ok')
    elif sys.argv[1] == 'range':
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
               '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(i0, i1):
            p.stdin.write(frame(i / FPS, i).tobytes())
            if i % 60 == 0:
                print(out, i, flush=True)
        p.stdin.close(); p.wait()
        print('done', out)
