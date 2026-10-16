#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Testanimation v2: Cold Open (00-01 bis 00-09) + Flash-Forward (F-01 bis F-11).

Stil: Rational Animations (Anthrazit, knochenweisse Figuren mit Tuschekontur,
Rasterpunkte, Filmkorn, gedaempfte Palette) + Kurzgesagt (leuchtende Bedrohungsfarbe).
Rendern:  python3 coldopen.py render <start_frame> <end_frame> <out.mp4>
Standbild: python3 coldopen.py still <sekunde> <out.png>
"""
import math, os, random, subprocess, sys
import numpy as np
import skia

W, H, FPS = 1920, 1080, 24
DUR = 130.0
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = lambda n: skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', n))
TF_SUB = FONT('Oswald_400Regular.ttf')
TF_TITLE = FONT('Cinzel_900Black.ttf')
TF_CAPS = FONT('Cinzel_700Bold.ttf')
TF_QUOTE = FONT('IMFellEnglish_400Regular_Italic.ttf')
TF_HEAD = FONT('Oswald_500Medium.ttf')
TF_TYPE = FONT('SpecialElite_400Regular.ttf')

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
    ow = ow if ow is not None else min(6.0, max(2.0, r * .11))
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
    cv.drawPath(head_path(w, closed=False), P_ink(min(6.0, max(2.5, w * .07))))
    # Mund (leichtes Schmunzeln), Nasenloch, Brauenwulst
    m = skia.Path()
    m.moveTo(L * .97, w * .1)
    m.cubicTo(L * .8, w * .2, L * .62, w * .24, L * .46, D * .2)
    m.quadTo(L * .4, D * .17, L * .37, D * .1)
    cv.drawPath(m, P_ink(min(4.5, max(1.5, w * .045))))
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
    cv.drawPath(eye, P_ink(min(4.5, max(1.8, w * .05))))
    br = skia.Path()
    br.moveTo(ex - er * 1.4, ey - er * 1.25)
    br.quadTo(ex - er * .1, ey - er * 1.6, ex + er * 1.5, ey - er * .55)
    cv.drawPath(br, P_ink(min(7.0, max(2, w * .09))))
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


def capsule(x0, y0, x1, y1, r0, r1):
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    q = poly([(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1),
              (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)])
    return union([q, circle(x0, y0, r0), circle(x1, y1, r1)])


def finger(x, y, ang, segs, bend):
    """Finger aus verjuengten Kapseln; ang/bend in Grad (bend pro Gelenk)."""
    parts = []
    a = math.radians(ang)
    for (L, r0, r1) in segs:
        x1, y1 = x + math.cos(a) * L, y + math.sin(a) * L
        parts.append(capsule(x, y, x1, y1, r0, r1))
        x, y = x1, y1
        a += math.radians(bend)
    return union(parts)


def outlined(cv, path, fill=BONE, ow=3.5, a=1.0):
    cv.drawPath(path, P_fill(fill, a))
    cv.drawPath(path, P_ink(ow, INK, a))


def draw_hand_open(cv, x, y, s, curl=0.0, a=1.0, apple=None):
    """Hohle Hand von der Daumenseite, Handflaeche nach oben, Unterarm von links unten."""
    c = clamp(curl)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    ow = 3.5 / s
    for (bx, by, ang, segs) in [(92, 24, 10, [(36, 12, 11), (26, 11, 10), (18, 10, 8.5)]),
                                (98, 10, 4, [(46, 14, 13), (32, 13, 11.5), (22, 11.5, 9.5)]),
                                (100, -6, -2, [(52, 15, 14), (36, 14, 12), (26, 12, 10)])]:
        outlined(cv, finger(bx, by, ang, segs, -(12 + 34 * c)), BONE_SH, ow, a)
    arm = union([capsule(-380, 220, 0, 0, 50, 40), capsule(0, 0, 104, 4, 40, 33)])
    outlined(cv, arm, BONE, ow, a)
    if apple:
        cv.save()
        cv.scale(1 / s, 1 / s)
        cv.translate(-x, -y)
        apple()
        cv.restore()
    outlined(cv, finger(100, -22, -8, [(48, 15, 14), (34, 14, 12), (24, 12, 10)], -(14 + 34 * c)), BONE, ow, a)
    outlined(cv, finger(30, -26, -62, [(42, 19, 16), (34, 16, 13)], 28 + 10 * c), BONE, ow, a)
    cv.drawPath(bez((-150, 92), (-110, 70), (-70, 48), (-30, 30)), P_ink(3 / s, BONE_SH, .8 * a))
    cv.drawPath(bez((30, 16), (55, 24), (80, 22), (98, 16)), P_ink(3 / s, BONE_SH, a))
    cv.restore()


def draw_reach_hand(cv, x, y, s, grip=0.0, a=1.0, apple=None):
    """Hand von rechts, greift nach links (Handruecken sichtbar). apple malt den Apfel zwischen Daumen und Fingern."""
    g = clamp(grip)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    ow = 3.5 / s
    outlined(cv, finger(-40, 30, 150, [(42, 19, 16), (34, 16, 13)], 18 * g), BONE_SH, ow, a)
    if apple:
        cv.save()
        apple()
        cv.restore()
    arm = union([capsule(520, 200, 0, 0, 52, 42), capsule(0, 0, -96, 2, 42, 36)])
    outlined(cv, arm, BONE, ow, a)
    bend = -(8 + 40 * g)
    for (bx, by, ang, segs) in [(-84, 26, 172, [(36, 13, 12), (26, 12, 10), (18, 10, 8.5)]),
                                (-92, 10, 178, [(48, 15, 14), (34, 14, 12), (22, 12, 10)]),
                                (-96, -8, 182, [(52, 16, 15), (38, 15, 13), (26, 13, 11)]),
                                (-92, -26, 186, [(46, 15, 14), (34, 14, 12), (24, 12, 10)])]:
        outlined(cv, finger(bx, by, ang, segs, bend), BONE, ow, a)
    for ky in (-24, -6, 12):
        k = skia.Path()
        k.addArc(skia.Rect.MakeXYWH(-104, ky - 6, 16, 14), 120, 120)
        cv.drawPath(k, P_ink(2.5 / s, BONE_SH, a))
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
    fx, fy0, fy1 = 540, 252, 704
    if fall <= 0:
        fy = fy0
    elif fall < 1:
        fy = lerp(fy0, fy1, ein(fall))
    else:
        fy = fy1 - 26 * abs(math.sin((t - 5.9) * 9)) * math.exp(-(t - 5.9) * 5)
    cv.drawLine(540, 176, 540, 222, P_ink(4, INK, 1 - eout(prog(t, 5.0, 5.2)), False))
    # Hand
    curl = .2 + .6 * eout(prog(t, 5.9, 6.4))
    if fall < 1:
        draw_hand_open(cv, 430, 760, 1.3, curl=curl)
        draw_apple(cv, fx, fy, 30, 'red', glow=.3)
    else:
        draw_hand_open(cv, 430, 760, 1.3, curl=curl, apple=lambda: draw_apple(cv, fx, fy, 30, 'red', glow=.3))
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
    cv.drawPath(alm, P_ink(8, INK))
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
                        apple=lambda: draw_apple(cv, -168, 22, 44, 'red', glow=glow))
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
        pts = coil_points(0, -50, -330, 82, 2.0, math.pi / 4, n, head_pt=(175, -455), neck_frac=.22)
        widths = snake_widths(n, 38)
        draw_snake_on_trunk(cv, pts, widths, 3.2, trunk_fn)
        # Kopf ruht auf dem Ast
        draw_head(cv, 175, -455, head_angle(pts) - 25, 30, lid=.35, tongue=prog((t * .5) % 1, .1, .25))
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
            cv.scale(.42, .42)
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
    draw_snake_run(cv, pts, widths, 5, front=True)
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


# ================================================================ Flash-Forward (F-01 bis F-11)
VISOR = '#17140f'
WOOD = '#3b342d'
PAPER = '#cbcabe'
PAPER_SH = '#a9a89c'
SLIP = '#d6cdb2'


def visor_path(x, r, y0, y1):
    ry = r * .2
    p = skia.Path()
    p.moveTo(x - r, y0)
    p.arcTo(skia.Rect.MakeXYWH(x - r, y0 - ry, 2 * r, 2 * ry), 180, -180, False)
    p.lineTo(x + r, y1)
    p.arcTo(skia.Rect.MakeXYWH(x - r, y1 - ry, 2 * r, 2 * ry), 0, 180, False)
    p.close()
    return p


def face_paths(x, fy, r, opened=0.0):
    eh = r * .07
    out = []
    for sx in (-1, 1):
        e = skia.Path()
        cx = x + sx * r * .19
        if opened <= 0:
            e.addArc(skia.Rect.MakeXYWH(cx - eh, fy - r * .05 - eh * .7, eh * 2, eh * 1.6), 200, 140)
        else:
            e.addOval(skia.Rect.MakeXYWH(cx - eh * .8, fy - r * .08, eh * 1.6, eh * 1.6 * opened + 1))
        out.append(e)
    m = skia.Path()
    m.addArc(skia.Rect.MakeXYWH(x - r * .13, fy - r * .02, r * .26, r * .14), 20, 140)
    out.append(m)
    return out


def eden_geom(x, base_y, h, r):
    top = base_y - h
    ry = r * .2
    return top, ry, top + r * .32, top + r * .62


def draw_eden_bot(cv, x, base_y, h, r, t, face=1.0, logo=0.0, glow=1.0, opened=0.0, hatches=0.0):
    top, ry, vy0, vy1 = eden_geom(x, base_y, h, r)
    body = skia.Path()
    body.addRect(skia.Rect.MakeLTRB(x - r, top, x + r, base_y + ry))
    capo = skia.Path()
    capo.addOval(skia.Rect.MakeXYWH(x - r, top - ry, 2 * r, 2 * ry))
    sil = union([body, capo])
    if glow > 0:
        cv.drawRect(skia.Rect.MakeLTRB(x - r * 1.05, top - ry, x + r * 1.05, base_y), P_glow(GOLD_HI, r * .45, .22 * glow))
    ow = min(6.0, max(3.0, r * .012))
    cv.drawPath(sil, P_fill(GOLD))
    cv.save()
    cv.clipPath(sil, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeLTRB(x - r * .8, top - ry, x - r * .52, base_y + ry), P_fill(GOLD_HI, .32, False))
    cv.drawRect(skia.Rect.MakeLTRB(x - r * .44, top - ry, x - r * .38, base_y + ry), P_fill(GOLD_HI, .22, False))
    cv.drawRect(skia.Rect.MakeLTRB(x + r * .4, top - ry, x + r, base_y + ry), P_fill(GOLD_DK, .42, False))
    cv.drawRect(skia.Rect.MakeLTRB(x + r * .74, top - ry, x + r, base_y + ry), P_fill(GOLD_DK, .38, False))
    step = max(60.0, r * .55)
    yy = vy1 + r * .5
    while yy < base_y:
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(x - r, yy - ry, 2 * r, 2 * ry), 0, 180)
        cv.drawPath(a, P_ink(max(2.0, r * .011), GOLD_DK, .85))
        yy += step
    if hatches > 0:
        for (hx, hy) in ((-.78, .95), (.78, 1.1), (-.7, 1.6), (.72, 1.75)):
            if top + r * hy > base_y - 20:
                continue
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + r * hx - r * .09, top + r * hy, r * .18, r * .1 * hatches),
                                       r * .02, r * .02)
            cv.drawRRect(rr, P_fill(VISOR, 1, False))
    if logo > 0:
        size = r * .3
        f = skia.Font(TF_TITLE, size)
        tw = f.measureText('EDEN')
        ly = top + r * 1.08 + ry * .9
        blob = skia.TextBlob.MakeFromString('EDEN', f)
        cv.drawTextBlob(blob, x - tw / 2 + r * .006, ly + r * .008, P_fill(GOLD_HI, .55 * logo, False))
        cv.drawTextBlob(blob, x - tw / 2, ly, P_fill(GOLD_DK, logo, False))
        sh = (t * .45) % 1.6 - .3
        if 0 <= sh <= 1:
            cv.save()
            pth = skia.Path()
            pth.addRect(skia.Rect.MakeXYWH(x - tw / 2 + tw * sh - r * .05, ly - size, r * .07, size * 1.2))
            cv.clipPath(pth)
            cv.drawTextBlob(blob, x - tw / 2, ly, P_fill(GOLD_HI, .8 * logo, False))
            cv.restore()
        f2 = skia.Font(TF_QUOTE, r * .085)
        sl = 'Work is optional.'
        sw = f2.measureText(sl)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(sl, f2), x - sw / 2, ly + r * .17, P_fill(GOLD_DK, logo, False))
    cv.restore()
    cv.drawPath(capo, P_fill('#e6c77c'))
    cv.drawOval(skia.Rect.MakeXYWH(x - r * .62, top - ry * .62, r * 1.24, ry * 1.24), P_ink(max(2.0, r * .011), GOLD_DK, .7))
    cv.drawPath(sil, P_ink(ow))
    cv.drawPath(capo, P_ink(ow))
    vp = visor_path(x, r, vy0, vy1)
    cv.drawPath(vp, P_fill(VISOR))
    cv.drawPath(vp, P_ink(ow))
    if face > 0:
        fy = (vy0 + vy1) / 2 + ry * .95
        for pth in face_paths(x, fy, r, opened):
            g = P_ink(r * .04, GOLD_HI, .55 * face, wobble=False)
            g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(2.0, r * .03)))
            cv.drawPath(pth, g)
            cv.drawPath(pth, P_ink(max(2.0, r * .024), GOLD_HI, face, wobble=False))
    return (x, (vy0 + vy1) / 2 + ry)


def ik2(bx, by, tx, ty, l1, l2, flip=1):
    dx, dy = tx - bx, ty - by
    d = max(abs(l1 - l2) + 1e-3, min(math.hypot(dx, dy), l1 + l2 - 1e-3))
    a = math.atan2(dy, dx)
    b = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    ex, ey = bx + math.cos(a + flip * b) * l1, by + math.sin(a + flip * b) * l1
    ang = math.atan2(ty - ey, tx - ex)
    return (ex, ey), (ex + math.cos(ang) * l2, ey + math.sin(ang) * l2)


def draw_arm(cv, joints, w, a=1.0):
    n = len(joints)
    parts = []
    for i in range(n - 1):
        (x0, y0), (x1, y1) = joints[i], joints[i + 1]
        parts.append(capsule(x0, y0, x1, y1, w / 2 * (1 - .18 * i / (n - 1)), w / 2 * (1 - .18 * (i + 1) / (n - 1))))
    path = union(parts)
    cv.drawPath(path, P_fill(GOLD, a))
    cv.save()
    cv.clipPath(path, doAntiAlias=True)
    for i in range(n - 1):
        (x0, y0), (x1, y1) = joints[i], joints[i + 1]
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        cv.drawLine(x0 - nx * w * .22, y0 - ny * w * .22, x1 - nx * w * .22, y1 - ny * w * .22,
                    P_ink(w * .14, GOLD_HI, .55 * a, wobble=False))
        cv.drawLine(x0 + nx * w * .3, y0 + ny * w * .3, x1 + nx * w * .3, y1 + ny * w * .3,
                    P_ink(w * .2, GOLD_DK, .4 * a, wobble=False))
    cv.restore()
    cv.drawPath(path, P_ink(3.5, INK, a))
    for (jx, jy) in joints[1:-1]:
        cv.drawCircle(jx, jy, w * .34, P_fill(GOLD_DK, a, False))
        cv.drawCircle(jx, jy, w * .34, P_ink(3, INK, a, False))
        cv.drawCircle(jx, jy, w * .1, P_fill(GOLD_HI, a, False))


def draw_claw(cv, x, y, ang, w, grip=0.0, a=1.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(math.degrees(ang))
    for sx in (-1, 1):
        sp = .55 - .4 * grip
        c = capsule(0, 0, w * 1.0, sx * w * sp, w * .22, w * .16)
        c2 = capsule(w * 1.0, sx * w * sp, w * 1.5, sx * w * (sp - .35), w * .16, w * .1)
        outlined(cv, union([c, c2]), GOLD_DK, 3, a)
    cv.drawCircle(0, 0, w * .38, P_fill(GOLD, a, False))
    cv.drawCircle(0, 0, w * .38, P_ink(3, INK, a, False))
    cv.restore()


# ---------------------------------------------------------------- City
def make_city(seed):
    rnd = random.Random(seed)
    back, front = [], []
    x = -80
    while x < W + 80:
        w_, h_ = rnd.uniform(70, 150), rnd.uniform(230, 470)
        back.append((x, w_, h_, rnd.random()))
        x += w_ + rnd.uniform(-12, 14)
    x = -60
    while x < W + 60:
        w_, h_ = rnd.uniform(100, 200), rnd.uniform(120, 300)
        front.append((x, w_, h_, rnd.random()))
        x += w_ + rnd.uniform(6, 30)
    return back, front


CITY = make_city(12)


def draw_city_layer(cv, blds, ground, colr, win_on, gold_frac, seed, win_alpha=.55):
    rnd = random.Random(seed)
    for (x, w_, h_, k) in blds:
        top = ground - h_
        path = skia.Path()
        path.addRect(skia.Rect.MakeLTRB(x, top, x + w_, ground + 300))
        if k < .3:
            path.addRect(skia.Rect.MakeXYWH(x + w_ * .3, top - 40, 6, 40))
        elif k < .5:
            path.addRect(skia.Rect.MakeXYWH(x + w_ * .55, top - 26, w_ * .3, 26))
        cv.drawPath(path, P_fill(colr, 1, False))
        cv.drawPath(path, P_ink(3, INK, 1, False))
        cols, rows = int((w_ - 16) // 24), int((h_ - 20) // 32)
        for cx in range(cols):
            for cy in range(rows):
                on = rnd.random() < win_on
                g = rnd.random() < gold_frac
                if on or g:
                    cv.drawRect(skia.Rect.MakeXYWH(x + 11 + cx * 24, top + 16 + cy * 32, 10, 15),
                                P_fill(GOLD if g else '#8d8b80', .95 if g else win_alpha, False))


def draw_cone(cv, x0, y0, w0, x1, y1, w1, c, a):
    p = poly([(x0 - w0, y0), (x0 + w0, y0), (x1 + w1, y1), (x1 - w1, y1)])
    pt = skia.Paint(AntiAlias=True)
    pt.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(c, .32 * a), col(c, .08 * a)]))
    pt.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
    cv.drawPath(p, pt)


def scene_zoomapple(cv, t):
    """F-01a  Der goldene Apfel waechst und flutet das Bild (53.0-54.4)"""
    scene_snake(cv, 9.5 + t)
    u = ein(prog(t, 0, 1.4))
    x, y, r = lerp(1587, 960, u), lerp(462, 540, u), lerp(213, 2600, u)
    G.zoom = 1.0
    draw_apple(cv, x, y, r, 'gold', glow=1.2, t=53 + t, circuit=.6)
    cv.drawPaint(skia.Paint(Color=col(GOLD, prog(t, .9, 1.4))))


def scene_city(cv, t):
    """F-01b/F-02  Stadt bei Nacht, EDEN steigt auf (54.4-61.0)"""
    cv.drawImage(BG_NIGHT, 0, 0)
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.05, eio(t / 6.6)))
    back, front = CITY
    rise = eio(prog(t, 1.4, 4.4))
    bx, base, r = 1240, 1060, 175
    h = lerp(0, 900, rise)
    gold = .05 + .55 * eout(prog(t, 4.6, 6.6))
    draw_city_layer(cv, back, 1100, '#222524', .14, gold * .6, 1, .35)
    if h > 5:
        face = eout(prog(t, 4.0, 4.6))
        draw_eden_bot(cv, bx, base, h, r, t, face=face, glow=.6 + .4 * face)
    draw_city_layer(cv, front, 1110, '#171918', .2, gold, 2)
    ca = eout(prog(t, 4.4, 5.4))
    if ca > 0:
        top, ry, vy0, vy1 = eden_geom(bx, base, h, r)
        draw_cone(cv, bx, (vy0 + vy1) / 2 + ry, r * .55, 900, 1100, 900, GOLD_HI, ca)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col(GOLD, 1 - eout(prog(t, 0, 1.4)))))


def scene_eden_close(cv, t):
    """F-03  Nahaufnahme: EDEN, Work is optional (61.0-67.8)"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 560, lerp(1.1, 1.0, eio(t / 6.8)))
    G.zoom = 1.0
    bx, r = 960, 640
    top = -120
    hatch = eout(prog(t, 4.4, 5.0))
    draw_eden_bot(cv, bx, top + 1500, 1500, r, t, face=1.0, logo=eout(prog(t, .5, 1.3)), glow=.8, hatches=hatch)
    if t > 5.0:
        ex = eout(prog(t, 5.0, 6.4))
        for sx, hy, ph in ((-1, .95, 0), (1, 1.1, 1.3)):
            hx0 = bx + sx * r * .78
            hy0 = top + r * hy + r * .05
            tx = hx0 + sx * lerp(0, 420, ex)
            ty = hy0 + lerp(0, 120, ex) + 30 * math.sin(t * 3 + ph)
            el, end = ik2(hx0, hy0, tx, ty, 260, 240, flip=-sx)
            draw_arm(cv, [(hx0, hy0), el, end], 46)
            draw_claw(cv, end[0], end[1], math.atan2(end[1] - el[1], end[0] - el[0]), 40, .3 + .3 * math.sin(t * 4))
    cv.restore()


# ---------------------------------------------------------------- Panels (F-04)
PANELS = [(40, 36, 908, 470), (972, 36, 908, 470), (40, 530, 908, 470), (972, 530, 908, 470)]


def sheet(cv, cx, cy, w, h, rot, stamped=0.0, seed=0, a=1.0):
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(rot)
    rr = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 8, -h / 2 + 10, w, h), P_fill('#000000', .25 * a, False))
    cv.drawRect(rr, P_fill(PAPER, a, False))
    cv.drawRect(rr, P_ink(3, INK, a, False))
    rnd = random.Random(seed)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 18, -h / 2 + 18, w * .55, 14), 7, 7), P_fill('#5c5d56', a, False))
    for i in range(int((h - 70) // 22)):
        lw = (w - 40) * rnd.uniform(.5, .95)
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 18, -h / 2 + 48 + i * 22, lw, 9), 4.5, 4.5),
                     P_fill(PAPER_SH, a, False))
    if stamped > 0:
        cv.save()
        cv.rotate(-9)
        sw, shh = w * .78, h * .2
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-sw / 2, -shh / 2 + h * .12, sw, shh), 8, 8),
                     P_ink(5, RED, .9 * a * stamped, False))
        f = skia.Font(TF_HEAD, shh * .62)
        tw = f.measureText('APPROVED')
        cv.drawTextBlob(skia.TextBlob.MakeFromString('APPROVED', f), -tw / 2, h * .12 + shh * .22,
                        P_fill(RED, .9 * a * stamped, False))
        cv.restore()
    cv.restore()


def panel_contracts(cv, w, h, t):
    cv.drawRect(skia.Rect.MakeWH(w, h), P_fill(WOOD, 1, False))
    for i in range(9):
        y = 30 + i * 52
        p = skia.Path()
        p.moveTo(-10, y)
        for x in range(0, int(w) + 40, 40):
            p.lineTo(x, y + 6 * math.sin(x * .02 + i))
        cv.drawPath(p, P_ink(3, '#2e2823', .8, False))
    period = 1.1
    k = int(t // period)
    u = (t % period) / period
    for i in range(5):
        sheet(cv, 150 + i * 1.5, 250 - i * 3, 190, 250, -4 + i, 0, 100 + i)
    for i in range(min(k, 8)):
        sheet(cv, 760 + (i % 2) * 6, 250 - i * 3, 190, 250, 3 + (i * 37 % 7) - 3, 1, 200 + i)
    cx = lerp(150, 450, eout(prog(u, 0, .25)))
    if u > .72:
        cx = lerp(450, 760, ein(prog(u, .72, 1)))
    sheet(cv, cx, 245, 210, 270, lerp(-4, 0, prog(u, 0, .25)), 1.0 if u > .48 else 0, 300 + k)
    press = 1 - abs(prog(u, .3, .62) * 2 - 1) if .3 < u < .62 else 0
    lift = 1 - press
    sx, sy = 450, 250
    shadow = 18 * lift
    sc = 1 + .12 * lift
    base = (w * .7, -80)
    el, end = ik2(base[0], base[1], sx + 10, sy - 40 - 20 * lift, 230, 210, flip=1)
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx - 70 * sc + shadow, sy - 45 * sc + shadow, 140 * sc, 90 * sc), 14, 14),
                 P_fill('#000000', .3, False))
    draw_arm(cv, [base, el, end], 44)
    stamp = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx - 70 * sc, sy - 45 * sc, 140 * sc, 90 * sc), 14, 14)
    cv.drawRRect(stamp, P_fill('#3a2f27', 1, False))
    cv.drawRRect(stamp, P_ink(3.5, INK, 1, False))
    cv.drawCircle(sx, sy, 30 * sc, P_fill(GOLD_DK, 1, False))
    cv.drawCircle(sx, sy, 30 * sc, P_ink(3, INK, 1, False))


def car_path(x, y, L=300):
    p = skia.Path()
    p.moveTo(x, y - 30)
    p.lineTo(x + 4, y - 62)
    p.lineTo(x + L * .24, y - 74)
    p.lineTo(x + L * .36, y - 116)
    p.lineTo(x + L * .68, y - 116)
    p.lineTo(x + L * .82, y - 74)
    p.lineTo(x + L, y - 62)
    p.lineTo(x + L, y - 30)
    p.close()
    return p


def draw_car(cv, x, y, L, colr, a=1.0, wheels=True):
    body = car_path(x, y, L)
    cv.drawPath(body, P_fill(colr, a))
    cv.drawPath(body, P_ink(3.5, INK, a))
    for (a0, a1) in ((.39, .51), (.54, .66)):
        win = poly([(x + L * a0, y - 108), (x + L * a1, y - 108), (x + L * (a1 + .05 if a1 > .6 else a1), y - 78),
                    (x + L * (a0 - .05 if a0 < .4 else a0), y - 78)])
        cv.drawPath(win, P_fill('#23262a', a, False))
        cv.drawPath(win, P_ink(2.5, INK, a, False))
    cv.drawLine(x + 10, y - 48, x + L - 10, y - 48, P_ink(2.5, INK, .5 * a, False))
    if wheels:
        for wx in (x + L * .2, x + L * .8):
            cv.drawCircle(wx, y - 26, 28, P_fill('#151616', a, False))
            cv.drawCircle(wx, y - 26, 28, P_ink(3, INK, a, False))
            cv.drawCircle(wx, y - 26, 11, P_fill(BONE_SH, a, False))


def panel_cars(cv, w, h, t):
    cv.drawRect(skia.Rect.MakeWH(w, h), P_fill('#202322', 1, False))
    for gx in range(0, int(w), 26):
        for gy in range(0, 200, 26):
            cv.drawCircle(gx, gy, 2.6 * (1 - gy / 200), P_fill('#2a2d2c', 1, False))
    gy = 380
    cv.drawRect(skia.Rect.MakeLTRB(0, gy, w, gy + 34), P_fill('#2b2b29', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(-5, gy, w + 5, gy + 34), P_ink(3, INK, 1, False))
    for i in range(14):
        rx = (i * 70 - t * 60) % (w + 70) - 35
        cv.drawCircle(rx, gy + 17, 11, P_fill('#4a4a46', 1, False))
        cv.drawCircle(rx, gy + 17, 11, P_ink(2.5, INK, 1, False))
    for i in range(3):
        cx = (t * 55 + i * 430) % (w + 430) - 330
        draw_car(cv, cx, gy, 300, (BONE, '#8c3b30', '#4b6278')[i])
    tip = (w * .52 + 10 * math.sin(t * 5), gy - 120 + 6 * math.sin(t * 9))
    el, end = ik2(w * .7, -60, tip[0], tip[1], 210, 200, flip=1)
    draw_arm(cv, [(w * .7, -60), el, end], 44)
    ang = math.atan2(end[1] - el[1], end[0] - el[0])
    nz = (end[0] + math.cos(ang) * 30, end[1] + math.sin(ang) * 30)
    cv.drawLine(end[0], end[1], nz[0], nz[1], P_ink(16, INK, 1, False))
    cv.drawLine(end[0], end[1], nz[0], nz[1], P_ink(10, GOLD_DK, 1, False))
    cv.drawCircle(nz[0], nz[1], 30, P_glow(GOLD_HI, 14, .8))
    cv.drawCircle(nz[0], nz[1], 9, P_fill('#fff6dc', 1, False))
    for j in range(22):
        ph = (t * 3 + j / 22) % 1
        rnd = random.Random(j * 131 + int(t * 3 + j / 22))
        vx, vy = rnd.uniform(-260, 260), rnd.uniform(-320, -60)
        x0 = nz[0] + vx * ph
        y0 = nz[1] + vy * ph + 600 * ph * ph
        x1 = x0 - vx * .04
        y1 = y0 - (vy + 1200 * ph) * .04
        cv.drawLine(x0, y0, x1, y1, P_ink(3, GOLD_HI, 1 - ph, wobble=False))


def panel_food(cv, w, h, t):
    cv.drawRect(skia.Rect.MakeWH(w, h), P_fill('#252321', 1, False))
    for i in range(6):
        cv.drawRect(skia.Rect.MakeXYWH(i * 160 + 20, 40, 120, 120), P_ink(3, '#2f2c29', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(0, 380, w, h), P_fill('#1a1918', 1, False))
    cv.drawLine(0, 380, w, 380, P_ink(4, INK, 1, False))
    cv.drawRect(skia.Rect.MakeXYWH(250, 362, 260, 18), P_fill('#3a3836', 1, False))
    for k in range(7):
        fx = 290 + k * 30
        fl = 18 + 6 * math.sin(t * 20 + k)
        p = poly([(fx - 8, 362), (fx, 362 - fl), (fx + 8, 362)])
        cv.drawPath(p, P_fill('#c9773d', .9, False))
    period = 1.5
    u = (t % period) / period
    jerk = math.sin(prog(u, .28, .4) * math.pi) * 10
    pan_y = 330 - jerk
    pan = poly([(270, pan_y - 22), (490, pan_y - 22), (470, pan_y + 6), (290, pan_y + 6)])
    cv.drawLine(490, pan_y - 14, 620, pan_y - 40, P_ink(20, INK, 1, False))
    cv.drawLine(490, pan_y - 14, 620, pan_y - 40, P_ink(13, '#3a3836', 1, False))
    if .32 < u < .82:
        q = prog(u, .32, .82)
        px = 380 + 10 * math.sin(q * math.pi)
        py = pan_y - 34 - 230 * math.sin(q * math.pi)
        fl = math.cos(q * math.pi * 2)
        cv.drawOval(skia.Rect.MakeXYWH(px - 70, py - 14 * abs(fl) - 4, 140, 28 * abs(fl) + 8),
                    P_fill('#d9b878' if fl > 0 else '#b48a4a', 1, False))
        cv.drawOval(skia.Rect.MakeXYWH(px - 70, py - 14 * abs(fl) - 4, 140, 28 * abs(fl) + 8), P_ink(3, INK, 1, False))
    else:
        cv.drawOval(skia.Rect.MakeXYWH(310, pan_y - 40, 140, 22), P_fill('#d9b878', 1, False))
        cv.drawOval(skia.Rect.MakeXYWH(310, pan_y - 40, 140, 22), P_ink(3, INK, 1, False))
    cv.drawPath(pan, P_fill('#2f2e2c'))
    cv.drawPath(pan, P_ink(3.5))
    for k in range(3):
        sy = (t * 40 + k * 60) % 180
        sp = skia.Path()
        sx = 340 + k * 50
        sp.moveTo(sx, pan_y - 50 - sy)
        sp.cubicTo(sx + 15, pan_y - 70 - sy, sx - 15, pan_y - 90 - sy, sx, pan_y - 110 - sy)
        cv.drawPath(sp, P_ink(4, BONE, .25 * (1 - sy / 180), False))
    el, end = ik2(w + 60, 120, 620, pan_y - 40, 220, 200, flip=1)
    draw_arm(cv, [(w + 60, 120), el, end], 44)
    draw_claw(cv, end[0], end[1], math.atan2(end[1] - el[1], end[0] - el[0]), 34, .9)


def panel_never(cv, w, h, t):
    cyc = 1.2
    dn = .5 + .5 * math.cos(t / cyc * 2 * math.pi)
    cv.drawRect(skia.Rect.MakeWH(w, h), P_fill(mix('#262826', '#3d3f3a', 1 - dn), 1, False))
    wx, wy, ww, wh = 60, 50, 330, 250
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), P_fill(mix('#141a20', '#7d8a86', 1 - dn), 1, False))
    ang = (t / cyc) * 2 * math.pi
    sxp, syp = wx + ww / 2 + math.sin(ang) * 120, wy + wh * .95 - abs(math.cos(ang)) * 170
    if math.cos(ang) < 0:
        cv.drawCircle(sxp, syp, 30, P_fill(GOLD, 1, False))
    else:
        cv.drawCircle(sxp, syp, 26, P_fill(BONE_HI, 1, False))
        cv.drawCircle(sxp + 10, syp - 6, 22, P_fill(mix('#141a20', '#7d8a86', 1 - dn), 1, False))
    for i in range(5):
        cv.drawRect(skia.Rect.MakeXYWH(wx + i * 70, wy + wh - 60 - (i * 29 % 50), 50, 80), P_fill('#1b1d1c', 1, False))
    cv.restore()
    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), P_ink(10, '#4a4740', 1, False))
    cv.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, P_ink(8, '#4a4740', 1, False))
    ccx, ccy = 600, 140
    cv.drawCircle(ccx, ccy, 82, P_fill(BONE, 1, False))
    cv.drawCircle(ccx, ccy, 82, P_ink(4, INK, 1, False))
    for i in range(12):
        a = i * math.pi / 6
        cv.drawLine(ccx + math.cos(a) * 66, ccy + math.sin(a) * 66, ccx + math.cos(a) * 76, ccy + math.sin(a) * 76,
                    P_ink(3, INK, 1, False))
    ha = t / cyc * 2 * math.pi - math.pi / 2
    ma = ha * 12
    cv.drawLine(ccx, ccy, ccx + math.cos(ha) * 40, ccy + math.sin(ha) * 40, P_ink(7, INK, 1, False))
    cv.drawLine(ccx, ccy, ccx + math.cos(ma) * 62, ccy + math.sin(ma) * 62, P_ink(4, INK, 1, False))
    day = int(t / cyc) % 31 + 1
    cv.drawRect(skia.Rect.MakeXYWH(740, 60, 120, 140), P_fill(BONE, 1, False))
    cv.drawRect(skia.Rect.MakeXYWH(740, 60, 120, 34), P_fill(RED, 1, False))
    cv.drawRect(skia.Rect.MakeXYWH(740, 60, 120, 140), P_ink(3.5, INK, 1, False))
    f = skia.Font(TF_HEAD, 72)
    s_ = str(day)
    cv.drawTextBlob(skia.TextBlob.MakeFromString(s_, f), 800 - f.measureText(s_) / 2, 178, P_fill(INK, 1, False))
    kx, ky = 260, 360
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(kx, ky, 420, 80), 10, 10), P_fill('#2f302d', 1, False))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(kx, ky, 420, 80), 10, 10), P_ink(3.5, INK, 1, False))
    step = int(t * 7)
    for r_ in range(3):
        for c_ in range(14):
            lit = (step * 5 + 3) % 42 == r_ * 14 + c_
            cv.drawRect(skia.Rect.MakeXYWH(kx + 12 + c_ * 29, ky + 10 + r_ * 22, 22, 16),
                        P_fill(GOLD_HI if lit else '#5a5a55', 1, False))
    kk = (step * 5 + 3) % 42
    tx = kx + 23 + (kk % 14) * 29
    ty = ky + 18 + (kk // 14) * 22 - 26 * (1 - ((t * 7) % 1))
    el, end = ik2(w + 40, h + 40, tx, ty - 30, 260, 240, flip=-1)
    draw_arm(cv, [(w + 40, h + 40), el, end], 44)
    draw_claw(cv, end[0], end[1], math.atan2(end[1] - el[1], end[0] - el[0]), 32, .7)


def scene_panels(cv, t):
    """F-04  Vier Comic-Felder (67.8-77.8)"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    fns = [panel_contracts, panel_cars, panel_food, panel_never]
    starts = [0.0, 2.4, 4.4, 6.2]
    for i, (px, py, pw, ph) in enumerate(PANELS):
        p = prog(t, starts[i], starts[i] + .45)
        if p <= 0:
            continue
        sc = eback(p)
        cv.save()
        cv.translate(px + pw / 2, py + ph / 2)
        cv.scale(sc, sc)
        cv.translate(-pw / 2, -ph / 2)
        cv.save()
        cv.clipRect(skia.Rect.MakeWH(pw, ph), doAntiAlias=True)
        G.zoom = 1.0
        fns[i](cv, pw, ph, t - starts[i] + 2.0)
        if i < 3 and t > starts[i + 1]:
            cv.drawPaint(skia.Paint(Color=col(BG, .35 * eout(prog(t, starts[i + 1], starts[i + 1] + .4)))))
        cv.restore()
        cv.drawRect(skia.Rect.MakeWH(pw, ph), P_ink(10, BONE, 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(-6, -6, pw + 12, ph + 12), P_ink(3, INK, 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(6, 6, pw - 12, ph - 12), P_ink(3, INK, 1, False))
        cv.restore()


# ---------------------------------------------------------------- Zeitungen (F-05)
def fit_font(tf, s, maxw, size):
    f = skia.Font(tf, size)
    while f.measureText(s) > maxw and size > 10:
        size -= 2
        f = skia.Font(tf, size)
    return f


def draw_paper(cv, w, h, kind, t):
    rr = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    cv.drawRect(rr, P_fill(PAPER, 1, False))
    rnd = random.Random(hash(kind) % 1000)

    def bars(y0, n, x0=-w / 2 + 26, ww=w - 52):
        for i in range(n):
            lw = ww * rnd.uniform(.45, .95)
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x0, y0 + i * 26, lw, 11), 5.5, 5.5), P_fill(PAPER_SH, 1, False))
            cv.drawCircle(x0 + lw + 16, y0 + i * 26 + 5.5, 5, P_fill(PAPER_SH, 1, False))

    def headline(lines, y0, colr=INK, band=None):
        y = y0
        for ln in lines:
            f = fit_font(TF_HEAD, ln, w - 60, 64)
            tw = f.measureText(ln)
            if band:
                pass
            cv.drawTextBlob(skia.TextBlob.MakeFromString(ln, f), -tw / 2, y, P_fill(colr, 1, False))
            y += f.getSize() * 1.05
        return y
    if kind == 'profits':
        y = headline(['RECORD', 'PROFITS'], -h / 2 + 80)
        cx0, cy0, cw, ch = -w / 2 + 40, y + 10, w - 80, 170
        cv.drawRect(skia.Rect.MakeXYWH(cx0, cy0, cw, ch), P_fill('#bdbcb0', 1, False))
        pts = [(cx0 + cw * i / 8, cy0 + ch - ch * (.1 + .85 * (i / 8) ** 1.6) + (8 if i % 2 else -6)) for i in range(9)]
        area = poly(pts + [(cx0 + cw, cy0 + ch), (cx0, cy0 + ch)])
        cv.drawPath(area, P_fill(GOLD, .55, False))
        cv.drawPath(poly(pts, close=False), P_ink(6, GOLD_DK, 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(cx0, cy0, cw, ch), P_ink(3, INK, 1, False))
        bars(cy0 + ch + 26, 6)
    elif kind == 'markets':
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 + 30, w, 150), P_fill('#2a2d2c', 1, False))
        headline(['MARKETS AT', 'ALL-TIME HIGH'], -h / 2 + 96, BONE_HI)
        for r_ in range(3):
            for c_ in range(7):
                cv.drawCircle(-w / 2 + 40 + c_ * 26, -h / 2 + 220 + r_ * 26, 8, P_fill('#5c5d56', 1, False))
        for k, rr_ in enumerate((90, 66, 40)):
            cv.drawCircle(w / 2 - 110, -h / 2 + 250, rr_, P_fill((GOLD_DK, GOLD, GOLD_HI)[k], 1, False))
        bars(-h / 2 + 330, 7)
    elif kind == 'eden':
        y = headline(['EDEN:', '"WORK IS OPTIONAL"'], -h / 2 + 76)
        cv.drawCircle(0, y + 80, 74, P_fill(GOLD, 1, False))
        cv.drawCircle(0, y + 80, 74, P_ink(4, INK, 1, False))
        for pth in face_paths(0, y + 92, 300):
            cv.drawPath(pth, P_ink(6, VISOR, 1, False))
        bars(y + 180, 6)
    elif kind == 'shares':
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2 + 26, w, 64), P_fill(RED, 1, False))
        f = fit_font(TF_HEAD, 'EDEN SHARES', w - 60, 46)
        tw = f.measureText('EDEN SHARES')
        cv.drawTextBlob(skia.TextBlob.MakeFromString('EDEN SHARES', f), -tw / 2, -h / 2 + 74, P_fill(BONE_HI, 1, False))
        big = '+312%'
        f2 = fit_font(TF_HEAD, big, w - 50, 150)
        tw = f2.measureText(big)
        gp = P_fill(GOLD_HI, .5, False)
        gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        cv.drawTextBlob(skia.TextBlob.MakeFromString(big, f2), -tw / 2, -h / 2 + 250, gp)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(big, f2), -tw / 2, -h / 2 + 250, P_fill(GOLD_DK, 1, False))
        ar = poly([(w / 2 - 70, -h / 2 + 300), (w / 2 - 40, -h / 2 + 350), (w / 2 - 100, -h / 2 + 350)])
        cv.drawPath(ar, P_fill(GOLD, 1, False))
        bars(-h / 2 + 300, 6, ww=w - 150)
    cv.drawRect(rr, P_ink(3.5, INK, 1, False))


PAPERS = [  # kind, cx, cy, w, h, rot, t_in, from (dx, dy)
    ('markets', 520, 430, 430, 600, -10, 0.0, (-900, -300)),
    ('eden', 1420, 470, 420, 560, 8, 0.5, (900, -400)),
    ('profits', 930, 560, 450, 620, 3, 1.2, (0, -1000)),
    ('shares', 1240, 640, 440, 520, -6, 3.0, (700, 700)),
]


def scene_papers(cv, t):
    """F-05  Zeitungen auf hellem Tisch (77.8-84.0)"""
    cv.drawPaint(P_fill('#9b9e93', 1, False))
    for gx in range(0, W, 28):
        for gy in range(0, H, 28):
            r = 3 * (.5 + .5 * math.sin(gx * .004 + gy * .006))
            if r > .6:
                cv.drawCircle(gx, gy, r, P_fill('#8e9187', 1, False))
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.08, eio(t / 6.2)))
    G.zoom = 1.0
    for (kind, cx, cy, w, h, rot, t0, (dx, dy)) in PAPERS:
        p = prog(t, t0, t0 + .7)
        if p <= 0:
            continue
        e = eout(p)
        x, y = cx + dx * (1 - e), cy + dy * (1 - e)
        rr = rot + 25 * (1 - e) * (1 if dx >= 0 else -1)
        cv.save()
        cv.translate(x + 14, y + 18)
        cv.rotate(rr)
        sh = skia.Paint(AntiAlias=True, Color=col('#000000', .3))
        sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
        cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), sh)
        cv.restore()
        cv.save()
        cv.translate(x, y)
        cv.rotate(rr)
        draw_paper(cv, w, h, kind, t)
        cv.restore()
        if kind == 'shares':
            hp = eout(prog(t, t0, t0 + .7)) * (1 - ein(prog(t, t0 + 1.4, t0 + 2.2)))
            if hp > 0:
                hx = lerp(2300, x + w * .42, hp)
                hy = lerp(1300, y + h * .36, hp)
                cv.save()
                cv.translate(hx, hy)
                cv.rotate(-35)
                draw_reach_hand(cv, 120, 0, 1.0, grip=.25)
                cv.restore()
    cv.restore()


# ---------------------------------------------------------------- Raster: jeder Vierte (F-06)
_rnd = random.Random(4)
DIM_ORDER = _rnd.sample(range(40), 10)


def draw_person(cv, x, y, s, dim=0.0, bob=0.0, a=1.0):
    fill = mix(BONE, '#3c3e3b', dim)
    sl = 1 - .22 * dim
    cv.save()
    cv.translate(x, y + bob)
    cv.scale(s, s)
    body = skia.Path()
    body.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-30, -100 * sl, 60, 100 * sl), 28, 28))
    cv.drawPath(body, P_fill(fill, a))
    cv.drawPath(body, P_ink(3.5 / s, INK, a))
    hx, hy = 8 * dim, -100 * sl - 30 + 14 * dim
    head = circle(hx, hy, 24)
    cv.drawPath(head, P_fill(fill, a))
    cv.drawPath(head, P_ink(3.5 / s, INK, a))
    cv.restore()


def scene_grid(cv, t):
    """F-06  Jeder Vierte ohne Arbeit (84.0-87.8)"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.drawRect(skia.Rect.MakeXYWH(0, 0, W, 300), P_glow(GOLD_HI, 120, .08))
    cv.save()
    cam(cv, 960, 560, lerp(1.04, 1.0, eio(t / 3.8)))
    for i in range(40):
        row, c_ = i // 10, i % 10
        x = 250 + c_ * 158 + (40 if row % 2 else 0)
        y = 400 + row * 160
        d = 0.0
        if i in DIM_ORDER:
            k = DIM_ORDER.index(i)
            d = eio(prog(t, .5 + k * .11, .9 + k * .11))
        bob = 3 * math.sin(t * 3 + i) * (1 - d)
        draw_person(cv, x, y, .9, d, bob)
    cv.restore()
    a = eout(prog(t, 1.9, 2.4))
    if a > 0:
        f = skia.Font(TF_HEAD, 110)
        s1, s2 = '1', ' IN 4'
        tw = f.measureText(s1 + s2)
        x0 = (W - tw) / 2
        cv.drawTextBlob(skia.TextBlob.MakeFromString(s1, f), x0, 170, P_fill(GOLD, a, False))
        cv.drawTextBlob(skia.TextBlob.MakeFromString(s2, f), x0 + f.measureText(s1), 170, P_fill(BONE_HI, a, False))


# ---------------------------------------------------------------- Autosalon (F-07)
CARS = [(560, '#8c3b30', '$ 39,990'), (1240, BONE, '$ 52,500'), (1920, '#4b6278', '$ 28,900')]


def scene_showroom(cv, t):
    """F-07  Der volle Autosalon, niemand kommt (87.8-96.4)"""
    cv.drawPaint(P_fill('#1e201f', 1, False))
    cv.save()
    cam(cv, lerp(1000, 1600, eio(t / 8.6)), 540, 1.0)
    G.zoom = 1.0
    cv.drawRect(skia.Rect.MakeLTRB(-200, -100, 2800, 700), P_fill('#232524', 1, False))
    wl, wt, wr, wb = 160, 110, 2270, 600
    cv.save()
    cv.clipRect(skia.Rect.MakeLTRB(wl, wt, wr, wb))
    cv.drawImage(BG_NIGHT, wl, wt - 200)
    cv.drawImage(BG_NIGHT, wl + W, wt - 200)
    cv.drawRect(skia.Rect.MakeLTRB(wl, 540, wr, wb), P_fill('#181a19', 1, False))
    fx0, fx1, ft = 820, 1720, 420
    fac = skia.Path()
    fac.moveTo(fx0, 545)
    fac.lineTo(fx0, ft)
    n = 6
    for i in range(n):
        xa = fx0 + (fx1 - fx0) * i / n
        fac.lineTo(xa + (fx1 - fx0) / n * .7, ft - 60)
        fac.lineTo(xa + (fx1 - fx0) / n, ft)
    fac.lineTo(fx1, 545)
    fac.close()
    cv.drawRect(skia.Rect.MakeLTRB(fx0 - 40, ft - 120, fx1 + 40, 545), P_glow(GOLD_HI, 50, .25))
    cv.drawPath(fac, P_fill('#2a2a26', 1, False))
    cv.drawPath(fac, P_ink(3, INK, 1, False))
    for i in range(16):
        cv.drawRect(skia.Rect.MakeXYWH(fx0 + 30 + i * 55, ft + 30, 34, 60), P_fill(GOLD, .7 + .3 * math.sin(t * 3 + i), False))
    draw_eden_bot(cv, 2010, 560, 380, 64, t, face=1.0, glow=.8)
    cv.drawRect(skia.Rect.MakeLTRB(wl, wt, wr, wb), P_fill(BG, .12, False))
    for k in range(5):
        x = wl + 200 + k * 460
        cv.drawPath(poly([(x, wt), (x + 120, wt), (x - 200, wb), (x - 320, wb)]), P_fill(BONE, .045, False))
    cv.restore()
    for x in range(wl, wr + 1, 527):
        cv.drawRect(skia.Rect.MakeXYWH(x - 14, wt - 10, 28, wb - wt + 20), P_fill('#2c2e2c', 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(x - 14, wt - 10, 28, wb - wt + 20), P_ink(3, INK, 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(wl, wt, wr, wb), P_ink(16, '#2c2e2c', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(wl - 8, wt - 8, wr + 8, wb + 8), P_ink(3, INK, 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(-200, 700, 2800, 1300), P_fill('#191a19', 1, False))
    cv.drawLine(-200, 700, 2800, 700, P_ink(4, INK, 1, False))
    for k in range(9):
        cv.drawLine(-200, 740 + k * k * 9, 2800, 740 + k * k * 9, P_ink(2, '#232523', 1, False))
    offs = [prog(t, 6.6 + k * .45, 6.7 + k * .45) for k in range(3)]
    for (k, (cx, colr, price)) in enumerate(CARS):
        on = 1 - offs[k]
        flick = 1.0 if on >= 1 else (on * (.5 + .5 * math.sin(t * 60)))
        gy = 860
        cv.save()
        cv.translate(0, 2 * gy - 10)
        cv.scale(1, -1)
        cv.save()
        cv.clipRect(skia.Rect.MakeLTRB(-200, gy - 10, 2800, gy + 400))
        draw_car(cv, cx - 200, gy, 400, colr, .14 + .1 * flick)
        cv.restore()
        cv.restore()
        cv.drawOval(skia.Rect.MakeXYWH(cx - 260, gy - 22, 520, 50), P_fill('#2b2c2a', 1, False))
        cv.drawOval(skia.Rect.MakeXYWH(cx - 260, gy - 22, 520, 50), P_ink(3, INK, 1, False))
        draw_car(cv, cx - 200, gy, 400, colr)
        cv.drawOval(skia.Rect.MakeXYWH(cx - 280, gy - 30, 560, 64), P_glow(BONE_HI, 20, .12 * flick))
        draw_cone(cv, cx, -60, 40, cx, gy, 280, BONE_HI, .55 * flick)
        cv.drawRect(skia.Rect.MakeXYWH(cx - 30, -80, 60, 30), P_fill('#2c2e2c', 1, False))
        sx_ = cx + 250
        cv.drawLine(sx_, gy + 20, sx_, gy - 150, P_ink(8, INK, 1, False))
        cv.drawLine(sx_, gy + 20, sx_, gy - 150, P_ink(4, '#5a5a55', 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(sx_ - 70, gy - 230, 140, 80), P_fill(BONE, 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(sx_ - 70, gy - 230, 140, 80), P_ink(3, INK, 1, False))
        f = skia.Font(TF_HEAD, 30)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(price, f), sx_ - f.measureText(price) / 2, gy - 180,
                        P_fill(INK, 1, False))
    dx = 2330
    cv.drawRect(skia.Rect.MakeXYWH(dx, 300, 220, 400), P_fill('#141515', 1, False))
    cv.drawRect(skia.Rect.MakeXYWH(dx, 300, 220, 400), P_ink(10, '#2c2e2c', 1, False))
    sw = 6 * math.sin(t * 2.2)
    cv.save()
    cv.translate(dx + 110, 380)
    cv.rotate(sw)
    cv.drawLine(-40, -30, 0, -60, P_ink(2.5, '#5a5a55', 1, False))
    cv.drawLine(40, -30, 0, -60, P_ink(2.5, '#5a5a55', 1, False))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-70, -30, 140, 56), 6, 6), P_fill(RED, 1, False))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-70, -30, 140, 56), 6, 6), P_ink(3, INK, 1, False))
    f = skia.Font(TF_HEAD, 34)
    cv.drawTextBlob(skia.TextBlob.MakeFromString('OPEN', f), -f.measureText('OPEN') / 2, 12, P_fill(BONE_HI, 1, False))
    cv.restore()
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', .35 * prog(t, 7.6, 8.6))))


# ---------------------------------------------------------------- Riss im Apfel (F-08 bis F-10)
def crack_points(r):
    rnd = random.Random(19)
    pts = [(0, -r * .62)]
    y = -r * .62
    x = 0
    while y < r * .95:
        y += r * rnd.uniform(.1, .17)
        x = clamp(x + r * rnd.uniform(-.13, .13), -r * .2, r * .2)
        pts.append((x, min(y, r * .97)))
    pts[-1] = (pts[-1][0], r * 1.2)
    return pts


def crack_branches(r, main):
    rnd = random.Random(23)
    out = []
    for n_, i in enumerate((2, 4, 6)):
        if i >= len(main):
            continue
        x, y = main[i]
        side = 1 if n_ % 2 == 0 else -1
        bp = [(x, y)]
        dy = rnd.choice([-1, 1])
        for k in range(4):
            x += side * r * rnd.uniform(.08, .13)
            y += r * (dy * rnd.uniform(.04, .1) if k % 2 == 0 else -dy * rnd.uniform(.0, .05))
            bp.append((x, y))
        out.append(bp)
    return out


def draw_apple_with_city(cv, r, t, glow=True):
    draw_apple(cv, 0, 0, r, 'gold', glow=(1.0 + .25 * math.sin(t * 3.5)) if glow else 0.0, t=t, circuit=.25)
    cv.save()
    cv.clipPath(apple_path(r * .88), doAntiAlias=True)
    back, front = CITY
    cv.save()
    cv.translate(-r, r * .55)
    sc = 2 * r / W
    cv.scale(sc, sc)
    for (x, w_, h_, k) in back[::2]:
        cv.drawRect(skia.Rect.MakeLTRB(x, -h_ * .9, x + w_, 600), P_fill(GOLD_DK, .55, False))
    draw_eden_bot(cv, 1240, 100, 820, 160, t, face=1.0, glow=.5)
    for (x, w_, h_, k) in front:
        cv.drawRect(skia.Rect.MakeLTRB(x, -h_ * .55, x + w_, 600), P_fill('#7a5d2c', .8, False))
    cv.restore()
    cv.restore()


def draw_slip(cv, cx, cy, sc, rot, t, typed1, typed2, a=1.0):
    w, h = 760, 300
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(rot)
    cv.scale(sc, sc)
    rnd = random.Random(31)
    pts = []
    for i in range(21):
        pts.append((-w / 2 + w * i / 20, -h / 2 + rnd.uniform(-5, 5)))
    for i in range(11):
        pts.append((w / 2 + rnd.uniform(-8, 3), -h / 2 + h * i / 10))
    for i in range(21):
        pts.append((w / 2 - w * i / 20, h / 2 + rnd.uniform(-5, 5)))
    for i in range(11):
        pts.append((-w / 2 + rnd.uniform(-3, 8), h / 2 - h * i / 10))
    sp = poly(pts)
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .4 * a))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    cv.save()
    cv.translate(12, 16)
    cv.drawPath(sp, sh)
    cv.restore()
    cv.drawPath(sp, P_fill(SLIP, a, False))
    for (sx, sy, sr) in ((-220, 60, 70), (250, -60, 50)):
        cv.drawCircle(sx, sy, sr, P_fill('#b9a77f', .25 * a, False))
    cv.drawPath(sp, P_ink(3, INK, a, False))
    f1 = skia.Font(TF_TYPE, 30)
    h1 = 'CLEVELAND, OHIO  -  1950s'
    cv.drawTextBlob(skia.TextBlob.MakeFromString(h1[:int(len(h1) * typed1)], f1), -w / 2 + 50, -h / 2 + 64, P_fill('#5b4a36', a, False))
    cv.drawLine(-w / 2 + 50, -h / 2 + 82, -w / 2 + 50 + 400 * typed1, -h / 2 + 82, P_ink(2, '#5b4a36', .6 * a, False))
    f2 = skia.Font(TF_TYPE, 48)
    q = ['"How are you going to get', 'them to buy cars?"']
    total = sum(len(s) for s in q)
    n = int(total * typed2)
    y = -h / 2 + 160
    for ln in q:
        k = min(len(ln), n)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ln[:k], f2), -w / 2 + 50, y, P_fill('#1f1a14', a, False))
        n -= k
        y += 62
    cv.restore()


def scene_crack(cv, t):
    """F-08 bis F-10  Riss im Apfel, Zettel aus den 1950ern (96.4-122.8)"""
    cv.drawImage(BG_NIGHT2, 0, 0)
    cv.save()
    push = eio(prog(t, 22.4, 25.6))
    slip_x, slip_y = 1180, 560
    cx = lerp(960, slip_x, push)
    cy = lerp(540, slip_y, push)
    cam(cv, cx, cy, lerp(1.06, 2.3, push))
    ax, ay, r = 1520, 470, 190
    main = crack_points(r)
    branches = crack_branches(r, main)
    cp = eio(prog(t, 10.8, 13.0))
    bp = eio(prog(t, 13.2, 16.8))
    split = eio(prog(t, 17.6, 18.8))
    if split <= 0:
        cv.save()
        cv.translate(ax, ay + 8 * math.sin(t * 1.2))
        G.zoom = 1.06
        draw_apple_with_city(cv, r, t)
        if cp > 0:
            cv.save()
            cv.clipPath(apple_path(r * 1.0), doAntiAlias=True)
            mp = trim(poly(main, close=False), cp)
            lg = P_ink(6 + 18 * bp, GOLD_HI, .5 + .4 * bp, wobble=False)
            lg.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8 + 10 * bp))
            cv.drawPath(mp, lg)
            cv.drawPath(mp, P_ink(7, INK, 1, wobble=False))
            cv.drawPath(mp, P_ink(2 + 3 * bp, '#fff3d0', .9 * bp, wobble=False))
            for b in branches:
                bpth = trim(poly(b, close=False), bp)
                cv.drawPath(bpth, lg)
                cv.drawPath(bpth, P_ink(5, INK, 1, wobble=False))
                cv.drawPath(bpth, P_ink(1.5 + 2 * bp, '#fff3d0', .9 * bp, wobble=False))
            cv.restore()
        cv.restore()
        for (k, t0) in enumerate((15.4, 16.1, 16.7)):
            if t > t0:
                tt = t - t0
                x = ax + (30 - k * 25) + 60 * tt
                y = ay - 60 + k * 60 + 300 * tt * tt
                cv.drawPath(poly([(x, y), (x + 18, y + 6), (x + 6, y + 20)]), P_fill(GOLD, 1 - prog(tt, .8, 1.4), False))
    else:
        left = poly(main + [(-r * 3, r * 3), (-r * 3, -r * 3), (0, -r * 3)])
        right = poly(main + [(r * 3, r * 3), (r * 3, -r * 3), (0, -r * 3)])
        cv.drawCircle(ax, ay, 300, P_glow(GOLD_HI, 110, .35))
        burst = P_glow(GOLD_HI, 60, .6 * (1 - prog(t, 18.0, 20.0)))
        cv.drawCircle(ax, ay, 220, burst)
        for (reg, sx) in ((left, -1), (right, 1)):
            cv.save()
            cv.translate(ax + sx * 160 * split, ay + 40 * split)
            cv.rotate(sx * 14 * split)
            cv.clipPath(reg, doAntiAlias=True)
            G.zoom = 1.06
            draw_apple_with_city(cv, r, t, glow=False)
            cv.drawPath(poly(main, close=False), P_ink(7, INK, 1, wobble=False))
            cv.restore()
    n = 60
    pts = []
    for i in range(n):
        u = i / (n - 1)
        x = lerp(-200, 610, u)
        y = 980 - 420 * math.sin(u * math.pi * .55) + 30 * math.sin(t * 1.2 + u * 3)
        pts.append((x, y, 1.0))
    widths = [lerp(230, 190, i / (n - 1)) for i in range(n)]
    G.zoom = 1.06
    draw_snake_run(cv, pts, widths, 5, front=True)
    hx, hy = pts[-1][:2]
    lid = .3
    if 7.8 < t < 10.8:
        lid = .3 + .3 * eout(prog(t, 7.8, 8.3))
    if t >= 10.8:
        lid = lerp(.6, 0.0, eout(prog(t, 10.8, 11.2)))
    pupil = lerp(1.0, .6, eout(prog(t, 10.8, 11.2)))
    look = eio(prog(t, 18.6, 19.6))
    ang = head_angle(pts) - 8 + lerp(0, 6, look)
    tongue = max(prog(t, 3.0, 3.5), prog(t, 19.8, 20.3))
    draw_head(cv, hx, hy, ang, 190 * .95, lid=lid, tongue=tongue, gold_rim=.6 + .3 * math.sin(t * 3.5), pupil=pupil)
    if split > 0:
        sp = eout(prog(t, 18.0, 19.4))
        sx = lerp(ax, slip_x, sp)
        sy = lerp(ay, slip_y, sp)
        draw_slip(cv, sx, sy, lerp(.15, 1.0, sp), lerp(20, -3, sp), t, prog(t, 18.8, 19.8), prog(t, 19.6, 22.2), min(1, sp * 3))
    cv.restore()
    la = eout(prog(t, .4, 1.0)) * (1 - prog(t, 17.0, 17.6))
    if la > 0:
        cv.drawLine(80, 92, 80 + 70 * la, 92, P_ink(2.5, GOLD, la, False))
        draw_text(cv, 'FICTION', 170, 102, TF_CAPS, 28, P_fill(GOLD, la, False), spacing=9)
    cv.drawPaint(skia.Paint(Color=col('#000000', prog(t, 25.2, 26.4))))


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
    (53.0, 54.4, scene_zoomapple),
    (54.4, 61.0, scene_city),
    (61.0, 67.8, scene_eden_close),
    (67.8, 77.8, scene_panels),
    (77.8, 84.0, scene_papers),
    (84.0, 87.8, scene_grid),
    (87.8, 96.4, scene_showroom),
    (96.4, 122.8, scene_crack),
    (122.8, 130.0, scene_title),
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
    (53.4, 55.8, 'Let me show you what that looks like.'),
    (56.4, 60.8, 'Picture a city, some years from now. And behind it, something new.'),
    (61.2, 63.6, 'Its makers call it EDEN.'),
    (63.8, 67.4, 'It can do almost any job a human can do, only cheaper.'),
    (68.0, 70.1, 'It writes the contracts.'),
    (70.2, 72.1, 'It builds the cars.'),
    (72.2, 73.9, 'It cooks the food.'),
    (74.0, 77.6, 'It never sleeps, and it never asks for a raise.'),
    (78.0, 80.4, 'Its owners have never been richer.'),
    (80.6, 83.6, 'The stock market breaks record after record.'),
    (84.2, 87.4, 'And one in four people has no job.'),
    (88.0, 91.6, 'Somewhere, a factory builds cars day and night without a single worker.'),
    (91.8, 93.8, 'The showroom is full.'),
    (94.0, 96.0, 'Nobody comes.'),
    (96.8, 99.6, 'This is a story, not a prediction.'),
    (99.8, 103.6, 'But every step of it follows from how our economy actually works.'),
    (104.2, 107.0, 'Most videos about AI end here, at the nightmare.'),
    (107.2, 109.4, 'But this picture has a flaw.'),
    (109.6, 113.4, "A world like this can't stay this way. Something has to break."),
    (114.0, 118.6, 'And the reason is hidden in a question a union leader asked in the 1950s.'),
    (118.8, 122.4, 'To understand it, we have to go back to the first apple.'),
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
        from scipy.ndimage import gaussian_filter, zoom
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
        vig = np.clip(1.0 - .32 * d ** 2.2, .55, 1.0)
        rng = np.random.default_rng(7)
        low = gaussian_filter(rng.normal(0, 1, (H // 4, W // 4)), 10)
        low = zoom(low, 4, order=1)[:H, :W]
        low /= np.abs(low).max()
        fib = gaussian_filter(rng.normal(0, 1, (H, W)), .9)
        fib /= np.abs(fib).max()
        tex = 1 + .05 * low + .025 * fib
        self.fac = (vig * tex * 256).astype(np.uint16)[:, :, None]
        rng = np.random.default_rng(1)
        self.noise = [rng.normal(0, 5.0, (H, W)).astype(np.int16)[:, :, None] for _ in range(6)]

    def apply(self, rgba, frame):
        rgb = rgba[:, :, :3].astype(np.uint16)
        rgb = (rgb * self.fac) >> 8
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
