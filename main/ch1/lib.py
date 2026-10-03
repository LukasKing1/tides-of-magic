"""Shared drawing toolkit for the main video (16:9). Design space is 1920x1080; the master can be
rendered larger by scaling the canvas (SCALE) - all coordinates below stay in design space."""
import math, contextlib
import numpy as np
import skia
from PIL import Image

W, H, FPS = 1920, 1080, 30
FD = '/home/claude/test/fonts/'
P = skia.Point
R = skia.Rect
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)

# palette (shared with the Short)
BONE = (230, 223, 208)
GOLD = (216, 179, 92)
GOLD_LT = (246, 222, 150)
GLUT = (196, 83, 46)
INK = (40, 32, 28)
ICE = (158, 211, 228)
NIGHT = (14, 17, 30)


def rgb(r, g, b, a=255):
    return skia.ColorSetARGB(int(max(0, min(255, a))), int(r), int(g), int(b))


def C(t, a=255):
    return rgb(t[0], t[1], t[2], a)


def mix(a, b, u):
    return tuple(a[i] + (b[i] - a[i]) * u for i in range(3))


def paint(col, aa=True, stroke=None, cap=None):
    p = skia.Paint(AntiAlias=aa, Color=col)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap is None else cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def blur_paint(col, sigma, stroke=None):
    p = paint(col, stroke=stroke)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


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


def win(t, a, b, fi=0.4, fo=0.4):
    """1 inside [a, b] with soft edges"""
    return ramp(t, a - fi, a) * (1 - ramp(t, b, b + fo))


def popout(u):
    u = clamp(u)
    c1 = 1.70158
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def popv(t, t0, dur=0.42, t1=None, d1=0.3):
    if t < t0:
        return 0.0
    v = popout((t - t0) / dur)
    if t1 is not None and t > t1:
        v *= 1 - ease((t - t1) / d1)
    return max(v, 0.0)


def lerp(a, b, u):
    return a + (b - a) * u


def lerp2(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def key_interp(keys, t, fn=None):
    fn = fn or ease
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t <= t1:
            u = fn((t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return keys[-1][1]


def flicker(t, ph=0.0):
    return 1 + 0.08 * math.sin(t * 9.3 + ph) + 0.05 * math.sin(t * 15.1 + 1 + ph) + 0.04 * math.sin(t * 4.1 + ph)


# ------------------------------------------------------------------ paths
def poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def smooth_path(pts, closed=True):
    path = skia.Path()
    n = len(pts)
    if n < 2:
        return path
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path


def wobbly(cx, cy, rx, ry, seed, n=40, amp=0.12):
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 3)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + amp * (0.6 * math.sin(3 * a + ph[0]) + 0.3 * math.sin(5 * a + ph[1]) + 0.2 * math.sin(9 * a + ph[2]))
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return smooth_path(pts)


@contextlib.contextmanager
def saved(c):
    c.save()
    yield
    c.restore()


@contextlib.contextmanager
def folded(c, ax, ay, s):
    """pop-up: scale y about a baseline"""
    c.save()
    c.translate(ax, ay)
    c.scale(1, max(s, 0.0001))
    c.translate(-ax, -ay)
    yield
    c.restore()


@contextlib.contextmanager
def layer_alpha(c, a):
    if a >= 0.999:
        yield
        return
    pp = skia.Paint()
    pp.setAlphaf(max(0.0, a))
    c.saveLayer(None, pp)
    yield
    c.restore()


# ------------------------------------------------------------------ text
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
TF_CORM = typeface('CormorantGaramond[wght].ttf', 500)
TF_CORM_I = typeface('CormorantGaramond-Italic[wght].ttf', 500)
TF_FELL = skia.Typeface.MakeFromFile(FD + 'IMFeENrm28P.ttf')
TF_FELL_I = skia.Typeface.MakeFromFile(FD + 'IMFeENit28P.ttf')
TF_FELL_SC = skia.Typeface.MakeFromFile(FD + 'IMFeENsc28P.ttf')
TF_OSWALD = typeface('Oswald[wght].ttf', 500)


def text(c, s, x, y, tf, size, col, align='left', alpha=255, rot=0, shadow=False, spacing=0.0):
    f = skia.Font(tf, size)
    if spacing:
        wsum = sum(f.measureText(ch) for ch in s) + spacing * (len(s) - 1)
    else:
        wsum = f.measureText(s)
    ox = {'left': 0, 'center': -wsum / 2, 'right': -wsum}[align]
    c.save()
    c.translate(x, y)
    if rot:
        c.rotate(rot)
    if shadow:
        sp = blur_paint(rgb(0, 0, 0, int(170 * alpha / 255)), 6)
        c.drawString(s, ox + 2, 3, f, sp)
    pp = paint(C(col, alpha))
    if spacing:
        xx = ox
        for ch in s:
            c.drawString(ch, xx, 0, f, pp)
            xx += f.measureText(ch) + spacing
    else:
        c.drawString(s, ox, 0, f, pp)
    c.restore()
    return wsum


def text_width(s, tf, size):
    return skia.Font(tf, size).measureText(s)


# ------------------------------------------------------------------ effects
def additive_glow(c, x, y, r, col, a):
    if a <= 0:
        return
    g = skia.GradientShader.MakeRadial(P(x, y), r, [rgb(*col, int(a)), rgb(*col, 0)])
    c.drawCircle(x, y, r, skia.Paint(Shader=g, BlendMode=skia.BlendMode.kPlus))


def radial_wash(c, x, y, r, col, a, rect=None):
    g = skia.GradientShader.MakeRadial(P(x, y), r, [rgb(*col, int(a)), rgb(*col, 0)])
    c.drawRect(rect or R(-500, -500, W + 500, H + 500), skia.Paint(Shader=g))


def flames(c, x, y, w, h, t, seed=0, cols=((196, 83, 46), (238, 150, 64), (252, 222, 160)), n=3, a=255):
    """layered flat flame tongues anchored at (x, y) bottom-centre"""
    if w <= 1 or h <= 1:
        return
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 8)
    for k, col in enumerate(cols):
        s = 1 - k * 0.27
        ww, hh = w * s, h * s
        pts = [(x - ww / 2, y)]
        tips = 3 if k < 2 else 2
        for i in range(tips):
            u = (i + 0.5) / tips
            sway = 0.10 * ww * math.sin(t * (6 + i) + ph[i] + k)
            hgt = hh * (0.62 + 0.38 * math.sin(math.pi * u)) * (0.86 + 0.14 * math.sin(t * (8.3 + i * 1.7) + ph[i + 3]))
            pts.append((x - ww / 2 + ww * (u - 0.25 / tips), y - hgt * 0.45))
            pts.append((x - ww / 2 + ww * u + sway, y - hgt))
        pts.append((x + ww / 2, y))
        pts.append((x, y + ww * 0.06))
        c.drawPath(smooth_path(pts), paint(C(col, a)))


class Embers:
    def __init__(self, n, seed, x0, x1, y0, rise=(60, 160), life=(2.0, 4.0), r=(1.4, 3.4)):
        rng = np.random.default_rng(seed)
        self.e = [dict(x=rng.uniform(x0, x1), t0=rng.uniform(0, 4), sp=rng.uniform(*rise), r=rng.uniform(*r),
                       life=rng.uniform(*life), ph=rng.uniform(0, 6.28)) for _ in range(n)]
        self.y0 = y0

    def draw(self, c, t, strength=1.0, col=(255, 170, 70), dx=0.0, dy=0.0, wind=18.0):
        if strength <= 0:
            return
        for e in self.e:
            age = (t - e['t0']) % e['life']
            u = age / e['life']
            x = e['x'] + wind * math.sin(t * 1.7 + e['ph']) + dx + 30 * u * wind / 18
            y = self.y0 - e['sp'] * age + dy
            a = int(255 * (1 - u) * strength * (0.6 + 0.4 * math.sin(t * 11 + e['ph'] * 9)))
            if a > 0:
                c.drawCircle(x, y, e['r'], paint(rgb(*col, a)))


# ------------------------------------------------------------------ textures
def value_noise(w, h, cx, cy, seed):
    rng = np.random.default_rng(seed)
    r = rng.random((cy, cx))
    return np.asarray(Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255


def parchment(w, h, seed=1, base=(228, 208, 168)):
    rng = np.random.default_rng(seed)
    n1, n2 = value_noise(w, h, w // 90 + 2, h // 90 + 2, seed), value_noise(w, h, w // 14, h // 14, seed + 1)
    fine = rng.normal(0, 1, (h, w)).astype(np.float32)
    col = np.array(base, np.float32)[None, None] * (0.93 + 0.07 * n1[..., None]) * (0.975 + 0.025 * n2[..., None]) + fine[..., None] * 2.5
    a = np.full((h, w, 1), 255, np.float32)
    return skia.Image.fromarray(np.clip(np.concatenate([col, a], 2), 0, 255).astype(np.uint8))


def to_image(arr):
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.full(arr.shape[:2] + (1,), 255, arr.dtype)], 2)
    return skia.Image.fromarray(np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8)))


def load_img(path):
    a = np.asarray(Image.open(path).convert('RGBA'))
    return skia.Image.fromarray(a.copy())


def draw_img(c, img, dst, alpha=1.0):
    pp = skia.Paint(AntiAlias=True)
    pp.setAlphaf(alpha)
    c.drawImageRect(img, R(0, 0, img.width(), img.height()), dst, SAMP, pp)


def surface(w=W, h=H):
    return skia.Surface(w, h)
