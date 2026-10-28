#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Maskottchen: die Schlange als Kanalfigur (Entwuerfe).

python3 mascot.py sheet <out.png>
"""
import math, sys
import skia
from rich_base import *

M_GREEN = '#6e9b7d'
M_GREEN_SH = '#567f67'
M_GREEN_HI = '#94bd9f'
M_SPOT = '#4f7563'
M_BELLY = '#efe5c6'
M_BELLY_SH = '#d5c9a3'
M_IRIS = '#e3a73c'
M_IRIS_DK = '#b07a22'
M_HAT = '#2a2a2e'
M_HAT_HI = '#3d3d43'
M_BLUSH = '#e59a86'


def head_path():
    return P_([(0.0, -0.56), (0.30, -0.58, 0.58, -0.40, 0.62, -0.06), (0.65, 0.22, 0.42, 0.46, 0.0, 0.48),
               (-0.42, 0.46, -0.65, 0.22, -0.62, -0.06), (-0.58, -0.40, -0.30, -0.58, 0.0, -0.56)])


def eye(cv, ex, ey, r, look, lid, wide, a):
    sc = circle(ex, ey, r * (1.08 if wide else 1.0))
    draw(cv, sc, '#fbf8ef', a, px=OW * .9)
    cv.save()
    cv.clipPath(sc, doAntiAlias=True)
    lx, ly = look
    ir = r * .68
    cv.drawCircle(ex + lx * r * .28, ey + ly * r * .22, ir, fillp(cv, M_IRIS, a, False))
    cv.drawCircle(ex + lx * r * .28, ey + ly * r * .22 + ir * .35, ir * .9, fillp(cv, M_IRIS_DK, .35 * a, False))
    cv.drawCircle(ex + lx * r * .30, ey + ly * r * .24, ir * (.5 if not wide else .38), fillp(cv, INK, a, False))
    cv.drawCircle(ex + lx * r * .30 - ir * .32, ey + ly * r * .24 - ir * .36, ir * .22, fillp(cv, '#ffffff', a, False))
    cv.drawCircle(ex + lx * r * .30 + ir * .25, ey + ly * r * .24 + ir * .25, ir * .09, fillp(cv, '#ffffff', .8 * a, False))
    if lid > 0:
        cv.drawRect(skia.Rect.MakeLTRB(ex - r * 1.2, ey - r * 1.2, ex + r * 1.2, ey - r + 2 * r * lid), fillp(cv, M_GREEN, a, False))
        cv.drawLine(ex - r * 1.2, ey - r + 2 * r * lid, ex + r * 1.2, ey - r + 2 * r * lid, inkp(cv, OW * .9, INK, a, wob=False))
    cv.restore()
    cv.drawPath(sc, inkp(cv, OW * .9, INK, a))


def mouth(cv, kind, tongue, a):
    if kind == 'smile':
        m = P_([(-0.20, 0.27), (-0.08, 0.37, 0.08, 0.37, 0.20, 0.27)], close=False)
        cv.drawPath(m, inkp(cv, OW * 1.1, INK, a))
    elif kind == 'smirk':
        m = P_([(-0.16, 0.31), (-0.02, 0.35, 0.12, 0.33, 0.21, 0.24)], close=False)
        cv.drawPath(m, inkp(cv, OW * 1.1, INK, a))
    elif kind == 'flat':
        cv.drawPath(P_([(-0.13, 0.31), (0.0, 0.32, 0.0, 0.32, 0.13, 0.31)], close=False), inkp(cv, OW * 1.1, INK, a))
    elif kind in ('o', 'open'):
        if kind == 'o':
            mp = skia.Path()
            mp.addOval(skia.Rect.MakeXYWH(-0.07, 0.25, 0.14, 0.13))
        else:
            mp = P_([(-0.19, 0.26), (0.0, 0.28), (0.19, 0.26), (0.12, 0.40, -0.12, 0.40, -0.19, 0.26)])
        draw(cv, mp, '#4a2a2a', a, px=OW)
        cv.save()
        cv.clipPath(mp, doAntiAlias=True)
        cv.drawOval(skia.Rect.MakeXYWH(-0.10, 0.33, 0.20, 0.12), fillp(cv, '#c0665a', a, False))
        cv.restore()
        cv.drawPath(mp, inkp(cv, OW, INK, a))
    if tongue > 0:
        L = 0.22 * math.sin(math.pi * clamp(tongue))
        tg = skia.Path()
        tg.moveTo(0.0, 0.36)
        tg.lineTo(0.0, 0.36 + L)
        tg.moveTo(0.0, 0.36 + L)
        tg.lineTo(-0.05, 0.36 + L + 0.06)
        tg.moveTo(0.0, 0.36 + L)
        tg.lineTo(0.05, 0.36 + L + 0.06)
        cv.drawPath(tg, strokep(cv, 0.045, INK, a))
        cv.drawPath(tg, strokep(cv, 0.025, '#c4574a', a))


def glasses(cv, a):
    for sx in (-1, 1):
        c = circle(sx * 0.25, -0.07, 0.205)
        cv.drawPath(c, fillp(cv, '#ffffff', .10 * a, False))
        cv.drawPath(c, strokep(cv, 0.05, INK, a))
        cv.drawPath(c, strokep(cv, 0.026, GOLD, a))
        hl = skia.Path()
        hl.addArc(skia.Rect.MakeXYWH(sx * 0.25 - 0.15, -0.22, 0.30, 0.30), 200, 50)
        cv.drawPath(hl, strokep(cv, 0.018, '#ffffff', .55 * a))
    br = P_([(-0.07, -0.10), (0.0, -0.15, 0.0, -0.15, 0.07, -0.10)], close=False)
    cv.drawPath(br, strokep(cv, 0.05, INK, a))
    cv.drawPath(br, strokep(cv, 0.026, GOLD, a))
    for sx in (-1, 1):
        arm = P_([(sx * 0.455, -0.09), (sx * 0.60, -0.10)], close=False)
        cv.drawPath(arm, strokep(cv, 0.045, INK, a))
        cv.drawPath(arm, strokep(cv, 0.022, GOLD, a))


def bowler(cv, a):
    cv.save()
    cv.translate(0.06, -0.50)
    cv.rotate(-9)
    brim = skia.Path()
    brim.addOval(skia.Rect.MakeXYWH(-0.47, -0.06, 0.94, 0.15))
    dome = P_([(-0.31, 0.02), (-0.33, -0.36, 0.33, -0.36, 0.31, 0.02)])
    draw(cv, brim, M_HAT, a, shade=P_([(-0.5, 0.03), (0.5, 0.03), (0.5, 0.2), (-0.5, 0.2)]), shade_col='#1c1c1f')
    draw(cv, dome, M_HAT, a, shade=P_([(0.08, -0.4), (0.4, -0.4), (0.4, 0.05), (0.08, 0.05)]), shade_col='#1c1c1f',
         hi=P_([(-0.24, -0.20), (-0.14, -0.27), (-0.12, -0.24), (-0.21, -0.15)]), hi_col=M_HAT_HI)
    band = P_([(-0.315, -0.04), (0.315, -0.04), (0.31, 0.02), (-0.31, 0.02)])
    draw(cv, band, GOLD, a, px=OW * .8)
    cv.restore()


def tophat(cv, a):
    cv.save()
    cv.translate(0.08, -0.52)
    cv.rotate(-10)
    brim = skia.Path()
    brim.addOval(skia.Rect.MakeXYWH(-0.40, -0.05, 0.80, 0.13))
    crown = P_([(-0.24, 0.02), (-0.27, -0.52), (0.27, -0.52), (0.24, 0.02)])
    draw(cv, brim, M_HAT, a, shade=P_([(-0.5, 0.03), (0.5, 0.03), (0.5, 0.2), (-0.5, 0.2)]), shade_col='#1c1c1f')
    draw(cv, crown, M_HAT, a, shade=P_([(0.08, -0.55), (0.3, -0.55), (0.3, 0.05), (0.08, 0.05)]), shade_col='#1c1c1f',
         hi=P_([(-0.20, -0.46), (-0.13, -0.46), (-0.13, -0.10), (-0.18, -0.10)]), hi_col=M_HAT_HI)
    top = skia.Path()
    top.addOval(skia.Rect.MakeXYWH(-0.27, -0.56, 0.54, 0.08))
    draw(cv, top, '#333338', a, px=OW * .8)
    band = P_([(-0.245, -0.06), (0.245, -0.06), (0.24, 0.02), (-0.24, 0.02)])
    draw(cv, band, GOLD, a, px=OW * .8)
    cv.restore()


def bowtie(cv, a):
    cv.save()
    cv.translate(0.0, 0.56)
    for sx in (-1, 1):
        w = P_([(0, 0), (sx * 0.20, -0.10), (sx * 0.22, 0.10)])
        draw(cv, w, '#9c4436', a, shade=P_([(0, 0.02), (sx * 0.3, 0.02), (sx * 0.3, 0.2), (0, 0.2)]), shade_col='#7a3329')
    k = skia.Path()
    k.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-0.05, -0.05, 0.10, 0.10), 0.03, 0.03))
    draw(cv, k, '#b5523f', a, px=OW * .8)
    cv.restore()


def mascot_head(cv, x, y, s, variant='A', expr='smile', look=(0.0, 0.0), tongue=0.0, tilt=0.0, a=1.0):
    """Kopf von vorn. (x, y) = Kopfmitte, s = Kopfbreite in Pixeln."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(tilt)
    cv.scale(s, s)
    hp = head_path()
    draw(cv, hp, M_GREEN, a, shade=cel(hp, -0.10, -0.05), shade_col=M_GREEN_SH,
         hi=P_([(-0.40, -0.40), (-0.20, -0.52), (-0.16, -0.47), (-0.36, -0.34)]), hi_col=M_GREEN_HI)
    cv.save()
    cv.clipPath(hp, doAntiAlias=True)
    muz = skia.Path()
    muz.addOval(skia.Rect.MakeXYWH(-0.40, 0.08, 0.80, 0.50))
    cv.drawPath(muz, fillp(cv, M_BELLY, a, False))
    cv.drawOval(skia.Rect.MakeXYWH(-0.40, 0.30, 0.80, 0.40), fillp(cv, M_BELLY_SH, a, False))
    for (sx, sy, r) in ((-0.14, -0.43, .045), (0.0, -0.47, .05), (0.14, -0.43, .045)):
        cv.drawCircle(sx, sy, r, fillp(cv, M_SPOT, .9 * a, False))
    cv.restore()
    cv.drawPath(hp, inkp(cv, OW * 1.1, INK, a))
    for sx in (-1, 1):
        cv.drawCircle(sx * 0.37, 0.15, 0.075, fillp(cv, M_BLUSH, .45 * a, False))
    lid = {'smile': 0.0, 'smirk': .42, 'o': 0.0, 'flat': .25, 'open': .05}.get(expr, 0)
    wide = expr == 'o'
    for sx in (-1, 1):
        eye(cv, sx * 0.25, -0.07, 0.16, look, lid if not (expr == 'smirk' and sx < 0) else lid * .7, wide, a)
    bro = {'smile': (-0.30, 0.0), 'smirk': (-0.28, 6.0), 'o': (-0.36, 0.0), 'flat': (-0.27, -8.0), 'open': (-0.31, 0.0)}
    by, bang = bro.get(expr, (-0.3, 0))
    for sx in (-1, 1):
        cv.save()
        cv.translate(sx * 0.25, by)
        cv.rotate(sx * bang if expr != 'smirk' else (bang if sx > 0 else -2))
        cv.drawPath(P_([(-0.10, 0.01), (0.0, -0.02, 0.0, -0.02, 0.10, 0.01)], close=False), strokep(cv, 0.035, M_SPOT, a))
        cv.restore()
    for sx in (-1, 1):
        cv.drawCircle(sx * 0.055, 0.19, 0.018, fillp(cv, INK, .8 * a, False))
    mouth(cv, expr, tongue, a)
    if variant in ('A', 'B', 'C'):
        glasses(cv, a)
    if variant == 'A':
        bowler(cv, a)
    elif variant == 'C':
        tophat(cv, a)
    cv.restore()


def mascot_body(cv, x, y, s, t=0.0, a=1.0):
    """Hals vorn herab, eine Windung am Boden, Schwanz links vorn. (x, y) = Kopfmitte."""
    cx, cy, rx, ry = x + s * 0.05, y + s * 1.50, s * 0.92, s * 0.25
    p0, p1, p2, p3 = (x, y + .30 * s), (x + .06 * s, y + 1.05 * s), (cx - .50 * s, cy + ry), (cx, cy + ry)
    neck = []
    for i in range(28):
        u = i / 27
        px = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0]
        py = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]
        neck.append((px, py + s * .02 * math.sin(t * 1.5 + u * 3), 1.0))
    loop = []
    for i in range(1, 100):
        u = i / 99
        th = math.radians(lerp(90, -235, u))
        k = lerp(1.0, .82, u)
        loop.append((cx + rx * k * math.cos(th), cy + ry * k * math.sin(th), math.sin(th)))
    body = neck + loop
    n = len(body)
    wd = [s * (0.40 if i < 60 else lerp(0.40, 0.08, (i - 60) / (n - 61))) for i in range(n)]
    rs = R_runs(body, wd)
    for front, p, w in rs:
        if not front:
            snake_body(cv, p, w, a, belly=.5)
    for k, (front, p, w) in enumerate(rs):
        if front:
            snake_body(cv, p, w, a, belly=.5, bdir=(1.0, 0.3) if k == 0 else (0.0, 1.0))


def R_runs(pts, wd):
    out, cur, curw, side = [], [], [], None
    for p, w in zip(pts, wd):
        sd = p[2] >= 0
        if side is None or sd == side:
            cur.append(p)
            curw.append(w)
        else:
            out.append((side, cur + [p], curw + [w]))
            cur, curw = [cur[-1], p], [curw[-1], w]
        side = sd
    out.append((side, cur, curw))
    return out


def recolor_snake():
    import rich_base as RB
    RB.SNAKE, RB.SNAKE_SH, RB.SNAKE_HI = M_GREEN, M_SPOT, M_GREEN_HI
    RB.BELLY, RB.BELLY_SH = M_BELLY, M_BELLY_SH
    globals().update(SNAKE=M_GREEN, SNAKE_SH=M_SPOT, SNAKE_HI=M_GREEN_HI, BELLY=M_BELLY, BELLY_SH=M_BELLY_SH)


def sheet(out):
    from PIL import Image
    P.init_assets()
    recolor_snake()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    P.G.zoom = 1.0
    text(cv, 'DIE SCHLANGE  -  ENTWUERFE', W / 2, 70, P.TF_CAPS, 30, GOLD, anchor='c', spacing=8)
    labels = [('A', 'Brille und Melone'), ('B', 'Brille und Fliege'), ('C', 'Brille und Zylinder')]
    for k, (v, lab) in enumerate(labels):
        x = 330 + k * 630
        cv.drawCircle(x, 400, 290, glowp(cv, GOLD_HI, 110, .10))
        mascot_body(cv, x, 285, 185)
        if v == 'B':
            cv.save()
            cv.translate(x, 285)
            cv.scale(185, 185)
            bowtie(cv, 1.0)
            cv.restore()
        mascot_head(cv, x, 285, 185, v, 'smile', look=(0.15, 0.1), tilt=-4 + 4 * k)
        text(cv, v + '   ' + lab, x, 712, P.TF_HEAD, 34, BONE_HI, anchor='c')
    cv.drawLine(120, 735, W - 120, 735, strokep(cv, 2, '#3a3b39'))
    text(cv, 'AUSDRUECKE  (ENTWURF A)', W / 2, 772, P.TF_CAPS, 24, GOLD, anchor='c', spacing=6)
    exprs = [('smile', 'freundlich', (0.1, 0.1), 0), ('smirk', 'verschmitzt', (0.3, 0.0), 0), ('o', 'ueberrascht', (0.0, -0.2), 0),
             ('flat', 'ernst', (0.0, 0.2), 0), ('open', 'erzaehlt', (0.2, 0.1), .6)]
    for k, (e, lab, look, tg) in enumerate(exprs):
        x = 260 + k * 350
        mascot_head(cv, x, 935, 140, 'A', e, look=look, tongue=tg, tilt=(-5 if e == 'smirk' else 0))
        text(cv, lab, x, 1060, P.TF_HEAD, 26, BONE, anchor='c')
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    post = P.Post()
    Image.fromarray(post.apply(img, 0)).save(out)
    print('saved', out)


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2])
