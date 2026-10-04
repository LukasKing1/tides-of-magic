"""Bildsprache 'Papiertheater im Buch des Sternsehers':
Radierung in Sepia, Flechtwerk-Rahmen, Schnörkelwolken, Papierbänder, Kompass-Sterne,
punzierte Goldnimben, Runenkreise. Alles in Design-Koordinaten (1920x1080)."""
import math, sys
import numpy as np
import cv2
import skia
sys.path.insert(0, '/home/claude/main/ch1')
from lib import *

SEPIA_INK = (58, 40, 26)
SEPIA_MID = (150, 112, 70)
SEPIA_PAPER = (232, 214, 176)
WOOD = (112, 78, 48)
WOOD_DK = (70, 46, 28)
WOOD_LT = (156, 116, 72)
GOLD_LEAF = (214, 172, 84)
GOLD_DK = (150, 108, 44)
BLOOD = (150, 26, 22)


# ------------------------------------------------------------------ Bild -> Radierung
def engrave(rgb_arr, strength=1.0, hatch=6, edge=True, warm=1.0):
    """Farbbild (HxWx3 uint8) -> Sepia-Radierung mit Schraffur und Tuschekontur (HxWx3 float)."""
    a = rgb_arr.astype(np.float32)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    lum = cv2.GaussianBlur(lum, (0, 0), 0.8)
    t = np.clip((lum - 0.03) * 1.25, 0, 1) ** 0.8
    ink = np.array(SEPIA_INK, np.float32)
    pap = np.array(SEPIA_PAPER, np.float32)
    mid = np.array(SEPIA_MID, np.float32)
    # dreistufige Tonung: Tinte - Mittelton - Papier
    col = np.where(t[..., None] < 0.5,
                   ink * (1 - t[..., None] * 2) + mid * (t[..., None] * 2),
                   mid * (1 - (t[..., None] - 0.5) * 2) + pap * ((t[..., None] - 0.5) * 2))
    H, Wd = t.shape
    yy, xx = np.mgrid[0:H, 0:Wd]
    d1 = ((xx + yy) % hatch) < 1.6
    d2 = ((xx - yy) % hatch) < 1.4
    d3 = (yy % (hatch - 1)) < 1.2
    m1 = d1 & (t < 0.62)
    m2 = d2 & (t < 0.40)
    m3 = d3 & (t < 0.22)
    for m, k in ((m1, 0.42), (m2, 0.38), (m3, 0.3)):
        col[m] = col[m] * (1 - k * strength) + ink * k * strength
    if edge:
        g = (lum * 255).astype(np.uint8)
        e = cv2.Canny(g, 40, 110).astype(np.float32) / 255
        e = cv2.GaussianBlur(e, (0, 0), 0.6)
        col = col * (1 - 0.55 * e[..., None]) + ink * 0.55 * e[..., None]
    return np.clip(col, 0, 255)


def tint_mix(color_arr, sepia_arr, u):
    """u=0 Sepia .. 1 volle Farbe (Farbe flutet von den Lichtern her ein)"""
    if u <= 0:
        return sepia_arr
    if u >= 1:
        return color_arr.astype(np.float32)
    lum = color_arr.astype(np.float32).mean(2, keepdims=True) / 255
    k = np.clip((u * 1.6 - (1 - lum) * 0.6), 0, 1)
    return sepia_arr * (1 - k) + color_arr.astype(np.float32) * k


# ------------------------------------------------------------------ Ornamente
def star8(c, x, y, r, col=GOLD_LEAF, a=255, rot=0.0, glow=0.0):
    """Kompass-Stern mit acht Spitzen (vier lange, vier kurze), Tuschekontur"""
    if a <= 0 or r <= 0.3:
        return
    if glow > 0:
        c.drawCircle(x, y, r * 1.8, blur_paint(rgb(255, 214, 140, int(110 * glow * a / 255)), r * 0.9))
    pts = []
    for i in range(16):
        ang = rot + i * math.pi / 8
        rr = r if i % 4 == 0 else (r * 0.55 if i % 2 == 0 else r * 0.2)
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    p = poly(pts)
    c.drawPath(p, paint(C(col, a)))
    c.drawPath(p, paint(C(SEPIA_INK, int(a * 0.85)), stroke=max(0.8, r * 0.08)))
    # Grat: halbe Spitzen dunkler (Radierung)
    for i in range(0, 16, 2):
        ang = rot + i * math.pi / 8
        rr = r if i % 4 == 0 else r * 0.55
        tip = (x + math.cos(ang) * rr, y + math.sin(ang) * rr)
        side = (x + math.cos(ang + math.pi / 8) * r * 0.2, y + math.sin(ang + math.pi / 8) * r * 0.2)
        c.drawPath(poly([(x, y), tip, side]), paint(C(GOLD_DK, int(a * 0.55))))


def cloud_scroll(c, x, y, w, h, flip=False, a=255, t=0.0, fill=SEPIA_PAPER, ink=SEPIA_INK, seed=0, puffs=6):
    """flache Schnörkelwolke (ausgeschnittenes Papier): Bäusche als Kreisunion, Einrollungen, Schraffur unten"""
    if a <= 0:
        return
    rng = np.random.default_rng(seed)
    circles = []
    for i in range(puffs):
        u = (i + 0.5) / puffs
        r = h * (0.32 + 0.38 * math.sin(math.pi * u) ** 0.8) * rng.uniform(0.85, 1.1)
        cx = -w / 2 + w * u + rng.uniform(-0.04, 0.04) * w
        cy = -r * rng.uniform(0.55, 0.8)
        circles.append((cx, cy, r))
    # zweite Reihe oben
    for i in range(max(1, puffs // 2 - 1)):
        u = (i + 1) / (puffs // 2)
        r = h * rng.uniform(0.28, 0.4)
        circles.append((-w * 0.3 + w * 0.6 * u + rng.uniform(-10, 10), -h * rng.uniform(0.75, 0.95), r))
    with saved(c):
        c.translate(x, y)
        if flip:
            c.scale(-1, 1)
        p = skia.Path()
        p.addRect(R(-w / 2, -h * 0.2, w / 2, 0))
        for (cx, cy, r) in circles:
            q = skia.Path()
            q.addCircle(cx, cy, r)
            p = skia.Op(p, q, skia.PathOp.kUnion_PathOp)
        sh = skia.Path(p)
        sh.offset(7, 9)
        c.drawPath(sh, blur_paint(rgb(20, 12, 6, int(100 * a / 255)), 7))
        c.drawPath(p, paint(C(fill, a)))
        c.save()
        c.clipPath(p, doAntiAlias=True)
        # Schatten-Schraffur im unteren Teil jedes Bauschs
        for (cx, cy, r) in circles:
            for k in range(-int(r), int(r), 6):
                xx = cx + k
                yy0 = cy + math.sqrt(max(0, r * r - k * k)) * 0.35
                c.drawLine(xx, yy0, xx + 8, cy + r, paint(C(ink, int(a * 0.28)), stroke=1.0))
        # Einrollungen: Bogen entlang der Unterkante jedes Bauschs, endet in einer Schnecke
        for j, (cx, cy, r) in enumerate(circles):
            if j % 2 == 1 and j < puffs:
                continue
            sp = skia.Path()
            a0 = math.radians(200 + 20 * math.sin(j))
            pts = []
            for i in range(30):
                u = i / 29
                ang = a0 + u * math.radians(170)
                rr = r * (0.82 - 0.5 * u ** 2)
                pts.append((cx + math.cos(ang) * rr * 0.98, cy + math.sin(ang) * rr * 0.9 + r * 0.06))
            c.drawPath(smooth_path(pts, closed=False), paint(C(ink, int(a * 0.75)), stroke=1.7))
        c.restore()
        c.drawPath(p, paint(C(ink, int(a * 0.95)), stroke=2.4))


def ribbon(c, pts, w=26, t=0.0, a=255, fill=SEPIA_PAPER, ink=SEPIA_INK, wave=10.0, ph=0.0):
    """Papierband entlang einer Mittellinie, mit Wellen und Rückseiten-Schatten"""
    if a <= 0:
        return
    path_pts = []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        path_pts.append((x, y + wave * math.sin(t * 1.3 + i * 0.9 + ph)))
    L, Rr = [], []
    for i in range(n):
        x0, y0 = path_pts[max(0, i - 1)]
        x1, y1 = path_pts[min(n - 1, i + 1)]
        ang = math.atan2(y1 - y0, x1 - x0)
        tw = math.cos(t * 0.6 + i * 0.32 + ph)         # Verdrehung des Bandes
        ww = w / 2 * (0.45 + 0.55 * abs(tw))
        nx, ny = -math.sin(ang) * ww, math.cos(ang) * ww
        L.append((path_pts[i][0] + nx, path_pts[i][1] + ny))
        Rr.append((path_pts[i][0] - nx, path_pts[i][1] - ny))
    p = smooth_path(L + Rr[::-1], closed=True)
    sh = skia.Path(p)
    sh.offset(5, 9)
    c.drawPath(sh, blur_paint(rgb(20, 12, 6, int(70 * a / 255)), 5))
    c.drawPath(p, paint(C(fill, a)))
    # dunklere Rückseite, wo das Band dreht
    for i in range(n - 1):
        tw = math.cos(t * 0.6 + i * 0.32 + ph)
        if tw < 0:
            c.drawPath(poly([L[i], L[i + 1], Rr[i + 1], Rr[i]]), paint(C(SEPIA_MID, int(a * 0.55 * min(1, -tw * 2)))))
    c.drawPath(p, paint(C(ink, int(a * 0.85)), stroke=1.8))
    c.drawPath(smooth_path(path_pts, closed=False), paint(C(ink, int(a * 0.25)), stroke=1.0))


def interlace_band(c, x0, y0, x1, y1, period=56, a=255, col=GOLD_LEAF, ink=SEPIA_INK, t=0.0):
    """zwei verflochtene Bänder in einem Rechteckstreifen (horizontal, wenn breiter als hoch)"""
    horiz = (x1 - x0) >= (y1 - y0)
    Lg = (x1 - x0) if horiz else (y1 - y0)
    th = (y1 - y0) if horiz else (x1 - x0)
    n = max(2, int(Lg / period))
    per = Lg / n
    amp = th * 0.32
    with saved(c):
        c.translate(x0, y0)
        if not horiz:
            c.rotate(90)
            c.translate(0, -th)
        cy = th / 2

        def curve(phase):
            pts = [(s, cy + amp * math.sin(2 * math.pi * s / per + phase)) for s in np.linspace(0, Lg, n * 24 + 1)]
            return poly(pts, closed=False)
        for ph in (0.0, math.pi):
            c.drawPath(curve(ph), paint(C(ink, a), stroke=th * 0.26))
            c.drawPath(curve(ph), paint(C(col, a), stroke=th * 0.16))
        # Über-Unter: an jeder Kreuzung das erste Band nochmal oben
        for k in range(2 * n):
            s = (k + 0.5) * per / 2
            if k % 2 == 0:
                seg = [(ss, cy + amp * math.sin(2 * math.pi * ss / per)) for ss in np.linspace(s - per * 0.12, s + per * 0.12, 9)]
                c.drawPath(poly(seg, closed=False), paint(C(ink, a), stroke=th * 0.26))
                c.drawPath(poly(seg, closed=False), paint(C(col, a), stroke=th * 0.16))
        c.drawLine(0, 1, Lg, 1, paint(C(ink, a), stroke=2))
        c.drawLine(0, th - 1, Lg, th - 1, paint(C(ink, a), stroke=2))


def knot_disc(c, x, y, r, a=255, col=GOLD_LEAF, ink=SEPIA_INK):
    """Eckknoten: Kreis mit vier verschlungenen Schlaufen"""
    c.drawCircle(x, y, r, paint(C(WOOD_DK, a)))
    for k in range(4):
        ang = k * math.pi / 2 + math.pi / 4
        cx, cy = x + math.cos(ang) * r * 0.38, y + math.sin(ang) * r * 0.38
        c.drawCircle(cx, cy, r * 0.42, paint(C(ink, a), stroke=r * 0.2))
        c.drawCircle(cx, cy, r * 0.42, paint(C(col, a), stroke=r * 0.11))
    c.drawCircle(x, y, r, paint(C(ink, a), stroke=2.5))
    c.drawCircle(x, y, r * 0.16, paint(C(col, a)))


def carved_plank(c, x0, y0, x1, y1, a=255, seed=0):
    """Holzleiste mit eingravierten Linien"""
    rect = R(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))
    c.drawRect(rect, paint(C(WOOD, a)))
    horiz = rect.width() >= rect.height()
    rng = np.random.default_rng(seed)
    if horiz:
        for k in range(5):
            yy = rect.top() + rect.height() * (0.18 + 0.16 * k)
            c.drawLine(rect.left(), yy, rect.right(), yy + rng.uniform(-1, 1), paint(C(WOOD_DK, int(a * 0.5)), stroke=1.2))
        c.drawLine(rect.left(), rect.top() + 2, rect.right(), rect.top() + 2, paint(C(WOOD_LT, a), stroke=2))
    else:
        for k in range(5):
            xx = rect.left() + rect.width() * (0.18 + 0.16 * k)
            c.drawLine(xx, rect.top(), xx + rng.uniform(-1, 1), rect.bottom(), paint(C(WOOD_DK, int(a * 0.5)), stroke=1.2))
        c.drawLine(rect.left() + 2, rect.top(), rect.left() + 2, rect.bottom(), paint(C(WOOD_LT, a), stroke=2))
    c.drawRect(rect, paint(C(SEPIA_INK, a), stroke=2.2))


def ornate_frame(c, rect, bw=56, a=255, t=0.0, braces=True, knot_r=None):
    """Flechtwerk-Rahmen: Holzleisten, Flechtband, Eckknoten, diagonale Streben"""
    x0, y0, x1, y1 = rect
    kr = knot_r or bw * 0.62
    # Holzleisten
    carved_plank(c, x0 - bw, y0 - bw, x1 + bw, y0, a, 1)
    carved_plank(c, x0 - bw, y1, x1 + bw, y1 + bw, a, 2)
    carved_plank(c, x0 - bw, y0, x0, y1, a, 3)
    carved_plank(c, x1, y0, x1 + bw, y1, a, 4)
    # Flechtband darin
    m = bw * 0.22
    interlace_band(c, x0 - bw + m + kr, y0 - bw + m, x1 + bw - m - kr, y0 - m, a=a, t=t)
    interlace_band(c, x0 - bw + m + kr, y1 + m, x1 + bw - m - kr, y1 + bw - m, a=a, t=t)
    interlace_band(c, x0 - bw + m, y0 + kr * 0.6, x0 - m, y1 - kr * 0.6, a=a, t=t)
    interlace_band(c, x1 + m, y0 + kr * 0.6, x1 + bw - m, y1 - kr * 0.6, a=a, t=t)
    # Goldfilet innen
    c.drawRect(R(x0 - 3, y0 - 3, x1 + 3, y1 + 3), paint(C(GOLD_LEAF, a), stroke=4))
    c.drawRect(R(x0 - 6, y0 - 6, x1 + 6, y1 + 6), paint(C(SEPIA_INK, a), stroke=1.5))
    if braces:
        q = bw * 1.25
        o = bw * 0.62
        for (ax, ay, bx, by) in ((x0 + q - o, y0 - o, x0 - o, y0 + q - o), (x1 - q + o, y0 - o, x1 + o, y0 + q - o),
                                 (x0 + q - o, y1 + o, x0 - o, y1 - q + o), (x1 - q + o, y1 + o, x1 + o, y1 - q + o)):
            with saved(c):
                c.translate((ax + bx) / 2, (ay + by) / 2)
                c.rotate(math.degrees(math.atan2(by - ay, bx - ax)))
                L = math.hypot(bx - ax, by - ay) + bw * 0.5
                carved_plank(c, -L / 2, -bw * 0.2, L / 2, bw * 0.2, a, 7)
    for (cx, cy) in ((x0 - bw / 2, y0 - bw / 2), (x1 + bw / 2, y0 - bw / 2), (x0 - bw / 2, y1 + bw / 2), (x1 + bw / 2, y1 + bw / 2)):
        knot_disc(c, cx, cy, kr, a)


def nimbus(c, x, y, r, a=255, col=GOLD_LEAF, inner=None, rays=False, t=0.0, crack=0.0):
    """punzierter Goldnimbus (Ikonen-Heiligenschein): Scheibe, Punzen-Ringe, Radialritzungen"""
    if a <= 0 or r <= 1:
        return
    g = skia.GradientShader.MakeRadial(P(x - r * 0.3, y - r * 0.35), r * 1.4,
                                       [rgb(*mix(col, (255, 240, 200), 0.45), a), rgb(*col, a), rgb(*mix(col, (60, 30, 10), 0.35), a)], [0, 0.55, 1])
    c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Shader=g))
    if inner:
        c.drawCircle(x, y, r * 0.66, paint(C(inner, int(a * 0.85))))
    # Radialritzung
    for k in range(48):
        ang = k * math.pi * 2 / 48
        c.drawLine(x + math.cos(ang) * r * 0.70, y + math.sin(ang) * r * 0.70, x + math.cos(ang) * r * 0.86, y + math.sin(ang) * r * 0.86,
                   paint(C(GOLD_DK, int(a * 0.55)), stroke=1.0))
    # Punzenringe
    for rr, nn in ((r * 0.93, 54), (r * 0.62, 34)):
        for k in range(nn):
            ang = k * math.pi * 2 / nn
            c.drawCircle(x + math.cos(ang) * rr, y + math.sin(ang) * rr, max(1.0, r * 0.028), paint(C(GOLD_DK, int(a * 0.8))))
    c.drawCircle(x, y, r, paint(C(SEPIA_INK, int(a * 0.8)), stroke=max(1.2, r * 0.03)))
    # Glanz, der wandert
    gl = (math.sin(t * 0.8) + 1) / 2
    ang = -2.2 + gl * 1.2
    c.drawCircle(x + math.cos(ang) * r * 0.55, y + math.sin(ang) * r * 0.55, r * 0.22, blur_paint(rgb(255, 250, 220, int(90 * a / 255)), r * 0.12))
    if rays:
        for k in range(16):
            ang = k * math.pi * 2 / 16 + t * 0.05
            l0, l1 = r * 1.05, r * (1.35 + 0.15 * (k % 2))
            c.drawLine(x + math.cos(ang) * l0, y + math.sin(ang) * l0, x + math.cos(ang) * l1, y + math.sin(ang) * l1,
                       paint(C(col, int(a * 0.8)), stroke=2.2))
    if crack > 0:
        rng = np.random.default_rng(5)
        for k in range(5):
            ang = rng.uniform(0, 6.28)
            pts = [(x, y)]
            for j in range(1, 6):
                u = j / 5 * crack
                pts.append((x + math.cos(ang + rng.uniform(-0.3, 0.3)) * r * u, y + math.sin(ang + rng.uniform(-0.3, 0.3)) * r * u))
            c.drawPath(poly(pts, closed=False), paint(C(SEPIA_INK, int(a * 0.9)), stroke=2.2))


RUNES = ['ᚠ', 'ᚢ', 'ᚦ', 'ᚨ', 'ᚱ', 'ᚲ', 'ᚷ', 'ᚹ', 'ᚺ', 'ᚾ', 'ᛁ', 'ᛃ', 'ᛇ', 'ᛈ', 'ᛉ', 'ᛊ', 'ᛏ', 'ᛒ', 'ᛖ', 'ᛗ', 'ᛚ', 'ᛜ', 'ᛞ', 'ᛟ']


def glyph(c, x, y, s, k, col, a, rot=0.0):
    """selbst gezeichnete Rune (keine Schrift nötig): Striche aus einem kleinen Raster"""
    rng = np.random.default_rng(100 + k)
    with saved(c):
        c.translate(x, y)
        c.rotate(rot)
        pts = [(0, -s), (0, s)]
        c.drawLine(0, -s, 0, s, paint(C(col, a), stroke=max(1.0, s * 0.18)))
        for j in range(rng.integers(1, 3)):
            yy = rng.uniform(-s, s * 0.6)
            dx = s * rng.choice([-0.7, 0.7])
            c.drawLine(0, yy, dx, yy + s * rng.uniform(0.2, 0.6), paint(C(col, a), stroke=max(1.0, s * 0.16)))
        if rng.random() < 0.4:
            c.drawCircle(0, -s * 0.2, s * 0.35, paint(C(col, a), stroke=max(1.0, s * 0.14)))


def rune_circle(c, x, y, r, u=1.0, col=GOLD_LEAF, a=255, t=0.0, squash=1.0, seed=0, glow=0.6):
    """Zauberkreis wie mit Tinte gezogen: Ringe, Runenband, Flechtring, geometrische Mitte.
    u = Fortschritt des Zeichnens 0..1; squash < 1 legt ihn perspektivisch auf den Boden"""
    if u <= 0 or a <= 0:
        return
    with saved(c):
        c.translate(x, y)
        c.scale(1, squash)
        if glow > 0:
            c.drawCircle(0, 0, r * 1.1, blur_paint(rgb(*col, int(70 * glow * a / 255 * u)), r * 0.18))

        def arc(rr, uu, sw):
            if uu <= 0:
                return
            p = skia.Path()
            p.addArc(R(-rr, -rr, rr, rr), -90 + t * 4, 360 * min(uu, 1))
            c.drawPath(p, paint(C(col, a), stroke=sw))
        arc(r, u * 1.6, 3.2)
        arc(r * 0.94, u * 1.6 - 0.15, 1.6)
        arc(r * 0.70, u * 1.6 - 0.3, 2.4)
        arc(r * 0.52, u * 1.6 - 0.45, 1.6)
        # Runen zwischen 0.72 und 0.92
        n = 24
        for k in range(n):
            uk = clamp((u * 1.6 - 0.2 - k / n * 0.8) * 4)
            if uk <= 0:
                continue
            ang = -math.pi / 2 + k * 2 * math.pi / n + math.radians(t * 4)
            glyph(c, math.cos(ang) * r * 0.82, math.sin(ang) * r * 0.82, r * 0.055, k + seed, col, int(a * uk), math.degrees(ang) + 90)
        # Mitte: zwei gedrehte Quadrate
        um = clamp((u - 0.55) / 0.45)
        if um > 0:
            for rot in (0, 45):
                with saved(c):
                    c.rotate(rot + t * 6)
                    s = r * 0.34
                    p = poly([(-s, -s), (s, -s), (s, s), (-s, s)])
                    m = skia.PathMeasure(p, True)
                    seg = skia.Path()
                    m.getSegment(0, m.getLength() * um, seg, True)
                    c.drawPath(seg, paint(C(col, a), stroke=2.4))
            c.drawCircle(0, 0, r * 0.1 * um, paint(C(col, a), stroke=2))
