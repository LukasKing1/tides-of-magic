#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Beispielszene im Herrenhaus: P-09 bis zur Titelkarte (P-15), vertont.

P-09 laeuft noch in der Geschichte (STORY am Rand). P-10: Rueckfahrt aus der Kristallkugel in den Salon.
P-11: Die Schlange stellt sich vor, Schnitt auf die Ahnengalerie. P-12/P-13: drei Annahmen als Karten,
goldene Siegel GRANTED, Riss in der Kugel. P-14: Fahrt in das Portraet der 1950er, es wird zum alten Film,
die Frage als Zwischentitel. Danach die Titelkarte.

Bild:  python3 manor_scene.py render <startframe> <endframe> <out.mp4>
Stand: python3 manor_scene.py still <sekunde> <out.png> [...]
Ton:   python3 manor_scene.py audio <out.wav>
Info:  python3 manor_scene.py info
"""
import math, random, subprocess, sys
import numpy as np
import skia
import start as S
import rich as R
import rich_base as RB
import mascot3 as M
import manor as MN
import frames9 as F
import frames10 as T
import frames11 as K
import style5 as ST
from rich_base import *

TF_CAPS, TF_HEAD, TF_TITLE, TF_D, TF_QUOTE = P.TF_CAPS, P.TF_HEAD, P.TF_TITLE, M.TF_DISPLAY, P.TF_QUOTE
CREAM = K.CREAM

# ---------------------------------------------------------------- Ablauf (Sekunden ab Szenenbeginn)
A0 = 0.0                       # P-09 in der Geschichte (s_lastjob), 7.2 s
L0 = 7.2                       # Beginn der Salonszene
P11S, P12S, P13S, P14S = S.P11S, S.P12S, S.P13S, S.P14S
CARD_ON, STAMP_ON = S.CARD_ON, S.STAMP_ON
CRACK0, CRACK1, BRANCH1 = S.CRACK0, S.CRACK1, S.BRANCH1
P14E = S.P14E
LONG = P14E + 2.0              # etwas laenger als Entwurf 1, damit der Zwischentitel lesbar bleibt
TITLE0 = L0 + LONG
TOTAL = TITLE0 + 6.0

CUT_GAL0, CUT_GAL1 = 14.75, 19.25   # Schnitt auf die Ahnengalerie und zurueck
CUT_PORT = 62.45                    # Schnitt auf das Portraet der 1950er
FILM0 = 65.0                        # alter Film bildfuellend
INTER0 = 66.9                       # Zwischentitel mit der Frage

# Welt: Salon in 1920x1080 wie manor.salon
Y_RAIL, Y_FLOOR = 600, 850
BALL_X, BALL_Y, BALL_R = 1395, 600, 61
SN_X, SN_Y, SN_S = 1700, 500, 128
PORT = MN.GALLERY[3]            # (3, 400, 400, 110, 110, True): 1950s, AUTOMATION
PCX, PCY = PORT[1] + PORT[3] / 2, PORT[2] + PORT[4] / 2

# ---------------------------------------------------------------- Ton
VOICE = [
    ('P-09', 0, 4.28, 0.4), ('P-09', 4.28, None, 4.9),
    ('P-10', 0, None, L0 + 0.8), ('P-11', 0, None, L0 + P11S), ('P-12', 0, None, L0 + P12S),
    ('P-13', 0, None, L0 + P13S), ('P-14', 0, None, L0 + P14S),
]
MUSIC = [
    ('music/01_P-01_bis_P-09_Cyclical-Darkness.mp3', 57.6, 0.0, L0 + 1.6, 0.4, 2.4, 1.0),
    ('music/02_P-10_bis_P-14_Have-We-Met-Before.mp3', 0.0, L0 - 0.6, TOTAL, 2.5, 3.0, 1.0),
]
SFX = [
    ('sfx/02_servo_roboterarme.mp3', 0.0, 1.2, 4.5, .3),
    ('sfx/06_lichtschalter_lampe-aus.mp3', 0.0, .336, 3.5 * 7.2 / 6.4 - .05, .5),
    ('sfx/11_whoosh_kamerafahrten.mp3', 0.0, .936, L0 + 0.55, .4),
    ('sfx/05_zeitung_auf-tisch.mp3', 0.0, .43, L0 + 4.85, .45),
    ('sfx/02_servo_roboterarme.mp3', 1.6, 1.2, L0 + 7.25, .22),
    ('sfx/04_stempel.mp3', None, .7, L0 + STAMP_ON[0], .6),
    ('sfx/04_stempel.mp3', None, .7, L0 + STAMP_ON[1], .6),
    ('sfx/04_stempel.mp3', None, .7, L0 + STAMP_ON[2], .7),
    ('sfx/07_glas-riss_kugel.mp3', 0.0, 3.0, L0 + CRACK0, .5),
    ('sfx/07_glas-riss_kugel.mp3', 0.0, 2.0, L0 + BRANCH1 - .15, .75),
    ('sfx/11_whoosh_kamerafahrten.mp3', 0.0, .936, L0 + 64.1, .45),
    ('music/03_P-15_Designed-Boom-Impact-Dark-Cinematic-Bright-Tone.mp3', 0.0, 5.3, TITLE0 + .2, .9),
]


def make_audio(out):
    S.VOICE, S.MUSIC, S.SFX, S.TOTAL = VOICE, MUSIC, SFX, TOTAL
    S.make_audio(out)


# ---------------------------------------------------------------- Mund zur Stimme
def voice_envelope():
    n = int(LONG * FPS) + 2
    env = np.zeros(n)
    hop = S.SR // FPS
    for (name, a, b, t) in VOICE:
        if t < L0:
            continue
        clip = S.decode(f'{S.REPO}/voice/{name}.mp3').mean(axis=1)
        clip = clip[int(a * S.SR):(len(clip) if b is None else int(b * S.SR))]
        for k in range(len(clip) // hop):
            f = int((t - L0) * FPS) + k
            if 0 <= f < n:
                env[f] = max(env[f], float(np.sqrt(np.mean(clip[k * hop:(k + 1) * hop] ** 2))))
    ref = np.percentile(env[env > 0], 90) if (env > 0).any() else 1.0
    env = np.clip((env / ref - .12) / .75, 0, 1)
    out = env.copy()
    for i in range(1, n):
        out[i] = max(env[i], out[i - 1] * .55)
    return out


ENV = None


def talk_at(u):
    global ENV
    if ENV is None:
        ENV = voice_envelope()
    f = u * FPS
    i = int(f)
    if i < 0 or i + 1 >= len(ENV):
        return 0.0
    return float(lerp(ENV[i], ENV[i + 1], f - i))


# ---------------------------------------------------------------- Schlange: Ausdruck, Blick, Nicken
LOOK_BALL = (-0.45, 0.12)
LOOK_CARDS = (-0.8, -0.05)
LOOK_UP = (-0.75, -0.6)
EXPR_T = [
    (0.0, 'neutral'), (P11S + 0.1, 'smug'), (P11S + 2.4, 'happy'), (P11S + 4.2, 'neutral'), (CUT_GAL1, 'neutral'),
    (P11S + 10.9, 'worried'), (P11S + 13.6, 'smug'), (P12S, 'neutral'), (P13S, 'happy'), (P13S + 2.6, 'smug'),
    (P13S + 3.4, 'neutral'), (CRACK0, 'worried'), (BRANCH1 + .2, 'surprised'), (BRANCH1 + .75, 'neutral'),
]
LOOK_T = [
    (0.0, LOOK_BALL), (P11S - 0.1, LOOK_BALL), (P11S + 0.5, (0.0, 0.0)), (P11S + 4.3, (0.0, 0.0)),
    (P11S + 4.75, (-0.8, -0.45)), (CUT_GAL1, (0.0, 0.0)), (P11S + 10.8, (0.0, 0.0)), (P11S + 11.3, LOOK_BALL),
    (P11S + 13.4, LOOK_BALL), (P11S + 13.8, (0.0, 0.0)), (P12S + 0.2, (0.0, 0.0)), (P12S + 0.9, LOOK_CARDS),
    (P13S - 0.2, LOOK_CARDS), (P13S + 0.4, (0.0, 0.0)), (P13S + 2.4, (0.0, 0.0)), (P13S + 3.0, LOOK_BALL),
    (BRANCH1 + .4, LOOK_BALL), (BRANCH1 + .85, LOOK_UP),
]


def expr_at(u):
    e = EXPR_T[0][1]
    for t0, name in EXPR_T:
        if u >= t0:
            e = name
    return e


def look_at(u):
    for (t0, l0), (t1, l1) in zip(LOOK_T, LOOK_T[1:]):
        if t0 <= u <= t1:
            k = eio(prog(u, t0, t1))
            return (lerp(l0[0], l1[0], k), lerp(l0[1], l1[1], k))
    return LOOK_T[-1][1]


def blink_at(u):
    ph = (u + 1.3) % 3.9
    return 1.0 if ph < .12 else 0.0


def snake(cv, u):
    e = expr_at(u)
    look = look_at(u)
    talk = talk_at(u)
    nod = sum(9 * math.sin(math.pi * prog(u, s - .15, s + .3)) for s in STAMP_ON)
    tilt = -6 + 3 * math.sin(u * .9) + 5 * look[0] + nod
    jolt = 16 * math.sin(math.pi * prog(u, BRANCH1 + .15, BRANCH1 + .6))
    gold = .15 + .5 * eout(prog(u, CRACK1, BRANCH1)) * (1 - prog(u, BRANCH1 + 1.0, BRANCH1 + 2.0))
    cv.save()
    cv.translate(SN_X, SN_Y)
    cv.scale(SN_S, SN_S)
    M.draw_body(cv)
    M.draw_collar(cv)
    cv.save()
    cv.translate(0, -0.02 + 0.012 * math.sin(u * 1.6) - jolt / SN_S)
    M.draw_head(cv, e, look, tilt, False, 1.0, t=u, reflect=gold, talk=0.0 if e == 'surprised' else talk,
                blink=0.0 if e in ('happy', 'surprised') else blink_at(u))
    cv.restore()
    cv.restore()


# ---------------------------------------------------------------- Kristallkugel mit der Stadt darin
CITY = None


def city_img():
    """Die goldene Stadt der Geschichte, doppelt aufgeloest, als Inhalt der Kugel."""
    global CITY
    if CITY is None:
        surf = skia.Surface(2 * W, 2 * H)
        cv = surf.getCanvas()
        cv.scale(2, 2)
        P.G.zoom = 1.0
        R.s_city(cv, 8.6)
        CITY = surf.makeImageSnapshot()
    return CITY


CRACK_MAIN = None


def ball(cv, u):
    global CRACK_MAIN
    x, y, r = BALL_X, BALL_Y, BALL_R
    cp = eio(prog(u, CRACK0, CRACK1))
    bp = eio(prog(u, CRACK1, BRANCH1))
    leak = bp * (.7 + .3 * math.sin(u * 6))
    cv.drawCircle(x, y, r * 1.5, glowp(cv, GOLD_HI, 70, .22 + .25 * leak))
    cv.save()
    cv.clipPath(circle(x, y, r), doAntiAlias=True)
    cv.drawPaint(fillp(cv, '#0d0b0a', 1, False))
    iw, ih = r * 3.73, r * 2.1
    cv.drawImageRect(city_img(), skia.Rect.MakeXYWH(x - iw / 2, y - ih / 2, iw, ih),
                     skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    vg = skia.Paint(AntiAlias=True)
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r, [col('#000000', 0), col('#000000', 0), col('#0b0a07', .7)],
                                                [0, .7, 1]))
    cv.drawCircle(x, y, r, vg)
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(x - r * .8, y - r * .8, r * 1.6, r * 1.6), 200, 55)
    cv.drawPath(hl, strokep(cv, r * .06, '#fff6dc', .45))
    cv.drawCircle(x + r * .38, y - r * .42, r * .07, fillp(cv, '#fff6dc', .6, False))
    if cp > 0:
        if CRACK_MAIN is None:
            m = P.crack_points(R.BR)
            CRACK_MAIN = (m, P.crack_branches(R.BR, m))
        main, branches = CRACK_MAIN
        k = r / R.BR
        cv.save()
        cv.translate(x, y)
        cv.scale(k, k)
        mp = trim(poly(main, close=False), cp)
        lg = strokep(cv, 16 + 30 * bp, GOLD_HI, .55 + .4 * bp)
        lg.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, (6 + 8 * bp) / mscale(cv) * 1.0))
        cv.drawPath(mp, lg)
        cv.drawPath(mp, M.ink(cv, 4.5))
        cv.drawPath(mp, strokep(cv, 6 + 8 * bp, '#fff3d0', .9 * max(bp, .35)))
        for b in branches:
            bpth = trim(poly(b, close=False), bp)
            cv.drawPath(bpth, lg)
            cv.drawPath(bpth, M.ink(cv, 3.4))
            cv.drawPath(bpth, strokep(cv, 4 + 5 * bp, '#fff3d0', .9 * bp))
        cv.restore()
    cv.restore()
    cv.drawPath(circle(x, y, r), M.ink(cv, 2.6))
    if leak > 0:
        cv.drawCircle(x, y + r * .15, r * .9, glowp(cv, GOLD_HI, 40, .35 * leak))
        rnd = random.Random(int(u * 3))
        for j in range(3):
            MN.sparkle(cv, x + rnd.uniform(-r, r), y + rnd.uniform(-r, r * .6), rnd.uniform(4, 8), a=.8 * leak)


# ---------------------------------------------------------------- Kleine Pointen im Salon (P-10)
def newspaper(cv, x, y, w, rot, pop):
    h = w * .62
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    s = 1 + .14 * math.sin(math.pi * pop)
    cv.translate(0, -18 * math.sin(math.pi * pop))
    cv.scale(s, s)
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .4))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
    cv.drawRect(skia.Rect.MakeXYWH(-w / 2 + 5, -h / 2 + 8, w, h), sh)
    pg = MN.rect(-w / 2, -h / 2, w, h, 2)
    MN.flat(cv, pg, '#e6dcc2', '#cbbd99', None, 4, line=2)
    cv.drawLine(0, -h / 2 + 4, 0, h / 2 - 4, strokep(cv, 1.4, '#a8987a', .7))
    text(cv, 'THE DAILY LEDGER', 0, -h / 2 + 19, TF_CAPS, w * .075, '#2a2017', anchor='c', spacing=1)
    cv.drawLine(-w / 2 + 8, -h / 2 + 25, w / 2 - 8, -h / 2 + 25, strokep(cv, 1.6, '#2a2017'))
    hs = fit_font(TF_TITLE, w * .105, ['THE END OF WORK?'], w - 22)
    text(cv, 'THE END OF WORK?', 0, -h / 2 + 25 + w * .12, TF_TITLE, hs, '#1c1610', anchor='c')
    for k in range(5):
        yy = -h / 2 + 25 + w * .17 + k * 10
        if yy > h / 2 - 8:
            break
        cv.drawLine(-w / 2 + 10, yy, -6, yy, strokep(cv, 3, '#9a8c70', .6))
        cv.drawLine(8, yy, w / 2 - 10, yy, strokep(cv, 3, '#9a8c70', .6))
    cv.restore()
    if 0 < pop < 1:
        MN.sparkle(cv, x + w * .45, y - h * .55, 10 * math.sin(math.pi * pop), a=.9)


def leaning_book(cv, u):
    k = eio(prog(u, 5.95, 6.4)) * (1 - eio(prog(u, 9.0, 9.6)))
    if k <= 0:
        return
    sh_h = (Y_FLOOR - 130 - 40) / 6
    y1 = 130 + 18 + sh_h + sh_h - 12
    bx, bw, bh = 214, 24, (sh_h - 12) * .9
    cv.save()
    cv.translate(bx + bw, y1)
    cv.rotate(-16 * k)
    cv.translate(0, -10 * k)
    b = MN.rect(-bw, -bh, bw, bh, 2)
    MN.flat(cv, b, '#6b2a24', '#481a17', '#8f4236', 3.5, 2, line=1.6)
    for band in (.16, .82):
        cv.drawLine(-bw + 2, -bh * band, -2, -bh * band, strokep(cv, 2, GOLD, .9))
    cv.restore()
    MN.sparkle(cv, bx + 4, y1 - bh - 16, 9 * k * (.6 + .4 * math.sin(u * 5)), a=.85)


# ---------------------------------------------------------------- Der Salon mit allem, was sich bewegt
HIRES_PORT = None


def salon_dyn(cv, u):
    global HIRES_PORT
    t = u
    MN.wallpaper(cv, -50, -50, W + 50, Y_RAIL)
    MN.halftone(cv, -10, -10, 520, 380, '#0c0d0a', 16, 4.5, 'left', .45)
    MN.wainscot(cv, -50, W + 50, Y_RAIL, Y_FLOOR)
    MN.floor(cv, Y_FLOOR)
    MN.rug(cv, 1140, 900, 1000, 1500, 1060)
    MN.bookshelf(cv, 30, 130, 300, Y_FLOOR - 130)
    leaning_book(cv, u)
    MN.window(cv, 1735, 110, 175, 430, t)
    MN.moonbeams(cv, 1740, 1905, 300, 1100, 1560, H, .07)
    MN.gas_lamp(cv, 935, 230, .85)
    MN.gas_lamp(cv, 1325, 230, .85)
    rail = MN.rect(-50, 62, W + 100, 14)
    MN.flat(cv, rail, MN.WOOD_HI, MN.WOOD_DK, '#7a5b45', 4, 2)
    for (ei, x, y, w, h, ov) in MN.GALLERY[:3]:
        for sx in (-1, 1):
            cv.drawLine(x + w / 2 + sx * 4, 74, x + w / 2 + sx * w * .3, y - 20, strokep(cv, 2, GOLD_DK, .9))
    for xx in (1130 - 70, 1130 + 70):
        cv.drawLine(1130, 74, xx, 114, strokep(cv, 2, GOLD_DK, .9))
    MN.gallery(cv)
    if u > CUT_PORT - 1.0:
        if HIRES_PORT is None:
            HIRES_PORT = T.portrait(T.ERAS[3], PORT[3] * 8, PORT[4] * 8)
        portrait_into(cv, u)
    fx = 1130
    shelf_y = MN.fireplace(cv, fx, Y_FLOOR, 400, 330, t)
    gx, gy, gw, gh = fx - 110, 140, 220, 240
    T.frame_at(cv, gx, gy, gw, gh, None, False, gold=True)
    cv.drawRect(skia.Rect.MakeXYWH(gx, gy, gw, gh), glowp(cv, GOLD_HI, 40, .22))
    text(cv, '?', gx + gw / 2, gy + gh / 2 + 40, TF_D, 120, GOLD, anchor='c')
    MN.small_plaque(cv, gx + gw / 2, gy + gh + 30, 'TODAY', 'AI', .75)
    for k_, (sx, sy, r) in enumerate(((gx - 18, gy + 30, 11), (gx + gw + 20, gy + 70, 8), (gx + gw - 10, gy - 22, 9))):
        MN.sparkle(cv, sx, sy, r * (.8 + .2 * math.sin(u * 2.1 + k_ * 2)))
    MN.candlestick(cv, fx - 150, shelf_y, .9)
    MN.mantel_clock(cv, fx + 170, shelf_y, .9)
    ty = MN.side_table(cv, BALL_X, Y_FLOOR + 30, 190, 68)
    ST.stand(cv, BALL_X, ty - 22, 66)
    ball(cv, u)
    newspaper(cv, 1150, 978, 230, -7, prog(u, 4.8, 5.45))
    cx, seat_y, cw = 1640, 790, 330
    MN.armchair_back(cv, cx, seat_y, cw)
    snake(cv, u)
    MN.armchair_front(cv, cx, seat_y, cw)
    st_y = MN.step_stool(cv, 470, Y_FLOOR + 6, 120, 110)
    bow = math.sin(math.pi * prog(u, 7.25, 8.6))
    target = (lerp(430 + 22 * math.sin(u * .8), 450, bow), lerp(560 + 10 * math.sin(u * 1.3), 640, bow))
    away = eio(prog(u, CUT_PORT + .2, CUT_PORT + 1.1))
    target = (lerp(target[0], 330, away), lerp(target[1], 720, away))
    cv.save()
    cv.translate(470, st_y + 8)
    cv.scale(1, 1 - .09 * bow)
    cv.rotate(-6 * bow)
    cv.translate(-470, -(st_y + 8))
    MN.butler(cv, 470, st_y + 8, 120, t * (1 - bow), 'dust', target=target)
    cv.restore()
    fire = skia.Paint()
    fire.setShader(skia.GradientShader.MakeRadial(skia.Point(fx, Y_FLOOR), 600,
                                                  [col('#f0a24a', .14 + .02 * math.sin(u * 7)), col('#f0a24a', 0)]))
    cv.drawRect(skia.Rect.MakeLTRB(fx - 700, Y_FLOOR - 500, fx + 700, H), fire)
    R.dust(cv, t, (1100, 300, 1900, 1000), 40, 6, '#dfe6ea', .3)
    R.dust(cv, t, (200, 150, 900, 700), 26, 4, '#f6e4bf', .22)
    MN.halftone(cv, -10, 900, W + 10, H + 10, '#000000', 16, 4, 'down', .35)


# ---------------------------------------------------------------- Kamera
def _kf(u, keys):
    if u <= keys[0][0]:
        return keys[0][1:]
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(keys, keys[1:]):
        if u <= t1:
            k = eio(prog(u, t0, t1))
            return lerp(x0, x1, k), lerp(y0, y1, k), math.exp(lerp(math.log(z0), math.log(z1), k))
    return keys[-1][1:]


Z_IN = 18.5
SHOT_ROOM = [(5.6, 960, 540, 1.0), (P11S, 990, 542, 1.04), (12.8, 1440, 540, 2.0), (CUT_GAL0, 1470, 535, 2.12)]
SHOT_GAL = [(CUT_GAL0, 560, 400, 1.85), (CUT_GAL1, 660, 410, 1.95)]
SHOT_SNAKE = [(CUT_GAL1, 1500, 520, 2.5), (22.9, 1512, 515, 2.62), (24.0, 1512, 515, 2.62), (27.6, 1258, 520, 1.45),
              (50.0, 1240, 525, 1.5), (P13S + 2.8, 1240, 525, 1.5), (55.6, 1500, 560, 2.4), (CRACK0, 1495, 562, 2.5),
              (BRANCH1 + .3, 1480, 570, 3.0), (CUT_PORT, 1478, 566, 3.05)]
SHOT_PORT = [(CUT_PORT, PCX, PCY + 15, 3.0), (64.8, PCX, PCY, 6.6), (FILM0, PCX, PCY, 6.8)]


def cam_long(u):
    if u < 5.6:
        k = eio(prog(u, 0.45, 5.6))
        z = math.exp(lerp(math.log(Z_IN), 0.0, k))
        sx = lerp(W / 2, BALL_X, k)
        sy = lerp(H / 2, BALL_Y, k)
        return BALL_X - (sx - W / 2) / z, BALL_Y - (sy - H / 2) / z, z
    if u < CUT_GAL0:
        return _kf(u, SHOT_ROOM)
    if u < CUT_GAL1:
        return _kf(u, SHOT_GAL)
    if u < CUT_PORT:
        return _kf(u, SHOT_SNAKE)
    return _kf(u, SHOT_PORT)


# ---------------------------------------------------------------- Karten: die drei Annahmen
CARDS = [('I', ('Machines can do almost every job,', 'cheaper than us.')),
         ('II', ('Companies replace workers', 'whenever it’s cheaper.')),
         ('III', ('The world runs as today:', 'the many buy, the many vote.'))]
CX0, CW, CH = 90, 960, 168
CY = [300, 500, 700]


def fit_font(tf, size, lines, maxw):
    f = skia.Font(tf, size)
    while max(f.measureText(l) for l in lines) > maxw and size > 20:
        size -= 1
        f = skia.Font(tf, size)
    return size


def wax_seal(cv, x, y, r, a=1.0):
    pts = []
    for i in range(36):
        th = i / 36 * 2 * math.pi
        rr = r * (1 + .07 * math.sin(i * 2.7) + .05 * math.sin(i * 5.3 + 1))
        pts.append((x + rr * math.cos(th), y + rr * math.sin(th)))
    blob = poly(pts)
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .35 * a))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5))
    cv.save()
    cv.translate(3, 5)
    cv.drawPath(blob, sh)
    cv.restore()
    MN.flat(cv, blob, GOLD, GOLD_SH, GOLD_HI, r * .14, r * .08, a=a, line=2)
    cv.drawCircle(x, y, r * .72, strokep(cv, 3, GOLD_DK, .9 * a))
    cv.drawCircle(x, y, r * .62, strokep(cv, 1.4, GOLD_DK, .7 * a))
    for i in range(16):
        th = i / 16 * 2 * math.pi
        cv.drawCircle(x + r * .67 * math.cos(th), y + r * .67 * math.sin(th), 1.6, fillp(cv, GOLD_DK, .8 * a, False))
    text(cv, 'GRANTED', x, y + r * .11, TF_CAPS, r * .3, '#5a3f12', a, anchor='c', spacing=.5)


def vcard(cv, x, y, roman, lines, rv, stamp, glow, idx):
    if rv <= 0:
        return
    k = eout(rv)
    a = clamp(rv * 1.6)
    rot = lerp(-7, (-.8, .6, -.4)[idx], k)
    cv.save()
    cv.translate(x + lerp(-220, 0, k) + CW / 2, y + CH / 2)
    cv.rotate(rot)
    cv.translate(-CW / 2, -CH / 2)
    if glow > 0:
        cv.drawRect(skia.Rect.MakeXYWH(-10, -10, CW + 20, CH + 20), glowp(cv, GOLD_HI, 26, .45 * glow * a))
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .5 * a))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
    cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(10, 16, CW, CH), 10, 10), sh)
    card = MN.rect(0, 0, CW, CH, 10)
    MN.flat(cv, card, '#e9dfc4', '#cbbd99', '#f4ecd8', 8, 4, a=a, line=2.4)
    cv.drawRect(skia.Rect.MakeLTRB(14, 14, CW - 14, CH - 14), strokep(cv, 2.4, '#8a6a33', .9 * a))
    cv.drawRect(skia.Rect.MakeLTRB(22, 22, CW - 22, CH - 22), strokep(cv, 1.1, '#8a6a33', .7 * a))
    for (cx_, cy_) in ((22, 22), (CW - 22, 22), (22, CH - 22), (CW - 22, CH - 22)):
        cv.drawCircle(cx_, cy_, 4, fillp(cv, '#8a6a33', a, False))
    nx, ny = 92, CH / 2
    cv.drawCircle(nx, ny, 46, fillp(cv, '#3a1d1a', a))
    cv.drawCircle(nx, ny, 46, strokep(cv, 3, GOLD, a))
    cv.drawCircle(nx, ny, 46, M.ink(cv, 2, a))
    text(cv, roman, nx, ny + 17, TF_TITLE, 46 if len(roman) < 3 else 38, GOLD, a, anchor='c')
    tx0, tx1 = 168, CW - 168
    fs = min(fit_font(TF_D, 46, l_, tx1 - tx0) for _, l_ in CARDS)
    for j, ln in enumerate(lines):
        text(cv, ln, tx0, CH / 2 + j * (fs + 8) - (fs + 8) / 2 + fs * .35, TF_D, fs, '#241c14', a)
    if stamp > 0:
        sp = eout(clamp(stamp / .6))
        s_ = lerp(1.7, 1.0, sp)
        sa = clamp(stamp * 4)
        sxx, syy = CW - 86, CH / 2 + 4
        cv.save()
        cv.translate(sxx, syy)
        cv.scale(s_, s_)
        cv.rotate(lerp(-30, -12, sp))
        wax_seal(cv, 0, 0, 56, sa)
        cv.restore()
        if .6 < stamp < 2.5:
            MN.sparkle(cv, sxx + 46, syy - 52, 12 * math.sin(math.pi * prog(stamp, .6, 2.5)), a=.9)
    cv.restore()


def cards(cv, u):
    fade = 1 - prog(u, P13S + 2.6, P13S + 3.5)
    if fade <= 0 or u < P12S:
        return
    cv.saveLayerAlpha(None, int(255 * fade))
    dim = eio(prog(u, P12S, P12S + 1.0))
    g = skia.Paint()
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(1350, 0)], [col('#0b0a08', .78 * dim), col('#0b0a08', .45 * dim), col('#0b0a08', 0)], [0, .6, 1]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, 1350, H), g)
    ha = eout(prog(u, P12S + .3, P12S + 1.1))
    if ha > 0:
        head = 'THE STORY ASSUMES'
        hw = P.text_w(TF_CAPS, 36, head, 9)
        hx = CX0 + CW / 2
        P.draw_text(cv, head, hx - hw / 2, 222, TF_CAPS, 36, fillp(cv, GOLD, ha, False), spacing=9)
        MN.flourish(cv, hx, 248, 380, GOLD_SH, ha)
    for i, (roman, lines) in enumerate(CARDS):
        rv = prog(u, CARD_ON[i], CARD_ON[i] + .8)
        nxt = CARD_ON[i + 1] if i < 2 else P12S + 23.2
        glow = eout(prog(u, CARD_ON[i], CARD_ON[i] + .5)) * (1 - eout(prog(u, nxt, nxt + .5)))
        glow = max(glow, eout(prog(u, STAMP_ON[i] - .05, STAMP_ON[i] + .2)) * (1 - prog(u, STAMP_ON[i] + .6, STAMP_ON[i] + 1.4)))
        stamp = max(0.0, u - STAMP_ON[i] + .25) if u > STAMP_ON[i] - .25 else 0.0
        vcard(cv, CX0, CY[i], roman, lines, rv, stamp, glow, i)
    cv.restore()


# ---------------------------------------------------------------- Portraet der 1950er -> alter Film
def reuther_scene(cv, t, band=True):
    """Ford-Motorenwerk, fruehe 1950er: Werksleiter und Walter Reuther vor den Maschinen (ohne Sprechblase)."""
    cv.drawPaint(fillp(cv, '#1b1d1c', 1, False))
    cv.save()
    z = lerp(1.0, 1.05, clamp(t / 5))
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-W / 2, -H / 2)
    for row in range(3):
        y = 160 + row * 150
        scale = 1 - row * .18
        for k in range(14):
            x = -40 + k * 150 * scale + row * 40
            w, h = 120 * scale, 110 * scale
            box = skia.Path()
            box.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), 8, 8))
            cv.drawPath(box, fillp(cv, mix('#2c302e', '#1b1d1c', row * .35), 1))
            cv.drawPath(box, M.ink(cv, 2))
            rnd = random.Random(k * 7 + row)
            for j in range(4):
                c = rnd.choice(['#7fc48f', GOLD, '#7fc48f', '#3d413f'])
                on = (int(t * 3 + k + j * 2 + row) % 5) != 0
                lx, ly = x + 18 * scale + j * 24 * scale, y + 26 * scale
                if c != '#3d413f' and on:
                    cv.drawCircle(lx, ly, 9 * scale, glowp(cv, c, 5, .5))
                cv.drawCircle(lx, ly, 5 * scale, fillp(cv, c if on else '#3d413f', 1, False))
            cv.drawRect(skia.Rect.MakeXYWH(x + 14 * scale, y + 52 * scale, w - 28 * scale, 40 * scale), fillp(cv, '#232625', 1, False))
    haze = skia.Paint()
    haze.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 120), skia.Point(0, 620)], [col('#1b1d1c', .75), col('#1b1d1c', 0)]))
    cv.drawRect(skia.Rect.MakeLTRB(0, 0, W, 640), haze)
    cv.drawRect(skia.Rect.MakeLTRB(0, 640, W, H), fillp(cv, '#151716', 1, False))
    cv.drawLine(0, 640, W, 640, M.ink(cv, 2.6))
    for k in range(-8, 14):
        cv.drawLine(960 + k * 50, 640, 960 + k * 230, H, strokep(cv, 1.5, '#1c1e1d', 1))
    F.spot(cv, 960, -80, 80, 960, 1000, 1300, .4)
    ft = INTER0 - CUT_PORT
    sp_r = prog(t, ft - 1.25, ft - 1.05) * (1 - prog(t, ft - .1, ft))
    sp_l = prog(t, 1.0, 1.2) * (1 - prog(t, ft - 1.6, ft - 1.4))
    mouth_r = .15 + .85 * abs(math.sin(t * 11)) * sp_r
    mouth_l = .1 + .8 * abs(math.sin(t * 9 + 1)) * sp_l
    person_profile(cv, 740, 680, 225, t, facing=1, hair='A', glasses=True, look=-4, mouth=mouth_l)
    person_profile(cv, 1250, 680, 225, t + 1.3, facing=-1, hair='B', look=3, mouth=mouth_r,
                   palette={'suit': '#2e2c2a', 'tie': GOLD_DK})
    cv.restore()
    if band:
        cv.drawRect(skia.Rect.MakeLTRB(0, 940, W, H), fillp(cv, '#0e0c0a', .85, False))
        P.draw_text(cv, 'CLEVELAND, OHIO  ·  EARLY 1950s', 90, 1004, TF_CAPS, 30, fillp(cv, '#e9e1c9', 1, False), spacing=9)
        P.draw_text(cv, 'Walter Reuther, United Auto Workers, at a Ford engine plant', 90, 1046, TF_HEAD, 24,
                    fillp(cv, '#bdb6a4', 1, False))


FILM_SURF = None


def film_frame(t, frame, band=True):
    global FILM_SURF
    if FILM_SURF is None:
        FILM_SURF = skia.Surface(W, H)
    cv = FILM_SURF.getCanvas()
    cv.clear(skia.ColorBLACK)
    P.G.zoom = 1.0
    reuther_scene(cv, t, band)
    arr = K.film_look(K.snap(FILM_SURF), 'bw', seed=900 + frame, scratches=5, dust=40, vign=.45, grain=.03)
    return weave(arr, frame, 2)


def weave(arr, frame, amp=3):
    rng = np.random.default_rng(1000 + frame)
    dx, dy = int(rng.integers(-amp, amp + 1)), int(rng.integers(-amp, amp + 1))
    out = np.roll(np.roll(arr, dy, axis=0), dx, axis=1)
    f = rng.uniform(.93, 1.04)
    out[..., :3] = np.clip(out[..., :3].astype(np.float32) * f, 0, 255).astype(np.uint8)
    return out


def portrait_into(cv, u):
    """Hochaufgeloestes Portraet der 1950er; beim Hineinfahren laeuft darin schon der alte Film."""
    ei, x, y, w, h, ov = PORT
    inner = MN.oval(x, y, w, h)
    cv.save()
    cv.clipPath(inner, doAntiAlias=True)
    cv.drawImageRect(HIRES_PORT, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
    fk = eio(prog(u, CUT_PORT + 0.9, CUT_PORT + 1.9))
    if fk > 0:
        img = K.to_img(film_frame(u - CUT_PORT, int(u * FPS), band=False))
        ih = H / SHOT_PORT[-1][3]
        iw = ih * W / H
        p = skia.Paint(AntiAlias=True)
        p.setAlphaf(fk)
        cv.drawImageRect(img, skia.Rect.MakeXYWH(x + w / 2 - iw / 2, y + h / 2 - ih / 2, iw, ih),
                         skia.SamplingOptions(skia.FilterMode.kLinear), p)
    sh = skia.Paint()
    sh.setShader(skia.GradientShader.MakeLinear([skia.Point(x, y), skia.Point(x, y + h * .35)], [col('#000000', .35), col('#000000', 0)]))
    cv.drawRect(skia.Rect.MakeXYWH(x, y, w, h), sh)
    cv.restore()
    cv.drawPath(inner, M.ink(cv, 2.4))


def person_profile(*a, **k):
    return RB.person_profile(*a, **k)


# ---------------------------------------------------------------- Zwischentitel
def intertitle_q(cv):
    cv.drawPaint(fillp(cv, '#0e0d0c', 1, False))
    x0, y0, x1, y1 = 150, 95, W - 150, H - 95
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), strokep(cv, 4, CREAM, .9))
    cv.drawRect(skia.Rect.MakeLTRB(x0 + 18, y0 + 18, x1 - 18, y1 - 18), strokep(cv, 2, CREAM, .7))
    for (x, y, sx, sy) in ((x0 + 18, y0 + 18, 1, 1), (x1 - 18, y0 + 18, -1, 1), (x0 + 18, y1 - 18, 1, -1), (x1 - 18, y1 - 18, -1, -1)):
        K.deco_corner(cv, x, y, sx, sy)
    for k in range(9):
        xx = 960 + (k - 4) * 28
        cv.drawLine(xx, y0 + 18, xx, y0 + 40 - abs(k - 4) * 4, strokep(cv, 2, CREAM, .7))
        cv.drawLine(xx, y1 - 18, xx, y1 - 40 + abs(k - 4) * 4, strokep(cv, 2, CREAM, .7))
    lines = ('“How are you going', 'to get them to buy cars?”')
    fs = fit_font(TF_D, 112, lines, 1480)
    for j, ln in enumerate(lines):
        f = skia.Font(TF_D, fs)
        w_ = f.measureText(ln)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(ln, f), 960 - w_ / 2, 470 + j * (fs + 30), fillp(cv, CREAM, 1, False))
    yy = 470 + 2 * (fs + 30) + 30
    MN.flourish(cv, 960, yy - 24, 420, CREAM, .85)
    lw = P.text_w(TF_CAPS, 30, 'WALTER REUTHER', 12)
    P.draw_text(cv, 'WALTER REUTHER', 960 - lw / 2, yy + 40, TF_CAPS, 30, fillp(cv, CREAM, .95, False), spacing=12)
    sub = 'UNITED AUTO WORKERS  ·  EARLY 1950s'
    lw = P.text_w(TF_CAPS, 20, sub, 7)
    P.draw_text(cv, sub, 960 - lw / 2, yy + 84, TF_CAPS, 20, fillp(cv, CREAM, .7, False), spacing=7)


INTER = None


def inter_frame(frame):
    global INTER
    if INTER is None:
        surf = skia.Surface(W, H)
        P.G.zoom = 1.0
        intertitle_q(surf.getCanvas())
        INTER = K.snap(surf)
    return weave(K.film_look(INTER, 'bw', seed=1500 + frame, scratches=6, dust=55, vign=.45, grain=.03), frame, 2)


# ---------------------------------------------------------------- Etikett STORY
def story_label(cv, a):
    if a <= 0:
        return
    cv.drawLine(80, 92, 150, 92, P.P_ink(2.5, GOLD, a, False))
    P.draw_text(cv, 'STORY', 170, 102, TF_CAPS, 28, P.P_fill(GOLD, a, False), spacing=9)


# ---------------------------------------------------------------- Titelkarte mit den Farben der neuen Schlange
def s_title2(cv, t):
    keep = (RB.SNAKE, RB.SNAKE_SH, RB.SNAKE_HI, RB.BELLY, RB.BELLY_SH)
    RB.SNAKE, RB.SNAKE_SH, RB.SNAKE_HI, RB.BELLY, RB.BELLY_SH = M.SN, M.SN_SPOT, M.SN_RIM, M.SN_BELLY, M.SN_BELLY_SH
    R.s_title(cv, t)
    RB.SNAKE, RB.SNAKE_SH, RB.SNAKE_HI, RB.BELLY, RB.BELLY_SH = keep


# ---------------------------------------------------------------- Bild
def to_arr(surface):
    return surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def blend(a, b, k):
    out = a.copy()
    out[..., :3] = (a[..., :3].astype(np.float32) * (1 - k) + b[..., :3].astype(np.float32) * k).astype(np.uint8)
    return out


def darken(arr, k):
    out = arr.copy()
    out[..., :3] = (out[..., :3].astype(np.float32) * k).astype(np.uint8)
    return out


def salon_frame(surface, u):
    cv = surface.getCanvas()
    cv.clear(col('#0d0b0a'))
    cv.save()
    cx, cy, z = cam_long(u)
    R.cam(cv, cx, cy, z)
    salon_dyn(cv, u)
    cv.restore()
    P.G.zoom = 1.0
    cards(cv, u)
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(u, 0, .4)))))
    story_label(cv, 1 - prog(u, 1.9, 2.6))
    return to_arr(surface)


def render_frame(surface, frame):
    t = frame / FPS
    G.frame = frame
    P.G.frame = frame
    P.G.zoom = 1.0
    if t < L0:
        cv = surface.getCanvas()
        cv.clear(col(BG))
        cv.save()
        R.s_lastjob(cv, t * 6.4 / 7.2)
        cv.restore()
        P.G.zoom = 1.0
        story_label(cv, eout(prog(t, 0.0, 0.5)))
        return to_arr(surface)
    if t >= TITLE0:
        cv = surface.getCanvas()
        cv.clear(col(BG))
        cv.save()
        s_title2(cv, t - TITLE0)
        cv.restore()
        return to_arr(surface)
    u = t - L0
    if u < 64.6:
        return salon_frame(surface, u)
    if u < FILM0:
        a = salon_frame(surface, u)
        b = film_frame(u - CUT_PORT, frame, band=True)
        s_ = cam_long(u)[2] / SHOT_PORT[-1][3]
        cv = surface.getCanvas()
        cv.clear(skia.ColorBLACK)
        cv.save()
        cv.translate(W / 2, H / 2)
        cv.scale(s_, s_)
        cv.translate(-W / 2, -H / 2)
        cv.drawImage(K.to_img(b), 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        cv.restore()
        return blend(a, to_arr(surface), eio(prog(u, 64.6, FILM0)))
    if u < INTER0:
        return film_frame(u - CUT_PORT, frame, band=True)
    arr = inter_frame(frame)
    k = eout(prog(u, INTER0, INTER0 + .15)) * (1 - prog(u, LONG - .5, LONG))
    return darken(arr, k)


def main():
    mode = sys.argv[1]
    if mode == 'audio':
        make_audio(sys.argv[2])
        return
    if mode == 'info':
        print('TOTAL', TOTAL, 'frames', int(TOTAL * FPS), 'L0', L0, 'TITLE0', TITLE0, 'LONG', LONG)
        return
    P.init_assets()
    R.init_layers()
    surface = skia.Surface(W, H)
    post = P.Post()
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
