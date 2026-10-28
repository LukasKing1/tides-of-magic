#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Stilbilder fuer den neuen, flachen und warmen Look mit der neuen Schlange.

python3 style5.py scene <out.png>   Kristallkugel mit Schlange
python3 style5.py title <out.png>   Titelkarte
"""
import math, random, sys
import skia
import rich as R
import mascot3 as M
from rich_base import *

WOOD = '#4d362a'
WOOD_RIM = '#6a4c3b'
WOOD_SH = '#3a281f'
RED2 = '#a84a3a'
RED2_DK = '#7f3529'


def beams(cv, a=.035):
    for k in range(5):
        x = 520 + k * 380
        cv.drawPath(poly([(x, -40), (x + 170, -40), (x - 330, H + 40), (x - 500, H + 40)]), fillp(cv, '#f6e4bf', a, False))


def vignette(cv, s=.6):
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(W / 2, H / 2), 1150, [col('#000000', 0), col('#000000', s)]))
    cv.drawPaint(vg)


def ball_at(cv, x, y, r, t):
    cv.save()
    k = r / R.BR
    cv.translate(x, y)
    cv.scale(k, k)
    cv.translate(-R.BX, -R.BY)
    P.G.zoom = mscale(cv)
    cv.drawCircle(R.BX, R.BY, R.BR * 1.5, glowp(cv, GOLD_HI, 120, .25))
    R.crystal_ball(cv, t)
    cv.restore()


def stand(cv, x, y, r):
    """Kleiner Holzsockel unter der Kugel."""
    cv.save()
    cv.translate(x, y)
    cv.scale(r, r)
    top = skia.Path()
    top.addOval(skia.Rect.MakeXYWH(-0.62, -0.10, 1.24, 0.22))
    neck = poly([(-0.42, 0.02), (0.42, 0.02), (0.30, 0.34), (-0.30, 0.34)])
    foot = skia.Path()
    foot.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-0.52, 0.30, 1.04, 0.16), 0.06, 0.06))
    for p_ in (foot, neck, top):
        M.ghost(cv, p_)
        cv.drawPath(p_, fillp(cv, WOOD, 1))
        cv.save()
        cv.clipPath(p_, doAntiAlias=True)
        M.shade_and_rim(cv, p_, WOOD_SH, WOOD_RIM, 0.05, 1, 0.03)
        cv.restore()
        cv.drawPath(p_, M.ink(cv))
    cv.restore()


def scene(out):
    from PIL import Image
    P.init_assets()
    R.init_layers()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawPaint(fillp(cv, '#2a1e1b', 1, False))
    wall = skia.Paint()
    wall.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 820)], [col('#3a2723'), col('#24191a')]))
    cv.drawRect(skia.Rect.MakeWH(W, 820), wall)
    for x in range(-60, W + 60, 240):
        cv.drawRect(skia.Rect.MakeXYWH(x, 0, 16, 820), fillp(cv, '#2d1f1d', 1, False))
    beams(cv)
    cv.drawRect(skia.Rect.MakeLTRB(0, 820, W, H), fillp(cv, '#1d1514', 1, False))
    cv.drawLine(0, 820, W, 820, M.ink(cv, 2.6))
    for k in range(6):
        cv.drawLine(0, 840 + k * k * 11, W, 840 + k * k * 11, strokep(cv, 2, '#261b19', 1))
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .5))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22))
    cv.drawOval(skia.Rect.MakeXYWH(470, 850, 460, 70), sh)
    cv.drawOval(skia.Rect.MakeXYWH(1060, 900, 640, 90), sh)
    stand(cv, 700, 735, 210)
    ball_at(cv, 700, 520, 225, 3.0)
    M.draw_mascot(cv, 1420, 330, 190, 'smug', look=(-0.6, 0.1), tilt=-7, reflect=.9)
    R.dust(cv, 2.0, (300, 150, 1600, 800), 40, 7, '#f6e4bf', .35)
    vignette(cv)
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    Image.fromarray(P.Post().apply(img, 0)).save(out)
    print('saved', out)


def extruded(cv, s, x, y, size, c, depth=14, a=1.0):
    f = skia.Font(M.TF_DISPLAY, size)
    blob = skia.TextBlob.MakeFromString(s, f)
    for k in range(depth, 0, -1):
        cv.drawTextBlob(blob, x + k * .9, y + k, fillp(cv, '#0e0a09', a, False))
    cv.drawTextBlob(blob, x + 3, y + 3, fillp(cv, mix(c, '#000000', .45), a, False))
    cv.drawTextBlob(blob, x, y, fillp(cv, c, a, False))
    return f.measureText(s)


def deco_circle(cv, x, y, r, c, rings=2):
    cv.drawCircle(x, y, r, fillp(cv, c, 1, False))
    for k in range(1, rings + 1):
        cv.drawCircle(x, y, r * (1 - k * .28), fillp(cv, mix(c, '#000000', .18 * k), 1, False))


def title(out):
    from PIL import Image
    P.init_assets()
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawPaint(fillp(cv, '#252120', 1, False))
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.rotate(-7)
    cv.translate(-W / 2, -H / 2)
    for k in range(-3, 14):
        cv.drawRect(skia.Rect.MakeXYWH(-300 + k * 190, -300, 120, H + 600), fillp(cv, '#2b2625', 1, False))
    panel = skia.Path()
    panel.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(250, 230, 1420, 620), 10, 10))
    cv.drawPath(panel, fillp(cv, '#141010', 1))
    cv.drawPath(panel, strokep(cv, 10, '#1b1615'))
    rnd = random.Random(4)
    for (x, y, n) in ((330, 205, 6), (720, 200, 3), (1150, 205, 16), (1500, 880, 6), (860, 885, 5), (400, 885, 3)):
        for k in range(n):
            cv.drawCircle(x + k * 30, y, 9, fillp(cv, '#8f8f82' if n > 5 else RED2, 1, False))
    for (x, y, w) in ((420, 150, 330), (1210, 950, 260)):
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, 26), 13, 13)
        cv.drawRRect(rr, fillp(cv, '#a3a493', 1))
    for (x, y, h) in ((175, 160, 220), (225, 200, 200), (1735, 420, 230), (1785, 460, 190)):
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, 24, h), 12, 12)
        cv.drawRRect(rr, fillp(cv, '#a3a493', 1))
    deco_circle(cv, 160, 300, 130, RED2)
    deco_circle(cv, 1720, 160, 80, GOLD)
    deco_circle(cv, 1730, 830, 120, RED2)
    deco_circle(cv, 140, 760, 70, RED2_DK, 1)
    cv.drawLine(1730, 710, 1730, 950, M.ink(cv, 3))
    cv.drawLine(1610, 830, 1850, 830, M.ink(cv, 3))
    cv.drawCircle(1730, 830, 10, fillp(cv, M.LINE, 1, False))
    for (x0, y0, x1, y1) in ((1650, 130, 1900, 40), (1780, 120, 1880, 240), (1690, 70, 1760, 150)):
        cv.drawLine(x0, y0, x1, y1, strokep(cv, 5, RED2))
    w1 = extruded(cv, 'WILL AI BUY', 470, 470, 150, BONE_HI, 12)
    f = skia.Font(M.TF_DISPLAY, 150)
    ai_x = 470 + f.measureText('WILL ')
    blob = skia.TextBlob.MakeFromString('AI', f)
    g = skia.Paint(AntiAlias=True, Color=col(GOLD_HI, .45))
    g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
    cv.drawTextBlob(blob, ai_x, 470, g)
    cv.drawTextBlob(blob, ai_x, 470, fillp(cv, GOLD, 1, False))
    extruded(cv, 'OUR CARS?', 330, 740, 250, RED2, 16)
    cv.restore()
    cv.save()
    cv.translate(1560, 990)
    cv.scale(150, 150)
    neck = M.tube([(0.0, 0.2), (0.0, 1.6)], [0.26, 0.29])
    cv.drawPath(neck, fillp(cv, M.SN, 1))
    cv.drawPath(neck, M.ink(cv))
    M.draw_collar(cv)
    M.draw_head(cv, 'smug', look=(-0.4, -0.1), tilt=-10)
    cv.restore()
    vignette(cv, .45)
    img = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
    Image.fromarray(P.Post().apply(img, 0)).save(out)
    print('saved', out)


if __name__ == '__main__':
    {'scene': scene, 'title': title}[sys.argv[1]](sys.argv[2])
