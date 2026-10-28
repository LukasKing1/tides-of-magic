#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Ueberarbeitete Entwuerfe: eigene Kapitelkarte, Haeute als Ahnengalerie.

python3 frames10.py <name[,name...]> <outdir>     name: chapter_ring chapter_card gallery
"""
import math, random, sys
import numpy as np
import skia
import rich as R
import mascot as MA
import mascot2 as M2
import mascot3 as M
import frames9 as F
from rich_base import *

TF_CAPS, TF_HEAD, TF_TITLE, TF_TYPE, TF_D = P.TF_CAPS, P.TF_HEAD, P.TF_TITLE, P.TF_TYPE, M.TF_DISPLAY


def scales_bg(cv, a=.05, size=54):
    """Schuppenmuster als Markenzeichen im Hintergrund."""
    for row in range(-1, int(H / (size * .55)) + 2):
        for colm in range(-1, int(W / size) + 2):
            x = colm * size + (size / 2 if row % 2 else 0)
            y = row * size * .55
            p = skia.Path()
            p.addArc(skia.Rect.MakeXYWH(x - size / 2, y - size / 2, size, size), 20, 140)
            cv.drawPath(p, strokep(cv, 2.0, BONE, a))


def ring(cv, cx, cy, Rr, w, expr='smug', look=(0.2, 0.2), tilt=-6):
    pts, rad, bv = [], [], []
    n = 220
    for i in range(n + 1):
        u = i / n
        a = math.radians(lerp(-70, 252, u))
        pts.append((cx + Rr * math.cos(a), cy + Rr * math.sin(a)))
        rad.append(w if u < .55 else lerp(w, w * .28, ((u - .55) / .45) ** 1.1))
        bv.append((-math.cos(a), -math.sin(a)))
    F.snake_tube(cv, pts, rad, bv)
    F.head_at(cv, cx - 6, cy - Rr - w * .65, w * 3.2, expr, look=look, tilt=tilt, collar=False)


# ================================================================ Kapitelkarte A: der Ring
ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']


def f_chapter_ring(out, k=0, words=('Haven’t we survived', 'this before?')):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#171818', 1, False))
    scales_bg(cv, .045)
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(960, 430), 900, [col('#2a2b2a', .9), col('#0c0d0d', .0)]))
    cv.drawPaint(vg)
    cx, cy, Rr = 960, 420, 210
    cv.drawCircle(cx, cy, Rr * 1.3, glowp(cv, GOLD_HI, 110, .12))
    cv.drawCircle(cx, cy, Rr - 46, fillp(cv, '#101111', 1, False))
    cv.drawCircle(cx, cy, Rr - 60, strokep(cv, 3, GOLD_DK, .8))
    f = skia.Font(TF_TITLE, 190)
    s = ROMAN[k]
    tw = f.measureText(s)
    blob = skia.TextBlob.MakeFromString(s, f)
    cv.drawTextBlob(blob, cx - tw / 2 + 5, cy + 72, fillp(cv, '#000000', .6, False))
    g = skia.Paint(AntiAlias=True, Color=col(GOLD_HI, .35))
    g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    cv.drawTextBlob(blob, cx - tw / 2, cy + 66, g)
    cv.drawTextBlob(blob, cx - tw / 2, cy + 66, fillp(cv, GOLD, 1, False))
    ring(cv, cx, cy, Rr, 40)
    lab = 'CHAPTER ' + ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE'][k]
    lw = P.text_w(TF_CAPS, 30, lab, 12)
    P.draw_text(cv, lab, cx - lw / 2, 770, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=12)
    cv.drawLine(cx - lw / 2 - 90, 760, cx - lw / 2 - 25, 760, strokep(cv, 2, GOLD_DK))
    cv.drawLine(cx + lw / 2 + 25, 760, cx + lw / 2 + 90, 760, strokep(cv, 2, GOLD_DK))
    for j, line in enumerate(words):
        fs = 92
        fnt = skia.Font(TF_D, fs)
        w_ = fnt.measureText(line)
        b = skia.TextBlob.MakeFromString(line, fnt)
        cv.drawTextBlob(b, cx - w_ / 2 + 4, 878 + j * 100 + 5, fillp(cv, '#000000', .55, False))
        cv.drawTextBlob(b, cx - w_ / 2, 878 + j * 100, fillp(cv, BONE_HI, 1, False))
    R.dust(cv, 1.0, (0, 0, W, H), 40, 3, BONE_HI, .22)
    F.finish(surf, out)


# ================================================================ Kapitelkarte B: die Karteikarte
def f_chapter_card(out):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#171818', 1, False))
    scales_bg(cv, .04)
    F.head_at(cv, 1665, 250, 165, 'smug', look=(-0.6, 0.2), tilt=14)
    cv.save()
    cv.translate(960, 560)
    cv.rotate(-2.5)
    w, h = 1280, 720
    F.soft_shadow(cv, 24, h / 2 + 10, w * 1.02, 90, .55, 30)
    card = skia.Path()
    card.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 14, 14))
    cv.drawPath(card, fillp(cv, '#d8cfb6', 1))
    cv.save()
    cv.clipPath(card, doAntiAlias=True)
    cv.drawPath(M.minus(card, M.shifted(card, -8, -8)), fillp(cv, '#bfb59a', 1, False))
    for k in range(12):
        y = -h / 2 + 170 + k * 46
        cv.drawLine(-w / 2, y, w / 2, y, strokep(cv, 1.6, '#9db0c0', .55))
    cv.drawLine(-w / 2 + 150, -h / 2, -w / 2 + 150, h / 2, strokep(cv, 2.4, '#b4564a', .7))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, 120), fillp(cv, '#2b2c2b', 1, False))
    cv.restore()
    cv.drawPath(card, M.ink(cv, 3))
    P.draw_text(cv, 'CHAPTER I', -w / 2 + 60, -h / 2 + 78, TF_CAPS, 40, fillp(cv, GOLD, 1, False), spacing=10)
    P.draw_text(cv, 'SKINS 1 & 2  ·  1760s TO 1914', w / 2 - 60 - P.text_w(TF_CAPS, 24, 'SKINS 1 & 2  ·  1760s TO 1914', 6),
                -h / 2 + 72, TF_CAPS, 24, fillp(cv, BONE_SH, 1, False), spacing=6)
    for j, line in enumerate(('Haven’t we survived', 'this before?')):
        fnt = skia.Font(TF_D, 112)
        b = skia.TextBlob.MakeFromString(line, fnt)
        cv.drawTextBlob(b, -w / 2 + 200, -h / 2 + 330 + j * 140, fillp(cv, '#1f1a14', 1, False))
    text(cv, 'Exhibits: the weavers, the assembly line,', -w / 2 + 200, h / 2 - 105, TF_TYPE, 28, '#5b4a36')
    text(cv, 'the Five-Dollar Day.', -w / 2 + 200, h / 2 - 60, TF_TYPE, 28, '#5b4a36')
    cv.save()
    cv.translate(w / 2 - 175, h / 2 - 200)
    cv.rotate(-14)
    cv.scale(.85, .85)
    cv.drawCircle(0, 0, 118, strokep(cv, 10, GOLD_DK, .9))
    cv.drawCircle(0, 0, 96, strokep(cv, 3, GOLD_DK, .9))
    tf = skia.Font(TF_CAPS, 30)
    for k, ch in enumerate('ASSUMPTION 2 · TESTED · '):
        a = math.radians(-90 + k * 15)
        cv.save()
        cv.translate(math.cos(a) * 82, math.sin(a) * 82)
        cv.rotate(math.degrees(a) + 90)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, tf), -9, 10, fillp(cv, GOLD_DK, .9, False))
        cv.restore()
    cv.restore()
    cv.restore()
    F.finish(surf, out)


# ================================================================ Haeute als Ahnengalerie (H-01 bis H-03)
def straw_hat(cv, a):
    cv.save()
    cv.translate(0.04, -0.46)
    cv.rotate(-7)
    brim = skia.Path()
    brim.addOval(skia.Rect.MakeXYWH(-0.80, -0.07, 1.60, 0.22))
    crown = P_([(-0.34, 0.02), (-0.36, -0.30, 0.36, -0.30, 0.34, 0.02)])
    for p_ in (brim, crown):
        cv.drawPath(p_, fillp(cv, '#d8b86c', a))
        cv.save()
        cv.clipPath(p_, doAntiAlias=True)
        for k in range(-12, 13):
            cv.drawLine(k * .07, -.4, k * .07 + .1, .2, strokep(cv, .012, '#b8954d', .8 * a))
        M.shade_and_rim(cv, p_, '#b8954d', '#f0d68f', .04, a, .025)
        cv.restore()
        cv.drawPath(p_, M.ink(cv, M.LW, a))
    band = P_([(-0.345, -0.06), (0.345, -0.06), (0.34, 0.02), (-0.34, 0.02)])
    cv.drawPath(band, fillp(cv, '#7a3a2e', a))
    cv.drawPath(band, M.ink(cv, M.LW * .8, a))
    cv.restore()


def wig_tricorn(cv, a):
    cv.save()
    cv.translate(0.05, -0.44)
    cv.rotate(-6)
    crown = P_([(-0.30, -0.02), (-0.30, -0.36, 0.30, -0.36, 0.30, -0.02)])
    brim = P_([(-0.74, -0.10), (-0.40, 0.02, -0.20, 0.08, 0.0, 0.06), (0.20, 0.08, 0.40, 0.02, 0.74, -0.10),
               (0.52, 0.10, 0.20, 0.16, 0.0, 0.18), (-0.20, 0.16, -0.52, 0.10, -0.74, -0.10)])
    flap = P_([(-0.74, -0.10), (-0.55, -0.34, -0.20, -0.30, 0.0, -0.20), (0.20, -0.30, 0.55, -0.34, 0.74, -0.10),
               (0.40, -0.02, -0.40, -0.02, -0.74, -0.10)])
    for p_, c_ in ((crown, '#2a2726'), (flap, '#33302e'), (brim, '#2a2726')):
        cv.drawPath(p_, fillp(cv, c_, a))
        cv.save()
        cv.clipPath(p_, doAntiAlias=True)
        M.shade_and_rim(cv, p_, '#1c1a19', '#4a4542', .035, a, .022)
        cv.restore()
        cv.drawPath(p_, M.ink(cv, M.LW, a))
    edge = P_([(-0.70, -0.11), (-0.55, -0.31, -0.20, -0.27, 0.0, -0.18), (0.20, -0.27, 0.55, -0.31, 0.70, -0.11)], close=False)
    cv.drawPath(edge, strokep(cv, .028, GOLD, a))
    cv.drawCircle(0.0, -0.16, 0.045, fillp(cv, GOLD, a, False))
    cv.restore()


ERAS = [
    # Jahr, Thema, Hut, Medium, Hintergrund
    ('1760s', 'STEAM', wig_tricorn, 'oil', '#4a3a2c'),
    ('1913', 'ASSEMBLY LINE', M2.flatcap, 'sepia', '#5c5444'),
    ('1915', 'TRACTOR', straw_hat, 'sepia', '#6a5a3e'),
    ('1950s', 'AUTOMATION', M2.fedora, 'bw', '#55585a'),
    ('1980s', 'COMPUTER', M2.headphones, 'polaroid', '#3e5a6e'),
]


def medium(img, kind):
    x = img[..., :3].astype(np.float32) / 255
    L = (.3 * x[..., 0] + .59 * x[..., 1] + .11 * x[..., 2])[..., None]
    if kind == 'sepia':
        x = np.concatenate([L * 1.07 + .06, L * .92 + .03, L * .70], axis=-1)
    elif kind == 'bw':
        x = np.repeat(L * 1.05, 3, axis=-1)
    elif kind == 'polaroid':
        x = x * np.array([1.05, .98, .88]) + np.array([.05, .04, .03])
        x = L + (x - L) * .75
    elif kind == 'oil':
        x = x * np.array([1.0, .93, .78]) + np.array([.03, .015, 0])
        x = L + (x - L) * .8
    out = img.copy()
    out[..., :3] = (np.clip(x, 0, 1) * 255).astype(np.uint8)
    return out


def portrait(era, w, h):
    year, topic, hat, kind, bgc = era
    surf = skia.Surface(w, h)
    cv = surf.getCanvas()
    g = skia.Paint()
    g.setShader(skia.GradientShader.MakeRadial(skia.Point(w * .4, h * .35), max(w, h) * .9, [col(mix(bgc, '#ffffff', .25)), col(bgc), col(mix(bgc, '#000000', .5))], [0, .5, 1]))
    cv.drawPaint(g)
    s = w * .52
    cv.save()
    cv.translate(w / 2, h * .50)
    cv.scale(s, s)
    neck = M.tube([(0.0, 0.2), (0.0, 1.6)], [0.26, 0.29])
    cv.drawPath(neck, fillp(cv, M.SN, 1))
    cv.save()
    cv.clipPath(neck, doAntiAlias=True)
    cv.drawPath(M.minus(neck, M.shifted(neck, -0.05, 0)), fillp(cv, M.SN_SH, 1, False))
    cv.drawPath(M.tube([(0.04, 0.2), (0.04, 1.6)], [0.10, 0.115]), fillp(cv, M.SN_BELLY, 1, False))
    cv.restore()
    cv.drawPath(neck, M.ink(cv))
    if year in ('1950s',):
        M.draw_collar(cv)
    elif year == '1760s':
        cra = P_([(-0.22, 0.44), (0.22, 0.44), (0.12, 0.80), (0.0, 0.70), (-0.12, 0.80)])
        cv.drawPath(cra, fillp(cv, '#efe6d2', 1))
        cv.drawPath(cra, M.ink(cv, M.LW * .9))
    elif year in ('1913', '1915'):
        sc = P_([(-0.27, 0.42), (0.27, 0.42), (0.20, 0.62), (0.0, 0.56), (-0.20, 0.62)])
        cv.drawPath(sc, fillp(cv, '#7a3a2e' if year == '1913' else '#3e5a6e', 1))
        cv.drawPath(sc, M.ink(cv, M.LW * .9))
    expr = {'1760s': 'neutral', '1913': 'happy', '1915': 'neutral', '1950s': 'smug', '1980s': 'happy'}[year]
    M.draw_head(cv, expr, (0.15, 0.05), -4 + 2 * len(year), False, 1.0, reflect=0.0, talk=.35 if year == '1980s' else 0)
    hat(cv, 1.0)
    cv.restore()
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    img = medium(img, kind)
    rnd = np.random.default_rng(len(year))
    noise = rnd.normal(0, 7, img.shape[:2])[..., None]
    img[..., :3] = np.clip(img[..., :3].astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)


def frame_at(cv, x, y, w, h, img, oval=False, gold=False):
    pad = 26
    outer = skia.Path()
    if oval:
        outer.addOval(skia.Rect.MakeXYWH(x - pad, y - pad, w + 2 * pad, h + 2 * pad))
    else:
        outer.addRect(skia.Rect.MakeXYWH(x - pad, y - pad, w + 2 * pad, h + 2 * pad))
    M.ghost(cv, outer)
    fc, fsh, frim = (GOLD, GOLD_SH, GOLD_HI) if gold else ('#6a4c33', '#4a3423', '#8d6a4a')
    cv.drawPath(outer, fillp(cv, fc, 1))
    cv.save()
    cv.clipPath(outer, doAntiAlias=True)
    M.shade_and_rim(cv, outer, fsh, frim, 7, 1, 4)
    cv.restore()
    cv.drawPath(outer, M.ink(cv, 2.4))
    inner = skia.Path()
    if oval:
        inner.addOval(skia.Rect.MakeXYWH(x, y, w, h))
    else:
        inner.addRect(skia.Rect.MakeXYWH(x, y, w, h))
    cv.save()
    cv.clipPath(inner, doAntiAlias=True)
    if img is not None:
        cv.drawImage(img, x, y)
    else:
        cv.drawPaint(fillp(cv, '#1a1610', 1, False))
    cv.restore()
    cv.drawPath(inner, M.ink(cv, 2.4))
    sh = skia.Paint()
    sh.setShader(skia.GradientShader.MakeLinear([skia.Point(x, y), skia.Point(x, y + h * .35)], [col('#000000', .35), col('#000000', 0)]))
    cv.save()
    cv.clipPath(inner, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), sh)
    cv.restore()


def plaque(cv, cx, y, year, topic):
    w = max(P.text_w(TF_CAPS, 18, topic, 4), P.text_w(TF_HEAD, 26, year)) + 44
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w / 2, y, w, 70), 6, 6)
    cv.drawRRect(r, fillp(cv, GOLD_SH, 1))
    cv.drawRRect(r, M.ink(cv, 2))
    text(cv, year, cx, y + 30, TF_HEAD, 26, '#2a2017', anchor='c')
    text(cv, topic, cx, y + 56, TF_CAPS, 18, '#2a2017', anchor='c', spacing=4)


def lamp(cv, cx, y, w):
    F.spot(cv, cx, y + 10, w * .25, cx, y + 420, w * 1.3, .22, '#f6e4bf')
    bar = skia.Path()
    bar.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(cx - w * .32, y - 8, w * .64, 22), 10, 10))
    cv.drawPath(bar, fillp(cv, GOLD_SH, 1))
    cv.drawPath(bar, M.ink(cv, 2))
    cv.drawLine(cx, y - 8, cx, y - 34, strokep(cv, 6, GOLD_DK))


def wallpaper(cv):
    cv.drawPaint(fillp(cv, '#1d1e1d', 1, False))
    for gx in range(-60, W + 120, 120):
        for gy in range(-60, H + 120, 150):
            ox = 60 if (gy // 150) % 2 else 0
            p = skia.Path()
            x, y = gx + ox, gy
            p.moveTo(x, y - 40)
            p.cubicTo(x + 26, y - 20, x + 26, y + 20, x, y + 40)
            p.cubicTo(x - 26, y + 20, x - 26, y - 20, x, y - 40)
            cv.drawPath(p, strokep(cv, 2, '#252726', 1))
            cv.drawCircle(x, y, 5, fillp(cv, '#262827', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(0, 914, W, H), fillp(cv, '#2a2623', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(0, 898, W, 918), fillp(cv, '#3a332d', 1, False))
    cv.drawLine(0, 898, W, 898, M.ink(cv, 2.4))
    cv.drawLine(0, 918, W, 918, M.ink(cv, 2))
    for x in range(0, W, 160):
        cv.drawLine(x, 918, x, H, strokep(cv, 2, '#221f1c', 1))


def f_gallery(out):
    surf, cv = F.new_canvas()
    wallpaper(cv)
    layout = [  # x, y, w, h, oval
        (200, 125, 250, 300, True),
        (530, 150, 240, 275, False),
        (850, 145, 250, 280, False),
        (230, 575, 230, 230, True),
        (540, 575, 250, 230, False),
    ]
    gx, gy, gw, gh = 870, 575, 210, 230
    for era, (x, y, w, h, oval) in zip(ERAS[:3], layout[:3]):
        lamp(cv, x + w / 2, y - 60, w)
    F.spot(cv, 560, -60, 120, 560, 900, 1300, .10, '#f6e4bf')
    for era, (x, y, w, h, oval) in zip(ERAS, layout):
        frame_at(cv, x, y, w, h, portrait(era, w, h), oval)
        plaque(cv, x + w / 2, y + h + 34, era[0], era[1])
    frame_at(cv, gx, gy, gw, gh, None, False, gold=True)
    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), glowp(cv, GOLD_HI, 40, .25))
    text(cv, '?', gx + gw / 2, gy + gh / 2 + 34, TF_D, 110, GOLD, anchor='c')
    plaque(cv, gx + gw / 2, gy + gh + 34, 'TODAY', 'AI')
    F.soft_shadow(cv, 1470, 925, 560, 70, .6, 20)
    F.mascot_full(cv, 1470, 330, 170, 'neutral', look=(-0.8, -0.1), tilt=-6)
    F.lower_third(cv, 'EVERY FEW DECADES, A NEW SKIN', 'the old jobs stayed behind, the economy moved on')
    F.finish(surf, out)


FR = {'chapter_ring': f_chapter_ring, 'chapter_card': f_chapter_card, 'gallery': f_gallery}

if __name__ == '__main__':
    P.init_assets()
    R.init_layers()
    for name in sys.argv[1].split(','):
        FR[name](f'{sys.argv[2]}/{name}.png')
