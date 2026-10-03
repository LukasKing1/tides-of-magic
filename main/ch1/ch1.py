"""Chapter 1 - Cold Open: The Legend (0:00-1:31). Main video 16:9.
python3 ch1.py still 1.0,5.2,...        -> stills/c1_XX.png
python3 ch1.py range i0 i1 out.mp4       -> frames [i0, i1)
"""
import math, os, sys
import numpy as np
import skia
from PIL import Image
from lib import *
import book as B
from book import SP, PT, PB, PW, RP, LP, CT, CB, CW, RPATH, LPATH
import pages as PG
import world as WD

D = '/home/claude/main/ch1/'
T_END = 91.0
SCALE = float(os.environ.get('SCALE', '1.0'))   # 1.0 -> 1920x1080, 1.3333 -> 2560x1440
OW, OH = int(round(W * SCALE)), int(round(H * SCALE))

# ------------------------------------------------------------------ voice timeline (seconds in the video)
V = {'Q1': (3.0, 18.0), '01-2': (19.0, 35.0), '01-3': (36.0, 48.0), '01-4': (49.0, 58.0), '01-5': (59.0, 64.0),
     '01-6': (66.0, 79.6), '01-7': (80.0, 85.2)}
T_HIT = 85.5

# ------------------------------------------------------------------ camera helper
def camera(c, cx, cy, z):
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


# ------------------------------------------------------------------ book scenes
FLAP_COVER = (SP, CT, SP + CW, CB)
FLAP_PAGE = RP


def flip_phi(t, t0, t1):
    return math.pi * ease((t - t0) / (t1 - t0))


def left_endpaper(c, t, sig_u=1.0, glow=0.0):
    B.cover_back(c)
    PG.exlibris(c, t, sig_u, glow)


def right_page_base(c):
    B.parch_fill(c, RPATH)


def left_page_base(c):
    B.parch_fill(c, LPATH)


def hand_track(t, windows, rest_r=None, rest_l=None):
    """right/left wrist positions following a turning edge during flip windows"""
    rpos, lpos = None, None
    for (t0, t1, L, side) in windows:
        if t0 - 0.5 <= t <= t1 + 0.6:
            if side == 'r':
                pre = smooth((t - (t0 - 0.5)) / 0.5)
                phi = math.pi * ease((t - t0) / (t1 - t0)) if t >= t0 else 0.0
                follow = clamp(1 - (phi - 1.8) / 0.6) if phi > 1.8 else 1.0
                edge = (SP + L * math.cos(min(phi, 1.8)) * 0.96, PB + 58 - 120 * math.sin(min(phi, 1.8)))
                rest = rest_r or (RP[2] - 96, PB + 70)
                k = pre * follow
                rpos = lerp2(rest, edge, k)
            else:
                pre = smooth((t - (t0 - 0.5)) / 0.5)
                phi = math.pi * (1 - ease((t - t0) / (t1 - t0))) if t >= t0 else math.pi
                follow = clamp((phi - 1.2) / 0.6) if phi < 1.8 else 1.0
                edge = (SP + L * math.cos(max(phi, 1.3)) * 0.96, PB + 58 - 120 * math.sin(max(phi, 1.3)))
                rest = rest_l or (LP[0] + 96, PB + 70)
                lpos = lerp2(rest, edge, pre * follow)
    return rpos, lpos


def book_frame(c, t, phi_cover, right_fn, left_fn, flap=None, overlay=None, head_left=True, hands=True, flips=(), cover_kw=None):
    """generic book view. right_fn/left_fn draw the visible spread under any flap.
    flap = (phi, front_fn, back_fn) for a turning page."""
    cover_kw = cover_kw or {}
    closed = phi_cover < 0.02
    open_k = clamp((phi_cover - 1.4) / (math.pi - 1.4))
    B.lap(c, t)
    B.book_shadow(c, open_k)
    B.book_block(c, left_pages=phi_cover >= math.pi - 0.001)
    if not closed:
        if phi_cover >= math.pi - 0.001:
            left_fn(c)
        right_fn(c)
        B.gutter_shadow(c)
    else:
        right_fn(c)
    if flap is not None:
        phi, front, back = flap
        B.draw_flap(c, phi, front, back, FLAP_PAGE)
        B.flap_shadow(c, phi, PT, PB, PW)
    if 0.0 < phi_cover < math.pi - 0.001:
        B.draw_flap(c, phi_cover, lambda c: B.cover_front(c, **cover_kw), lambda c: left_fn(c), FLAP_COVER)
        B.flap_shadow(c, phi_cover)
    elif closed:
        B.cover_front(c, **cover_kw)
    if overlay:
        overlay(c)
    if hands:
        # resting places: open spread corners, or the closed book's corners
        k = ease(clamp(phi_cover / 1.6))
        rest_l = lerp2((SP + 70, PB + 66), (LP[0] + 96, PB + 70), k)
        rest_r = (RP[2] - 96, PB + 70)
        rpos, lpos = hand_track(t, flips, rest_r=rest_r, rest_l=rest_l)
        B.hands_hold(c, t, lpos=lpos or rest_l, rpos=rpos or rest_r)


# ---- part 1: the legend in the book (0 .. 18.9)
T_COVER1 = (0.45, 1.45)
T_FLIP1 = (2.0, 2.85)


def legend_left(c, t):
    left_page_base(c)
    PG.legend_panel(c, t, 'l')


def legend_right(c, t):
    right_page_base(c)
    PG.legend_panel(c, t, 'r')
    B.running_head(c, alpha=200, left_title='')


def title_right(c, t, q_u=0.0):
    right_page_base(c)
    PG.title_page(c, t, q_u)


def part1(c, t):
    phi_c = math.pi * ease((t - T_COVER1[0]) / (T_COVER1[1] - T_COVER1[0]))
    flip = None
    if t < T_FLIP1[0]:
        right = lambda c: title_right(c, t)
        left = lambda c: left_endpaper(c, t)
    else:
        right = lambda c: legend_right(c, t)
        phi = flip_phi(t, *T_FLIP1)
        if phi < math.pi - 0.001:
            left = lambda c: left_endpaper(c, t)
            flip = (phi, lambda c: title_right(c, t), lambda c: legend_left(c, t))
        else:
            left = lambda c: (left_endpaper(c, t), legend_left(c, t))

    def overlay(c):
        if t >= T_FLIP1[1] - 0.1:
            PG.legend_popups(c, t)
            PG.quote_lines(c, t, clamp((t - V['Q1'][0] - 0.3) / (V['Q1'][1] - V['Q1'][0] - 1.0)))

    # camera: centred on the closed cover, then the spread, slow push, then the dive into the sun
    cx = lerp(SP + CW / 2, SP, eramp(t, 0.4, 2.2))
    cy = 540.0
    z = lerp(1.06, 1.0, eramp(t, 0.4, 2.2)) * (1 + 0.05 * ramp(t, 3.0, 17.0))
    dive = ease_in(clamp((t - 17.5) / 1.4))
    if dive > 0:
        cx = lerp(cx, PG.SUN[0], ease(clamp((t - 17.4) / 1.0)))
        cy = lerp(cy, PG.SUN[1] + 40, ease(clamp((t - 17.4) / 1.0)))
        z *= 1 + 3.2 * dive
    with saved(c):
        camera(c, cx, cy, z)
        book_frame(c, t, phi_c, right, left, flap=flip, overlay=overlay, cover_kw={'emboss': 0.0},
                   flips=[(T_COVER1[0], T_COVER1[1], CW, 'r'), (T_FLIP1[0], T_FLIP1[1], PW, 'r')])
    # light from the burst
    fl = 1 - clamp((t - PG.T_BURST) / 1.0)
    if PG.T_BURST <= t:
        radial_wash(c, W / 2, H / 2, 1200, (255, 200, 140), 40 * fl)


# ---- part 2: the Dothraki Sea (18.4 .. 36.4)
SEA_DRAGONS = [dict(t0=18.3 + k * 0.05, y=180 + (k * 53) % 300, s=0.55 + (k * 37 % 40) / 100, ph=k * 1.7, sp=420 + (k * 29) % 220)
               for k in range(46)]
EMB_SEA = Embers(120, 4, -100, W + 100, 700, rise=(-30, 40), life=(3, 6), r=(1.2, 3.0))
QARTH_T = (27.3, 33.3)


def sea_dragons(c, t):
    for d in SEA_DRAGONS:
        age = t - d['t0']
        if age < 0:
            continue
        x = W + 160 - d['sp'] * age - 60 * math.sin(d['ph'])
        y = d['y'] + 40 * math.sin(age * 1.3 + d['ph']) + 22 * age
        dis = clamp((age - 1.8 - (d['ph'] % 1.5)) / 1.4)
        if dis >= 1 or x < -200:
            continue
        a = int(255 * (1 - dis))
        PG.paper_dragon(c, x, y, d['s'] * (1 - 0.3 * dis), t, ph=d['ph'], heading=190, col=(120, 36, 30), a=a)
        if dis > 0:
            for k in range(5):
                c.drawCircle(x + 30 * math.sin(k * 2.1 + age), y + 20 * k * dis, 2.4, paint(rgb(255, 170, 70, int(200 * dis * (1 - dis) * 2))))


def part2(c, t):
    cam = 260 * (t - 18.4) / 18.0
    z = 1.12 - 0.12 * ease_out(clamp((t - 18.4) / 2.0))
    with saved(c):
        camera(c, W / 2, H / 2, z)
        WD.dothraki(c, t, cam)
        sea_dragons(c, t)
        pop = popv(t, QARTH_T[0], 0.55, QARTH_T[1], 0.4)
        WD.plate_card(c, WD.QARTH, 520 - cam * 0.5, 1004, 300, 375, 'QARTH', pop, t)
        EMB_SEA.draw(c, t, strength=0.5 * ramp(t, 19.5, 21.5) + 0.8 * ramp(t, 34.6, 35.6), wind=30)


# ---- part 3: dawn at the pyre (35.6 .. 65)
SMOKE = WD.Smoke(40, 3, WD.PYRE[0], WD.PYRE[1] - 20, spread=150, rise=46, life=8.0, size=(14, 40), drift=22)
SMOKE_FG = WD.Smoke(26, 8, 300, 1060, spread=320, rise=40, life=6.0, size=(60, 140), drift=30)
PLATE_R = (1250 - 180, 190, 1250 + 180, 190 + 528)
DISS = WD.Dissolve(int(PLATE_R[2] - PLATE_R[0] + 40), int(PLATE_R[3] - PLATE_R[1] + 40))
T_PLATE = (49.3, 50.9)
T_BURN = 53.4
MIRRI_KEYS = [(36.9, -260, 800, 1.0), (40.4, 520, 800, 1.0), (61.5, 520, 800, 1.0)]


def plate_layer(t):
    """the framed plate II rendered to an RGBA array, dissolving in from smoke"""
    w, h = DISS.w, DISS.h
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(rgb(0, 0, 0, 0))
    x0, y0 = 20, 20
    pw, ph = PLATE_R[2] - PLATE_R[0], PLATE_R[3] - PLATE_R[1]
    c.drawRect(R(x0 - 12, y0 - 12, x0 + pw + 12, y0 + ph + 12), paint(rgb(206, 186, 146)))
    draw_img(c, WD.PLATE2, R(x0, y0, x0 + pw, y0 + ph))
    c.drawRect(R(x0, y0, x0 + pw, y0 + ph), paint(rgb(150, 110, 60), stroke=5))
    f = skia.Font(TF_FELL_SC, 22)
    lab = 'PLATE II  ·  THE PYRE'
    lw = f.measureText(lab)
    cx = x0 + pw / 2
    c.drawRect(R(cx - lw / 2 - 16, y0 + 14, cx + lw / 2 + 16, y0 + 50), paint(rgb(222, 204, 164)))
    text(c, lab, cx, y0 + 42, TF_FELL_SC, 22, INK, align='center')
    arr = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)
    u = clamp((t - T_PLATE[0]) / (T_PLATE[1] - T_PLATE[0]))
    return to_image(DISS.apply(arr, u))


def burn_hole(t):
    r = 0.0
    if t >= T_BURN:
        r = 420 * ease_in(clamp((t - T_BURN) / 1.5)) + 60 * ease_out(clamp((t - T_BURN) / 0.6))
    return r


def hole_path(cx, cy, r, t):
    n = 48
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + 0.14 * math.sin(3 * a + 0.7 + 0.3 * t) + 0.08 * math.sin(5 * a + 2.1) + 0.05 * math.sin(9 * a + 1.3 + t))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * 1.15))
    return smooth_path(pts)


HATCH = [dict(x=1120, y=560, dx=-160, flip=True, acc=GLUT, tt=55.3), dict(x=1250, y=520, dx=10, flip=False, acc=(120, 150, 70), tt=55.8),
         dict(x=1380, y=560, dx=170, flip=False, acc=(70, 110, 150), tt=56.3)]


def plate_fire(c, t):
    """behind the burnt plate: a column of fire with three small dragons rising from it"""
    cx, cy = (PLATE_R[0] + PLATE_R[2]) / 2, (PLATE_R[1] + PLATE_R[3]) / 2
    k = clamp((t - T_BURN) / 0.8) * (1 - clamp((t - 58.6) / 1.2))
    if k <= 0:
        return
    additive_glow(c, cx, cy + 80, 420, (255, 130, 50), 120 * k)
    by = WD.PYRE[1] - 6
    flames(c, cx, by, 340 * k, 620 * k, t, seed=3, a=int(235 * k))
    flames(c, cx - 130, by + 6, 180 * k, 360 * k, t, seed=5, a=int(220 * k))
    flames(c, cx + 140, by + 6, 190 * k, 380 * k, t, seed=7, a=int(220 * k))
    for h in HATCH:
        a = clamp((t - h['tt']) / 0.5)
        if a <= 0:
            continue
        u = ease_out(clamp((t - h['tt']) / 2.6))
        fade = 1 - clamp((t - 58.6) / 0.9)
        x, y = h['x'] + h['dx'] * u, h['y'] - 300 * u
        WD.hatchling(c, x, y, 1.15 + 0.2 * u, flip=h['flip'], wing=0.5 + 0.5 * math.sin(t * 7 + h['x']), accent=h['acc'], a=int(255 * a * fade))


def part3(c, t):
    # gentle push toward the pyre, then toward Mirri's back as she lifts the book
    push = ease_in(clamp((t - 63.2) / 1.6))
    z = 1.0 + 0.03 * ramp(t, 36.0, 60.0) + 0.9 * push
    cx = lerp(W / 2, 560, push)
    cy = lerp(H / 2, 560, push)
    with saved(c):
        camera(c, cx, cy, z)
        WD.dawn_sky(c, t)
        WD.dawn_land(c, t)
        glow = 1.0 + 0.6 * clamp((t - T_BURN) / 0.6) * (1 - clamp((t - 58.4) / 1.2))
        WD.pyre_remains(c, t, glow)
        SMOKE.draw(c, t, a=1.0, col=(150, 146, 150))
        # plate II forms out of the smoke, then burns through
        if t >= T_PLATE[0] - 0.05 and t < 58.6:
            plate_fire(c, t)
            r = burn_hole(t)
            img = plate_layer(t)
            c.saveLayer()
            c.drawImage(img, PLATE_R[0] - 20, PLATE_R[1] - 20)
            if r > 0:
                hcx, hcy = (PLATE_R[0] + PLATE_R[2]) / 2, (PLATE_R[1] + PLATE_R[3]) / 2 + 40
                hp = hole_path(hcx, hcy, r, t)
                ring = paint(rgb(54, 28, 16, 235), stroke=40)
                ring.setBlendMode(skia.BlendMode.kSrcATop)
                c.drawPath(hp, ring)
                c.drawPath(hp, skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kClear))
            c.restore()
            if r > 0:
                with saved(c):
                    c.clipRect(R(PLATE_R[0] - 14, PLATE_R[1] - 14, PLATE_R[2] + 14, PLATE_R[3] + 14))
                    c.drawPath(hp, paint(rgb(255, 150, 60), stroke=5))
                    c.drawPath(hp, blur_paint(rgb(255, 190, 90), 8, stroke=14))
                    m = skia.PathMeasure(hp, True)
                    L = m.getLength()
                    for k in range(10):
                        pos, tan = m.getPosTan(L * (k + 0.5) / 10)
                        if pos is not None:
                            flames(c, pos.x(), pos.y() + 10, 54, 60, t, seed=60 + k, a=210)
        elif 58.6 <= t < 60.0:
            plate_fire(c, t)
        # Mirri walks out of the smoke
        x, y, s, speed = WD.mirri_pose(t, MIRRI_KEYS)
        walk = clamp(speed / 120)
        lift = eramp(t, 61.8, 63.4)
        head = ramp(t, 59.2, 60.4) * (1 - ramp(t, 61.0, 61.8)) + 0.6 * lift
        if t > 36.6:
            WD.mirri_back(c, t, x, y, s, walk=walk, lift=lift, head_down=head, rim_from=(1250, 640 if T_BURN < t < 58.5 else 860),
                          rim=0.8 + 0.6 * clamp((t - T_BURN) / 0.6) * (1 - clamp((t - 58.4) / 1.0)), light=(255, 176, 120))
        SMOKE_FG.draw(c, t, a=1 - ramp(t, 38.0, 41.0), col=(170, 164, 166))


# ---- part 4: the stargazer's book (64.2 .. 91)
T_COVER2 = (65.25, 66.3)
T_SIG = (67.0, 68.8)
T_Q = (V['01-6'][0] + 6.08, V['01-6'][0] + 7.75)
T_ICE = (V['01-6'][0] + 10.6, V['01-6'][0] + 12.6)
T_FIRE = (V['01-6'][0] + 12.2, V['01-6'][0] + 13.5)
T_FLIP2 = (79.65, 80.4)
T_TIDE_POP = (80.3, 81.0)
T_DOT = (81.5, V['01-7'][0] + 4.55)
T_JUMP = (84.75, 85.0)
T_CLOSE = (85.0, 85.5)


def part4(c, t):
    q_u = clamp((t - T_Q[0]) / (T_Q[1] - T_Q[0]))
    sig_u = clamp((t - T_SIG[0]) / (T_SIG[1] - T_SIG[0]))
    ice = clamp((t - T_ICE[0]) / (T_ICE[1] - T_ICE[0]))
    fire = clamp((t - T_FIRE[0]) / (T_FIRE[1] - T_FIRE[0]))
    comet_glow = ramp(t, 66.5, 67.5)

    def left_ex(c):
        left_endpaper(c, t, sig_u, comet_glow)
        PG.frost(c, t, ice)

    def right_title(c):
        title_right(c, t, q_u)
        PG.fire_page(c, t, fire)

    def tide_l(c):
        left_page_base(c)
        PG.tide_chart(c, t, pop=popv(t, T_TIDE_POP[0], 0.7), side='l')
        B.running_head(c, alpha=200)

    def tide_r(c):
        right_page_base(c)
        PG.tide_chart(c, t, pop=popv(t, T_TIDE_POP[0], 0.7), side='r')

    phi_c = math.pi * ease((t - T_COVER2[0]) / (T_COVER2[1] - T_COVER2[0]))
    flap = None
    cover_kw = {'emboss': 0.0}
    overlay = None
    if t < T_FLIP2[0]:
        right, left = right_title, left_ex
    elif t < T_FLIP2[1]:
        right, left = tide_r, left_ex
        flap = (flip_phi(t, *T_FLIP2), right_title, tide_l)
    elif t < T_CLOSE[0]:
        right, left = tide_r, lambda c: (left_ex(c), tide_l(c))
    else:
        right = tide_r
        left = lambda c: (left_ex(c), tide_l(c))
        phi_c = math.pi * (1 - ease((t - T_CLOSE[0]) / (T_CLOSE[1] - T_CLOSE[0])))
        emb = ease(clamp((t - T_HIT) / 1.6))
        glint = clamp((t - 86.9) / 1.4) if t > 86.9 else -1
        cover_kw = {'emboss': emb, 'glint': glint}
        if phi_c <= 0.02:
            right = lambda c: None

    if T_FLIP2[1] - 0.1 <= t < T_CLOSE[1]:
        def overlay(c):
            if t < T_CLOSE[0]:
                dot = clamp((t - T_DOT[0]) / (T_DOT[1] - T_DOT[0]))
                jump = clamp((t - T_JUMP[0]) / (T_JUMP[1] - T_JUMP[0]))
                if t >= T_TIDE_POP[0] + 0.7:
                    PG.tide_dot(c, t, dot, jump)
    # camera
    closed_mix = 1 - eramp(t, 65.2, 66.6)
    if t >= T_CLOSE[0]:
        closed_mix = eramp(t, T_CLOSE[0], T_HIT + 0.6)
    cx = lerp(SP, SP + CW / 2, closed_mix)
    z = lerp(1.0, 1.08, closed_mix) * (1 + 0.035 * ramp(t, 66.0, 79.0)) * (1 + 0.06 * ramp(t, T_HIT, T_END))
    shake = 0.0
    if t >= T_HIT:
        shake = 6 * math.exp(-(t - T_HIT) / 0.12) * math.sin((t - T_HIT) * 70)
    with saved(c):
        camera(c, cx, 540 + shake, z)
        book_frame(c, t, phi_c, right, left, flap=flap, overlay=overlay, cover_kw=cover_kw,
                   flips=[(T_COVER2[0], T_COVER2[1], CW, 'r'), (T_FLIP2[0], T_FLIP2[1], PW, 'r'), (T_CLOSE[0], T_CLOSE[1], CW, 'l')])
        if t >= T_HIT:
            emb = Embers(60, 31, SP + 40, SP + CW - 40, CB - 40, rise=(80, 200), life=(1.5, 3.5))
            emb.draw(c, t - T_HIT, strength=1 - 0.6 * ramp(t, 87, 91))
    if t >= T_HIT:
        fl = math.exp(-(t - T_HIT) / 0.25)
        radial_wash(c, W / 2, H / 2, 1300, (255, 220, 160), 120 * fl)


# ------------------------------------------------------------------ compositor
def render_part(fn, t):
    s = skia.Surface(W, H)
    fn(s.getCanvas(), t)
    return s.makeImageSnapshot()


def xfade(c, t, fa, fb, u):
    if u <= 0:
        fa(c, t)
        return
    if u >= 1:
        fb(c, t)
        return
    fa(c, t)
    img = render_part(fb, t)
    pp = skia.Paint()
    pp.setAlphaf(u)
    c.drawImage(img, 0, 0, SAMP, pp)


def scene(c, t):
    if t < 18.2:
        part1(c, t)
    elif t < 18.8:
        xfade(c, t, part1, part2, smooth((t - 18.2) / 0.6))
    elif t < 35.4:
        part2(c, t)
    elif t < 36.4:
        # fade through dusk-dark into dawn
        u = (t - 35.4) / 1.0
        if u < 0.5:
            part2(c, t)
            c.drawRect(R(0, 0, W, H), paint(rgb(8, 8, 12, int(255 * smooth(u / 0.5)))))
        else:
            part3(c, t)
            c.drawRect(R(0, 0, W, H), paint(rgb(8, 8, 12, int(255 * (1 - smooth((u - 0.5) / 0.5))))))
    elif t < 64.3:
        part3(c, t)
    elif t < 64.9:
        xfade(c, t, part3, part4, smooth((t - 64.3) / 0.6))
    else:
        part4(c, t)
    # fade in / out
    if t < 0.35:
        c.drawRect(R(0, 0, W, H), paint(rgb(0, 0, 0, int(255 * (1 - t / 0.35)))))
    if t > T_END - 0.8:
        c.drawRect(R(0, 0, W, H), paint(rgb(0, 0, 0, int(255 * smooth((t - (T_END - 0.8)) / 0.8)))))


# ------------------------------------------------------------------ preview captions (temporary)
CAPS = [(V['01-2'][0], V['01-2'][1], 'A slave girl told that story to Daenerys Targaryen ... No one believed it.'),
        (V['01-3'][0], V['01-3'][1], 'Neither did I. I was a godswife in Lhazar ... And how little of it was left.'),
        (V['01-4'][0], V['01-4'][1], 'Then they tied me to a pyre ... and walked out with three dragons.'),
        (V['01-5'][0], V['01-5'][1], 'I burned that night. She did not. I have had a long time to wonder why.')]
SHOW_CAPS = os.environ.get('CAPS', '1') == '1'


def captions(c, t):
    if not SHOW_CAPS:
        return
    for (t0, t1, s) in CAPS:
        a = win(t, t0, t1, 0.25, 0.25)
        if a > 0:
            f = skia.Font(TF_CORM_I, 34)
            wd = f.measureText(s)
            c.drawRoundRect(R(W / 2 - wd / 2 - 24, H - 92, W / 2 + wd / 2 + 24, H - 42), 8, 8, paint(rgb(0, 0, 0, int(120 * a))))
            text(c, s, W / 2, H - 56, TF_CORM_I, 34, BONE, align='center', alpha=int(235 * a))


# ------------------------------------------------------------------ finish
_r = np.random.default_rng(3)
GRAIN = [_r.normal(0, 3.6, (OH, OW, 1)).astype(np.float32) for _ in range(6)]
YY, XX = np.mgrid[0:OH, 0:OW]
VIGN = (1 - 0.26 * np.clip(np.sqrt(((XX - OW / 2) / (OW * 0.7)) ** 2 + ((YY - OH / 2) / (OH * 0.72)) ** 2) - 0.35, 0, 1) ** 1.4)[..., None].astype(np.float32)


def frame(t, idx=0):
    s = skia.Surface(OW, OH)
    c = s.getCanvas()
    c.scale(SCALE, SCALE)
    scene(c, t)
    captions(c, t)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    a = a * VIGN + GRAIN[idx % 6]
    return np.clip(a, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    import subprocess
    if sys.argv[1] == 'still':
        os.makedirs(D + 'stills', exist_ok=True)
        for ts in sys.argv[2].split(','):
            t = float(ts)
            Image.fromarray(frame(t, int(t * FPS))).save(D + f'stills/c1_{t:05.2f}.png')
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
