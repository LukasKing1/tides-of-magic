"""Zeichenbasis v4 fuer 'Will AI Buy Our Cars?' im Stil von Rational Animations.

Konturen werden in Bildschirmpixeln angegeben (unabhaengig von Skalierung), jede Flaeche bekommt
einen Cel-Schatten, Figuren sind Profilkoepfe mit Anzug, Haende haben lange, gegliederte Finger.
"""
import importlib.util, math, os, random
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('prophecy', os.path.join(HERE, 'prophecy.py'))
P = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(P)

W, H, FPS = P.W, P.H, P.FPS
col, mix, clamp, prog, lerp = P.col, P.mix, P.clamp, P.prog, P.lerp
eio, eout, ein, eback = P.eio, P.eout, P.ein, P.eback
circle, poly, union, bez, seg, capsule = P.circle, P.poly, P.union, P.bez, P.seg, P.capsule
star5, sparkle4, trim = P.star5, P.sparkle4, P.trim

INK = '#0d0e0e'
BG = '#1a1b1b'
BONE = '#c9c8bb'
BONE_HI = '#e2e0d4'
BONE_SH = '#a3a397'
SKIN = '#c6c6b9'
SKIN_SH = '#a2a397'
HAIR = '#b2b3a7'
HAIR_SH = '#8b8c82'
SUIT = '#242626'
SUIT_HI = '#353837'
SHIRT = '#d6d4c8'
GOLD = '#d4ad5f'
GOLD_HI = '#ffe2a0'
GOLD_DK = '#8a6a33'
GOLD_SH = '#a9813f'
RED = '#9c4436'
SNAKE = '#5a7060'
SNAKE_SH = '#405246'
SNAKE_HI = '#7d947f'
BELLY = '#c8c2a6'
BELLY_SH = '#a39d84'
AMBER = '#dba443'
OW = 3.0  # Konturbreite in Bildschirmpixeln


class G:
    frame = 0
    cache = {}


def mscale(cv):
    m = cv.getTotalMatrix()
    return math.sqrt(abs(m.getScaleX() * m.getScaleY() - m.getSkewX() * m.getSkewY())) or 1.0


def _boil(s):
    key = (G.frame // 3, round(s, 2))
    pe = G.cache.get(key)
    if pe is None:
        if len(G.cache) > 200:
            G.cache.clear()
        d = skia.DiscretePathEffect.Make(16 / s, .9 / s, G.frame // 3)
        c = skia.CornerPathEffect.Make(5 / s)
        pe = skia.PathEffect.MakeCompose(c, d)
        G.cache[key] = pe
    return pe


def fillp(cv, c, a=1.0, wob=True):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    if wob:
        p.setPathEffect(_boil(mscale(cv)))
    return p


def inkp(cv, px=OW, c=INK, a=1.0, wob=True, cap=True):
    s = mscale(cv)
    p = skia.Paint(AntiAlias=True, Color=col(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=px / s,
                   StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap,
                   StrokeJoin=skia.Paint.kRound_Join)
    if wob:
        p.setPathEffect(_boil(s))
    return p


def strokep(cv, w, c, a=1.0, wob=False, cap=True):
    """Strich mit Breite in lokalen Einheiten."""
    p = skia.Paint(AntiAlias=True, Color=col(c, a), Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=skia.Paint.kRound_Cap if cap else skia.Paint.kButt_Cap,
                   StrokeJoin=skia.Paint.kRound_Join)
    if wob:
        p.setPathEffect(_boil(mscale(cv)))
    return p


def glowp(cv, c, sigma_px, a=1.0):
    p = skia.Paint(AntiAlias=True, Color=col(c, a))
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma_px / mscale(cv)))
    return p


def draw(cv, path, fill, a=1.0, px=OW, shade=None, shade_col=None, hi=None, hi_col=None, wob=True):
    """Flaeche mit Fuellung, optionalem Cel-Schatten und Glanz, dann Kontur."""
    cv.drawPath(path, fillp(cv, fill, a, wob))
    if shade is not None or hi is not None:
        cv.save()
        cv.clipPath(path, doAntiAlias=True)
        if shade is not None:
            cv.drawPath(shade, fillp(cv, shade_col, a, False))
        if hi is not None:
            cv.drawPath(hi, fillp(cv, hi_col, a, False))
        cv.restore()
    if px > 0:
        cv.drawPath(path, inkp(cv, px, INK, a, wob))


def offset(path, dx, dy):
    q = skia.Path(path)
    q.offset(dx, dy)
    return q


def rim(cv, path, dx, dy, c, a=1.0):
    """Randlicht auf der Seite, aus der (dx, dy) zeigt."""
    r = skia.Op(path, offset(path, -dx, -dy), skia.PathOp.kDifference_PathOp)
    if r is not None:
        cv.drawPath(r, fillp(cv, c, a, False))


def cel(path, dx, dy):
    """Schattenregion: Teil der Flaeche, der vom verschobenen Gegenstueck nicht bedeckt ist (Licht von -dx,-dy)."""
    return skia.Op(path, offset(path, -dx, -dy), skia.PathOp.kDifference_PathOp)


def P_(pts, close=True, s=1.0, ox=0.0, oy=0.0):
    p = skia.Path()
    p.moveTo(ox + pts[0][0] * s, oy + pts[0][1] * s)
    for q in pts[1:]:
        if len(q) == 2:
            p.lineTo(ox + q[0] * s, oy + q[1] * s)
        else:
            p.cubicTo(ox + q[0] * s, oy + q[1] * s, ox + q[2] * s, oy + q[3] * s, ox + q[4] * s, oy + q[5] * s)
    if close:
        p.close()
    return p


def text(cv, s, x, y, tf, size, c, a=1.0, spacing=0.0, anchor='l'):
    f = skia.Font(tf, size)
    w = f.measureText(s) + spacing * max(0, len(s) - 1)
    if anchor == 'c':
        x -= w / 2
    elif anchor == 'r':
        x -= w
    if spacing == 0:
        cv.drawTextBlob(skia.TextBlob.MakeFromString(s, f), x, y, skia.Paint(AntiAlias=True, Color=col(c, a)))
    else:
        for ch in s:
            cv.drawTextBlob(skia.TextBlob.MakeFromString(ch, f), x, y, skia.Paint(AntiAlias=True, Color=col(c, a)))
            x += f.measureText(ch) + spacing
    return w


def blink(t, seed=0.0, period=3.7):
    ph = (t + seed) % period
    return 1.0 - math.sin(math.pi * clamp(ph / .16)) if ph < .16 else 1.0


# ================================================================ Menschen
HEAD = [(0.20, 0.10), (0.35, 0.00, 0.55, 0.00, 0.62, 0.10), (0.645, 0.30), (0.665, 0.33, 0.645, 0.35, 0.648, 0.37),
        (0.765, 0.515), (0.785, 0.55, 0.745, 0.572, 0.69, 0.566), (0.676, 0.60), (0.688, 0.624), (0.662, 0.646),
        (0.678, 0.672), (0.662, 0.72, 0.664, 0.78, 0.652, 0.82), (0.625, 0.88, 0.52, 0.892, 0.44, 0.862),
        (0.30, 0.765), (0.262, 0.60), (0.18, 0.55, 0.115, 0.45, 0.118, 0.32), (0.12, 0.20, 0.15, 0.12, 0.20, 0.10)]
HAIR_A = [(0.10, 0.50), (0.035, 0.30, 0.07, 0.04, 0.30, -0.025), (0.48, -0.075, 0.67, -0.035, 0.705, 0.06),
          (0.725, 0.125, 0.665, 0.15, 0.625, 0.125), (0.55, 0.10, 0.48, 0.12, 0.43, 0.16), (0.37, 0.30),
          (0.305, 0.315), (0.245, 0.40, 0.225, 0.46, 0.205, 0.52)]
HAIR_B = [(0.11, 0.46), (0.06, 0.28, 0.10, 0.06, 0.28, 0.0), (0.45, -0.04, 0.60, -0.01, 0.645, 0.08),
          (0.60, 0.10, 0.52, 0.10, 0.46, 0.13), (0.40, 0.28), (0.31, 0.31), (0.25, 0.40, 0.22, 0.44, 0.20, 0.50)]


def person_profile(cv, x, y, s, t, facing=1, hair='A', glasses=False, look=0.0, mouth=0.0, breathe=True,
                   arm=None, palette=None, a=1.0, eye_open=None):
    """Brustbild im Profil (nach rechts schauend bei facing=1). (x,y) = Kinn-Hoehe Mitte Kopf, s = Kopfhoehe in px.
    arm: Funktion(cv) zeichnet den vorderen Arm im selben Koordinatensystem (Kopfeinheiten)."""
    pal = palette or {}
    skin, skin_sh = pal.get('skin', SKIN), pal.get('skin_sh', SKIN_SH)
    hair_c, hair_sh = pal.get('hair', HAIR), pal.get('hair_sh', HAIR_SH)
    suit, suit_hi = pal.get('suit', SUIT), pal.get('suit_hi', SUIT_HI)
    br = 1 + (.012 * math.sin(t * 1.6) if breathe else 0)
    cv.save()
    cv.translate(x, y)
    cv.scale(s * facing, s)
    cv.translate(-0.45, -0.5)
    # Jacke / Schultern
    cv.save()
    cv.translate(0.35, 1.0)
    cv.scale(1, br)
    cv.translate(-0.35, -1.06)
    jacket = P_([(-0.42, 2.4), (-0.40, 1.55), (-0.36, 1.22, -0.10, 1.04, 0.20, 1.00), (0.42, 1.18), (0.60, 0.98),
                 (0.84, 1.04, 1.00, 1.22, 1.04, 1.50), (1.08, 2.4)])
    draw(cv, jacket, suit, a, shade=cel(jacket, -.10, 0), shade_col='#1b1c1c')
    cv.drawPath(P_([(0.42, 1.18), (0.30, 1.55), (0.36, 2.2)], close=False), inkp(cv, OW * .8, INK, a))
    cv.drawPath(P_([(0.60, 0.98), (0.70, 1.30), (0.56, 1.55)], close=False), inkp(cv, OW * .8, INK, a))
    cv.drawPath(P_([(-0.30, 1.40), (-0.20, 1.22, 0.00, 1.10, 0.16, 1.07)], close=False), inkp(cv, OW * 1.6, suit_hi, .8 * a, cap=True))
    shirt = P_([(0.20, 1.00), (0.42, 1.18), (0.60, 0.98), (0.56, 0.92), (0.24, 0.92)])
    draw(cv, shirt, SHIRT, a)
    tie = P_([(0.40, 1.10), (0.46, 1.10), (0.48, 1.40), (0.43, 1.46), (0.38, 1.40)])
    draw(cv, tie, '#3d3027' if not pal.get('tie') else pal['tie'], a)
    cv.restore()
    # Hals
    neck = P_([(0.28, 0.70), (0.49, 0.82), (0.52, 0.97), (0.25, 0.97)])
    draw(cv, neck, skin_sh, a)
    # Kopf
    cv.save()
    cv.translate(0.45, 0.78)
    cv.rotate(look)
    cv.translate(-0.45, -0.78)
    face = P_(HEAD)
    shade = P_([(0.30, 0.42), (0.42, 0.50), (0.50, 0.64), (0.52, 0.80), (0.44, 0.87), (0.28, 0.77)])
    draw(cv, face, skin, a, shade=shade, shade_col=skin_sh,
         hi=P_([(0.50, 0.04), (0.62, 0.10), (0.645, 0.30), (0.60, 0.30), (0.58, 0.12)]), hi_col=BONE_HI)
    # Ohr
    ear = P_([(0.355, 0.37), (0.27, 0.33, 0.25, 0.53, 0.335, 0.53), (0.36, 0.46)])
    draw(cv, ear, skin, a)
    cv.drawPath(P_([(0.33, 0.41), (0.29, 0.42, 0.29, 0.48, 0.325, 0.49)], close=False), inkp(cv, OW * .7, INK, a))
    # Haare
    hp = P_(HAIR_A if hair == 'A' else HAIR_B)
    draw(cv, hp, hair_c, a, shade=P_([(0.0, 0.25), (0.20, 0.10), (0.30, 0.40), (0.10, 0.6)]), shade_col=hair_sh)
    cv.drawPath(P_([(0.18, 0.05), (0.32, 0.0, 0.46, 0.01, 0.58, 0.06)], close=False), inkp(cv, OW * .7, '#d8d8cc', .7 * a))
    # Auge und Braue
    eo = blink(t, x * .001) if eye_open is None else eye_open
    if glasses:
        g = skia.Path()
        g.addOval(skia.Rect.MakeXYWH(0.50, 0.29, 0.14, 0.13))
        cv.drawPath(g, fillp(cv, '#e8e2d6', .85 * a))
        cv.drawPath(g, inkp(cv, OW * .9, INK, a))
        cv.drawLine(0.50, 0.34, 0.36, 0.32, inkp(cv, OW * .8, INK, a))
    else:
        if eo > .15:
            eye = skia.Path()
            eye.addOval(skia.Rect.MakeXYWH(0.545, 0.34 + 0.02 * (1 - eo), 0.05, 0.045 * eo))
            cv.drawPath(eye, fillp(cv, INK, a, False))
        cv.drawPath(P_([(0.525, 0.335), (0.56, 0.322, 0.60, 0.326, 0.618, 0.338)], close=False), inkp(cv, OW * .9, INK, a))
    cv.drawPath(P_([(0.50, 0.285), (0.56, 0.272, 0.61, 0.276, 0.645, 0.29)], close=False), inkp(cv, OW * 1.5, hair_sh, a))
    cv.drawPath(P_([(0.663, 0.646 + .01 * mouth), (0.63, 0.652 + .02 * mouth), (0.61, 0.648)], close=False),
                inkp(cv, OW * .8, INK, a))
    cv.restore()
    if arm:
        arm(cv)
    cv.restore()


def finger_path(x, y, ang, segs, bend):
    parts = []
    a = math.radians(ang)
    for (L, r0, r1) in segs:
        x1, y1 = x + math.cos(a) * L, y + math.sin(a) * L
        parts.append(capsule(x, y, x1, y1, r0, r1))
        x, y = x1, y1
        a += math.radians(bend)
    return union(parts), (x, y)


def hand_side(cv, x, y, s, ang, curl=0.3, a=1.0, fill=SKIN, shade_c=SKIN_SH, pen=False, sleeve=SUIT):
    """Hand von der Seite (Daumenseite), Handgelenk bei (x,y), zeigt in Richtung ang (Grad). s = Handlaenge."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s / 100, s / 100)
    # hintere Finger
    for (bx, by, fa, segs, b) in [(78, 14, 18, [(22, 7, 6.5), (17, 6.5, 6), (13, 6, 5)], 1.0),
                                  (82, 6, 10, [(26, 7.5, 7), (19, 7, 6.5), (14, 6.5, 5.5)], 1.0)]:
        fp, _ = finger_path(bx, by, fa, segs, (22 + 40 * curl) * b)
        draw(cv, fp, shade_c, a)
    if pen:
        cv.drawLine(40, 34, 128, -2, strokep(cv, 7, INK, a))
        cv.drawLine(40, 34, 128, -2, strokep(cv, 4.5, '#2f2a24', a))
        cv.drawLine(116, 3, 128, -2, strokep(cv, 4.5, GOLD, a))
    palm = P_([(0, -16), (52, -20), (86, -8), (90, 12), (80, 26), (40, 28), (0, 18)])
    draw(cv, palm, fill, a, shade=P_([(0, 8), (90, 4), (90, 30), (0, 30)]), shade_col=shade_c)
    for (bx, by, fa, segs) in [(84, -6, 2, [(28, 8, 7.5), (21, 7.5, 7), (15, 7, 6)]),
                               (84, 4, 8, [(26, 7.5, 7), (19, 7, 6.5), (14, 6.5, 5.5)])]:
        fp, _ = finger_path(bx, by, fa, segs, 20 + 45 * curl)
        draw(cv, fp, fill, a)
    th, _ = finger_path(40, -14, -38, [(26, 9, 8), (20, 8, 7)], 30 + 20 * curl)
    draw(cv, th, fill, a)
    sl = P_([(-90, -26), (2, -24), (6, 24), (-90, 30)])
    draw(cv, sl, sleeve, a)
    cuff = P_([(-4, -22), (8, -21), (10, 22), (-2, 23)])
    draw(cv, cuff, SHIRT, a)
    cv.restore()


def hand_flat(cv, x, y, s, ang, spread=1.0, a=1.0, fill=SKIN, shade_c=SKIN_SH, sleeve=SHIRT):
    """Hand von oben (Handruecken), Handgelenk bei (x,y), Finger in Richtung ang."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s / 100, s / 100)
    fingers = [(92, -24, -10 * spread, [(30, 8, 7.5), (22, 7.5, 7), (16, 7, 6)]),
               (100, -8, -3 * spread, [(34, 8.5, 8), (25, 8, 7.5), (17, 7.5, 6.5)]),
               (100, 10, 4 * spread, [(32, 8.5, 8), (23, 8, 7.5), (16, 7.5, 6.5)]),
               (92, 26, 12 * spread, [(25, 7.5, 7), (18, 7, 6.5), (13, 6.5, 5.5)])]
    for (bx, by, fa, segs) in fingers:
        fp, _ = finger_path(bx, by, fa, segs, 4)
        draw(cv, fp, fill, a)
    th, _ = finger_path(40, -30, -48 * spread, [(30, 10, 9), (24, 9, 8)], 22)
    draw(cv, th, fill, a)
    palm = P_([(0, -28), (60, -34), (98, -30), (104, 0), (98, 34), (56, 38), (0, 30)])
    draw(cv, palm, fill, a, shade=P_([(0, 14), (104, 18), (104, 40), (0, 40)]), shade_col=shade_c)
    cv.drawPath(P_([(30, 4), (55, 0, 72, 2, 90, 6)], close=False), inkp(cv, OW * .6, shade_c, a))
    sl = P_([(-140, -40), (4, -34), (8, 36), (-140, 44)])
    draw(cv, sl, sleeve, a, shade=P_([(-140, 20), (8, 18), (8, 44), (-140, 44)]), shade_col=BONE_SH)
    cv.restore()


def robot_hand(cv, x, y, s, ang, curl=0.3, a=1.0, open_=0.0):
    """Goldene Roboterhand, Handgelenk bei (x,y), zeigt in Richtung ang."""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    cv.scale(s / 100, s / 100)
    joint = lambda jx, jy, r: (cv.drawCircle(jx, jy, r, fillp(cv, GOLD_DK, a, False)),
                               cv.drawCircle(jx, jy, r, inkp(cv, OW * .8, INK, a, False)))
    for (bx, by, fa, n) in [(78, -18, -6, 3), (84, -4, 0, 3), (84, 10, 6, 3), (78, 22, 12, 3)]:
        px_, py_ = bx, by
        ang_ = math.radians(fa - 18 * open_)
        for k, L in enumerate((28, 22, 16)):
            nx, ny = px_ + math.cos(ang_) * L, py_ + math.sin(ang_) * L
            draw(cv, capsule(px_, py_, nx, ny, 5.5 - k * .8, 5 - k * .8), GOLD, a, shade=None)
            joint(px_, py_, 4.5 - k * .6)
            px_, py_ = nx, ny
            ang_ += math.radians(16 + 36 * curl)
    px_, py_, ang_ = 36, -22, math.radians(-50 - 20 * open_)
    for k, L in enumerate((26, 20)):
        nx, ny = px_ + math.cos(ang_) * L, py_ + math.sin(ang_) * L
        draw(cv, capsule(px_, py_, nx, ny, 6, 5.2), GOLD, a)
        joint(px_, py_, 5)
        px_, py_ = nx, ny
        ang_ += math.radians(24 + 20 * curl)
    palm = P_([(0, -24), (70, -26), (86, -12), (86, 20), (70, 30), (0, 26)])
    draw(cv, palm, GOLD, a, shade=P_([(0, 10), (90, 8), (90, 34), (0, 34)]), shade_col=GOLD_SH,
         hi=P_([(4, -20), (70, -22), (70, -14), (4, -12)]), hi_col=GOLD_HI)
    cv.drawCircle(40, 2, 9, fillp(cv, GOLD_DK, a, False))
    cv.drawCircle(40, 2, 9, inkp(cv, OW * .8, INK, a, False))
    cv.drawCircle(40, 2, 3.5, fillp(cv, GOLD_HI, a, False))
    cv.restore()


def robot_arm(cv, pts, w, a=1.0):
    """Gegliederter goldener Arm durch die Punkte pts."""
    n = len(pts)
    for i in range(n - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        r0, r1 = w / 2 * (1 - .15 * i), w / 2 * (1 - .15 * (i + 1))
        c = capsule(x0, y0, x1, y1, r0, r1)
        L = math.hypot(x1 - x0, y1 - y0) or 1
        nx, ny = -(y1 - y0) / L, (x1 - x0) / L
        sh = poly([(x0 + nx * r0 * .1, y0 + ny * r0 * .1), (x1 + nx * r1 * .1, y1 + ny * r1 * .1),
                   (x1 + nx * r1 * 1.2, y1 + ny * r1 * 1.2), (x0 + nx * r0 * 1.2, y0 + ny * r0 * 1.2)])
        hi = poly([(x0 - nx * r0 * .35, y0 - ny * r0 * .35), (x1 - nx * r1 * .35, y1 - ny * r1 * .35),
                   (x1 - nx * r1 * .6, y1 - ny * r1 * .6), (x0 - nx * r0 * .6, y0 - ny * r0 * .6)])
        draw(cv, c, GOLD, a, shade=sh, shade_col=GOLD_SH, hi=hi, hi_col=GOLD_HI)
    for i in range(1, n - 1):
        jx, jy = pts[i]
        r = w * .36 * (1 - .12 * i)
        cv.drawCircle(jx, jy, r, fillp(cv, GOLD_DK, a, False))
        cv.drawCircle(jx, jy, r, inkp(cv, OW, INK, a, False))
        cv.drawCircle(jx, jy, r * .35, fillp(cv, GOLD_HI, a, False))


def bust_front(cv, x, y, s, variant=0, dim=0.0, t=0.0, a=1.0):
    """Brustbild von vorn (fuer Menschenmengen). (x,y) = Schulterlinie Mitte, s = Kopfhoehe."""
    rnd = random.Random(variant)
    suits = ['#2a2c2c', '#3c4a41', '#6b5a45', '#4a3533', '#3a3f48', '#55574f']
    suit = suits[variant % len(suits)]
    skin = mix(SKIN, '#3a3c3a', dim * .85)
    skin_sh = mix(SKIN_SH, '#2b2d2b', dim * .85)
    hair = mix(rnd.choice([HAIR, '#6f6b60', '#4a4640', '#d4d2c4']), '#2a2b29', dim * .7)
    suit = mix(suit, '#202121', dim * .7)
    sink = 0.10 * dim
    tilt = 14 * dim * (1 if variant % 2 else -1)
    cv.save()
    cv.translate(x, y + s * sink)
    cv.scale(s, s)
    body = P_([(-0.72, 1.4), (-0.70, 0.30, -0.55, 0.05, -0.20, 0.0), (0.20, 0.0), (0.55, 0.05, 0.70, 0.30, 0.72, 1.4)])
    draw(cv, body, suit, a, shade=cel(body, -.12, 0), shade_col=mix(suit, '#000000', .35))
    collar = P_([(-0.20, 0.0), (0.0, 0.26), (0.20, 0.0), (0.12, -0.04), (-0.12, -0.04)])
    draw(cv, collar, mix(SHIRT, '#2a2b29', dim * .7), a)
    neck = P_([(-0.11, -0.16), (0.11, -0.16), (0.11, 0.02), (0.0, 0.08), (-0.11, 0.02)])
    draw(cv, neck, skin_sh, a)
    cv.save()
    cv.translate(0, -0.12)
    cv.rotate(tilt)
    hw, hh = 0.40, 0.66
    head = skia.Path()
    head.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-hw / 2, -hh, hw, hh), .17, .2))
    draw(cv, head, skin, a, shade=P_([(0.03, -hh), (hw, -hh), (hw, 0), (0.06, 0)]), shade_col=skin_sh)
    for sx in (-1, 1):
        ear = skia.Path()
        ear.addOval(skia.Rect.MakeXYWH(sx * hw / 2 - 0.035, -hh * .58, 0.07, 0.14))
        draw(cv, ear, skin if sx < 0 else skin_sh, a)
    v = variant % 4
    if v == 0:
        hp = P_([(-hw / 2 - .01, -hh * .62), (-hw / 2 - .02, -hh * 1.06, hw / 2 + .02, -hh * 1.06, hw / 2 + .01, -hh * .62),
                 (hw * .3, -hh * .8), (-hw * .1, -hh * .82)])
    elif v == 1:
        hp = P_([(-hw / 2 - .01, -hh * .55), (-hw / 2, -hh * 1.04, hw / 2, -hh * 1.04, hw / 2 + .01, -hh * .55),
                 (hw / 2 - .02, -hh * .78), (-hw * .05, -hh * .86), (-hw / 2 + .02, -hh * .78)])
    elif v == 2:
        hp = P_([(-hw / 2 - .04, -hh * .25), (-hw / 2 - .05, -hh * 1.1, hw / 2 + .05, -hh * 1.1, hw / 2 + .04, -hh * .25),
                 (hw / 2 - .02, -hh * .78), (-hw / 2 + .02, -hh * .78)])
    else:
        hp = P_([(-hw / 2 + .02, -hh * .78), (-hw / 2, -hh * 1.0, hw / 2, -hh * 1.0, hw / 2 - .02, -hh * .78),
                 (0, -hh * .9)])
    draw(cv, hp, hair, a)
    ey = -hh * .52 + 0.04 * dim
    eo = blink(t, variant * .7, 4.1) if dim < .5 else 1
    for sx in (-1, 1):
        if dim > .5:
            cv.drawLine(sx * .075 - .025, ey + .01, sx * .075 + .025, ey + .01, inkp(cv, OW * .8, INK, a))
        elif eo > .2:
            e = skia.Path()
            e.addOval(skia.Rect.MakeXYWH(sx * .075 - .018, ey - .025 * eo, .036, .05 * eo))
            cv.drawPath(e, fillp(cv, INK, a, False))
    mo = .02 * (1 - dim) - .03 * dim
    cv.drawPath(P_([(-.05, -hh * .24), (0, -hh * .24 + mo, 0, -hh * .24 + mo, .05, -hh * .24)], close=False),
                inkp(cv, OW * .8, INK, a))
    cv.restore()
    cv.restore()


def bust_back(cv, x, y, s, variant=0, rim_a=0.0, a=1.0):
    """Silhouette von hinten. (x,y) = Schulterlinie Mitte, s = Kopfhoehe."""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = P_([(-0.78, 1.6), (-0.76, 0.32, -0.60, 0.04, -0.20, 0.0), (0.20, 0.0), (0.60, 0.04, 0.76, 0.32, 0.78, 1.6)])
    neck = P_([(-0.12, -0.18), (0.12, -0.18), (0.13, 0.04), (-0.13, 0.04)])
    head = skia.Path()
    head.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-0.21, -0.78, 0.42, 0.66), .19, .22))
    ears = union([P_([(-0.21, -0.50), (-0.27, -0.48, -0.27, -0.34, -0.20, -0.33)]),
                  P_([(0.21, -0.50), (0.27, -0.48, 0.27, -0.34, 0.20, -0.33)])])
    if variant == 1:
        hairp = P_([(-0.23, -0.30), (-0.30, -0.95, 0.30, -0.95, 0.23, -0.30)])
    else:
        hairp = P_([(-0.22, -0.46), (-0.24, -0.90, 0.24, -0.90, 0.22, -0.46)])
    sil = union([body, neck, head, ears, hairp])
    cv.drawPath(sil, fillp(cv, '#101111', a))
    cv.drawPath(sil, inkp(cv, OW, INK, a))
    if rim_a > 0:
        cv.save()
        cv.clipPath(sil, doAntiAlias=True)
        rim(cv, sil, 0.035, -0.02, GOLD, rim_a * a)
        cv.restore()
    cv.restore()


# ================================================================ Schlange v4
def snake_head(cv, x, y, ang, w, lid=0.0, tongue=0.0, pupil=1.0, smirk=0.0, a=1.0, flip=False, gold=0.0):
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    if flip:
        cv.scale(1, -1)
    if tongue > 0:
        tl = w * 1.0 * math.sin(math.pi * clamp(tongue))
        tg = skia.Path()
        tg.moveTo(1.9 * w, .08 * w)
        tg.lineTo(1.9 * w + tl, .08 * w)
        tg.moveTo(1.9 * w + tl, .08 * w)
        tg.lineTo(1.9 * w + tl + .22 * w, -.06 * w)
        tg.moveTo(1.9 * w + tl, .08 * w)
        tg.lineTo(1.9 * w + tl + .22 * w, .22 * w)
        cv.drawPath(tg, strokep(cv, w * .1, INK, a))
        cv.drawPath(tg, strokep(cv, w * .055, '#b5523f', a))
    head = P_([(-0.45 * w, -0.42 * w), (0.2 * w, -0.56 * w, 0.75 * w, -0.62 * w, 1.25 * w, -0.55 * w),
               (1.66 * w, -0.50 * w, 1.96 * w, -0.30 * w, 2.0 * w, -0.10 * w),
               (2.02 * w, 0.02 * w, 1.95 * w, 0.12 * w, 1.80 * w, 0.16 * w), (1.0 * w, 0.32 * w),
               (0.6 * w, 0.44 * w, 0.1 * w, 0.46 * w, -0.45 * w, 0.42 * w)])
    jaw = P_([(-0.6 * w, 0.06 * w), (0.5 * w, 0.12 * w), (1.1 * w, 0.22 * w), (1.9 * w, 0.12 * w), (2.1 * w, 0.6 * w),
              (-0.6 * w, 0.6 * w)])
    shade = P_([(-0.6 * w, -0.02 * w), (2.1 * w, -0.08 * w), (2.1 * w, 0.6 * w), (-0.6 * w, 0.6 * w)])
    base = mix(SNAKE, GOLD, gold)
    draw(cv, head, base, a, shade=shade, shade_col=mix(SNAKE_SH, GOLD_SH, gold))
    cv.save()
    cv.clipPath(head, doAntiAlias=True)
    cv.drawPath(jaw, fillp(cv, BELLY, a, False))
    cv.drawPath(P_([(-0.6 * w, 0.32 * w), (2.1 * w, 0.2 * w), (2.1 * w, 0.6 * w), (-0.6 * w, 0.6 * w)]), fillp(cv, BELLY_SH, a, False))
    for k in range(4):
        sx = 0.15 * w + k * 0.28 * w
        sc = skia.Path()
        sc.addArc(skia.Rect.MakeXYWH(sx, -0.62 * w, 0.30 * w, 0.24 * w), 200, 140)
        cv.drawPath(sc, inkp(cv, OW * .7, mix(SNAKE_SH, GOLD_DK, gold), .8 * a))
    cv.drawPath(P_([(0.0, -0.52 * w), (0.9 * w, -0.6 * w, 1.6 * w, -0.5 * w, 1.9 * w, -0.3 * w)], close=False),
                strokep(cv, w * .06, mix(SNAKE_HI, GOLD_HI, gold), .7 * a))
    cv.restore()
    cv.drawPath(head, inkp(cv, OW, INK, a))
    m = P_([(1.88 * w, 0.12 * w), (1.5 * w, 0.20 * w, 1.15 * w, 0.24 * w, 0.75 * w, 0.17 * w),
            (0.66 * w, 0.15 * w - smirk * .1 * w, 0.62 * w, 0.10 * w - smirk * .12 * w, 0.60 * w, 0.06 * w - smirk * .1 * w)], close=False)
    cv.drawPath(m, inkp(cv, OW, INK, a))
    cv.drawCircle(1.82 * w, -0.2 * w, 0.035 * w, fillp(cv, INK, a, False))
    ex, ey, ew, eh = 1.12 * w, -0.27 * w, 0.30 * w, 0.20 * w
    eye = skia.Path()
    eye.moveTo(ex - ew / 2, ey)
    eye.cubicTo(ex - ew / 4, ey - eh * .75, ex + ew / 4, ey - eh * .75, ex + ew / 2, ey - eh * .1)
    eye.cubicTo(ex + ew / 4, ey + eh * .55, ex - ew / 4, ey + eh * .55, ex - ew / 2, ey)
    eye.close()
    cv.drawCircle(ex, ey, ew * .9, glowp(cv, AMBER, w * .15 * mscale(cv), .25 * a))
    cv.drawPath(eye, fillp(cv, AMBER, a, False))
    cv.save()
    cv.clipPath(eye, doAntiAlias=True)
    cv.drawRect(skia.Rect.MakeXYWH(ex - ew, ey + eh * .05, ew * 2, eh), fillp(cv, '#a8701f', a, False))
    pw = ew * .07 * pupil
    cv.drawOval(skia.Rect.MakeXYWH(ex - pw, ey - eh * .7, pw * 2, eh * 1.4), fillp(cv, INK, a, False))
    cv.drawCircle(ex - ew * .2, ey - eh * .22, ew * .07, fillp(cv, '#fff6dc', a, False))
    if lid > 0:
        cv.drawRect(skia.Rect.MakeXYWH(ex - ew, ey - eh, ew * 2, eh * 1.6 * lid), fillp(cv, base, a, False))
        cv.drawLine(ex - ew, ey - eh + eh * 1.6 * lid, ex + ew, ey - eh + eh * 1.6 * lid, inkp(cv, OW, INK, a, False))
    cv.restore()
    cv.drawPath(eye, inkp(cv, OW * .9, INK, a, False))
    brow = P_([(0.86 * w, -0.47 * w), (1.05 * w, -0.60 * w, 1.35 * w, -0.58 * w, 1.46 * w, -0.40 * w),
               (1.30 * w, -0.44 * w, 1.05 * w, -0.44 * w, 0.86 * w, -0.47 * w)])
    draw(cv, brow, mix(SNAKE_SH, GOLD_DK, gold), a)
    cv.restore()


def snake_body(cv, pts, widths, a=1.0, front=True, gold=0.0, gold_from=1.0, belly=0.25, bdir=(0.0, 1.0)):
    """Koerper entlang pts (x,y[,depth]) mit Ruecken, Bauchstreifen (unten) und Rautenmuster."""
    if len(pts) < 2:
        return
    n = len(pts)
    left, right, nrm = [], [], []
    for i in range(n):
        x0, y0 = pts[max(0, i - 1)][:2]
        x1, y1 = pts[min(n - 1, i + 1)][:2]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        wd = widths[i] / 2
        left.append((pts[i][0] + nx * wd, pts[i][1] + ny * wd))
        right.append((pts[i][0] - nx * wd, pts[i][1] - ny * wd))
        nrm.append((nx, ny))
    body = poly(left + right[::-1])
    base = SNAKE if front else SNAKE_SH
    cv.drawPath(body, fillp(cv, base, a))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    # Bauch auf der Seite, deren Normale nach unten zeigt
    bl, br_ = [], []
    for i in range(n):
        nx, ny = nrm[i]
        sgn = 1 if nx * bdir[0] + ny * bdir[1] > 0 else -1
        wd = widths[i] / 2
        cx, cy = pts[i][:2]
        bl.append((cx + nx * sgn * wd * 1.1, cy + ny * sgn * wd * 1.1))
        br_.append((cx + nx * sgn * wd * belly, cy + ny * sgn * wd * belly))
    bp = poly(bl + br_[::-1])
    cv.drawPath(bp, fillp(cv, BELLY if front else BELLY_SH, a, False))
    for i in range(1, n - 1, 2):
        nx, ny = nrm[i]
        sgn = 1 if nx * bdir[0] + ny * bdir[1] > 0 else -1
        cx, cy = pts[i][:2]
        wd = widths[i] / 2
        cv.drawLine(cx + nx * sgn * wd * (belly + .05), cy + ny * sgn * wd * (belly + .05), cx + nx * sgn * wd * 1.1, cy + ny * sgn * wd * 1.1,
                    strokep(cv, max(1.0, 1.6 / mscale(cv)), BELLY_SH, .8 * a))
    # Rautenmuster auf dem Ruecken
    acc = 0.0
    for i in range(1, n - 1):
        acc += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        wd = widths[i]
        if acc > wd * .8 and front:
            acc = 0
            nx, ny = nrm[i]
            sgn = -1 if nx * bdir[0] + ny * bdir[1] > 0 else 1
            cx, cy = pts[i][0] + nx * sgn * wd * .12, pts[i][1] + ny * sgn * wd * .12
            tx, ty = ny, -nx
            dm = poly([(cx + tx * wd * .22, cy + ty * wd * .22), (cx + nx * sgn * wd * .16, cy + ny * sgn * wd * .16),
                       (cx - tx * wd * .22, cy - ty * wd * .22), (cx - nx * sgn * wd * .16, cy - ny * sgn * wd * .16)])
            cv.drawPath(dm, fillp(cv, SNAKE_SH, .9 * a, False))
    # Glanzlinie
    up = [nrm[i][0] * bdir[0] + nrm[i][1] * bdir[1] <= 0 for i in range(n)]
    hl = [(pts[i][0] + ((left[i][0] if up[i] else right[i][0]) - pts[i][0]) * .55,
           pts[i][1] + ((left[i][1] if up[i] else right[i][1]) - pts[i][1]) * .55) for i in range(n)]
    if front:
        cv.drawPath(poly(hl, close=False), strokep(cv, max(1.5, widths[n // 2] * .06), SNAKE_HI, .55 * a))
    if gold > 0:
        k0 = int(n * gold_from)
        if k0 < n - 1:
            gp = poly(left[k0:] + right[k0:][::-1])
            cv.drawPath(gp, fillp(cv, GOLD, .85 * gold, False))
    cv.restore()
    cv.drawPath(poly(left, close=False), inkp(cv, OW, INK, a))
    cv.drawPath(poly(right, close=False), inkp(cv, OW, INK, a))


def snake_ang(pts):
    (x0, y0), (x1, y1) = pts[-3][:2], pts[-1][:2]
    return math.degrees(math.atan2(y1 - y0, x1 - x0))
