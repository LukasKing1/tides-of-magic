#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Maskottchen, zweite Runde: sechs weitere Entwuerfe (D bis I).

python3 mascot2.py sheet <out.png>
"""
import math, sys
import skia
import rich_base as RB
import mascot as M
from rich_base import *

PAL = {
    'green': dict(g='#6e9b7d', gs='#567f67', gh='#94bd9f', spot='#4f7563', belly='#efe5c6', belly_sh='#d5c9a3'),
    'forest': dict(g='#4f7d5d', gs='#3e6449', gh='#70a07d', spot='#365642', belly='#e8dcb8', belly_sh='#cbbd94'),
    'teal': dict(g='#4f8f8a', gs='#3d726e', gh='#78b3ad', spot='#34605d', belly='#efe4c2', belly_sh='#d3c69e'),
    'mint': dict(g='#86bf9a', gs='#6aa47f', gh='#aad6b8', spot='#5c9170', belly='#f3ead0', belly_sh='#dccfa9'),
    'slate': dict(g='#6d8496', gs='#566b7b', gh='#91a7b7', spot='#4a5d6c', belly='#ece3c8', belly_sh='#d0c5a4'),
}


def set_palette(name):
    p = PAL[name]
    M.M_GREEN, M.M_GREEN_SH, M.M_GREEN_HI, M.M_SPOT = p['g'], p['gs'], p['gh'], p['spot']
    M.M_BELLY, M.M_BELLY_SH = p['belly'], p['belly_sh']
    RB.SNAKE, RB.SNAKE_SH, RB.SNAKE_HI = p['g'], p['spot'], p['gh']
    RB.BELLY, RB.BELLY_SH = p['belly'], p['belly_sh']


HEADS = {
    'round': [(0.0, -0.56), (0.30, -0.58, 0.58, -0.40, 0.62, -0.06), (0.65, 0.22, 0.42, 0.46, 0.0, 0.48),
              (-0.42, 0.46, -0.65, 0.22, -0.62, -0.06), (-0.58, -0.40, -0.30, -0.58, 0.0, -0.56)],
    'bean': [(0.0, -0.52), (0.26, -0.54, 0.50, -0.40, 0.56, -0.10), (0.66, 0.22, 0.48, 0.52, 0.0, 0.52),
             (-0.48, 0.52, -0.66, 0.22, -0.56, -0.10), (-0.50, -0.40, -0.26, -0.54, 0.0, -0.52)],
    'oval': [(0.0, -0.62), (0.28, -0.64, 0.53, -0.44, 0.56, -0.08), (0.58, 0.24, 0.38, 0.50, 0.0, 0.52),
             (-0.38, 0.50, -0.58, 0.24, -0.56, -0.08), (-0.53, -0.44, -0.28, -0.64, 0.0, -0.62)],
}


# ---------------------------------------------------------------- Accessoires
def monocle(cv, a):
    c = circle(0.25, -0.07, 0.21)
    cv.drawPath(c, fillp(cv, '#ffffff', .10 * a, False))
    cv.drawPath(c, strokep(cv, 0.055, INK, a))
    cv.drawPath(c, strokep(cv, 0.03, GOLD, a))
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(0.10, -0.22, 0.30, 0.30), 200, 50)
    cv.drawPath(hl, strokep(cv, 0.018, '#ffffff', .6 * a))
    ch = P_([(0.40, 0.04), (0.55, 0.30, 0.50, 0.55, 0.30, 0.70)], close=False)
    cv.drawPath(ch, strokep(cv, 0.022, GOLD_DK, a))
    for k in range(9):
        u = k / 8
        x = (1 - u) ** 3 * .40 + 3 * (1 - u) ** 2 * u * .55 + 3 * (1 - u) * u * u * .50 + u ** 3 * .30
        y = (1 - u) ** 3 * .04 + 3 * (1 - u) ** 2 * u * .30 + 3 * (1 - u) * u * u * .55 + u ** 3 * .70
        cv.drawCircle(x, y, 0.014, fillp(cv, GOLD, a, False))


def half_glasses(cv, a):
    for sx in (-1, 1):
        lens = P_([(sx * 0.25 - 0.17, 0.03), (sx * 0.25 + 0.17, 0.03), (sx * 0.25 + 0.17, 0.16, sx * 0.25 - 0.17, 0.16, sx * 0.25 - 0.17, 0.03)])
        cv.drawPath(lens, fillp(cv, '#ffffff', .12 * a, False))
        cv.drawPath(lens, strokep(cv, 0.05, INK, a))
        cv.drawPath(lens, strokep(cv, 0.026, GOLD, a))
    br = P_([(-0.08, 0.04), (0.0, 0.0, 0.0, 0.0, 0.08, 0.04)], close=False)
    cv.drawPath(br, strokep(cv, 0.045, INK, a))
    cv.drawPath(br, strokep(cv, 0.022, GOLD, a))
    for sx in (-1, 1):
        arm = P_([(sx * 0.42, 0.04), (sx * 0.60, -0.08)], close=False)
        cv.drawPath(arm, strokep(cv, 0.04, INK, a))
        cv.drawPath(arm, strokep(cv, 0.02, GOLD, a))


def flatcap(cv, a):
    cv.save()
    cv.translate(0.0, -0.40)
    cv.rotate(-6)
    cap = P_([(-0.50, 0.02), (-0.52, -0.20, -0.20, -0.32, 0.12, -0.30), (0.40, -0.28, 0.56, -0.14, 0.52, 0.0)])
    draw(cv, cap, '#6a5643', a, shade=P_([(-0.6, -0.08), (0.6, -0.08), (0.6, 0.1), (-0.6, 0.1)]), shade_col='#54443a',
         hi=P_([(-0.30, -0.20), (-0.05, -0.27), (-0.04, -0.23), (-0.28, -0.16)]), hi_col='#86705a')
    brim = P_([(0.20, 0.00), (0.52, -0.02), (0.74, 0.04, 0.70, 0.12, 0.50, 0.10), (0.20, 0.08)])
    draw(cv, brim, '#5a4838', a)
    for k in range(4):
        cv.drawLine(-0.40 + k * .2, -0.24 + k * .01, -0.36 + k * .2, 0.0, strokep(cv, 0.012, '#54443a', .7 * a))
    cv.drawCircle(0.06, -0.31, 0.035, fillp(cv, '#54443a', a, False))
    cv.restore()


def fedora(cv, a):
    cv.save()
    cv.translate(0.04, -0.50)
    cv.rotate(-8)
    brim = P_([(-0.58, 0.02), (-0.40, -0.10, 0.40, -0.10, 0.60, 0.00), (0.40, 0.10, -0.40, 0.12, -0.58, 0.02)])
    crown = P_([(-0.30, -0.02), (-0.34, -0.36), (-0.10, -0.40), (0.0, -0.32), (0.10, -0.40), (0.34, -0.36), (0.30, -0.02)])
    draw(cv, brim, '#33302d', a, shade=P_([(-0.7, 0.03), (0.7, 0.03), (0.7, 0.2), (-0.7, 0.2)]), shade_col='#24221f')
    draw(cv, crown, '#3b3734', a, shade=P_([(0.06, -0.45), (0.4, -0.45), (0.4, 0.05), (0.06, 0.05)]), shade_col='#2a2725')
    band = P_([(-0.305, -0.10), (0.305, -0.10), (0.30, -0.02), (-0.30, -0.02)])
    draw(cv, band, GOLD, a, px=OW * .8)
    cv.restore()


def headphones(cv, a):
    band = skia.Path()
    band.addArc(skia.Rect.MakeXYWH(-0.64, -0.70, 1.28, 1.28), 195, 150)
    cv.drawPath(band, strokep(cv, 0.11, INK, a))
    cv.drawPath(band, strokep(cv, 0.07, '#3a3b3d', a))
    for sx in (-1, 1):
        cup = skia.Path()
        cup.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx * 0.62 - 0.09, -0.24, 0.18, 0.32), 0.07, 0.07))
        draw(cv, cup, '#2e2f31', a, hi=P_([(sx * 0.62 - 0.05, -0.20), (sx * 0.62 + 0.0, -0.20), (sx * 0.62, 0.0), (sx * 0.62 - 0.05, 0.0)]),
             hi_col='#4a4c4f')
        cv.drawCircle(sx * 0.62, -0.08, 0.04, fillp(cv, GOLD, a, False))
    boom = P_([(-0.62, 0.04), (-0.62, 0.26, -0.48, 0.36, -0.26, 0.34)], close=False)
    cv.drawPath(boom, strokep(cv, 0.05, INK, a))
    cv.drawPath(boom, strokep(cv, 0.026, '#3a3b3d', a))
    mic = skia.Path()
    mic.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-0.30, 0.30, 0.10, 0.08), 0.04, 0.04))
    draw(cv, mic, '#2e2f31', a, px=OW * .8)


def scarf(cv, a):
    cv.save()
    cv.translate(0.0, 0.58)
    wrap = P_([(-0.36, -0.08), (0.0, -0.02), (0.36, -0.08), (0.36, 0.10), (0.0, 0.16), (-0.36, 0.10)])
    tail = P_([(0.10, 0.06), (0.30, 0.08), (0.34, 0.50), (0.16, 0.52)])
    for path in (tail, wrap):
        draw(cv, path, '#9c4436', a, shade=P_([(0.0, 0.06), (0.6, 0.06), (0.6, 0.6), (0.0, 0.6)]), shade_col='#7e3529')
        cv.save()
        cv.clipPath(path, doAntiAlias=True)
        for k in range(-6, 8):
            cv.drawLine(-0.4 + k * 0.1, -0.2, -0.3 + k * 0.1, 0.6, strokep(cv, 0.025, '#e8dcb8', .55 * a))
        cv.restore()
        cv.drawPath(path, inkp(cv, OW, INK, a))
    for k in range(4):
        cv.drawLine(0.17 + k * .05, 0.52, 0.17 + k * .05, 0.58, strokep(cv, 0.018, '#9c4436', a))
    cv.restore()


def tie(cv, a):
    cv.save()
    cv.translate(0.0, 0.52)
    knot = P_([(-0.06, 0.0), (0.06, 0.0), (0.045, 0.08), (-0.045, 0.08)])
    blade = P_([(-0.045, 0.08), (0.045, 0.08), (0.09, 0.40), (0.0, 0.48), (-0.09, 0.40)])
    draw(cv, blade, GOLD, a, shade=P_([(0.0, 0.08), (0.2, 0.08), (0.2, 0.5), (0.0, 0.5)]), shade_col=GOLD_SH)
    draw(cv, knot, GOLD_SH, a, px=OW * .8)
    cv.restore()


def coin(cv, x, y, r, a):
    cv.drawCircle(x, y, r * 1.6, glowp(cv, GOLD_HI, r * .9 * mscale(cv), .35 * a))
    c = circle(x, y, r)
    draw(cv, c, GOLD, a, hi=P_([(x - r * .7, y - r * .3), (x - r * .2, y - r * .8), (x, y - r * .7), (x - r * .55, y - r * .1)]),
         hi_col=GOLD_HI)
    cv.drawCircle(x, y, r * .72, strokep(cv, max(1.0, r * .07), GOLD_DK, a))
    text(cv, '$', x, y + r * .34, P.TF_HEAD, r * 1.0, GOLD_DK, a, anchor='c')


def watch(cv, x, y, r, a):
    cv.drawCircle(x, y, r * 1.5, glowp(cv, GOLD_HI, r * .8 * mscale(cv), .25 * a))
    cv.drawCircle(x, y - r * 1.12, r * .2, strokep(cv, r * .08, GOLD, a))
    c = circle(x, y, r)
    draw(cv, c, GOLD, a)
    f = circle(x, y, r * .78)
    draw(cv, f, '#f3ead0', a, px=OW * .8)
    for k in range(12):
        an = math.radians(k * 30)
        cv.drawLine(x + math.cos(an) * r * .6, y + math.sin(an) * r * .6, x + math.cos(an) * r * .7, y + math.sin(an) * r * .7,
                    strokep(cv, r * .04, INK, a))
    cv.drawLine(x, y, x + r * .32, y - r * .30, strokep(cv, r * .07, INK, a))
    cv.drawLine(x, y, x, y - r * .55, strokep(cv, r * .05, INK, a))
    cv.drawCircle(x, y, r * .06, fillp(cv, INK, a, False))


# ---------------------------------------------------------------- Figur
def eye_dot(cv, ex, ey, look, a):
    lx, ly = look
    e = skia.Path()
    e.addOval(skia.Rect.MakeXYWH(ex - 0.085 + lx * .03, ey - 0.11 + ly * .03, 0.17, 0.22))
    cv.drawPath(e, fillp(cv, INK, a, False))
    cv.drawCircle(ex - 0.03 + lx * .03, ey - 0.05 + ly * .03, 0.035, fillp(cv, '#ffffff', a, False))
    cv.drawCircle(ex + 0.03 + lx * .03, ey + 0.04 + ly * .03, 0.014, fillp(cv, '#ffffff', .8 * a, False))


def head(cv, x, y, s, cfg, expr='smile', look=(0.0, 0.0), tongue=0.0, tilt=0.0, a=1.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(tilt)
    cv.scale(s, s)
    if 'headphones_back' in cfg.get('head', ()):
        pass
    hp = P_(HEADS[cfg.get('shape', 'round')])
    draw(cv, hp, M.M_GREEN, a, shade=cel(hp, -0.10, -0.05), shade_col=M.M_GREEN_SH,
         hi=P_([(-0.40, -0.40), (-0.20, -0.52), (-0.16, -0.47), (-0.36, -0.34)]), hi_col=M.M_GREEN_HI)
    cv.save()
    cv.clipPath(hp, doAntiAlias=True)
    muz = skia.Path()
    muz.addOval(skia.Rect.MakeXYWH(-0.40, 0.08, 0.80, 0.52))
    cv.drawPath(muz, fillp(cv, M.M_BELLY, a, False))
    cv.drawOval(skia.Rect.MakeXYWH(-0.40, 0.32, 0.80, 0.40), fillp(cv, M.M_BELLY_SH, a, False))
    for (sx, sy, r) in ((-0.14, -0.43, .045), (0.0, -0.47, .05), (0.14, -0.43, .045)):
        cv.drawCircle(sx, sy, r, fillp(cv, M.M_SPOT, .9 * a, False))
    cv.restore()
    cv.drawPath(hp, inkp(cv, OW * 1.1, INK, a))
    for sx in (-1, 1):
        cv.drawCircle(sx * 0.37, 0.15, 0.075, fillp(cv, M.M_BLUSH, .45 * a, False))
    style = cfg.get('eyes', 'round')
    if style == 'dot':
        for sx in (-1, 1):
            eye_dot(cv, sx * 0.24, -0.07, look, a)
    else:
        lid = {'smile': 0.0, 'smirk': .42, 'o': 0.0, 'flat': .25, 'open': .05}.get(expr, 0)
        if style == 'sleepy':
            lid = max(lid, .42)
        for sx in (-1, 1):
            M.eye(cv, sx * 0.25, -0.07, 0.16, look, lid, expr == 'o', a)
    for sx in (-1, 1):
        cv.save()
        cv.translate(sx * 0.25, -0.31 if style != 'sleepy' else -0.27)
        cv.rotate(sx * (-6 if style == 'sleepy' else 0))
        cv.drawPath(P_([(-0.10, 0.01), (0.0, -0.02, 0.0, -0.02, 0.10, 0.01)], close=False), strokep(cv, 0.035, M.M_SPOT, a))
        cv.restore()
    for sx in (-1, 1):
        cv.drawCircle(sx * 0.055, 0.19, 0.018, fillp(cv, INK, .8 * a, False))
    M.mouth(cv, expr, tongue, a)
    for acc in cfg.get('head', ()):
        {'glasses': M.glasses, 'half': half_glasses, 'monocle': monocle, 'bowler': M.bowler, 'tophat': M.tophat,
         'flatcap': flatcap, 'fedora': fedora, 'headphones': headphones}[acc](cv, a)
    cv.restore()


def body(cv, x, y, s, t=0.0, tail_up=False, a=1.0):
    cx, cy, rx, ry = x + s * 0.05, y + s * 1.50, s * 0.92, s * 0.25
    p0, p1, p2, p3 = (x, y + .30 * s), (x + .06 * s, y + 1.05 * s), (cx - .50 * s, cy + ry), (cx, cy + ry)
    pts = []
    for i in range(28):
        u = i / 27
        px = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0]
        py = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]
        pts.append((px, py + s * .02 * math.sin(t * 1.5 + u * 3), 1.0))
    end = -235 if not tail_up else -205
    for i in range(1, 100):
        u = i / 99
        th = math.radians(lerp(90, end, u))
        k = lerp(1.0, .86, u)
        pts.append((cx + rx * k * math.cos(th), cy + ry * k * math.sin(th), math.sin(th)))
    tip = None
    if tail_up:
        sx_, sy_ = pts[-1][:2]
        q0, q1, q2, q3 = (sx_, sy_), (sx_ - .35 * s, sy_ + .05 * s), (x - 1.15 * s, y + .75 * s), (x - .92 * s, y + .50 * s)
        for i in range(1, 30):
            u = i / 29
            px = (1 - u) ** 3 * q0[0] + 3 * (1 - u) ** 2 * u * q1[0] + 3 * (1 - u) * u * u * q2[0] + u ** 3 * q3[0]
            py = (1 - u) ** 3 * q0[1] + 3 * (1 - u) ** 2 * u * q1[1] + 3 * (1 - u) * u * u * q2[1] + u ** 3 * q3[1]
            pts.append((px, py, 1.0))
        tip = pts[-1][:2]
    n = len(pts)
    wd = [s * (0.40 if i < 60 else lerp(0.40, 0.09, (i - 60) / (n - 61))) for i in range(n)]
    rs = M.R_runs(pts, wd)
    for front, p, w in rs:
        if not front:
            snake_body(cv, p, w, a, belly=.5)
    for k, (front, p, w) in enumerate(rs):
        if front:
            snake_body(cv, p, w, a, belly=.5, bdir=(1.0, 0.3) if k == 0 else (0.0, 1.0))
    return tip


def figure(cv, x, y, s, cfg, expr='smile', look=(0.15, 0.1), tongue=0.0, tilt=0.0, t=0.0):
    set_palette(cfg.get('pal', 'green'))
    tip = body(cv, x, y, s, t, tail_up=bool(cfg.get('prop')))
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    for acc in cfg.get('neck', ()):
        {'bowtie': M.bowtie, 'scarf': scarf, 'tie': tie}[acc](cv, 1.0)
    cv.restore()
    head(cv, x, y, s, cfg, expr, look, tongue, tilt)
    if tip is not None:
        {'coin': coin, 'watch': watch}[cfg['prop']](cv, tip[0] + s * .02, tip[1] - s * .14, s * .17, 1.0)


VARIANTS = [
    ('D', 'Der Oekonom', 'Monokel, Melone, Muenze', dict(pal='green', head=('monocle', 'bowler'), prop='coin')),
    ('E', 'Die Professorin', 'Lesebrille, Schal', dict(pal='teal', shape='oval', head=('half',), neck=('scarf',))),
    ('F', 'Der Arbeiter', 'Schiebermuetze, Rundbrille', dict(pal='forest', head=('glasses', 'flatcap'))),
    ('G', 'Der Erzaehler', 'Knopfaugen, Kopfhoerer', dict(pal='mint', shape='bean', eyes='dot', head=('headphones',))),
    ('H', 'Der Charmeur', 'Schlafzimmerblick, Fedora, Krawatte', dict(pal='slate', shape='oval', eyes='sleepy', head=('fedora',), neck=('tie',))),
    ('I', 'Die Historikerin', 'Rundbrille, Taschenuhr', dict(pal='green', eyes='round', head=('glasses',), prop='watch', neck=('bowtie',))),
]


def sheet(out):
    from PIL import Image
    P.init_assets()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    P.G.zoom = 1.0
    text(cv, 'DIE SCHLANGE  -  WEITERE ENTWUERFE', W / 2, 62, P.TF_CAPS, 28, GOLD, anchor='c', spacing=8)
    for k, (v, name, desc, cfg) in enumerate(VARIANTS):
        col_, row = k % 3, k // 3
        x, y = 360 + col_ * 600, 225 + row * 470
        cv.drawCircle(x, y + 110, 230, glowp(cv, GOLD_HI, 90, .09))
        expr = 'smirk' if cfg.get('eyes') == 'sleepy' else 'smile'
        figure(cv, x, y, 128, cfg, expr=expr, tongue=.5 if v == 'G' else 0, tilt=(-5 if v in 'DH' else 3 if v == 'E' else 0))
        text(cv, f'{v}   {name}', x, y + 300, P.TF_HEAD, 32, BONE_HI, anchor='c')
        text(cv, desc, x, y + 336, P.TF_HEAD, 22, BONE_SH, anchor='c')
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    Image.fromarray(P.Post().apply(img, 0)).save(out)
    print('saved', out)


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2])
