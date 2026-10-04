"""Testszene Kapitel 4 (Papiertheater): 04-7 + Zitat Q4 (der Blutstein-Kaiser) + 04-8.
python3 scene4.py still 1.0,5.2,...      -> stills/s4_XX.png
python3 scene4.py range i0 i1 out.mp4     -> Bilder [i0, i1)
"""
import math, os, sys, json
import numpy as np
import cv2
import skia
from PIL import Image
sys.path.insert(0, '/home/claude/main/ch1')
sys.path.insert(0, '/home/claude/main/ch4')
from lib import *
import book as B
from book import SP, PT, PB, PW, RP, LP, RPATH, LPATH
import ch1 as C1
import world as WD
import pages as PG
import style as S
import puppets as PU

D = '/home/claude/main/ch4/'
CUT = D + 'cut/'
IMG = '/home/claude/tides-of-magic/images/'
SCALE = float(os.environ.get('SCALE', '1.0'))
OW, OH = int(round(W * SCALE)), int(round(H * SCALE))

# ------------------------------------------------------------------ Zeitplan (Sekunden im Clip)
V47 = 1.2            # 04-7  (5.4 s)
VQ = 9.2             # Q4    (24.5 s)
V48 = 36.6           # 04-8  (19.0 s)
T_END = 58.6
T_FLIP1 = (1.9, 2.75)
T_ZOOM_IN = (4.3, 7.0)
T_X_IN = (6.55, 7.0)
T_X_OUT = (34.95, 35.45)
T_ZOOM_OUT = (34.95, 36.3)
T_FLIP2 = (36.15, 36.95)


def r_(t):
    return t - VQ


# ------------------------------------------------------------------ Bühne: Gemälde-Raum -> Bühnen-Raum
PK = 1.03
POX, POY = 960 - 714 * PK / 2, 70.0
WIN = (606, 70, 1300, 1010)
FBW = 64
FLOOR = 742                     # Bodenlinie der Vorgeschichte
CAM0 = (960, 540, 0.88)         # neutrale Theater-Kamera
BOOK_F, BOOK_C = 0.55, (1285, 520)


def pm(px, py):
    return (POX + (px - 58) * PK, POY + (py - 52) * PK)


def paint_space(c):
    c.translate(POX, POY)
    c.scale(PK, PK)
    c.translate(-58, -52)


# ------------------------------------------------------------------ Ebenen laden (Farbe + Radierung + Papierkante + Schatten)
META = json.load(open(CUT + 'meta.json'))
ORIG = np.array(Image.open(IMG + '4-E.png').convert('RGB'))
ENG_FULL = S.engrave(ORIG)
BD = np.array(Image.open(CUT + 'backdrop2.png').convert('RGB'))
BD_IMG = to_image(BD)
BD_ENG = to_image(S.engrave(BD))
ENG_PAINT = to_image(ENG_FULL)


def _layer(k):
    a = np.array(Image.open(CUT + k + '.png').convert('RGBA'))
    x0, y0, x1, y1 = META[k]
    al = a[..., 3].astype(np.float32) / 255
    eng = np.dstack([ENG_FULL[y0:y1, x0:x1], a[..., 3]])
    pad = 14
    big = np.pad(al, pad)
    ring = cv2.dilate((big > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))).astype(np.float32)
    ring = np.clip(ring - big, 0, 1)
    edge = np.dstack([np.full(big.shape + (3,), (236, 222, 190), np.float32), ring[..., None] * 230])
    sh = cv2.GaussianBlur(big, (0, 0), 5)
    shadow = np.dstack([np.full(big.shape + (3,), (20, 12, 6), np.float32), sh[..., None] * 150])
    return dict(col=to_image(a), eng=to_image(eng), edge=to_image(edge), sh=to_image(shadow), box=(x0, y0, x1, y1), pad=pad)


LAY = {k: _layer(k) for k in ('statue', 'emperor', 'arm', 'stone', 'tiger')}
PIV_STATUE = (215, 612)
PIV_ARM = (497, 492)
STONE_C = (588, 494)
EMP_HEAD = (466, 466)


def draw_layer(c, k, sep, a=1.0, dx=0.0, dy=0.0, rot=0.0, pivot=None, shadow=True):
    L = LAY[k]
    x0, y0 = L['box'][:2]
    pad = L['pad']
    with saved(c):
        c.translate(dx, dy)
        if rot:
            c.translate(*pivot)
            c.rotate(rot)
            c.translate(-pivot[0], -pivot[1])
        pp = skia.Paint(AntiAlias=True)
        if shadow:
            pp.setAlphaf(a * 0.8)
            c.drawImage(L['sh'], x0 - pad + 7, y0 - pad + 9, SAMP, pp)
        pp.setAlphaf(a)
        c.drawImage(L['edge'], x0 - pad, y0 - pad, SAMP, pp)
        if sep < 1:
            c.drawImage(L['col'], x0, y0, SAMP, pp)
        if sep > 0:
            pe = skia.Paint(AntiAlias=True)
            pe.setAlphaf(a * sep)
            c.drawImage(L['eng'], x0, y0, SAMP, pe)


def small_engraving(path, size, crop=None):
    im = Image.open(path).convert('RGB')
    if crop:
        im = im.crop(crop)
    im = im.resize(size, Image.LANCZOS)
    return to_image(S.engrave(np.array(im), hatch=5))


ENG_4A = small_engraving(IMG + '4-A.png', (360, 360), (300, 30, 860, 560))
ENG_4B = small_engraving(IMG + '4-B.png', (360, 360), (260, 30, 800, 560))
ENG_4C = small_engraving(IMG + '4-C.png', (360, 360), (120, 180, 720, 780))
ENG_4D = small_engraving(IMG + '4-D.png', (360, 360), (150, 60, 700, 610))
ENG_4E = small_engraving(IMG + '4-E-b.png', (360, 360), (150, 150, 690, 690))
ENG_4C_PL = small_engraving(IMG + '4-C.png', (300, 372), (60, 50, 765, 920))
ENG_4D_PL = small_engraving(IMG + '4-D.png', (300, 372), (60, 50, 765, 920))


# ------------------------------------------------------------------ Farbfilter: Sepia-Anteil
def sepia_filter(u):
    i = np.array([[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0]], np.float32)
    ink = np.array(S.SEPIA_INK, np.float32) / 255
    pap = np.array(S.SEPIA_PAPER, np.float32) / 255
    s = np.zeros((4, 5), np.float32)
    for ch in range(3):
        k = pap[ch] - ink[ch]
        s[ch, :3] = [0.3 * k, 0.59 * k, 0.11 * k]
        s[ch, 4] = ink[ch]
    s[3, 3] = 1
    m = i * (1 - u) + s * u
    return skia.ColorFilters.Matrix(list(m.flatten()))


# ------------------------------------------------------------------ Umgebung des Theaters (Buchseite mit Radierungen)
_rs = np.random.default_rng(21)
SUR_STARS = [(_rs.uniform(-120, 2040), _rs.uniform(-60, 1140), _rs.uniform(7, 16), _rs.uniform(0, 6.28)) for _ in range(40)]
SUR_STARS = [s for s in SUR_STARS if not (480 < s[0] < 1430 and -10 < s[1] < 1090)]
PARCH_BIG = parchment(2400, 1500, 31, base=S.SEPIA_PAPER)


def surround(c, t, pop, red=0.0):
    """Hintergrund um den Rahmen: Papier, Strahlenkranz, Sterne, Bänder (hinten)"""
    c.drawImage(PARCH_BIG, -240, -210)
    # Strahlenkranz hinter dem Rahmen (Radierung)
    cx, cy = 960, 300
    for k in range(120):
        ang = math.pi + k * math.pi / 119 * 1.0
        ang = -math.pi + k * 2 * math.pi / 120
        r0, r1 = 520, 1500
        c.drawLine(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, cx + math.cos(ang) * r1, cy + math.sin(ang) * r1,
                   paint(C(S.SEPIA_MID, 60 if k % 2 else 34), stroke=1.4))
    c.drawCircle(cx, cy, 500, paint(C(S.SEPIA_MID, 90), stroke=3))
    c.drawCircle(cx, cy, 520, paint(C(S.SEPIA_MID, 60), stroke=1.4))
    for k in range(24):
        ang = k * math.pi * 2 / 24 + t * 0.02
        S.star8(c, cx + math.cos(ang) * 510, cy + math.sin(ang) * 510, 9, a=200, rot=ang)
    if red > 0:
        g = skia.GradientShader.MakeRadial(P(960, 560), 1100, [rgb(170, 40, 24, int(110 * red)), rgb(120, 20, 10, 0)])
        c.drawRect(R(-300, -300, 2300, 1400), skia.Paint(Shader=g))
    # Sterne funkeln
    for (x, y, r, ph) in SUR_STARS:
        tw = 0.6 + 0.4 * math.sin(t * 2.1 + ph)
        S.star8(c, x, y, r * pop * (0.85 + 0.15 * tw), a=int(230 * pop), rot=ph, glow=0.5 * tw)
    # Bänder hinter dem Rahmen
    if pop > 0:
        a = int(255 * pop)
        S.ribbon(c, [(-300 + 46 * i, 330 - 90 * math.sin(i * 0.33) - 9 * i) for i in range(22)], w=34, t=t, a=a, ph=0.3, wave=7)
        S.ribbon(c, [(1360 + 46 * i, 900 - 110 * math.sin(i * 0.3) - 12 * i) for i in range(20)], w=34, t=t, a=a, ph=2.1, wave=7)


def fore_clouds(c, t, pop):
    """Schnörkelwolken als Pop-up-Kulissen vor dem Rahmen"""
    specs = [(330, 1120, 520, 170, False, 1, 0.0), (1600, 1130, 520, 170, True, 2, 0.12), (170, 720, 360, 120, False, 3, 0.22),
             (1760, 660, 360, 120, True, 4, 0.3), (250, 260, 300, 100, False, 5, 0.4), (1690, 230, 300, 100, True, 6, 0.46)]
    for (x, y, w, h, fl, sd, dl) in specs:
        u = clamp((pop - dl) / max(0.01, 1 - dl)) if pop < 1 else 1.0
        if u <= 0:
            continue
        sway = 4 * math.sin(t * 0.8 + sd)
        with folded(c, x, y, popout(u) if u < 1 else 1.0):
            S.cloud_scroll(c, x + sway, y, w, h, flip=fl, seed=sd, t=t)


# ------------------------------------------------------------------ Vorgeschichte: das Bilderbuch-Blatt (Radierung) mit Stabpuppen
_rsc = np.random.default_rng(8)
SCRIM_STARS = [(_rsc.uniform(640, 1270), _rsc.uniform(110, 560), _rsc.uniform(6, 12), _rsc.uniform(0, 6)) for _ in range(14)]


def scrim_plate(c, t):
    x0, y0, x1, y1 = WIN
    c.drawRect(R(x0, y0, x1, y1), paint(C(S.SEPIA_PAPER)))
    with saved(c):
        c.clipRect(R(x0, y0, x1, y1))
        c.drawImage(B.PARCH2, 0, 0, SAMP, skia.Paint(Alphaf=0.35))
        cx, cy = 953, 330
        for k in range(90):
            ang = -math.pi + k * math.pi / 89
            c.drawLine(cx + math.cos(ang) * 180, cy + math.sin(ang) * 180, cx + math.cos(ang) * 620, cy + math.sin(ang) * 620,
                       paint(C(S.SEPIA_MID, 120 if k % 2 else 70), stroke=1.4))
        c.drawCircle(cx, cy, 168, paint(C(S.SEPIA_MID, 140), stroke=3))
        c.drawCircle(cx, cy, 150, paint(C(S.SEPIA_MID, 90), stroke=1.4))
        for k in range(12):
            ang = -math.pi + (k + 0.5) * math.pi / 12
            S.star8(c, cx + math.cos(ang) * 160, cy + math.sin(ang) * 160, 8, a=210, rot=ang)
        for (x, y, r, ph) in SCRIM_STARS:
            S.star8(c, x, y, r, a=int(170 + 60 * math.sin(t * 2 + ph)), rot=ph)
        # gravierter Boden mit Fluchtlinien
        for k in range(14):
            yy = FLOOR + (k ** 1.6) * 6
            c.drawLine(x0, yy, x1, yy, paint(C(S.SEPIA_INK, 70), stroke=1.2))
        for k in range(-8, 9):
            c.drawLine(cx + k * 30, FLOOR, cx + k * 190, y1, paint(C(S.SEPIA_INK, 45), stroke=1.0))
        c.drawRect(R(x0, FLOOR, x1, y1), paint(C(S.SEPIA_MID, 40)))
        # Palastsilhouette am Horizont (gravierte Dächer)
        for k, (px, w, h) in enumerate(((700, 150, 90), (830, 120, 130), (1080, 140, 120), (1210, 130, 80))):
            yb = FLOOR
            for lvl in range(3):
                ww = w * (1 - lvl * 0.22)
                yy = yb - h * lvl / 3 - 24
                roof = smooth_path([(px - ww / 2 - 18, yy + 8), (px - ww / 2, yy), (px, yy - 18), (px + ww / 2, yy), (px + ww / 2 + 18, yy + 8),
                                    (px + ww / 2 - 6, yy + 4), (px, yy - 8), (px - ww / 2 + 6, yy + 4)])
                c.drawRect(R(px - ww / 2 + 10, yy, px + ww / 2 - 10, yy + 22 if lvl == 0 else yy + 14), paint(C(S.SEPIA_MID, 120)))
                c.drawPath(roof, paint(C(S.SEPIA_MID, 170)))
                c.drawPath(roof, paint(C(S.SEPIA_INK, 150), stroke=1.4))
        # Wolken links und rechts
        S.cloud_scroll(c, 700, 560, 300, 110, seed=11, t=t)
        S.cloud_scroll(c, 1210, 520, 280, 110, flip=True, seed=12, t=t)
        # Zierrahmen innen
        c.drawRect(R(x0 + 18, y0 + 18, x1 - 18, y1 - 18), paint(C(S.SEPIA_INK, 180), stroke=2))
        c.drawRect(R(x0 + 26, y0 + 26, x1 - 26, y1 - 26), paint(C(S.SEPIA_INK, 120), stroke=1))
        for (cx_, cy_, sx, sy) in ((x0 + 26, y0 + 26, 1, 1), (x1 - 26, y0 + 26, -1, 1), (x0 + 26, y1 - 26, 1, -1), (x1 - 26, y1 - 26, -1, -1)):
            for j in range(3):
                pts = []
                for i in range(26):
                    u = i / 25
                    ang = u * math.pi * 1.7
                    rr = (70 - j * 18) * (1 - 0.7 * u)
                    pts.append((cx_ + sx * (rr * math.cos(ang) * 0.9 + 12 + j * 22), cy_ + sy * (rr * math.sin(ang) * 0.9 + 12 + j * 6)))
                c.drawPath(smooth_path(pts, closed=False), paint(C(S.SEPIA_INK, 160), stroke=1.8))


def blood_blot(c, x, y, r, a=255, seed=3):
    if r <= 0:
        return
    c.drawPath(wobbly(x, y, r * 1.12, r * 0.78, seed, amp=0.22), blur_paint(C(S.BLOOD, int(a * 0.35)), 8))
    c.drawPath(wobbly(x, y, r, r * 0.7, seed, amp=0.22), paint(C(S.BLOOD, int(a * 0.85))))
    c.drawPath(wobbly(x, y, r * 0.55, r * 0.4, seed + 1, amp=0.3), paint(rgb(96, 12, 10, int(a * 0.7))))
    rng = np.random.default_rng(seed)
    for k in range(9):
        ang = rng.uniform(0, 6.28)
        d = r * rng.uniform(1.05, 1.6)
        c.drawCircle(x + math.cos(ang) * d, y + math.sin(ang) * d * 0.7, r * rng.uniform(0.05, 0.14), paint(C(S.BLOOD, int(a * 0.85))))


BURN_C = (830, 730)


def burn_r(r):
    if r < 9.9:
        return 0.0
    return 1250 * ease_in(clamp((r - 9.9) / 1.6)) + 90 * ease_out(clamp((r - 9.9) / 0.5))


def hole_path(cx, cy, rad, t):
    n = 56
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = rad * (1 + 0.12 * math.sin(3 * a + 0.7 + 0.4 * t) + 0.07 * math.sin(5 * a + 2.1) + 0.05 * math.sin(11 * a + 1.3 + t))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 0.9))
    return smooth_path(pts)


def backstory(c, t):
    """das Bilderbuch-Blatt mit den Puppen; brennt ab r=9.9 von der Blutstelle aus weg"""
    r = r_(t)
    drop = clamp((t - 8.35) / 0.75)
    if drop <= 0:
        return
    rb = burn_r(r)
    if rb > 1400:
        return
    oy = -1000 * (1 - popout(drop)) if drop < 1 else 0.0
    c.saveLayer(R(*WIN), None)
    with saved(c):
        c.translate(0, oy)
        # Seile, an denen das Blatt hängt
        c.drawLine(700, -400, 700, WIN[1] + 4, paint(C(S.SEPIA_INK, 200), stroke=2))
        c.drawLine(1206, -400, 1206, WIN[1] + 4, paint(C(S.SEPIA_INK, 200), stroke=2))
        scrim_plate(c, t)
        fl = FLOOR + 3
        # Opal-Kaiser: steigt aus dem Bodenschlitz, geht wieder hinab
        up = ease_out(clamp((r - 0.1) / 0.6))
        dn = ease_in(clamp((r - 2.1) / 0.9))
        if up > 0 and dn < 1:
            PU.figure(c, 900, FLOOR + 360 * (1 - up) + 380 * dn, 0.82, 'opal', t=t, lean=-8 * dn, arm=-18,
                      halo=((236, 230, 214), (205, 218, 228)), clip_floor=fl)
        # Kaiserin
        ein = ease(clamp((r - 2.6) / 1.1))
        fall = clamp((r - 6.7) / 0.7)
        if ein > 0:
            ha = popv(t, VQ + 3.3, 0.5)
            ex = lerp(500, 860, ein)
            if fall < 1:
                PU.figure(c, ex, FLOOR + 160 * ease_in(fall), 0.82, 'empress', t=t, lean=-100 * ease_in(fall), arm=-14 - 20 * fall,
                          halo=(S.GOLD_LEAF, (150, 100, 170)) if r < 6.8 else None, halo_a=ha, clip_floor=fl)
            if r >= 6.8:
                u = clamp((r - 6.8) / 1.4)
                hx, hy = ex - 36 - 180 * u, FLOOR - 296 + 340 * ease_in(u)
                with saved(c):
                    c.clipRect(R(-5000, -5000, 5000, fl))
                    S.nimbus(c, hx, hy, 47, a=int(255 * (1 - u * 0.6)), col=S.GOLD_LEAF, inner=(150, 100, 170), t=t, crack=clamp((r - 6.9) / 0.4))
        # Blutfleck
        if r > 7.2:
            g = ease_out(clamp((r - 7.2) / 0.8))
            blood_blot(c, BURN_C[0], BURN_C[1], 60 * g + 50 * clamp((r - 8.0) / 2.0))
        # Bruder
        bin_ = ease(clamp((r - 5.3) / 1.0))
        if bin_ > 0:
            bx = lerp(1420, 1060, bin_) - 50 * ease(clamp((r - 8.0) / 0.9))
            arm = 0.0
            if r > 6.25:
                arm = -125 * ease_out(clamp((r - 6.25) / 0.2))
            if r > 6.5:
                arm = lerp(-125, -35, ease(clamp((r - 6.5) / 0.35)))
            if r > 8.0:
                arm = lerp(-35, 0, ease(clamp((r - 8.0) / 0.6)))
            if r > 9.35:
                arm = lerp(0, -140, ease_out(clamp((r - 9.35) / 0.6)))
            tu = clamp((r - 9.0) / 0.4)
            flip = math.cos(math.pi * ease(tu))
            ha = ramp(r, 9.6, 10.3)
            PU.figure(c, bx, FLOOR, 0.82, 'brother', t=t, arm=arm, face=-1, flip_u=flip if abs(flip) > 0.04 else 0.04,
                      blade=6.2 < r < 8.3, halo=(S.BLOOD, (90, 12, 10)) if ha > 0 else None, halo_a=ha, clip_floor=fl)
        # Bodenleiste mit Schlitz
        c.drawRect(R(WIN[0], FLOOR + 2, WIN[2], FLOOR + 8), paint(C(S.WOOD_DK, 220)))
    # Brandloch: Rand verkohlt, Mitte frei
    if rb > 0:
        hp = hole_path(BURN_C[0], BURN_C[1], rb, t)
        big = hole_path(BURN_C[0], BURN_C[1], rb + 46, t)
        c.drawPath(big, skia.Paint(AntiAlias=True, Color=rgb(40, 22, 10, 230), BlendMode=skia.BlendMode.kSrcATop,
                                   MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16)))
        c.drawPath(hp, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kClear))
    c.restore()
    if rb > 0:
        with saved(c):
            c.clipRect(R(*WIN))
            hp = hole_path(BURN_C[0], BURN_C[1], rb, t)
            pg = blur_paint(rgb(255, 140, 50, 230), 7, stroke=9)
            pg.setBlendMode(skia.BlendMode.kPlus)
            c.drawPath(hp, pg)
            c.drawPath(hp, paint(rgb(255, 200, 120, 200), stroke=2.4))
            EMB_BURN.draw(c, t, strength=clamp(1 - (r - 11.2) / 1.0), col=(255, 160, 70))


EMB_BURN = Embers(90, 12, 640, 1280, 1000, rise=(90, 260), life=(1.2, 2.6), r=(1.5, 3.4))


# ------------------------------------------------------------------ die farbige Bühne (ab dem Brand)
SMOKE_L = WD.Smoke(18, 41, *pm(410, 612), spread=10, rise=40, life=6.0, size=(10, 30), drift=18)
SMOKE_R = WD.Smoke(18, 42, *pm(640, 642), spread=10, rise=40, life=6.0, size=(10, 30), drift=18)
SLAVES = [(651, 0.0), (729, 0.15), (850, 0.3), (905, 0.45)]
SLAVE_Y = pm(0, 640)[1]
ROPE_T = [(210, 350), (240, 400), (320, 420), (345, 410)]


def rot_pt(p, piv, deg):
    a = math.radians(deg)
    dx, dy = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + dx * math.cos(a) - dy * math.sin(a), piv[1] + dx * math.sin(a) + dy * math.cos(a))


def slave_hand(x, y, s, arm_deg, lean):
    a = math.radians(arm_deg)
    rx, ry = 14 * math.cos(a) - 110 * math.sin(a), 14 * math.sin(a) + 110 * math.cos(a)
    px, py = 8 + rx, -232 + ry
    l = math.radians(lean)
    return (x + s * (px * math.cos(l) - py * math.sin(l)), y + s * (px * math.sin(l) + py * math.cos(l)))


def stage_state(t):
    r = r_(t)
    st = {}
    st['fall'] = ease_in(clamp((r - 21.3) / 1.0))
    st['rot'] = 7 * st['fall'] - 2.5 * math.sin(clamp((r - 20.95) / 0.35) * math.pi) * (r < 21.3)
    st['glow'] = 1 - ramp(r, 21.3, 22.5)
    st['stone_y'] = None
    if r >= 22.6:
        u = clamp((r - 22.6) / 0.9)
        st['stone_y'] = -680 * (1 - ease_in(u))
    st['landed'] = r >= 23.5
    st['arm'] = 45 * (1 - ease(clamp((r - 23.6) / 0.7)))
    st['tiger_dx'] = 170 * (1 - ease(clamp((r - 17.7) / 0.9)))
    st['nim'] = ramp(r, 10.4, 11.4)
    st['red'] = ramp(r, 11.0, 12.4) * 0.6 + 0.25 * win(r, 19.7, 20.8, 0.3, 0.6) + 0.15 * ramp(r, 23.5, 24.0)
    st['circle'] = clamp((r - 14.0) / 1.2)
    st['skel'] = ease_out(clamp((r - 15.2) / 0.7)) * (1 - ease_in(clamp((r - 19.9) / 0.7)))
    st['slaves'] = [ease(clamp((r - 15.9 - d) / 1.1)) for (_, d) in SLAVES]
    st['ropes'] = clamp((r - 20.9) / 0.25)
    st['lean'] = -16 * ease(clamp((r - 21.0) / 0.4))
    if t < 9.05:            # vor dem Vorhang: genau das Gemälde
        st.update(arm=0.0, tiger_dx=0.0, stone_y=0.0, landed=True, nim=0.0, red=0.0, circle=0.0, skel=0.0,
                  slaves=[0.0] * 4, ropes=0.0)
    return st


def stage_color(c, t, sep, cam):
    """Inhalt des Bühnenfensters (ohne Rahmen); cam=(cx,cy,z) für Parallaxe"""
    r = r_(t)
    st = stage_state(t)
    px = (cam[0] - 960) * 0.05
    with saved(c):
        c.translate(px, 0)
        with saved(c):
            paint_space(c)
            pp = skia.Paint(AntiAlias=True)
            c.drawImage(BD_IMG, 0, 0, SAMP, pp)
            if sep > 0:
                c.drawImage(BD_ENG, 0, 0, SAMP, skia.Paint(Alphaf=sep))
    # Rauch aus den Räucherschalen
    SMOKE_L.draw(c, t, a=0.5, col=(200, 186, 176) if sep < 1 else (214, 196, 160))
    SMOKE_R.draw(c, t, a=0.5, col=(230, 170, 160) if sep < 1 else (214, 196, 160))
    # roter Zauberkreis auf dem Boden
    if st['circle'] > 0:
        S.rune_circle(c, 860, 846, 250, u=st['circle'], col=(120, 20, 14), squash=0.34, t=t, glow=0.0)
    # Statue (Gold) mit Leuchten
    with saved(c):
        paint_space(c)
        gx, gy = rot_pt((290, 360 + 640 * st['fall']), PIV_STATUE, st['rot'])
        additive_glow(c, gx, gy, 420, (255, 196, 90), 70 * st['glow'] * (0.92 + 0.08 * math.sin(t * 3)))
        if st['fall'] > 0:
            c.save()
            c.clipRect(R(-500, -500, 1500, PIV_STATUE[1] + 8))
        draw_layer(c, 'statue', sep, rot=st['rot'], pivot=PIV_STATUE, dy=640 * st['fall'])
        if st['fall'] > 0:
            c.restore()
    # Staub beim Aufschlag der Statue
    if r > 21.6:
        u = clamp((r - 21.6) / 1.8)
        fx, fy = pm(250, PIV_STATUE[1])
        for k in range(16):
            ang = math.pi + k * math.pi / 15
            x, y = fx + math.cos(ang) * 230 * ease_out(u), fy + math.sin(ang) * 50 * ease_out(u)
            c.drawCircle(x, y, 30 + 50 * u, blur_paint(rgb(170, 150, 130, int(110 * (1 - u))), 16))
    # Skelett-Marionette
    if st['skel'] > 0:
        PU.skeleton(c, 690, FLOOR + 60 + 440 * (1 - st['skel']), 0.72, t, a=255)
    # Sklaven an Ketten, später an den Seilen
    pts_hand = []
    necks = []
    SS = 0.62
    for i, ((sx, _), u) in enumerate(zip(SLAVES, st['slaves'])):
        if u <= 0:
            pts_hand.append(None)
            continue
        x = lerp(380 - i * 60, sx, u)
        ln = st['lean'] * (1 + 0.15 * math.sin(i)) + 3 * math.sin(t * 7 + i) * st['ropes']
        PU.slave(c, x, SLAVE_Y, SS, t, lean=ln, step=(t * 1.4 + i * 0.3) if u < 1 else 0.0, pull=st['ropes'])
        hx, hy = PU.slave_hand_local(st['ropes'])
        l = math.radians(ln)
        pts_hand.append((x + SS * (hx * math.cos(l) - hy * math.sin(l)), SLAVE_Y + SS * (hx * math.sin(l) + hy * math.cos(l))))
        nx_, ny_ = 13, -162
        necks.append((x + SS * (nx_ * math.cos(l) - ny_ * math.sin(l)), SLAVE_Y + SS * (nx_ * math.sin(l) + ny_ * math.cos(l))))
    for a_, b_ in zip(necks[:-1], necks[1:]):
        n = 9
        for j in range(n):
            q = lerp2(a_, b_, (j + 0.5) / n)
            sag = 14 * math.sin(math.pi * (j + 0.5) / n)
            c.drawOval(R(q[0] - 5, q[1] - 3 + sag, q[0] + 5, q[1] + 3 + sag), paint(rgb(190, 180, 168), stroke=2))
    # Seile zur Statue
    if st['ropes'] > 0:
        for h, tp in zip(pts_hand, ROPE_T):
            if h is None:
                continue
            tgt = pm(*rot_pt(tp, PIV_STATUE, st['rot']))
            tgt = (tgt[0], min(tgt[1] + 640 * PK * st['fall'], pm(0, PIV_STATUE[1])[1]))
            e = lerp2(h, tgt, st['ropes'])
            c.drawLine(h[0], h[1], e[0], e[1], paint(rgb(196, 170, 120), stroke=3))
            c.drawLine(h[0], h[1], e[0], e[1], paint(rgb(90, 70, 46), stroke=1))
    # Kaiser mit Blutnimbus, Arm
    with saved(c):
        paint_space(c)
        if st['nim'] > 0:
            S.nimbus(c, EMP_HEAD[0] + 2, EMP_HEAD[1] + 4, 40 * (0.6 + 0.4 * popout(st['nim'])), a=int(255 * st['nim']), col=S.BLOOD, inner=(80, 10, 8), t=t)
        draw_layer(c, 'emperor', sep)
        draw_layer(c, 'arm', sep, rot=st['arm'], pivot=PIV_ARM, shadow=False)
        # Stein: fällt am Draht aus dem Schnürboden
        if st['stone_y'] is not None:
            sy = st['stone_y']
            sx, scy = STONE_C
            if not st['landed']:
                c.drawLine(sx, -400, sx, scy - 50 + sy, paint(rgb(60, 50, 40), stroke=1.6))
                flames(c, sx, scy - 36 + sy, 84, 210, t, seed=9, a=230)
                for k in range(6):
                    S.star8(c, sx + 40 * math.sin(t * 9 + k), scy + sy - 80 - k * 40, 6 + k, a=220 - k * 30, rot=t * 3 + k)
            draw_layer(c, 'stone', sep, dy=sy)
            if st['landed']:
                fl = 1 - clamp((r - 23.5) / 0.5)
                pulse = 0.75 + 0.25 * math.sin(t * 4)
                if sep >= 1:
                    additive_glow(c, sx, scy, 200, (255, 170, 90), 30 * pulse)
                else:
                    additive_glow(c, sx, scy, 260, (255, 60, 30), 90 * pulse + 150 * fl)
        draw_layer(c, 'tiger', sep, dx=st['tiger_dx'])
    # Funkenstern-Explosion beim Aufschlag
    if r > 23.5:
        u = clamp((r - 23.5) / 1.2)
        cx, cy = pm(*STONE_C)
        for k in range(12):
            ang = k * math.pi * 2 / 12 + 0.3
            d = 40 + 220 * ease_out(u)
            S.star8(c, cx + math.cos(ang) * d, cy + math.sin(ang) * d * 0.8, 10 * (1 - u) + 2, a=int(255 * (1 - u)), rot=ang, glow=0.8)
    # Licht: Rot über alles, Dunkel an den Rändern
    if st['red'] > 0:
        c.drawRect(R(*WIN), skia.Paint(Color=rgb(255, int(255 - 80 * st['red']), int(255 - 100 * st['red'])), BlendMode=skia.BlendMode.kMultiply))
    if st['circle'] > 0:
        c.saveLayer(R(*WIN), skia.Paint(BlendMode=skia.BlendMode.kPlus))
        S.rune_circle(c, 860, 846, 250, u=st['circle'], col=(255, 70, 40), squash=0.34, t=t, glow=0.6 + 0.6 * win(r, 19.7, 20.8, 0.3, 0.5),
                      a=int(200 + 55 * win(r, 19.7, 20.8, 0.3, 0.5)))
        c.restore()
    g = skia.GradientShader.MakeRadial(P(960, 560), 620, [rgb(0, 0, 0, 0), rgb(10, 4, 2, 150)], [0.55, 1])
    c.drawRect(R(*WIN), skia.Paint(Shader=g))


def footlights(c, t, red=0.0):
    x0, y0, x1, y1 = WIN
    c.drawRect(R(x0, y1 - 22, x1, y1), paint(C(S.WOOD_DK)))
    c.drawLine(x0, y1 - 22, x1, y1 - 22, paint(C(S.WOOD_LT), stroke=2))
    col = mix((255, 190, 110), (255, 90, 50), red)
    for k in range(9):
        x = x0 + 46 + k * (x1 - x0 - 92) / 8
        f = flicker(t, k)
        additive_glow(c, x, y1 - 30, 90, col, 40 * f)
        flames(c, x, y1 - 20, 12, 24 * f, t, seed=k, a=230)
        c.drawRect(R(x - 7, y1 - 22, x + 7, y1 - 14), paint(C(S.GOLD_DK)))


def title_ribbon(c, t, txt_u):
    """Band über der oberen Leiste mit dem Titel; txt_u: 0 = 'YI TI', 1 = 'THE BLOODSTONE EMPEROR'"""
    S.ribbon(c, [(600 + i * 72, 36 + 3 * math.sin(i)) for i in range(11)], w=74, t=t, a=255, wave=3, ph=1.0)
    if txt_u < 0.15:
        text(c, 'YI TI', 960, 50, TF_CINZEL_B, 36, S.SEPIA_INK, align='center', alpha=int(255 * (1 - txt_u / 0.15)), spacing=8)
    if txt_u > 0.15:
        s = 'THE BLOODSTONE EMPEROR'
        n = int(len(s) * clamp((txt_u - 0.15) / 0.75))
        wfull = text_width(s, TF_CINZEL_B, 30) + 2 * (len(s) - 1)
        text(c, s[:n], 960 - wfull / 2, 49, TF_CINZEL_B, 30, (110, 22, 16), alpha=255, spacing=2)


# ------------------------------------------------------------------ das Theater als Ganzes
CAM_KEYS = [(7.0, (960, 540, 0.88)), (8.6, (960, 550, 0.92)), (9.6, (945, 575, 1.17)), (17.4, (955, 585, 1.2)),
            (19.3, (960, 560, 0.95)), (21.4, (960, 548, 1.0)), (23.0, (880, 700, 1.38)), (25.0, (820, 690, 1.42)), (26.4, (860, 650, 1.36)),
            (27.2, (1090, 650, 1.32)), (28.6, (1000, 600, 1.12)), (30.0, (840, 520, 1.25)), (31.3, (800, 560, 1.28)),
            (31.9, (1080, 450, 1.3)), (32.8, (1110, 540, 1.32)), (33.7, (1000, 560, 1.05)), (34.9, (960, 540, 0.88))]


def theatre_cam(t):
    cx, cy, z = key_interp(CAM_KEYS, t)
    r = r_(t)
    if 23.5 < r < 24.3:
        k = (1 - (r - 23.5) / 0.8) ** 2
        cx += 14 * k * math.sin(t * 70)
        cy += 10 * k * math.cos(t * 83)
    return cx, cy, z


def theatre(c, t):
    c.save()
    _theatre(c, t)
    c.restore()


def _theatre(c, t):
    r = r_(t)
    cam = theatre_cam(t)
    C1.camera(c, *cam)
    pop = clamp((t - 7.0) / 0.9) * (1 - clamp((t - 34.2) / 0.7))
    st_red = ramp(r, 11.0, 12.4) * (1 - 0.4 * ramp(r, 24.5, 25.5))
    surround(c, t, pop, red=st_red * (1 - clamp((t - 34.0) / 0.8)))
    # Bühnenfenster: vor dem Brand Radierung, danach Farbe; am Ende friert die Szene zur Radierung ein
    sep = 1.0 if r < 9.6 else 0.0
    c.save()
    c.clipRect(R(*WIN))
    if r > 9.5 or t < 9.3:
        stage_color(c, t, sep, cam)
    backstory(c, t)
    footlights(c, t, red=st_red)
    fz = ramp(t, 33.9, 34.8)
    if fz > 0:
        c.drawImage(final_img(), WIN[0], WIN[1], SAMP, skia.Paint(Alphaf=fz))
    c.restore()
    S.ornate_frame(c, WIN, bw=FBW, t=t)
    title_ribbon(c, t, clamp((r - 10.0) / 1.4))
    fore_clouds(c, t, pop)


# ------------------------------------------------------------------ das Buch: Seiten
def ink_lines(c, x0, x1, y0, n, gap=34, seed=1, a=170, last=0.55, u=1.0):
    rng = np.random.default_rng(seed)
    for k in range(n):
        wk = last if k == n - 1 else rng.uniform(0.86, 1.0)
        yy = y0 + k * gap
        xe = x0 + (x1 - x0) * wk * clamp(u * n - k)
        xx = x0
        while xx < xe:
            wl = rng.uniform(24, 86)
            xw = min(xx + wl, xe)
            pts = [(x, yy + 2.5 * math.sin(x * 0.35 + k)) for x in np.linspace(xx, xw, max(3, int((xw - xx) / 8)))]
            c.drawPath(poly(pts, closed=False), paint(C(INK, a), stroke=2.0))
            xx = xw + rng.uniform(11, 17)


def framed_small(c, img, x, y, w, h, label):
    c.drawRect(R(x + 8, y + 10, x + w + 8, y + h + 10), blur_paint(rgb(0, 0, 0, 90), 8))
    c.drawRect(R(x - 10, y - 10, x + w + 10, y + h + 10), paint(C(S.WOOD)))
    c.drawRect(R(x - 10, y - 10, x + w + 10, y + h + 10), paint(C(S.SEPIA_INK), stroke=2))
    draw_img(c, img, R(x, y, x + w, y + h))
    c.drawRect(R(x, y, x + w, y + h), paint(C(S.GOLD_LEAF), stroke=3))
    text(c, label, x + w / 2, y + h + 46, TF_FELL_SC, 24, INK, align='center', alpha=220)


def spreadA_left(c):
    B.parch_fill(c, LPATH)
    text(c, 'OLDTOWN', LP[0] + 70, PT + 120, TF_CINZEL_B, 30, INK, alpha=220)
    ink_lines(c, LP[0] + 70, LP[2] - 70, PT + 170, 6, seed=3)
    framed_small(c, ENG_4D_PL, LP[0] + 175, PT + 400, 300, 372, 'the black base of the Hightower')


def spreadA_right(c):
    B.parch_fill(c, RPATH)
    text(c, 'PYKE', RP[0] + 70, PT + 120, TF_CINZEL_B, 30, INK, alpha=220)
    ink_lines(c, RP[0] + 70, RP[2] - 70, PT + 170, 6, seed=4)
    framed_small(c, ENG_4C_PL, RP[0] + 175, PT + 400, 300, 372, 'the Seastone Chair')


def spreadB_left(c, t=0.0):
    B.parch_fill(c, LPATH)
    x0, x1 = LP[0] + 70, LP[2] - 70
    text(c, 'YI TI', (x0 + x1) / 2, PT + 170, TF_CINZEL_B, 64, INK, align='center', alpha=230, spacing=10)
    text(c, 'the Bloodstone Emperor', (x0 + x1) / 2, PT + 222, TF_FELL_I, 32, INK, align='center', alpha=210)
    c.drawLine(x0 + 60, PT + 250, x1 - 60, PT + 250, paint(C(INK, 120), stroke=1.4))
    S.star8(c, (x0 + x1) / 2, PT + 250, 9, a=220)
    ink_lines(c, x0, x1, PT + 300, 7, seed=7)
    S.nimbus(c, (x0 + x1) / 2, PT + 650, 84, col=S.BLOOD, inner=(80, 10, 8), t=t)
    with saved(c):
        p = skia.Path()
        p.addCircle((x0 + x1) / 2, PT + 650, 54)
        c.clipPath(p, doAntiAlias=True)
        draw_img(c, ENG_4E, R((x0 + x1) / 2 - 54, PT + 596, (x0 + x1) / 2 + 54, PT + 704))
    c.drawCircle((x0 + x1) / 2, PT + 650, 54, paint(C(S.SEPIA_INK), stroke=2))
    ink_lines(c, x0, x1, PT + 760, 2, seed=8, last=0.4)


FINAL_IMG = None


def window_snapshot(t):
    """Endzustand der Bühne in Farbe rendern und zur Radierung umwandeln (Tafel im Buch nach dem Theater)"""
    s = skia.Surface(WIN[2] - WIN[0], WIN[3] - WIN[1])
    c = s.getCanvas()
    c.translate(-WIN[0], -WIN[1])
    stage_color(c, t, 0.0, CAM0)
    footlights(c, t, red=0.6)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    return to_image(S.engrave(a))


def final_img():
    global FINAL_IMG
    if FINAL_IMG is None:
        FINAL_IMG = window_snapshot(VQ + 25.0)
    return FINAL_IMG


def plate(c, t, mode):
    """die Tafel im Bühnen-Raum (Rahmen + Fenster). mode 'eng' = Radierung des Gemäldes, 'final' = Endzustand"""
    global FINAL_IMG
    with saved(c):
        c.clipRect(R(*WIN))
        if mode == 'final':
            c.drawImage(final_img(), WIN[0], WIN[1], SAMP)
        else:
            c.drawRect(R(*WIN), paint(C(S.SEPIA_PAPER)))
            with saved(c):
                paint_space(c)
                c.drawImage(ENG_PAINT, 0, 0, SAMP)
    S.ornate_frame(c, WIN, bw=FBW, t=t)


def spreadB_right(c, t, mode='eng'):
    B.parch_fill(c, RPATH)
    with saved(c):
        c.translate(*BOOK_C)
        c.scale(BOOK_F, BOOK_F)
        c.translate(-960, -540)
        c.drawRect(R(WIN[0] - FBW + 14, WIN[1] - FBW + 18, WIN[2] + FBW + 14, WIN[3] + FBW + 18), blur_paint(rgb(0, 0, 0, 110), 14))
        plate(c, t, mode)
    text(c, 'PLATE IX', BOOK_C[0], PB - 76, TF_FELL_SC, 26, INK, align='center', alpha=210)


# ------------------------------------------------------------------ 04-8: die gefallenen Steine auf der Gezeitenlinie
MEDS = [('ASSHAI', ENG_4A, (610, 430), 0.35), ('YEEN', ENG_4B, (1420, 330), 1.35), ('PYKE', ENG_4C, (800, 560), 1.75),
        ('OLDTOWN', ENG_4D, (1190, 560), 3.0), ('YI TI', ENG_4E, (1460, 600), 4.5)]
SAW_X0, SAW_X1, SAW_BASE = LP[0] + 80, RP[2] - 110, PB - 130
HTS = [230, 280, 250, 270, 330]


def saw_points():
    tw = (SAW_X1 - SAW_X0 - 120) / 5
    pts = [(SAW_X0, SAW_BASE)]
    peaks = []
    for k in range(5):
        xs = SAW_X0 + k * tw
        pk = (xs + tw * 0.12, SAW_BASE - HTS[k])
        peaks.append(pk)
        pts.append(pk)
        pts.append((xs + tw if k < 4 else SAW_X1, SAW_BASE))
    return pts, peaks


SAW, PEAKS = saw_points()


def medallion(c, img, x, y, r, label, a=255, t=0.0, q=0.0):
    c.drawCircle(x + 6, y + 9, r + 10, blur_paint(rgb(0, 0, 0, int(a * 0.4)), 8))
    with saved(c):
        p = skia.Path()
        p.addCircle(x, y, r)
        c.clipPath(p, doAntiAlias=True)
        draw_img(c, img, R(x - r, y - r, x + r, y + r), alpha=a / 255)
    c.drawCircle(x, y, r + 6, paint(C(S.GOLD_LEAF, a), stroke=12))
    for k in range(36):
        ang = k * math.pi * 2 / 36
        c.drawCircle(x + math.cos(ang) * (r + 6), y + math.sin(ang) * (r + 6), 1.8, paint(C(S.GOLD_DK, a)))
    c.drawCircle(x, y, r + 12, paint(C(S.SEPIA_INK, a), stroke=2))
    c.drawCircle(x, y, r, paint(C(S.SEPIA_INK, a), stroke=2))
    # Bandlabel
    wl = text_width(label, TF_CINZEL_B, 20) + 44
    S.ribbon(c, [(x - wl / 2 + i * wl / 5, y + r + 30 + 4 * math.sin(i)) for i in range(6)], w=34, t=t, a=a, wave=2, ph=x * 0.01)
    text(c, label, x, y + r + 37, TF_CINZEL_B, 20, S.SEPIA_INK, align='center', alpha=a)
    if q > 0:
        text(c, '?', x + wl / 2 + 14, y + r + 42, TF_FELL_I, 40, INK, align='center', alpha=int(a * q))


def spreadC(c, t, side):
    """Doppelseite für 04-8; side 'l' / 'r' / None (beide)"""
    rel = t - V48
    c.save()
    if side == 'l':
        B.parch_fill(c, LPATH)
        c.clipPath(LPATH, doAntiAlias=True)
    elif side == 'r':
        B.parch_fill(c, RPATH)
        c.clipPath(RPATH, doAntiAlias=True)
    S.ribbon(c, [(LP[0] + 40 + i * 64, PT + 98 + 3 * math.sin(i)) for i in range(8)], w=60, t=t, a=255, wave=2, ph=0.6)
    text(c, 'THE FALLEN STONES', LP[0] + 70, PT + 110, TF_CINZEL_B, 30, INK, alpha=230)
    for (sx, sy, sr) in ((LP[0] + 560, PT + 180, 12), (RP[0] + 120, PT + 120, 9), (RP[2] - 90, PT + 210, 14), (SP - 40, PT + 300, 8)):
        S.star8(c, sx, sy, sr, a=210, rot=sx * 0.01)
    text(c, 'as the stargazer gathered them', LP[0] + 70, PT + 152, TF_FELL_I, 28, INK, alpha=190)
    # Wasser unter der Linie (Papierschichten wie in Kapitel 1)
    wpop = ease_out(clamp((rel - 14.0) / 0.8))
    if wpop > 0:
        for col, dy, hk, al in [((176, 200, 196), 0, 1.0, 170), ((146, 178, 180), 18, 0.9, 150)]:
            with folded(c, 0, SAW_BASE + 30, wpop):
                p = skia.Path()
                p.moveTo(SAW_X0, SAW_BASE + 30)
                for (x, y) in SAW:
                    p.lineTo(x, SAW_BASE - (SAW_BASE - y) * hk + dy)
                p.lineTo(SAW_X1, SAW_BASE + 30)
                p.close()
                c.drawPath(p, paint(rgb(*col, al)))
                c.save()
                c.clipPath(p, doAntiAlias=True)
                for k in range(int(SAW_X0) - 400, int(SAW_X1), 9):
                    c.drawLine(k, SAW_BASE + 30, k + 340, SAW_BASE - 340, paint(rgb(60, 90, 96, 50), stroke=1.1))
                c.restore()
            with folded(c, 0, SAW_BASE + 30, wpop):
                for k in range(3):
                    y = SAW_BASE + 2 + k * 9
                    wp = [(x, y + 3 * math.sin(x * 0.045 + k * 1.7 + t * 1.2)) for x in np.linspace(SAW_X0 + 6, SAW_X1 - 6, 120)]
                    c.drawPath(poly(wp, closed=False), paint(rgb(236, 240, 232, 140), stroke=1.8))
    # die Linie zeichnet sich
    lu = clamp((rel - 10.1) / 3.0)
    if lu > 0:
        pth = poly(SAW, closed=False)
        if lu < 1:
            m = skia.PathMeasure(pth, False)
            seg = skia.Path()
            m.getSegment(0, m.getLength() * lu, seg, True)
            pth = seg
        c.drawPath(pth, paint(C(INK, 230), stroke=3.4))
        c.drawLine(SAW_X0 - 20, SAW_BASE + 30, SAW_X1 + 70, SAW_BASE + 30, paint(C(INK, int(150 * lu)), stroke=1.6))
        text(c, 'the ages', SAW_X0, SAW_BASE + 66, TF_FELL_I, 24, INK, alpha=int(160 * lu))
    if rel > 13.5:
        a = int(230 * clamp((rel - 13.5) / 0.6))
        lx, ly = PEAKS[4]
        text(c, 'LONG NIGHT', lx + 26, ly + 34, TF_CINZEL_B, 19, INK, align='left', alpha=a)
    # Gipfel leuchten nacheinander
    for k, (x, y) in enumerate(PEAKS):
        g = win(rel, 16.4 + k * 0.32, 18.2, 0.15, 0.8)
        if g > 0:
            additive_glow(c, x, y, 70, (255, 200, 110), 120 * g)
    # JETZT: neuer Anstieg in Gold
    nu = clamp((rel - 17.6) / 1.2)
    if nu > 0:
        x0, y0 = SAW_X1, SAW_BASE
        x1, y1 = SAW_X1 + 46, SAW_BASE - 200
        xe, ye = lerp(x0, x1, ease(nu)), lerp(y0, y1, ease(nu))
        c.drawLine(x0, y0, xe, ye, blur_paint(rgb(255, 210, 120, 160), 5, stroke=9))
        c.drawLine(x0, y0, xe, ye, paint(C(S.GOLD_LEAF), stroke=4))
        c.drawCircle(xe, ye, 22, blur_paint(rgb(255, 200, 100, 150), 9))
        c.drawCircle(xe, ye, 10, paint(C(GOLD)))
        text(c, 'NOW', SAW_X1, SAW_BASE + 66, TF_CINZEL_B, 22, (120, 40, 26), align='center', alpha=int(230 * nu))
    # Medaillons: erscheinen verstreut, fliegen dann auf die Gipfel
    for k, (lab, img, (mx, my), tp) in enumerate(MEDS):
        pop = popv(t, V48 + tp, 0.5)
        if pop <= 0:
            continue
        fu = ease(clamp((rel - (11.7 + k * 0.55)) / 0.9))
        px_, py_ = PEAKS[k]
        tx, ty = px_, py_ - 92 - 26
        x = lerp(mx, tx, fu)
        y = lerp(my, ty, fu) - 120 * math.sin(math.pi * fu)
        rr = lerp(84, 64, fu)
        q = clamp((rel - (6.9 if k < 2 else 99)) / 0.4)
        # fallender Stern trifft den Gipfel
        su = clamp((rel - (11.7 + k * 0.55 + 0.45)) / 0.5)
        if 0 < su < 1:
            sx, sy = px_ + 160 * (1 - su), py_ - 420 * (1 - su)
            c.drawLine(sx, sy, sx + 70, sy - 180, blur_paint(rgb(255, 210, 130, int(200 * (1 - su * 0.5))), 4, stroke=4))
            S.star8(c, sx, sy, 14, a=255, rot=su * 4, glow=1.0)
        if fu > 0.98:
            c.drawLine(px_, py_, tx, ty + rr, paint(C(INK, 160), stroke=1.6))
        PG.popped_disc(c, x, y, rr, pop, lambda c_, r_, img=img, lab=lab, q=q: medallion(c_, img, 0, 0, r_, lab, t=t, q=q), lift=10 + 20 * math.sin(math.pi * fu))
    c.restore()


# ------------------------------------------------------------------ Buchansicht
FLIPS = [(T_FLIP1[0], T_FLIP1[1], PW, 'r'), (T_FLIP2[0], T_FLIP2[1], PW, 'r')]


def book_view(c, t):
    c.save()
    _book_view(c, t)
    c.restore()


def _book_view(c, t):
    # Kamera: neutral -> in die Tafel hinein; am Ende aus der Tafel heraus
    zin = ease(clamp((t - T_ZOOM_IN[0]) / (T_ZOOM_IN[1] - T_ZOOM_IN[0])))
    zout = 1 - ease(clamp((t - T_ZOOM_OUT[0]) / (T_ZOOM_OUT[1] - T_ZOOM_OUT[0])))
    k = zin if t < 20 else zout
    zt = CAM0[2] / BOOK_F
    z = lerp(1.0, zt, k) if k < 1 else zt
    # damit die Tafel exakt auf das Theater fällt, interpolieren wir den Bildpunkt der Tafelmitte
    cx = lerp(960, BOOK_C[0], k)
    cy = lerp(540, BOOK_C[1] + (540 - 540), k)
    if t > 37.0:
        k2 = ease(clamp((t - 37.0) / 12.0))
        k3 = ease(clamp((t - (V48 + 16.2)) / 2.6))
        z = 1 + 0.07 * k2 + 0.08 * k3
        cx = 960 + 150 * k3
        cy = 540 + 50 * k2 + 20 * k3
    C1.camera(c, cx, cy, z)
    mode = 'eng' if t < 20 else 'final'
    if t < T_FLIP1[0]:
        C1.book_frame(c, t, math.pi, spreadA_right, spreadA_left, flips=FLIPS)
    elif t < T_FLIP1[1]:
        phi = C1.flip_phi(t, *T_FLIP1)
        C1.book_frame(c, t, math.pi, lambda c: spreadB_right(c, t, mode), spreadA_left,
                      flap=(phi, spreadA_right, lambda c: spreadB_left(c, t)), flips=FLIPS)
    elif t < T_FLIP2[0]:
        C1.book_frame(c, t, math.pi, lambda c: spreadB_right(c, t, mode), lambda c: spreadB_left(c, t), flips=FLIPS)
    elif t < T_FLIP2[1]:
        phi = C1.flip_phi(t, *T_FLIP2)
        C1.book_frame(c, t, math.pi, lambda c: spreadC(c, t, 'r'), lambda c: spreadB_left(c, t),
                      flap=(phi, lambda c: spreadB_right(c, t, mode), lambda c: spreadC(c, t, 'l')), flips=FLIPS)
    else:
        C1.book_frame(c, t, math.pi, lambda c: spreadC(c, t, 'r'), lambda c: spreadC(c, t, 'l'), flips=FLIPS)


# ------------------------------------------------------------------ Szene
def scene(c, t):
    if t < T_X_IN[0]:
        book_view(c, t)
    elif t < T_X_IN[1]:
        C1.xfade(c, t, book_view, theatre, smooth((t - T_X_IN[0]) / (T_X_IN[1] - T_X_IN[0])))
    elif t < T_X_OUT[0]:
        theatre(c, t)
    elif t < T_X_OUT[1]:
        C1.xfade(c, t, theatre, book_view, smooth((t - T_X_OUT[0]) / (T_X_OUT[1] - T_X_OUT[0])))
    else:
        book_view(c, t)
    if t < 0.5:
        c.drawRect(R(0, 0, W, H), paint(rgb(0, 0, 0, int(255 * (1 - t / 0.5)))))
    if t > T_END - 0.9:
        c.drawRect(R(0, 0, W, H), paint(rgb(0, 0, 0, int(255 * smooth((t - (T_END - 0.9)) / 0.9)))))


_r = np.random.default_rng(3)
GRAIN = [_r.normal(0, 3.4, (OH, OW, 1)).astype(np.float32) for _ in range(6)]
YY, XX = np.mgrid[0:OH, 0:OW]
VIGN = (1 - 0.24 * np.clip(np.sqrt(((XX - OW / 2) / (OW * 0.7)) ** 2 + ((YY - OH / 2) / (OH * 0.72)) ** 2) - 0.35, 0, 1) ** 1.4)[..., None].astype(np.float32)


def frame(t, idx=0):
    s = skia.Surface(OW, OH)
    c = s.getCanvas()
    c.scale(SCALE, SCALE)
    scene(c, t)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    a = a * VIGN + GRAIN[idx % 6]
    return np.clip(a, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    import subprocess
    if sys.argv[1] == 'still':
        os.makedirs(D + 'stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            Image.fromarray(frame(t, int(t * FPS))).save(D + f'stills/s4_{t:05.2f}.png')
        print('ok')
    elif sys.argv[1] == 'range':
        i0, i1, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS),
               '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(i0, i1):
            p.stdin.write(frame(i / FPS, i).tobytes())
            if i % 90 == 0:
                print(out, i, flush=True)
        p.stdin.close(); p.wait()
        print('done', out)
