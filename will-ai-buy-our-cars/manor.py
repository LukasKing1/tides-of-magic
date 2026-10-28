#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Das viktorianische Herrenhaus der Schlange (Erzaehlebene des Kanals).

python3 manor.py <name[,name...]> <outdir>     name: salon
"""
import math, random, sys
import numpy as np
import skia
from PIL import Image
import rich as R
import mascot3 as M
import frames9 as F
import frames10 as T
import frames11 as K
import style5 as ST
from rich_base import *

TF_CAPS, TF_HEAD, TF_TITLE, TF_TYPE, TF_D, TF_QUOTE = P.TF_CAPS, P.TF_HEAD, P.TF_TITLE, P.TF_TYPE, M.TF_DISPLAY, P.TF_QUOTE

# ---------------------------------------------------------------- Palette des Hauses
WALL, WALL_DK, DAMASK = '#24271f', '#181a15', '#30352a'
WOOD, WOOD_DK, WOOD_HI = '#3d2a1f', '#281b14', '#5a4130'
MARBLE, MARBLE_SH, MARBLE_HI = '#cfc8b4', '#a9a18c', '#e6e0cf'
LEATHER, LEATHER_DK, LEATHER_HI = '#6b2a24', '#481a17', '#8f4236'
RUG, RUG_DK = '#4f2220', '#35161a'
NIGHT = '#232b33'
LW = M.LW


def ink(cv, px=LW, a=1.0):
    return M.ink(cv, px, a)


def flat(cv, path, fill, shade=None, rim=None, d=6.0, rd=None, a=1.0, line=LW, ghost=False):
    """Flaeche im Kanalstil: Fuellung, Schattenband unten rechts, Lichtkante oben links, Tuschekontur."""
    if ghost:
        M.ghost(cv, path, a)
    cv.drawPath(path, fillp(cv, fill, a))
    if shade or rim:
        cv.save()
        cv.clipPath(path, doAntiAlias=True)
        if shade:
            cv.drawPath(M.minus(path, M.shifted(path, -d, -d)), fillp(cv, shade, a, False))
        if rim:
            r_ = rd if rd is not None else d * .55
            cv.drawPath(M.minus(path, M.shifted(path, r_, r_)), fillp(cv, rim, a, False))
        cv.restore()
    if line:
        cv.drawPath(path, ink(cv, line, a))


def rect(x, y, w, h, r=0.0):
    p = skia.Path()
    if r:
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    else:
        p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    return p


def oval(x, y, w, h):
    p = skia.Path()
    p.addOval(skia.Rect.MakeXYWH(x, y, w, h))
    return p


# ---------------------------------------------------------------- Detailschicht wie bei RA
def halftone(cv, x0, y0, x1, y1, c, step=14, rmax=4.0, fade='down', a=.35):
    for gx in np.arange(x0, x1, step):
        for gy in np.arange(y0, y1, step):
            ox = step / 2 if int((gy - y0) / step) % 2 else 0
            u = {'down': (gy - y0) / (y1 - y0), 'up': 1 - (gy - y0) / (y1 - y0),
                 'right': (gx - x0) / (x1 - x0), 'left': 1 - (gx - x0) / (x1 - x0)}[fade]
            r = rmax * clamp(u)
            if r > .5:
                cv.drawCircle(gx + ox, gy, r, fillp(cv, c, a, False))


def sparkle(cv, x, y, r, c=GOLD_HI, a=.9):
    p = skia.Path()
    p.moveTo(x, y - r)
    p.quadTo(x, y, x + r, y)
    p.quadTo(x, y, x, y + r)
    p.quadTo(x, y, x - r, y)
    p.quadTo(x, y, x, y - r)
    p.close()
    cv.drawCircle(x, y, r * 1.2, glowp(cv, c, r * .6, .35 * a))
    cv.drawPath(p, fillp(cv, c, a, False))


def dotted_line(cv, x0, y0, x1, y1, c, gap=16, r=2.0, a=.4):
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L / gap)
    for k in range(n + 1):
        u = k / max(1, n)
        cv.drawCircle(lerp(x0, x1, u), lerp(y0, y1, u), r, fillp(cv, c, a, False))


# ---------------------------------------------------------------- Raum
DAMASK_PATH = None


def damask_motif():
    p = skia.Path()
    p.moveTo(0, -52)
    p.cubicTo(10, -40, 10, -30, 0, -22)
    p.cubicTo(-10, -30, -10, -40, 0, -52)
    p.moveTo(0, -22)
    p.lineTo(0, 40)
    for sx in (-1, 1):
        p.moveTo(0, -8)
        p.cubicTo(sx * 22, -22, sx * 40, -4, sx * 26, 12)
        p.cubicTo(sx * 18, 20, sx * 8, 14, sx * 12, 6)
        p.moveTo(0, 22)
        p.cubicTo(sx * 16, 18, sx * 26, 30, sx * 18, 42)
        p.moveTo(sx * 26, 12)
        p.cubicTo(sx * 34, 26, sx * 44, 28, sx * 50, 20)
    p.addCircle(0, 46, 4)
    return p


def wallpaper(cv, x0, y0, x1, y1):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fillp(cv, WALL, 1, False))
    mot = damask_motif()
    for row, gy in enumerate(np.arange(y0 - 40, y1 + 60, 120)):
        for gx in np.arange(x0 - 40, x1 + 80, 110):
            cv.save()
            cv.translate(gx + (55 if row % 2 else 0), gy)
            cv.drawPath(mot, strokep(cv, 3, DAMASK, .9))
            cv.restore()
    for x in np.arange(x0, x1, 110):
        cv.drawLine(x + 55, y0, x + 55, y1, strokep(cv, 1.2, WALL_DK, .35))


def wainscot(cv, x0, x1, y_rail, y_floor):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y_rail, x1, y_floor), fillp(cv, WOOD, 1, False))
    rail = rect(x0 - 10, y_rail - 16, x1 - x0 + 20, 26)
    flat(cv, rail, WOOD_HI, WOOD_DK, '#7a5b45', 6, 3)
    w = 190
    for x in np.arange(x0 + 20, x1 - 40, w):
        pnl = rect(x + 14, y_rail + 32, w - 28, y_floor - y_rail - 70, 4)
        cv.drawPath(pnl, fillp(cv, mix(WOOD, WOOD_DK, .35), 1, False))
        cv.drawPath(M.minus(pnl, M.shifted(pnl, 5, 5)), fillp(cv, WOOD_DK, 1, False))
        cv.drawPath(M.minus(pnl, M.shifted(pnl, -4, -4)), fillp(cv, WOOD_HI, .7, False))
        cv.drawPath(pnl, ink(cv, 1.8, .8))
    base = rect(x0 - 10, y_floor - 26, x1 - x0 + 20, 26)
    flat(cv, base, WOOD_DK, None, WOOD_HI, 4, 3)


def floor(cv, y_floor, vx=960, vy=520):
    cv.drawRect(skia.Rect.MakeLTRB(-50, y_floor, W + 50, H + 50), fillp(cv, '#2a1d16', 1, False))
    for k in range(-14, 16):
        x = vx + k * 150
        cv.drawLine(vx + (x - vx) * (y_floor - vy) / (H - vy) * .55, y_floor, x * 1.0, H + 40, strokep(cv, 2, '#1e1510', 1))
    for k, y in enumerate((y_floor + 34, y_floor + 82, y_floor + 148)):
        cv.drawLine(-50, y, W + 50, y, strokep(cv, 1.5, '#1e1510', .8))


def rug(cv, cx, y0, w_top, w_bot, y1):
    p = poly([(cx - w_top / 2, y0), (cx + w_top / 2, y0), (cx + w_bot / 2, y1), (cx - w_bot / 2, y1)])
    cv.drawPath(p, fillp(cv, RUG, 1))
    inner = poly([(cx - w_top / 2 + 26, y0 + 12), (cx + w_top / 2 - 26, y0 + 12), (cx + w_bot / 2 - 44, y1 - 20),
                  (cx - w_bot / 2 + 44, y1 - 20)])
    cv.drawPath(inner, strokep(cv, 6, GOLD_SH, .75))
    inner2 = poly([(cx - w_top / 2 + 46, y0 + 22), (cx + w_top / 2 - 46, y0 + 22), (cx + w_bot / 2 - 78, y1 - 36),
                   (cx - w_bot / 2 + 78, y1 - 36)])
    cv.drawPath(inner2, strokep(cv, 2.5, '#d6c49a', .5))
    cv.save()
    cv.clipPath(inner2, doAntiAlias=True)
    for k in range(-6, 7):
        u = k / 6
        x0 = cx + u * w_top * .42
        x1 = cx + u * w_bot * .42
        cv.drawLine(x0, y0, x1, y1, strokep(cv, 2, RUG_DK, .6))
    mid_y = (y0 + y1) / 2
    med = poly([(cx, mid_y - 60), (cx + 150, mid_y), (cx, mid_y + 60), (cx - 150, mid_y)])
    cv.drawPath(med, fillp(cv, RUG_DK, .9, False))
    cv.drawPath(med, strokep(cv, 3, GOLD_SH, .7))
    cv.restore()
    cv.drawPath(p, ink(cv))
    for k in range(int(w_bot / 14)):
        x = cx - w_bot / 2 + 7 + k * 14
        cv.drawLine(x, y1, x, y1 + 12, strokep(cv, 2, '#d6c49a', .7))


def bookshelf(cv, x, y, w, h, seed=3):
    rnd = random.Random(seed)
    case = rect(x, y, w, h)
    flat(cv, case, WOOD, WOOD_DK, WOOD_HI, 10, 6, ghost=True)
    crown = rect(x - 16, y - 26, w + 32, 30)
    flat(cv, crown, WOOD_HI, WOOD_DK, '#7a5b45', 6, 3)
    inner_x0, inner_x1 = x + 18, x + w - 18
    shelves = 6
    sh_h = (h - 40) / shelves
    spines = ['#6b2a24', '#2f4a3a', '#4a3a2a', '#c9b98e', '#3a3f48', '#7a5b3a', '#5a4a6a', '#2b2b2b', '#8a6a33']
    for s in range(shelves):
        y0 = y + 18 + s * sh_h
        y1 = y0 + sh_h - 12
        cv.drawRect(skia.Rect.MakeLTRB(inner_x0, y0, inner_x1, y1), fillp(cv, '#160f0b', 1, False))
        bx = inner_x0 + 3
        while bx < inner_x1 - 14:
            bw = rnd.uniform(12, 26)
            if bx + bw > inner_x1 - 3:
                break
            bh = rnd.uniform(.62, .95) * (y1 - y0)
            lean = 0
            if rnd.random() < .06 and bx + bw + 30 < inner_x1:
                lean = 1
            c = rnd.choice(spines)
            b = rect(bx, y1 - bh, bw, bh, 2)
            if lean:
                cv.save()
                cv.translate(bx, y1)
                cv.rotate(14)
                cv.translate(-bx, -y1)
            flat(cv, b, c, mix(c, '#000000', .35), mix(c, '#ffffff', .18), 3.5, 2, line=1.6)
            for band in (.16, .82):
                cv.drawLine(bx + 2, y1 - bh * band, bx + bw - 2, y1 - bh * band, strokep(cv, 2, GOLD_SH, .85))
            if lean:
                cv.restore()
                bx += bw + 8
            bx += bw + rnd.uniform(0.5, 2.5)
        board = rect(x + 10, y1, w - 20, 12)
        flat(cv, board, WOOD_HI, WOOD_DK, None, 4)
    halftone(cv, x + 18, y + 18, x + w - 18, y + h, '#000000', 12, 3.2, 'down', .35)


def window(cv, x, y, w, h, t=0.0):
    outer = skia.Path()
    outer.moveTo(x, y + w / 2)
    outer.arcTo(skia.Rect.MakeXYWH(x, y, w, w), 180, 180, False)
    outer.lineTo(x + w, y + h)
    outer.lineTo(x, y + h)
    outer.close()
    cv.save()
    cv.clipPath(outer, doAntiAlias=True)
    sky = skia.Paint()
    sky.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y), skia.Point(0, y + h)], [col('#2e3a46'), col('#4a5560')]))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), sky)
    cv.drawCircle(x + w * .7, y + w * .35, 34, glowp(cv, '#e9e4d2', 30, .5))
    cv.drawCircle(x + w * .7, y + w * .35, 22, fillp(cv, '#ece7d6', 1, False))
    rnd = random.Random(5)
    for k in range(7):
        cx = x + k * w / 6 + rnd.uniform(-10, 10)
        ch = rnd.uniform(.25, .45) * h
        ch_w = rnd.uniform(14, 24)
        cv.drawRect(skia.Rect.MakeXYWH(cx, y + h - ch, ch_w, ch), fillp(cv, '#1d242b', 1, False))
        for j in range(4):
            cv.drawCircle(cx + ch_w / 2 + j * 10 + 6 * math.sin(t + j), y + h - ch - 14 - j * 22, 10 + j * 5,
                          fillp(cv, '#6a727a', .45 - j * .08, False))
    for k in range(9):
        bx = x + k * w / 8
        bh = rnd.uniform(.08, .2) * h
        cv.drawRect(skia.Rect.MakeXYWH(bx, y + h - bh, w / 8 + 2, bh), fillp(cv, '#1a2026', 1, False))
        if rnd.random() < .6:
            cv.drawRect(skia.Rect.MakeXYWH(bx + 8, y + h - bh + 10, 6, 8), fillp(cv, GOLD, .8, False))
    fog = skia.Paint()
    fog.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y + h * .55), skia.Point(0, y + h)], [col('#9aa3a8', 0), col('#9aa3a8', .35)]))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fog)
    cv.restore()
    for k in range(1, 3):
        cv.drawLine(x + w * k / 3, y + 10, x + w * k / 3, y + h, strokep(cv, 7, WOOD_DK))
    for k in range(1, 4):
        yy = y + w / 2 + (h - w / 2) * k / 4
        cv.drawLine(x, yy, x + w, yy, strokep(cv, 7, WOOD_DK))
    cv.drawPath(outer, strokep(cv, 18, WOOD))
    cv.drawPath(outer, ink(cv, 2.6))
    sill = rect(x - 24, y + h, w + 48, 22)
    flat(cv, sill, WOOD_HI, WOOD_DK, None, 4)


def drape(cv, x, y, w, h, side=1):
    """Gerafter Samtvorhang neben dem Fenster."""
    p = skia.Path()
    p.moveTo(x, y)
    p.lineTo(x + w, y)
    p.cubicTo(x + w * .9, y + h * .35, x + w * .25, y + h * .45, x + w * .45, y + h * .55)
    p.cubicTo(x + w * .7, y + h * .7, x + w * .9, y + h * .9, x + w * 1.05, y + h)
    p.lineTo(x - w * .05, y + h)
    p.cubicTo(x, y + h * .7, x + w * .05, y + h * .4, x, y)
    p.close()
    if side < 0:
        m = skia.Matrix()
        m.setScale(-1, 1, x + w / 2, 0)
        p.transform(m)
    sh = skia.Paint(AntiAlias=True)
    sh.setShader(skia.GradientShader.MakeLinear([skia.Point(x, 0), skia.Point(x + 34, 0)],
                                                [col('#22301f'), col('#33472e'), col('#4c6644'), col('#33472e'), col('#22301f')],
                                                None, skia.TileMode.kRepeat))
    M.ghost(cv, p)
    cv.drawPath(p, sh)
    cv.drawPath(p, ink(cv))
    tie_y = y + h * .55
    tx = x + w * .45 if side > 0 else x + w * .55
    cv.drawOval(skia.Rect.MakeXYWH(tx - 26, tie_y - 9, 52, 18), fillp(cv, GOLD, 1))
    cv.drawOval(skia.Rect.MakeXYWH(tx - 26, tie_y - 9, 52, 18), ink(cv, 2))
    cv.drawLine(tx + 20 * side, tie_y + 4, tx + 30 * side, tie_y + 46, strokep(cv, 3, GOLD_SH))
    cv.drawCircle(tx + 30 * side, tie_y + 52, 7, fillp(cv, GOLD, 1))


def moonbeams(cv, x0, x1, y0, fx0, fx1, fy, a=.06):
    beam = poly([(x0, y0), (x1, y0), (fx1, fy), (fx0, fy)])
    p = skia.Paint(AntiAlias=True, Color=col('#dfe6ea', a))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    cv.drawPath(beam, p)
    for k in range(1, 3):
        u = k / 3
        cv.drawLine(lerp(x0, x1, u), y0, lerp(fx0, fx1, u), fy, strokep(cv, 10, '#0c0a08', .12))


def fireplace(cv, x, y_floor, w, h, t=0.0):
    """Marmorkamin. x = Mitte."""
    top = y_floor - h
    shelf = rect(x - w / 2 - 30, top - 34, w + 60, 34, 4)
    body = rect(x - w / 2, top, w, h)
    opening = skia.Path()
    ow, oh = w * .56, h * .66
    opening.moveTo(x - ow / 2, y_floor)
    opening.lineTo(x - ow / 2, y_floor - oh + ow / 2)
    opening.arcTo(skia.Rect.MakeXYWH(x - ow / 2, y_floor - oh, ow, ow), 180, 180, False)
    opening.lineTo(x + ow / 2, y_floor)
    opening.close()
    cv.drawRect(skia.Rect.MakeXYWH(x - w, y_floor - 30, 2 * w, 80), glowp(cv, '#f0a24a', 50, .25))
    flat(cv, body, MARBLE, MARBLE_SH, MARBLE_HI, 10, 6, ghost=True)
    for sx in (-1, 1):
        pil = rect(x + sx * (w / 2 - 34) - 18, top + 30, 36, h - 40, 3)
        flat(cv, pil, MARBLE_HI, MARBLE_SH, None, 5)
        cap = rect(x + sx * (w / 2 - 34) - 26, top + 20, 52, 18, 3)
        flat(cv, cap, MARBLE, MARBLE_SH, MARBLE_HI, 4, 2)
    rnd = random.Random(8)
    for _ in range(6):
        vx = x + rnd.uniform(-w / 2 + 50, w / 2 - 50)
        vy = top + rnd.uniform(10, 50)
        cv.drawPath(P_([(vx, vy), (vx + 20, vy + 8, vx + 30, vy + 2, vx + 50, vy + 14)], close=False), strokep(cv, 1.6, MARBLE_SH, .7))
    cv.drawPath(opening, fillp(cv, '#0d0a08', 1, False))
    cv.save()
    cv.clipPath(opening, doAntiAlias=True)
    cv.drawCircle(x, y_floor - 30, ow * .55, glowp(cv, '#f0a24a', 40, .55))
    for k, (dx, hh, c) in enumerate(((-34, 100, '#d4682e'), (24, 120, '#d4682e'), (-8, 150, '#e8913a'), (-28, 80, GOLD), (20, 90, GOLD),
                                     (-4, 100, GOLD_HI))):
        fl = skia.Path()
        bx = x + dx
        sway = 6 * math.sin(t * 3 + k)
        fl.moveTo(bx - 26, y_floor - 26)
        fl.cubicTo(bx - 28, y_floor - hh * .5, bx + sway - 6, y_floor - hh * .8, bx + sway, y_floor - hh)
        fl.cubicTo(bx + sway + 8, y_floor - hh * .7, bx + 28, y_floor - hh * .45, bx + 26, y_floor - 26)
        fl.close()
        cv.drawPath(fl, fillp(cv, c, .95))
    for k in range(4):
        lg = rect(x - 60 + k * 10, y_floor - 34 - k * 6, 120 - k * 20, 18, 9)
        flat(cv, lg, '#3a2618', '#24170f', '#5a3d28', 3, line=1.8)
    cv.restore()
    cv.drawPath(opening, ink(cv, 2.6))
    for k in range(6):
        gx = x - ow / 2 + 20 + k * (ow - 40) / 5
        cv.drawLine(gx, y_floor - 46, gx, y_floor, strokep(cv, 5, '#151110'))
    cv.drawLine(x - ow / 2 + 10, y_floor - 46, x + ow / 2 - 10, y_floor - 46, strokep(cv, 5, '#151110'))
    flat(cv, shelf, MARBLE_HI, MARBLE_SH, '#f1ecdf', 6, 3, ghost=True)
    hearth = rect(x - w / 2 - 40, y_floor, w + 80, 26, 3)
    flat(cv, hearth, MARBLE_SH, '#8c8572', MARBLE, 5, 3)
    return top - 34


def mantel_clock(cv, x, y_base, s=1.0):
    body = skia.Path()
    body.moveTo(x - 46 * s, y_base)
    body.lineTo(x - 46 * s, y_base - 60 * s)
    body.cubicTo(x - 46 * s, y_base - 110 * s, x + 46 * s, y_base - 110 * s, x + 46 * s, y_base - 60 * s)
    body.lineTo(x + 46 * s, y_base)
    body.close()
    flat(cv, body, WOOD_HI, WOOD_DK, '#7a5b45', 5, 3, ghost=True)
    face = circle(x, y_base - 62 * s, 30 * s)
    flat(cv, face, '#efe6d2', '#d1c6ad', None, 3)
    cv.drawCircle(x, y_base - 62 * s, 30 * s, strokep(cv, 4, GOLD))
    for k in range(12):
        a = math.radians(k * 30)
        cv.drawLine(x + math.cos(a) * 22 * s, y_base - 62 * s + math.sin(a) * 22 * s, x + math.cos(a) * 27 * s,
                    y_base - 62 * s + math.sin(a) * 27 * s, strokep(cv, 2, INK))
    cv.drawLine(x, y_base - 62 * s, x + 12 * s, y_base - 74 * s, strokep(cv, 3, INK))
    cv.drawLine(x, y_base - 62 * s, x, y_base - 84 * s, strokep(cv, 2.2, INK))
    cv.drawPath(face, ink(cv, 2))


def candlestick(cv, x, y_base, s=1.0):
    stem = poly([(x - 6 * s, y_base - 10 * s), (x + 6 * s, y_base - 10 * s), (x + 4 * s, y_base - 70 * s), (x - 4 * s, y_base - 70 * s)])
    foot = oval(x - 24 * s, y_base - 12 * s, 48 * s, 14 * s)
    cup = oval(x - 14 * s, y_base - 76 * s, 28 * s, 10 * s)
    for p_ in (foot, stem, cup):
        flat(cv, p_, GOLD, GOLD_SH, GOLD_HI, 3, 2, line=2)
    cd = rect(x - 7 * s, y_base - 118 * s, 14 * s, 44 * s, 2)
    flat(cv, cd, '#efe6d2', '#d1c6ad', None, 3, line=2)
    cv.drawCircle(x, y_base - 134 * s, 40 * s, glowp(cv, '#f6d79a', 22, .45))
    fl = skia.Path()
    fl.moveTo(x, y_base - 146 * s)
    fl.cubicTo(x + 9 * s, y_base - 132 * s, x + 6 * s, y_base - 120 * s, x, y_base - 120 * s)
    fl.cubicTo(x - 6 * s, y_base - 120 * s, x - 9 * s, y_base - 132 * s, x, y_base - 146 * s)
    cv.drawPath(fl, fillp(cv, GOLD_HI, 1, False))


def gas_lamp(cv, x, y, s=1.0):
    cv.drawCircle(x, y - 20 * s, 150 * s, glowp(cv, '#f6d79a', 70, .22))
    plate = rect(x - 12 * s, y + 18 * s, 24 * s, 46 * s, 6 * s)
    flat(cv, plate, GOLD, GOLD_SH, GOLD_HI, 3, 2, line=2)
    arm = P_([(x, y + 40 * s), (x + 26 * s, y + 36 * s, x + 26 * s, y + 8 * s, x, y + 2 * s)], close=False)
    cv.drawPath(arm, strokep(cv, 7 * s, INK))
    cv.drawPath(arm, strokep(cv, 4 * s, GOLD_SH))
    glass = skia.Path()
    glass.moveTo(x - 22 * s, y - 52 * s)
    glass.lineTo(x + 22 * s, y - 52 * s)
    glass.lineTo(x + 14 * s, y)
    glass.lineTo(x - 14 * s, y)
    glass.close()
    cv.drawPath(glass, fillp(cv, '#f8e7bd', .95))
    cv.drawPath(M.minus(glass, M.shifted(glass, 6, 0)), fillp(cv, '#fff6dc', .9, False))
    cv.drawPath(glass, ink(cv, 2))
    cup = rect(x - 16 * s, y - 2 * s, 32 * s, 10 * s, 4)
    flat(cv, cup, GOLD, GOLD_SH, None, 2, line=2)
    capp = poly([(x - 28 * s, y - 52 * s), (x + 28 * s, y - 52 * s), (x, y - 74 * s)])
    flat(cv, capp, GOLD, GOLD_SH, GOLD_HI, 3, 2, line=2)
    cv.drawCircle(x, y - 78 * s, 5 * s, fillp(cv, GOLD, 1))


def crest(cv, x, y, s=1.0):
    """Familienwappen: Schild mit dem Ring der Schlange, graviert in Gold."""
    sh = skia.Path()
    sh.moveTo(x - 50 * s, y - 60 * s)
    sh.lineTo(x + 50 * s, y - 60 * s)
    sh.lineTo(x + 50 * s, y + 10 * s)
    sh.cubicTo(x + 50 * s, y + 50 * s, x + 10 * s, y + 66 * s, x, y + 74 * s)
    sh.cubicTo(x - 10 * s, y + 66 * s, x - 50 * s, y + 50 * s, x - 50 * s, y + 10 * s)
    sh.close()
    flat(cv, sh, '#2f3a2a', '#232c20', '#3f4d38', 6, 3, ghost=True)
    cv.drawPath(sh, strokep(cv, 6 * s, GOLD))
    cv.drawPath(sh, ink(cv, 2))
    ring = skia.Path()
    ring.addArc(skia.Rect.MakeXYWH(x - 28 * s, y - 30 * s, 56 * s, 56 * s), -60, 320)
    cv.drawPath(ring, strokep(cv, 9 * s, GOLD))
    cv.drawPath(ring, strokep(cv, 3 * s, GOLD_DK))
    hd = oval(x - 2 * s, y - 42 * s, 26 * s, 20 * s)
    cv.drawPath(hd, fillp(cv, GOLD, 1))
    cv.drawPath(hd, ink(cv, 1.6))
    for k in (-1, 1):
        cv.drawCircle(x + 11 * s + k * 5 * s, y - 33 * s, 2.2 * s, fillp(cv, GOLD_DK, 1, False))
    rib = poly([(x - 82 * s, y + 70 * s), (x + 82 * s, y + 70 * s), (x + 74 * s, y + 94 * s), (x - 74 * s, y + 94 * s)])
    flat(cv, rib, '#efe6d2', '#d1c6ad', None, 3, line=1.8)
    text(cv, 'SEMPER RENOVATA', x, y + 88 * s, TF_CAPS, 11 * s, '#2a2017', anchor='c', spacing=1.0 * s)


def armchair_back(cv, cx, seat_y, w):
    h = w * 1.05
    back = skia.Path()
    back.moveTo(cx - w * .40, seat_y)
    back.lineTo(cx - w * .42, seat_y - h * .55)
    back.cubicTo(cx - w * .44, seat_y - h * .95, cx + w * .44, seat_y - h * .95, cx + w * .42, seat_y - h * .55)
    back.lineTo(cx + w * .40, seat_y)
    back.close()
    flat(cv, back, LEATHER, LEATHER_DK, LEATHER_HI, 14, 7, ghost=True)
    cv.save()
    cv.clipPath(back, doAntiAlias=True)
    for r in range(4):
        for c_ in range(5):
            bx = cx - w * .30 + c_ * w * .15 + (w * .075 if r % 2 else 0)
            by = seat_y - h * .72 + r * h * .15
            cv.drawCircle(bx, by, 4, fillp(cv, GOLD_SH, 1, False))
            for (dx, dy) in ((-14, -10), (14, -10), (-14, 10), (14, 10)):
                cv.drawLine(bx, by, bx + dx, by + dy, strokep(cv, 1.6, LEATHER_DK, .8))
    cv.restore()
    for sx in (-1, 1):
        wing = skia.Path()
        wx = cx + sx * w * .42
        wing.moveTo(wx, seat_y - h * .62)
        wing.cubicTo(wx + sx * w * .14, seat_y - h * .70, wx + sx * w * .16, seat_y - h * .40, wx + sx * w * .10, seat_y - h * .18)
        wing.lineTo(wx, seat_y - h * .14)
        wing.close()
        flat(cv, wing, LEATHER, LEATHER_DK, LEATHER_HI, 8, 4)
    seat = rect(cx - w * .40, seat_y - 30, w * .80, 54, 18)
    flat(cv, seat, LEATHER_HI, LEATHER_DK, '#a85848', 8, 4)


def armchair_front(cv, cx, seat_y, w):
    for sx in (-1, 1):
        ax = cx + sx * w * .44
        arm = skia.Path()
        arm.moveTo(ax - w * .09, seat_y + 90)
        arm.lineTo(ax - w * .09, seat_y - 40)
        arm.cubicTo(ax - w * .09, seat_y - 78, ax + w * .09, seat_y - 78, ax + w * .09, seat_y - 40)
        arm.lineTo(ax + w * .09, seat_y + 90)
        arm.close()
        flat(cv, arm, LEATHER, LEATHER_DK, LEATHER_HI, 10, 5)
        roll = circle(ax, seat_y - 40, w * .09)
        flat(cv, roll, LEATHER_HI, LEATHER_DK, '#a85848', 6, 3)
        cv.drawPath(P_([(ax, seat_y - 40 - w * .05), (ax + w * .03, seat_y - 40, ax, seat_y - 40 + w * .05, ax - w * .02, seat_y - 40)],
                       close=False), strokep(cv, 2, LEATHER_DK))
    skirt = rect(cx - w * .40, seat_y + 22, w * .80, 70, 6)
    flat(cv, skirt, LEATHER, LEATHER_DK, LEATHER_HI, 10, 5)
    for k in range(int(w * .8 / 16)):
        nx = cx - w * .40 + 8 + k * 16
        cv.drawCircle(nx, seat_y + 30, 3, fillp(cv, GOLD, 1, False))
    for sx in (-1, 1):
        leg = poly([(cx + sx * w * .36 - 9, seat_y + 92), (cx + sx * w * .36 + 9, seat_y + 92), (cx + sx * w * .36 + 5, seat_y + 122),
                    (cx + sx * w * .36 - 5, seat_y + 122)])
        flat(cv, leg, WOOD_DK, None, WOOD_HI, 3, line=2)


def side_table(cv, x, y_floor, h=170, r=78):
    top_y = y_floor - h
    ped = poly([(x - 12, top_y + 10), (x + 12, top_y + 10), (x + 18, y_floor - 30), (x - 18, y_floor - 30)])
    flat(cv, ped, WOOD, WOOD_DK, WOOD_HI, 5, 3)
    for sx in (-1, 1):
        foot = P_([(x, y_floor - 34), (x + sx * 30, y_floor - 26, x + sx * 50, y_floor - 10, x + sx * 58, y_floor),
                   (x + sx * 40, y_floor), (x + sx * 30, y_floor - 12, x + sx * 14, y_floor - 20, x, y_floor - 22)])
        flat(cv, foot, WOOD, WOOD_DK, WOOD_HI, 4, 2)
    top = oval(x - r, top_y - 12, 2 * r, 26)
    flat(cv, top, WOOD_HI, WOOD_DK, '#7a5b45', 5, 3, ghost=True)
    edge = rect(x - r, top_y, 2 * r, 12)
    cv.drawPath(edge, fillp(cv, WOOD, 1))
    return top_y - 4


def teacup(cv, x, y, s=1.0):
    saucer = oval(x - 30 * s, y - 6 * s, 60 * s, 14 * s)
    flat(cv, saucer, '#efe6d2', '#d1c6ad', None, 3, line=2)
    cup = skia.Path()
    cup.moveTo(x - 20 * s, y - 34 * s)
    cup.lineTo(x + 20 * s, y - 34 * s)
    cup.cubicTo(x + 20 * s, y - 10 * s, x + 12 * s, y - 2 * s, x, y - 2 * s)
    cup.cubicTo(x - 12 * s, y - 2 * s, x - 20 * s, y - 10 * s, x - 20 * s, y - 34 * s)
    cup.close()
    flat(cv, cup, '#efe6d2', '#d1c6ad', None, 4, line=2)
    cv.drawLine(x - 18 * s, y - 24 * s, x + 18 * s, y - 24 * s, strokep(cv, 2.2, GOLD))
    handle = skia.Path()
    handle.addArc(skia.Rect.MakeXYWH(x + 14 * s, y - 30 * s, 16 * s, 16 * s), -90, 180)
    cv.drawPath(handle, strokep(cv, 3.4 * s, '#efe6d2'))
    cv.drawPath(handle, ink(cv, 1.6))
    for k in range(3):
        cv.drawPath(P_([(x - 8 * s + k * 8 * s, y - 40 * s), (x - 14 * s + k * 8 * s, y - 52 * s, x - 2 * s + k * 8 * s, y - 60 * s,
                         x - 8 * s + k * 8 * s, y - 72 * s)], close=False), strokep(cv, 2, '#e9e1c9', .35))


# ---------------------------------------------------------------- Der Butler (Hintergrundpointe)
def butler(cv, x, y_floor, s, t=0.0, pose='dust', target=None):
    """Kleiner goldener Diener-Roboter: Mini-EDEN mit Fliege. s = Hoehe in px."""
    k = s / 100
    base_y = y_floor - 8 * k
    bw, bh = 44 * k, 56 * k
    by = base_y - bh - 10 * k
    wheel = oval(x - 30 * k, base_y - 12 * k, 60 * k, 20 * k)
    flat(cv, wheel, '#2a2726', None, '#4a4542', 4, line=2)
    body = rect(x - bw / 2, by, bw, bh + 6 * k, 12 * k)
    flat(cv, body, GOLD, GOLD_SH, GOLD_HI, 7 * k, 4 * k, ghost=True)
    for j in range(2):
        cv.drawLine(x - bw / 2 + 4, by + bh * (.45 + j * .25), x + bw / 2 - 4, by + bh * (.45 + j * .25), strokep(cv, 2, GOLD_DK, .8))
    head = skia.Path()
    hw, hh = 40 * k, 34 * k
    hy = by - hh - 2 * k
    head.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - hw / 2, hy, hw, hh), 12 * k, 12 * k))
    flat(cv, head, GOLD, GOLD_SH, GOLD_HI, 6 * k, 3 * k)
    cap = oval(x - hw / 2, hy - 6 * k, hw, 12 * k)
    flat(cv, cap, '#e6c77c', GOLD_SH, None, 3 * k, line=2)
    visor = rect(x - hw * .38, hy + hh * .28, hw * .76, hh * .42, 7 * k)
    cv.drawPath(visor, fillp(cv, '#161514', 1))
    for sx in (-1, 1):
        cv.drawPath(P_([(x + sx * 9 * k - 4 * k, hy + hh * .50), (x + sx * 9 * k, hy + hh * .42, x + sx * 9 * k, hy + hh * .42,
                         x + sx * 9 * k + 4 * k, hy + hh * .50)], close=False), strokep(cv, 2.2 * k, GOLD_HI))
    cv.drawPath(P_([(x - 5 * k, hy + hh * .60), (x, hy + hh * .64, x, hy + hh * .64, x + 5 * k, hy + hh * .60)], close=False),
                strokep(cv, 2 * k, GOLD_HI))
    cv.drawPath(visor, ink(cv, 2))
    cv.drawLine(x, hy - 6 * k, x, hy - 18 * k, strokep(cv, 2.4 * k, GOLD_DK))
    cv.drawCircle(x, hy - 20 * k, 4 * k, fillp(cv, GOLD_HI, 1))
    tie = union([poly([(x, by + 4 * k), (x - 12 * k, by - 3 * k), (x - 12 * k, by + 11 * k)]),
                 poly([(x, by + 4 * k), (x + 12 * k, by - 3 * k), (x + 12 * k, by + 11 * k)])])
    cv.drawPath(tie, fillp(cv, '#161514', 1))
    sh_l, sh_r = (x - bw / 2, by + 12 * k), (x + bw / 2, by + 12 * k)
    if pose == 'dust':
        tx, ty = target if target else (x - 60 * k, by - 70 * k)
        el = (lerp(sh_l[0], tx, .45) - 10 * k, lerp(sh_l[1], ty, .45) + 14 * k)
        R.robot_arm(cv, [sh_l, el, (tx, ty)], 8 * k)
        cv.save()
        cv.translate(tx, ty)
        cv.rotate(-35 + 12 * math.sin(t * 8))
        cv.drawLine(0, 0, 0, -34 * k, strokep(cv, 4.5 * k, INK))
        cv.drawLine(0, 0, 0, -34 * k, strokep(cv, 2.6 * k, WOOD_HI))
        rnd = random.Random(2)
        for j in range(16):
            fx, fy = rnd.uniform(-13, 13) * k, -34 * k - rnd.uniform(0, 30) * k
            cv.drawCircle(fx, fy, rnd.uniform(6, 10) * k, fillp(cv, rnd.choice(['#d9cfb6', '#bfb49a', '#e8e0cc']), 1))
        for j in range(16):
            fx, fy = rnd.uniform(-13, 13) * k, -34 * k - rnd.uniform(0, 30) * k
            cv.drawCircle(fx, fy, rnd.uniform(3, 6) * k, fillp(cv, '#efe8d6', .9, False))
        cv.restore()
        R.robot_arm(cv, [sh_r, (sh_r[0] + 10 * k, sh_r[1] + 22 * k), (sh_r[0] + 6 * k, sh_r[1] + 40 * k)], 7 * k)
    elif pose == 'tray':
        hand = (sh_r[0] + 26 * k, sh_r[1] + 4 * k)
        R.robot_arm(cv, [sh_r, (sh_r[0] + 16 * k, sh_r[1] + 16 * k), hand], 7 * k)
        tray = oval(hand[0] - 40 * k, hand[1] - 8 * k, 80 * k, 16 * k)
        flat(cv, tray, '#c9c3b2', '#a8a291', '#e2ddd0', 3, line=2)
        teacup(cv, hand[0] - 6 * k, hand[1] - 2 * k, .8 * k)
        R.robot_arm(cv, [sh_l, (sh_l[0] - 8 * k, sh_l[1] + 22 * k), (sh_l[0] - 2 * k, sh_l[1] + 40 * k)], 7 * k)
    elif pose == 'card':
        hand = (sh_r[0] + 30 * k, sh_r[1] - 26 * k)
        R.robot_arm(cv, [sh_r, (sh_r[0] + 22 * k, sh_r[1] + 6 * k), hand], 7 * k)
        R.robot_arm(cv, [sh_l, (sh_l[0] - 8 * k, sh_l[1] + 22 * k), (sh_l[0] - 2 * k, sh_l[1] + 40 * k)], 7 * k)
        return hand
    return None


# ---------------------------------------------------------------- Galerie an der Wand
def small_plaque(cv, cx, y, year, topic, s=.8):
    f1, f2 = 26 * s, 17 * s
    w = max(P.text_w(TF_CAPS, f2, topic, 3 * s), P.text_w(TF_HEAD, f1, year)) + 30 * s
    r = rect(cx - w / 2, y, w, 52 * s, 5)
    flat(cv, r, GOLD_SH, GOLD_DK, GOLD, 3, 2, line=1.8)
    text(cv, year, cx, y + 23 * s, TF_HEAD, f1, '#2a2017', anchor='c')
    text(cv, topic, cx, y + 44 * s, TF_CAPS, f2, '#2a2017', anchor='c', spacing=3 * s)


GALLERY = [  # era index, x, y, w, h, oval
    (0, 385, 135, 120, 150, True),
    (1, 560, 150, 105, 135, False),
    (2, 724, 160, 105, 125, False),
    (3, 400, 400, 110, 110, True),
    (4, 575, 395, 115, 115, False),
]


def gallery(cv):
    for (ei, x, y, w, h, ov) in GALLERY:
        T.frame_at(cv, x, y, w, h, T.portrait(T.ERAS[ei], w, h), ov)
        small_plaque(cv, x + w / 2, y + h + 32, T.ERAS[ei][0], T.ERAS[ei][1], .66)
    crest(cv, 790, 450, .95)


def step_stool(cv, x, y_floor, w=110, h=96):
    top = rect(x - w / 2, y_floor - h, w, 16, 3)
    for sx in (-1, 1):
        leg = poly([(x + sx * (w / 2 - 14) - 7, y_floor - h + 10), (x + sx * (w / 2 - 14) + 7, y_floor - h + 10),
                    (x + sx * (w / 2 - 6) + 7, y_floor), (x + sx * (w / 2 - 6) - 7, y_floor)])
        flat(cv, leg, WOOD, WOOD_DK, WOOD_HI, 3, line=2)
    rung = rect(x - w / 2 + 10, y_floor - h * .45, w - 20, 10, 3)
    flat(cv, rung, WOOD, WOOD_DK, None, 3, line=2)
    flat(cv, top, WOOD_HI, WOOD_DK, '#7a5b45', 4, 2, ghost=True)
    return y_floor - h


# ================================================================ Schluesselbild: der Salon
def salon(cv, t=0.0, snake_expr='neutral', snake_look=(-0.45, 0.1)):
    Y_RAIL, Y_FLOOR = 600, 850
    wallpaper(cv, -50, -50, W + 50, Y_RAIL)
    halftone(cv, -10, -10, 520, 380, '#0c0d0a', 16, 4.5, 'left', .45)
    wainscot(cv, -50, W + 50, Y_RAIL, Y_FLOOR)
    floor(cv, Y_FLOOR)
    rug(cv, 1140, 900, 1000, 1500, 1060)
    bookshelf(cv, 30, 130, 300, Y_FLOOR - 130)
    window(cv, 1735, 110, 175, 430, t)
    moonbeams(cv, 1740, 1905, 300, 1100, 1560, H, .07)
    gas_lamp(cv, 935, 230, .85)
    gas_lamp(cv, 1325, 230, .85)
    rail = rect(-50, 62, W + 100, 14)
    flat(cv, rail, WOOD_HI, WOOD_DK, '#7a5b45', 4, 2)
    for (ei, x, y, w, h, ov) in GALLERY[:3]:
        for sx in (-1, 1):
            cv.drawLine(x + w / 2 + sx * 4, 74, x + w / 2 + sx * w * .3, y - 20, strokep(cv, 2, GOLD_DK, .9))
    for (x0, x1, yb) in ((1130 - 110, 1130 + 110, 114),):
        for xx in (x0 + 40, x1 - 40):
            cv.drawLine(1130, 74, xx, yb, strokep(cv, 2, GOLD_DK, .9))
    gallery(cv)
    fx = 1130
    shelf_y = fireplace(cv, fx, Y_FLOOR, 400, 330, t)
    gx, gy, gw, gh = fx - 110, 140, 220, 240
    T.frame_at(cv, gx, gy, gw, gh, None, False, gold=True)
    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), glowp(cv, GOLD_HI, 40, .22))
    text(cv, '?', gx + gw / 2, gy + gh / 2 + 40, TF_D, 120, GOLD, anchor='c')
    small_plaque(cv, gx + gw / 2, gy + gh + 30, 'TODAY', 'AI', .75)
    for (sx, sy, r) in ((gx - 18, gy + 30, 11), (gx + gw + 20, gy + 70, 8), (gx + gw - 10, gy - 22, 9)):
        sparkle(cv, sx, sy, r)
    candlestick(cv, fx - 150, shelf_y, .9)
    mantel_clock(cv, fx + 170, shelf_y, .9)
    ty = side_table(cv, 1395, Y_FLOOR + 30, 190, 68)
    ST.stand(cv, 1395, ty - 22, 66)
    ST.ball_at(cv, 1395, ty - 86, 61, 2.0)
    for (sx, sy, r) in ((1335, ty - 150, 8), (1455, ty - 115, 6)):
        sparkle(cv, sx, sy, r)
    cx, seat_y, cw = 1640, 790, 330
    armchair_back(cv, cx, seat_y, cw)
    M.draw_mascot(cv, cx + 60, seat_y - 290, 128, snake_expr, snake_look, -6, reflect=.15)
    armchair_front(cv, cx, seat_y, cw)
    st_y = step_stool(cv, 470, Y_FLOOR + 6, 120, 110)
    butler(cv, 470, st_y + 8, 120, t, 'dust', target=(430, 560))
    fire = skia.Paint()
    fire.setShader(skia.GradientShader.MakeRadial(skia.Point(fx, Y_FLOOR), 600, [col('#f0a24a', .14), col('#f0a24a', 0)]))
    cv.drawRect(skia.Rect.MakeLTRB(fx - 700, Y_FLOOR - 500, fx + 700, H), fire)
    R.dust(cv, t, (1100, 300, 1900, 1000), 40, 6, '#dfe6ea', .3)
    halftone(cv, -10, 900, W + 10, H + 10, '#000000', 16, 4, 'down', .35)


def f_salon(out):
    surf, cv = F.new_canvas()
    salon(cv, 1.0)
    F.finish(surf, out)


FR = {'salon': f_salon}


# ================================================================ Uebergaenge
def bust(cv, x, y, s, expr='neutral', look=(0, 0), tilt=0.0, reflect=0.0, talk=0.0, lean=0.0):
    """Kopf mit Hals, der aus dem Bild nach unten laeuft."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    pts = [(0.0, 0.25), (lean * .3, 1.2), (lean, 2.6)]
    neck = M.tube(pts, [0.26, 0.29, 0.31])
    cv.drawPath(neck, fillp(cv, M.SN, 1))
    cv.save()
    cv.clipPath(neck, doAntiAlias=True)
    cv.drawPath(M.minus(neck, M.shifted(neck, -0.06, 0)), fillp(cv, M.SN_SH, 1, False))
    cv.drawPath(M.tube([(0.04, 0.25), (lean * .3 + .04, 1.2), (lean + .04, 2.6)], [0.10, 0.12, 0.13]), fillp(cv, M.SN_BELLY, 1, False))
    cv.drawPath(M.minus(neck, M.shifted(neck, 0.035, 0)), fillp(cv, M.SN_RIM, .9, False))
    cv.restore()
    cv.drawPath(neck, M.ink(cv))
    M.draw_collar(cv)
    M.draw_head(cv, expr, look, tilt, False, 1.0, reflect=reflect, talk=talk)
    cv.restore()


def wall_only(cv, y_rail=760):
    wallpaper(cv, -50, -50, W + 50, y_rail)
    wainscot(cv, -50, W + 50, y_rail, H + 60)


def scaled_into(cv, arr, x, y, w, h):
    K.fit_rect(cv, K.to_img(arr), x, y, w, h)


def past1(t=0.0):
    surf, cv = F.new_canvas()
    wall_only(cv, 820)
    gas_lamp(cv, 1130, 300, 1.2)
    era = T.ERAS[2]
    T.frame_at(cv, 420, 170, 520, 440, T.portrait(era, 520, 440), False)
    small_plaque(cv, 680, 650, era[0], era[1], 1.1)
    bust(cv, 1520, 700, 300, 'neutral', look=(-0.75, -0.35), tilt=-10, lean=.2)
    halftone(cv, -10, 700, W + 10, H + 10, '#000000', 16, 4, 'down', .35)
    return K.snap(surf)


HORSE_FILM = None


def horse_film(seed=3):
    import os
    path = 'frames9/horses_notext.png'
    if not os.path.exists(path):
        keep = F.extruded
        F.extruded = lambda *a, **k: 0
        F.f_horses(path)
        F.extruded = keep
    return K.film_look(K.load(path), 'sepia', seed=seed)


def past2(t=0.0):
    surf, cv = F.new_canvas()
    wall_only(cv, 1040)
    x, y, w, h = 150, 60, 1620, 911
    T.frame_at(cv, x, y, w, h, None, False)
    cv.save()
    cv.clipRect(skia.Rect.MakeXYWH(x, y, w, h))
    scaled_into(cv, horse_film(4), x, y, w, h)
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fillp(cv, '#fff2cf', .06, False))
    cv.restore()
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), ink(cv, 2.4))
    return K.snap(surf)


def past3(t=0.0):
    arr = horse_film(9).copy()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawImage(K.to_img(arr), 0, 0)
    band = rect(0, 940, W, 140)
    cv.drawPath(band, fillp(cv, '#0e0c0a', .85, False))
    P.draw_text(cv, '1915  ·  THE TRACTOR', 90, 1015, TF_CAPS, 30, fillp(cv, '#e9e1c9', 1, False), spacing=9)
    arr = K.snap(surf)
    return K.film_look(arr, 'sepia', seed=21, scratches=3, dust=20, vign=.2, grain=.02)


def fut1(t=0.0):
    surf, cv = F.new_canvas()
    wall_only(cv, 640)
    cv.drawRect(skia.Rect.MakeLTRB(-50, 900, W + 50, H + 50), fillp(cv, '#2a1d16', 1, False))
    top = oval(1150 - 300, 840, 600, 90)
    flat(cv, top, WOOD_HI, WOOD_DK, '#7a5b45', 8, 4, ghost=True)
    cv.drawRect(skia.Rect.MakeXYWH(1150 - 300, 885, 600, 40), fillp(cv, WOOD, 1))
    ST.stand(cv, 1150, 820, 230)
    ST.ball_at(cv, 1150, 560, 250, 2.0)
    for (sx, sy, r) in ((900, 330, 14), (1420, 420, 10), (1380, 260, 8)):
        sparkle(cv, sx, sy, r)
    bust(cv, 540, 470, 330, 'surprised', look=(0.75, 0.2), tilt=10, reflect=1.0, lean=-.3)
    return K.snap(surf)


def city_frame(t=8.6):
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    P.G.zoom = 1.0
    R.s_city(cv, t)
    P.fiction_label(cv, 1.0)
    return K.snap(surf)


def fut2(t=0.0):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#0d0b0a', 1, False))
    cx, cy, r = 960, 560, 640
    cv.save()
    cv.clipPath(circle(cx, cy, r), doAntiAlias=True)
    scaled_into(cv, city_frame(8.0), cx - r * 1.5, cy - r * .84, r * 3.0, r * 1.69)
    vg = skia.Paint(AntiAlias=True)
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, [col('#000000', 0), col('#000000', 0), col('#0b0a07', .65)], [0, .72, 1]))
    cv.drawCircle(cx, cy, r, vg)
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(cx - r * .82, cy - r * .82, r * 1.64, r * 1.64), 200, 52)
    cv.drawPath(hl, strokep(cv, r * .05, '#fff6dc', .4))
    cv.restore()
    cv.drawPath(circle(cx, cy, r), ink(cv, 4))
    cv.drawCircle(cx, cy, r + 30, glowp(cv, GOLD_HI, 60, .25))
    return K.snap(surf)


def board_panel(cv, x, y, w, h, arr, title, sub):
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 10, 10)
    cv.save()
    cv.clipRRect(r, doAntiAlias=True)
    K.fit_rect(cv, K.to_img(arr), x, y, w, h)
    cv.restore()
    cv.drawRRect(r, strokep(cv, 3, '#3a3c3b'))
    text(cv, title, x, y + h + 36, TF_HEAD, 26, BONE_HI)
    text(cv, sub, x, y + h + 66, TF_HEAD, 20, BONE_SH)


def arrow(cv, x, y):
    cv.drawLine(x - 14, y, x + 10, y, strokep(cv, 4, GOLD))
    cv.drawPath(poly([(x + 18, y), (x + 4, y - 10), (x + 4, y + 10)]), fillp(cv, GOLD, 1, False))


def f_transitions(out):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    P.draw_text(cv, 'ÜBERGÄNGE AUS DEM SALON', 80, 70, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    rows = [
        ('GESCHICHTE  ·  INS PORTRÄT', [(past1(), 'Die Schlange blickt auf ein Porträt', 'die Kamera fährt auf das Bild an der Wand zu'),
                                         (past2(), 'Das Bild erwacht', 'im Rahmen läuft die Szene schon als alter Film'),
                                         (past3(), 'Alter Film, bildfüllend', 'Sepia, Kratzer, Flackern; zurück auf demselben Weg')]),
        ('ZUKUNFT  ·  IN DIE KUGEL', [(fut1(), 'Die Schlange beugt sich zur Kugel', 'die goldene Stadt spiegelt sich in ihrer Brille'),
                                        (fut2(), 'Durch das Glas', 'die Kugel füllt das Bild, der Rand bleibt sichtbar'),
                                        (city_frame(8.6), 'EDEN, bildfüllend', 'FICTION am Rand; P-10 ist dieselbe Fahrt rückwärts')]),
    ]
    pw, ph = 540, 304
    for ri, (label, panels) in enumerate(rows):
        y = 150 + ri * 455
        P.draw_text(cv, label, 80, y - 18, TF_CAPS, 20, fillp(cv, BONE_SH, 1, False), spacing=5)
        for k, (arr, t1, t2) in enumerate(panels):
            x = 80 + k * (pw + 60)
            board_panel(cv, x, y, pw, ph, arr, t1, t2)
            if k < 2:
                arrow(cv, x + pw + 30, y + ph / 2)
    F.finish(surf, out)


FR['transitions'] = f_transitions


# ================================================================ Kapitelkarte: Seite aus den Memoiren
PAPER, PAPER_SH, PAPER_DK = '#e4d9bd', '#cbbd99', '#a8987a'


def page_path(x0, x1, y0, y1, gutter_left, curl=18):
    """Buchseite mit leicht gewoelbter Ober- und Unterkante; gutter_left: Falz links (rechte Seite)."""
    p = skia.Path()
    if gutter_left:
        p.moveTo(x0, y0 + curl)
        p.cubicTo(x0 + (x1 - x0) * .25, y0 - curl * .4, x0 + (x1 - x0) * .7, y0, x1, y0 + 4)
        p.lineTo(x1, y1 - 4)
        p.cubicTo(x0 + (x1 - x0) * .7, y1, x0 + (x1 - x0) * .25, y1 + curl * .4, x0, y1 - curl * .5)
    else:
        p.moveTo(x0, y0 + 4)
        p.cubicTo(x0 + (x1 - x0) * .3, y0, x0 + (x1 - x0) * .75, y0 - curl * .4, x1, y0 + curl)
        p.lineTo(x1, y1 - curl * .5)
        p.cubicTo(x0 + (x1 - x0) * .75, y1 + curl * .4, x0 + (x1 - x0) * .3, y1, x0, y1 - 4)
    p.close()
    return p


def flourish(cv, cx, y, w, c='#5b4a36', a=1.0):
    for sx in (-1, 1):
        p = skia.Path()
        p.moveTo(cx + sx * 18, y)
        p.cubicTo(cx + sx * w * .2, y - 14, cx + sx * w * .35, y + 14, cx + sx * w * .5, y)
        p.moveTo(cx + sx * w * .3, y + 2)
        p.cubicTo(cx + sx * w * .34, y - 16, cx + sx * w * .42, y - 14, cx + sx * w * .4, y - 4)
        cv.drawPath(p, strokep(cv, 2.2, c, a))
    dm = poly([(cx, y - 9), (cx + 9, y), (cx, y + 9), (cx - 9, y)])
    cv.drawPath(dm, fillp(cv, c, a, False))


def page_border(cv, x0, y0, x1, y1, c='#8a6a33'):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(cv, 2.6, c, .9))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 9, y0 + 9, x1 - 9, y1 - 9), strokep(cv, 1.2, c, .8))
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        cv.save()
        cv.translate(x, y)
        cv.scale(sx, sy)
        p = skia.Path()
        p.moveTo(9, 34)
        p.cubicTo(9, 18, 18, 9, 34, 9)
        p.moveTo(18, 40)
        p.cubicTo(22, 26, 26, 22, 40, 18)
        cv.drawPath(p, strokep(cv, 1.8, c, .9))
        cv.drawCircle(20, 20, 4, fillp(cv, c, .9, False))
        cv.restore()


def wrap(s, tf, size, maxw):
    f = skia.Font(tf, size)
    words, lines, cur = s.split(), [], ''
    for w_ in words:
        t_ = (cur + ' ' + w_).strip()
        if f.measureText(t_) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = t_
    if cur:
        lines.append(cur)
    return lines


def memoir_spread(cv, num='I', ordinal='THE FIRST', title=('Haven’t we survived', 'this before?'),
                  sub='In which the weavers smash the machines, Mr Ford doubles the pay, and the economy learns to bite its own tail.'):
    gx = 960
    y0, y1 = 150, 930
    cover = skia.Path()
    cover.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(gx - 760, y0 - 26, gx + 760, y1 + 30), 22, 22))
    M.ghost(cv, cover)
    cv.drawPath(cover, fillp(cv, '#3a1d1a', 1))
    cv.drawPath(M.minus(cover, M.shifted(cover, -10, -10)), fillp(cv, '#2a1312', 1, False))
    cv.drawPath(cover, ink(cv, 2.6))
    for k in range(4):
        cv.drawRect(skia.Rect.MakeLTRB(gx - 740 + k * 3, y0 - 10 + k * 3, gx + 740 - k * 3, y1 + 14 - k * 3), strokep(cv, 1.6, PAPER_DK, .6))
    left = page_path(gx - 720, gx - 6, y0, y1, False)
    right = page_path(gx + 6, gx + 720, y0, y1, True)
    for pg, gl in ((left, False), (right, True)):
        cv.drawPath(pg, fillp(cv, PAPER, 1))
        cv.save()
        cv.clipPath(pg, doAntiAlias=True)
        g = skia.Paint()
        if gl:
            g.setShader(skia.GradientShader.MakeLinear([skia.Point(gx, 0), skia.Point(gx + 160, 0)], [col('#6a5a40', .55), col('#6a5a40', 0)]))
        else:
            g.setShader(skia.GradientShader.MakeLinear([skia.Point(gx, 0), skia.Point(gx - 160, 0)], [col('#6a5a40', .55), col('#6a5a40', 0)]))
        cv.drawPaint(g)
        rnd = random.Random(7 if gl else 3)
        for _ in range(18):
            cv.drawCircle(rnd.uniform(gx - 720, gx + 720), rnd.uniform(y0, y1), rnd.uniform(10, 40), fillp(cv, PAPER_SH, .18, False))
        cv.restore()
        cv.drawPath(pg, ink(cv, 2.2))
    cv.drawLine(gx, y0 + 10, gx, y1 - 6, strokep(cv, 3, '#6a5a40', .8))
    # linke Seite: Ring, Kapitelnummer
    lx0, lx1 = gx - 650, gx - 80
    page_border(cv, lx0, y0 + 70, lx1, y1 - 60)
    text(cv, 'THE MEMOIRS OF THE ECONOMY', (lx0 + lx1) / 2, y0 + 46, TF_CAPS, 18, '#6a5a40', anchor='c', spacing=5)
    lc = (lx0 + lx1) / 2
    cv.drawCircle(lc, 420, 118, fillp(cv, '#d8cba9', 1, False))
    cv.drawCircle(lc, 420, 118, strokep(cv, 2, '#8a6a33', .8))
    text(cv, num, lc, 452, TF_TITLE, 96, '#8a6a33', anchor='c')
    T.ring(cv, lc, 420, 150, 30, 'smug', look=(0.1, 0.2), tilt=-6)
    text(cv, 'CHAPTER', lc, 690, TF_CAPS, 34, '#3b2f22', anchor='c', spacing=12)
    text(cv, ordinal, lc, 745, TF_CAPS, 44, '#3b2f22', anchor='c', spacing=10)
    flourish(cv, lc, 790, 300)
    # rechte Seite: Titel, Untertitel, Initiale
    rx0, rx1 = gx + 90, gx + 650
    text(cv, 'CHAPTER ' + num, (rx0 + rx1) / 2, y0 + 46, TF_CAPS, 18, '#6a5a40', anchor='c', spacing=5)
    yy = 330
    for ln in title:
        fs = 76
        f = skia.Font(TF_D, fs)
        while f.measureText(ln) > rx1 - rx0:
            fs -= 2
            f = skia.Font(TF_D, fs)
        w_ = f.measureText(ln)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ln, f), (rx0 + rx1) / 2 - w_ / 2, yy, fillp(cv, '#241c14', 1, False))
        yy += 92
    flourish(cv, (rx0 + rx1) / 2, yy - 20, 320)
    yy += 50
    for ln in wrap(sub, TF_QUOTE, 36, rx1 - rx0 - 40):
        text(cv, ln, (rx0 + rx1) / 2, yy, TF_QUOTE, 36, '#4a3b2a', anchor='c')
        yy += 50
    cap_y = yy + 40
    cv.drawRect(skia.Rect.MakeXYWH(rx0 + 20, cap_y, 86, 86), fillp(cv, '#3a1d1a', 1, False))
    cv.drawRect(skia.Rect.MakeXYWH(rx0 + 20, cap_y, 86, 86), strokep(cv, 2.4, GOLD))
    text(cv, 'E', rx0 + 63, cap_y + 70, TF_TITLE, 68, GOLD, anchor='c')
    rnd = random.Random(2)
    for k in range(4):
        lx = rx0 + 126 if k < 2 else rx0 + 20
        ly = cap_y + 18 + k * 30
        if ly > y1 - 70:
            break
        cv.drawLine(lx, ly, rx1 - 20 - rnd.uniform(40, 120) * (k == 3), ly, strokep(cv, 9, '#b8a984', .55))
    text(cv, '- 1 -', (rx0 + rx1) / 2, y1 - 22, TF_QUOTE, 22, '#6a5a40', anchor='c')


def desk(cv):
    cv.drawPaint(fillp(cv, '#2b1c14', 1, False))
    rnd = random.Random(12)
    for k in range(48):
        y = k * 24 + rnd.uniform(-6, 6)
        p = skia.Path()
        p.moveTo(-20, y)
        for x in range(0, W + 80, 80):
            p.lineTo(x, y + 6 * math.sin(x * .004 + k * 1.3) + 3 * math.sin(x * .017 + k))
        cv.drawPath(p, strokep(cv, 2.2, '#24170f', .9))
    for k in range(5):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, H)
        cv.drawOval(skia.Rect.MakeXYWH(x, y, 70, 22), strokep(cv, 2, '#24170f', .8))


def quill_and_ink(cv, x, y):
    well = rect(x - 46, y - 30, 92, 70, 14)
    flat(cv, well, '#1d2226', '#121518', '#3a434a', 6, 3, ghost=True)
    top = oval(x - 30, y - 42, 60, 22)
    flat(cv, top, GOLD, GOLD_SH, GOLD_HI, 3, 2, line=2)
    cv.save()
    cv.translate(x + 6, y - 40)
    cv.rotate(-32)
    shaft = M.tube([(0, 0), (0, -330)], [3, 2])
    cv.drawPath(shaft, fillp(cv, '#e8e0cc', 1))
    vane = skia.Path()
    vane.moveTo(0, -90)
    vane.cubicTo(-46, -160, -50, -280, -6, -360)
    vane.cubicTo(30, -300, 34, -160, 0, -90)
    vane.close()
    flat(cv, vane, '#efe8d6', '#d0c6ad', None, 6, line=2)
    for k in range(14):
        yy = -110 - k * 17
        cv.drawLine(0, yy, -30 + abs(k - 7) * 2, yy - 22, strokep(cv, 1.4, '#c9bfa5', .9))
        cv.drawLine(0, yy, 26 - abs(k - 7) * 2, yy - 20, strokep(cv, 1.4, '#c9bfa5', .9))
    cv.drawPath(shaft, ink(cv, 1.6))
    cv.restore()


def f_chapter_book(out):
    surf, cv = F.new_canvas()
    desk(cv)
    cv.drawCircle(220, 120, 520, glowp(cv, '#f6d79a', 160, .22))
    memoir_spread(cv)
    quill_and_ink(cv, 1820, 900)
    hand_x, hand_y = 140, 940
    teacup(cv, hand_x, hand_y, 1.4)
    R.robot_arm(cv, [(-80, 1130), (40, 1060), (hand_x - 30, hand_y + 14)], 22)
    R.robot_hand(cv, hand_x - 30, hand_y + 14, 70, -20, curl=.55)
    halftone(cv, -10, -10, W + 10, 160, '#000000', 16, 4, 'up', .35)
    halftone(cv, -10, 960, W + 10, H + 10, '#000000', 16, 4, 'down', .35)
    F.finish(surf, out)


# ================================================================ Abspann im Salon
def f_endscreen(out):
    surf, cv = F.new_canvas()
    Y_RAIL, Y_FLOOR = 640, 870
    wallpaper(cv, -50, -50, W + 50, Y_RAIL)
    wainscot(cv, -50, W + 50, Y_RAIL, Y_FLOOR)
    floor(cv, Y_FLOOR)
    rug(cv, 960, 920, 1100, 1600, 1070)
    rail = rect(-50, 62, W + 100, 14)
    flat(cv, rail, WOOD_HI, WOOD_DK, '#7a5b45', 4, 2)
    slots = [(110, 210, 640, 360), (1170, 210, 640, 360)]
    for (x, y, w, h) in slots:
        for sx in (-1, 1):
            cv.drawLine(x + w / 2 + sx * 4, 74, x + w / 2 + sx * w * .3, y - 20, strokep(cv, 2, GOLD_DK, .9))
        T.frame_at(cv, x, y, w, h, None, False, gold=True)
        p = strokep(cv, 2.4, BONE_SH, .55)
        p.setPathEffect(skia.DashPathEffect.Make([16, 12], 0))
        cv.drawRect(skia.Rect.MakeXYWH(x + 18, y + 18, w - 36, h - 36), p)
        text(cv, 'NEXT VIDEO', x + w / 2, y + h / 2 + 10, TF_CAPS, 28, BONE_SH, .6, anchor='c', spacing=6)
        text(cv, 'end screen element', x + w / 2, y + h / 2 + 48, TF_HEAD, 20, '#6f716b', .8, anchor='c')
    gas_lamp(cv, 960 - 120, 200, .8)
    gas_lamp(cv, 960 + 120, 200, .8)
    crest(cv, 960, 250, 1.3)
    p = strokep(cv, 2.4, GOLD, .6)
    p.setPathEffect(skia.DashPathEffect.Make([12, 10], 0))
    cv.drawCircle(960, 250, 112, p)
    text(cv, 'SUBSCRIBE', 960, 400, TF_CAPS, 18, GOLD, .7, anchor='c', spacing=4)
    cx, seat_y, cw = 960, 830, 330
    armchair_back(cv, cx, seat_y, cw)
    M.draw_mascot(cv, cx + 60, seat_y - 290, 128, 'happy', (0, 0), -4, reflect=0)
    armchair_front(cv, cx, seat_y, cw)
    butler(cv, 1400, Y_FLOOR + 14, 135, 0, 'tray')
    ty = side_table(cv, 640, Y_FLOOR + 30, 190, 68)
    ST.stand(cv, 640, ty - 22, 66)
    ST.ball_at(cv, 640, ty - 86, 61, 2.0)
    halftone(cv, -10, 920, W + 10, H + 10, '#000000', 16, 4, 'down', .35)
    F.finish(surf, out)


FR['chapter_book'] = f_chapter_book
FR['endscreen'] = f_endscreen


# ================================================================ Tafel: visuelle Strategie
def f_strategy(out):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    P.draw_text(cv, 'VISUELLE STRATEGIE  ·  DAS HAUS DER SCHLANGE', 80, 70, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=6)
    text(cv, 'Die Schlange ist die Wirtschaft. Sie lebt in einem viktorianischen Herrenhaus und erzählt von dort aus.', 80, 112,
         TF_HEAD, 25, BONE)
    salon_img = K.load('manor/salon.png')
    worlds = [
        (salon_img, 'DER SALON', 'Erzählebene, Gegenwart', ['warm: Holz, Samt, Kerzen und Kamin', 'hier spricht die Schlange',
                                                            'Anfang und Ende jedes Videos']),
        (past3(), 'DIE PORTRÄTS', 'Geschichte', ['jede Epoche ein Porträt an der Wand', 'hinein geht es als alter Film',
                                                'Sepia oder Schwarzweiß, Kratzer, Flackern']),
        (city_frame(8.6), 'DIE KRISTALLKUGEL', 'Zukunft und Fiktion', ['alles Erfundene liegt in der Kugel', 'Anthrazit und Gold, EDEN',
                                                                      'FICTION am Bildrand']),
    ]
    pw, ph = 560, 315
    for k, (arr, t1, t2, pts) in enumerate(worlds):
        x, y = 80 + k * (pw + 40), 150
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, pw, ph), 10, 10)
        cv.save()
        cv.clipRRect(r, doAntiAlias=True)
        K.fit_rect(cv, K.to_img(arr), x, y, pw, ph)
        cv.restore()
        cv.drawRRect(r, strokep(cv, 3, '#3a3c3b'))
        P.draw_text(cv, t1, x, y + ph + 42, TF_CAPS, 26, fillp(cv, GOLD, 1, False), spacing=5)
        text(cv, t2, x, y + ph + 74, TF_HEAD, 22, BONE_HI)
        for j, ln in enumerate(pts):
            cv.drawCircle(x + 6, y + ph + 104 + j * 30 - 7, 3.5, fillp(cv, GOLD_DK, 1, False))
            text(cv, ln, x + 20, y + ph + 104 + j * 30, TF_HEAD, 21, BONE)
    y0 = 700
    cv.drawLine(80, y0 - 30, W - 80, y0 - 30, strokep(cv, 1.5, '#2c2e2d'))
    P.draw_text(cv, 'KEHRT IN JEDEM VIDEO WIEDER', 80, y0 + 10, TF_CAPS, 22, fillp(cv, GOLD, 1, False), spacing=5)
    items = [('Die Memoiren', 'jedes Kapitel eine Buchseite, mit „In which …“'),
             ('Das Wappen mit dem Ring', 'Kanallogo, zugleich der Abo-Knopf im Abspann'),
             ('Der leere goldene Rahmen', 'wartet auf die nächste Haut: heute die KI'),
             ('Der Butler', 'ein kleiner goldener Roboter; übernimmt jedes Mal etwas mehr'),
             ('Die Galerie wächst', 'jedes Video hängt ein neues Bild dazu')]
    for j, (a, b) in enumerate(items):
        yy = y0 + 56 + j * 50
        text(cv, a, 80, yy, TF_HEAD, 25, BONE_HI)
        text(cv, b, 400, yy, TF_HEAD, 22, BONE)
    P.draw_text(cv, 'REGELN', 1110, y0 + 10, TF_CAPS, 22, fillp(cv, GOLD, 1, False), spacing=5)
    rules = ['Die Schlange zeigt sich im Salon, an Kapitelanfängen,',
             'bei Pointen und als Kurve. In Porträt- und Kugelszenen',
             'nur, wenn sie etwas zeigt. Sonst sprechen die Bilder.',
             'Gold bedeutet Zukunft und Bedrohung, sonst nichts.',
             'Detail wie bei Rational Animations: Rasterpunkte,',
             'Funkeln, Lichtkegel, Staub, Korn, Tuschekontur.',
             'Jede Einstellung bewegt sich: eine langsame Fahrt.']
    for j, ln in enumerate(rules):
        text(cv, ln, 1110, y0 + 56 + j * 40, TF_HEAD, 22, BONE)
    F.finish(surf, out)


FR['strategy'] = f_strategy


if __name__ == '__main__':
    P.init_assets()
    R.init_layers()
    for name in sys.argv[1].split(','):
        FR[name](f'{sys.argv[2]}/{name}.png')
