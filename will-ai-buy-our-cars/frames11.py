#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Konzept "Das Lichtspielhaus der Schlange": Geschichte laeuft als alter Film,
die Zukunft leuchtet in der Kristallkugel, die Schlange schaut zu und kommentiert.

python3 frames11.py <name[,name...]> <outdir>    name: cinema intertitle countdown board modes
"""
import math, random, sys
import numpy as np
import skia
from PIL import Image
import rich as R
import mascot3 as M
import frames9 as F
import frames10 as T
import style5 as ST
from rich_base import *

TF_CAPS, TF_HEAD, TF_TITLE, TF_TYPE, TF_D = P.TF_CAPS, P.TF_HEAD, P.TF_TITLE, P.TF_TYPE, M.TF_DISPLAY
CREAM = '#e9e1c9'
VELVET, VELVET_DK, VELVET_HI = '#7a2a27', '#4c1817', '#a4473e'


# ---------------------------------------------------------------- Bilddaten
def load(path):
    return np.array(Image.open(path).convert('RGBA'))


def to_img(arr):
    if arr.shape[2] == 3:
        arr = np.concatenate([arr, np.full(arr.shape[:2] + (1,), 255, np.uint8)], axis=2)
    return skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.ColorType.kRGBA_8888_ColorType)


def snap(surf):
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def film_look(arr, tone='sepia', seed=0, scratches=6, dust=50, vign=.6, grain=.035):
    """Altes Filmmaterial: Sepia oder Schwarzweiss, Kratzer, Staub, Vignette, Korn."""
    rng = np.random.default_rng(seed)
    x = arr[..., :3].astype(np.float32) / 255
    h, w = x.shape[:2]
    L = .3 * x[..., 0] + .59 * x[..., 1] + .11 * x[..., 2]
    L = np.clip((L - .03) * 1.15, 0, 1)
    if tone == 'sepia':
        rgb = np.stack([L * 1.04 + .045, L * .91 + .028, L * .70 + .005], axis=-1)
    else:
        rgb = np.stack([L, L, L * .97], axis=-1)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx - w / 2) / (w * .62)) ** 2 + ((yy - h / 2) / (h * .62)) ** 2
    rgb *= np.clip(1 - vign * d, .15, 1)[..., None]
    for _ in range(scratches):
        x0 = rng.uniform(.05, .95) * w
        y0, y1 = sorted(rng.uniform(0, h, 2))
        if y1 - y0 < h * .3:
            y1 = min(h, y0 + h * .6)
        ys = np.arange(int(y0), int(y1))
        xs = (x0 + rng.uniform(0, 5) * np.sin(ys * rng.uniform(.004, .02) + rng.uniform(0, 6))).astype(int)
        b = rng.choice([.30, .22, -.20])
        for dx in range(int(rng.integers(1, 3))):
            cols = np.clip(xs + dx, 0, w - 1)
            rgb[ys, cols] = np.clip(rgb[ys, cols] + b, 0, 1)
    for _ in range(dust):
        cx, cy, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1.0, 4.5)
        x0, x1, y0, y1 = int(max(0, cx - r - 1)), int(min(w, cx + r + 2)), int(max(0, cy - r - 1)), int(min(h, cy + r + 2))
        m = ((xx[y0:y1, x0:x1] - cx) ** 2 + ((yy[y0:y1, x0:x1] - cy) * rng.uniform(.6, 1.6)) ** 2) < r * r
        rgb[y0:y1, x0:x1][m] = .05 if rng.random() < .7 else .92
    rgb += rng.normal(0, grain, (h, w, 1))
    out = np.empty((h, w, 4), np.uint8)
    out[..., :3] = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    out[..., 3] = 255
    return out


def fit_rect(cv, img, x, y, w, h):
    cv.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))


# ---------------------------------------------------------------- Kinobausteine
def velvet(cv, x0, x1, y0, y1, fold=56, sway=0.0, hem=True):
    """Samtvorhang als Streifenfalten mit welliger Unterkante und Goldfransen."""
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    n = max(2, int((x1 - x0) / fold))
    p.lineTo(x1, y1)
    for k in range(n, -1, -1):
        xx = x0 + (x1 - x0) * k / n
        p.lineTo(xx, y1 + (14 if k % 2 else 0))
    p.close()
    sh = skia.Paint(AntiAlias=True)
    sh.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x0 + fold, 0)],
                                                [col(VELVET_DK), col(VELVET), col(VELVET_HI), col(VELVET), col(VELVET_DK)],
                                                None, skia.TileMode.kRepeat))
    cv.drawPath(p, sh)
    cv.drawPath(p, M.ink(cv, 2.4))
    if hem:
        for k in range(n + 1):
            xx = x0 + (x1 - x0) * k / n
            yb = y1 + (14 if k % 2 else 0)
            cv.drawLine(xx, yb, xx, yb + 18, strokep(cv, 3, GOLD))
        cv.drawLine(x0, y1 + 2, x1, y1 + 2, strokep(cv, 5, GOLD_SH))


def valance(cv, x0, x1, y0, h, skip_mid=None):
    p = skia.Path()
    p.moveTo(x0, y0)
    p.lineTo(x1, y0)
    n = int((x1 - x0) / 120)
    p.lineTo(x1, y0 + h * .6)
    for k in range(n, 0, -1):
        xa = x0 + (x1 - x0) * k / n
        xb = x0 + (x1 - x0) * (k - 1) / n
        p.quadTo((xa + xb) / 2, y0 + h * 1.25, xb, y0 + h * .6)
    p.close()
    cv.drawPath(p, fillp(cv, VELVET, 1))
    cv.save()
    cv.clipPath(p, doAntiAlias=True)
    cv.drawPath(M.minus(p, M.shifted(p, 0, -10)), fillp(cv, VELVET_DK, 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y0 + 16), fillp(cv, VELVET_HI, .6, False))
    cv.restore()
    cv.drawPath(p, M.ink(cv, 2.4))
    for k in range(n):
        xm = x0 + (x1 - x0) * (k + .5) / n
        if skip_mid and skip_mid[0] < xm < skip_mid[1]:
            continue
        cv.drawLine(xm, y0 + h * 1.12, xm, y0 + h * 1.12 + 30, strokep(cv, 4, GOLD_SH))
        cv.drawCircle(xm, y0 + h * 1.12 + 36, 9, fillp(cv, GOLD, 1))
        cv.drawCircle(xm, y0 + h * 1.12 + 36, 9, M.ink(cv, 2))


def sconce(cv, x, y, s=1.0):
    cv.drawCircle(x, y - 30 * s, 120 * s, glowp(cv, '#f6d79a', 60, .25))
    fan = skia.Path()
    fan.moveTo(x, y)
    fan.arcTo(skia.Rect.MakeXYWH(x - 60 * s, y - 70 * s, 120 * s, 140 * s), 200, 140, False)
    fan.close()
    cv.drawPath(fan, fillp(cv, '#f2d9a2', 1))
    for k in range(5):
        a = math.radians(200 + 28 * k + 14)
        cv.drawLine(x, y, x + math.cos(a) * 58 * s, y + math.sin(a) * 68 * s, strokep(cv, 2, GOLD_SH))
    cv.drawPath(fan, M.ink(cv, 2.2))
    base = skia.Path()
    base.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 16 * s, y - 4, 32 * s, 40 * s), 6, 6))
    cv.drawPath(base, fillp(cv, GOLD_SH, 1))
    cv.drawPath(base, M.ink(cv, 2))


def seat(cv, x, y, w, h, lit=1.0):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y, w, h * 1.6), w * .28, w * .28))
    cv.drawPath(p, fillp(cv, '#5b2422', 1))
    cv.save()
    cv.clipPath(p, doAntiAlias=True)
    cv.drawPath(M.minus(p, M.shifted(p, -w * .12, 0)), fillp(cv, '#3f1718', 1, False))
    cv.drawPath(M.minus(p, M.shifted(p, 0, h * .09)), fillp(cv, mix('#a4574a', '#e0b27a', .3), .85 * lit, False))
    cv.drawLine(x - w * .34, y + h * .55, x + w * .34, y + h * .55, strokep(cv, max(1.2, w * .02), '#3f1718', .9))
    cv.restore()
    cv.drawPath(p, M.ink(cv, 2.2))


ROWS = [(645, 92, 78, 104), (715, 122, 102, 136), (805, 162, 136, 178), (925, 214, 180, 236)]


def seat_row(cv, r, skip=()):
    y, w, h, sp = ROWS[r]
    n = int(W / sp) + 3
    off = (sp / 2) if r % 2 else 0
    xs = [960 + off + (k - n // 2) * sp for k in range(n)]
    for x in xs:
        if any(abs(x - s) < sp * .5 for s in skip):
            continue
        seat(cv, x, y, w, h, lit=1 - r * .18)
    return xs


def beam(cv, sx0, sy0, sx1, sy1, t=0.0):
    rnd = random.Random(2)
    for k in range(7):
        u0 = rnd.uniform(.0, 1.0)
        ax = lerp(sx0, sx1, u0)
        ray = poly([(lerp(-200, W + 200, u0) - 140, -40), (lerp(-200, W + 200, u0) + 140, -40),
                    (ax + 40, lerp(sy0, sy1, .5)), (ax - 40, lerp(sy0, sy1, .5))])
        p = skia.Paint(AntiAlias=True, Color=col('#f6e4bf', .035))
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
        cv.drawPath(ray, p)
    whole = poly([(-260, -40), (W + 260, -40), (sx1, sy1), (sx0, sy1)])
    p = skia.Paint(AntiAlias=True, Color=col('#f6e4bf', .05))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 50))
    cv.drawPath(whole, p)
    R.dust(cv, t, (200, 0, W - 200, 600), 70, 4, '#f6e4bf', .45)


def popcorn(cv, x, y, s=1.0):
    b = poly([(x - 36 * s, y), (x + 36 * s, y), (x + 26 * s, y + 80 * s), (x - 26 * s, y + 80 * s)])
    cv.save()
    rnd = random.Random(4)
    for k in range(11):
        cv.drawCircle(x + rnd.uniform(-34, 34) * s, y - rnd.uniform(-4, 20) * s, rnd.uniform(11, 15) * s, fillp(cv, '#f4e7c3', 1))
        cv.drawCircle(x + rnd.uniform(-34, 34) * s, y - rnd.uniform(-4, 20) * s, rnd.uniform(11, 15) * s, M.ink(cv, 1.6))
    cv.drawPath(b, fillp(cv, '#efe6d2', 1))
    cv.save()
    cv.clipPath(b, doAntiAlias=True)
    for k in range(-3, 4):
        cv.drawRect(skia.Rect.MakeXYWH(x + k * 22 * s - 6 * s, y, 11 * s, 90 * s), fillp(cv, M.TIE, 1, False))
    cv.restore()
    cv.drawPath(b, M.ink(cv, 2))
    cv.restore()


def proscenium(cv, sx, sy, sw, sh, screen_img):
    cv.drawRect(skia.Rect.MakeXYWH(sx - 150, sy - 110, sw + 300, sh + 210), fillp(cv, '#140f0e', 1, False))
    for k, (pad, c) in enumerate(((128, GOLD_SH), (112, '#2a1d17'), (92, GOLD_DK))):
        cv.drawRect(skia.Rect.MakeXYWH(sx - pad, sy - pad * .75, sw + 2 * pad, sh + pad * 1.6), strokep(cv, 8 if k != 1 else 14, c))
    for sx_ in (-1, 1):
        for k in range(4):
            x = sx + sw / 2 + sx_ * (sw / 2 + 128 - k * 22)
            cv.drawLine(x, sy - 96 + k * 14, x, sy - 70 + k * 14, strokep(cv, 6, GOLD))
    cv.drawRect(skia.Rect.MakeXYWH(sx - 6, sy - 6, sw + 12, sh + 12), fillp(cv, '#0a0908', 1, False))
    fit_rect(cv, screen_img, sx, sy, sw, sh)
    cv.drawRect(skia.Rect.MakeXYWH(sx - 30, sy - 30, sw + 60, sh + 60), glowp(cv, '#f6e4bf', 40, .12))


# ================================================================ A  Das Lichtspielhaus (Schlüsselbild)
def f_cinema(out, screen='frames9/horses.png', tone='sepia'):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#1b1312', 1, False))
    wall = skia.Paint()
    wall.setShader(skia.GradientShader.MakeRadial(skia.Point(960, 330), 1100, [col('#3a2620'), col('#160f0e')]))
    cv.drawRect(skia.Rect.MakeWH(W, 760), wall)
    for x in range(-40, W + 60, 96):
        cv.drawLine(x, 0, x, 700, strokep(cv, 2, '#231816', 1))
    sx, sy, sw, sh = 560, 120, 800, 450
    film = to_img(film_look(load(screen), tone, seed=3))
    proscenium(cv, sx, sy, sw, sh, film)
    velvet(cv, sx - 230, sx + 20, sy - 70, sy + sh + 90, 52)
    velvet(cv, sx + sw - 20, sx + sw + 230, sy - 70, sy + sh + 90, 52)
    valance(cv, sx - 240, sx + sw + 240, sy - 100, 70, skip_mid=(sx + 20, sx + sw - 20))
    sconce(cv, 180, 360)
    sconce(cv, W - 180, 360)
    cv.drawRect(skia.Rect.MakeLTRB(0, 690, W, H), fillp(cv, '#120d0c', 1, False))
    beam(cv, sx, sy, sx + sw, sy + sh, 1.0)
    snake_x = 1090
    seat_row(cv, 0)
    seat_row(cv, 1)
    y2, w2, h2, sp2 = ROWS[2]
    neck = M.tube([(snake_x, y2 + 60), (snake_x - 4, y2 - 40)], [54, 48])
    cv.drawPath(neck, fillp(cv, M.SN, 1))
    cv.drawPath(neck, M.ink(cv))
    xs = seat_row(cv, 2)
    ball_seat = min(xs, key=lambda v: abs(v - (snake_x + sp2)))
    ST.ball_at(cv, ball_seat, y2 - 38, 78, 2.0)
    popcorn(cv, snake_x - sp2 * .62, y2 - 24, 1.0)
    F.head_at(cv, snake_x - 6, y2 - 118, 178, 'smug', look=(-0.15, 0.25), tilt=-8)
    seat_row(cv, 3)
    vg = skia.Paint()
    vg.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 900), skia.Point(0, H)], [col('#000000', 0), col('#000000', .6)]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), vg)
    F.finish(surf, out)


# ================================================================ B  Kapitelkarte als Stummfilm-Zwischentitel
def deco_corner(cv, x, y, sx, sy, c=CREAM):
    cv.save()
    cv.translate(x, y)
    cv.scale(sx, sy)
    for k, r in enumerate((60, 42, 24)):
        a = skia.Path()
        a.addArc(skia.Rect.MakeXYWH(-r, -r, 2 * r, 2 * r), 0, 90)
        cv.drawPath(a, strokep(cv, 3 if k == 0 else 2, c, .9))
    cv.drawLine(0, 0, 110, 0, strokep(cv, 3, c, .9))
    cv.drawLine(0, 0, 0, 110, strokep(cv, 3, c, .9))
    cv.drawCircle(0, 0, 7, fillp(cv, c, 1, False))
    cv.restore()


def intertitle(cv, chapter='CHAPTER ONE', roman='I', lines=('Haven’t we survived', 'this before?'), ring=True):
    cv.drawPaint(fillp(cv, '#0e0d0c', 1, False))
    x0, y0, x1, y1 = 150, 95, W - 150, H - 95
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(cv, 4, CREAM, .9))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 18, y0 + 18, x1 - 18, y1 - 18), strokep(cv, 2, CREAM, .7))
    for (x, y, sx, sy) in ((x0 + 18, y0 + 18, 1, 1), (x1 - 18, y0 + 18, -1, 1), (x0 + 18, y1 - 18, 1, -1), (x1 - 18, y1 - 18, -1, -1)):
        deco_corner(cv, x, y, sx, sy)
    for k in range(9):
        xx = 960 + (k - 4) * 28
        cv.drawLine(xx, y0 + 18, xx, y0 + 40 - abs(k - 4) * 4, strokep(cv, 2, CREAM, .7))
        cv.drawLine(xx, y1 - 18, xx, y1 - 40 + abs(k - 4) * 4, strokep(cv, 2, CREAM, .7))
    if ring:
        cv.drawCircle(960, 300, 58, fillp(cv, '#0e0d0c', 1, False))
        text(cv, roman, 960, 326, TF_TITLE, 66, GOLD, anchor='c')
        T.ring(cv, 960, 300, 92, 20, 'smug', look=(0.1, 0.2), tilt=-6)
    lw = P.text_w(TF_CAPS, 32, chapter, 14)
    P.draw_text(cv, chapter, 960 - lw / 2, 520, TF_CAPS, 32, fillp(cv, CREAM, 1, False), spacing=14)
    for sx_ in (-1, 1):
        cv.drawLine(960 + sx_ * (lw / 2 + 30), 508, 960 + sx_ * (lw / 2 + 140), 508, strokep(cv, 2, CREAM, .8))
        dm = poly([(960 + sx_ * (lw / 2 + 150), 508), (960 + sx_ * (lw / 2 + 160), 500), (960 + sx_ * (lw / 2 + 170), 508),
                   (960 + sx_ * (lw / 2 + 160), 516)])
        cv.drawPath(dm, fillp(cv, CREAM, .9, False))
    for j, ln in enumerate(lines):
        f = skia.Font(TF_D, 104)
        w_ = f.measureText(ln)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ln, f), 960 - w_ / 2, 680 + j * 125, fillp(cv, CREAM, 1, False))


def f_intertitle(out):
    surf, cv = F.new_canvas()
    intertitle(cv)
    arr = film_look(snap(surf), 'sepia', seed=11, scratches=7, dust=70, vign=.45)
    Image.fromarray(arr[..., :3]).save(out)
    print('saved', out)


# ================================================================ C  Startband vor jedem Geschichtskapitel
def leader(cv, num=3, sweep=.62, label='REEL I  ·  1760s  ·  STEAM'):
    cv.drawPaint(fillp(cv, '#8a857a', 1, False))
    cx, cy = 960, 520
    sec = skia.Path()
    sec.moveTo(cx, cy)
    sec.arcTo(skia.Rect.MakeXYWH(cx - 1200, cy - 1200, 2400, 2400), -90, 360 * sweep, False)
    sec.close()
    cv.drawPath(sec, fillp(cv, '#5d594f', 1, False))
    cv.drawLine(0, cy, W, cy, strokep(cv, 4, '#1a1916'))
    cv.drawLine(cx, 0, cx, H, strokep(cv, 4, '#1a1916'))
    for r, wv in ((330, 10), (290, 5)):
        cv.drawCircle(cx, cy, r, strokep(cv, wv, '#efe9da'))
    cv.drawCircle(cx, cy, 270, fillp(cv, '#8a857a', 1, False))
    cv.save()
    cv.clipPath(circle(cx, cy, 270), doAntiAlias=True)
    cv.drawPath(sec, fillp(cv, '#5d594f', 1, False))
    cv.restore()
    f = skia.Font(TF_HEAD, 420)
    s = str(num)
    w_ = f.measureText(s)
    cv.drawTextBlob(skia.TextBlob.MakeFromString(s, f), cx - w_ / 2, cy + 150, fillp(cv, '#14130f', 1, False))
    lw = P.text_w(TF_CAPS, 30, label, 8)
    P.draw_text(cv, label, cx - lw / 2, 1000, TF_CAPS, 30, fillp(cv, '#1a1916', 1, False), spacing=8)
    for k in range(4):
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(40, 80 + k * 260, 46, 70), 8, 8), fillp(cv, '#1a1916', 1, False))
        cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W - 86, 80 + k * 260, 46, 70), 8, 8), fillp(cv, '#1a1916', 1, False))


def f_countdown(out):
    surf, cv = F.new_canvas()
    leader(cv)
    arr = film_look(snap(surf), 'bw', seed=5, scratches=8, dust=80, vign=.5)
    Image.fromarray(arr[..., :3]).save(out)
    print('saved', out)


# ================================================================ D  Tafel: Kinouebergaenge
def scene_eden():
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    P.G.zoom = 1.0
    cv.drawImage(P.BG_NIGHT, 0, 0)
    R.draw_layer(cv, 'far', 0)
    P.draw_eden_bot(cv, 1000, 1040, 860, 170, 0, face=1.0, glow=1.0)
    R.draw_layer(cv, 'mid_g', 0)
    R.draw_layer(cv, 'near_g', 0)
    return snap(surf)


def p_iris():
    base = load('frames10/gallery.png').astype(np.float32)
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - 1470) ** 2 + (yy - 400) ** 2)
    m = np.clip((420 - d) / 3, 0, 1)[..., None]
    base[..., :3] *= m
    return film_look(base.astype(np.uint8), 'sepia', seed=2, scratches=3, dust=20, vign=.2)


def p_curtain():
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#140f0e', 1, False))
    film = to_img(film_look(load('frames9/reuther.png'), 'bw', seed=8))
    proscenium(cv, 420, 150, 1080, 608, film)
    velvet(cv, 0, 760, 30, 1000, 60)
    velvet(cv, 1160, W, 30, 1000, 60)
    valance(cv, -20, W + 20, 0, 90)
    return snap(surf)


def p_strip():
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#0e0d0c', 1, False))
    cv.drawRect(skia.Rect.MakeLTRB(300, -20, 1620, H + 20), fillp(cv, '#1a1714', 1, False))
    a = to_img(film_look(load('frames9/horses.png'), 'sepia', seed=1))
    b = to_img(film_look(load('frames9/reuther.png'), 'sepia', seed=4))
    fw, fh = 1120, 630
    y_line = 400
    fit_rect(cv, a, 400, y_line - fh, fw, fh)
    cv.drawRect(skia.Rect.MakeLTRB(400, y_line, 400 + fw, y_line + 34), fillp(cv, '#0b0a09', 1, False))
    fit_rect(cv, b, 400, y_line + 34, fw, fh)
    for x in (330, 1560):
        for k in range(-2, 14):
            rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y_line - 300 + k * 92, 34, 52), 7, 7)
            cv.drawRRect(rr, fillp(cv, '#cfc3a2', .85, False))
    f = skia.Font(TF_HEAD, 24)
    cv.save()
    cv.translate(388, 900)
    cv.rotate(-90)
    cv.drawTextBlob(skia.TextBlob.MakeFromString('SAFETY FILM  ▸ 1913  ▸  REEL II', f), 0, 0, fillp(cv, '#d18a3e', .85, False))
    cv.restore()
    return snap(surf)


def p_burn():
    A = film_look(load('frames9/horses.png'), 'sepia', seed=6).astype(np.float32)
    B = scene_eden().astype(np.float32)
    h, w = A.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = xx - 980, yy - 520
    rho = np.sqrt(dx * dx + dy * dy)
    th = np.arctan2(dy, dx)
    rr = 360 * (1 + .16 * np.sin(3 * th + 1) + .09 * np.sin(7 * th + 2) + .05 * np.sin(13 * th))
    dist = rho - rr
    out = A.copy()
    inside = dist < 0
    out[inside] = B[inside]
    hot = np.clip(1 - np.abs(dist) / 16, 0, 1)
    char = np.clip(1 - (dist - 10) / 55, 0, 1) * (dist > 0)
    out[..., :3] = out[..., :3] * (1 - .75 * char[..., None]) + np.array([40, 22, 10]) * .75 * char[..., None]
    glow = np.array([255, 196, 110])
    out[..., :3] = out[..., :3] * (1 - hot[..., None]) + glow * hot[..., None]
    white = np.clip(1 - np.abs(dist + 4) / 5, 0, 1)
    out[..., :3] = out[..., :3] * (1 - white[..., None]) + 255 * white[..., None]
    return np.clip(out, 0, 255).astype(np.uint8)


def p_reverse():
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#0c0a09', 1, False))
    film = to_img(film_look(load('frames9/horses.png'), 'sepia', seed=9))
    fit_rect(cv, film, 120, 40, 1680, 945)
    cv.drawRect(skia.Rect.MakeXYWH(120, 40, 1680, 945), glowp(cv, '#f6e4bf', 50, .1))
    for k in range(9):
        x = -40 + k * 250
        p = skia.Path()
        p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 900, 220, 300), 70, 70))
        cv.drawPath(p, fillp(cv, '#0a0807', 1, False))
        cv.drawPath(M.minus(p, M.shifted(p, 0, 6)), fillp(cv, '#4a3a2c', .8, False))
    cv.save()
    cv.translate(1120, 820)
    cv.scale(210, 210)
    hp = P_(M.HEAD3)
    neck = M.tube([(0.0, 0.3), (0.0, 1.6)], [0.27, 0.30])
    sil = union([hp, neck])
    cv.drawPath(sil, fillp(cv, '#0a0807', 1, False))
    cv.drawPath(M.minus(sil, M.shifted(sil, 0, 0.03)), fillp(cv, '#6a5640', .9, False))
    for sx in (-1, 1):
        cv.drawPath(P_([(sx * 0.66, -0.20), (sx * 0.74, -0.18)], close=False), strokep(cv, 0.03, '#b29a70', .9))
    cv.restore()
    popcorn(cv, 1370, 860, 1.3)
    cv.drawRect(skia.Rect.MakeXYWH(1310, 830, 130, 200), fillp(cv, '#000000', .55, False))
    return snap(surf)


def p_slip():
    base = load('frames9/ring.png')
    h, w = base.shape[:2]
    off = 380
    out = np.zeros_like(base)
    out[off + 30:] = base[:h - off - 30]
    out[:off] = base[h - off:]
    out[off:off + 30, :, :3] = 8
    out[..., 3] = 255
    rng = np.random.default_rng(3)
    out[..., :3] = np.clip(out[..., :3].astype(np.int16) + 45, 0, 255).astype(np.uint8)
    arr = film_look(out, 'sepia', seed=12, scratches=10, dust=60, vign=.4)
    surf = skia.Surface(W, H)
    cv = surf.getCanvas()
    cv.drawImage(to_img(arr), 0, 0)
    cv.drawRect(skia.Rect.MakeWH(W, H), fillp(cv, '#fff6dc', .18, False))
    return snap(surf)


def board_panel(cv, x, y, w, h, arr, title, sub):
    img = to_img(arr)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 12, 12)
    cv.save()
    cv.clipRRect(r, doAntiAlias=True)
    fit_rect(cv, img, x, y, w, h)
    cv.restore()
    cv.drawRRect(r, strokep(cv, 3, '#3a3c3b'))
    text(cv, title, x, y + h + 38, TF_HEAD, 28, BONE_HI)
    text(cv, sub, x, y + h + 70, TF_HEAD, 21, BONE_SH)


def f_board(out):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    P.draw_text(cv, 'ÜBERGÄNGE WIE IM ALTEN KINO', 80, 82, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    items = [
        (p_iris(), 'Iris-Blende', 'Stummfilm-Kreis um ein Detail, dann die nächste Szene'),
        (p_curtain(), 'Vorhang auf', 'Samtvorhang öffnet jedes Geschichtskapitel'),
        (p_strip(), 'Filmstreifen', 'das Bild rutscht im Projektor ins nächste'),
        (p_burn(), 'Film brennt durch', 'Vergangenheit brennt weg, dahinter die goldene Zukunft'),
        (p_reverse(), 'Gegenschuss ins Kino', 'von der Leinwand zurück zur Schlange im Saal'),
        (p_slip(), 'Bildstand verrutscht', 'Pointe in 08-04b: der Projektor macht, was er will'),
    ]
    pw, ph = 560, 315
    for k, (arr, t1, t2) in enumerate(items):
        x = 80 + (k % 3) * (pw + 40)
        y = 130 + (k // 3) * (ph + 140)
        board_panel(cv, x, y, pw, ph, arr, t1, t2)
    F.finish(surf, out)


# ================================================================ E  Tafel: wo die Erzaehlerin auftaucht
def p_peek():
    surf, cv = F.new_canvas()
    cv.drawImage(to_img(load('frames9/reuther.png')), 0, 0)
    F.head_at(cv, 1830, 770, 190, 'smug', look=(-0.8, 0.0), tilt=-24)
    return snap(surf)


def f_modes(out):
    surf, cv = F.new_canvas()
    cv.drawPaint(fillp(cv, '#141515', 1, False))
    P.draw_text(cv, 'WO DIE ERZÄHLERIN AUFTAUCHT', 80, 82, TF_CAPS, 30, fillp(cv, GOLD, 1, False), spacing=7)
    items = [
        (load('frames11/cinema.png'), 'Im Kino', 'zwischen den Kapiteln: schaut zu, kommentiert, dreht sich zu uns um'),
        (load('frames10/gallery.png'), 'In der Szene', 'wenn sie Teil der Geschichte ist: Häute, Ring, These'),
        (load('frames9/curve.png'), 'Als Diagramm', 'ihr Körper ist die Kurve: Pferde, Arbeitslosigkeit, Lohnquote'),
        (p_peek(), 'Am Bildrand', 'in historischen Szenen nur ein kurzer Blick von der Seite'),
    ]
    pw, ph = 680, 382
    for k, (arr, t1, t2) in enumerate(items):
        x = 250 + (k % 2) * (pw + 60)
        y = 120 + (k // 2) * (ph + 100)
        board_panel(cv, x, y, pw, ph, arr, t1, t2)
    F.finish(surf, out)


FR = {'cinema': f_cinema, 'intertitle': f_intertitle, 'countdown': f_countdown, 'board': f_board, 'modes': f_modes}

if __name__ == '__main__':
    P.init_assets()
    R.init_layers()
    for name in sys.argv[1].split(','):
        FR[name](f'{sys.argv[2]}/{name}.png')
