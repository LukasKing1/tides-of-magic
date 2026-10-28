#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Maskottchen, dritte Runde: neue Schlange im flachen, warmen Stil.

Koerper als glatte Roehre (Vereinigung verjuengter Kapseln) statt versetzter Polygone,
damit Hals, Windung und Schwanz keine Knicke oder Bruchstellen bekommen.

python3 mascot3.py sheet <out.png>
"""
import math, sys
import skia
from rich_base import *

# ---------------------------------------------------------------- Palette (warm, gedaempft)
LINE = '#1b1412'
BG3 = '#231b19'
SN = '#7f9b60'
SN_RIM = '#a6bf80'
SN_SH = '#66804b'
SN_SPOT = '#5c7544'
SN_BELLY = '#ead9ae'
SN_BELLY_SH = '#d3bf8e'
BROW = '#40542f'
JK = '#3a3f3c'
JK_RIM = '#555d58'
JK_SH = '#2b2f2d'
SHIRT3 = '#e8e0cf'
TIE = '#a2463a'
TIE_SH = '#83372e'
TONGUE = '#c9645a'
BLUSH = '#d9866f'
LW = 2.6  # Konturbreite in Bildschirmpixeln
TF_DISPLAY = skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', 'PlayfairDisplay_900Black_Italic.ttf'))


def ink(cv, px=LW, a=1.0):
    return inkp(cv, px, LINE, a)


# ---------------------------------------------------------------- Geometrie
def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        u = i / n
        out.append(((1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0],
                    (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]))
    return out


def tube(pts, radii):
    """Glatte Roehre: Umriss aus beiden Randkurven plus runden Enden, Selbstueberschneidungen per Simplify aufgeloest."""
    n = len(pts)
    left, right = [], []
    for i in range(n):
        x0, y0 = pts[max(0, i - 1)]
        x1, y1 = pts[min(n - 1, i + 1)]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        r = radii[i]
        left.append((pts[i][0] + nx * r, pts[i][1] + ny * r))
        right.append((pts[i][0] - nx * r, pts[i][1] - ny * r))
    outline = poly(left + right[::-1])
    b = skia.OpBuilder()
    b.add(skia.Simplify(outline) or outline, skia.PathOp.kUnion_PathOp)
    for i in range(n):
        tight = False
        if 0 < i < n - 1:
            (ax, ay), (bx, by), (cx, cy) = pts[i - 1], pts[i], pts[i + 1]
            ab, bc, ca = math.hypot(bx - ax, by - ay), math.hypot(cx - bx, cy - by), math.hypot(ax - cx, ay - cy)
            cross = abs((bx - ax) * (cy - ay) - (by - ay) * (cx - ax))
            tight = cross > 1e-9 and ab * bc * ca / (2 * cross) < radii[i] * 1.15
        if i in (0, n - 1) or tight:
            c = skia.Path()
            c.addCircle(pts[i][0], pts[i][1], radii[i])
            b.add(c, skia.PathOp.kUnion_PathOp)
    out = b.resolve()
    out.setFillType(skia.PathFillType.kWinding)
    return out


def shifted(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return q


def minus(a, b):
    return skia.Op(a, b, skia.PathOp.kDifference_PathOp)


def shade_and_rim(cv, path, shade_col, rim_col, d, a=1.0, rim_d=None):
    """Flacher Stil: ein Schattenband unten rechts, ein Lichtband oben links."""
    cv.drawPath(minus(path, shifted(path, -d, -d)), fillp(cv, shade_col, a, False))
    rd = rim_d or d * .8
    cv.drawPath(minus(path, shifted(path, rd, rd)), fillp(cv, rim_col, a, False))


def ghost(cv, path, a=1.0):
    """Versetzter dunkler Schattenumriss hinter der Figur."""
    p = skia.Paint(AntiAlias=True, Color=col('#000000', .42 * a))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3.0))
    s = mscale(cv)
    cv.drawPath(shifted(path, -12 / s, -9 / s), p)


# ---------------------------------------------------------------- Koerper
def body_spine():
    neck = bez((0.0, 0.25), (0.0, 0.95), (0.55, 1.15), (0.55, 1.98), 40)
    rad = [lerp(0.25, 0.28, i / 40) for i in range(41)]
    cx, cy, rx, ry = -0.47, 1.98, 1.02, 0.40
    n = 130
    pts = list(neck)
    for i in range(1, n + 1):
        u = i / n
        th = math.radians(lerp(0, 296, u))
        pts.append((cx + rx * math.cos(th), cy + ry * math.sin(th)))
        rad.append(0.28 if u < .40 else lerp(0.28, 0.03, ((u - .40) / .60) ** 1.2))
    belly_w = [0.0] * 41 + [min(1.0, i / 14) for i in range(1, n + 1)]
    return pts, rad, belly_w


def draw_body(cv, a=1.0, shadow=True):
    pts, rad, bw = body_spine()
    body = tube(pts, rad)
    if shadow:
        ghost(cv, body, a)
    cv.drawPath(body, fillp(cv, SN, a))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    cv.drawPath(minus(body, shifted(body, -0.05, -0.05)), fillp(cv, SN_SH, a, False))
    bpts = [(x + .22 * r * (1 - w), y + .6 * r * w) for (x, y), r, w in zip(pts, rad, bw)]
    brad = [r * lerp(.32, .40, w) for r, w in zip(rad, bw)]
    belly = tube(bpts, brad)
    cv.drawPath(belly, fillp(cv, SN_BELLY, a, False))
    cv.drawPath(minus(belly, shifted(belly, -0.03, -0.03)), fillp(cv, SN_BELLY_SH, a, False))
    cv.save()
    cv.clipPath(belly, doAntiAlias=True)
    acc = 0.0
    for i in range(1, len(pts) - 1):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc > 0.085:
            acc = 0.0
            (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0) or 1
            nx, ny = -(y1 - y0) / L, (x1 - x0) / L
            bx, by = bpts[i]
            r = brad[i]
            cv.drawLine(bx - nx * r, by - ny * r, bx + nx * r, by + ny * r, strokep(cv, 1.6 / mscale(cv), SN_BELLY_SH, .9 * a))
    cv.restore()
    acc = 0.0
    for i in range(1, len(pts) - 6):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc > 0.30 and bw[i] > .5:
            acc = 0.0
            (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
            ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
            cv.save()
            cv.translate(pts[i][0], pts[i][1] - .38 * rad[i])
            cv.rotate(ang)
            cv.drawOval(skia.Rect.MakeXYWH(-.075 * rad[i] / .27, -.04 * rad[i] / .27, .15 * rad[i] / .27, .08 * rad[i] / .27),
                        fillp(cv, SN_SPOT, a, False))
            cv.restore()
    cv.drawPath(minus(body, shifted(body, 0.035, 0.035)), fillp(cv, SN_RIM, .9 * a, False))
    cv.restore()
    cv.drawPath(body, ink(cv, LW, a))


def draw_collar(cv, a=1.0):
    """Hemdkragen und Krawatte direkt am Hals."""
    band = poly([(-0.27, 0.42), (0.27, 0.42), (0.27, 0.52), (-0.27, 0.52)])
    cv.drawPath(band, fillp(cv, SHIRT3, a))
    cv.drawPath(minus(band, shifted(band, -0.02, -0.02)), fillp(cv, '#cfc6b2', a, False))
    cv.drawPath(band, ink(cv, LW * .85, a))
    blade = poly([(-0.045, 0.56), (0.045, 0.56), (0.095, 0.92), (0.0, 1.02), (-0.095, 0.92)])
    knot = poly([(-0.06, 0.47), (0.06, 0.47), (0.045, 0.57), (-0.045, 0.57)])
    for p_, c_ in ((blade, TIE), (knot, TIE_SH)):
        cv.drawPath(p_, fillp(cv, c_, a))
        cv.drawPath(p_, ink(cv, LW * .85, a))
    cv.drawPath(poly([(0.0, 0.64), (0.06, 0.88)], close=False), strokep(cv, 1.5 / mscale(cv), TIE_SH, .8 * a))
    for sx in (-1, 1):
        wing = poly([(sx * 0.27, 0.42), (sx * 0.03, 0.46), (sx * 0.20, 0.62)])
        cv.drawPath(wing, fillp(cv, SHIRT3, a))
        cv.drawPath(wing, ink(cv, LW * .85, a))


def jacket_path():
    j = skia.Path()
    j.moveTo(-0.27, 0.40)
    j.cubicTo(-0.50, 0.46, -0.66, 0.70, -0.68, 1.05)
    j.lineTo(-0.70, 1.62)
    j.cubicTo(-0.40, 1.76, 0.40, 1.76, 0.70, 1.62)
    j.lineTo(0.68, 1.05)
    j.cubicTo(0.66, 0.70, 0.50, 0.46, 0.27, 0.40)
    j.close()
    return j


def draw_jacket(cv, a=1.0, shadow=True):
    j = jacket_path()
    if shadow:
        ghost(cv, j, a)
    cv.drawPath(j, fillp(cv, JK, a))
    cv.save()
    cv.clipPath(j, doAntiAlias=True)
    shade_and_rim(cv, j, JK_SH, JK_RIM, 0.06, a, 0.035)
    cv.restore()
    cv.drawPath(j, ink(cv, LW, a))
    shirt = poly([(-0.25, 0.41), (0.25, 0.41), (0.0, 1.04)])
    cv.drawPath(shirt, fillp(cv, SHIRT3, a))
    cv.drawPath(shirt, ink(cv, LW * .9, a))
    knot = poly([(-0.055, 0.49), (0.055, 0.49), (0.04, 0.57), (-0.04, 0.57)])
    blade = poly([(-0.04, 0.57), (0.04, 0.57), (0.085, 0.86), (0.0, 0.95), (-0.085, 0.86)])
    for p_, c_ in ((blade, TIE), (knot, TIE_SH)):
        cv.drawPath(p_, fillp(cv, c_, a))
        cv.drawPath(p_, ink(cv, LW * .85, a))
    for sx in (-1, 1):
        colr = poly([(sx * 0.27, 0.40), (sx * 0.03, 0.47), (sx * 0.17, 0.60)])
        cv.drawPath(colr, fillp(cv, SHIRT3, a))
        cv.drawPath(colr, ink(cv, LW * .85, a))
        lap = poly([(sx * 0.28, 0.40), (sx * 0.20, 0.45), (sx * 0.005, 1.05), (sx * 0.30, 0.86), (sx * 0.22, 0.74), (sx * 0.38, 0.64)])
        cv.drawPath(lap, fillp(cv, mix(JK, JK_RIM, .35), a))
        cv.drawPath(lap, ink(cv, LW * .9, a))
    cv.drawPath(poly([(0.005, 1.05), (0.02, 1.73)], close=False), ink(cv, LW * .9, a))
    for by in (1.22, 1.43):
        cv.drawCircle(0.075, by, 0.028, fillp(cv, LINE, a, False))
    cv.drawPath(poly([(-0.56, 0.98), (-0.34, 0.95)], close=False), ink(cv, LW * .8, a))
    sq = poly([(-0.53, 0.975), (-0.48, 0.90), (-0.44, 0.93), (-0.38, 0.89), (-0.37, 0.96)])
    cv.drawPath(sq, fillp(cv, GOLD, a))
    cv.drawPath(sq, ink(cv, LW * .7, a))


# ---------------------------------------------------------------- Kopf
HEAD3 = [(0.0, -0.50), (0.38, -0.52, 0.64, -0.40, 0.66, -0.14), (0.68, 0.10, 0.58, 0.36, 0.34, 0.46),
         (0.18, 0.52, -0.18, 0.52, -0.34, 0.46), (-0.58, 0.36, -0.68, 0.10, -0.66, -0.14),
         (-0.64, -0.40, -0.38, -0.52, 0.0, -0.50)]
EX, EY = 0.30, -0.15
GX, GY, GR = 0.32, -0.15, 0.28
JAW = {  # Kieferlinie: linkes Ende, Mitte, rechtes Ende (y), Kontrollhoehe
    'smile': (0.12, 0.30, 0.12), 'tongue': (0.12, 0.30, 0.12), 'smirk': (0.20, 0.25, 0.08), 'wavy': (0.20, 0.22, 0.20),
    'o': (0.16, 0.24, 0.16), 'flat': (0.18, 0.22, 0.18),
}


def jaw_curve(kind):
    l, m, r = JAW.get(kind, JAW['smile'])
    if kind == 'wavy':
        return P_([(-0.60, l), (-0.30, m + 0.04, -0.15, m - 0.05, 0.0, m), (0.15, m + 0.05, 0.30, m - 0.04, 0.60, r)], close=False)
    return P_([(-0.60, l), (-0.30, m + 0.06, 0.30, m + 0.06, 0.60, r)], close=False)


def lens(sx):
    return circle(sx * GX, GY, GR)


def eyes(cv, kind, look, a):
    lx, ly = look
    for sx in (-1, 1):
        ex, ey = sx * EX + lx * 0.04, EY + ly * 0.03
        if kind == 'closed':
            p = P_([(ex - 0.09, ey - 0.01), (ex - 0.05, ey + 0.06, ex + 0.05, ey + 0.06, ex + 0.09, ey - 0.01)], close=False)
            cv.drawPath(p, ink(cv, LW * 1.05, a))
        elif kind in ('dot', 'big', 'small'):
            w, h = {'dot': (0.085, 0.11), 'big': (0.105, 0.135), 'small': (0.07, 0.09)}[kind]
            cv.drawOval(skia.Rect.MakeXYWH(ex - w / 2, ey - h / 2, w, h), fillp(cv, LINE, a, False))
        elif kind == 'lidded':
            e = skia.Path()
            e.moveTo(ex - 0.05, ey - 0.01)
            e.lineTo(ex + 0.05, ey - 0.01)
            e.cubicTo(ex + 0.05, ey + 0.06, ex - 0.05, ey + 0.06, ex - 0.05, ey - 0.01)
            e.close()
            cv.drawPath(e, fillp(cv, LINE, a, False))
            cv.drawPath(poly([(ex - 0.085, ey - 0.005), (ex + 0.085, ey - 0.025)], close=False), ink(cv, LW, a))


def brows(cv, kind, a):
    p = strokep(cv, max(1.0, 3.2 / mscale(cv) * mscale(cv)) / mscale(cv), BROW, a)
    p.setStrokeWidth(0.03)
    for sx in (-1, 1):
        x = sx * EX
        if kind == 'soft':
            q = P_([(x - 0.08, -0.25), (x - 0.02, -0.28, x + 0.02, -0.28, x + 0.08, -0.25)], close=False)
        elif kind == 'worried':
            q = P_([(x - sx * 0.08, -0.23), (x + sx * 0.07, -0.29)], close=False)
        elif kind == 'high':
            q = P_([(x - 0.08, -0.29), (x - 0.02, -0.33, x + 0.02, -0.33, x + 0.08, -0.29)], close=False)
        elif kind == 'smug':
            q = (P_([(x - 0.08, -0.31), (x - 0.02, -0.35, x + 0.03, -0.34, x + 0.08, -0.29)], close=False) if sx > 0 else
                 P_([(x - 0.08, -0.22), (x + 0.08, -0.24)], close=False))
        else:
            continue
        cv.drawPath(q, p)


def mouth3(cv, kind, a):
    cv.drawPath(jaw_curve(kind), ink(cv, LW * 1.05, a))
    if kind == 'tongue':
        m = skia.Path()
        m.moveTo(-0.12, 0.33)
        m.cubicTo(-0.05, 0.355, 0.05, 0.355, 0.12, 0.33)
        m.cubicTo(0.09, 0.45, -0.09, 0.45, -0.12, 0.33)
        m.close()
        cv.drawPath(m, fillp(cv, '#5a2e28', a))
        cv.save()
        cv.clipPath(m, doAntiAlias=True)
        cv.drawOval(skia.Rect.MakeXYWH(-0.07, 0.37, 0.14, 0.10), fillp(cv, TONGUE, a, False))
        cv.restore()
        cv.drawPath(m, ink(cv, LW, a))
    elif kind == 'o':
        m = skia.Path()
        m.addOval(skia.Rect.MakeXYWH(-0.05, 0.27, 0.10, 0.12))
        cv.drawPath(m, fillp(cv, '#5a2e28', a))
        cv.drawPath(m, ink(cv, LW, a))
    for sx in (-1, 1):
        cv.drawPath(P_([(sx * 0.60, 0.12 if kind not in ('smirk',) or sx < 0 else 0.08), (sx * 0.64, 0.09)], close=False), ink(cv, LW, a))


def fork(cv, out, a):
    if out <= 0:
        return
    L = 0.16 * math.sin(math.pi * clamp(out))
    t = skia.Path()
    t.moveTo(0.0, 0.33)
    t.lineTo(0.0, 0.33 + L)
    t.moveTo(0.0, 0.33 + L)
    t.lineTo(-0.035, 0.33 + L + 0.05)
    t.moveTo(0.0, 0.33 + L)
    t.lineTo(0.035, 0.33 + L + 0.05)
    p = skia.Paint(AntiAlias=True, Color=col(LINE, a), Style=skia.Paint.kStroke_Style, StrokeWidth=0.042,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
    cv.drawPath(t, p)
    p.setColor(col(TONGUE, a))
    p.setStrokeWidth(0.022)
    cv.drawPath(t, p)


def glasses3(cv, a, reflect=0.0, t=0.0):
    for sx in (-1, 1):
        L = lens(sx)
        cv.drawPath(L, fillp(cv, '#ffffff', .06 * a, False))
        if reflect > 0:
            cv.save()
            cv.clipPath(L, doAntiAlias=True)
            g = skia.Paint(AntiAlias=True, Color=col(GOLD_HI, .22 * reflect * a))
            cv.drawCircle(sx * GX, GY + 0.12, GR * .9, g)
            cx0 = sx * GX - GR
            sky = [(cx0, GY + GR)]
            x = cx0
            k = 0
            while x < cx0 + 2 * GR:
                h = (0.10, 0.18, 0.08, 0.22, 0.12, 0.16)[k % 6]
                sky += [(x, GY + 0.27 - h * .6), (x + 0.07, GY + 0.27 - h * .6)]
                x += 0.07
                k += 1
            sky += [(cx0 + 2 * GR, GY + GR)]
            cv.drawPath(poly(sky), fillp(cv, GOLD, .45 * reflect * a, False))
            cyl = skia.Path()
            cyl.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx * GX + 0.08, GY + 0.02, 0.06, 0.18), 0.02, 0.02))
            cv.drawPath(cyl, fillp(cv, GOLD_HI, .6 * reflect * a, False))
            cv.restore()
        glare = skia.Path()
        glare.addArc(skia.Rect.MakeXYWH(sx * GX - GR * .78, GY - GR * .78, GR * 1.56, GR * 1.56), 200, 45)
        gp = skia.Paint(AntiAlias=True, Color=col('#ffffff', .35 * a), Style=skia.Paint.kStroke_Style, StrokeWidth=0.03,
                        StrokeCap=skia.Paint.kRound_Cap)
        cv.drawPath(glare, gp)
        cv.drawPath(L, ink(cv, LW * .95, a))
    br = P_([(-0.04, -0.15), (0.0, -0.19, 0.0, -0.19, 0.04, -0.15)], close=False)
    cv.drawPath(br, ink(cv, LW * .95, a))
    for sx in (-1, 1):
        cv.drawPath(poly([(sx * (GX + GR - 0.01), GY - 0.08), (sx * 0.70, GY - 0.12)], close=False), ink(cv, LW * .9, a))


def bowler3(cv, a):
    cv.save()
    cv.translate(0.06, -0.46)
    cv.rotate(-8)
    brim = skia.Path()
    brim.addOval(skia.Rect.MakeXYWH(-0.50, -0.05, 1.00, 0.15))
    dome = P_([(-0.33, 0.03), (-0.35, -0.38, 0.35, -0.38, 0.33, 0.03)])
    for p_ in (brim, dome):
        cv.drawPath(p_, fillp(cv, '#2c2a29', a))
        cv.save()
        cv.clipPath(p_, doAntiAlias=True)
        shade_and_rim(cv, p_, '#1f1d1c', '#46423f', 0.04, a, 0.025)
        cv.restore()
        cv.drawPath(p_, ink(cv, LW, a))
    band = poly([(-0.335, -0.05), (0.335, -0.05), (0.33, 0.03), (-0.33, 0.03)])
    cv.drawPath(band, fillp(cv, TIE, a))
    cv.drawPath(band, ink(cv, LW * .8, a))
    cv.restore()


EXPR = {
    'happy': ('closed', None, 'tongue', 0.0),
    'neutral': ('dot', 'soft', 'smile', 0.0),
    'smug': ('lidded', 'smug', 'smirk', 0.0),
    'worried': ('small', 'worried', 'wavy', 0.0),
    'surprised': ('big', 'high', 'o', 0.0),
    'gold': ('closed', None, 'o', 0.0),
    'hiss': ('dot', 'soft', 'smile', 0.7),
}


def draw_head(cv, expr='happy', look=(0.0, 0.0), tilt=0.0, hat=False, a=1.0, shadow=True, t=0.0, reflect=None):
    e_kind, b_kind, m_kind, tongue = EXPR[expr]
    cv.save()
    cv.rotate(tilt)
    hp = P_(HEAD3)
    if shadow:
        ghost(cv, hp, a)
    cv.drawPath(hp, fillp(cv, SN, a))
    cv.save()
    cv.clipPath(hp, doAntiAlias=True)
    cv.drawPath(minus(hp, shifted(hp, -0.06, -0.06)), fillp(cv, SN_SH, a, False))
    jaw = skia.Path(jaw_curve(m_kind))
    jaw.lineTo(0.8, 0.8)
    jaw.lineTo(-0.8, 0.8)
    jaw.close()
    cv.drawPath(jaw, fillp(cv, SN_BELLY, a, False))
    cv.drawPath(minus(jaw, shifted(jaw, -0.03, -0.035)), fillp(cv, SN_BELLY_SH, a, False))
    for (sx, sy, r) in ((-0.09, -0.40, .035), (0.0, -0.44, .04), (0.09, -0.40, .035)):
        cv.drawOval(skia.Rect.MakeXYWH(sx - r * 1.4, sy - r, r * 2.8, r * 2), fillp(cv, SN_SPOT, a, False))
    cv.drawPath(minus(hp, shifted(hp, 0.035, 0.035)), fillp(cv, SN_RIM, .9 * a, False))
    cv.restore()
    cv.drawPath(hp, ink(cv, LW * 1.05, a))
    for sx in (-1, 1):
        cv.drawOval(skia.Rect.MakeXYWH(sx * 0.44 - 0.075, 0.07, 0.15, 0.08), fillp(cv, BLUSH, .45 * a, False))
        cv.drawOval(skia.Rect.MakeXYWH(sx * 0.075 - 0.022, 0.06, 0.044, 0.03), fillp(cv, '#3b2c22', a, False))
    eyes(cv, e_kind, look, a)
    brows(cv, b_kind, a)
    mouth3(cv, m_kind, a)
    fork(cv, tongue, a)
    glasses3(cv, a, reflect=(1.0 if expr == 'gold' else 0.0) if reflect is None else reflect, t=t)
    if hat:
        bowler3(cv, a)
    cv.restore()


def draw_mascot(cv, x, y, s, expr='happy', look=(0.1, 0.05), tilt=-3.0, hat=False, a=1.0, t=0.0, reflect=None):
    """Ganzfigur. (x, y) = Kopfmitte, s = Kopfbreite / 1.32 in Pixeln."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    draw_body(cv, a)
    draw_collar(cv, a)
    cv.save()
    cv.translate(0, -0.02 + 0.01 * math.sin(t * 1.6))
    draw_head(cv, expr, look, tilt, hat, a, t=t, reflect=reflect)
    cv.restore()
    cv.restore()


def badge(cv, x, y, r, expr, look=(0.0, 0.0), tilt=0.0, hat=False, label=None):
    c = circle(x, y, r)
    cv.drawCircle(x + 6, y + 8, r, fillp(cv, '#000000', .35, False))
    cv.drawPath(c, fillp(cv, '#3a2b27', 1, False))
    cv.save()
    cv.clipPath(c, doAntiAlias=True)
    cv.drawCircle(x - r * .3, y - r * .4, r * 1.1, glowp(cv, '#f1d9a8', r * .5, .10))
    s = r * 0.78
    cv.save()
    cv.translate(x, y - r * 0.05)
    cv.scale(s, s)
    neck = tube([(0.0, 0.2), (0.0, 1.6)], [0.26, 0.29])
    cv.drawPath(neck, fillp(cv, SN, 1))
    cv.save()
    cv.clipPath(neck, doAntiAlias=True)
    cv.drawPath(minus(neck, shifted(neck, -0.05, 0)), fillp(cv, SN_SH, 1, False))
    bl = tube([(0.04, 0.2), (0.04, 1.6)], [0.10, 0.115])
    cv.drawPath(bl, fillp(cv, SN_BELLY, 1, False))
    cv.restore()
    cv.drawPath(neck, ink(cv, LW, 1))
    draw_collar(cv, 1)
    draw_head(cv, expr, look, tilt, hat, 1, shadow=True)
    cv.restore()
    cv.restore()
    cv.drawPath(c, strokep(cv, 6, '#4b3a33', 1))
    cv.drawPath(c, ink(cv, LW, 1))
    if label:
        text(cv, label, x, y + r + 40, P.TF_HEAD, 26, BONE, anchor='c')


def backdrop(cv, base=BG3):
    cv.drawPaint(fillp(cv, base, 1, False))
    for k in range(5):
        x = 200 + k * 430
        cv.drawPath(poly([(x, -20), (x + 150, -20), (x - 260, H + 20), (x - 410, H + 20)]), fillp(cv, '#f3e2bd', .025, False))
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150, [col('#000000', 0), col('#000000', .55)]))
    cv.drawPaint(vg)


def sheet(out):
    from PIL import Image
    P.init_assets()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    backdrop(cv)
    P.G.zoom = 1.0
    f = skia.Font(TF_DISPLAY, 64)
    t1 = 'Meet the Snake.'
    cv.drawTextBlob(skia.TextBlob.MakeFromString(t1, f), 86, 128, fillp(cv, '#000000', .5, False))
    cv.drawTextBlob(skia.TextBlob.MakeFromString(t1, f), 80, 120, fillp(cv, BONE_HI, 1, False))
    text(cv, 'NEUER ENTWURF  -  FLACH, WARM, OHNE KNICKE', 84, 172, P.TF_CAPS, 22, GOLD, spacing=5)
    draw_mascot(cv, 390, 330, 160, 'happy', tilt=-4)
    draw_mascot(cv, 900, 330, 160, 'neutral', look=(0.3, 0.1), tilt=3, hat=True)
    text(cv, 'ohne Hut', 330, 1000, P.TF_HEAD, 30, BONE_HI, anchor='c')
    text(cv, 'mit Melone', 800, 1000, P.TF_HEAD, 30, BONE_HI, anchor='c')
    items = [('happy', 'freundlich', (0, 0), -4), ('neutral', 'erzaehlt', (0.3, 0.1), 2), ('smug', 'verschmitzt', (0.4, 0), 6),
             ('worried', 'besorgt', (0, 0.3), -2), ('surprised', 'ueberrascht', (0, -0.2), 0), ('gold', 'sieht EDEN', (0, 0), -3)]
    for k, (e, lab, lk, tl) in enumerate(items):
        col_, row = k % 3, k // 3
        badge(cv, 1205 + col_ * 255, 360 + row * 360, 112, e, lk, tl, label=lab)
    text(cv, 'Ausdruecke, zugleich Vorschlaege fuers Profilbild', 1460, 1000, P.TF_HEAD, 24, BONE_SH, anchor='c')
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    Image.fromarray(P.Post().apply(img, 0)).save(out)
    print('saved', out)


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2])
