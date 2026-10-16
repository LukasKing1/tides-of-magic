#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Testanimation Cold Open (00-01 bis 00-09).

Stil: Rational Animations (Anthrazit, knochenweisse Figuren mit Tuschekontur,
Rasterpunkte, Filmkorn, gedaempfte Palette) + Kurzgesagt (leuchtende Bedrohungsfarbe).
Rendern:  python3 coldopen.py render <start_frame> <end_frame> <out.mp4>
Standbild: python3 coldopen.py still <sekunde> <out.png>
"""
import math, os, random, subprocess, sys
import numpy as np
import skia

W, H, FPS = 1920, 1080, 24
DUR = 60.0
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = lambda n: skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', n))
TF_SUB = FONT('Oswald_400Regular.ttf')
TF_TITLE = FONT('Cinzel_900Black.ttf')
TF_CAPS = FONT('Cinzel_700Bold.ttf')
TF_QUOTE = FONT('IMFellEnglish_400Regular_Italic.ttf')

# ---------------------------------------------------------------- Palette
BG = '#191a1a'
BG_BAND = '#1d1f1e'
DOT = '#2c2e2d'
INK = '#0b0c0c'
BONE = '#c6c4b8'
BONE_SH = '#9d9c92'
BONE_HI = '#dcdacd'
GOLD = '#d4ad5f'
GOLD_HI = '#ffe2a0'
GOLD_DK = '#8a6a33'
RED = '#9c4436'
RED_DK = '#6e2f27'
SNAKE = '#566d5c'
SNAKE_DK = '#3c4c40'
SNAKE_LT = '#7d9480'
AMBER = '#dba443'
TRUNK = '#302c29'
TRUNK_DK = '#221f1d'
CROWN = '#262926'
CROWN_DK = '#1e201f'
CROWN_LT = '#363a36'
LEAF = '#6b7f62'


def col(h, a=1.0):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(max(0, min(1, a)) * 255))


def mix(h1, h2, x):
    a = [int(h1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * max(0, min(1, x))) for i in range(3))


# ---------------------------------------------------------------- Easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= b)


def eio(x):
    x = clamp(x)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ein(x):
    x = clamp(x)
    return x ** 3


def eback(x, s=1.7):
    x = clamp(x) - 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def lerp(a, b, x):
    return a + (b - a) * x


# ---------------------------------------------------------------- Line boil
class G:
    frame = 0
    zoom = 1.0
    _cache = {}


def boil():
    """Leichtes 'Linienzittern' wie handgezeichnet: zufaellige Auslenkung, dann Ecken gerundet."""
    key = (G.frame // 3, round(G.zoom, 3))
    pe = G._cache.get(key)
    if pe is None:
        if len(G._cache) > 64:
            G._cache.clear()
        d = skia.DiscretePathEffect.Make(14 / G.zoom, 1.1 / G.zoom, G.frame // 3)
        c = skia.CornerPathEffect.Make(6 / G.zoom)
        pe = skia.PathEffect.MakeCompose(c, d)
        G._cache[key] = pe
    return pe


def big_enough(path, limit=70):
    b = path.computeTightBounds()
    return (b.width() + b.height()) / 2 * G.zoom >= limit


def P_fill(c, a=1.0, wobble=True):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    if wobble:
        p.setPathEffect(boil())
    return p


def P_ink(w=4.0, c=INK, a=1.0, wobble=True, cap=True):
    p = skia.Paint(AntiAlias=True, Color=col(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap,
                   StrokeJoin=skia.Paint.kRound_Join)
    if wobble:
        p.setPathEffect(boil())
    return p


def P_glow(c, sigma, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def shape(cv, path, fill, ow=4.0, a=1.0):
    wb = big_enough(path)
    cv.drawPath(path, P_fill(fill, a, wb))
    if ow > 0:
        cv.drawPath(path, P_ink(ow, INK, a, wb))


def circle(x, y, r):
    p = skia.Path()
    p.addCircle(x, y, r)
    return p


def poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def union(paths):
    out = paths[0]
    for q in paths[1:]:
        out = skia.Op(out, q, skia.PathOp.kUnion_PathOp)
    return out


def star5(x, y, r):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return poly(pts)


def sparkle4(x, y, r):
    pts = []
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * 0.18
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    return poly(pts)


def trim(path, p):
    pm = skia.PathMeasure(path, False)
    L = pm.getLength()
    out = skia.Path()
    if p > 0:
        pm.getSegment(0, L * clamp(p), out, True)
    return out


def text_w(tf, size, s, spacing=0.0):
    return skia.Font(tf, size).measureText(s) + spacing * max(0, len(s) - 1)


def draw_text(cv, s, x, y, tf, size, paint, spacing=0.0):
    f = skia.Font(tf, size)
    if spacing == 0:
        cv.drawTextBlob(skia.TextBlob.MakeFromString(s, f), x, y, paint)
        return
    for ch in s:
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, f), x, y, paint)
        x += f.measureText(ch) + spacing


# ---------------------------------------------------------------- Backgrounds
def make_night_bg(seed, stars=16, bands=True, w=W, h=H):
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    cv.clear(col(BG))
    rnd = random.Random(seed)
    if bands:
        for _ in range(6):
            x = rnd.uniform(-100, w)
            cv.drawRect(skia.Rect.MakeXYWH(x, 0, rnd.uniform(80, 280), h), P_fill(BG_BAND, rnd.uniform(.5, 1), False))
    # halftone fields (Rasterpunkte wie bei Rational Animations)
    for _ in range(5):
        x0, y0 = rnd.uniform(-50, w - 150), rnd.uniform(-50, h - 200)
        cols, rows = rnd.randint(6, 14), rnd.randint(10, 26)
        for gx in range(cols):
            for gy in range(rows):
                r = 3.0 * (1 - gy / rows) * (0.6 + 0.4 * math.sin(gx * 0.7 + seed))
                if r > 0.5:
                    cv.drawCircle(x0 + gx * 17, y0 + gy * 17, r, P_fill('#232524', 1, False))
    # diagonal dot trails
    for _ in range(8):
        x0, y0 = rnd.uniform(-200, w), rnd.uniform(0, h)
        n = rnd.randint(18, 60)
        ang = math.radians(rnd.choice([-38, -38, -52]))
        for k in range(n):
            cv.drawCircle(x0 + math.cos(ang) * k * 11, y0 + math.sin(ang) * k * 11, 1.9, P_fill(DOT, 1, False))
    for _ in range(stars):
        x, y = rnd.uniform(30, w - 30), rnd.uniform(25, h * 0.85)
        cv.drawPath(star5(x, y, rnd.uniform(5, 10)), P_fill(BONE_SH, rnd.uniform(.55, .9), False))
    for _ in range(stars // 2 + 2):
        x, y = rnd.uniform(30, w - 30), rnd.uniform(25, h * 0.85)
        cv.drawPath(sparkle4(x, y, rnd.uniform(4, 8)), P_fill(BONE, rnd.uniform(.5, .85), False))
    return surf.makeImageSnapshot()


def make_bark_bg(seed):
    surf = skia.Surface(W + 200, H + 200)
    cv = surf.getCanvas()
    cv.clear(col('#2b2723'))
    rnd = random.Random(seed)
    for i in range(70):
        x = rnd.uniform(-40, W + 240)
        p = skia.Path()
        p.moveTo(x, -20)
        amp, ph, fr = rnd.uniform(6, 22), rnd.uniform(0, 6.3), rnd.uniform(0.004, 0.01)
        for y in range(0, H + 240, 30):
            p.lineTo(x + math.sin(y * fr + ph) * amp, y)
        dark = rnd.random() < 0.6
        cv.drawPath(p, P_ink(rnd.uniform(3, 9) if dark else rnd.uniform(1.5, 3),
                             '#1c1916' if dark else '#3b352f', rnd.uniform(.6, 1), False))
    for _ in range(900):
        cv.drawCircle(rnd.uniform(0, W + 200), rnd.uniform(0, H + 200), rnd.uniform(.6, 1.6),
                      P_fill('#3e3832', rnd.uniform(.3, .8), False))
    return surf.makeImageSnapshot()


# ---------------------------------------------------------------- Tree (world units, s = scale)
CROWN_CIRCLES = [(0, -560, 200), (-190, -480, 150), (190, -480, 150), (-120, -690, 150), (120, -690, 150),
                 (0, -800, 135), (-290, -405, 95), (290, -405, 95), (-265, -610, 110), (265, -610, 110)]
APPLES = [(-232, -432, 'soot'), (204, -452, 'chrome'), (-118, -548, 'earth'), (112, -612, 'tube'),
          (-262, -652, 'pixel'), (258, -650, 'soot'), (-58, -712, 'chrome'), (156, -768, 'earth'),
          (-170, -802, 'tube'), (58, -500, 'pixel')]
GOLD_POS = (0, -888)


def trunk_path(s):
    p = skia.Path()
    p.moveTo(-150 * s, 6 * s)
    p.cubicTo(-90 * s, -6 * s, -60 * s, -40 * s, -52 * s, -110 * s)
    p.cubicTo(-46 * s, -220 * s, -58 * s, -330 * s, -40 * s, -430 * s)
    p.lineTo(40 * s, -430 * s)
    p.cubicTo(56 * s, -330 * s, 44 * s, -220 * s, 52 * s, -110 * s)
    p.cubicTo(60 * s, -40 * s, 92 * s, -6 * s, 150 * s, 6 * s)
    p.cubicTo(60 * s, 14 * s, -60 * s, 14 * s, -150 * s, 6 * s)
    p.close()
    return p


def draw_trunk(cv, s):
    tp = trunk_path(s)
    for (a, b, c2) in [((-20, -380), (-120, -440), (-200, -470)), ((24, -390), (120, -430), (190, -470)),
                       ((0, -420), (-6, -500), (10, -580))]:
        br = skia.Path()
        br.moveTo(a[0] * s, a[1] * s)
        br.quadTo(b[0] * s, b[1] * s, c2[0] * s, c2[1] * s)
        cv.drawPath(br, P_ink(34 * s, INK))
        cv.drawPath(br, P_ink(26 * s, TRUNK))
    shape(cv, tp, TRUNK, 4)
    cv.save()
    cv.clipPath(tp, doAntiAlias=True)
    rnd = random.Random(7)
    for i in range(7):
        x = rnd.uniform(-38, 38) * s
        q = skia.Path()
        q.moveTo(x, -30 * s)
        q.cubicTo(x + 10 * s, -150 * s, x - 12 * s, -260 * s, x + 4 * s, -420 * s)
        cv.drawPath(trim(q, rnd.uniform(.3, .8)), P_ink(3 * s, TRUNK_DK))
    q = skia.Path()
    q.moveTo(-42 * s, -60 * s)
    q.cubicTo(-38 * s, -200 * s, -48 * s, -300 * s, -34 * s, -420 * s)
    cv.drawPath(q, P_ink(3 * s, BONE, .18))
    cv.restore()


def crown_path(s):
    return union([circle(x * s, y * s, r * s) for (x, y, r) in CROWN_CIRCLES])


def draw_crown(cv, s, dim=0.0):
    cp = crown_path(s)
    shape(cv, cp, CROWN, 4)
    cv.save()
    cv.clipPath(cp, doAntiAlias=True)
    for (x, y, r) in CROWN_CIRCLES:
        cv.drawCircle((x + r * .25) * s, (y + r * .3) * s, r * .8 * s, P_fill(CROWN_DK, .85))
    for (x, y, r) in CROWN_CIRCLES:
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH((x - r * .82) * s, (y - r * .82) * s, r * 1.64 * s, r * 1.64 * s), 190, 70)
        cv.drawPath(a, P_ink(5 * s, CROWN_LT, .9))
    if dim > 0:
        cv.drawPaint(skia.Paint(Color=col(BG, dim * .6)))
    cv.restore()


# ---------------------------------------------------------------- Apple
APPLE_COL = {'red': (RED, '#c06a55'), 'soot': ('#4a4a47', '#6d6d68'), 'chrome': ('#aeb2ad', '#eef0ea'),
             'earth': ('#6a4a35', '#8f6a4d'), 'tube': ('#5b7a57', '#86a47f'), 'pixel': ('#4b6278', '#7290ab'),
             'gold': (GOLD, GOLD_HI)}


def apple_path(r):
    p = skia.Path()
    p.moveTo(0, -r * .62)
    p.cubicTo(r * .45, -r * 1.02, r * 1.08, -r * .78, r * 1.0, -r * .05)
    p.cubicTo(r * .95, r * .62, r * .52, r * 1.02, r * .16, r * .9)
    p.cubicTo(r * .05, r * .86, -r * .05, r * .86, -r * .16, r * .9)
    p.cubicTo(-r * .52, r * 1.02, -r * .95, r * .62, -r * 1.0, -r * .05)
    p.cubicTo(-r * 1.08, -r * .78, -r * .45, -r * 1.02, 0, -r * .62)
    p.close()
    return p


def draw_apple(cv, x, y, r, kind, glow=0.0, bite=0.0, alpha=1.0, t=0.0, ow=None, circuit=0.0):
    base, hi = APPLE_COL[kind]
    ow = ow if ow is not None else max(2.0, r * .11)
    wb = r * G.zoom > 40
    cv.save()
    cv.translate(x, y)
    if glow > 0:
        gc = GOLD_HI if kind == 'gold' else hi
        cv.drawCircle(0, 0, r * (1.5 + .5 * glow), P_glow(gc, r * .7, .35 * glow * alpha))
        cv.drawCircle(0, 0, r * 1.05, P_glow(gc, r * .25, .45 * glow * alpha))
    # Stiel und Blatt
    st = skia.Path()
    st.moveTo(0, -r * .6)
    st.quadTo(r * .05, -r * 1.0, r * .2, -r * 1.25)
    cv.drawPath(st, P_ink(ow * 1.1, INK, alpha, wb))
    lf = skia.Path()
    lf.moveTo(r * .08, -r * .95)
    lf.cubicTo(r * .3, -r * 1.35, r * .75, -r * 1.25, r * .82, -r * 1.12)
    lf.cubicTo(r * .6, -r * .9, r * .3, -r * .88, r * .08, -r * .95)
    lf.close()
    cv.drawPath(lf, P_fill(LEAF if kind != 'gold' else GOLD_DK, alpha, wb))
    cv.drawPath(lf, P_ink(ow * .8, INK, alpha, wb))
    body = apple_path(r)
    cv.drawPath(body, P_fill(base, alpha, wb))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    cv.drawCircle(r * .35, r * .45, r * .85, P_fill(INK, .22 * alpha, False))
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(-r * .7, -r * .55, r * .9, r * 1.1), 160, 70)
    cv.drawPath(hl, P_ink(r * .14, hi, .85 * alpha, wb))
    if kind == 'pixel':
        rnd = random.Random(3)
        for _ in range(9):
            px, py = rnd.uniform(-.7, .6) * r, rnd.uniform(-.4, .7) * r
            cv.drawRect(skia.Rect.MakeXYWH(px, py, r * .16, r * .16), P_fill(hi, .55 * alpha, False))
    if kind == 'soot':
        rnd = random.Random(5)
        for _ in range(12):
            cv.drawCircle(rnd.uniform(-.7, .7) * r, rnd.uniform(-.5, .8) * r, r * .05, P_fill('#2a2a28', alpha, False))
    if kind == 'chrome':
        cv.drawRect(skia.Rect.MakeXYWH(-r * .1, -r, r * .12, r * 2), P_fill('#ffffff', .5 * alpha, False))
    if kind == 'gold' and circuit > 0:
        draw_circuit(cv, r, t, circuit * alpha)
    if bite > 0:
        # Biss auf der Vorderseite (bewusst nicht als Kerbe in der Silhouette)
        b = eout(bite)
        bx, by = r * .18, -r * .02
        pts = []
        for i in range(73):
            a = i / 72 * 2 * math.pi
            tooth = .1 * abs(math.sin(a * 6))
            rx, ry = r * .5 * b * (1 - tooth), r * .58 * b * (1 - tooth)
            pts.append((bx + math.cos(a) * rx, by + math.sin(a) * ry))
        flesh = poly(pts)
        cv.drawPath(flesh, P_fill('#e8e0c6', alpha, wb))
        cv.save()
        cv.clipPath(flesh, doAntiAlias=True)
        cv.drawOval(skia.Rect.MakeXYWH(bx - r * .55 * b, by - r * .7 * b, r * 1.0 * b, r * .55 * b),
                    P_fill('#cbbf9c', .9 * alpha, False))
        cv.restore()
        cv.drawPath(flesh, P_ink(max(2, ow * .6), INK, alpha, wb))
        cv.drawLine(bx, by - r * .12 * b, bx + r * .02 * b, by + r * .18 * b, P_ink(max(1.5, r * .025), '#a8996f', alpha, False))
    cv.restore()
    cv.drawPath(body, P_ink(ow, INK, alpha, wb))
    cv.restore()


def circuit_paths(r):
    rnd = random.Random(11)
    out = []
    for i in range(9):
        x, y = rnd.uniform(-.75, .75) * r, rnd.uniform(-.55, .85) * r
        p = skia.Path()
        p.moveTo(x, y)
        pts = [(x, y)]
        for k in range(rnd.randint(2, 4)):
            if k % 2 == 0:
                x += rnd.choice([-1, 1]) * rnd.uniform(.15, .35) * r
            else:
                y += rnd.choice([-1, 1]) * rnd.uniform(.12, .3) * r
            p.lineTo(x, y)
            pts.append((x, y))
        out.append((p, pts))
    return out


_CIRCUIT_CACHE = {}


def draw_circuit(cv, r, t, a):
    key = round(r, 1)
    if key not in _CIRCUIT_CACHE:
        _CIRCUIT_CACHE[key] = circuit_paths(r)
    for i, (p, pts) in enumerate(_CIRCUIT_CACHE[key]):
        cv.drawPath(p, P_ink(max(1.2, r * .035), GOLD_DK, a, cap=True))
        for (px, py) in (pts[0], pts[-1]):
            cv.drawCircle(px, py, max(1.6, r * .045), P_fill(GOLD_DK, a))
        # Lichtpuls, der die Leiterbahn entlanglaeuft
        ph = (t * .7 + i * .37) % 1.0
        pm = skia.PathMeasure(p, False)
        L = pm.getLength()
        seg = skia.Path()
        pm.getSegment(L * ph, min(L, L * ph + r * .25), seg, True)
        cv.drawPath(seg, P_ink(max(1.6, r * .05), GOLD_HI, a * .95, wobble=False))


# ---------------------------------------------------------------- Snake
def snake_outline(pts, widths):
    left, right = [], []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[max(0, i - 1)][:2]
        x1, y1 = pts[min(n - 1, i + 1)][:2]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        w = widths[i] / 2
        left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    return left, right


def draw_snake_run(cv, pts, widths, ow, front=True):
    if len(pts) < 2:
        return
    left, right = snake_outline(pts, widths)
    body = poly(left + right[::-1])
    cv.drawPath(body, P_fill(SNAKE if front else SNAKE_DK))
    if front:
        cv.save()
        cv.clipPath(body, doAntiAlias=True)
        n = len(pts)
        # dunkle Rueckenzeichnung
        acc = 0.0
        for i in range(1, n - 1):
            acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            w = widths[i]
            if acc > w * 0.9:
                acc = 0
                dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
                L = math.hypot(dx, dy) or 1
                dx, dy = dx / L, dy / L
                nx, ny = -dy, dx
                cx, cy = pts[i][:2]
                v = poly([(cx - dx * w * .2 + nx * w * .3, cy - dy * w * .2 + ny * w * .3),
                          (cx + dx * w * .14, cy + dy * w * .14),
                          (cx - dx * w * .2 - nx * w * .3, cy - dy * w * .2 - ny * w * .3)], close=False)
                cv.drawPath(v, P_ink(max(1.5, w * .09), SNAKE_DK))
        hl = [(pts[i][0] + (left[i][0] - pts[i][0]) * .62, pts[i][1] + (left[i][1] - pts[i][1]) * .62) for i in range(n)]
        cv.drawPath(poly(hl, close=False), P_ink(max(1.2, widths[n // 2] * .08), SNAKE_LT, .7))
        cv.restore()
    cv.drawPath(poly(left, close=False), P_ink(ow, INK))
    cv.drawPath(poly(right, close=False), P_ink(ow, INK))


def snake_widths(n, wmax, neck=0.78):
    out = []
    for i in range(n):
        u = i / max(1, n - 1)
        if u < .55:
            f = .12 + .88 * math.sin(u / .55 * math.pi / 2)
        else:
            f = lerp(1.0, neck, (u - .55) / .45)
        out.append(wmax * f)
    return out


def head_path(w, closed=True):
    L, D = 1.75 * w, 1.05 * w
    p = skia.Path()
    p.moveTo(-w * .35, -w * .39)
    p.cubicTo(L * .2, -D * .5, L * .5, -D * .62, L * .78, -D * .42)
    p.cubicTo(L * .93, -D * .3, L * 1.02, -w * .14, L, -w * .02)
    p.cubicTo(L * .98, w * .14, L * .85, D * .44, L * .42, D * .5)
    p.cubicTo(L * .16, D * .5, 0, w * .42, -w * .35, w * .39)
    if closed:
        p.close()
    return p


def draw_head(cv, x, y, ang, w, lid=0.0, tongue=0.0, gold_rim=0.0, pupil=1.0, flip=False):
    """Kopf mit Hals bei (x,y), Schnauze in Richtung ang (Grad)."""
    L, D = 1.75 * w, 1.05 * w
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    if flip:
        cv.scale(1, -1)
    if tongue > 0:
        tl = w * 1.1 * math.sin(math.pi * clamp(tongue))
        tg = skia.Path()
        tg.moveTo(L * .95, w * .02)
        tg.lineTo(L + tl, w * .02)
        tg.moveTo(L + tl, w * .02)
        tg.lineTo(L + tl + w * .22, -w * .12)
        tg.moveTo(L + tl, w * .02)
        tg.lineTo(L + tl + w * .22, w * .16)
        cv.drawPath(tg, P_ink(w * .11, INK))
        cv.drawPath(tg, P_ink(w * .06, '#b5523f'))
    hp = head_path(w)
    cv.drawPath(hp, P_fill(SNAKE))
    cv.save()
    cv.clipPath(hp, doAntiAlias=True)
    cv.drawOval(skia.Rect.MakeXYWH(L * .05, D * .1, L * 1.0, D * .7), P_fill(SNAKE_DK, .55))
    for k in range(3):
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(L * (.12 + k * .2), -D * .42, w * .32, w * .3), 200, 140)
        cv.drawPath(a, P_ink(w * .045, SNAKE_DK))
    if gold_rim > 0:
        cv.drawCircle(L * 1.3, -D * .2, L * .9, P_glow(GOLD_HI, w * .4, .45 * gold_rim))
    cv.restore()
    cv.drawPath(head_path(w, closed=False), P_ink(max(2.5, w * .07)))
    # Mund (leichtes Schmunzeln), Nasenloch, Brauenwulst
    m = skia.Path()
    m.moveTo(L * .97, w * .1)
    m.cubicTo(L * .8, w * .2, L * .62, w * .24, L * .46, D * .2)
    m.quadTo(L * .4, D * .17, L * .37, D * .1)
    cv.drawPath(m, P_ink(max(1.5, w * .045)))
    cv.drawCircle(L * .9, -w * .14, w * .04, P_fill(INK))
    ex, ey, er = L * .56, -D * .2, w * .17
    cv.drawCircle(ex, ey, er * 1.5, P_glow(AMBER, er * .8, .35))
    eye = circle(ex, ey, er)
    cv.drawPath(eye, P_fill(AMBER))
    cv.save()
    cv.clipPath(eye, doAntiAlias=True)
    cv.drawCircle(ex + er * .3, ey + er * .35, er * .9, P_fill('#9a6420', .55))
    pw = er * .22 * pupil
    cv.drawOval(skia.Rect.MakeXYWH(ex - pw, ey - er * .85, pw * 2, er * 1.7), P_fill(INK))
    cv.drawCircle(ex - er * .38, ey - er * .38, er * .16, P_fill('#fff6dc'))
    if lid > 0:
        ld = skia.Path()
        ld.addRect(skia.Rect.MakeXYWH(ex - er * 1.4, ey - er * 1.4, er * 2.8, er * 2.8 * clamp(lid) * .5 + er * .02))
        cv.drawPath(ld, P_fill(SNAKE))
        cv.drawLine(ex - er * 1.2, ey - er * 1.4 + er * 2.8 * clamp(lid) * .5, ex + er * 1.2,
                    ey - er * 1.4 + er * 2.8 * clamp(lid) * .5, P_ink(max(1.5, w * .05)))
    cv.restore()
    cv.drawPath(eye, P_ink(max(1.8, w * .05)))
    br = skia.Path()
    br.moveTo(ex - er * 1.4, ey - er * 1.25)
    br.quadTo(ex - er * .1, ey - er * 1.6, ex + er * 1.5, ey - er * .55)
    cv.drawPath(br, P_ink(max(2, w * .09)))
    cv.restore()


def coil_points(tx, y_bot, y_top, R, turns, phase_end, n, head_pt=None, neck_frac=0.0):
    """Punkte (x, y, depth) vom Schwanz (unten) nach oben um einen Stamm."""
    pts = []
    n_coil = int(n * (1 - neck_frac))
    ph0 = phase_end - 2 * math.pi * turns
    for i in range(n_coil):
        u = i / max(1, n_coil - 1)
        ph = ph0 + 2 * math.pi * turns * u
        pts.append((tx + R * math.sin(ph), lerp(y_bot, y_top, u) + 18 * math.cos(ph) * (R / 60), math.cos(ph)))
    if head_pt is not None and neck_frac > 0:
        x0, y0, _ = pts[-1]
        hx, hy = head_pt
        cx, cy = x0 + (hx - x0) * .2, y0 - abs(hy - y0) * .9 - 40
        for i in range(1, n - n_coil + 1):
            u = i / (n - n_coil)
            bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * hx
            by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * hy
            pts.append((bx, by, 1.0))
    return pts


def split_runs(pts, widths):
    runs, cur, curw, front = [], [], [], None
    for p, w in zip(pts, widths):
        f = p[2] >= 0
        if front is None or f == front:
            cur.append(p)
            curw.append(w)
        else:
            cur.append(p)
            curw.append(w)
            runs.append((front, cur, curw))
            cur, curw = [p], [w]
        front = f
    if cur:
        runs.append((front, cur, curw))
    return runs


def draw_snake_on_trunk(cv, pts, widths, ow, trunk_fn, head=None):
    runs = split_runs(pts, widths)
    for front, rp, rw in runs:
        if not front:
            draw_snake_run(cv, rp, rw, ow, front=False)
    trunk_fn()
    for front, rp, rw in runs:
        if front:
            draw_snake_run(cv, rp, rw, ow, front=True)
    if head:
        draw_head(cv, **head)


def head_angle(pts):
    (x0, y0), (x1, y1) = pts[-3][:2], pts[-1][:2]
    return math.degrees(math.atan2(y1 - y0, x1 - x0))


# ---------------------------------------------------------------- Figures
def stroke_figure(cv, strokes, ow=4.0, fill=BONE, a=1.0):
    """strokes: [(path, width)] - erst Tusche breiter, dann Fuellung: verschmolzene Silhouette."""
    for p, w in strokes:
        cv.drawPath(p, P_ink(w + ow * 2, INK, a))
    for p, w in strokes:
        cv.drawPath(p, P_ink(w, fill, a))


def seg(a, b):
    p = skia.Path()
    p.moveTo(*a)
    p.lineTo(*b)
    return p


def bez(a, c1, c2, b):
    p = skia.Path()
    p.moveTo(*a)
    p.cubicTo(*c1, *c2, *b)
    return p


def merged(cv, parts, ow=4.5, fill=BONE, a=1.0):
    """parts: [('s', path, width) | ('f', path)] - verschmolzene Silhouette mit Aussenkontur."""
    for kind, p, *w in parts:
        if kind == 's':
            cv.drawPath(p, P_ink(w[0] + ow * 2, INK, a))
        else:
            cv.drawPath(p, P_fill(INK, a))
            cv.drawPath(p, P_ink(ow * 2, INK, a))
    for kind, p, *w in parts:
        if kind == 's':
            cv.drawPath(p, P_ink(w[0], fill, a))
        else:
            cv.drawPath(p, P_fill(fill, a))


def draw_hand_open(cv, x, y, s, curl=0.0, a=1.0):
    """Hohle Hand von der Seite, Handflaeche nach oben, Unterarm von links unten."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    palm = skia.Path()
    palm.addOval(skia.Rect.MakeXYWH(-60, -38, 170, 76))
    c = curl
    parts = [('s', seg((-330, 190), (-30, 10)), 92),
             ('f', palm),
             ('s', bez((90, -4), (150, -6), (200, -14 - 10 * c), (226, -44 - 18 * c)), 30),
             ('s', bez((90, 16), (160, 16), (215, 6 - 8 * c), (246, -18 - 20 * c)), 27),
             ('s', bez((-6, -26), (20, -64), (52, -84 - 8 * c), (92, -86 - 10 * c)), 30)]
    merged(cv, parts, 4.5, BONE, a)
    cv.drawPath(bez((-200, 128), (-150, 100), (-90, 70), (-40, 50)), P_ink(4, BONE_SH, .8 * a))
    cv.drawPath(bez((10, 22), (50, 30), (90, 28), (120, 20)), P_ink(3.5, BONE_SH, a))
    cv.drawPath(bez((120, 2), (150, 4), (175, 2), (195, -6)), P_ink(3, BONE_SH, a))
    cv.restore()


def draw_reach_hand(cv, x, y, s, grip=0.0, a=1.0, apple=None):
    """Hand von rechts, greift nach links. apple = Funktion, die den Apfel zwischen Handflaeche und Fingern malt."""
    g = clamp(grip)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    palm = skia.Path()
    palm.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-60, -46, 130, 96), 44, 44))
    back = [('s', seg((520, 170), (40, 4)), 90), ('f', palm)]
    thumb = [('s', bez((-10, 34), (-50, 70), (-100, 86), (-140 + 30 * g, 82 - 10 * g)), 30)]
    fingers = [('s', bez((-40, -30), (-100, -44), (-150, -40 + 6 * g), (-196 + 40 * g, -22 + 44 * g)), 28),
               ('s', bez((-44, -8), (-110, -14), (-160, -6 + 8 * g), (-204 + 40 * g, 14 + 40 * g)), 27),
               ('s', bez((-40, 14), (-104, 16), (-150, 26 + 6 * g), (-188 + 36 * g, 44 + 30 * g)), 25)]
    merged(cv, back + thumb, 4.5, BONE, a)
    if apple:
        cv.save()
        apple()
        cv.restore()
    merged(cv, fingers, 4.5, BONE, a)
    cv.drawPath(bez((-30, -24), (-20, -10), (-20, 8), (-28, 22)), P_ink(3, BONE_SH, a))
    cv.restore()


def draw_worker(cv, x, y, s, t, a=1.0):
    """Gebeugte Figur mit Hacke, Profil nach rechts."""
    sw = math.sin(t * 2 * math.pi * 1.1)
    lift = max(0, sw)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    hip = (-10, -95)
    sh = (38, -158 + 6 * lift)
    head = (70, -170 + 8 * lift)
    hands = (85 + 12 * lift, -112 - 40 * lift)
    ang = math.radians(60 - 55 * lift)
    hx0, hy0 = hands[0] - math.cos(ang) * 70, hands[1] - math.sin(ang) * 70
    hx1, hy1 = hands[0] + math.cos(ang) * 110, hands[1] + math.sin(ang) * 110
    tool = [(seg((hx0, hy0), (hx1, hy1)), 9)]
    blade = poly([(hx1, hy1), (hx1 + math.cos(ang + 1.9) * 40, hy1 + math.sin(ang + 1.9) * 40),
                  (hx1 + math.cos(ang + 1.6) * 46, hy1 + math.sin(ang + 1.6) * 46)])
    body = [(seg(hip, (-30, 0)), 30), (seg(hip, (20, -2)), 30), (bez(hip, (0, -140), (20, -160), sh), 44),
            (seg(sh, hands), 22), (seg((sh[0] - 6, sh[1] + 6), (hands[0] - 10, hands[1] + 8)), 20)]
    for p, w in tool:
        cv.drawPath(p, P_ink(w + 6, INK, a))
        cv.drawPath(p, P_ink(w, '#6a5a48', a))
    shape(cv, blade, '#7d7c74', 3, a)
    stroke_figure(cv, body, 4, BONE, a)
    hc = circle(head[0], head[1], 26)
    shape(cv, hc, BONE, 4, a)
    cv.save()
    cv.clipPath(hc, doAntiAlias=True)
    cv.drawCircle(head[0] - 14, head[1] - 16, 26, P_fill('#5a524a', a, False))
    cv.restore()
    cv.drawPath(hc, P_ink(4, INK, a, False))
    # Schweisstropfen
    ph = (t * 1.1) % 1.0
    dy = ein(ph) * 150
    da = 1 - prog(ph, .7, 1)
    drop = skia.Path()
    dx0, dy0 = head[0] + 30, head[1] - 10 + dy
    drop.moveTo(dx0, dy0 - 14)
    drop.cubicTo(dx0 + 9, dy0 - 2, dx0 + 8, dy0 + 6, dx0, dy0 + 6)
    drop.cubicTo(dx0 - 8, dy0 + 6, dx0 - 9, dy0 - 2, dx0, dy0 - 14)
    shape(cv, drop, BONE_HI, 2.5, a * da)
    cv.restore()


def draw_resting_pair(cv, x, y, s, a=1.0):
    """Zwei Figuren liegen im Gras, Koepfe zueinander, Arme hinter dem Kopf."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    for sx in (-1, 1):
        cv.save()
        cv.scale(sx, 1)
        parts = [('s', seg((14, -4), (62, -2)), 15), ('s', seg((62, -2), (104, 2)), 11),
                 ('s', bez((18, -8), (10, -22), (2, -24), (-4, -18)), 6)]
        merged(cv, parts, 2.2, BONE, a)
        head = circle(4, -8, 9)
        cv.drawPath(head, P_fill(BONE, a, False))
        cv.drawPath(head, P_ink(2.2, INK, a, False))
        cv.restore()
    cv.restore()


# ---------------------------------------------------------------- Eden (paper layers)
def hill_path(y_top, amp, freq, phase, bump=None, x0=-900, x1=W + 900, base=H + 200):
    p = skia.Path()
    p.moveTo(x0, base)
    for x in range(int(x0), int(x1) + 1, 20):
        y = y_top + amp * math.sin(x * freq + phase) + amp * .4 * math.sin(x * freq * 2.3 + phase * 1.7)
        if bump:
            bx, bh, bw = bump
            y -= bh * math.exp(-((x - bx) / bw) ** 2)
        p.lineTo(x, y)
    p.lineTo(x1, base)
    p.close()
    return p


def popup(cv, base_y, s):
    cv.translate(0, base_y)
    cv.scale(1, max(0.001, s))
    cv.translate(0, -base_y)


def draw_bush_row(cv, y, seed, colr, fruit=True, t=0.0, grow=1.0):
    rnd = random.Random(seed)
    blobs = []
    x = -100
    while x < W + 100:
        r = rnd.uniform(50, 95)
        blobs.append((x, y - r * .4 + rnd.uniform(-10, 10), r))
        x += r * 1.2
    path = union([circle(bx, by, br * grow) for bx, by, br in blobs])
    shape(cv, path, colr, 4)
    cv.save()
    cv.clipPath(path, doAntiAlias=True)
    for bx, by, br in blobs:
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(bx - br * .8, by - br * .8, br * 1.6, br * 1.6), 200, 60)
        cv.drawPath(a, P_ink(5, mix(colr, BONE, .25), .8))
    cv.restore()
    if fruit:
        for bx, by, br in blobs[::2]:
            for k in range(2):
                fx, fy = bx + rnd.uniform(-.5, .5) * br, by + rnd.uniform(-.5, .2) * br
                shape(cv, circle(fx, fy, 9 * grow), RED, 2.5)


def draw_eden(cv, t, pops, fold=None, barren=0.0, figures=1.0):
    """pops: dict layer->scale 0..1; fold: dict layer->scale (Zusammenklappen)."""
    def S(name):
        v = pops.get(name, 1.0)
        if fold and name in fold:
            v *= fold[name]
        return v
    sky = skia.Paint(AntiAlias=True)
    sky.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 760)],
                                                 [col('#171818'), col(mix('#2b2924', '#1c1b1a', barren))]))
    cv.drawPaint(sky)
    # Mond
    ma = pops.get('moon', 1.0) * (1 - .6 * barren)
    cv.drawCircle(1480, 240, 150, P_glow('#d8d2bc', 60, .18 * ma))
    shape(cv, circle(1480, 240, 64), '#cfc9b3', 3.5, ma)
    cv.drawCircle(1500, 228, 14, P_fill('#b8b29c', ma))
    cv.drawCircle(1462, 262, 9, P_fill('#b8b29c', ma))
    # ferner Huegel mit Baum
    s = S('far')
    if s > 0.002:
        cv.save()
        popup(cv, H + 200, s)
        hp = hill_path(690, 14, .004, .5, bump=(960, 90, 380))
        shape(cv, hp, mix('#3b3d35', '#2a2723', barren), 4)
        cv.save()
        cv.translate(960, 612)
        draw_trunk(cv, .42)
        draw_crown(cv, .42)
        draw_apple(cv, -40 * .42 * 2.2, -460 * .42, 13, 'red', glow=.6 * (1 - barren))
        cv.restore()
        if figures > 0:
            draw_resting_pair(cv, 1100, 640, 1.4, figures)
        cv.restore()
    s = S('mid')
    if s > 0.002:
        cv.save()
        popup(cv, H + 200, s)
        shape(cv, hill_path(800, 22, .0035, 2.0), mix('#4a4c40', '#3a332d', barren), 4)
        cv.restore()
    s = S('bush')
    if s > 0.002:
        cv.save()
        popup(cv, H + 200, s)
        draw_bush_row(cv, 905, 4, '#55654f', fruit=True)
        cv.restore()
    s = S('front')
    if s > 0.002:
        cv.save()
        popup(cv, H + 200, s)
        fp = hill_path(985, 12, .006, 1.0)
        shape(cv, fp, '#2f312a', 4)
        rnd = random.Random(9)
        for _ in range(80):
            gx = rnd.uniform(0, W)
            gy = 985 + 12 * math.sin(gx * .006 + 1.0) + 6
            bl = skia.Path()
            bl.moveTo(gx, gy + 4)
            sway = 6 * math.sin(t * 1.5 + gx * .01)
            bl.quadTo(gx + sway * .5, gy - 20, gx + sway, gy - rnd.uniform(26, 48))
            cv.drawPath(bl, P_ink(7, INK))
            cv.drawPath(bl, P_ink(3.5, '#4d5a48'))
        for _ in range(16):
            fx = rnd.uniform(40, W - 40)
            fy = 985 + 12 * math.sin(fx * .006 + 1.0) - rnd.uniform(18, 36)
            for k in range(5):
                a = k * 2 * math.pi / 5
                cv.drawCircle(fx + math.cos(a) * 6, fy + math.sin(a) * 6, 4.5, P_fill(BONE_HI))
            cv.drawCircle(fx, fy, 3.5, P_fill(GOLD))
        cv.restore()
    if barren > 0:
        cv.save()
        bp = hill_path(870, 16, .003, 3.0)
        shape(cv, bp, '#3a302a', 4, barren)
        rnd = random.Random(21)
        for _ in range(40):
            sx, sy = rnd.uniform(-700, W + 500), rnd.uniform(900, 1060)
            rr = rnd.uniform(6, 18)
            shape(cv, skia.Path().addOval(skia.Rect.MakeXYWH(sx - rr, sy - rr * .6, rr * 2, rr * 1.2)), '#5b5650', 2.5,
                  barren)
        for k in range(7):
            fy = 920 + k * 22
            cv.drawLine(-900, fy, W + 900, fy + 18, P_ink(2.5, '#2a231e', barren))
        cv.restore()


# ---------------------------------------------------------------- Icons (No fields / rent / alarm)
def icon_bubble(cv, x, y, r, kind, a, strike):
    shape(cv, circle(x, y, r), '#232524', 4, a)
    p = P_ink(6, BONE, a)
    if kind == 'plough':
        cv.drawLine(x - 50, y - 40, x + 10, y + 20, p)
        cv.drawLine(x - 62, y - 30, x - 38, y - 52, p)
        blade = poly([(x + 4, y + 10), (x + 52, y + 18), (x + 20, y + 42)])
        cv.drawPath(blade, P_ink(6, BONE, a))
        cv.drawLine(x - 60, y + 46, x + 60, y + 46, P_ink(4, BONE_SH, a))
    elif kind == 'rent':
        house = poly([(x - 46, y - 2), (x, y - 46), (x + 46, y - 2), (x + 34, y - 2), (x + 34, y + 42),
                      (x - 34, y + 42), (x - 34, y - 2)])
        cv.drawPath(house, p)
        cv.drawCircle(x, y + 16, 15, P_ink(5, GOLD, a))
        draw_text(cv, '$', x - 7, y + 24, TF_SUB, 24, P_fill(GOLD, a, False))
    elif kind == 'clock':
        cv.drawCircle(x, y + 6, 40, p)
        cv.drawLine(x, y + 6, x, y - 18, p)
        cv.drawLine(x, y + 6, x + 18, y + 14, p)
        for sx in (-1, 1):
            b = skia.Path()
            b.addArc(skia.Rect.MakeXYWH(x + sx * 34 - 18, y - 48, 36, 36), 180 if sx < 0 else 270, 90)
            cv.drawPath(b, P_ink(7, BONE, a))
            cv.drawLine(x + sx * 24, y + 40, x + sx * 34, y + 54, p)
    if strike > 0:
        sp = trim(seg((x - r * .72, y + r * .72), (x + r * .72, y - r * .72)), eout(strike))
        cv.drawPath(sp, P_ink(14, INK, a))
        cv.drawPath(sp, P_ink(8, RED, a))


# ---------------------------------------------------------------- Scenes
BG_NIGHT = None
BG_NIGHT2 = None
BG_BARK = None


def init_assets():
    global BG_NIGHT, BG_NIGHT2, BG_BARK
    BG_NIGHT = make_night_bg(3, stars=18)
    BG_NIGHT2 = make_night_bg(8, stars=10)
    BG_BARK = make_bark_bg(5)


def cam(cv, cx, cy, z):
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-cx, -cy)
    G.zoom = z


def scene_garden(cv, t):
    """00-01  In the beginning, there was no work.  (0-5 s)"""
    pops = {'moon': eout(prog(t, .3, 1.4)), 'far': eback(prog(t, .5, 1.5)), 'mid': eback(prog(t, .9, 1.9)),
            'bush': eback(prog(t, 1.3, 2.3)), 'front': eback(prog(t, 1.7, 2.7))}
    cv.drawImage(BG_NIGHT, 0, 0)
    cv.save()
    z = lerp(1.0, 1.07, eio(t / 5))
    cam(cv, 960, 600, z)
    draw_eden(cv, t, pops)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(t, 0, .8)))))


def scene_hand(cv, t):
    """00-02  No fields ... simply grew  (5-12 s), t lokal 0-7"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 560, lerp(1.0, 1.05, t / 7))
    # unscharfer Garten im Hintergrund
    cv.save()
    cv.translate(-200, 120)
    cv.scale(1.25, 1.25)
    draw_eden(cv, t + 5, {}, figures=0)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col(BG, .45)))
    # wachsende Pflanzen
    gp = prog(t, 4.4, 6.4)
    rnd = random.Random(31)
    for k in range(7):
        bx = 980 + k * 120 + rnd.uniform(-30, 30)
        by = 1080
        hh = rnd.uniform(220, 380)
        stem = bez((bx, by), (bx - 30, by - hh * .4), (bx + 40, by - hh * .7), (bx + 10, by - hh))
        part = trim(stem, eout(clamp(gp * 1.4 - k * .08)))
        cv.drawPath(part, P_ink(12, INK))
        cv.drawPath(part, P_ink(6, '#5f7457'))
        pm = skia.PathMeasure(stem, False)
        for j in range(4):
            lp = clamp(gp * 1.6 - k * .08 - j * .15)
            if lp <= 0:
                continue
            pos, tan = pm.getPosTan(pm.getLength() * (.3 + j * .2))
            side = 1 if j % 2 else -1
            lf = skia.Path()
            ls = 38 * eback(lp)
            lf.moveTo(pos.x(), pos.y())
            lf.cubicTo(pos.x() + side * ls * .6, pos.y() - ls * .7, pos.x() + side * ls * 1.4, pos.y() - ls * .5,
                       pos.x() + side * ls * 1.6, pos.y() - ls * .1)
            lf.cubicTo(pos.x() + side * ls * 1.0, pos.y() + ls * .2, pos.x() + side * ls * .3, pos.y() + ls * .1,
                       pos.x(), pos.y())
            shape(cv, lf, LEAF, 3)
        fp = eback(clamp(gp * 1.5 - k * .1 - .3))
        if fp > 0:
            end = pm.getPosTan(pm.getLength())[0]
            shape(cv, circle(end.x(), end.y(), 16 * fp), RED, 3)
    # Ast mit Fruechten oben links
    branch = bez((-40, 120), (200, 170), (420, 150), (640, 210))
    cv.drawPath(branch, P_ink(40, INK))
    cv.drawPath(branch, P_ink(30, TRUNK))
    for (fx, fy) in [(240, 205), (380, 212)]:
        cv.drawLine(fx, fy - 40, fx, fy - 18, P_ink(4, INK, 1, False))
        draw_apple(cv, fx, fy, 24, 'red')
    # fallende Frucht
    fall = prog(t, 5.0, 5.9)
    fx, fy0, fy1 = 521, 252, 680
    if fall <= 0:
        fy = fy0
    elif fall < 1:
        fy = lerp(fy0, fy1, ein(fall))
    else:
        fy = fy1 - 26 * abs(math.sin((t - 5.9) * 9)) * math.exp(-(t - 5.9) * 5)
    cv.drawLine(521, 172, 521, 222, P_ink(4, INK, 1 - eout(prog(t, 5.0, 5.2)), False))
    draw_apple(cv, fx, fy, 30, 'red', glow=.3)
    # Hand
    curl = .2 + .8 * eout(prog(t, 5.9, 6.4))
    draw_hand_open(cv, 430, 760, 1.3, curl=curl)
    cv.restore()
    # Icons: No fields to plough / No rent to pay / No alarm clock
    for (kind, t0, t1, x) in [('plough', .2, 2.0, 1180), ('rent', 2.0, 3.6, 1420), ('clock', 3.6, 4.6, 1660)]:
        a = eout(prog(t, t0, t0 + .35)) * (1 - prog(t, 4.6, 5.2))
        if a <= 0:
            continue
        sc = eback(prog(t, t0, t0 + .45))
        cv.save()
        cv.translate(x, 300)
        cv.scale(sc, sc)
        icon_bubble(cv, 0, 0, 92, kind, a, prog(t, t0 + .5, t0 + .9))
        cv.restore()


def trunk_close_path():
    p = skia.Path()
    p.moveTo(820, -60)
    p.cubicTo(800, 300, 830, 700, 790, 1140)
    p.lineTo(1130, 1140)
    p.cubicTo(1090, 700, 1120, 300, 1100, -60)
    p.close()
    return p


def draw_trunk_close(cv):
    tp = trunk_close_path()
    shape(cv, tp, TRUNK, 5)
    cv.save()
    cv.clipPath(tp, doAntiAlias=True)
    rnd = random.Random(4)
    for i in range(16):
        x = rnd.uniform(830, 1090)
        q = bez((x, -60), (x + rnd.uniform(-30, 30), 300), (x + rnd.uniform(-30, 30), 700), (x, 1140))
        cv.drawPath(trim(q, rnd.uniform(.3, 1)), P_ink(rnd.uniform(3, 7), TRUNK_DK))
    cv.drawPath(bez((838, -60), (820, 300), (848, 700), (812, 1140)), P_ink(5, BONE, .16))
    cv.restore()


def scene_eye(cv, t):
    """00-03a  Auge oeffnet sich (12-13.6 s), t lokal 0-1.6"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    z = lerp(1.0, 1.08, t / 1.6)
    cam(cv, 960, 540, z)
    # Schuppen ringsum
    for row in range(-5, 6):
        for k in range(-9, 10):
            x = 960 + k * 120 + (60 if row % 2 else 0)
            y = 540 + row * 82
            if ((x - 960) / 560) ** 2 + ((y - 540) / 230) ** 2 < 1:
                continue
            sc = skia.Path()
            sc.addArc(skia.Rect.MakeXYWH(x - 62, y - 44, 124, 88), 20, 140)
            cv.drawPath(sc, P_ink(16, SNAKE_DK))
            cv.drawPath(sc, P_ink(5, INK, .7))
    op = eout(prog(t, .15, .95))
    hh = lerp(6, 230, op)
    alm = skia.Path()
    alm.moveTo(430, 540)
    alm.cubicTo(640, 540 - hh * 1.35, 1280, 540 - hh * 1.35, 1490, 540)
    alm.cubicTo(1280, 540 + hh * 1.35, 640, 540 + hh * 1.35, 430, 540)
    alm.close()
    cv.drawCircle(960, 540, 260, P_glow(AMBER, 90, .25 * op))
    cv.drawPath(alm, P_fill(AMBER))
    cv.save()
    cv.clipPath(alm, doAntiAlias=True)
    cv.drawCircle(960, 540, 300, P_fill('#c58a2c'))
    cv.drawCircle(960, 540, 215, P_fill(AMBER))
    for k in range(24):
        a = k * 2 * math.pi / 24
        cv.drawLine(960 + math.cos(a) * 60, 540 + math.sin(a) * 60, 960 + math.cos(a) * 210,
                    540 + math.sin(a) * 210, P_ink(4, '#b57b25', .6))
    pw = lerp(46, 26, op)
    cv.drawOval(skia.Rect.MakeXYWH(960 - pw, 540 - 250, pw * 2, 500), P_fill(INK))
    cv.drawCircle(890, 470, 26, P_fill('#fff3d6', op))
    cv.drawCircle(1030, 610, 10, P_fill('#fff3d6', .6 * op))
    cv.restore()
    cv.drawPath(alm, P_ink(12, INK))
    for sx in (-1, 1):
        sp = poly([(960 + sx * 530, 540), (960 + sx * 610, 520), (960 + sx * 590, 548)])
        shape(cv, sp, INK, 4)
    cv.restore()


def scene_offer(cv, t):
    """00-03b  Schlange gleitet herab, bietet Apfel an (13.6-16 s), t lokal 0-2.4"""
    cv.drawImage(BG_NIGHT, 0, 0)
    cv.save()
    cam(cv, 960, 540, 1.0)
    br = bez((1080, 478), (1200, 470), (1320, 488), (1440, 462))
    slide = eout(prog(t, 0, 1.6))
    n = 120
    s_head = lerp(.3, 1.0, slide)
    turns = 1.5
    pts = []
    for i in range(n):
        u = s_head - 1.25 * (1 - i / (n - 1))
        ph = 2 * math.pi * turns * u + (math.pi / 4 - 2 * math.pi * turns)
        pts.append((960 + 190 * math.sin(ph), -160 + u * 780 + 42 * math.cos(ph), math.cos(ph)))
    widths = [72 * (1 if i < .86 * n else lerp(1, .8, (i - .86 * n) / (.14 * n))) for i in range(n)]

    def trunk_fn():
        draw_trunk_close(cv)
        cv.drawPath(br, P_ink(42, INK))
        cv.drawPath(br, P_ink(32, TRUNK))
    ax0, ay0 = 1290, 600
    hx, hy = pts[-1][:2]
    look = math.degrees(math.atan2(ay0 - hy, ax0 - hx))
    ang = lerp(head_angle(pts), look, eout(prog(t, 1.1, 1.7)))
    draw_snake_on_trunk(cv, pts, widths, 4.5, trunk_fn,
                        head=dict(x=hx, y=hy, ang=ang, w=72 * .8, lid=.3, tongue=prog(t, 1.5, 2.0)))
    # Apfel am Ast, Hand greift
    reach = eout(prog(t, 1.1, 1.9))
    grip = eout(prog(t, 1.9, 2.15))
    pull = ein(prog(t, 2.15, 2.4))
    hand_x = lerp(2150, ax0 + 150, reach) + 220 * pull
    hand_y = ay0 - 28 - 30 * pull
    glow = .7 + .3 * math.sin(t * 6)
    if t < 1.9:
        cv.drawLine(ax0, 478, ax0, ay0 - 52, P_ink(4, INK, 1, False))
        draw_apple(cv, ax0, ay0, 44, 'red', glow=glow)
        if reach > 0:
            draw_reach_hand(cv, hand_x, hand_y, 1.0, grip=0)
    else:
        cv.drawLine(ax0, 478, ax0, 500 + 30 * grip, P_ink(4, INK, 1, False))
        draw_reach_hand(cv, hand_x, hand_y, 1.0, grip=grip,
                        apple=lambda: draw_apple(cv, -150, 28, 44, 'red', glow=glow))
    cv.restore()


def scene_bite(cv, t):
    """00-04a  Biss (16-17.8 s), t lokal 0-1.8"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.1, t / 1.8))
    rot = math.sin(t * 1.4) * 6
    cv.save()
    cv.translate(960, 560)
    cv.rotate(rot)
    b = prog(t, .7, .9)
    draw_apple(cv, 0, 0, 230, 'red', glow=.6, bite=b)
    cv.restore()
    # Kruemel
    if t > .78:
        rnd = random.Random(2)
        for k in range(14):
            tt = t - .78
            vx, vy = rnd.uniform(80, 420), rnd.uniform(-420, -100)
            x = 960 + 200 + vx * tt
            y = 500 + vy * tt + 900 * tt * tt
            shape(cv, circle(x, y, rnd.uniform(5, 11)), '#e6dfc6', 2.5, 1 - prog(t, 1.4, 1.8))
    if .78 < t < 1.0:
        cv.drawPaint(skia.Paint(Color=col('#fff4d8', .12 * (1 - prog(t, .78, 1.0)))))
    cv.restore()


def scene_fall(cv, t):
    """00-04b  Garten klappt zusammen, Genesis 3:19, Arbeit (17.8-24 s), t lokal 0-6.2"""
    cv.drawImage(BG_NIGHT, 0, 0)
    fold = {'front': 1 - ein(prog(t, .1, .7)), 'bush': 1 - ein(prog(t, .35, .95)), 'mid': 1 - ein(prog(t, .6, 1.2))}
    barren = eout(prog(t, 1.0, 1.8))
    cv.save()
    cam(cv, lerp(960, 640, eio(prog(t, .2, 2.2))), 600, lerp(1.07, 1.0, eio(t / 6.2)))
    draw_eden(cv, t + 18, {}, fold=fold, barren=barren, figures=1 - prog(t, .2, .8))
    if t > 4.6:
        wa = eout(prog(t, 4.6, 5.0))
        draw_worker(cv, 560, 1000, 1.1, t, wa)
    cv.restore()
    # Zitat eingeritzt
    qa = 1 - prog(t, 5.9, 6.2)
    lines = ['In the sweat of thy face', 'shalt thou eat bread.']
    t0 = 1.9
    k = 0
    for li, line in enumerate(lines):
        size = 70
        x = 150
        y = 250 + li * 92
        f = skia.Font(TF_QUOTE, size)
        for ch in line:
            a = eout(prog(t, t0 + k * .045, t0 + k * .045 + .3)) * qa
            if a > 0:
                cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, f), x + 2, y + 3, P_fill(INK, a * .8, False))
                cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, f), x, y, P_fill(BONE_HI, a, False))
            x += f.measureText(ch)
            k += 1
    ca = eout(prog(t, 3.6, 4.1)) * qa
    if ca > 0:
        cap = 'GENESIS 3:19'
        cv.drawLine(154, 438, 154 + 90 * eout(prog(t, 3.6, 4.2)), 438, P_ink(2.5, GOLD, ca * .8, False))
        draw_text(cv, cap, 264, 448, TF_CAPS, 26, P_fill(GOLD, ca, False), spacing=8)


def draw_world_tree(cv, t, apple_pop, apple_glow, gold=0.0, dim_others=0.0, snake=True, figures=0.0):
    tx, gy, s = 960, 1010, 1.0
    # Boden
    gp = hill_path(1000, 14, .0032, .8, bump=(960, 30, 500))
    shape(cv, gp, '#1f211f', 4)
    cv.save()
    cv.translate(tx, gy)

    def trunk_fn():
        draw_trunk(cv, s)
        draw_crown(cv, s, dim=dim_others)
    if snake:
        n = 110
        pts = coil_points(0, -60, -330, 70, 2.2, math.pi / 4, n, head_pt=(150, -440), neck_frac=.22)
        widths = snake_widths(n, 24)
        draw_snake_on_trunk(cv, pts, widths, 2.6, trunk_fn)
        # Kopf ruht auf dem Ast
        draw_head(cv, 150, -440, head_angle(pts) - 25, 20, lid=.35, tongue=prog((t * .5) % 1, .1, .25))
    else:
        trunk_fn()
    for i, (ax, ay, kind) in enumerate(APPLES):
        p = apple_pop[i] if i < len(apple_pop) else 0
        if p <= 0:
            continue
        sc = eback(p)
        cv.drawLine(ax, ay - 34, ax, ay - 24, P_ink(3))
        draw_apple(cv, ax, ay, 25 * sc, kind, glow=apple_glow * (1 - dim_others), alpha=1 - .55 * dim_others)
        if p < 1:
            sp = 1 - p
            cv.drawPath(sparkle4(ax + 30, ay - 30, 22 * sp), P_fill(BONE_HI, sp))
    if gold > 0:
        gx, gyy = GOLD_POS
        sc = eback(clamp(gold * 1.2))
        draw_apple(cv, gx, gyy, 34 * sc, 'gold', glow=gold * (1 + .25 * math.sin(t * 5)), t=t, circuit=gold)
    if figures > 0:
        for k, fx in enumerate((-330, -250, 280)):
            cv.save()
            cv.translate(fx, -2)
            cv.scale(.32, .32)
            draw_worker(cv, 0, 0, 1, t + k * .3, figures)
            cv.restore()
    cv.restore()


def scene_tree(cv, t):
    """00-05  Viele Aepfel (24-33 s), t lokal 0-9"""
    cv.drawImage(BG_NIGHT, 0, 0)
    cv.save()
    u = eio(prog(t, 0, 8.6))
    cam(cv, 960, lerp(740, 590, u), lerp(1.55, 1.0, u))
    pops = [prog(t, .6 + i * .45, 1.0 + i * .45) for i in range(len(APPLES))]
    glow = eout(prog(t, 3.4, 4.4))
    draw_world_tree(cv, t, pops, glow, figures=1.0)
    cv.restore()


def scene_crown(cv, t):
    """00-06  Ein Apfel bleibt (33-39 s), t lokal 0-6"""
    cv.drawImage(BG_NIGHT, 0, 0)
    cv.save()
    u = eio(prog(t, 0, 3.0))
    gwx, gwy = 960 + GOLD_POS[0], 1010 + GOLD_POS[1]
    z = lerp(1.0, 2.4, u) + .15 * eio(prog(t, 3.0, 6))
    cam(cv, lerp(960, gwx, u), lerp(590, gwy + 60, u), z)
    gold = eout(prog(t, 1.8, 2.8))
    dim = eout(prog(t, 3.9, 4.8))
    draw_world_tree(cv, t, [1] * len(APPLES), .6, gold=gold, dim_others=dim, snake=True)
    cv.restore()


def scene_reflect(cv, t):
    """00-07  It does the work (39-43.5 s), t lokal 0-4.5"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 560, lerp(1.0, 1.06, t / 4.5))
    r = 330
    cy = 580 + 10 * math.sin(t * 1.5)
    draw_apple(cv, 960, cy, r, 'gold', glow=1.0 + .2 * math.sin(t * 4), t=t, circuit=.35)
    cv.save()
    cv.translate(960, cy)
    cv.clipPath(apple_path(r * .9), doAntiAlias=True)
    # Spiegelungen: Buerotuerme, Zahnrad, Bildschirme
    dark = GOLD_DK
    for k, (bx, bw, bh) in enumerate([(-220, 84, 190), (-120, 96, 260), (-6, 74, 170), (84, 104, 230)]):
        base = 270
        cv.drawRect(skia.Rect.MakeXYWH(bx, base - bh, bw, bh), P_fill(dark, .5, False))
        cv.drawRect(skia.Rect.MakeXYWH(bx, base - bh, bw, bh), P_ink(3, INK, .45, False))
        cols_n, rows_n = int((bw - 12) // 22), int((bh - 16) // 30)
        for i in range(cols_n):
            for j in range(rows_n):
                idx = k * 11 + i * 4 + (rows_n - j)
                on = prog(t, .25 + idx * .022, .3 + idx * .022)
                cv.drawRect(skia.Rect.MakeXYWH(bx + 10 + i * 22, base - bh + 12 + j * 30, 11, 16),
                            P_fill(GOLD_HI if on > .5 else '#76592a', .9, False))
    ga = eout(prog(t, 2.2, 2.7))
    if ga > 0:
        cv.save()
        cv.translate(-150, -150)
        cv.rotate(t * 70)
        for i in range(10):
            cv.save()
            cv.rotate(i * 36)
            cv.drawRect(skia.Rect.MakeXYWH(-11, -66, 22, 22), P_fill(dark, .8 * ga, False))
            cv.restore()
        cv.drawCircle(0, 0, 50, P_fill(dark, .8 * ga, False))
        cv.drawCircle(0, 0, 17, P_fill(GOLD, ga, False))
        cv.restore()
        for i in range(2):
            my = -215 + i * 70
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(10, my, 170, 52), 6, 6), P_fill(dark, .75 * ga, False))
            for j in range(3):
                lw = 130 * prog(t, 2.6 + i * .3 + j * .12, 3.0 + i * .3 + j * .12)
                cv.drawRect(skia.Rect.MakeXYWH(24, my + 10 + j * 13, lw, 6), P_fill(GOLD_HI, ga, False))
    cv.restore()
    cv.restore()


def scene_snake(cv, t):
    """00-08  Die Frage (43.5-53 s), t lokal 0-9.5"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.12, eio(t / 9.5)))
    # goldener Apfel rechts
    draw_apple(cv, 1520, 470, 190, 'gold', glow=1.0 + .25 * math.sin(t * 3.5), t=t, circuit=.6)
    # Hals von links unten
    n = 60
    pts = []
    for i in range(n):
        u = i / (n - 1)
        x = lerp(-200, 610, u)
        y = 980 - 420 * math.sin(u * math.pi * .55) + 30 * math.sin(t * 1.2 + u * 3)
        pts.append((x, y, 1.0))
    widths = [lerp(230, 190, i / (n - 1)) for i in range(n)]
    draw_snake_run(cv, pts, widths, 7, front=True)
    hx, hy = pts[-1][:2]
    ask = prog(t, 6.9, 7.4)
    lid = lerp(.55, 0.0, eout(ask)) if t < 9.0 else 0
    if 2.0 < t < 2.4:
        lid = max(lid, math.sin(prog(t, 2.0, 2.4) * math.pi))
    tongue = max(prog(t, 1.2, 1.7), prog(t, 5.6, 6.1))
    draw_head(cv, hx, hy, head_angle(pts) - 8, 190 * .95, lid=lid, tongue=tongue,
              gold_rim=.8 + .2 * math.sin(t * 3.5), pupil=lerp(1.0, .55, eout(ask)))
    cv.restore()


def scene_title(cv, t):
    """00-09  Titelkarte in der Rinde (53-60 s), t lokal 0-7"""
    cv.save()
    z = lerp(1.0, 1.05, t / 7)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2 - 100, -H / 2 - 100)
    cv.drawImage(BG_BARK, 0, 0)
    cv.restore()
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1000,
                                                [col('#000000', 0), col('#000000', .7)]))
    cv.drawPaint(vg)
    lines = [['WILL ', 'AI', ' BUY'], ['OUR CARS?']]
    size = 170
    f = skia.Font(TF_TITLE, size)
    k = 0
    for li, parts in enumerate(lines):
        full = ''.join(parts)
        x = (W - f.measureText(full)) / 2
        y = 470 + li * 200
        for part in parts:
            gold = part == 'AI'
            for ch in part:
                cw = f.measureText(ch)
                rp = prog(t, .5 + k * .16, .5 + k * .16 + .3)
                if ch != ' ' and rp > 0:
                    gid = f.textToGlyphs(ch)[0]
                    gp_ = f.getPath(gid)
                    gpath = skia.Path(gp_)
                    gpath.offset(x, y)
                    cv.save()
                    cv.clipRect(skia.Rect.MakeXYWH(x - 10, y - size, (cw + 20) * eout(rp), size * 1.3))
                    # Schnitt in die Rinde: helles Holz mit Schatten an der oberen linken Innenkante
                    cv.drawPath(gpath, P_ink(7, '#0f0d0b', 1, False))
                    cv.save()
                    cv.clipPath(gpath, doAntiAlias=True)
                    cv.drawPath(gpath, P_fill('#5a4a38', 1, False))
                    inner = skia.Path(gpath)
                    inner.offset(5, 6)
                    cv.drawPath(inner, P_fill('#cdb48b', 1, False))
                    if gold:
                        ga = eout(prog(t, 4.0, 4.6))
                        if ga > 0:
                            cv.drawPath(inner, P_fill(GOLD, ga, False))
                    cv.restore()
                    if gold:
                        ga = eout(prog(t, 4.0, 4.6))
                        if ga > 0:
                            glow = P_fill(GOLD_HI, .55 * ga * (.85 + .15 * math.sin(t * 4)), False)
                            glow.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
                            cv.drawPath(gpath, glow)
                    cv.restore()
                    if rp < 1:
                        rnd = random.Random(k)
                        for d in range(7):
                            dx = x + cw * eout(rp) + rnd.uniform(-6, 6)
                            dy = y - rnd.uniform(0, size * .8) + 50 * (1 - rp)
                            cv.drawCircle(dx, dy, rnd.uniform(1.5, 3.5), P_fill('#cdb48b', 1 - rp, False))
                x += cw
                k += 1
    cv.drawPaint(skia.Paint(Color=col('#000000', prog(t, 6.2, 7.0))))


SCENES = [
    (0.0, 5.0, scene_garden),
    (5.0, 12.0, scene_hand),
    (12.0, 13.6, scene_eye),
    (13.6, 16.0, scene_offer),
    (16.0, 17.8, scene_bite),
    (17.8, 24.0, scene_fall),
    (24.0, 33.0, scene_tree),
    (33.0, 39.0, scene_crown),
    (39.0, 43.5, scene_reflect),
    (43.5, 53.0, scene_snake),
    (53.0, 60.0, scene_title),
]

SUBS = [
    (0.6, 4.6, 'In the beginning, there was no work.'),
    (5.2, 7.0, 'No fields to plough.'),
    (7.0, 8.6, 'No rent to pay.'),
    (8.6, 9.6, 'No alarm clock.'),
    (9.6, 11.8, 'Everything you needed simply grew.'),
    (12.4, 15.7, 'Then I offered someone an apple.'),
    (16.3, 18.6, 'And the sentence came down:'),
    (22.6, 24.0, 'Work. From that day on.'),
    (24.4, 27.4, "Since then, I've offered you many more apples."),
    (27.6, 29.4, 'Each one was knowledge.'),
    (29.6, 32.8, 'And each one came with the same promise: this will lighten the sentence.'),
    (33.2, 34.8, 'None of them ended it.'),
    (35.0, 36.8, "But there's one apple left."),
    (37.0, 38.8, 'And this one is different.'),
    (39.2, 41.2, "It doesn't make work easier."),
    (41.4, 43.3, 'It does the work.'),
    (43.8, 47.2, "Before you bite, though, there's a question nobody seems to ask."),
    (47.4, 50.2, 'If machines do all the work, and nobody earns a wage…'),
    (50.4, 52.9, "…who's going to buy what they make?"),
]


def draw_subs(cv, t):
    for (a, b, s) in SUBS:
        if a <= t < b:
            al = min(prog(t, a, a + .2), 1 - prog(t, b - .2, b))
            band = skia.Paint()
            band.setShader(skia.GradientShader.MakeLinear([skia.Point(0, H - 210), skia.Point(0, H)],
                                                          [col('#000000', 0), col('#000000', .55 * al)]))
            cv.drawRect(skia.Rect.MakeXYWH(0, H - 210, W, 210), band)
            size = 42
            w = text_w(TF_SUB, size, s)
            x, y = (W - w) / 2, H - 64
            sh = P_fill('#000000', .75 * al, False)
            sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4))
            draw_text(cv, s, x + 2, y + 3, TF_SUB, size, sh)
            draw_text(cv, s, x, y, TF_SUB, size, P_fill('#e4e1d4', al, False))


# ---------------------------------------------------------------- Post (Korn, Vignette)
class Post:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
        vig = np.clip(1.0 - .32 * d ** 2.2, .55, 1.0)
        self.vig = (vig * 256).astype(np.uint16)[:, :, None]
        rng = np.random.default_rng(1)
        self.noise = [rng.normal(0, 5.5, (H, W)).astype(np.int16)[:, :, None] for _ in range(6)]

    def apply(self, rgba, frame):
        rgb = rgba[:, :, :3].astype(np.uint16)
        rgb = (rgb * self.vig) >> 8
        out = rgb.astype(np.int16) + self.noise[frame % len(self.noise)]
        return np.clip(out, 0, 255).astype(np.uint8)


def render_frame(surface, frame):
    t = frame / FPS
    G.frame = frame
    G.zoom = 1.0
    cv = surface.getCanvas()
    cv.clear(col(BG))
    for (a, b, fn) in SCENES:
        if a <= t < b:
            cv.save()
            fn(cv, t - a)
            cv.restore()
            break
    G.zoom = 1.0
    draw_subs(cv, t)
    return surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def main():
    init_assets()
    surface = skia.Surface(W, H)
    post = Post()
    mode = sys.argv[1]
    if mode == 'still':
        for i in range(2, len(sys.argv) - 1, 2):
            sec, out = float(sys.argv[i]), sys.argv[i + 1]
            f = int(round(sec * FPS))
            arr = post.apply(render_frame(surface, f), f)
            from PIL import Image
            Image.fromarray(arr).save(out)
            print('saved', out)
    elif mode == 'render':
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                                 '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            arr = post.apply(render_frame(surface, f), f)
            proc.stdin.write(arr.tobytes())
            if f % 48 == 0:
                print('frame', f, flush=True)
        proc.stdin.close()
        proc.wait()


if __name__ == '__main__':
    main()
