#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Entwurf des Videoanfangs (v5): Prophezeiung P-01 bis P-15 mit echter Stimme.

Bildspur:  python3 start.py render <startframe> <endframe> <out.mp4>
Standbild: python3 start.py still <sekunde> <out.png> [...]
Tonspur:   python3 start.py audio <out.wav>
"""
import math, random, subprocess, sys, os
import numpy as np
import skia
import rich as R
from rich_base import *

P.SUBS = []  # mit echter Stimme keine eingebrannten Untertitel
BX, BY, BR = R.BX, R.BY, R.BR
REPO = os.environ.get('VIDEO_REPO', '/home/claude/tides-of-magic/will-ai-buy-our-cars')

# Stufen der Menge an die Stimme angepasst (lokale Sekunden der Szene)
R.STAGES6 = [(4, .4, '1 IN 10'), (10, 3.7, '1 IN 4'), (20, 5.8, '1 IN 2')]

# ---------------------------------------------------------------- Zeitplan der Stimme in der langen Szene (lokal)
P11S = 10.0
P11E = P11S + 16.20
P12S = 27.0
P12E = P12S + 23.17
P13S = P12E + 0.7
P13E = P13S + 11.08
P14S = P13E + 0.6
P14E = P14S + 5.25
LONG = P14E + 1.15

CARD_ON = [P12S + 3.6, P12S + 9.05, P12S + 12.97]
STAMP_ON = [P13S + 1.45, P13S + 1.8, P13S + 2.15]
CRACK0, CRACK1 = P13S + 6.9, P13S + 9.0
BRANCH1 = P13S + 10.6
SPLIT0 = P14S
CARD_TEXT = [('1', 'MACHINES CAN DO ALMOST EVERY JOB, CHEAPER THAN US'),
             ('2', "COMPANIES REPLACE WORKERS WHENEVER IT'S CHEAPER"),
             ('3', 'THE WORLD RUNS AS TODAY: THE MANY BUY, THE MANY VOTE')]
CARD_X, CARD_Y, CARD_W, CARD_H = 2120, [340, 540, 740], 1080, 150
SLIP_X, SLIP_Y = BX + 40, BY + 20

# Kamera: (lokale Zeit, cx, cy, zoom); dazwischen weich, Zoom logarithmisch
CAM = [
    (0.3, BX, BY + 60, 3.6),
    (5.0, 960, 560, 1.0),
    (10.0, 960, 560, 1.0),
    (11.0, 960, 560, 1.1),
    (P11E - 0.2, 980, 560, 1.12),
    (P12S + 0.6, 1700, 540, 0.85),
    (P13S + 2.3, 1720, 540, 0.86),
    (P13S + 3.9, BX, BY + 20, 1.55),
    (P14S + 1.0, BX + 10, BY + 20, 1.58),
    (P14S + 2.6, SLIP_X, SLIP_Y, 1.5),
    (LONG, SLIP_X, SLIP_Y, 1.56),
]


def cam_at(u):
    if u <= CAM[0][0]:
        return CAM[0][1:]
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAM, CAM[1:]):
        if u <= t1:
            k = eio(prog(u, t0, t1))
            return lerp(x0, x1, k), lerp(y0, y1, k), math.exp(lerp(math.log(z0), math.log(z1), k))
    return CAM[-1][1:]


def ball_halves(cv, u, split):
    """Kugel mit Riss; split>0 bricht sie in zwei Haelften auf."""
    main = P.crack_points(BR)
    branches = P.crack_branches(BR, main)
    cp = eio(prog(u, CRACK0, CRACK1))
    bp = eio(prog(u, CRACK1, BRANCH1))
    leak = bp * (.6 + .4 * math.sin(u * 6)) if u < SPLIT0 else 0
    if split <= 0:
        R.crystal_ball(cv, u)
        if cp > 0:
            cv.save()
            cv.translate(BX, BY)
            cv.clipPath(circle(0, 0, BR), doAntiAlias=True)
            mp = trim(poly(main, close=False), cp)
            lg = strokep(cv, 6 + 18 * bp, GOLD_HI, .5 + .4 * bp)
            lg.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8 + 10 * bp))
            cv.drawPath(mp, lg)
            cv.drawPath(mp, inkp(cv, 3.5, INK, 1, wob=False))
            cv.drawPath(mp, strokep(cv, 2 + 3 * bp, '#fff3d0', .9 * bp))
            for b in branches:
                bpth = trim(poly(b, close=False), bp)
                cv.drawPath(bpth, lg)
                cv.drawPath(bpth, inkp(cv, 2.6, INK, 1, wob=False))
                cv.drawPath(bpth, strokep(cv, 1.5 + 2 * bp, '#fff3d0', .9 * bp))
            cv.restore()
            if leak > 0:
                cv.drawCircle(BX, BY + BR * .2, BR * .8, glowp(cv, GOLD_HI, 60, .25 * leak))
        return
    left = poly(main + [(-BR * 3, BR * 3), (-BR * 3, -BR * 3), (0, -BR * 3)])
    right = poly(main + [(BR * 3, BR * 3), (BR * 3, -BR * 3), (0, -BR * 3)])
    cv.drawCircle(BX, BY, BR * 1.1, glowp(cv, GOLD_HI, 110, .25 + .2 * (1 - prog(u, SPLIT0, SPLIT0 + 2.0))))
    cv.drawCircle(BX, BY, BR * .7, glowp(cv, '#fff3d0', 60, .5 * (1 - eout(prog(u, SPLIT0 + .1, SPLIT0 + 1.3)))))
    for (reg, sx) in ((left, -1), (right, 1)):
        cv.save()
        cv.translate(BX + sx * 175 * split, BY + 30 * split)
        cv.rotate(sx * 12 * split)
        cv.translate(-BX, -BY)
        cv.save()
        cv.translate(BX, BY)
        cv.clipPath(reg, doAntiAlias=True)
        cv.translate(-BX, -BY)
        R.crystal_ball(cv, u)
        cv.restore()
        cv.save()
        cv.translate(BX, BY)
        cv.clipPath(circle(0, 0, BR), doAntiAlias=True)
        cv.drawPath(poly(main, close=False), inkp(cv, 4, INK, 1, wob=False))
        cv.drawPath(poly(main, close=False), strokep(cv, 3, '#fff3d0', .8))
        cv.restore()
        cv.restore()


def snake_and_ball(cv, u, ang, lid, tongue, smirk, pupil, split):
    head = (BX - BR * 1.12, BY - BR * .62 + 6 * math.sin(u * 1.1), ang)
    coil, neck = R.coil_pts(u, head)
    nt = len(coil) + len(neck)
    wd_all = []
    for i in range(nt):
        q = i / (nt - 1)
        wd_all.append(lerp(10, 66, q / .18) if q < .18 else (66 if q < .75 else lerp(66, 54, (q - .75) / .25)))
    rs = R.runs(coil, wd_all[:len(coil)])
    for (front, p, w) in rs:
        if not front:
            snake_body(cv, p, w, belly=.55)
    ball_halves(cv, u, split)
    fr = [r_ for r_ in rs if r_[0]]
    for k, (front, p, w) in enumerate(fr):
        if k == len(fr) - 1:
            snake_body(cv, p + neck, w + wd_all[len(coil):], belly=.4, bdir=(.6, .8))
        else:
            snake_body(cv, p, w, belly=.55)
    snake_head(cv, head[0], head[1], ang, 76, lid=lid, tongue=tongue, smirk=smirk, pupil=pupil)
    ar = math.radians(ang)
    ext = neck[-8:] + [(head[0] + math.cos(ar) * 76 * k, head[1] + math.sin(ar) * 76 * k, 1.0) for k in (.12, .24, .34)]
    snake_body(cv, ext, [54 + 6 * i / (len(ext) - 1) for i in range(len(ext))], belly=.4, bdir=(.6, .8))


def cards(cv, u):
    fade = 1 - prog(u, P13S + 2.6, P13S + 3.6)
    if fade <= 0:
        return
    cv.saveLayerAlpha(None, int(255 * fade))
    _cards(cv, u)
    cv.restore()


def _cards(cv, u):
    ha = eout(prog(u, P12S + .3, P12S + 1.1))
    if ha > 0:
        head = 'THE PROPHECY ASSUMES'
        hw = P.text_w(P.TF_CAPS, 34, head, 8)
        P.draw_text(cv, head, CARD_X - hw / 2, 215, P.TF_CAPS, 34, P.P_fill(GOLD, ha, False), spacing=8)
    for i, (num, text) in enumerate(CARD_TEXT):
        rv = prog(u, CARD_ON[i], CARD_ON[i] + .9)
        if rv <= 0:
            continue
        nxt = CARD_ON[i + 1] if i < 2 else P12E
        glow = eout(prog(u, CARD_ON[i], CARD_ON[i] + .5)) * (1 - eout(prog(u, nxt, nxt + .5)))
        glow = max(glow, eout(prog(u, STAMP_ON[i] - .1, STAMP_ON[i] + .2)) * (1 - prog(u, STAMP_ON[i] + .6, STAMP_ON[i] + 1.4)))
        P.G.zoom = mscale(cv)
        P.draw_card(cv, CARD_X, CARD_Y[i], CARD_W, CARD_H, num, text, rv, prog(u, STAMP_ON[i], STAMP_ON[i] + .25), glow, u)


def s_long(cv, u):
    """P-10 bis P-14: Kugel und Schlange, die drei Annahmen, der Riss, der Zettel."""
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    cv.save()
    cx, cy, z = cam_at(u)
    R.cam(cv, cx, cy, z)
    split = eout(prog(u, SPLIT0, SPLIT0 + .8))
    cv.drawCircle(BX, BY, BR * 1.45, glowp(cv, GOLD_HI, 120, .22 + .2 * eout(prog(u, CRACK1, BRANCH1))))
    sh = skia.Paint(AntiAlias=True, Color=col('#000000', .55))
    sh.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30))
    cv.drawOval(skia.Rect.MakeXYWH(BX - BR * 1.35, BY + BR * 1.12, BR * 2.7, BR * .5), sh)
    tilt = eio(prog(u, 10.0, 11.0))
    to_cards = eio(prog(u, P12S - .6, P12S + .6)) * (1 - eio(prog(u, P13S + 2.4, P13S + 3.6)))
    nod = sum(9 * math.sin(math.pi * prog(u, s - .15, s + .3)) for s in STAMP_ON)
    ang = lerp(8, -12, tilt) + 3 * math.sin(u * .8) + 6 * to_cards + nod
    ang += -8 * eout(prog(u, CRACK0, CRACK1)) * (1 - eio(prog(u, SPLIT0 + 1.0, SPLIT0 + 2.0)))
    lid = .2 + .25 * eout(prog(u, 10.0, 10.6)) - .25 * eout(prog(u, 15.0, 15.4))
    lid -= .2 * eout(prog(u, P11S + 10.9, P11S + 11.4)) * (1 - eout(prog(u, P11S + 13.6, P11S + 14.2)))
    lid -= .2 * eout(prog(u, CRACK0, CRACK0 + .6))
    lid = max(0.0, lid)
    tongue = max(prog(u, 6.0, 6.5), prog(u, 13.4, 13.9), prog(u, 17.4, 17.9), prog(u, P11S + 13.9, P11S + 14.4),
                 prog(u, P12S + 1.0, P12S + 1.5), prog(u, SPLIT0 + 1.2, SPLIT0 + 1.7))
    pupil = lerp(1, .7, eout(prog(u, 15.0, 15.4)))
    pupil = lerp(pupil, 1.15, eout(prog(u, P11S + 10.9, P11S + 11.4)) * (1 - eout(prog(u, P11S + 13.6, P11S + 14.2))))
    pupil = lerp(pupil, .55, eout(prog(u, CRACK0, CRACK0 + .5)))
    snake_and_ball(cv, u, ang, lid, tongue, .5 + .5 * tilt, pupil, split)
    cards(cv, u)
    if split > 0:
        sp = eout(prog(u, SPLIT0 + .4, SPLIT0 + 1.8))
        sx = lerp(BX, SLIP_X, sp)
        sy = lerp(BY, SLIP_Y, sp)
        P.G.zoom = mscale(cv)
        P.draw_slip(cv, sx, sy, lerp(.15, 1.0, sp), lerp(20, -3, sp), u, prog(u, P14S + 1.2, P14S + 2.4),
                    prog(u, P14S + 3.8, P14S + 5.4), min(1, sp * 3))
        if u < SPLIT0 + 2.5:
            rnd = random.Random(5)
            for k in range(26):
                a_ = rnd.uniform(0, 6.28)
                v = rnd.uniform(200, 520)
                tt = u - SPLIT0
                x = BX + math.cos(a_) * v * tt
                y = BY + math.sin(a_) * v * tt + 260 * tt * tt
                cv.drawPath(poly([(x, y), (x + 14, y + 4), (x + 4, y + 15)]), fillp(cv, '#fff3d0', .8 * (1 - prog(tt, .6, 2.4)), False))
    R.dust(cv, u, (BX - 500, BY - 400, BX + 500, BY + 400), 30, 9, GOLD_HI, .4)
    cv.restore()
    cv.drawPaint(skia.Paint(Color=col('#000000', 1 - eout(prog(u, 0, .4)))))
    cv.drawPaint(skia.Paint(Color=col('#000000', .85 * prog(u, LONG - .5, LONG))))


def scaled(fn, nominal, actual):
    return lambda cv, t: fn(cv, t * nominal / actual)


SEQ = [
    (R.s_city, 9.0), (R.s_eden, 7.6), (R.s_contract, 4.4), (R.s_split, 4.0), (R.s_never, 4.6),
    (R.s_towers, 6.0), (R.s_papers, 6.2), (R.s_crowd, 8.2), (R.s_showroom, 7.6),
    (scaled(R.s_lastjob, 6.4, 7.2), 7.2), (s_long, LONG), (R.s_title, 6.0),
]
SCENES = []
_t = 0.0
for fn, d in SEQ:
    SCENES.append((_t, _t + d, fn))
    _t += d
TOTAL = _t
LONG0 = SCENES[10][0]
TITLE0 = SCENES[11][0]

# ---------------------------------------------------------------- Ton
VOICE = [  # Datei, von, bis (None = Ende), Startzeit im Video
    ('P-01', 0, None, 0.8), ('P-02', 0, None, 4.4), ('P-03', 0, None, 9.4),
    ('P-04', 0, 1.67, 17.0), ('P-04', 1.67, 3.31, 21.2), ('P-04', 3.31, 4.88, 23.1), ('P-04', 4.88, None, 25.3),
    ('P-05', 0, None, 30.0), ('P-06', 0, None, 36.0),
    ('P-07', 0, 3.12, 42.2), ('P-07', 3.12, 4.77, 45.5), ('P-07', 4.77, None, 47.6),
    ('P-08', 0, None, 50.4),
    ('P-09', 0, 4.28, 58.0), ('P-09', 4.28, None, 62.5),
    ('P-10', 0, None, LONG0 + 0.8), ('P-11', 0, None, LONG0 + P11S), ('P-12', 0, None, LONG0 + P12S),
    ('P-13', 0, None, LONG0 + P13S), ('P-14', 0, None, LONG0 + P14S),
]
MUSIC = [  # Datei, Quellstart, Start, Ende, Einblenden, Ausblenden, Pegel
    ('music/01_P-01_bis_P-09_Cyclical-Darkness.mp3', 0.0, 0.0, LONG0 + 1.6, 2.0, 2.4, 1.0),
    ('music/02_P-10_bis_P-14_Have-We-Met-Before.mp3', 0.0, LONG0 - 0.6, TITLE0 + 6.0, 2.5, 3.0, 1.0),
]
SFX = [  # Datei, Quellstart, Laenge, Start, Pegel
    ('sfx/01_grollen_EDEN-steigt-auf.mp3', 0.0, 6.5, 1.6, .55),
    ('sfx/02_servo_roboterarme.mp3', 0.0, 1.3, 9.0 + 4.5, .35),
    ('sfx/02_servo_roboterarme.mp3', 1.6, 1.2, 9.0 + 4.9, .28),
    ('sfx/02_servo_roboterarme.mp3', 0.0, 1.0, 16.6, .3),
    ('sfx/03_stift_unterschrift.mp3', None, 1.5, 17.2, .55),
    ('sfx/04_stempel.mp3', None, .7, 16.6 + 2.2, .7),
    ('sfx/05_zeitung_auf-tisch.mp3', 0.0, .43, 35.6 + .62, .55),
    ('sfx/05_zeitung_auf-tisch.mp3', 0.0, .43, 35.6 + 1.12, .45),
    ('sfx/05_zeitung_auf-tisch.mp3', 0.0, .43, 35.6 + 1.82, .55),
    ('sfx/05_zeitung_auf-tisch.mp3', 0.0, .43, 35.6 + 3.62, .65),
    ('sfx/02_servo_roboterarme.mp3', 0.0, 1.2, 57.6 + 4.5, .3),
    ('sfx/04_stempel.mp3', None, .7, LONG0 + STAMP_ON[0], .6),
    ('sfx/04_stempel.mp3', None, .7, LONG0 + STAMP_ON[1], .6),
    ('sfx/04_stempel.mp3', None, .7, LONG0 + STAMP_ON[2], .7),
    ('sfx/07_glas-riss_kugel.mp3', 0.0, 3.0, LONG0 + CRACK0, .5),
    ('sfx/07_glas-riss_kugel.mp3', 0.0, 2.2, LONG0 + SPLIT0, .85),
    ('music/03_P-15_Designed-Boom-Impact-Dark-Cinematic-Bright-Tone.mp3', 0.0, 5.3, TITLE0 + .2, .9),
]
SR = 48000


def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def first_onset(a, thr=.05):
    e = np.abs(a).max(axis=1)
    idx = np.argmax(e > thr * e.max())
    return max(0, idx - int(.01 * SR)) / SR


def busiest(a, length):
    e = np.convolve(np.abs(a).mean(axis=1), np.ones(int(length * SR)), 'valid')
    return int(np.argmax(e)) / SR


def place(buf, clip, t, gain=1.0, fin=0.005, fout=0.02):
    clip = clip.copy()
    n = len(clip)
    fi, fo = max(1, int(fin * SR)), max(1, int(fout * SR))
    clip[:fi] *= np.linspace(0, 1, fi)[:, None]
    clip[-fo:] *= np.linspace(1, 0, fo)[:, None]
    i0 = int(t * SR)
    i1 = min(len(buf), i0 + n)
    buf[i0:i1] += clip[:i1 - i0] * gain


def rms_db(x):
    return 20 * math.log10(max(1e-9, float(np.sqrt(np.mean(x ** 2)))))


def make_audio(out):
    n = int((TOTAL + 1) * SR)
    voice = np.zeros((n, 2), np.float32)
    for (name, a, b, t) in VOICE:
        clip = decode(f'{REPO}/voice/{name}.mp3')
        i0, i1 = int(a * SR), (len(clip) if b is None else int(b * SR))
        place(voice, clip[i0:i1], t, 1.0, .01, .04)
    act = np.abs(voice).max(axis=1) > 1e-4
    vg = 10 ** ((-19 - rms_db(voice[act])) / 20)
    voice *= vg
    # Ducking-Huellkurve aus der Stimme
    hop = int(.02 * SR)
    env = np.sqrt(np.convolve((voice ** 2).mean(axis=1), np.ones(hop) / hop, 'same'))
    env = (env > 10 ** (-40 / 20)).astype(np.float32)
    sm = np.zeros_like(env)
    att, rel = 1 - math.exp(-1 / (.08 * SR)), 1 - math.exp(-1 / (.6 * SR))
    acc = 0.0
    for i in range(0, len(env), hop):
        target = env[i]
        k = att if target > acc else rel
        acc += (target - acc) * (1 - (1 - k) ** hop)
        sm[i:i + hop] = acc
    music = np.zeros((n, 2), np.float32)
    for (path, src0, t0, t1, fin, fout, lvl) in MUSIC:
        m = decode(f'{REPO}/{path}')
        seg = m[int(src0 * SR):int((src0 + t1 - t0) * SR)]
        seg = seg * 10 ** ((-25 - rms_db(seg)) / 20) * lvl
        place(music, seg, t0, 1.0, fin, fout)
    duck = 1 - .62 * sm
    music *= duck[:, None]
    sfx = np.zeros((n, 2), np.float32)
    for (path, src0, ln, t, gain) in SFX:
        s = decode(f'{REPO}/{path}')
        if src0 is None:
            src0 = first_onset(s) if 'stempel' in path else busiest(s, ln)
        seg = s[int(src0 * SR):int((src0 + ln) * SR)]
        seg = seg / max(1e-6, np.abs(seg).max()) * .5
        place(sfx, seg, t, gain, .01, min(.3, ln * .3))
    mix = voice + music + sfx
    pk = np.abs(mix).max()
    if pk > .97:
        mix *= .97 / pk
    mix = mix[:int(TOTAL * SR)]
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', out],
                   input=mix.astype(np.float32).tobytes(), check=True)
    print('audio', out, round(TOTAL, 2), 's')


# ---------------------------------------------------------------- Bild
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
    if 1.0 <= t < LONG0:
        P.fiction_label(cv, eout(prog(t, 1.0, 1.6)) * (1 - prog(t, LONG0 - .6, LONG0)))
    return surface.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)


def main():
    mode = sys.argv[1]
    if mode == 'audio':
        make_audio(sys.argv[2])
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
    elif mode == 'info':
        print('TOTAL', TOTAL, 'frames', int(TOTAL * FPS), 'LONG0', LONG0, 'TITLE0', TITLE0)


if __name__ == '__main__':
    main()
