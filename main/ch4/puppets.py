"""Stabpuppen im Radierstil: Profilfiguren aus Papier mit Gelenkstift, Stab, Schraffur.
Füße bei (0,0), Höhe ca. 400*s, Blick nach rechts (face=1) oder links (face=-1)."""
import math
import numpy as np
import skia
from lib import *
import style as S

ROBES = {
    'opal': dict(fill=(222, 214, 196), dark=(170, 160, 150), sheen=(196, 214, 230)),
    'empress': dict(fill=(136, 98, 132), dark=(92, 62, 92), sheen=(176, 140, 170)),
    'brother': dict(fill=(132, 50, 38), dark=(86, 30, 24), sheen=(170, 80, 60)),
    'slave': dict(fill=(78, 60, 46), dark=(52, 38, 28), sheen=(100, 80, 62)),
}


def _robe_path(kind):
    if kind == 'empress':
        pts = [(-118, 0), (-70, -60), (-46, -190), (-34, -290), (-26, -318), (-8, -330), (18, -320), (28, -296), (30, -250), (24, -200),
               (40, -110), (66, 0)]
    elif kind == 'slave':
        pts = [(-46, 0), (-40, -110), (-36, -200), (-20, -246), (6, -258), (30, -238), (34, -190), (38, -100), (44, 0)]
    else:
        pts = [(-92, 0), (-60, -80), (-44, -200), (-36, -296), (-26, -320), (-6, -332), (20, -322), (32, -298), (36, -240), (40, -150),
               (58, -40), (70, 0)]
    p = smooth_path(pts + [(30, 8), (-40, 8)], closed=True)
    return p


def _head(c, kind, a, ink):
    """Kopf im Profil + Krone / Haare / Bart, in lokalen Koordinaten (Hals bei 0,-330)"""
    skin = (214, 190, 160) if kind != 'slave' else (150, 120, 96)
    if kind == 'slave':
        hy = -272
        head = smooth_path([(-18, hy - 4), (-10, hy - 22), (12, hy - 22), (24, hy - 8), (28, hy + 4), (18, hy + 14), (4, hy + 18), (-14, hy + 10)])
        c.drawPath(head, paint(C(skin, a)))
        c.drawPath(head, paint(C(ink, a), stroke=2))
        return
    hy = -356
    # Haare der Kaiserin hinten bis zur Taille
    if kind == 'empress':
        hair = smooth_path([(-6, hy - 26), (-30, hy - 10), (-42, hy + 60), (-50, hy + 160), (-30, hy + 150), (-18, hy + 40), (-4, hy + 4)])
        c.drawPath(hair, paint(C((60, 40, 30), a)))
        c.drawPath(hair, paint(C(ink, a), stroke=2))
    head = smooth_path([(-20, hy - 6), (-12, hy - 26), (10, hy - 28), (20, hy - 16), (22, hy - 6), (30, hy + 2), (22, hy + 8), (22, hy + 16),
                        (14, hy + 26), (0, hy + 28), (-14, hy + 18)])
    c.drawPath(head, paint(C(skin, a)))
    c.drawPath(head, paint(C(ink, a), stroke=2.2))
    c.drawCircle(12, hy - 6, 2.0, paint(C(ink, a)))
    if kind == 'opal':
        beard = smooth_path([(-2, hy + 14), (22, hy + 18), (18, hy + 60), (6, hy + 96), (-6, hy + 56)])
        c.drawPath(beard, paint(C((236, 232, 222), a)))
        c.drawPath(beard, paint(C(ink, a), stroke=1.8))
        for k in range(4):
            c.drawLine(4 + k * 4, hy + 24, 2 + k * 3, hy + 80 - k * 6, paint(C(ink, int(a * 0.5)), stroke=1))
        crown = poly([(-18, hy - 22), (-20, hy - 70), (-10, hy - 54), (-2, hy - 82), (6, hy - 54), (14, hy - 72), (16, hy - 22)])
        c.drawPath(crown, paint(C((230, 226, 214), a)))
        c.drawPath(crown, paint(C(ink, a), stroke=1.8))
        for (x, y) in ((-10, hy - 34), (0, hy - 38), (10, hy - 34)):
            c.drawCircle(x, y, 3.2, paint(C((170, 196, 214), a)))
    elif kind == 'empress':
        crown = poly([(-16, hy - 22), (-22, hy - 62), (-12, hy - 42), (-6, hy - 76), (2, hy - 44), (10, hy - 72), (14, hy - 40), (22, hy - 58), (18, hy - 22)])
        c.drawPath(crown, paint(C(S.GOLD_LEAF, a)))
        c.drawPath(crown, paint(C(ink, a), stroke=1.8))
        c.drawCircle(-6, hy - 34, 4, paint(C((140, 80, 170), a)))
    elif kind == 'brother':
        cap = smooth_path([(-18, hy - 16), (-14, hy - 30), (8, hy - 32), (18, hy - 20)])
        c.drawPath(cap, paint(C((30, 24, 22), a)))
        c.drawRect(R(-6, hy - 66, 4, hy - 30), paint(C((30, 24, 22), a)))
        c.drawRect(R(-14, hy - 52, 12, hy - 46), paint(C((30, 24, 22), a)))
        c.drawPath(cap, paint(C(ink, a), stroke=1.6))


def figure(c, x, y, s, kind, t=0.0, arm=0.0, a=255, face=1, rod=True, flip_u=1.0, bob=True, blade=False, lean=0.0,
           halo=None, halo_a=1.0, clip_floor=None):
    """kind: opal / empress / brother / slave. arm: Winkel des vorderen Arms in Grad (0 = hängend, -90 = nach vorn oben).
    flip_u: -1..1 Breitenfaktor für das Umdrehen der Papierfigur. halo: (col, inner) für den Goldnimbus."""
    if a <= 0:
        return
    st = ROBES[kind]
    ink = S.SEPIA_INK
    b = 3 * math.sin(t * 2.2 + x * 0.01) if bob else 0.0
    c.save()
    if clip_floor is not None:
        c.clipRect(R(-5000, -5000, 5000, clip_floor), skia.ClipOp.kIntersect, True)
    c.translate(x, y + b)
    c.rotate(lean)
    c.scale(s * face * flip_u, s)
    # Stab des Puppenspielers (vom Rücken nach unten)
    if rod:
        c.drawLine(-6, -200, -20, 420, paint(C((40, 28, 20), int(a * 0.55)), stroke=3.2))
    # Nimbus hinter dem Kopf
    if halo:
        col, inner = halo
        S.nimbus(c, 2, -360 if kind != 'slave' else -272, 58, a=int(a * halo_a), col=col, inner=inner, t=t)
    robe = _robe_path(kind)
    sh = skia.Path(robe)
    sh.offset(6, 6)
    c.drawPath(sh, blur_paint(rgb(20, 12, 6, int(a * 0.35)), 4))
    g = skia.GradientShader.MakeLinear([P(-60, 0), P(60, 0)], [C(st['dark'], a), C(st['fill'], a), C(st['sheen'], a)], [0, 0.6, 1])
    c.drawPath(robe, skia.Paint(AntiAlias=True, Shader=g))
    # Gravur: Schraffur am Rücken + Faltenlinien
    c.save()
    c.clipPath(robe, doAntiAlias=True)
    for k in range(-140, 60, 7):
        c.drawLine(-120, k - 300, k + 40, -300 + k + 160, paint(C(ink, int(a * 0.22)), stroke=1.0))
    for k, (x0, x1) in enumerate(((-30, -70), (-10, -30), (10, 20), (26, 50))):
        c.drawPath(smooth_path([(x0 * 0.4, -230), (x0 * 0.7, -150), (x1, 0)], closed=False), paint(C(ink, int(a * 0.55)), stroke=1.6))
    # Saumborte, Gürtel, Kragen
    c.drawPath(smooth_path([(-120, -14), (0, -10), (80, -14)], closed=False), paint(C(S.GOLD_LEAF, int(a * 0.8)), stroke=5))
    if kind != 'slave':
        c.drawPath(smooth_path([(-60, -236), (0, -230), (60, -238)], closed=False), paint(C(S.GOLD_DK, int(a * 0.9)), stroke=7))
        c.drawPath(smooth_path([(-60, -236), (0, -230), (60, -238)], closed=False), paint(C(S.GOLD_LEAF, a), stroke=3))
        c.drawPath(smooth_path([(-26, -322), (-4, -306), (22, -318)], closed=False), paint(C(S.GOLD_LEAF, a), stroke=5))
    c.restore()
    c.drawPath(robe, paint(C(ink, a), stroke=2.4))
    _head(c, kind, a, ink)
    # vorderer Arm mit weitem Ärmel, Drehpunkt an der Schulter
    sx, sy = (10, -306) if kind != 'slave' else (8, -232)
    with saved(c):
        c.translate(sx, sy)
        c.rotate(arm)
        L = 130 if kind != 'slave' else 100
        sleeve = smooth_path([(-14, -6), (16, -6), (26, L * 0.6), (40, L), (-6, L + 14), (-20, L * 0.7)])
        c.drawPath(sleeve, paint(C(st['fill'], a)))
        c.save()
        c.clipPath(sleeve, doAntiAlias=True)
        for k in range(-40, 60, 7):
            c.drawLine(-30, k, 40, k + 30, paint(C(ink, int(a * 0.2)), stroke=1))
        c.restore()
        c.drawPath(sleeve, paint(C(ink, a), stroke=2.2))
        c.drawCircle(14, L + 10, 9, paint(C((214, 190, 160) if kind != 'slave' else (150, 120, 96), a)))
        c.drawCircle(14, L + 10, 9, paint(C(ink, a), stroke=1.6))
        if blade:
            c.drawPath(poly([(10, L + 6), (18, L + 6), (16, L + 90), (13, L + 98), (10, L + 90)]), paint(C((200, 200, 196), a)))
            c.drawPath(poly([(10, L + 6), (18, L + 6), (16, L + 90), (13, L + 98), (10, L + 90)]), paint(C(ink, a), stroke=1.4))
            c.drawRect(R(4, L + 2, 24, L + 8), paint(C(S.GOLD_DK, a)))
        if rod:
            c.drawLine(14, L + 10, 30, L + 420, paint(C((40, 28, 20), int(a * 0.5)), stroke=2.4))
        # Gelenkstift
        c.drawCircle(0, 0, 5, paint(C(S.GOLD_LEAF, a)))
        c.drawCircle(0, 0, 5, paint(C(ink, a), stroke=1.4))
    c.restore()


def skeleton(c, x, y, s, t, a=255, lift=1.0):
    """Marionette: Knochenfigur an Fäden, hängt schlaff und zuckt"""
    if a <= 0:
        return
    ink = S.SEPIA_INK
    bone = (222, 210, 182)
    bdk = (170, 152, 120)
    jit = math.sin(t * 7.0) * 6 * (1 - lift * 0.5)

    def bonel(p, q, w):
        c.drawLine(p[0], p[1], q[0], q[1], paint(C(ink, a), stroke=w + 3))
        c.drawLine(p[0], p[1], q[0], q[1], paint(C(bone, a), stroke=w))
        for e in (p, q):
            c.drawCircle(e[0], e[1], w * 0.75, paint(C(bone, a)))
            c.drawCircle(e[0], e[1], w * 0.75, paint(C(ink, a), stroke=1.4))
    with saved(c):
        c.translate(x, y)
        c.scale(s, s)
        for (fx, fy) in ((-40, -250), (40, -250), (0, -330), (-60, -170), (60, -170)):
            c.drawLine(fx, fy, fx * 1.4, -1500, paint(C((40, 30, 24), int(a * 0.6)), stroke=1.4))
        c.rotate(jit * 0.6)
        # Beine, Arme
        for side in (-1, 1):
            sw = math.sin(t * 5 + side) * 10
            bonel((side * 14, -150), (side * (18 + sw * 0.4), -76), 8)
            bonel((side * (18 + sw * 0.4), -76), (side * (14 + sw * 0.8), -4), 7)
            bonel((side * 30, -300), (side * (46 + sw * 0.3), -236), 6)
            bonel((side * (46 + sw * 0.3), -236), (side * (60 + sw), -170), 5)
        # Wirbelsäule, Rippen
        c.drawLine(0, -322, 0, -160, paint(C(ink, a), stroke=9))
        c.drawLine(0, -322, 0, -160, paint(C(bone, a), stroke=6))
        for k in range(6):
            yy = -302 + k * 20
            w = 42 - k * 4
            for sd in (-1, 1):
                rib = smooth_path([(0, yy), (sd * w, yy + 6), (sd * (w + 4), yy + 18), (sd * (w - 6), yy + 24)], closed=False)
                c.drawPath(rib, paint(C(ink, a), stroke=7))
                c.drawPath(rib, paint(C(bone, a), stroke=4))
        pel = smooth_path([(-30, -168), (30, -168), (22, -142), (0, -134), (-22, -142)])
        c.drawPath(pel, paint(C(bone, a)))
        c.drawPath(pel, paint(C(ink, a), stroke=2))
        # Schädel mit Kiefer
        sk = smooth_path([(-24, -344), (-24, -372), (-6, -388), (16, -386), (28, -368), (26, -346), (14, -334), (-12, -334)])
        c.drawPath(sk, paint(C(bone, a)))
        c.save()
        c.clipPath(sk, doAntiAlias=True)
        for k in range(-20, 40, 5):
            c.drawLine(-30, -330 - k, 10, -370 - k, paint(C(bdk, a), stroke=1))
        c.restore()
        c.drawPath(sk, paint(C(ink, a), stroke=2))
        c.drawPath(smooth_path([(-10, -364), (-2, -370), (4, -362), (-4, -354)]), paint(C(ink, a)))
        c.drawPath(smooth_path([(10, -364), (18, -368), (22, -360), (14, -354)]), paint(C(ink, a)))
        c.drawPath(poly([(6, -350), (10, -342), (2, -342)]), paint(C(ink, a)))
        jaw = smooth_path([(-12, -334), (16, -334), (12, -320 + 4 * math.sin(t * 9)), (-8, -320 + 4 * math.sin(t * 9))])
        c.drawPath(jaw, paint(C(bone, a)))
        c.drawPath(jaw, paint(C(ink, a), stroke=1.6))


def slave(c, x, y, s, t, a=255, lean=0.0, step=0.0, pull=0.0):
    """vorgebeugte Gestalt im Profil (nach rechts), Halsring, Arme nach vorn; Füße bei (0,0), Höhe ~200*s.
    step: Gehbewegung, pull: 0..1 Arme zum Seil gestreckt"""
    if a <= 0:
        return
    ink = S.SEPIA_INK
    body = (70, 52, 40)
    skin = (150, 112, 84)
    rim = (236, 206, 160)
    sw = math.sin(step * math.pi * 2) * 16
    with saved(c):
        c.translate(x, y)
        c.rotate(lean)
        c.scale(s, s)
        # Beine
        for k, ph in ((0, 1), (1, -1)):
            col = mix(body, (24, 18, 14), 0.45) if k == 0 else body
            fx = 14 * ph + sw * ph
            leg = smooth_path([(-12, -92), (6, -92), (fx + 6, -40), (fx + 8, -6), (fx + 24, -2), (fx + 24, 4), (fx - 8, 4), (fx - 8, -38)])
            c.drawPath(leg, paint(C(col, a)))
            c.drawPath(leg, paint(C(ink, a), stroke=1.6))
        # Tunika, Oberkörper vorgebeugt
        tun = smooth_path([(-22, -84), (-26, -130), (-14, -170), (8, -186), (28, -178), (32, -150), (24, -112), (20, -80), (-2, -72)])
        c.drawPath(tun, paint(C(body, a)))
        c.save()
        c.clipPath(tun, doAntiAlias=True)
        for k in range(-80, 60, 6):
            c.drawLine(-40, -190 + k, 40, -140 + k, paint(C(ink, int(a * 0.28)), stroke=1))
        c.restore()
        c.drawPath(smooth_path([(-26, -130), (-14, -170), (8, -186)], closed=False), paint(C(rim, int(a * 0.85)), stroke=2.4))
        c.drawPath(tun, paint(C(ink, a), stroke=1.8))
        c.drawLine(-22, -100, 22, -96, paint(C((40, 30, 22), a), stroke=4))
        # Kopf gesenkt, Profil mit Nase
        hd = smooth_path([(18, -200), (30, -212), (44, -208), (50, -196), (56, -190), (50, -186), (50, -178), (40, -170), (26, -174), (18, -186)])
        c.drawPath(smooth_path([(16, -198), (28, -216), (42, -214), (34, -204), (22, -192)]), paint(rgb(30, 22, 18, a)))
        c.drawPath(hd, paint(C(skin, a)))
        c.drawPath(hd, paint(C(ink, a), stroke=1.6))
        c.drawPath(smooth_path([(20, -204), (30, -216), (44, -214), (40, -206), (28, -200)]), paint(rgb(30, 22, 18, a)))
        c.drawCircle(42, -194, 1.6, paint(C(ink, a)))
        # Halsring
        c.drawOval(R(14, -182, 34, -170), paint(rgb(180, 170, 160, a), stroke=3.4))
        # Arme nach vorn (zwei, hinterer dunkler)
        for k, dy in ((0, 6), (1, 0)):
            ex = 70 + 16 * pull
            col = mix(body, (24, 18, 14), 0.4) if k == 0 else mix(body, (100, 80, 64), 0.3)
            arm = smooth_path([(10, -168 + dy), (ex - 10, -150 - 8 * pull + dy), (ex + 4, -146 - 8 * pull + dy), (ex - 6, -136 - 8 * pull + dy), (8, -150 + dy)])
            c.drawPath(arm, paint(C(col, a)))
            c.drawPath(arm, paint(C(ink, a), stroke=1.4))
            c.drawCircle(ex + 2, -141 - 8 * pull + dy, 6.5, paint(C(skin, a)))
            c.drawCircle(ex + 2, -141 - 8 * pull + dy, 6.5, paint(C(ink, a), stroke=1.2))


def slave_hand_local(pull):
    return (72 + 16 * pull, -141 - 8 * pull)
