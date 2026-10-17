#!/usr/bin/env python3
"""Will AI Buy Our Cars? - Konzept 4 (ohne religioese Bildsprache): Standbilder der neuen Schluesselbilder.

Kristallkugel = die Prophezeiung, Kreislauf (Schlange beisst sich in den Schwanz) = die Wirtschaft,
abgestreifte Haeute = die Geschichte. Baut auf prophecy.py auf.
"""
import importlib.util, math, os, random, sys
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('pr', os.path.join(HERE, 'prophecy.py'))
pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr)
from types import SimpleNamespace
P = pr  # Kurzname

W, H = P.W, P.H
col, mix, clamp, prog, eout, eio, lerp = P.col, P.mix, P.clamp, P.prog, P.eout, P.eio, P.lerp
P_fill, P_ink, P_glow, shape, circle, poly = P.P_fill, P.P_ink, P.P_glow, P.shape, P.circle, P.poly
INK, BONE, BONE_HI, BONE_SH, GOLD, GOLD_HI, GOLD_DK = P.INK, P.BONE, P.BONE_HI, P.BONE_SH, P.GOLD, P.GOLD_HI, P.GOLD_DK
SNAKE, SNAKE_DK = P.SNAKE, P.SNAKE_DK


def bez_pts(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        u = i / (n - 1)
        x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u * u * p2[0] + u ** 3 * p3[0]
        y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u * u * p2[1] + u ** 3 * p3[1]
        out.append((x, y))
    return out


# ---------------------------------------------------------------- Kristallkugel
def ball_city(cv, cx, cy, R, t):
    back, front = P.CITY
    cv.save()
    sc = 2 * R / W * 1.05
    cv.translate(cx - R * 1.05, cy + R * .62)
    cv.scale(sc, sc)
    cv.translate(0, -1100)
    for (x, w_, h_, k) in back:
        cv.drawRect(skia.Rect.MakeLTRB(x, 1100 - h_ * .95, x + w_, 1400), P_fill('#3a3122', 1, False))
        cv.drawRect(skia.Rect.MakeLTRB(x, 1100 - h_ * .95, x + w_, 1400), P_ink(5, INK, .8, False))
    P.draw_eden_bot(cv, 1000, 1060, 900, 175, t, face=1.0, glow=1.0)
    for (x, w_, h_, k) in front:
        cv.drawRect(skia.Rect.MakeLTRB(x, 1110 - h_ * .7, x + w_, 1400), P_fill('#4a3d26', 1, False))
        cv.drawRect(skia.Rect.MakeLTRB(x, 1110 - h_ * .7, x + w_, 1400), P_ink(5, INK, .8, False))
        rnd = random.Random(int(x))
        for cx_ in range(int((w_ - 16) // 24)):
            for cy_ in range(int((h_ * .7 - 20) // 32)):
                if rnd.random() < .5:
                    cv.drawRect(skia.Rect.MakeXYWH(x + 11 + cx_ * 24, 1110 - h_ * .7 + 16 + cy_ * 32, 10, 15),
                                P_fill(GOLD, .9, False))
    cv.restore()


def draw_ball(cv, cx, cy, R, t, crack=0.0, crack_glow=0.0):
    cv.drawCircle(cx, cy, R * 1.25, P_glow(GOLD_HI, R * .45, .28))
    ball = circle(cx, cy, R)
    cv.save()
    cv.clipPath(ball, doAntiAlias=True)
    bg = skia.Paint(AntiAlias=True)
    bg.setShader(skia.GradientShader.MakeRadial(skia.Point(cx - R * .2, cy - R * .3), R * 1.3,
                                                [col('#3b3524'), col('#18150f')]))
    cv.drawCircle(cx, cy, R, bg)
    rnd = random.Random(4)
    for _ in range(14):
        cv.drawPath(P.star5(cx + rnd.uniform(-.8, .8) * R, cy + rnd.uniform(-.85, -.1) * R, rnd.uniform(4, 8)),
                    P_fill(BONE_SH, .6, False))
    ball_city(cv, cx, cy, R, t)
    # Glas: Rand dunkler, Spiegelung
    vg = skia.Paint(AntiAlias=True)
    vg.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), R, [col('#000000', 0), col('#000000', 0),
                                                                        col('#0b0a07', .55)], [0, .72, 1]))
    cv.drawCircle(cx, cy, R, vg)
    hl = skia.Path()
    hl.addArc(skia.Rect.MakeXYWH(cx - R * .78, cy - R * .78, R * 1.56, R * 1.56), 200, 55)
    cv.drawPath(hl, P_ink(R * .07, '#fff6dc', .5))
    cv.drawCircle(cx - R * .38, cy - R * .62, R * .05, P_fill('#fff6dc', .7, False))
    hl2 = skia.Path()
    hl2.addArc(skia.Rect.MakeXYWH(cx - R * .9, cy - R * .9, R * 1.8, R * 1.8), 20, 40)
    cv.drawPath(hl2, P_ink(R * .025, '#fff6dc', .35))
    if crack > 0:
        rr = R
        main = [(cx + x * 1.0, cy + y * 1.0) for (x, y) in P.crack_points(rr)]
        branches = [[(cx + x, cy + y) for (x, y) in b] for b in P.crack_branches(rr, P.crack_points(rr))]
        mp = P.trim(poly(main, close=False), crack)
        lg = P_ink(8 + 16 * crack_glow, GOLD_HI, .5 + .4 * crack_glow, wobble=False)
        lg.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10 + 10 * crack_glow))
        cv.drawPath(mp, lg)
        cv.drawPath(mp, P_ink(6, INK, 1, wobble=False))
        cv.drawPath(mp, P_ink(2.5 + 3 * crack_glow, '#fff3d0', .9, wobble=False))
        for b in branches:
            bp = P.trim(poly(b, close=False), crack_glow)
            cv.drawPath(bp, lg)
            cv.drawPath(bp, P_ink(5, INK, 1, wobble=False))
            cv.drawPath(bp, P_ink(2.5, '#fff3d0', .9, wobble=False))
    cv.restore()
    cv.drawPath(ball, P_ink(6, INK))
    inner = skia.Path()
    inner.addArc(skia.Rect.MakeXYWH(cx - R + 9, cy - R + 9, 2 * R - 18, 2 * R - 18), 120, 120)
    cv.drawPath(inner, P_ink(4, GOLD_HI, .35))


def coil_and_neck(cx, ey, rx, ry, head, t):
    """Koerper: Ring um den Kugelfuss (hinten/vorne getrennt), dann Hals nach links oben zum Kopf."""
    back, front = [], []
    a0, a1 = -100, 152
    n = 70
    for i in range(n):
        a = math.radians(lerp(a0, a1, i / (n - 1)))
        x, y = cx + rx * math.cos(a), ey + ry * math.sin(a)
        (front if math.sin(a) >= -0.02 else back).append((x, y, 1.0 if math.sin(a) >= 0 else -1.0))
    sx, sy = front[-1][0], front[-1][1]
    hx, hy = head
    neck = bez_pts((sx, sy), (sx - 210, sy - 80), (hx - 120, hy + 250), (hx, hy), 50)
    neck = [(x, y + 6 * math.sin(t * 1.3 + i * .15), 1.0) for i, (x, y) in enumerate(neck)]
    return back, front, neck[1:]


def widths_for(n_total, i0, n, w_tail, w_body, w_neck):
    out = []
    for i in range(n):
        u = (i0 + i) / (n_total - 1)
        if u < .25:
            w = lerp(w_tail, w_body, u / .25)
        elif u < .7:
            w = w_body
        else:
            w = lerp(w_body, w_neck, (u - .7) / .3)
        out.append(w)
    return out


def scene_seer(cv, t, crack=0.0, crack_glow=0.0, slip=0.0):
    """Die Schlange haelt die Kristallkugel mit der EDEN-Stadt."""
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    P.G.zoom = 1.0
    cx, cy, R = 1220, 450, 300
    ey, rx, ry = cy + R * .86, R * 1.08, R * .26
    head = (520, 440)
    back, front, neck = coil_and_neck(cx, ey, rx, ry, head, t)
    nt = len(back) + len(front) + len(neck)
    wb = widths_for(nt, 0, len(back), 14, 82, 64)
    wf = widths_for(nt, len(back), len(front), 14, 82, 64)
    wn = widths_for(nt, len(back) + len(front), len(neck), 14, 82, 64)
    P.draw_snake_run(cv, back, wb, 5, front=False)
    draw_ball(cv, cx, cy, R, t, crack, crack_glow)
    P.draw_snake_run(cv, front + neck, wf + wn, 5, front=True)
    P.draw_head(cv, head[0], head[1], -6, 64 * 1.05, lid=.3, tongue=.5 if crack == 0 else 0,
                gold_rim=.5)
    if slip > 0:
        P.draw_slip(cv, lerp(cx, 1000, slip), lerp(cy, 820, slip), lerp(.2, .9, slip), lerp(15, -4, slip),
                    t, 1, 1, 1)
    P.fiction_label(cv, 1.0) if crack == 0 else None


# ---------------------------------------------------------------- Kreislauf (Ouroboros)
def ring_pts(cx, cy, R, a_start, a_end, n, ry=None):
    ry = ry or R
    pts = []
    for i in range(n):
        a = math.radians(lerp(a_start, a_end, i / (n - 1)))
        pts.append((cx + R * math.cos(a), cy + ry * math.sin(a), 1.0))
    return pts


def draw_ouroboros(cv, cx, cy, R, w, ow=5, head_scale=1.0, tongue=0.0):
    """Ring im Uhrzeigersinn; Kopf oben links beisst in die Schwanzspitze."""
    a_tail, a_head = -100, 243
    n = 140
    pts = ring_pts(cx, cy, R, a_tail, a_head, n)
    widths = []
    for i in range(n):
        u = i / (n - 1)
        widths.append(w * (.22 + .78 * min(1, u / .18)) * (1 - .12 * max(0, (u - .85) / .15)))
    P.draw_snake_run(cv, pts, widths, ow, front=True)
    hx, hy = pts[-1][:2]
    ang = P.head_angle(pts)
    P.draw_head(cv, hx, hy, ang, w * .95 * head_scale, lid=.25, tongue=tongue)


def icon_factory(cv, x, y, s, a=1.0):
    p = skia.Path()
    p.moveTo(x - 70 * s, y + 40 * s)
    p.lineTo(x - 70 * s, y - 10 * s)
    for k in range(3):
        xa = x - 70 * s + k * 40 * s
        p.lineTo(xa + 28 * s, y - 34 * s)
        p.lineTo(xa + 40 * s, y - 10 * s)
    p.lineTo(x + 50 * s, y - 10 * s)
    p.lineTo(x + 50 * s, y - 70 * s)
    p.lineTo(x + 70 * s, y - 70 * s)
    p.lineTo(x + 70 * s, y + 40 * s)
    p.close()
    shape(cv, p, '#3a3836', 4, a)
    for k in range(4):
        cv.drawRect(skia.Rect.MakeXYWH(x - 56 * s + k * 30 * s, y + 4 * s, 16 * s, 20 * s), P_fill(GOLD, a, False))


def scene_loop(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    P.G.zoom = 1.0
    cx, cy, R = 960, 520, 330
    # Pfeile/Fluss
    draw_ouroboros(cv, cx, cy, R, 92, tongue=0)
    icon_factory(cv, cx, cy - 150, 1.0)
    for k, dx in enumerate((-60, 0, 60)):
        P.draw_person(cv, cx + dx, cy + 210, .75, 0.0, 0)
    f = skia.Font(P.TF_HEAD, 40)

    def label(txt, x, y, c=BONE_HI):
        tw = f.measureText(txt)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(txt, f), x - tw / 2, y, P_fill(c, 1, False))
    label('COMPANIES', cx, cy - 40)
    label('WORKERS', cx, cy + 270)
    label('WAGES', cx + R + 150, cy + 14, GOLD)
    label('PURCHASES', cx - R - 170, cy + 14, GOLD)
    # Muenzen und Einkaufstueten auf dem Ring (im Uhrzeigersinn)
    for k in range(10):
        ad = (-60 + k * 36 + t * 40) % 360
        if 200 < ad < 290:
            continue
        a = math.radians(ad)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        if math.cos(a) > 0:
            cv.drawCircle(x, y, 20, P_fill(GOLD, 1, False))
            cv.drawCircle(x, y, 20, P_ink(3, INK, 1, False))
            cv.drawCircle(x, y, 11, P_ink(2.5, GOLD_DK, 1, False))
        else:
            cv.save()
            cv.translate(x, y + 14)
            cv.scale(.22, .22)
            P.draw_car(cv, -150, 0, 300, BONE)
            cv.restore()
    for (a0, side) in ((20, 1), (200, -1)):
        arc = skia.Path()
        arc.addArc(skia.Rect.MakeXYWH(cx - R - 120, cy - R - 120, 2 * R + 240, 2 * R + 240), a0, 60)
        cv.drawPath(arc, P_ink(4, BONE_SH, .8, False))
        a = math.radians(a0 + 60)
        tx, ty = cx + (R + 120) * math.cos(a), cy + (R + 120) * math.sin(a)
        dx, dy = -math.sin(a), math.cos(a)
        cv.drawPath(poly([(tx + dx * 18, ty + dy * 18), (tx - dy * 10 - dx * 4, ty + dx * 10 - dy * 4),
                          (tx + dy * 10 - dx * 4, ty - dx * 10 - dy * 4)]), P_fill(BONE_SH, .8, False))


# ---------------------------------------------------------------- Haeute (Geschichte)
SKINS = [('1760s', 'STEAM', 'soot'), ('1913', 'ASSEMBLY LINE', 'chrome'), ('1915', 'TRACTOR', 'earth'),
         ('1950s', 'AUTOMATION', 'tube'), ('1980s', 'COMPUTERS', 'pixel')]


def skin_pattern(cv, kind, bounds):
    l, tp, r, b = bounds
    rnd = random.Random(hash(kind) % 997)
    if kind == 'soot':
        for _ in range(60):
            cv.drawCircle(rnd.uniform(l, r), rnd.uniform(tp, b), rnd.uniform(2, 5), P_fill('#4a4a47', .7, False))
    elif kind == 'chrome':
        for x in range(int(l), int(r), 26):
            cv.drawRect(skia.Rect.MakeLTRB(x, tp, x + 8, b), P_fill('#eef0ea', .5, False))
    elif kind == 'earth':
        for _ in range(16):
            x, y = rnd.uniform(l, r), rnd.uniform(tp, b)
            cv.drawOval(skia.Rect.MakeXYWH(x, y, 26, 12), P_fill('#6a4a35', .6, False))
    elif kind == 'tube':
        for x in range(int(l), int(r), 34):
            cv.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, (tp + b) / 2 - 12, 18, 24), 9, 9),
                         P_fill('#86a47f', .6, False))
    elif kind == 'pixel':
        for _ in range(40):
            cv.drawRect(skia.Rect.MakeXYWH(rnd.uniform(l, r), rnd.uniform(tp, b), 10, 10), P_fill('#7290ab', .6, False))


def draw_skin(cv, x0, x1, y, kind, seed):
    rnd = random.Random(seed)
    n = 40
    pts = []
    for i in range(n):
        u = i / (n - 1)
        pts.append((lerp(x0, x1, u), y + 22 * math.sin(u * math.pi * 2 + seed) + rnd.uniform(-2, 2), 1.0))
    widths = [lerp(16, 58, min(1, u * 4)) * (1 - .25 * u) for u in [i / (n - 1) for i in range(n)]]
    left, right = P.snake_outline(pts, widths)
    body = poly(left + right[::-1])
    cv.drawPath(body, P_fill('#b7b29f', .55))
    cv.save()
    cv.clipPath(body, doAntiAlias=True)
    b = body.computeTightBounds()
    skin_pattern(cv, kind, (b.left(), b.top(), b.right(), b.bottom()))
    for i in range(2, n - 2, 3):
        x, yy = pts[i][:2]
        cv.drawLine(x - 8, yy - widths[i] * .4, x + 4, yy, P_ink(2, '#8c887a', .7, False))
        cv.drawLine(x + 4, yy, x - 8, yy + widths[i] * .4, P_ink(2, '#8c887a', .7, False))
    cv.restore()
    cv.drawPath(poly(left, close=False), P_ink(3, INK, .8))
    cv.drawPath(poly(right, close=False), P_ink(3, INK, .8))
    mx = (x0 + x1) / 2
    cv.drawOval(skia.Rect.MakeXYWH(x1 - 22, pts[-1][1] - 30, 44, 60), P_ink(3, INK, .7))


def scene_skins(cv, t):
    cv.drawImage(P.BG_NIGHT, 0, 0)
    P.G.zoom = 1.0
    cv.drawRect(skia.Rect.MakeLTRB(-10, 760, W + 10, H + 10), P_fill('#1b1c1b', 1, False))
    cv.drawLine(-10, 760, W + 10, 760, P_ink(4, INK, 1, False))
    f = skia.Font(P.TF_HEAD, 34)
    f2 = skia.Font(P.TF_CAPS, 26)
    for i, (yr, name, kind) in enumerate(SKINS):
        x0 = 80 + i * 300
        draw_skin(cv, x0, x0 + 250, 690, kind, i + 1)
        tw = f.measureText(name)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(name, f), x0 + 125 - tw / 2, 830, P_fill(BONE_HI, 1, False))
        yw = f2.measureText(yr)
        cv.drawTextBlob(skia.TextBlob.MakeFromString(yr, f2), x0 + 125 - yw / 2, 870, P_fill(GOLD, 1, False))
    # die lebende Schlange rechts: unter der Haut schimmert Gold
    coil = []
    for i in range(40):
        a = math.radians(lerp(-160, 200, i / 39))
        coil.append((1700 + 120 * math.cos(a), 720 + 32 * math.sin(a), 1.0 if math.sin(a) >= 0 else -1.0))
    neck = bez_pts(coil[-1][:2], (1560, 700), (1700, 470), (1600, 430), 30)
    pts = coil + [(x, y, 1.0) for (x, y) in neck[1:]]
    widths = [lerp(20, 76, min(1, i / 12)) for i in range(len(pts))]
    back = [(p_, w_) for p_, w_ in zip(pts, widths) if p_[2] < 0]
    if back:
        P.draw_snake_run(cv, [b[0] for b in back], [b[1] for b in back], 5, front=False)
    frontpts = [p_ for p_ in pts if p_[2] >= 0]
    frontw = [w_ for p_, w_ in zip(pts, widths) if p_[2] >= 0]
    cv.drawCircle(1680, 620, 190, P_glow(GOLD_HI, 70, .25))
    P.draw_snake_run(cv, frontpts, frontw, 5, front=True)
    cpts = [p_[:2] for p_ in frontpts]
    gl = P_ink(16, GOLD_HI, .7, wobble=False)
    gl.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8))
    seam = poly([(x, y - 6) for (x, y) in cpts[len(cpts) // 3:]], close=False)
    cv.drawPath(seam, gl)
    cv.drawPath(seam, P_ink(7, GOLD, 1, wobble=False))
    P.draw_head(cv, pts[-1][0], pts[-1][1], P.head_angle(pts), 76, lid=.3, flip=True)
    tw = f.measureText('AI')
    cv.drawTextBlob(skia.TextBlob.MakeFromString('AI', f), 1700 - tw / 2, 830, P_fill(GOLD, 1, False))
    yw = f2.measureText('NOW')
    cv.drawTextBlob(skia.TextBlob.MakeFromString('NOW', f2), 1700 - yw / 2, 870, P_fill(GOLD, 1, False))


# ---------------------------------------------------------------- Titel mit Ouroboros-O
def scene_title4(cv, t):
    cv.drawImage(P.BG_NIGHT2, 0, 0)
    P.G.zoom = 1.0
    size = 170
    f = skia.Font(P.TF_TITLE, size)
    lines = [['WILL ', 'AI', ' BUY'], ['O', 'UR CARS?']]
    for li, parts in enumerate(lines):
        full = ''.join(parts)
        x = (W - f.measureText(full)) / 2
        y = 470 + li * 210
        for part in parts:
            pw = f.measureText(part)
            if li == 1 and part == 'O':
                cx, cy, R = x + pw / 2, y - size * .36, size * .34
                draw_ouroboros(cv, cx, cy, R, 30, ow=3.5)
            else:
                blob = skia.TextBlob.MakeFromString(part, f)
                cv.drawTextBlob(blob, x + 5, y + 6, P_fill('#000000', .6, False))
                if part == 'AI':
                    g = P_fill(GOLD_HI, .55, False)
                    g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 20))
                    cv.drawTextBlob(blob, x, y, g)
                    cv.drawTextBlob(blob, x, y, P_fill(GOLD, 1, False))
                else:
                    cv.drawTextBlob(blob, x, y, P_fill(BONE_HI, 1, False))
            x += pw


def main():
    P.init_assets()
    post = P.Post()
    surf = skia.Surface(W, H)
    out = sys.argv[1]
    frames = [('seer', lambda cv: scene_seer(cv, 1.0)),
              ('crack', lambda cv: scene_seer(cv, 2.0, crack=1.0, crack_glow=1.0, slip=1.0)),
              ('title', lambda cv: scene_title4(cv, 0)),
              ('loop', lambda cv: scene_loop(cv, 0)),
              ('skins', lambda cv: scene_skins(cv, 0))]
    from PIL import Image
    for name, fn in frames:
        cv = surf.getCanvas()
        cv.clear(col(P.BG))
        P.G.frame = 0
        cv.save()
        fn(cv)
        cv.restore()
        arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        Image.fromarray(post.apply(arr, 0)).save(os.path.join(out, name + '.png'))
        print('saved', name)


if __name__ == '__main__':
    main()
