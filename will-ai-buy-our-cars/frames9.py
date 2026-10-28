#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Entwuerfe fuer Szenen quer durch das Video (Stil des ersten Entwurfs,
Qualitaet der Referenzen, neue Schlange als Erzaehlerin).

python3 frames9.py <name> <out.png>     name: chapter skins ring curve endscreen luddites horses reuther
                                              moravec cage board
"""
import math, random, sys
import numpy as np
import skia
import rich as R
import mascot3 as M
import style5 as ST
from rich_base import *

TF_CAPS, TF_HEAD, TF_TITLE, TF_TYPE, TF_SUB = P.TF_CAPS, P.TF_HEAD, P.TF_TITLE, P.TF_TYPE, P.TF_SUB
TF_D = M.TF_DISPLAY
WOODC = '#3b342d'


# ---------------------------------------------------------------- Bausteine
def lower_third(cv, line, sub=None, a=1.0):
    band = skia.Paint()
    band.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 900), skia.Point(0, H)], [col('#0b0c0c', 0), col('#0b0c0c', .85 * a)]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), band)
    cv.drawLine(80, 985, 150, 985, strokep(cv, 2.5, GOLD, a))
    P.draw_text(cv, line, 170, 995, TF_CAPS, 28, fillp(cv, GOLD, a, False), spacing=7)
    if sub:
        text(cv, sub, 170, 1032, TF_HEAD, 24, BONE_SH, a)


def fiction(cv):
    P.fiction_label(cv, 1.0)


def fit(tf, s, maxw, size):
    f = skia.Font(tf, size)
    w = f.measureText(s)
    return size * min(1.0, maxw / w)


def extruded(cv, s, x, y, size, c, depth=12, tf=None):
    f = skia.Font(tf or TF_D, size)
    blob = skia.TextBlob.MakeFromString(s, f)
    for k in range(depth, 0, -1):
        cv.drawTextBlob(blob, x + k * .9, y + k, fillp(cv, '#090a0a', 1, False))
    cv.drawTextBlob(blob, x + 3, y + 3, fillp(cv, mix(c, '#000000', .45), 1, False))
    cv.drawTextBlob(blob, x, y, fillp(cv, c, 1, False))
    return f.measureText(s)


def spot(cv, x0, y0, w0, x1, y1, w1, a=1.0, c=BONE_HI):
    P.G.zoom = mscale(cv)
    P.draw_cone(cv, x0, y0, w0, x1, y1, w1, c, a)


def soft_shadow(cv, x, y, w, h, a=.5, blur=20):
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', a))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    cv.drawOval(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), sh)


def snake_tube(cv, pts, rad, belly_vec=None, spots=True, a=1.0, ghost=True):
    """Koerper der neuen Schlange entlang beliebiger Mittellinie (glatte Roehre)."""
    n = len(pts)
    if belly_vec is None:
        belly_vec = [(0.0, 1.0)] * n
    body = M.tube(pts, rad)
    if ghost:
        M.ghost(cv, body, a)
    cv.drawPath(body, fillp(cv, M.SN, a))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    d = max(rad) * .18
    cv.drawPath(M.minus(body, M.shifted(body, -d, -d)), fillp(cv, M.SN_SH, a, False))
    bpts = [(x + vx * r * .6, y + vy * r * .6) for (x, y), r, (vx, vy) in zip(pts, rad, belly_vec)]
    brad = [r * .40 for r in rad]
    belly = M.tube(bpts, brad)
    cv.drawPath(belly, fillp(cv, M.SN_BELLY, a, False))
    cv.save()
    cv.clipPath(belly, doAntiAlias=True)
    acc = 0.0
    for i in range(1, n - 1):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        if acc > max(rad) * .32:
            acc = 0.0
            (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0) or 1
            nx, ny = -(y1 - y0) / L, (x1 - x0) / L
            bx, by = bpts[i]
            r = brad[i]
            cv.drawLine(bx - nx * r, by - ny * r, bx + nx * r, by + ny * r, strokep(cv, 1.6 / mscale(cv), M.SN_BELLY_SH, .9 * a))
    cv.restore()
    if spots:
        acc = 0.0
        for i in range(2, n - 4):
            acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
            if acc > max(rad) * 1.15:
                acc = 0.0
                (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
                ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
                vx, vy = belly_vec[i]
                cv.save()
                cv.translate(pts[i][0] - vx * rad[i] * .4, pts[i][1] - vy * rad[i] * .4)
                cv.rotate(ang)
                cv.drawOval(skia.Rect.MakeXYWH(-rad[i] * .28, -rad[i] * .15, rad[i] * .56, rad[i] * .30), fillp(cv, M.SN_SPOT, a, False))
                cv.restore()
    rd = max(rad) * .12
    cv.drawPath(M.minus(body, M.shifted(body, rd, rd)), fillp(cv, M.SN_RIM, .9 * a, False))
    cv.restore()
    cv.drawPath(body, M.ink(cv, M.LW, a))
    return body


def head_at(cv, x, y, s, expr='neutral', look=(0, 0), tilt=0.0, talk=0.0, reflect=0.0, collar=True, hat=False):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    if collar:
        M.draw_collar(cv)
    M.draw_head(cv, expr, look, tilt, hat, 1.0, talk=talk, reflect=reflect)
    cv.restore()


def mascot_full(cv, x, y, s, expr='neutral', look=(0, 0), tilt=0.0, talk=0.0, reflect=0.0, hat=False):
    M.draw_mascot(cv, x, y, s, expr, look, tilt, hat, reflect=reflect)


def finish(surf, out, grade_post=True):
    from PIL import Image
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    Image.fromarray(P.Post().apply(img, 0)).save(out)
    print('saved', out)


def new_canvas():
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    P.G.zoom = 1.0
    return surf, cv


# ================================================================ A  Kapitelkarte
def f_chapter(out, num='CHAPTER ONE', l1='HAVEN’T WE', l2='SURVIVED THIS BEFORE?'):
    surf, cv = new_canvas()
    cv.drawPaint(fillp(cv, '#1b1c1c', 1, False))
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.rotate(-6)
    cv.translate(-W / 2, -H / 2)
    for k in range(-3, 14):
        cv.drawRect(skia.Rect.MakeXYWH(-300 + k * 190, -300, 120, H + 600), fillp(cv, '#202222', 1, False))
    panel = skia.Path()
    panel.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(230, 250, 1460, 600), 10, 10))
    cv.drawPath(panel, fillp(cv, '#111212', 1))
    cv.drawPath(panel, strokep(cv, 10, '#181a19'))
    for (x, y, n, c) in ((330, 225, 6, '#8f9188'), (760, 222, 3, GOLD), (1160, 225, 15, '#8f9188'), (1480, 878, 6, '#8f9188'),
                         (860, 880, 4, GOLD), (380, 880, 3, GOLD)):
        for k in range(n):
            cv.drawCircle(x + k * 30, y, 9, fillp(cv, c, 1, False))
    for (x, y, w) in ((420, 168, 330), (1190, 935, 260)):
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, 26), 13, 13), fillp(cv, '#a3a493', 1))
    for (x, y, h) in ((160, 170, 220), (210, 210, 200), (1745, 430, 230), (1795, 470, 190)):
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 24, h), 12, 12), fillp(cv, '#a3a493', 1))
    ST.deco_circle(cv, 150, 330, 125, GOLD_DK)
    ST.deco_circle(cv, 1720, 175, 80, GOLD)
    ST.deco_circle(cv, 1735, 840, 115, '#3c403e')
    ST.deco_circle(cv, 135, 770, 68, GOLD_DK, 1)
    cv.drawLine(1735, 720, 1735, 960, M.ink(cv, 3))
    cv.drawLine(1615, 840, 1855, 840, M.ink(cv, 3))
    cv.drawCircle(1735, 840, 10, fillp(cv, M.LINE, 1, False))
    P.draw_text(cv, num, 330, 370, TF_CAPS, 34, fillp(cv, GOLD, 1, False), spacing=10)
    cv.drawLine(330, 392, 330 + P.text_w(TF_CAPS, 34, num, 10), 392, strokep(cv, 3, GOLD_DK))
    extruded(cv, l1, 330, 545, fit(TF_D, l1, 1250, 140), BONE_HI, 12)
    extruded(cv, l2, 330, 715, fit(TF_D, l2, 1280, 140), GOLD, 14)
    cv.restore()
    R.dust(cv, 1.0, (0, 0, W, H), 40, 3, BONE_HI, .25)
    finish(surf, out)


# ================================================================ B  Die alten Haeute (H-02)
SKINS = [('SOOT', '1760s', 'STEAM'), ('CHROME', '1913', 'ASSEMBLY LINE'), ('EARTH', '1915', 'TRACTOR'),
         ('TUBE', '1950s', 'AUTOMATION'), ('PIXEL', '1980s', 'COMPUTER')]


def skin_pattern(cv, kind, box, seed):
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    if kind == 'SOOT':
        for _ in range(40):
            cv.drawCircle(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(4, 14), fillp(cv, '#3a3a37', .55, False))
    elif kind == 'CHROME':
        for k in range(int((x1 - x0) / 22) + 8):
            x = x0 - 80 + k * 22
            cv.drawLine(x, y1, x + 60, y0, strokep(cv, 8, '#e4e4dc' if k % 2 else '#8f938f', .7))
    elif kind == 'EARTH':
        for _ in range(60):
            cv.drawCircle(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(2, 6), fillp(cv, '#6b5640', .8, False))
    elif kind == 'TUBE':
        for _ in range(22):
            x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            cv.drawCircle(x, y, 9, glowp(cv, '#8fd0a0', 6, .5))
            cv.drawCircle(x, y, 5, fillp(cv, '#8fc29b', .9, False))
    elif kind == 'PIXEL':
        for gx in range(int(x0), int(x1), 16):
            for gy in range(int(y0), int(y1), 16):
                if rnd.random() < .45:
                    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, 11, 11), fillp(cv, '#7397bb', .8, False))


def shed_skin(cv, x, y, L, r, kind, seed, curl=1.0):
    pts = []
    n = 60
    for i in range(n + 1):
        u = i / n
        pts.append((x + (u - .5) * L, y + 16 * math.sin(u * math.pi * 2 * curl + seed) - 10 * u))
    rad = [r * (1.0 if u < .55 else lerp(1.0, .15, ((u - .55) / .45) ** 1.3)) for u in [i / n for i in range(n + 1)]]
    rad[0] = r * .85
    body = M.tube(pts, rad)
    soft_shadow(cv, x, y + r * 1.3, L * 1.05, r * 1.2, .5, 16)
    cv.drawPath(body, fillp(cv, '#d9d3bf', .42))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    b = body.computeTightBounds()
    skin_pattern(cv, kind, (b.left(), b.top(), b.right(), b.bottom()), seed)
    acc = 0
    for i in range(1, n - 3, 2):
        sx, sy = pts[i]
        cv.drawPath(P_([(sx - r * .3, sy - r * .1), (sx, sy - r * .45, sx, sy - r * .45, sx + r * .3, sy - r * .1)], close=False),
                    strokep(cv, 1.6, '#f3eedf', .45))
    cv.drawPath(M.minus(body, M.shifted(body, 4, 4)), fillp(cv, '#fbf6e6', .5, False))
    cv.restore()
    cv.drawPath(body, inkp(cv, 2.2, '#cfc7ae', .9))
    mouth = skia.Path()
    mouth.addOval(skia.Rect.MakeXYWH(pts[0][0] - r * .35, pts[0][1] - r * .8, r * .7, r * 1.6))
    cv.drawPath(mouth, fillp(cv, '#141515', .85, False))
    cv.drawPath(mouth, inkp(cv, 2.0, '#cfc7ae', .9))


def f_skins(out):
    surf, cv = new_canvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    floor = skia.Paint()
    floor.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 640), skia.Point(0, H)], [col('#1d1f1f'), col('#121313')]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 640, W, H), floor)
    cv.drawLine(0, 640, W, 640, M.ink(cv, 2.6))
    for k in range(-6, 14):
        cv.drawLine(960 + k * 60, 640, 960 + k * 260, H, strokep(cv, 1.5, '#262828', 1))
    spot(cv, 760, -60, 60, 760, 900, 1500, .35)
    for k, (kind, year, label) in enumerate(SKINS):
        x = 200 + k * 255
        y = 790 - (k % 2) * 30
        shed_skin(cv, x, y, 250, 30, kind, k * 1.7)
        text(cv, year, x, 895, TF_HEAD, 34, BONE_HI, anchor='c')
        text(cv, label, x, 930, TF_CAPS, 18, GOLD, anchor='c', spacing=3)
    cv.drawRect(skia.Rect.MakeXYWH(1400, 700, 520, 260), glowp(cv, GOLD_HI, 120, .10))
    mascot_full(cv, 1600, 410, 150, 'neutral', look=(-0.7, 0.2), tilt=-5, reflect=.2)
    cv.save()
    cv.translate(1600, 410)
    cv.scale(150, 150)
    pts = M.body_paths()['pts'][0]
    seam = [(x + .05, y - .02) for (x, y) in pts[30:150:2]]
    for (x0, y0), (x1, y1) in zip(seam, seam[1:]):
        pass
    cv.restore()
    finish(surf, out)


# ================================================================ D  Der Ring aus Lohn und Kauf (01-10)
def factory_icon(cv, x, y, s):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    saw = poly([(-1.0, 0.6), (-1.0, -0.1), (-0.6, -0.4), (-0.6, -0.1), (-0.2, -0.4), (-0.2, -0.1), (0.2, -0.4), (0.2, -0.1),
                (0.6, -0.4), (0.6, 0.6)])
    stack = poly([(0.66, 0.6), (0.66, -0.9), (0.86, -0.9), (0.86, 0.6)])
    for p_ in (stack, saw):
        M.ghost(cv, p_)
        cv.drawPath(p_, fillp(cv, BONE, 1))
        cv.save()
        cv.clipPath(p_, doAntiAlias=True)
        M.shade_and_rim(cv, p_, BONE_SH, BONE_HI, .07, 1, .04)
        cv.restore()
        cv.drawPath(p_, M.ink(cv))
    for k in range(4):
        cv.drawRect(skia.Rect.MakeXYWH(-0.88 + k * 0.38, 0.12, 0.18, 0.22), fillp(cv, GOLD, 1, False))
        cv.drawRect(skia.Rect.MakeXYWH(-0.88 + k * 0.38, 0.12, 0.18, 0.22), M.ink(cv, 2))
    for k in range(3):
        cv.drawCircle(0.78 + 0.12 * k, -1.05 - 0.22 * k, 0.12 + 0.05 * k, fillp(cv, '#6c6e69', .7 - .15 * k, False))
    cv.restore()


def coin(cv, x, y, r):
    c = circle(x, y, r)
    cv.drawPath(c, fillp(cv, GOLD, 1))
    cv.drawCircle(x, y, r * .7, strokep(cv, 2, GOLD_DK))
    text(cv, '$', x, y + r * .36, TF_HEAD, r * 1.05, GOLD_DK, anchor='c')
    cv.drawPath(c, M.ink(cv, 2.2))


def arrow_arc(cv, cx, cy, r, a0, a1, c, w=4):
    p = skia.Path()
    p.addArc(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), a0, a1 - a0)
    cv.drawPath(p, strokep(cv, w, c, .9))
    ae = math.radians(a1)
    ex, ey = cx + r * math.cos(ae), cy + r * math.sin(ae)
    tx, ty = -math.sin(ae) * (1 if a1 > a0 else -1), math.cos(ae) * (1 if a1 > a0 else -1)
    nx, ny = -ty, tx
    head = poly([(ex + tx * 18, ey + ty * 18), (ex + nx * 11, ey + ny * 11), (ex - nx * 11, ey - ny * 11)])
    cv.drawPath(head, fillp(cv, c, .9, False))


def f_ring(out):
    surf, cv = new_canvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cx, cy, Rr = 960, 600, 300
    cv.drawCircle(cx, cy, 420, glowp(cv, GOLD_HI, 160, .10))
    pts, rad, bv = [], [], []
    n = 220
    for i in range(n + 1):
        u = i / n
        a = math.radians(lerp(-70, 252, u))
        pts.append((cx + Rr * math.cos(a), cy + Rr * math.sin(a)))
        rad.append(46 if u < .55 else lerp(46, 13, ((u - .55) / .45) ** 1.1))
        bv.append((-math.cos(a), -math.sin(a)))
    snake_tube(cv, pts, rad, bv)
    factory_icon(cv, 830, 640, 88)
    for k in range(3):
        bust_front(cv, 1055 + k * 62, 640 + (k % 2) * 14, 46, variant=k * 5 + 1, t=k)
    for k, a in enumerate((140, 115, 90, 65, 40)):
        ar = math.radians(a)
        coin(cv, cx + 205 * math.cos(ar), cy + 205 * math.sin(ar), 21)
    arrow_arc(cv, cx, cy, 252, 150, 35, GOLD, 4)
    for k, a in enumerate((-40, -140)):
        ar = math.radians(a)
        P.draw_car(cv, cx + 215 * math.cos(ar) - 55, cy + 215 * math.sin(ar) + 20, 110, (BONE, '#4b6278')[k])
    arrow_arc(cv, cx, cy, 252, -30, -150, BONE_HI, 4)
    text(cv, 'WAGES', cx, cy + Rr + 110, TF_CAPS, 34, GOLD, anchor='c', spacing=10)
    text(cv, 'PURCHASES', cx, cy - 92, TF_CAPS, 26, BONE_HI, anchor='c', spacing=8)
    head_at(cv, cx - 6, cy - Rr - 30, 150, 'smug', look=(0.2, 0.2), tilt=-6, collar=False)
    lower_third(cv, 'THE LOOP', 'wages turn into purchases, purchases turn back into wages')
    finish(surf, out)


# ================================================================ F  Pferdebestand als Schlangenkoerper (02-05)
HORSES = [(1900, 17.0), (1905, 18.5), (1910, 20.0), (1915, 21.4), (1920, 19.8), (1925, 16.3), (1930, 13.0), (1935, 11.4),
          (1940, 10.4), (1945, 8.7), (1950, 6.0), (1955, 4.2), (1960, 3.0)]


def f_curve(out):
    surf, cv = new_canvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    x0, x1, y0, y1 = 260, 1560, 880, 250
    X = lambda yr: lerp(x0, x1, (yr - 1900) / 60)
    Y = lambda v: lerp(y0, y1, v / 25)
    for v in range(0, 26, 5):
        cv.drawLine(x0, Y(v), x1 + 40, Y(v), strokep(cv, 1.5, '#2c2e2e', 1))
        text(cv, f'{v} M' if v else '0', x0 - 22, Y(v) + 9, TF_HEAD, 24, BONE_SH, anchor='r')
    for yr in range(1900, 1961, 10):
        cv.drawLine(X(yr), y0, X(yr), y0 + 12, strokep(cv, 2, BONE_SH))
        text(cv, str(yr), X(yr), y0 + 46, TF_HEAD, 26, BONE_SH, anchor='c')
    cv.drawLine(x0, y0, x1 + 40, y0, M.ink(cv, 2.4))
    cv.drawLine(x0, y0, x0, y1 - 20, strokep(cv, 2, BONE_SH))
    P.draw_text(cv, 'HORSES IN THE UNITED STATES', 260, 150, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    text(cv, 'approximate, 1900 to 1960', 260, 192, TF_HEAD, 26, BONE_SH)
    xs = np.array([X(a) for a, _ in HORSES])
    ys = np.array([Y(b) for _, b in HORSES])
    pts = []
    for k in range(len(HORSES) - 1):
        p0 = (xs[max(0, k - 1)], ys[max(0, k - 1)])
        p1, p2 = (xs[k], ys[k]), (xs[k + 1], ys[k + 1])
        p3 = (xs[min(len(xs) - 1, k + 2)], ys[min(len(ys) - 1, k + 2)])
        for j in range(16):
            t = j / 16
            t2, t3 = t * t, t * t * t
            pts.append((0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                        0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)))
    pts.append((xs[-1], ys[-1]))
    n = len(pts)
    neck = [(xs[-1] + 40 * u, ys[-1] - 150 * u * u) for u in [k / 14 for k in range(1, 15)]]
    pts = pts + neck
    rad = [lerp(6, 24, min(1, i / 60)) for i in range(len(pts))]
    fill = poly([(x0, y0)] + pts[:n] + [(xs[-1], y0)])
    gp = skia.Paint(AntiAlias=True)
    gp.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y1), skia.Point(0, y0)], [col(M.SN, .25), col(M.SN, .03)]))
    cv.drawPath(fill, gp)
    snake_tube(cv, pts, rad)
    hx, hy = pts[-1]
    head_at(cv, hx, hy - 40, 120, 'worried', look=(-0.6, 0.4), tilt=6)
    for (yr, v, lab, dx, dy) in ((1915, 21.4, '1915 · 20+ MILLION', -250, -70), (1960, 3.0, '1960 · 1 TO 3 MILLION', -420, 70)):
        px, py = X(yr), Y(v)
        cv.drawCircle(px, py, 11, fillp(cv, GOLD, 1, False))
        cv.drawCircle(px, py, 11, M.ink(cv, 2))
        cv.drawLine(px, py, px + dx * .5, py + dy * .6, strokep(cv, 2, GOLD))
        text(cv, lab, px + dx, py + dy, TF_HEAD, 30, GOLD_HI, anchor='l' if dx > -100 else 'l')
    tx, ty = X(1919), Y(20.3) - 70
    text(cv, 'THE TRACTOR ARRIVES', X(1921) + 40, Y(22.6), TF_CAPS, 24, BONE_HI, spacing=5)
    cv.drawLine(X(1921) + 30, Y(22.6) - 8, X(1920) + 6, Y(20.0) - 22, strokep(cv, 2, BONE_HI))
    text(cv, 'Source: U.S. Census of Agriculture via TheHorse.com', W - 60, 1050, TF_SUB, 20, '#6f716b', anchor='r')
    finish(surf, out)


# ================================================================ J  Abspann (09-09)
def f_endscreen(out):
    surf, cv = new_canvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.drawCircle(960, 560, 380, glowp(cv, GOLD_HI, 150, .10))
    for (x, y) in ((110, 250), (1190, 250)):
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 620, 349), 16, 16)
        cv.drawRRect(rr, fillp(cv, '#141515', .8, False))
        p = strokep(cv, 3, BONE_SH, .8)
        p.setPathEffect(skia.DashPathEffect.Make([18, 12], 0))
        cv.drawRRect(rr, p)
        text(cv, 'NEXT VIDEO', x + 310, y + 185, TF_CAPS, 30, BONE_SH, .8, anchor='c', spacing=6)
        text(cv, 'end screen element', x + 310, y + 225, TF_HEAD, 22, '#6f716b', anchor='c')
    sub = circle(960, 870, 90)
    p = strokep(cv, 3, GOLD, .8)
    p.setPathEffect(skia.DashPathEffect.Make([14, 10], 0))
    cv.drawPath(sub, p)
    text(cv, 'SUBSCRIBE', 960, 880, TF_CAPS, 20, GOLD, .8, anchor='c', spacing=4)
    mascot_full(cv, 960, 300, 120, 'happy', look=(0, 0), tilt=-4, hat=False)
    text(cv, 'THANKS FOR WATCHING', 960, 130, TF_CAPS, 34, GOLD, anchor='c', spacing=12)
    finish(surf, out)


FRAMES = {'chapter': f_chapter, 'skins': f_skins, 'ring': f_ring, 'curve': f_curve, 'endscreen': f_endscreen}


# ================================================================ G  "The workers were horses." (02-02 / 02-06)
def horse_path(flip=1, step=0.0):
    parts = []
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(-1.05, -0.45, 2.1, 0.9))
    parts.append(body)
    parts.append(M.tube([(0.75, -0.15), (1.05, -0.70), (1.22, -1.05)], [0.33, 0.25, 0.20]))
    parts.append(M.tube([(1.12, -1.10), (1.45, -0.92), (1.72, -0.70)], [0.21, 0.17, 0.15]))
    parts.append(poly([(1.02, -1.18), (1.06, -1.42), (1.18, -1.20)]))
    parts.append(poly([(1.16, -1.20), (1.24, -1.42), (1.30, -1.16)]))
    sw = math.sin(step) * .18
    for (x, ph) in ((0.72, 0.0), (0.42, 1.0), (-0.52, 1.0), (-0.82, 0.0)):
        o = sw * (1 if ph else -1)
        parts.append(M.tube([(x, 0.10), (x + o * .4, 0.62), (x + o * .7, 0.95), (x + o, 1.38)], [0.20, 0.13, 0.11, 0.10]))
        hoof = skia.Path()
        hoof.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x + o - 0.13, 1.34, 0.26, 0.13), 0.04, 0.04))
        parts.append(hoof)
    parts.append(M.tube([(-1.0, -0.25), (-1.32, 0.05), (-1.38, 0.65)], [0.12, 0.13, 0.08]))
    mane = poly([(0.78, -0.42), (0.96, -0.86), (1.12, -1.12), (1.02, -0.70), (0.86, -0.30)])
    parts.append(mane)
    return union(parts)


def f_horses(out):
    surf, cv = new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    sky = skia.Paint()
    sky.setShader(skia.GradientShader.MakeRadial(skia.Point(1560, 560), 1100, [col('#e9d6a0'), col('#8a6a33'), col('#1a1b1b')], [0, .35, 1]))
    cv.drawRect(skia.Rect.MakeWH(W, 760), sky)
    for k in range(9):
        x = 200 + k * 160
        cv.drawRect(skia.Rect.MakeXYWH(x, 760 - 60 - (k % 3) * 40, 90, 400), fillp(cv, '#2a2622', .5, False))
    cv.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), fillp(cv, '#141413', 1, False))
    for k in range(12):
        cv.drawLine(1560 + (k - 6) * 40, 760, 1560 + (k - 6) * 420, H, strokep(cv, 2, '#1e1d1b', 1))
    for (x, y) in ((1500, 640), (1640, 640)):
        cv.drawCircle(x, y, 120, glowp(cv, '#fff2cf', 70, .8))
        cv.drawCircle(x, y, 34, fillp(cv, '#fffbef', 1, False))
    spot(cv, 1570, 640, 160, 300, 900, 900, .5, '#fff2cf')
    for k, (x, y, s, st) in enumerate(((300, 660, 125, 0.0), (640, 675, 132, 1.4), (980, 660, 122, 2.6))):
        hp = horse_path(1, st)
        cv.save()
        cv.translate(x, y)
        cv.scale(s, s)
        cv.drawPath(hp, fillp(cv, '#0f0f0f', 1))
        cv.save()
        cv.clipPath(hp, doAntiAlias=True)
        cv.drawPath(M.minus(hp, M.shifted(hp, -0.045, 0.035)), fillp(cv, '#f0d99a', .95, False))
        cv.restore()
        cv.drawPath(hp, M.ink(cv, 2.4))
        collar = M.tube([(0.62, -0.62), (0.80, -0.20), (1.02, 0.05)], [0.07, 0.08, 0.07])
        cv.save()
        cv.clipPath(hp, doAntiAlias=True)
        cv.drawPath(collar, fillp(cv, '#4a3a2a', 1))
        cv.drawPath(M.tube([(1.0, -0.2), (-0.6, -0.2), (-0.9, 0.05)], [0.035, 0.035, 0.035]), fillp(cv, '#3a2b20', 1))
        cv.restore()
        cv.restore()
        soft_shadow(cv, x - 60, y + 190, s * 2.6, 36, .6, 14)
    extruded(cv, 'The workers', 1110, 910, 92, BONE_HI, 8)
    extruded(cv, 'were horses.', 1180, 1015, 92, GOLD, 9)
    finish(surf, out)


# ================================================================ H  Reuther im automatisierten Werk (03-02 / 03-03)
def f_reuther(out):
    surf, cv = new_canvas()
    cv.drawPaint(fillp(cv, '#1b1d1c', 1, False))
    for row in range(3):
        y = 160 + row * 150
        scale = 1 - row * .18
        for k in range(14):
            x = -40 + k * 150 * scale + row * 40
            w, h = 120 * scale, 110 * scale
            box = skia.Path()
            box.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 8, 8))
            cv.drawPath(box, fillp(cv, mix('#2c302e', '#1b1d1c', row * .35), 1))
            cv.drawPath(box, M.ink(cv, 2))
            rnd = random.Random(k * 7 + row)
            for j in range(4):
                c = rnd.choice(['#7fc48f', GOLD, '#7fc48f', '#3d413f'])
                lx, ly = x + 18 * scale + j * 24 * scale, y + 26 * scale
                if c != '#3d413f':
                    cv.drawCircle(lx, ly, 9 * scale, glowp(cv, c, 5, .5))
                cv.drawCircle(lx, ly, 5 * scale, fillp(cv, c, 1, False))
            cv.drawRect(skia.Rect.MakeXYWH(x + 14 * scale, y + 52 * scale, w - 28 * scale, 40 * scale), fillp(cv, '#232625', 1, False))
    haze = skia.Paint()
    haze.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 120), skia.Point(0, 620)], [col('#1b1d1c', .75), col('#1b1d1c', 0)]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, 640), haze)
    cv.drawRect(skia.Rect.MakeLTRB(0, 640, W, H), fillp(cv, '#151716', 1, False))
    cv.drawLine(0, 640, W, 640, M.ink(cv, 2.6))
    for k in range(-8, 14):
        cv.drawLine(960 + k * 50, 640, 960 + k * 230, H, strokep(cv, 1.5, '#1c1e1d', 1))
    spot(cv, 960, -80, 80, 960, 1000, 1300, .4)
    person_profile(cv, 740, 680, 225, 0.0, facing=1, hair='A', glasses=True, look=-4, mouth=.6)
    person_profile(cv, 1250, 680, 225, 1.3, facing=-1, hair='B', look=3, mouth=1.0,
                   palette={'suit': '#2e2c2a', 'tie': GOLD_DK})
    q = skia.Path()
    q.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(560, 90, 800, 120), 16, 16))
    tail = poly([(780, 205), (760, 300), (840, 207)])
    bubble = union([q, tail])
    M.ghost(cv, bubble)
    cv.drawPath(bubble, fillp(cv, BONE_HI, 1))
    cv.drawPath(bubble, M.ink(cv, 2.6))
    text(cv, '"How are you going to get them', 960, 142, TF_TYPE, 38, '#1f1a14', anchor='c')
    text(cv, 'to buy cars?"', 960, 190, TF_TYPE, 38, '#1f1a14', anchor='c')
    lower_third(cv, 'CLEVELAND, OHIO  ·  EARLY 1950s', 'Walter Reuther, United Auto Workers, visiting a Ford engine plant')
    finish(surf, out)


# ================================================================ I  Der goldene Kaefig (08-05)
def f_cage(out):
    surf, cv = new_canvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cx, top, bot, rw = 1000, 170, 900, 430
    cv.drawCircle(cx, 520, 520, glowp(cv, GOLD_HI, 180, .18))
    cv.drawRect(skia.Rect.MakeLTRB(0, bot, W, H), fillp(cv, '#121313', 1, False))
    cv.drawLine(0, bot, W, bot, M.ink(cv, 2.6))
    inside = skia.Path()
    inside.addRect(skia.Rect.MakeLTRB(cx - rw, top + 150, cx + rw, bot))
    inside.addOval(skia.Rect.MakeXYWH(cx - rw, top, 2 * rw, 300))
    cv.save()
    cv.clipPath(inside, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeLTRB(cx - rw, top, cx + rw, bot), fillp(cv, '#1f1e1b', 1, False))
    for ri, (y, s) in enumerate(((600, 70), (700, 84), (820, 102))):
        n = 7 - ri
        for k in range(n):
            x = cx - rw + (k + .5) * (2 * rw) / n + (s * .3 if ri % 2 else 0)
            bust_front(cv, x, y, s, variant=ri * 11 + k * 3, dim=.25, t=k * .4)
            cv.drawCircle(x + s * .6, y + s * .55, s * .13, fillp(cv, GOLD, 1, False))
            cv.drawCircle(x + s * .6, y + s * .55, s * .13, M.ink(cv, 1.8))
    cv.restore()
    for k in range(17):
        u = k / 16
        x = cx - rw + u * 2 * rw
        ytop = top + 150 - 150 * math.sqrt(max(0, 1 - ((u - .5) * 2) ** 2))
        bar = M.tube([(x, ytop), (x, bot)], [7, 7])
        cv.drawPath(bar, fillp(cv, GOLD, 1))
        cv.drawPath(M.minus(bar, M.shifted(bar, 3, 0)), fillp(cv, GOLD_HI, 1, False))
        cv.drawPath(bar, M.ink(cv, 2))
    for y in (top + 150, 560, bot - 10):
        ring = skia.Path()
        ring.addRect(skia.Rect.MakeXYWH(cx - rw - 10, y - 12, 2 * rw + 20, 24))
        cv.drawPath(ring, fillp(cv, GOLD_SH, 1))
        cv.drawPath(ring, M.ink(cv, 2))
    dome = skia.Path()
    dome.addArc(skia.Rect.MakeXYWH(cx - rw, top, 2 * rw, 300), 180, 180)
    cv.drawPath(dome, strokep(cv, 16, GOLD))
    cv.drawPath(dome, M.ink(cv, 2))
    knob = circle(cx, top - 10, 26)
    cv.drawPath(knob, fillp(cv, GOLD, 1))
    cv.drawPath(knob, M.ink(cv, 2))
    cv.drawRect(skia.Rect.MakeXYWH(cx - 6, top - 120, 12, 100), fillp(cv, GOLD_DK, 1, False))
    for (x, f, hair) in ((300, 1, 'B'), (470, 1, 'A')):
        person_profile(cv, x, 560, 175, 0.0, facing=f, hair=hair, look=-2,
                       palette={'suit': '#141515', 'tie': GOLD_DK})
    cv.save()
    cv.translate(560, 760)
    cv.rotate(-30)
    key = union([circle(0, 0, 26), M.tube([(20, 0), (120, 0)], [8, 8]), poly([(95, 0), (95, 26), (110, 26), (110, 0)])])
    cv.drawPath(key, fillp(cv, GOLD, 1))
    cv.drawPath(circle(0, 0, 11), fillp(cv, '#141515', 1, False))
    cv.drawPath(key, M.ink(cv, 2))
    cv.restore()
    lower_third(cv, 'ENDING THREE', 'not extinction, just being kept')
    finish(surf, out)


# ================================================================ K  Uebergaenge und Einblendungen
def panel(cv, x, y, w, h, title, sub, draw_fn):
    cv.save()
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 12, 12)
    cv.clipRRect(r, doAntiAlias=True)
    cv.translate(x, y)
    cv.scale(w / W, h / H)
    draw_fn(cv)
    cv.restore()
    cv.drawRRect(r, strokep(cv, 3, '#3a3c3b'))
    text(cv, title, x, y + h + 38, TF_HEAD, 28, BONE_HI)
    text(cv, sub, x, y + h + 70, TF_HEAD, 21, BONE_SH)


def t_iris(cv):
    cv.drawPaint(fillp(cv, '#0f1010', 1, False))
    cv.save()
    c = circle(960, 540, 420)
    cv.clipPath(c, doAntiAlias=True)
    cv.drawImage(P.BG_NIGHT, 0, 0)
    R.draw_layer(cv, 'far', 0)
    P.G.zoom = .3
    P.draw_eden_bot(cv, 1180, 1040, 860, 170, 0, face=1.0, glow=1.0)
    R.draw_layer(cv, 'mid_g', 0)
    cv.restore()
    cv.drawPath(circle(960, 540, 420), strokep(cv, 14, '#2b2c2b'))
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(960 - 340, 540 - 340, 680, 680), 200, 52)
    cv.drawPath(hl, strokep(cv, 26, '#fff6dc', .45))
    for k in range(4):
        a = math.radians(45 + k * 90)
        cv.drawLine(960 + math.cos(a) * 560, 540 + math.sin(a) * 560, 960 + math.cos(a) * 470, 540 + math.sin(a) * 470,
                    strokep(cv, 10, GOLD, .9))


def t_curtain(cv):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.drawRect(skia.Rect.MakeLTRB(0, 640, W, H), fillp(cv, '#151716', 1, False))
    for k in range(5):
        P.draw_car(cv, 300 + k * 340, 760, 300, (BONE, '#4b6278', BONE, '#8c3b30', BONE)[k])
    cv.drawRect(skia.Rect.MakeXYWH(0, 760, W, 40), fillp(cv, '#2b2b29', 1, False))
    spot(cv, 960, -60, 60, 960, 800, 1100, .4)
    extruded(cv, '1913', 800, 420, 160, GOLD, 10)
    for sx in (-1, 1):
        cv.save()
        cv.translate(960 + sx * 520, 0)
        p = poly([(-sx * 0, -20), (sx * 620, -20), (sx * 620, H + 20), (-sx * 0, H + 20)])
        wave = skia.Path()
        wave.moveTo(0, -20)
        for yy in range(0, H + 40, 40):
            wave.lineTo(-sx * 30 * math.sin(yy * .02), yy)
        wave.lineTo(sx * 700, H + 20)
        wave.lineTo(sx * 700, -20)
        wave.close()
        cv.drawPath(wave, fillp(cv, '#c7c0a8', 1))
        cv.save()
        cv.clipPath(wave, doAntiAlias=True)
        rnd = random.Random(3 + sx)
        for _ in range(90):
            cv.drawCircle(rnd.uniform(-700, 700), rnd.uniform(0, H), rnd.uniform(6, 22), fillp(cv, '#3a3a37', .45, False))
        for yy in range(0, H, 46):
            cv.drawPath(P_([(-sx * 40, yy), (sx * 80, yy - 20, sx * 200, yy - 20, sx * 320, yy)], close=False), strokep(cv, 3, '#e8e2cc', .5))
        cv.restore()
        cv.drawPath(wave, M.ink(cv, 4))
        cv.restore()


def t_date(cv):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cv.translate(960, 470)
    cv.rotate(-8)
    cv.drawCircle(0, 0, 250, strokep(cv, 16, GOLD))
    cv.drawCircle(0, 0, 210, strokep(cv, 5, GOLD_DK))
    f = skia.Font(TF_D, 190)
    tw = f.measureText('1913')
    cv.drawTextBlob(skia.TextBlob.MakeFromString('1913', f), -tw / 2 + 6, 70, fillp(cv, '#000000', .5, False))
    cv.drawTextBlob(skia.TextBlob.MakeFromString('1913', f), -tw / 2, 64, fillp(cv, GOLD, 1, False))
    P.draw_text(cv, 'DETROIT', -P.text_w(TF_CAPS, 44, 'DETROIT', 14) / 2, 150, TF_CAPS, 44, fillp(cv, BONE_HI, 1, False), spacing=14)
    cv.restore()
    lower_third(cv, 'SECOND SKIN  ·  THE ASSEMBLY LINE', 'Highland Park, Michigan')


def t_quote(cv):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cv.translate(960, 540)
    cv.rotate(-3)
    pg = skia.Path()
    pg.addRect(skia.Rect.MakeXYWH(-620, -260, 1240, 520))
    soft_shadow(cv, 20, 290, 1300, 80, .5, 30)
    cv.drawPath(pg, fillp(cv, '#d6cdb2', 1))
    cv.drawPath(pg, M.ink(cv, 3))
    text(cv, 'U.S. SENATE, 1958', -540, -170, TF_TYPE, 40, '#5b4a36')
    cv.drawLine(-540, -150, -150, -150, strokep(cv, 2, '#5b4a36', .6))
    for k, ln in enumerate(('"Consumers are still made', 'in the good old fashioned way."')):
        text(cv, ln, -540, -40 + k * 90, TF_TYPE, 70, '#1f1a14')
    text(cv, '- Walter Reuther', 520, 200, TF_TYPE, 40, '#5b4a36', anchor='r')
    cv.restore()


def t_wipe(cv):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cv.translate(960, 540)
    cv.rotate(-28)
    cols = ['#202222', GOLD, '#111212', '#8f9188', '#202222', GOLD_DK, '#111212']
    for k, c in enumerate(cols):
        cv.drawRect(skia.Rect.MakeXYWH(-1400 + k * 300, -1400, 260, 2800), fillp(cv, c, 1, False))
    cv.restore()
    extruded(cv, 'CHAPTER TWO', 560, 600, 120, BONE_HI, 10)


def t_year(cv):
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    cv.save()
    k = 1.25
    cv.translate(960 - R.BX * k, 560 - R.BY * k)
    cv.scale(k, k)
    P.G.zoom = k
    R.crystal_ball(cv, 0)
    cv.restore()
    arc = skia.Path()
    rr = R.BR * 1.25 + 34
    arc.addArc(skia.Rect.MakeXYWH(960 - rr, 560 - rr, 2 * rr, 2 * rr), 200, 140)
    cv.drawPath(arc, strokep(cv, 4, GOLD, .7))
    f = skia.Font(TF_CAPS, 60)
    s = 'YEAR  FOUR'
    pm = skia.PathMeasure(arc, False)
    L = pm.getLength()
    tw = f.measureText(s) + 10 * len(s)
    d = (L - tw) / 2
    for ch in s:
        pos, tan = pm.getPosTan(d)
        cv.save()
        cv.translate(pos.x(), pos.y() - 18)
        cv.rotate(math.degrees(math.atan2(tan.y(), tan.x())))
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, f), 0, 0, fillp(cv, GOLD_HI, 1, False))
        cv.restore()
        d += f.measureText(ch) + 10
    P.fiction_label(cv, 1.0)


def f_board(out):
    surf, cv = new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    P.draw_text(cv, 'UEBERGAENGE UND EINBLENDUNGEN', 80, 82, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    items = [
        (t_iris, 'Fahrt in die Kristallkugel', 'Iris-Blende von Gegenwart in Fiktion und zurueck'),
        (t_curtain, 'Die Haut als Vorhang', 'jede Haeutung oeffnet ihr Kapitel wie ein Vorhang'),
        (t_date, 'Datumsstempel', 'Jahreszahl als goldenes Siegel, darunter Ort und Thema'),
        (t_quote, 'Zitatkarte', 'echte Zitate tippen sich auf altes Papier'),
        (t_wipe, 'Kapitel-Wischer', 'diagonale Streifen aus dem Titeldesign wischen ins Kapitel'),
        (t_year, 'EDEN-Jahre', 'YEAR-Zaehler laeuft ueber das Glas, FICTION am Rand'),
    ]
    pw, ph = 560, 315
    for k, (fn, t1, t2) in enumerate(items):
        x = 80 + (k % 3) * (pw + 40)
        y = 130 + (k // 3) * (ph + 140)
        panel(cv, x, y, pw, ph, t1, t2, fn)
    finish(surf, out)


# ================================================================ L  Stilblatt
def f_style(out):
    surf, cv = new_canvas()
    cv.drawPaint(fillp(cv, '#161717', 1, False))
    P.draw_text(cv, 'STILBLATT', 80, 82, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    sw = [('#1a1b1b', 'Anthrazit', 'Grund'), ('#c9c8bb', 'Knochenweiss', 'Figuren, Papier'), (GOLD, 'Gold', 'EDEN, Bedrohung'),
          (GOLD_HI, 'Goldlicht', 'Glanz, Randlicht'), (M.SN, 'Schlangengruen', 'nur die Erzaehlerin'),
          (M.SN_BELLY, 'Creme', 'Bauch, Kiefer'), (M.TIE, 'Krawattenrot', 'einziger Rotton')]
    for k, (c, n, use) in enumerate(sw):
        x = 80 + k * 255
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 130, 220, 150), 12, 12)
        cv.drawRRect(r, fillp(cv, c, 1, False))
        cv.drawRRect(r, strokep(cv, 2.4, '#4a4c4a'))
        text(cv, n, x, 320, TF_HEAD, 28, BONE_HI)
        text(cv, use, x, 352, TF_HEAD, 21, BONE_SH)
    extruded(cv, 'Will AI Buy Our Cars?', 80, 500, 84, BONE_HI, 8)
    text(cv, 'Playfair Display Black Italic  -  Titel, Kapitel, Pointen', 80, 548, TF_HEAD, 24, BONE_SH)
    P.draw_text(cv, 'THE PROPHECY ASSUMES', 80, 625, TF_CAPS, 34, fillp(cv, GOLD, 1, False), spacing=8)
    text(cv, 'Cinzel  -  Ueberschriften, Bauchbinden, Jahreszahlen', 80, 665, TF_HEAD, 24, BONE_SH)
    text(cv, '"How are you going to get them to buy cars?"', 80, 745, TF_TYPE, 40, BONE_HI)
    text(cv, 'Special Elite  -  echte Zitate und Dokumente', 80, 785, TF_HEAD, 24, BONE_SH)
    text(cv, 'RECORD PROFITS  ·  1 IN 4  ·  +312 %', 80, 865, TF_HEAD, 44, BONE_HI)
    text(cv, 'Oswald  -  Zahlen, Schlagzeilen, Diagramme', 80, 905, TF_HEAD, 24, BONE_SH)
    rules = ['Die Schlange erscheint, wenn sie spricht:',
             '  Enthuellung (P-10), Annahmen, Kapitelanfaenge,',
             '  Pointen, These (07-05), Schluss und Abspann.',
             'Sie fehlt in den Fiktionsszenen und echten',
             '  historischen Bildern: dort sprechen die Bilder.',
             'Ein Schattenton pro Flaeche, Licht oben links,',
             '  dunkler Versatzschatten hinter Figuren.',
             'Gold nur fuer EDEN und das, was er beruehrt.',
             'Jede Einstellung bewegt sich: langsame Fahrt.']
    P.draw_text(cv, 'REGELN', 1160, 445, TF_CAPS, 28, fillp(cv, GOLD, 1, False), spacing=6)
    for k, ln in enumerate(rules):
        text(cv, ln, 1160, 495 + k * 40, TF_HEAD, 25, BONE_HI if not ln.startswith('  ') else BONE)
    for k, (e, lab) in enumerate((('neutral', 'erzaehlt'), ('smug', 'Pointe'), ('worried', 'ernst'))):
        badge(cv, 1260 + k * 230, 935, 70, e, (0.1, 0.0), 0)
    finish(surf, out)


def badge(cv, x, y, r, expr, look, tilt):
    M.badge(cv, x, y, r, expr, look, tilt)


from rich_base import bust_front, person_profile
FRAMES.update({'horses': f_horses, 'reuther': f_reuther, 'cage': f_cage, 'board': f_board, 'style': f_style})

if __name__ == '__main__':
    P.init_assets()
    R.init_layers()
    for name in sys.argv[1].split(','):
        FRAMES[name](f'{sys.argv[2]}/{name}.png')
