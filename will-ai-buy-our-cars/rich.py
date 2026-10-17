#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Testanimation v4: Prophezeiung P-01 bis P-11 + Titel, im Niveau von Rational Animations.

Rendern:   python3 rich.py render <startframe> <endframe> <out.mp4>
Standbild: python3 rich.py still <sekunde> <out.png> [<sekunde> <out.png> ...]
"""
import math, random, subprocess, sys
import numpy as np
import skia
from rich_base import *

# duennere Konturen fuer wiederverwendete Bausteine aus prophecy.py
_orig_ink = P.P_ink


def _thin_ink(w=4.0, c=P.INK, a=1.0, wobble=True, cap=True):
    if c == P.INK and w <= 8:
        w *= .62
    return _orig_ink(w, c, a, wobble, cap)


P.P_ink = _thin_ink
TF_HEAD, TF_TITLE, TF_CAPS, TF_SUB, TF_TYPE = P.TF_HEAD, P.TF_TITLE, P.TF_CAPS, P.TF_SUB, P.TF_TYPE


def cam(cv, cx, cy, z):
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-cx, -cy)
    P.G.zoom = z


def dust(cv, t, region, n=40, seed=1, c=GOLD_HI, a=.5):
    x0, y0, x1, y1 = region
    rnd = random.Random(seed)
    for i in range(n):
        bx, by = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        sp = rnd.uniform(6, 16)
        ph = rnd.uniform(0, 6.3)
        x = bx + 18 * math.sin(t * .4 + ph)
        y = y0 + ((by - y0 - t * sp) % (y1 - y0))
        r = rnd.uniform(1.2, 3.0)
        tw = .5 + .5 * math.sin(t * 2 + ph)
        cv.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=col(c, a * tw)))


# ================================================================ Stadt-Ebenen (vorgerendert)
LAYER_W = W + 600


def make_layer(seed, n_h, ground, front_c, side_c, haze, win_p, gold=False, sw=26, ink_px=2.4):
    rnd = random.Random(seed)
    surf = skia.Surface(LAYER_W, H)
    cv = surf.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    rects = []
    x = -40
    while x < LAYER_W:
        w = rnd.uniform(90, 190)
        h = rnd.uniform(*n_h)
        top = ground - h
        k = rnd.random()
        fc = mix(front_c, '#3a3122', .55) if gold else front_c
        side = poly([(x - sw, top + sw * .45), (x, top), (x, H + 50), (x - sw, H + 50)])
        cv.drawPath(side, skia.Paint(AntiAlias=True, Color=col(side_c)))
        front = skia.Path()
        front.addRect(skia.Rect.MakeLTRB(x, top, x + w, H + 50))
        if k < .25:
            front.addRect(skia.Rect.MakeXYWH(x + w * .3, top - 46, 5, 46))
        elif k < .45:
            front.addRect(skia.Rect.MakeXYWH(x + w * .5, top - 24, w * .32, 24))
        elif k < .6:
            front = union([front, poly([(x, top), (x + w * .5, top - 30), (x + w, top)])])
        cv.drawPath(front, skia.Paint(AntiAlias=True, Color=col(fc)))
        cv.drawLine(x + 2, top + 2, x + w - 2, top + 2, skia.Paint(AntiAlias=True, Color=col(mix(fc, BONE, .18)),
                                                                     StrokeWidth=3, Style=skia.Paint.kStroke_Style))
        ip = skia.Paint(AntiAlias=True, Color=col(INK), Style=skia.Paint.kStroke_Style, StrokeWidth=ink_px,
                        StrokeJoin=skia.Paint.kRound_Join)
        cv.drawPath(front, ip)
        cv.drawPath(side, ip)
        cols, rows = int((w - 18) // 24), int((h - 24) // 34)
        for cx in range(cols):
            for cy in range(rows):
                r1 = rnd.random()
                wx, wy = x + 12 + cx * 24, top + 18 + cy * 34
                if gold and r1 < .75:
                    cv.drawRect(skia.Rect.MakeXYWH(wx - 4, wy - 4, 19, 24), glowp(cv, GOLD_HI, 6, .35))
                    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 11, 16), skia.Paint(AntiAlias=True, Color=col(GOLD)))
                elif r1 < win_p:
                    cv.drawRect(skia.Rect.MakeXYWH(wx - 3, wy - 3, 17, 22), glowp(cv, '#d8c48f', 5, .25))
                    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 11, 16), skia.Paint(AntiAlias=True, Color=col('#cdb98a', .85)))
                else:
                    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, 11, 16), skia.Paint(AntiAlias=True, Color=col(mix(fc, '#000000', .25))))
        rects.append((x - sw, top - 46, x + w, H + 50))
        x += w + rnd.uniform(-10, 30)
    if haze > 0:
        cv.drawRect(skia.Rect.MakeWH(LAYER_W, H), skia.Paint(Color=col(BG, haze), BlendMode=skia.BlendMode.kSrcATop))
        fog = skia.Paint(BlendMode=skia.BlendMode.kSrcATop)
        fog.setShader(skia.GradientShader.MakeLinear([skia.Point(0, ground - 160), skia.Point(0, ground + 60)],
                                                     [col(BG, 0), col(BG, .8)]))
        cv.drawRect(skia.Rect.MakeWH(LAYER_W, H), fog)
    return surf.makeImageSnapshot(), rects


L = {}


def init_layers():
    L['far'] = make_layer(11, (300, 560), 1010, '#26292a', '#1f2122', .5, .10)
    L['mid'] = make_layer(22, (220, 470), 1060, '#202323', '#191b1b', .22, .14)
    L['mid_g'] = make_layer(22, (220, 470), 1060, '#202323', '#191b1b', .22, .14, gold=True)
    L['near'] = make_layer(33, (140, 330), 1120, '#191b1b', '#131414', .0, .18)
    L['near_g'] = make_layer(33, (140, 330), 1120, '#191b1b', '#131414', .0, .18, gold=True)


def draw_layer(cv, key, px):
    img, _ = L[key]
    cv.drawImage(img, -300 + px, 0)


def eden_geom(bx, base, h, r):
    return P.eden_geom(bx, base, h, r)


def cone(cv, x0, y0, w0, x1, y1, w1, c, a):
    P.draw_cone(cv, x0, y0, w0, x1, y1, w1, c, a)


def rooftop(cv, t, rim_a):
    """Vordergrund: Dachkante mit Lueftung, zwei Silhouetten von hinten."""
    par = P_([(-40, 900), (2000, 880), (2000, 1200), (-40, 1200)])
    cv.drawPath(par, fillp(cv, '#121313'))
    cv.drawLine(-40, 900, 2000, 880, inkp(cv, 3, '#2c2f2e', 1))
    for (x, h) in ((160, 70), (1660, 110)):
        v = P_([(x, 900 - h), (x + 70, 898 - h), (x + 70, 900), (x, 902)])
        draw(cv, v, '#161818', 1, shade=P_([(x + 46, 900 - h), (x + 80, 900 - h), (x + 80, 910), (x + 46, 910)]),
             shade_col='#0f1010')
        cv.drawLine(x + 8, 912 - h, x + 62, 910 - h, inkp(cv, 2, '#2c2f2e', 1))
    cv.drawLine(1760, 880, 1760, 700, inkp(cv, 6, '#121313', 1))
    cv.drawLine(1730, 730, 1790, 720, inkp(cv, 4, '#121313', 1))
    bust_back(cv, 760, 790, 175, 0, rim_a=rim_a)
    bust_back(cv, 1060, 812, 165, 1, rim_a=rim_a)


# ================================================================ S1  Stadt, EDEN steigt auf (0-9.0)
def s_city(cv, t):
    cv.drawImage(P.BG_NIGHT, 0, 0)
    pan = -70 * eio(t / 9.0)
    z = lerp(1.0, 1.06, eio(t / 9.0))
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    rise = eio(prog(t, 3.4, 6.6))
    face = eout(prog(t, 6.0, 6.7))
    bx, base, r = 1260 + pan * .35, 1040, 170
    h = lerp(0, 860, rise)
    P.G.zoom = z
    cv.drawRect(skia.Rect.MakeXYWH(-100, 600, W + 200, 500), glowp(cv, GOLD_HI, 160, .10 * face))
    draw_layer(cv, 'far', pan * .25)
    if h > 5:
        P.draw_eden_bot(cv, bx, base, h, r, t, face=face, glow=.4 + .6 * face)
    draw_layer(cv, 'mid', pan * .5)
    ca = eout(prog(t, 6.3, 7.4))
    if ca > 0:
        top, ry, vy0, vy1 = eden_geom(bx, base, h, r)
        cone(cv, bx, (vy0 + vy1) / 2 + ry, r * .5, 760, 1080, 820, GOLD_HI, ca)
    draw_layer(cv, 'near', pan * .8)
    if ca > 0:
        dust(cv, t, (300, 300, 1500, 1000), 50, 3, GOLD_HI, .45 * ca)
    cv.save()
    cv.translate(pan * 1.1, 0)
    rooftop(cv, t, .9 * face)
    cv.restore()
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(t, 0, 1.0)))))


# ================================================================ S2  EDEN Nahaufnahme (9.0-16.6)
def s_eden(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 560, lerp(1.1, 1.0, eio(t / 7.6)))
    bx, r, top = 960, 600, -100
    cv.drawRect(skia.Rect.MakeXYWH(-200, 300, W + 400, 900), glowp(cv, GOLD_HI, 200, .1))
    hatch = eout(prog(t, 4.0, 4.5))
    P.draw_eden_bot(cv, bx, top + 1500, 1500, r, t, face=1.0, logo=eout(prog(t, .4, 1.2)), glow=.8, hatches=hatch)
    # vier Arme fahren aus den Luken: Vorfuehr-Geste
    for k, (hx, hy, sx, dx, dy, ph) in enumerate(((-.78, .95, -1, 330, -120, 0.0), (.78, 1.1, 1, 330, -60, 1.3),
                                                  (-.70, 1.6, -1, 300, 40, 2.1), (.72, 1.75, 1, 290, 20, .7))):
        ex = eback(prog(t, 4.5 + k * .18, 5.3 + k * .18))
        if ex <= 0:
            continue
        hx0, hy0 = bx + r * hx, top + r * hy + r * .05
        cv.save()
        cv.translate(hx0, hy0)
        cv.scale(ex, ex)
        tx = sx * dx + 14 * math.sin(t * 1.7 + ph)
        ty = dy + 18 * math.sin(t * 2.3 + ph)
        el, end = P.ik2(0, 0, tx, ty, 200, 190, flip=sx)
        robot_arm(cv, [(0, 0), el, end], 46)
        ang = math.degrees(math.atan2(end[1] - el[1], end[0] - el[0]))
        robot_hand(cv, end[0], end[1], 115, ang - sx * 25, curl=.15 + .12 * math.sin(t * 2.6 + ph), open_=.6)
        cv.restore()
    dust(cv, t, (0, 0, W, H), 45, 5, GOLD_HI, .35)
    cv.restore()


# ================================================================ S3a  Vertrag (16.6-21.0)
def contract(cv, x, y, w, h, rot, sig, stamp):
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .35))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 14, -h / 2 + 18, w, h), sh)
    pg = skia.Path()
    pg.addRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h))
    draw(cv, pg, '#d3d0c2', 1, shade=P_([(w / 2 - 24, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (w / 2 - 24, h / 2)]),
         shade_col='#bdbaac')
    text(cv, 'CONTRACT', 0, -h / 2 + 84, TF_TYPE, 54, '#2a2520', anchor='c', spacing=6)
    cv.drawLine(-w / 2 + 60, -h / 2 + 108, w / 2 - 60, -h / 2 + 108, strokep(cv, 3, '#2a2520'))
    rnd = random.Random(4)
    for i in range(9):
        lw = (w - 140) * rnd.uniform(.55, .98)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 70, -h / 2 + 150 + i * 36, lw, 13), 6.5, 6.5)
        cv.drawRRect(rr, fillp(cv, '#a9a699', 1, False))
        cv.drawCircle(-w / 2 + 70 + lw + 20, -h / 2 + 156 + i * 36, 6, fillp(cv, '#a9a699', 1, False))
    ly = h / 2 - 110
    cv.drawLine(-w / 2 + 90, ly, w / 2 - 120, ly, strokep(cv, 3, '#2a2520'))
    text(cv, 'X', -w / 2 + 70, ly - 8, TF_HEAD, 34, '#2a2520')
    sp = skia.Path()
    x0 = -w / 2 + 120
    sp.moveTo(x0, ly - 20)
    sp.cubicTo(x0 + 30, ly - 90, x0 + 50, ly - 10, x0 + 70, ly - 40)
    sp.cubicTo(x0 + 90, ly - 70, x0 + 100, ly - 5, x0 + 130, ly - 30)
    sp.cubicTo(x0 + 160, ly - 60, x0 + 170, ly - 20, x0 + 200, ly - 35)
    sp.cubicTo(x0 + 240, ly - 55, x0 + 260, ly - 15, x0 + 330, ly - 30)
    if sig > 0:
        cv.drawPath(trim(sp, sig), strokep(cv, 4.5, '#1c2433'))
    pm = skia.PathMeasure(sp, False)
    pos, _ = pm.getPosTan(pm.getLength() * clamp(sig))
    ra = math.radians(rot)
    tip = (x + math.cos(ra) * pos.x() - math.sin(ra) * pos.y(), y + math.sin(ra) * pos.x() + math.cos(ra) * pos.y())
    if stamp > 0:
        cv.save()
        cv.translate(w / 2 - 170, -h / 2 + 240)
        cv.rotate(-12)
        sc = lerp(1.6, 1.0, eout(stamp))
        cv.scale(sc, sc)
        al = clamp(stamp * 3)
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-120, -38, 240, 76), 10, 10)
        cv.drawRRect(rr, strokep(cv, 6, GOLD_DK, al))
        text(cv, 'APPROVED', 0, 16, TF_HEAD, 44, GOLD_DK, al, anchor='c')
        cv.restore()
    cv.restore()
    return tip


def s_contract(cv, t):
    cv.drawPaint(fillp(cv, '#2a2622', 1, False))
    rnd = random.Random(8)
    for i in range(22):
        y = i * 52 + rnd.uniform(-10, 10)
        p = skia.Path()
        p.moveTo(-20, y)
        for x in range(0, W + 60, 60):
            p.lineTo(x, y + 8 * math.sin(x * .006 + i * 1.7))
        cv.drawPath(p, strokep(cv, 2.5, '#221e1b', .9))
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.06, eio(t / 4.4)))
    slide = ein(prog(t, 3.2, 4.2))
    px, py = 900 + 900 * slide, 520 - 80 * slide
    sig = prog(t, .6, 2.0)
    stamp = prog(t, 2.2, 2.5)
    tipx, tipy = contract(cv, px, py, 760, 860, -3 + 6 * slide, sig, stamp)
    # menschliche Hand links, flach auf dem Tisch; zieht sich zurueck, wenn der Vertrag weggleitet
    curl = eout(prog(t, 3.3, 4.2))
    hand_flat(cv, 330 - 60 * curl, 700 + 40 * curl, 250, -14 - 8 * curl, spread=lerp(1.0, .45, curl), sleeve=SUIT)
    # goldene Hand fuehrt den Fueller; Spitze sitzt exakt auf der Unterschrift
    enter = eout(prog(t, 0, .6))
    leave = ein(prog(t, 2.4, 3.2))
    lift = 40 * eout(prog(t, 2.0, 2.3)) + 900 * leave
    tx, ty = tipx + 700 * (1 - enter) + 600 * leave, tipy - 500 * (1 - enter) - lift
    pa = math.radians(-58)
    top_ = (tx + math.cos(pa) * 230, ty + math.sin(pa) * 230)
    wx, wy = tx + math.cos(pa) * 150 + 70, ty + math.sin(pa) * 150 - 10
    el, _ = P.ik2(W + 260, -260, wx + 60, wy - 60, 640, 640, flip=1)
    robot_arm(cv, [(W + 260, -260), el, (wx + 60, wy - 60)], 70)
    cv.drawLine(tx, ty, top_[0], top_[1], strokep(cv, 15, INK))
    cv.drawLine(tx, ty, top_[0], top_[1], strokep(cv, 10, '#2f2a24'))
    cv.drawLine(tx + math.cos(pa) * 150, ty + math.sin(pa) * 150, top_[0], top_[1], strokep(cv, 10, GOLD_DK))
    cv.drawLine(tx, ty, tx + math.cos(pa) * 26, ty + math.sin(pa) * 26, strokep(cv, 6, GOLD_HI))
    robot_hand(cv, wx + 60, wy - 60, 150, 128, curl=.8, open_=0)
    cv.restore()


# ================================================================ S3b  Fabrik und Kueche (21.0-25.0)
def s_split(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.04, eio(t / 4.0)))
    panels = [(36, 300, 908, 470, P.panel_cars, 0.0), (976, 300, 908, 470, P.panel_food, 1.9)]
    for (px, py, pw, ph, fn, t0) in panels:
        p = prog(t, t0, t0 + .4)
        if p <= 0:
            continue
        sc = eback(p)
        cv.save()
        cv.translate(px + pw / 2, py + ph / 2)
        cv.scale(sc, sc)
        cv.translate(-pw / 2, -ph / 2)
        cv.save()
        cv.clipRect(skia.Rect.MakeWH(pw, ph), doAntiAlias=True)
        P.G.zoom = 1.0
        fn(cv, pw, ph, t - t0 + 2)
        cv.restore()
        cv.drawRect(skia.Rect.MakeWH(pw, ph), strokep(cv, 10, BONE))
        cv.drawRect(skia.Rect.MakeXYWH(-6, -6, pw + 12, ph + 12), strokep(cv, 3, INK))
        cv.drawRect(skia.Rect.MakeXYWH(6, 6, pw - 12, ph - 12), strokep(cv, 3, INK))
        cv.restore()
    cv.restore()


# ================================================================ S3c  Nachtbuero (25.0-29.6)
DAY = 1.6


def s_never(cv, t):
    """Tage rasen vorbei, EDEN tippt durch."""
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.07, eio(t / 4.6)))
    wall = skia.Paint()
    wall.setShader(skia.GradientShader.MakeLinear([skia.Point(0, -100), skia.Point(0, 780)], [col('#242625'), col('#1a1b1b')]))
    cv.drawRect(skia.Rect.MakeLTRB(-300, -300, W + 300, 790), wall)
    for x in range(-300, W + 300, 150):
        cv.drawLine(x, -300, x, 780, strokep(cv, 2, '#1e201f', 1))
    ph = t / DAY + .62
    u = ph % 1
    bright = math.sin(math.pi * u / .5) if u < .5 else 0.0
    # Fenster mit Tag-Nacht-Wechsel
    wx, wy, ww, wh = 110, 90, 640, 560
    win = skia.Rect.MakeXYWH(wx, wy, ww, wh)
    cv.save()
    cv.clipRect(win, doAntiAlias=True)
    cv.drawRect(win, fillp(cv, mix('#111418', '#66716b', bright), 1, False))
    v = u / .5 if u < .5 else (u - .5) / .5
    bx, by = wx + ww * lerp(-.05, 1.05, v), wy + wh * .78 - math.sin(math.pi * v) * wh * .62
    if u < .5:
        cv.drawCircle(bx, by, 110, glowp(cv, '#f3dfa6', 40, .5))
        cv.drawCircle(bx, by, 40, fillp(cv, '#f3dfa6', 1, False))
    else:
        mp = skia.Path()
        mp.addCircle(bx, by, 34)
        cut = skia.Path()
        cut.addCircle(bx + 15, by - 9, 30)
        mp = skia.Op(mp, cut, skia.PathOp.kDifference_PathOp)
        cv.drawPath(mp, fillp(cv, BONE, 1, False))
    cv.save()
    sc = ww / W * 1.25
    cv.translate(wx - 40, wy + wh + 30)
    cv.scale(sc, sc)
    cv.translate(0, -1080)
    cv.drawImage(L['mid'][0], -300, 0)
    cv.restore()
    cv.drawRect(win, fillp(cv, '#000000', .25 * (1 - bright), False))
    for k in range(3):
        g = P_([(wx + 120 + k * 60, wy), (wx + 170 + k * 60, wy), (wx - 30 + k * 60, wy + wh), (wx - 80 + k * 60, wy + wh)])
        cv.drawPath(g, fillp(cv, '#ffffff', .035, False))
    cv.restore()
    cv.drawRect(win, strokep(cv, 26, '#2e302e'))
    cv.drawRect(skia.Rect.MakeXYWH(wx - 13, wy - 13, ww + 26, wh + 26), inkp(cv, OW, INK))
    cv.drawRect(skia.Rect.MakeXYWH(wx + 13, wy + 13, ww - 26, wh - 26), inkp(cv, OW * .8, INK))
    cv.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, strokep(cv, 14, '#2e302e'))
    sill = P_([(wx - 40, wy + wh + 10), (wx + ww + 40, wy + wh + 10), (wx + ww + 40, wy + wh + 40), (wx - 40, wy + wh + 40)])
    draw(cv, sill, '#333532', 1, shade=P_([(wx - 40, wy + wh + 28), (wx + ww + 40, wy + wh + 28), (wx + ww + 40, wy + wh + 40),
                                         (wx - 40, wy + wh + 40)]), shade_col='#272927')
    # Uhr: Stundenzeiger rast, Minutenzeiger nur noch Unschaerfe
    cx, cy, r = 1150, 270, 150
    cv.drawCircle(cx + 10, cy + 14, r + 8, fillp(cv, '#000000', .3, False))
    face = circle(cx, cy, r)
    draw(cv, face, BONE, 1, shade=skia.Op(circle(cx, cy, r), circle(cx - 22, cy - 22, r), skia.PathOp.kDifference_PathOp),
         shade_col=BONE_SH)
    cv.drawCircle(cx, cy, r, strokep(cv, 16, '#2e302e'))
    cv.drawCircle(cx, cy, r + 8, inkp(cv, OW, INK))
    for k in range(12):
        a_ = math.radians(k * 30)
        L0 = r * (.78 if k % 3 else .7)
        cv.drawLine(cx + math.cos(a_) * L0, cy + math.sin(a_) * L0, cx + math.cos(a_) * r * .88, cy + math.sin(a_) * r * .88,
                    strokep(cv, 6 if k % 3 == 0 else 3.5, INK))
    blur = skia.Paint(AntiAlias=True, Color=col(INK, .22))
    blur.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    cv.drawCircle(cx, cy, r * .74, blur)
    ha = math.radians(-90 + ph * 720)
    cv.drawLine(cx, cy, cx + math.cos(ha) * r * .5, cy + math.sin(ha) * r * .5, strokep(cv, 11, INK))
    cv.drawCircle(cx, cy, 10, fillp(cv, INK, 1, False))
    # Kalender mit fliegenden Blaettern
    day = int(ph)
    kx, ky, kw, kh = 1480, 120, 260, 300

    def page(n, a_=1.0):
        pg = P_([(0, 0), (kw, 0), (kw, kh), (0, kh)])
        draw(cv, pg, BONE, a_, shade=P_([(0, kh - 40), (kw, kh - 40), (kw, kh), (0, kh)]), shade_col=BONE_SH)
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, kw, 70), fillp(cv, '#7d3a30', a_, False))
        cv.drawRect(skia.Rect.MakeXYWH(0, 0, kw, kh), inkp(cv, OW, INK, a_))
        text(cv, str(n), kw / 2, kh - 70, TF_HEAD, 150, INK, a_, anchor='c')
    cv.drawRect(skia.Rect.MakeXYWH(kx + 12, ky + 16, kw, kh), fillp(cv, '#000000', .3, False))
    cv.save()
    cv.translate(kx, ky)
    page(12 + day)
    cv.restore()
    fl = (ph % 1)
    if fl < .35:
        q = fl / .35
        cv.save()
        cv.translate(kx + kw / 2 + 260 * q, ky + 40 - 420 * q + 380 * q * q)
        cv.rotate(70 * q)
        cv.translate(-kw / 2, -40)
        page(11 + day, 1 - q * q)
        cv.restore()
    # Schreibtisch
    desk = P_([(-300, 770), (W + 300, 770), (W + 300, 1400), (-300, 1400)])
    draw(cv, desk, '#3a332c', 1)
    cv.drawLine(-300, 784, W + 300, 784, strokep(cv, 6, '#4a4137'))
    cv.drawRect(skia.Rect.MakeXYWH(700, 640, 760, 360), glowp(cv, GOLD_HI, 90, .22))
    # Papierstapel waechst
    n = 6 + int(t * 7)
    rnd = random.Random(3)
    for k in range(n):
        ox = rnd.uniform(-8, 8)
        y0 = 930 - k * 7
        sh_ = P_([(300 + ox, y0 - 34), (560 + ox, y0 - 34), (590 + ox, y0), (270 + ox, y0)])
        draw(cv, sh_, BONE if k % 2 else BONE_SH, 1, px=OW * .6)
    # Monitor
    mx, my, mw, mh = 800, 430, 520, 320
    draw(cv, P_([(mx + mw / 2 - 30, my + mh), (mx + mw / 2 + 30, my + mh), (mx + mw / 2 + 50, 800), (mx + mw / 2 - 50, 800)]),
         '#2b2d2b', 1)
    draw(cv, P_([(mx + mw / 2 - 110, 795), (mx + mw / 2 + 110, 795), (mx + mw / 2 + 120, 812), (mx + mw / 2 - 120, 812)]),
         '#2b2d2b', 1)
    bez = skia.Path()
    bez.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(mx, my, mw, mh), 14, 14))
    draw(cv, bez, '#2b2d2b', 1, shade=P_([(mx + mw - 30, my), (mx + mw, my), (mx + mw, my + mh), (mx + mw - 30, my + mh)]),
         shade_col='#222423')
    scr = skia.Rect.MakeXYWH(mx + 22, my + 22, mw - 44, mh - 44)
    cv.drawRect(scr, fillp(cv, '#2a2416', 1, False))
    cv.save()
    cv.clipRect(scr)
    rnd = random.Random(7)
    off = (t * 140) % 26
    for k in range(40):
        lw = rnd.uniform(60, mw - 110)
        ind = rnd.choice([0, 0, 30, 60])
        yy = my + mh - 30 - k * 26 + off
        cv.drawRect(skia.Rect.MakeXYWH(mx + 44 + ind, yy, lw - ind, 9), fillp(cv, GOLD, .75, False))
    cv.restore()
    cv.drawRect(scr, glowp(cv, GOLD_HI, 30, .25))
    cv.drawRect(scr, inkp(cv, OW * .8, INK))
    # Tastatur
    kb = P_([(830, 850), (1300, 850), (1330, 905), (800, 905)])
    draw(cv, kb, '#2b2d2b', 1)
    rnd = random.Random(int(t * 16))
    lit = {rnd.randrange(36) for _ in range(4)}
    for i in range(12):
        for j in range(3):
            q = i + j * 12
            kx0 = 830 + 6 + i * 38 - j * 10
            cv.drawRect(skia.Rect.MakeXYWH(kx0 + 4, 856 + j * 16, 30, 11), fillp(cv, GOLD if q in lit else '#3c3e3b', 1, False))
    # zwei Roboterarme tippen
    for (bx_, by_, hx, hy, ph_) in ((W + 160, 560, 1000, 845, 0.0), (W + 160, 1150, 1180, 870, 1.1)):
        bob = 10 * abs(math.sin(t * 16 + ph_))
        el, end = P.ik2(bx_, by_, hx + 120, hy - 70 - bob, 520, 480, flip=1 if by_ < 900 else -1)
        robot_arm(cv, [(bx_, by_), el, end], 60)
        robot_hand(cv, end[0], end[1], 125, 155, curl=.5 + .2 * math.sin(t * 16 + ph_), open_=.1)
    dust(cv, t, (600, 300, 1500, 900), 30, 21, GOLD_HI, .35)
    cv.restore()
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150, [col('#000000', 0), col('#000000', .5)]))
    cv.drawPaint(vg)


# ================================================================ S4  Tuerme werden golden (29.6-35.6)
def s_towers(cv, t):
    cv.drawImage(P.BG_NIGHT, 0, 0)
    pan = -70 - 40 * eio(t / 6)
    cv.save()
    z = lerp(1.04, 1.0, eio(t / 6))
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    P.G.zoom = z
    bx, base, r = 1260 + pan * .35, 1040, 170
    cv.drawRect(skia.Rect.MakeXYWH(-100, 600, W + 200, 500), glowp(cv, GOLD_HI, 160, .1 + .1 * eout(prog(t, 0, 5))))
    draw_layer(cv, 'far', pan * .25)
    P.draw_eden_bot(cv, bx, base, 860, r, t, face=1.0, glow=1.0)
    for key, f in (('mid', .5), ('near', .8)):
        draw_layer(cv, key, pan * f)
        img, rects = L[key + '_g']
        ox = -300 + pan * f
        for (l, tp, rr, b) in rects:
            cxw = (l + rr) / 2 + ox
            d = abs(cxw - bx) / 1300
            g = eout(prog(t, .3 + d * 3.4, .9 + d * 3.4))
            if g <= 0:
                continue
            cv.save()
            cv.clipRect(skia.Rect.MakeLTRB(l + ox, tp, rr + ox, b))
            cv.drawImage(img, ox, 0, skia.SamplingOptions(), skia.Paint(Color=col('#ffffff', g)))
            cv.restore()
        if key == 'mid':
            top, ry, vy0, vy1 = eden_geom(bx, base, 860, r)
            cone(cv, bx, (vy0 + vy1) / 2 + ry, r * .5, 760, 1080, 820, GOLD_HI, 1)
    dust(cv, t + 9, (300, 300, 1500, 1000), 50, 3, GOLD_HI, .45)
    cv.save()
    cv.translate(pan * 1.1, 0)
    rooftop(cv, t, .9)
    cv.restore()
    cv.restore()


# ================================================================ S5  Zeitungen (35.6-41.8)
def s_papers(cv, t):
    cv.drawPaint(fillp(cv, '#9b9e93', 1, False))
    for gx in range(0, W, 28):
        for gy in range(0, H, 28):
            r = 3 * (.5 + .5 * math.sin(gx * .004 + gy * .006))
            if r > .6:
                cv.drawCircle(gx, gy, r, fillp(cv, '#8e9187', 1, False))
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.08, eio(t / 6.2)))
    P.G.zoom = 1.0
    for (kind, cx, cy, w, h, rot, t0, (dx, dy)) in P.PAPERS:
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
        P.draw_paper(cv, w, h, kind, t)
        cv.restore()
        if kind == 'shares':
            hp = eout(prog(t, t0, t0 + .7)) * (1 - ein(prog(t, t0 + 2.0, t0 + 2.8)))
            if hp > 0:
                hx = lerp(2400, x + 390, hp)
                hy = lerp(1500, y + 400, hp)
                hand_flat(cv, hx, hy, 230, -142, spread=.8, sleeve=SUIT)
                cv.drawCircle(hx - 16, hy + 8, 9, fillp(cv, GOLD, 1, False))
                cv.drawCircle(hx - 16, hy + 8, 9, inkp(cv, OW * .7, INK))
    cv.restore()


# ================================================================ S6  Menge (41.8-50.0)
ROWS = [(420, 70, 10, 0.55), (545, 86, 10, 0.35), (690, 104, 10, 0.18), (860, 126, 10, 0.0)]
_rnd6 = random.Random(9)
DIM6 = _rnd6.sample(range(40), 20)
STAGES6 = [(4, .4, '1 IN 10'), (10, 3.2, '1 IN 4'), (20, 5.6, '1 IN 2')]


def s_crowd(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.drawRect(skia.Rect.MakeXYWH(200, -200, W - 400, 900), glowp(cv, BONE_HI, 220, .07))
    cv.save()
    cam(cv, 960, 590, lerp(1.05, 1.0, eio(t / 8.2)))
    for ri, (y, s, n, haze) in enumerate(ROWS):
        span = W + 140
        for k in range(n):
            i = ri * n + k
            x = -70 + span * (k + .5) / n + (s * .35 if ri % 2 else 0)
            d = 0.0
            if i in DIM6:
                j = DIM6.index(i)
                prev = 0
                for (cnt, t0, _) in STAGES6:
                    if j < cnt:
                        jj = j - prev
                        d = eio(prog(t, t0 + jj * .09, t0 + .45 + jj * .09))
                        break
                    prev = cnt
            bust_front(cv, x, y, s, variant=i * 7 + 3, dim=d, t=t + i * .37)
        if haze > 0:
            hz = skia.Paint()
            hz.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y + s * 1.0), skia.Point(0, y + s * 2.2)],
                                                        [col(BG, haze * .6), col(BG, 0)]))
            cv.drawRect(skia.Rect.MakeLTRB(-300, -400, W + 300, y + s * 2.2), hz)
    cv.restore()
    label, t0 = None, 0
    for (cnt, ts, lab) in STAGES6:
        if t >= ts + .3:
            label, t0 = lab, ts + .3
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 260)], [col(BG, .95), col(BG, 0)]))
    cv.drawRect(skia.Rect.MakeWH(W, 260), vg)
    if label:
        sc = eback(prog(t, t0, t0 + .35))
        f = skia.Font(TF_HEAD, 110)
        a_, b_ = label.split(' IN ')
        s2 = ' IN ' + b_
        tw = f.measureText(a_ + s2)
        cv.save()
        cv.translate(W / 2, 135)
        cv.scale(sc, sc)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(a_, f), -tw / 2, 35, skia.Paint(AntiAlias=True, Color=col(GOLD)))
        cv.drawTextBlob(skia.TextBlob.MakeFromString(s2, f), -tw / 2 + f.measureText(a_), 35,
                        skia.Paint(AntiAlias=True, Color=col(BONE_HI)))
        cv.restore()


# ================================================================ S7  Autosalon mit Verkaeufer (50.0-57.6)
def s_showroom(cv, t):
    tt = t * (8.6 / 7.6)
    P.scene_showroom(cv, tt)
    # Verkaeufer im Vordergrund (Parallaxe 1.3), wartet auf Kunden an der Tuer
    camx = lerp(1000, 1600, eio(tt / 8.6))
    sx = 1212 - (camx - 960) * 1.3
    look = -4 * eio(prog(tt, 1.0, 1.8)) + 12 * eio(prog(tt, 5.4, 6.4))
    cv.save()
    cv.drawRect(skia.Rect.MakeXYWH(sx - 260, 420, 520, 700), glowp(cv, '#000000', 60, .35))
    person_profile(cv, sx, 650, 270, tt, facing=1, hair='B', look=look, mouth=-.6 * prog(tt, 5.4, 6.4),
                   palette={'skin': mix(SKIN, '#2a2b29', .25), 'skin_sh': mix(SKIN_SH, '#2a2b29', .3),
                            'hair': mix(HAIR, '#2a2b29', .3)})
    cv.restore()


# ================================================================ S8  Der letzte Job (57.6-64.0)
def s_lastjob(cv, t):
    cv.drawPaint(fillp(cv, '#1c1e1d', 1, False))
    cv.save()
    cam(cv, 960, 540, lerp(1.0, 1.06, eio(t / 6.4)))
    wx, wy, ww, wh = 420, 110, 1080, 460
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(wx, wy, ww, wh))
    cv.drawImage(P.BG_NIGHT, wx - 300, wy - 300)
    cv.save()
    cv.translate(wx, wy + wh)
    sc = ww / W
    cv.scale(sc, sc)
    cv.translate(0, -1080)
    draw_layer(cv, 'far', 0)
    P.G.zoom = sc
    P.draw_eden_bot(cv, 1260, 1040, 700, 170, t, face=1.0, glow=1.0)
    img, _ = L['mid_g']
    cv.drawImage(img, -300, 0)
    cv.restore()
    cv.restore()
    cv.drawRect(skia.Rect.MakeXYWH(wx, wy, ww, wh), strokep(cv, 22, '#2c2e2c'))
    cv.drawRect(skia.Rect.MakeXYWH(wx - 11, wy - 11, ww + 22, wh + 22), strokep(cv, 3, INK))
    cv.drawLine(wx + ww / 2, wy, wx + ww / 2, wy + wh, strokep(cv, 12, '#2c2e2c'))
    cv.drawRect(skia.Rect.MakeXYWH(wx - 60, wy, ww + 120, wh), glowp(cv, GOLD_HI, 80, .08))
    cv.drawRect(skia.Rect.MakeLTRB(-200, 880, 2200, 1300), fillp(cv, '#161716', 1, False))
    cv.drawLine(-200, 880, 2200, 880, inkp(cv, 3, INK))
    lamp = 1 - eout(prog(t, 3.5, 3.7))
    # Figur hinter dem langen Schreibtisch: legt den Ausweis ab, dreht sich um, geht
    reach = eio(prog(t, .2, 1.0)) * (1 - eio(prog(t, 1.25, 1.85)))
    walk = eio(prog(t, 2.0, 4.2))
    px = lerp(820, -520, walk)
    bob = 6 * abs(math.sin(t * 7)) if 0 < walk < 1 else 0
    facing = 1 if t < 1.95 else -1
    wrist = (lerp(.62, 1.05, reach), lerp(2.15, 1.74, reach))
    badge_on_hand = t < 1.25

    def arm(cv_):
        if facing < 0:
            return
        sh_ = (.55, 1.2)
        el, end = P.ik2(sh_[0], sh_[1], wrist[0], wrist[1], .55, .52, flip=1)
        for (p0, p1, r0, r1) in ((sh_, el, .13, .11), (el, end, .11, .09)):
            draw(cv_, capsule(p0[0], p0[1], p1[0], p1[1], r0, r1), SUIT, 1, px=OW * .9)
        ang = math.degrees(math.atan2(end[1] - el[1], end[0] - el[0]))
        hand_side(cv_, end[0], end[1], .42, ang * .4 + 6, curl=.35, sleeve=SUIT)
    if badge_on_hand:
        P.draw_badge(cv, px + (wrist[0] + .42 - .45) * 200, 430 + (wrist[1] + .06 - .5) * 200, 1.0, lerp(-30, 82, reach))
    if px > -460:
        person_profile(cv, px, 430 - bob, 200, t, facing=facing, hair='A', look=5 if t < 1.95 else 2, mouth=-1, arm=arm)
    # Lampe mit Lichtkegel
    if lamp > 0:
        P.draw_cone(cv, 1150, 560, 40, 1020, 700, 300, '#f1e2b8', .45 * lamp)
    desk = P_([(-300, 690), (1320, 690), (1320, 712), (-300, 712)])
    draw(cv, desk, '#4a4137', 1)
    front = P_([(-300, 712), (1320, 712), (1320, 900), (-300, 900)])
    draw(cv, front, '#2e2823', 1, shade=P_([(-300, 712), (1320, 712), (1320, 730), (-300, 730)]), shade_col='#231e1a')
    for dx_ in (240, 760):
        cv.drawRect(skia.Rect.MakeXYWH(dx_, 760, 300, 90), inkp(cv, OW * .8, '#1f1b17'))
        cv.drawLine(dx_ + 120, 790, dx_ + 180, 790, strokep(cv, 6, '#4a4137'))
    lb = skia.Path()
    lb.addOval(skia.Rect.MakeXYWH(1170, 676, 100, 22))
    draw(cv, lb, '#2b2d2b', 1)
    cv.drawLine(1220, 684, 1190, 560, inkp(cv, 8, INK))
    cv.drawLine(1220, 684, 1190, 560, strokep(cv, 5, '#3b3d3a'))
    shade_p = P_([(1150, 520), (1215, 545), (1180, 600), (1110, 575)])
    draw(cv, shade_p, mix('#3b3d3a', '#e8d9ae', .5 * lamp), 1)
    # Ausweis
    lift = ein(prog(t, 4.9, 5.9))
    bx_, by_ = 820 + (1.05 + .42 - .45) * 200, 686 - lift * 900
    if not badge_on_hand:
        P.draw_badge(cv, bx_, by_, 1.0, 82)
    arm_in = eio(prog(t, 4.0, 4.9))
    if arm_in > 0:
        ty = lerp(-300, by_ - 150, arm_in)
        el, end = P.ik2(1240, -200, bx_ + 20, ty, 440, 440, flip=1)
        robot_arm(cv, [(1240, -200), el, end], 62)
        robot_hand(cv, end[0], end[1], 140, math.degrees(math.atan2(end[1] - el[1], end[0] - el[0])),
                   curl=.75 if t > 4.85 else .2, open_=0 if t > 4.85 else .5)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', prog(t, 6.0, 6.4))))


# ================================================================ S9  Kugel und Schlange (64.0-84.0)
BX, BY, BR = 1080, 450, 290
SKY = '#1c1c1b'


def ball_interior(cv, t):
    cv.drawCircle(BX, BY, BR, fillp(cv, SKY, 1, False))
    cv.save()
    sc = 2 * BR / W * 1.08
    cv.translate(BX - BR * 1.08, BY + BR * .68)
    cv.scale(sc, sc)
    cv.translate(0, -1080)
    cv.drawImage(P.BG_NIGHT, 0, 0)
    draw_layer(cv, 'far', -40)
    P.G.zoom = sc
    P.draw_eden_bot(cv, 1180, 1040, 860, 170, t, face=1.0, glow=1.0)
    img, _ = L['mid_g']
    cv.drawImage(img, -340, 0)
    top, ry, vy0, vy1 = eden_geom(1180, 1040, 860, 170)
    cone(cv, 1180, (vy0 + vy1) / 2 + ry, 85, 760, 1080, 820, GOLD_HI, .8)
    img, _ = L['near_g']
    cv.drawImage(img, -360, 0)
    cv.drawRect(skia.Rect.MakeLTRB(-400, 1080, W + 400, 2400), fillp(cv, '#141513', 1, False))
    cv.restore()


def crystal_ball(cv, t):
    ball = circle(BX, BY, BR)
    cv.save()
    cv.clipPath(ball, doAntiAlias=True)
    ball_interior(cv, t)
    vg = skia.Paint(AntiAlias=True)
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(BX, BY), BR, [col('#000000', 0), col('#000000', 0),
                                                                         col('#0b0a07', .6)], [0, .7, 1]))
    cv.drawCircle(BX, BY, BR, vg)
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(BX - BR * .8, BY - BR * .8, BR * 1.6, BR * 1.6), 200, 52)
    cv.drawPath(hl, strokep(cv, BR * .06, '#fff6dc', .45))
    cv.drawCircle(BX - BR * .40, BY - BR * .62, BR * .045, fillp(cv, '#fff6dc', .7, False))
    hl2 = skia.Path()
    hl2.addArc(skia.Rect.MakeXYWH(BX - BR * .9, BY - BR * .9, BR * 1.8, BR * 1.8), 22, 38)
    cv.drawPath(hl2, strokep(cv, BR * .02, '#fff6dc', .3))
    cv.restore()
    cv.drawPath(ball, inkp(cv, OW * 1.3, INK))
    inner = skia.Path()
    inner.addArc(skia.Rect.MakeXYWH(BX - BR + 8, BY - BR + 8, 2 * BR - 16, 2 * BR - 16), 115, 125)
    cv.drawPath(inner, strokep(cv, 3, GOLD_HI, .35))


def coil_pts(t, head):
    """1,6 Windungen unter der Kugel, endet links und steigt als Hals zum Kopf."""
    pts = []
    n = 240
    for i in range(n):
        u = i / (n - 1)
        th = math.radians(lerp(-40, 540, u))
        yc = BY + BR * lerp(1.02, .84, u)
        rx = BR * lerp(1.10, .98, u)
        ry = rx * .30
        pts.append((BX + rx * math.cos(th), yc + ry * math.sin(th), math.sin(th)))
    sx, sy = pts[-1][:2]
    hx, hy, ha = head
    c1, c2 = (sx - 10, sy - 210), (hx - 200 * math.cos(math.radians(ha)), hy - 200 * math.sin(math.radians(ha)))
    neck = []
    for i in range(1, 60):
        u = i / 59
        x = (1 - u) ** 3 * sx + 3 * (1 - u) ** 2 * u * c1[0] + 3 * (1 - u) * u * u * c2[0] + u ** 3 * hx
        y = (1 - u) ** 3 * sy + 3 * (1 - u) ** 2 * u * c1[1] + 3 * (1 - u) * u * u * c2[1] + u ** 3 * hy
        neck.append((x, y + 5 * math.sin(t * 1.3 + i * .12) * u, 1.0))
    return pts, neck


def runs(pts, wd):
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


def s_reveal(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    u = eio(prog(t, .3, 5.0))
    z = math.exp(lerp(math.log(3.6), math.log(1.0), u))
    cx = lerp(BX, 960, u)
    cy = lerp(BY + 60, 560, u)
    tilt = eio(prog(t, 10.0, 11.0))
    cam(cv, cx, cy, z * lerp(1.0, 1.1, tilt))
    cv.drawCircle(BX, BY, BR * 1.45, glowp(cv, GOLD_HI, 120, .22))
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .55))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    cv.drawOval(skia.Rect.MakeXYWH(BX - BR * 1.35, BY + BR * 1.12, BR * 2.7, BR * .5), sh)
    ang = lerp(8, -12, tilt) + 3 * math.sin(t * .8)
    head = (BX - BR * 1.12, BY - BR * .62 + 6 * math.sin(t * 1.1), ang)
    coil, neck = coil_pts(t, head)
    nt = len(coil) + len(neck)
    wd_all = []
    for i in range(nt):
        q = i / (nt - 1)
        wd_all.append(lerp(10, 66, q / .18) if q < .18 else (66 if q < .75 else lerp(66, 54, (q - .75) / .25)))
    rs = runs(coil, wd_all[:len(coil)])
    for (front, p, w) in rs:
        if not front:
            snake_body(cv, p, w, belly=.55)
    crystal_ball(cv, t)
    fr = [r_ for r_ in rs if r_[0]]
    for k, (front, p, w) in enumerate(fr):
        if k == len(fr) - 1:
            snake_body(cv, p + neck, w + wd_all[len(coil):], belly=.4, bdir=(.6, .8))
        else:
            snake_body(cv, p, w, belly=.55)
    lid = .2 + .25 * eout(prog(t, 10.0, 10.6)) - .25 * eout(prog(t, 15.0, 15.4))
    tongue = max(prog(t, 6.0, 6.5), prog(t, 13.4, 13.9), prog(t, 17.4, 17.9))
    snake_head(cv, head[0], head[1], ang, 76, lid=lid, tongue=tongue, smirk=.5 + .5 * tilt,
               pupil=lerp(1, .7, eout(prog(t, 15.0, 15.4))))
    # Hals-Ansatz ueber die Hinterkante des Kopfes legen
    ar = math.radians(ang)
    ext = neck[-8:] + [(head[0] + math.cos(ar) * 76 * k, head[1] + math.sin(ar) * 76 * k, 1.0) for k in (.12, .24, .34)]
    snake_body(cv, ext, [54 + 6 * i / (len(ext) - 1) for i in range(len(ext))], belly=.4, bdir=(.6, .8))
    dust(cv, t, (BX - 500, BY - 400, BX + 500, BY + 400), 30, 9, GOLD_HI, .4)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(t, 0, .4)))))
    cv.drawPaint(skia.Paint(Color=col('#000000', prog(t, 19.3, 20.0))))


# ================================================================ S10  Titel mit Ring (84.0-90.0)
def ouroboros(cv, cx, cy, R, w, t, a=1.0):
    n = 120
    a_tail, a_head = -95, 238
    pts = []
    for i in range(n):
        ang = math.radians(lerp(a_tail, a_head, i / (n - 1)) + 20 * t)
        pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang), 1.0))
    wd = [w * (.25 + .75 * min(1, (i / (n - 1)) / .2)) for i in range(n)]
    snake_body(cv, pts, wd, a)
    snake_head(cv, pts[-1][0], pts[-1][1], snake_ang(pts) + 6, w * .82, lid=.3, a=a)


def s_title(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    z = lerp(1.0, 1.05, t / 6)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    size = 170
    f = skia.Font(TF_TITLE, size)
    lines = [['WILL ', 'AI', ' BUY'], ['O', 'UR CARS?']]
    k = 0
    for li, parts in enumerate(lines):
        full = ''.join(parts)
        x = (W - f.measureText(full)) / 2
        y = 470 + li * 210
        for part in parts:
            pw = f.measureText(part)
            rp = eout(prog(t, .3 + k * .25, .9 + k * .25))
            if li == 1 and part == 'O':
                if rp > 0:
                    ouroboros(cv, x + pw / 2, y - size * .36, size * .34, 30, t * .3, a=rp)
            elif rp > 0:
                blob = skia.TextBlob.MakeFromString(part, f)
                cv.save()
                cv.translate(0, 30 * (1 - rp))
                cv.drawTextBlob(blob, x + 5, y + 6, skia.Paint(AntiAlias=True, Color=col('#000000', .6 * rp)))
                if part == 'AI':
                    ga = eout(prog(t, 2.2, 2.8))
                    g = skia.Paint(AntiAlias=True, Color=col(GOLD_HI, .55 * ga))
                    g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
                    cv.drawTextBlob(blob, x, y, g)
                    cv.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=col(mix(BONE_HI, GOLD, ga), rp)))
                else:
                    cv.drawTextBlob(blob, x, y, skia.Paint(AntiAlias=True, Color=col(BONE_HI, rp)))
                cv.restore()
            x += pw
            k += 1
    dust(cv, t, (300, 200, 1620, 900), 30, 12, GOLD_HI, .3)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(t, 0, .4)))))
    cv.drawPaint(skia.Paint(Color=col('#000000', prog(t, 5.2, 6.0))))


# ================================================================ Zeitplan
SCENES = [
    (0.0, 9.0, s_city),
    (9.0, 16.6, s_eden),
    (16.6, 21.0, s_contract),
    (21.0, 25.0, s_split),
    (25.0, 29.6, s_never),
    (29.6, 35.6, s_towers),
    (35.6, 41.8, s_papers),
    (41.8, 50.0, s_crowd),
    (50.0, 57.6, s_showroom),
    (57.6, 64.0, s_lastjob),
    (64.0, 84.0, s_reveal),
    (84.0, 90.0, s_title),
]
TOTAL = 90.0

SUBS = [
    (0.8, 3.8, 'Picture a city, a few years from now.'),
    (4.4, 8.6, 'One morning, something new rises behind its skyline.'),
    (9.4, 11.4, 'Its makers call it EDEN.'),
    (11.6, 16.2, 'It can do almost any job a human can do. Only cheaper.'),
    (17.0, 19.6, 'It writes the contracts.'),
    (21.2, 22.9, 'It builds the cars.'),
    (23.0, 24.8, 'It cooks the food.'),
    (25.3, 29.3, 'It never sleeps, and it never asks for a raise.'),
    (30.0, 32.6, 'Every company that buys it saves a fortune.'),
    (32.8, 35.3, 'So every company buys it.'),
    (36.0, 38.4, 'Its owners have never been richer.'),
    (38.6, 41.5, 'The stock market breaks record after record.'),
    (42.2, 45.0, 'First, one in ten people loses their job.'),
    (45.2, 47.1, 'Then one in four.'),
    (47.6, 49.7, 'Then one in two.'),
    (50.4, 55.8, 'The factories run day and night. More cars than ever before.'),
    (58.0, 61.2, 'Until one day, the last human job is gone.'),
    (61.4, 63.6, 'The machines have won.'),
    (64.8, 66.6, "That's the story."),
    (66.8, 69.2, "You've heard it a hundred times."),
    (69.4, 73.4, 'In headlines, in books, from the people building these machines.'),
    (74.0, 76.0, "And it's a story about me."),
    (76.2, 78.6, "I'm what you call the economy."),
    (79.0, 83.6, "Every few decades, someone tells me I'm about to die."),
]
P.SUBS = SUBS


def render_frame(surface, frame):
    t = frame / FPS
    G.frame = frame
    P.G.frame = frame
    P.G.zoom = 1.0
    cv = surface.getCanvas()
    cv.clear(col(BG))
    for (a, b, fn) in SCENES:
        if a <= t < b:
            cv.save()
            fn(cv, t - a)
            cv.restore()
            break
    P.G.zoom = 1.0
    if 1.0 <= t < 64.0:
        P.fiction_label(cv, eout(prog(t, 1.0, 1.6)) * (1 - prog(t, 63.4, 64.0)))
    P.draw_subs(cv, t)
    return surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def main():
    P.init_assets()
    init_layers()
    surface = skia.Surface(W, H)
    post = P.Post()
    mode = sys.argv[1]
    if mode == 'still':
        from PIL import Image
        for i in range(2, len(sys.argv) - 1, 2):
            sec, out = float(sys.argv[i]), sys.argv[i + 1]
            f = int(round(sec * FPS))
            Image.fromarray(post.apply(render_frame(surface, f), f)).save(out)
            print('saved', out, flush=True)
    elif mode == 'render':
        f0, f1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                 '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium',
                                 '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(f0, f1):
            proc.stdin.write(post.apply(render_frame(surface, f), f).tobytes())
            if f % 48 == 0:
                print('frame', f, flush=True)
        proc.stdin.close()
        proc.wait()


if __name__ == '__main__':
    main()
