"""What is printed (and what pops up) on the pages of the Starseer's book in chapter 1."""
import math, sys
import numpy as np
import skia
from lib import *
from book import SP, PT, PB, PW, RP, LP, CT, CB, CW, RPATH, LPATH, saw_draw, saw_pts
from world import paper_dragon

sys.path.insert(0, '/home/claude/rig')
from starseer import Starseer, Pose

PAPER = (226, 206, 166)


# ------------------------------------------------------------------ engraving of the Starseer (bookplate)
def _engraving():
    w, h = 520, 520
    s = skia.Surface(w, h)
    c = s.getCanvas()
    c.clear(rgb(0, 0, 0, 0))
    ss = Starseer()
    pz = Pose(head=-26, look=0.9, ua=-48, fa=-40, hand=2, scroll=0.0, wind=0.3, brow_y=0.3)
    ss.draw(c, pz, 200, 400, 0.95)
    a = s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).astype(np.float32)
    lum = (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]) / 255
    t = np.clip(lum * 1.15, 0, 1) ** 0.85
    ink = np.array(INK, np.float32)
    pap = np.array(PAPER, np.float32)
    col = ink[None, None] * (1 - t[..., None]) + pap[None, None] * t[..., None]
    # engraving hatch: diagonal lines where it is dark
    yy, xx = np.mgrid[0:h, 0:w]
    hatch = ((xx + yy) % 7 < 2) & (t < 0.62)
    col[hatch] = col[hatch] * 0.55 + ink * 0.45
    out = np.concatenate([col, a[..., 3:4]], 2)
    return to_image(out)


ENGRAVING = _engraving()


def ink_stroke(c, pts, w=2.4, col=INK, a=220, u=1.0):
    """polyline drawn on progressively (u = 0..1 of its length)"""
    if u <= 0:
        return
    p = smooth_path(pts, closed=False)
    if u < 1:
        m = skia.PathMeasure(p, False)
        seg = skia.Path()
        m.getSegment(0, m.getLength() * u, seg, True)
        p = seg
    c.drawPath(p, paint(C(col, a), stroke=w))


SIGNATURE = [(0, 0), (14, -30), (22, -6), (30, -34), (40, 2), (54, -20), (70, -8), (86, -26), (100, -4), (122, -12), (150, -2), (190, -16)]


def exlibris(c, t, sig_u=1.0, glow=0.0):
    """bookplate pasted on the inside of the cover (left side when open)"""
    x0, x1 = SP - CW + 70, SP - 60
    y0, y1 = CT + 120, CB - 150
    cx = (x0 + x1) / 2
    c.drawRect(R(x0 + 6, y0 + 8, x1 + 6, y1 + 8), blur_paint(rgb(40, 24, 12, 90), 6))
    c.drawRect(R(x0, y0, x1, y1), paint(rgb(232, 216, 180)))
    c.drawRect(R(x0 + 16, y0 + 16, x1 - 16, y1 - 16), paint(C(INK, 200), stroke=2.4))
    c.drawRect(R(x0 + 24, y0 + 24, x1 - 24, y1 - 24), paint(C(INK, 120), stroke=1))
    text(c, 'EX  LIBRIS', cx, y0 + 84, TF_CINZEL_B, 30, INK, align='center', alpha=230, spacing=3)
    # scene: hill, stars, comet, then the engraved figure with his glass
    sx0, sy0, sx1, sy1 = x0 + 50, y0 + 110, x1 - 50, y1 - 170
    c.save()
    c.clipRect(R(sx0, sy0, sx1, sy1))
    rng = np.random.default_rng(2)
    for _ in range(46):
        x, y = rng.uniform(sx0, sx1), rng.uniform(sy0, sy0 + 220)
        c.drawCircle(x, y, rng.uniform(0.8, 2.0), paint(C(INK, 170)))
    # comet engraved
    hx, hy = sx1 - 110, sy0 + 70
    for k in range(9):
        c.drawLine(hx, hy, hx + 150 - k * 6, hy - 70 + k * 9, paint(C(INK, 120), stroke=1.2))
    c.drawCircle(hx, hy, 6, paint(C(INK, 230)))
    if glow > 0:
        additive_glow(c, hx, hy, 60, (255, 120, 60), int(120 * glow))
    # hill
    c.drawPath(smooth_path([(sx0 - 20, sy1 - 40), (sx0 + 120, sy1 - 110), (sx0 + 300, sy1 - 130), (sx1 + 20, sy1 - 90), (sx1 + 20, sy1 + 10), (sx0 - 20, sy1 + 10)]),
               paint(C(INK, 60)))
    for k in range(12):
        y = sy1 - 100 + k * 9
        c.drawLine(sx0, y, sx1, y + 14, paint(C(INK, 50), stroke=1))
    c.restore()
    draw_img(c, ENGRAVING, R(cx - 210, sy1 - 330, cx + 130, sy1 + 10))
    # telescope on a tripod
    tx, ty = cx + 64, sy1 - 120
    c.drawLine(tx, ty, tx - 26, sy1 - 40, paint(C(INK, 220), stroke=3))
    c.drawLine(tx, ty, tx + 26, sy1 - 40, paint(C(INK, 220), stroke=3))
    c.drawLine(tx, ty, tx + 2, sy1 - 40, paint(C(INK, 220), stroke=3))
    with saved(c):
        c.translate(tx, ty); c.rotate(-38)
        c.drawRoundRect(R(-50, -9, 90, 9), 4, 4, paint(C(INK, 230)))
        c.drawRoundRect(R(60, -12, 96, 12), 4, 4, paint(C(INK, 230)))
        for k in range(3):
            c.drawLine(-30 + k * 30, -9, -30 + k * 30, 9, paint(rgb(232, 216, 180, 200), stroke=1.4))
    # small campfire
    fx, fy = cx - 190, sy1 - 52
    c.drawPath(poly([(fx - 16, fy), (fx - 4, fy - 30), (fx + 2, fy - 12), (fx + 10, fy - 38), (fx + 18, fy)]), paint(C(INK, 210)))
    text(c, 'the stargazer, at his glass', cx, y1 - 116, TF_FELL_I, 24, INK, align='center', alpha=210)
    # signature (written on)
    with saved(c):
        c.translate(cx - 96, y1 - 52)
        ink_stroke(c, SIGNATURE, w=2.6, a=230, u=sig_u)
        if sig_u >= 1:
            c.drawLine(-6, 14, 200, 8, paint(C(INK, 160), stroke=1.6))


# ------------------------------------------------------------------ title page (first right page)
QUESTION = 'why now  -  and why everywhere at once?'


def title_page(c, t, q_u=0.0, a=230):
    cx = (RP[0] + RP[2]) / 2
    text(c, 'THE TIDES', cx, PT + 250, TF_CINZEL_B, 64, INK, align='center', alpha=a)
    text(c, 'OF MAGIC', cx, PT + 330, TF_CINZEL_B, 64, INK, align='center', alpha=a)
    c.drawLine(cx - 150, PT + 372, cx + 150, PT + 372, paint(C(INK, 150), stroke=1.6))
    c.drawCircle(cx, PT + 372, 4, paint(C(INK, 200)))
    text(c, 'Observations of a Stargazer', cx, PT + 430, TF_FELL_I, 36, INK, align='center', alpha=a)
    saw_draw(c, cx - 90, PT + 560, 180, 50, col=INK, a=200, sw=3.4, dot=1.0)
    text(c, 'N° 01', cx, PT + 640, TF_CINZEL, 26, INK, align='center', alpha=200)
    # the question, in his hand, written while Mirri asks it
    if q_u > 0:
        f = skia.Font(TF_FELL_I, 34)
        wd = f.measureText(QUESTION)
        c.save()
        c.clipRect(R(cx - wd / 2 - 10, PB - 190, cx - wd / 2 - 10 + (wd + 30) * q_u, PB - 120))
        text(c, QUESTION, cx, PB - 150, TF_FELL_I, 34, (70, 30, 24), align='center', alpha=235)
        c.restore()


# ------------------------------------------------------------------ frost (left) and fire (right)
def _frost_branches(seed=6):
    rng = np.random.default_rng(seed)
    br = []

    def grow(x, y, ang, ln, depth, t0):
        if depth > 5 or ln < 8:
            return
        n = int(rng.integers(3, 6))
        px, py, tt = x, y, t0
        for i in range(n):
            ang += rng.normal(0, 0.25)
            nx, ny = px + math.cos(ang) * ln, py + math.sin(ang) * ln
            br.append((px, py, nx, ny, tt, depth))
            if rng.random() < 0.5:
                grow(nx, ny, ang + rng.choice([-1, 1]) * rng.uniform(0.6, 1.1), ln * 0.62, depth + 1, tt)
            px, py = nx, ny
            tt += ln / 900
    for k in range(16):
        y = PT + 30 + k * 54 + rng.uniform(-14, 14)
        grow(SP - CW + 10, y, rng.uniform(-0.35, 0.35), rng.uniform(40, 70), 0, rng.uniform(0, 0.12))
    return br


FROST = _frost_branches()


def frost(c, t, u):
    """ice creeping across the left side, u = progress 0..1 (reaches the gutter at 1)"""
    if u <= 0:
        return
    edge = SP - CW + (CW + 20) * ease_out(u)
    c.save()
    c.clipRect(R(SP - CW, CT, SP + 2, CB))
    g = skia.GradientShader.MakeLinear([P(SP - CW, 0), P(edge, 0)], [rgb(220, 240, 250, 150), rgb(190, 225, 240, 70), rgb(190, 225, 240, 0)], [0, 0.7, 1])
    c.drawRect(R(SP - CW, CT, edge, CB), skia.Paint(Shader=g))
    tt = u * 0.9
    for (x0, y0, x1, y1, t0, d) in FROST:
        if t0 > tt or x0 > edge:
            continue
        k = clamp((tt - t0) / 0.06)
        x2, y2 = lerp(x0, x1, k), lerp(y0, y1, k)
        c.drawLine(x0, y0, x2, y2, paint(rgb(250, 254, 255, 210 - d * 25), stroke=max(0.8, 3.2 - d * 0.5)))
    c.drawRect(R(SP - CW, CT, edge, CB), skia.Paint(Color=rgb(120, 170, 200, int(36 * u)), BlendMode=skia.BlendMode.kMultiply))
    c.restore()


def fire_page(c, t, u):
    """scorch and flames creeping in from the right edge of the right page"""
    if u <= 0:
        return
    edge = RP[2] - (PW + 10) * ease_out(u)
    c.save()
    c.clipPath(RPATH, doAntiAlias=True)
    pts = [(RP[2] + 40, PT - 40)]
    for k in range(24):
        y = PT - 20 + k * (PB - PT + 40) / 23
        pts.append((edge + 26 * math.sin(y * 0.03 + t * 3) + 16 * math.sin(y * 0.071 + 1.3), y))
    pts.append((RP[2] + 40, PB + 40))
    scorch = poly(pts)
    g = skia.GradientShader.MakeLinear([P(edge, 0), P(RP[2], 0)], [rgb(60, 30, 16, 150), rgb(30, 16, 10, 225)])
    c.drawPath(scorch, skia.Paint(AntiAlias=True, Shader=g))
    c.restore()
    # glowing edge + flames along it
    ep = poly(pts[1:-1], closed=False)
    c.drawPath(ep, blur_paint(rgb(255, 140, 50, 220), 8, stroke=14))
    c.drawPath(ep, paint(rgb(255, 210, 120), stroke=3))
    for k in range(9):
        x, y = pts[1 + k * 2 + 2]
        flames(c, x, y + 10, 46, 70 + 20 * math.sin(k), t, seed=40 + k, a=230)
    additive_glow(c, edge, (PT + PB) / 2, 360, (255, 120, 40), 60 * u)


# ------------------------------------------------------------------ the tide chart (spread)
TIDE_X0, TIDE_X1 = LP[0] + 80, RP[2] - 80
TIDE_AXIS = PB - 140
TIDE_BASE = TIDE_AXIS - 60          # the water never drops below this
TEETH = 4


def tide_points(h=300):
    return saw_pts(TIDE_X0, TIDE_BASE, TIDE_X1 - TIDE_X0, h, TEETH)


def tide_chart(c, t, pop=1.0, side=None):
    """paper water with a sawtooth surface, layered; side clips to one page"""
    c.save()
    if side == 'l':
        c.clipPath(LPATH, doAntiAlias=True)
    elif side == 'r':
        c.clipPath(RPATH, doAntiAlias=True)
    pts = tide_points()
    text(c, 'THE TIDE OF MAGIC', TIDE_X0, PT + 150, TF_CINZEL_B, 30, INK, alpha=220)
    text(c, 'as the stargazer reckons it', TIDE_X0, PT + 190, TF_FELL_I, 26, INK, alpha=190)
    c.drawLine(TIDE_X0 - 20, TIDE_AXIS, TIDE_X1 + 30, TIDE_AXIS, paint(C(INK, 170), stroke=2))
    c.drawPath(poly([(TIDE_X1 + 30, TIDE_AXIS - 7), (TIDE_X1 + 44, TIDE_AXIS), (TIDE_X1 + 30, TIDE_AXIS + 7)]), paint(C(INK, 170)))
    text(c, 'the ages', TIDE_X0, TIDE_AXIS + 40, TF_FELL_I, 26, INK, alpha=170)
    ex, ey = pts[-1]
    c.drawLine(ex, TIDE_AXIS - 8, ex, TIDE_AXIS + 8, paint(C(INK, 200), stroke=2))
    text(c, 'NOW', ex, TIDE_AXIS + 40, TF_CINZEL_B, 22, (120, 40, 26), align='center', alpha=230)
    if pop > 0:
        layers = [((132, 176, 184), 0, 1.0), ((104, 150, 166), 16, 0.94), ((80, 124, 146), 32, 0.88)]
        for col, dy, hk in layers:
            with folded(c, 0, TIDE_AXIS, pop):
                p = skia.Path()
                p.moveTo(TIDE_X0, TIDE_AXIS)
                for (x, y) in pts:
                    p.lineTo(x, TIDE_BASE - (TIDE_BASE - y) * hk + dy)
                p.lineTo(TIDE_X1, TIDE_AXIS)
                p.close()
                sh = skia.Path(p); sh.offset(5, 8)
                c.drawPath(sh, blur_paint(rgb(30, 20, 10, 60), 6))
                c.drawPath(p, paint(rgb(*col)))
        with folded(c, 0, TIDE_AXIS, pop):
            # paper wave strips inside the water
            for k in range(3):
                y = TIDE_BASE + 8 + k * 18
                wp = [(x, y + 4 * math.sin(x * 0.04 + k * 1.7 + t * 1.2)) for x in np.linspace(TIDE_X0 + 6, TIDE_X1 - 6, 120)]
                c.drawPath(poly(wp, closed=False), paint(rgb(210, 230, 230, 120), stroke=2))
            c.drawPath(poly(pts, closed=False), paint(C(INK, 220), stroke=3.4))
            k_last_peak = 2 * (TEETH - 1) + 1
            lx, ly = pts[k_last_peak]
            text(c, 'LONG NIGHT', lx, ly - 22, TF_CINZEL_B, 24, INK, align='center', alpha=230)
            for k in range(TEETH - 1):
                px, py = pts[2 * k + 1]
                text(c, '?', px, py - 16, TF_FELL_I, 30, INK, align='center', alpha=150)
            # annotations along the last cycle
            ax0, ay0 = pts[k_last_peak]
            ang = math.degrees(math.atan2(ey - ay0, ex - ax0))
            mx, my = lerp2((ax0, ay0), (ex, ey), 0.45)
            text(c, 'the long ebb', mx + 14, my - 14, TF_FELL_I, 26, INK, align='center', alpha=200, rot=ang)
            rx0, ry0 = pts[k_last_peak - 1]
            text(c, 'the rise', rx0 - 12, (ry0 + ly) / 2, TF_FELL_I, 24, INK, align='right', alpha=180)
    c.restore()


def tide_dot(c, t, dot, jump=0.0):
    pts = tide_points()
    k_last_peak = 2 * (TEETH - 1) + 1
    a_, b_ = pts[k_last_peak], pts[-1]
    px, py = lerp2(a_, b_, ease(dot))
    if jump > 0:
        py -= 280 * ease_out(jump)
        c.drawLine(px, b_[1], px, py, blur_paint(rgb(255, 210, 120, int(200 * (1 - jump * 0.3))), 5, stroke=8))
    c.drawCircle(px, py, 26, blur_paint(rgb(255, 200, 100, 150), 10))
    c.drawCircle(px, py, 11, paint(C(GOLD)))
    c.drawCircle(px - 3, py - 3, 4, paint(C(GOLD_LT)))


# ------------------------------------------------------------------ the legend spread: two moons, the sun, the dragons
PANEL = (LP[0] + 50, PT + 96, RP[2] - 50, PB - 210)
MOON1 = (700, 380, 70)
MOON2_A = (880, 450, 60)
SUN = (1390, 400, 92)
T_DRIFT = (6.0, 10.2)
T_CRACK = (9.6, 10.8)
T_BURST = 10.9
CRACK_PT = (1252, 430)


def moon2_state(t):
    u = ease(clamp((t - T_DRIFT[0]) / (T_DRIFT[1] - T_DRIFT[0])))
    x = lerp(MOON2_A[0], CRACK_PT[0], u)
    y = lerp(MOON2_A[1], CRACK_PT[1], u) - 40 * math.sin(math.pi * u)
    heat = clamp((t - 7.8) / 2.6)
    crack = clamp((t - T_CRACK[0]) / (T_CRACK[1] - T_CRACK[0]))
    return x, y, heat, crack


def legend_panel(c, t, side=None):
    x0, y0, x1, y1 = PANEL
    c.save()
    clip = {'l': LPATH, 'r': RPATH}.get(side) or skia.Op(RPATH, LPATH, skia.PathOp.kUnion_PathOp)
    c.clipPath(clip, doAntiAlias=True)
    g = skia.GradientShader.MakeLinear([P(0, y0), P(0, y1)], [rgb(20, 26, 52), rgb(36, 40, 74), rgb(66, 56, 86)], [0, 0.7, 1])
    c.drawRect(R(x0, y0, x1, y1), skia.Paint(Shader=g))
    rng = np.random.default_rng(12)
    for _ in range(150):
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1 - 60)
        r = rng.uniform(0.8, 2.4)
        c.drawCircle(x, y, r, paint(rgb(232, 224, 200, int(150 + 80 * math.sin(t * 1.4 + x)))))
    # printed grass sea at the bottom
    p = skia.Path()
    p.moveTo(x0, y1)
    for i in range(int((x1 - x0) / 14) + 1):
        xx = x0 + i * 14
        p.lineTo(xx, y1 - 36 - 10 * math.sin(xx * 0.05))
        p.lineTo(xx + 7, y1 - 24)
    p.lineTo(x1, y1)
    p.close()
    c.drawPath(p, paint(rgb(18, 18, 26)))
    c.drawRect(R(x0, y0, x1, y1), paint(C(GOLD, 200), stroke=3))
    # gutter shading over the panel
    sh = skia.GradientShader.MakeLinear([P(SP - 60, 0), P(SP + 60, 0)], [rgb(0, 0, 0, 0), rgb(0, 0, 0, 90), rgb(0, 0, 0, 0)], [0, 0.5, 1])
    c.drawRect(R(SP - 60, y0, SP + 60, y1), skia.Paint(Shader=sh))
    c.restore()


def quote_lines(c, t, u, a=1.0):
    """the quote's lines in ink (until Luke's exact text is set): handwriting-like strokes + the source"""
    x0, x1 = PANEL[0] + 40, PANEL[2] - 40
    y = PANEL[3] + 62
    widths = [1.0, 0.92, 0.6]
    total = sum(widths)
    acc = 0.0
    for k, wk in enumerate(widths):
        lu = clamp((u * total - acc) / wk)
        acc += wk
        if lu <= 0:
            continue
        yy = y + k * 40
        xe = x0 + (x1 - x0) * wk * lu
        rng = np.random.default_rng(50 + k)
        xx = x0
        while xx < xe:
            wl = rng.uniform(26, 90)
            xw = min(xx + wl, xe)
            pts = [(x, yy + 3 * math.sin(x * 0.35 + k)) for x in np.linspace(xx, xw, max(3, int((xw - xx) / 8)))]
            c.drawPath(poly(pts, closed=False), paint(C(INK, int(170 * a)), stroke=2.2))
            xx = xw + rng.uniform(12, 18)
    if u > 0.97:
        text(c, 'A GAME OF THRONES  ·  CH. 23', PANEL[2] - 40, PANEL[3] + 186, TF_CINZEL, 18, INK, align='right', alpha=int(200 * a))


def popped_disc(c, x, y, r, pop, draw, lift=10):
    """a paper disc lifted off the page: shadow grows with the lift"""
    if pop <= 0.001:
        return
    s = pop
    c.drawCircle(x + lift * 0.6, y + lift, r * s, blur_paint(rgb(0, 0, 0, 110), 6 + lift * 0.4))
    with saved(c):
        c.translate(x, y)
        c.scale(s, s)
        draw(c, r)


def moon_draw(col=(232, 228, 214), crater=(206, 202, 190)):
    def f(c, r):
        c.drawCircle(0, 0, r, paint(rgb(*col)))
        for (dx, dy, rr) in ((-0.3, -0.25, 0.22), (0.32, 0.12, 0.16), (-0.08, 0.4, 0.12), (0.36, -0.36, 0.1)):
            c.drawCircle(dx * r, dy * r, rr * r, paint(rgb(*crater)))
        c.drawCircle(0, 0, r, paint(rgb(120, 110, 90, 120), stroke=1.6))
    return f


def sun_draw(t, dim=0.0):
    def f(c, r):
        col_out = mix((236, 150, 60), (150, 120, 96), dim)
        col_in = mix((252, 214, 130), (190, 170, 140), dim)
        with saved(c):
            c.rotate(t * 6)
            star = skia.Path()
            for k in range(24):
                a = k * math.pi / 12
                rr = r * (1.45 if k % 2 == 0 else 1.08)
                (star.moveTo if k == 0 else star.lineTo)(math.cos(a) * rr, math.sin(a) * rr)
            star.close()
            c.drawPath(star, paint(rgb(*col_out)))
        c.drawCircle(0, 0, r, paint(rgb(*col_in)))
        c.drawCircle(0, 0, r * 0.7, paint(rgb(*mix((255, 234, 170), (200, 184, 156), dim))))
    return f


class Swarm:
    def __init__(self, n=110, seed=8):
        rng = np.random.default_rng(seed)
        self.d = []
        for i in range(n):
            self.d.append(dict(te=T_BURST + i * 0.032 + rng.uniform(0, 0.05), a0=rng.uniform(-math.pi, math.pi), sp=rng.uniform(120, 260),
                               orb=rng.uniform(140, 300), ph=rng.uniform(0, 6.28), w=rng.uniform(0.9, 1.25), sz=rng.uniform(0.32, 0.5),
                               col=rng.integers(0, 3)))

    def pos(self, t, d):
        """book-space position, scale, heading; None before emission"""
        if t < d['te']:
            return None
        age = t - d['te']
        cx, cy = SUN[0], SUN[1]
        # 1) burst out of the crack, 2) curve into an orbit around the sun, 3) break toward the camera
        bx = CRACK_PT[0] + math.cos(d['a0']) * d['sp'] * min(age, 0.6)
        by = CRACK_PT[1] + math.sin(d['a0']) * d['sp'] * min(age, 0.6)
        ang = d['ph'] + d['w'] * (age - 0.6) * 1.6
        ox = cx + math.cos(ang) * d['orb'] * (1.0 + 0.15 * math.sin(age * 0.7 + d['ph']))
        oy = cy + math.sin(ang) * d['orb'] * 0.62
        k = smooth(clamp((age - 0.4) / 1.4))
        x, y = lerp(bx, ox, k), lerp(by, oy, k)
        s = d['sz'] * (0.4 + 0.6 * clamp(age / 1.2))
        # break-out toward the camera from 17.2
        b = clamp((t - 17.2 - (d['te'] - T_BURST) * 0.3) / 1.6)
        if b > 0:
            dx, dy = x - cx, y - cy
            x += dx * 2.2 * ease_in(b)
            y += dy * 2.2 * ease_in(b) - 120 * b
            s *= 1 + 3.0 * ease_in(b)
        heading = math.degrees(ang) + 90 if k > 0.5 else math.degrees(d['a0'])
        return x, y, s, heading

    def draw(self, c, t, glow=0.0):
        cols = [((120, 36, 30), (230, 130, 60)), ((96, 28, 26), (220, 110, 50)), ((140, 50, 34), (250, 160, 80))]
        items = []
        for d in self.d:
            p = self.pos(t, d)
            if p is not None:
                items.append((p[2], p, d))
        items.sort(key=lambda z: z[0])
        for _, (x, y, s, hd), d in items:
            body, edge = cols[int(d['col'])]
            body = mix(body, (200, 90, 40), 0.5 * glow)
            if glow > 0:
                c.drawCircle(x, y, 40 * s, blur_paint(rgb(255, 140, 60, int(70 * glow)), 14 * s))
            paper_dragon(c, x, y, s, t, ph=d['ph'], heading=hd, col=body, edge=edge)


SWARM = Swarm()


def legend_popups(c, t):
    # moons and sun lift off the printed sky
    p1 = popv(t, 3.1, 0.5)
    p2 = popv(t, 3.35, 0.5)
    ps = popv(t, 3.7, 0.55)
    popped_disc(c, MOON1[0], MOON1[1], MOON1[2], p1, moon_draw(), lift=12)
    dim = clamp((t - 14.6) / 2.6)
    popped_disc(c, SUN[0], SUN[1], SUN[2], ps, sun_draw(t, dim), lift=14)
    if ps > 0:
        additive_glow(c, SUN[0], SUN[1], 260, (255, 170, 80), int(90 * ps * (1 - 0.7 * dim)))
    x, y, heat, crack = moon2_state(t)
    if t < T_BURST:
        col = mix((232, 228, 214), (236, 120, 70), heat)
        crater = mix((206, 202, 190), (196, 90, 50), heat)

        def m2(c, r):
            moon_draw(col, crater)(c, r)
            if crack > 0:
                for k, (a, ln) in enumerate(((0.3, 1.0), (2.1, 0.9), (3.9, 0.8), (5.2, 0.95), (1.2, 0.6))):
                    seg = clamp(crack * 1.4 - k * 0.12)
                    if seg <= 0:
                        continue
                    pts = [(0, 0)]
                    for j in range(1, 5):
                        rr = r * ln * j / 4 * seg
                        pts.append((math.cos(a + 0.25 * math.sin(j * 3 + k)) * rr, math.sin(a + 0.25 * math.sin(j * 3 + k)) * rr))
                    c.drawPath(poly(pts, closed=False), paint(rgb(255, 220, 140), stroke=3))
                    c.drawPath(poly(pts, closed=False), blur_paint(rgb(255, 160, 60, 200), 4, stroke=7))
        shake = 4 * crack * math.sin(t * 60)
        popped_disc(c, x + shake, y, MOON2_A[2], p2, m2, lift=12)
        if heat > 0:
            additive_glow(c, x, y, 150, (255, 120, 50), int(90 * heat))
    else:
        # shards fly apart and fall flat
        u = clamp((t - T_BURST) / 1.4)
        for k in range(9):
            a = k * 0.7 + 0.3
            r = 30 + 260 * ease_out(u) * (0.6 + 0.4 * math.sin(k * 2.3))
            sx, sy = x + math.cos(a) * r, y + math.sin(a) * r * 0.8 + 140 * u * u
            with saved(c):
                c.translate(sx, sy); c.rotate(200 * u * (1 + k % 3))
                c.drawPath(poly([(-14, -10), (12, -14), (16, 8), (-8, 14)]), paint(rgb(236, 140, 90, int(255 * (1 - u)))))
        fl = 1 - clamp((t - T_BURST) / 0.8)
        additive_glow(c, x, y, 420, (255, 200, 120), int(230 * fl))
    SWARM.draw(c, t, glow=clamp((t - 14.6) / 2.0))
