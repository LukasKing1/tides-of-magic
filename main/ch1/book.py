"""The book as seen from above, 16:9: Mirri's lap, her painted hands, cover, pages, page flips,
running head with the tide curve."""
import math
import numpy as np
import skia
from lib import *

# ------------------------------------------------------------------ geometry (design space 1920x1080)
SP = 960                  # spine
PT, PB = 116, 966         # page top / bottom
PW = 650                  # page width
RP = (SP, PT, SP + PW, PB)            # right page rect
LP = (SP - PW, PT, SP, PB)            # left page rect
CT, CB = 96, 986          # cover top / bottom
CW = PW + 16              # cover width beyond the spine

PARCH = parchment(W, H, 3)
PARCH2 = parchment(W, H, 11, base=(222, 202, 162))

# Mirri: dark skin with painted ochre lines, dark wool, rust marks, copper bangles
SKIN = (112, 74, 56)
SKIN_DK = (88, 56, 42)
SKIN_LT = (138, 96, 72)
LINES = (204, 112, 62)
WOOL = (46, 39, 37)
WOOL_DK = (32, 27, 26)
WOOL_LT = (66, 56, 52)
RUST = (150, 64, 44)
COPPER = (190, 120, 74)


def page_path(rect, side='r', bulge=9):
    x0, y0, x1, y1 = rect
    p = skia.Path()
    if side == 'r':
        p.moveTo(x0, y0)
        p.quadTo((x0 + x1) / 2, y0 - bulge, x1, y0 + 3)
        p.lineTo(x1, y1 - 3)
        p.quadTo((x0 + x1) / 2, y1 + bulge, x0, y1)
    else:
        p.moveTo(x1, y0)
        p.quadTo((x0 + x1) / 2, y0 - bulge, x0, y0 + 3)
        p.lineTo(x0, y1 - 3)
        p.quadTo((x0 + x1) / 2, y1 + bulge, x1, y1)
    p.close()
    return p


RPATH = page_path(RP, 'r')
LPATH = page_path(LP, 'l')


def parch_fill(c, path, img=None, tint=None):
    c.save()
    c.clipPath(path, doAntiAlias=True)
    c.drawImage(img or PARCH, 0, 0)
    if tint:
        c.drawPath(path, paint(rgb(*tint)))
    c.restore()


def gutter_shadow(c):
    sh = skia.GradientShader.MakeLinear([P(SP - 120, 0), P(SP + 120, 0)],
                                        [rgb(60, 36, 18, 0), rgb(60, 36, 18, 120), rgb(60, 36, 18, 0)], [0.0, 0.5, 1.0])
    c.save()
    c.clipPath(skia.Op(RPATH, LPATH, skia.PathOp.kUnion_PathOp), doAntiAlias=True)
    c.drawRect(R(SP - 120, 0, SP + 120, H), skia.Paint(Shader=sh))
    c.restore()


# ------------------------------------------------------------------ the tide curve (running head emblem)
def saw_pts(x0, y0, w, h, teeth=3):
    """sawtooth: sudden rise, long fall; returns points left->right, ending at a low point"""
    pts = [(x0, y0)]
    tw = w / teeth
    for k in range(teeth):
        xs = x0 + k * tw
        pts.append((xs + tw * 0.12, y0 - h))       # sudden rise
        pts.append((xs + tw, y0))                  # long fall
    return pts


def saw_draw(c, x0, y0, w, h, col=INK, a=220, sw=2.6, teeth=3, dot=1.0, dot_a=None):
    pts = saw_pts(x0, y0, w, h, teeth)
    c.drawPath(poly(pts, closed=False), paint(C(col, a), stroke=sw))
    # gold dot: dot in [0,1] along the path (1 = the last low point = "now")
    segs = list(zip(pts[:-1], pts[1:]))
    L = [math.hypot(b[0] - a_[0], b[1] - a_[1]) for a_, b in segs]
    s = dot * sum(L)
    for (a_, b), l in zip(segs, L):
        if s <= l:
            u = s / l if l else 0
            px, py = lerp2(a_, b, u)
            break
        s -= l
    else:
        px, py = pts[-1]
    da = a if dot_a is None else dot_a
    c.drawCircle(px, py, 9, blur_paint(rgb(255, 200, 100, int(120 * da / 255)), 4))
    c.drawCircle(px, py, 5.5, paint(C(GOLD, da)))
    return px, py


def running_head(c, alpha=210, left_title='OBSERVATIONS OF A STARGAZER', dot=1.0):
    text(c, 'N° 01  ·  THE TIDES OF MAGIC', RP[0] + 56, PT + 58, TF_CINZEL, 18, INK, alpha=alpha)
    saw_draw(c, RP[2] - 168, PT + 62, 110, 26, a=int(alpha * 0.9), dot=dot, dot_a=alpha)
    c.drawLine(RP[0] + 56, PT + 74, RP[2] - 48, PT + 74, paint(C(INK, int(alpha * 0.35)), stroke=1.2))
    text(c, left_title, LP[2] - 56, PT + 58, TF_CINZEL, 18, INK, align='right', alpha=alpha)
    c.drawLine(LP[0] + 48, PT + 74, LP[2] - 56, PT + 74, paint(C(INK, int(alpha * 0.35)), stroke=1.2))
    # folio numbers
    text(c, 'i', LP[0] + 70, PB - 40, TF_FELL_I, 22, INK, alpha=int(alpha * 0.7))
    text(c, 'ii', RP[2] - 70, PB - 40, TF_FELL_I, 22, INK, align='right', alpha=int(alpha * 0.7))


# ------------------------------------------------------------------ background, lap
def background(c, t, warm=1.0):
    g = skia.GradientShader.MakeLinear([P(0, 0), P(0, H)], [rgb(14, 13, 16), rgb(40, 26, 20)])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=g))
    fl = flicker(t)
    gl = skia.GradientShader.MakeRadial(P(W * 0.78, H * 1.08), 1250 * (0.96 + 0.04 * fl),
                                        [rgb(170, 80, 30, int(80 * fl * warm)), rgb(0, 0, 0, 0)])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=gl, BlendMode=skia.BlendMode.kPlus))


def lap(c, t):
    """Mirri's lap: heavy dark wool with rust marks, filling the frame around the book"""
    c.drawRect(R(-900, -600, W + 900, H + 600), paint(C(WOOL_DK)))
    for k, x in enumerate((-640, -350, -60, 200, 470, 760, 1060, 1350, 1640, 1900, 2180, 2460)):
        sw = 10 * math.sin(t * 0.55 + k * 1.3)
        c.drawPath(smooth_path([(x - 60, -600), (x - 10, -200), (x + 30 + sw, 300), (x - 20, 620), (x + 50 + sw, 1120), (x + 60, 1700), (x + 160, 1700), (x + 150, 1120),
                                (x + 100 + sw, 620), (x + 130, 300), (x + 90, -200), (x + 70, -600)]), paint(C(WOOL, 235)))
        c.drawPath(smooth_path([(x + 20, -600), (x + 40, -200), (x + 60 + sw, 300), (x + 30, 620), (x + 80 + sw, 1120), (x + 90, 1700), (x + 106, 1700), (x + 96, 1120),
                                (x + 60 + sw, 620), (x + 76, 300), (x + 56, -200), (x + 40, -600)]), paint(C(WOOL_LT, 110)))
    # rust-red painted marks on the wool, half hidden under the book
    for (x, y, s) in ((150, 230, 1.0), (1780, 300, 0.9), (110, 820, 0.8), (1820, 860, 1.1)):
        c.drawCircle(x, y, 26 * s, paint(C(RUST, 120), stroke=5))
        c.drawCircle(x, y, 6 * s, paint(C(RUST, 140)))
        for k in range(3):
            c.drawLine(x - 40 * s, y + (44 + 12 * k) * s, x + 40 * s, y + (44 + 12 * k) * s, paint(C(RUST, 100), stroke=3))
    vg = skia.GradientShader.MakeRadial(P(W / 2, H / 2), 1150, [rgb(0, 0, 0, 0), rgb(0, 0, 0, 150)], [0.55, 1.0])
    c.drawRect(R(-900, -600, W + 900, H + 600), skia.Paint(Shader=vg))


def book_shadow(c, open_k=1.0):
    """open_k: 0 closed .. 1 the cover lies open on the left"""
    r = R(SP - 6, CT + 8, SP + CW + 18, CB + 26)
    c.drawRoundRect(r, 18, 18, blur_paint(rgb(8, 4, 2, 160), 22))
    if open_k > 0:
        x0 = SP - CW * open_k
        c.drawRoundRect(R(x0 - 6, CT + 8, SP + 10, CB + 26), 18, 18, blur_paint(rgb(8, 4, 2, int(160 * open_k)), 22))


def book_block(c, left_pages=False):
    """back board under the right-hand pages + page edges (the front board is the cover itself)"""
    c.drawRoundRect(R(SP - 14, CT, SP + CW, CB), 14, 14, paint(rgb(70, 40, 27)))
    for k in range(5):
        c.drawLine(RP[2] + 2 + k * 2, PT + 8, RP[2] + 2 + k * 2, PB - 8, paint(rgb(200, 180, 140, 200 - k * 30), stroke=1.4))
        if left_pages:
            c.drawLine(LP[0] - 2 - k * 2, PT + 8, LP[0] - 2 - k * 2, PB - 8, paint(rgb(200, 180, 140, 200 - k * 30), stroke=1.4))


# ------------------------------------------------------------------ cover
def cover_front(c, emboss=1.0, glint=-1.0):
    """front cover in the 'lying right' frame (x from SP to SP+CW)"""
    x0, y0, x1, y1 = SP, CT, SP + CW, CB
    lg = skia.GradientShader.MakeLinear([P(x0, y0), P(x1, y1)], [rgb(98, 58, 38), rgb(58, 33, 22)])
    c.drawRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 12, 12), skia.Paint(AntiAlias=True, Shader=lg))
    # leather grain
    rng = np.random.default_rng(5)
    for _ in range(160):
        x, y = rng.uniform(x0 + 10, x1 - 10), rng.uniform(y0 + 10, y1 - 10)
        c.drawCircle(x, y, rng.uniform(0.8, 2.2), paint(rgb(40, 22, 14, 60)))
    c.drawRect(R(x0 + 40, y0 + 58, x1 - 40, y1 - 58), paint(C(GOLD, int(70 + 150 * emboss)), stroke=3))
    c.drawRect(R(x0 + 58, y0 + 76, x1 - 58, y1 - 76), paint(C(GOLD, int(40 + 100 * emboss)), stroke=1.6))
    cx = (x0 + x1) / 2
    # title: blind-tooled (dark) -> gold leaf (emboss)
    for s, yy in (('THE TIDES', y0 + 330), ('OF MAGIC', y0 + 420)):
        text(c, s, cx + 2, yy + 3, TF_CINZEL_B, 70, (24, 12, 8), align='center', alpha=150)
        text(c, s, cx, yy, TF_CINZEL_B, 70, (78, 44, 30), align='center')
        if emboss > 0:
            c.save()
            f = skia.Font(TF_CINZEL_B, 70)
            wd = f.measureText(s)
            # gold fill wipes left->right
            c.clipRect(R(cx - wd / 2 - 10, yy - 70, cx - wd / 2 - 10 + (wd + 20) * emboss, yy + 20))
            text(c, s, cx, yy, TF_CINZEL_B, 70, GOLD, align='center')
            c.restore()
    # emblem: tide curve with a dot at the low point
    saw_draw(c, cx - 110, y0 + 560, 220, 60, col=GOLD, a=int(80 + 175 * emboss), sw=5, dot=1.0, dot_a=int(80 + 175 * emboss))
    text(c, 'N° 01', cx, y0 + 690, TF_CINZEL, 34, GOLD, align='center', alpha=int(80 + 175 * emboss))
    if glint >= 0:
        gx = lerp(x0 - 200, x1 + 200, glint)
        g = skia.GradientShader.MakeLinear([P(gx - 120, y0), P(gx + 120, y1)],
                                           [rgb(255, 240, 200, 0), rgb(255, 240, 200, 120), rgb(255, 240, 200, 0)], [0, 0.5, 1])
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 12, 12), skia.ClipOp.kIntersect, True)
        c.drawRect(R(x0, y0, x1, y1), skia.Paint(Shader=g, BlendMode=skia.BlendMode.kPlus))
        c.restore()


def cover_back(c):
    """inside of the front cover, drawn where it lies when open (left of the spine)"""
    x0, y0, x1, y1 = SP - CW, CT, SP, CB
    c.drawRRect(skia.RRect.MakeRectXY(R(x0, y0, x1, y1), 12, 12), paint(rgb(78, 46, 30)))
    ep = R(x0 + 22, y0 + 20, x1 - 4, y1 - 20)
    c.save()
    c.clipRect(ep, skia.ClipOp.kIntersect, True)
    c.drawImage(PARCH2, 0, 0)
    # marbled endpaper hint
    for k in range(14):
        y = y0 + 40 + k * 64
        c.drawPath(smooth_path([(x0, y), (x0 + 200, y + 18), (x0 + 420, y - 14), (x1, y + 10), (x1, y + 24), (x0 + 420, y), (x0 + 200, y + 32), (x0, y + 14)]),
                   paint(rgb(120, 70, 46, 46)))
    c.restore()


# ------------------------------------------------------------------ flaps (cover or page turning around the spine)
def flap_matrix(phi, src, x0=SP, bump=40):
    L = src[2] - src[0]
    xe = x0 + L * math.cos(phi)
    b = bump * math.sin(phi)
    top, bot = src[1], src[3]
    s = [P(src[0], src[1]), P(src[2], src[1]), P(src[2], src[3]), P(src[0], src[3])]
    if math.cos(phi) >= 0:
        d = [P(x0, top), P(xe, top - b), P(xe, bot + b), P(x0, bot)]
    else:
        # seen from the back: the far edge is now on the left; keep front/back drawing in the same frame
        d = [P(x0, top), P(xe, top - b), P(xe, bot + b), P(x0, bot)]
    m = skia.Matrix()
    m.setPolyToPoly(s, d)
    return m


def draw_flap(c, phi, front, back, src, shade_k=0.35):
    """phi=0: lying on the right; phi=pi: lying on the left.
    front/back draw in the 'lying right' frame; back is mirrored automatically."""
    if abs(math.cos(phi)) < 0.02:
        return
    m = flap_matrix(phi, src)
    c.save()
    c.concat(m)
    if math.cos(phi) >= 0:
        front(c)
        dark = shade_k * math.sin(phi)
    else:
        # back() draws in left-page coordinates; mirror about the spine so the flap matrix maps it back unmirrored
        c.translate(2 * SP, 0)
        c.scale(-1, 1)
        back(c)
        dark = shade_k * 0.5 * math.sin(phi)
    c.drawRect(R(src[0] - 30, src[1] - 30, src[2] + 30, src[3] + 30), paint(rgb(10, 6, 4, int(255 * dark))))
    c.restore()


def flap_shadow(c, phi, top=CT, bot=CB, L=CW):
    if phi <= 0.01 or phi >= math.pi - 0.01:
        return
    xe = SP + L * math.cos(phi)
    sgn = 1 if math.cos(phi) >= 0 else -1
    wdt = 130 * math.sin(phi)
    x1 = xe + sgn * wdt
    g = skia.GradientShader.MakeLinear([P(xe, 0), P(x1, 0)], [rgb(20, 10, 6, int(110 * math.sin(phi))), rgb(20, 10, 6, 0)])
    c.drawRect(R(min(xe, x1), top, max(xe, x1), bot), skia.Paint(Shader=g))


# ------------------------------------------------------------------ hands (seen from above, forearms from the bottom edge)
def forearm(c, base, wrist, w0=200, w1=104):
    ang = math.atan2(wrist[1] - base[1], wrist[0] - base[0])
    nx, ny = -math.sin(ang), math.cos(ang)
    pts = [(base[0] + nx * w0 / 2, base[1] + ny * w0 / 2), (wrist[0] + nx * w1 / 2, wrist[1] + ny * w1 / 2),
           (wrist[0] - nx * w1 / 2, wrist[1] - ny * w1 / 2), (base[0] - nx * w0 / 2, base[1] - ny * w0 / 2)]
    c.drawPath(poly(pts), paint(C(SKIN)))
    c.drawPath(poly([pts[0], pts[1], lerp2(pts[1], pts[2], 0.3), lerp2(pts[0], pts[3], 0.3)]), paint(C(SKIN_DK, 140)))
    # painted lines (godswife marks) on the forearm
    for k in range(3):
        u = 0.55 + 0.1 * k
        cx, cy = lerp(base[0], wrist[0], u), lerp(base[1], wrist[1], u)
        ww = lerp(w0, w1, u) / 2 - 6
        p = skia.Path()
        p.moveTo(cx + nx * ww, cy + ny * ww)
        p.quadTo(cx + math.cos(ang) * 14, cy + math.sin(ang) * 14, cx - nx * ww, cy - ny * ww)
        c.drawPath(p, paint(C(LINES, 190), stroke=3.2))
    # copper bangles near the wrist
    for k in range(3):
        u = 0.84 + 0.045 * k
        cx, cy = lerp(base[0], wrist[0], u), lerp(base[1], wrist[1], u)
        ww = lerp(w0, w1, u) / 2 + 3
        c.drawLine(cx + nx * ww, cy + ny * ww, cx - nx * ww, cy - ny * ww, paint(C(COPPER), stroke=6 - k))
    # wide wool sleeve with a rust band
    sl = 0.42
    s0 = (lerp(base[0], wrist[0], sl), lerp(base[1], wrist[1], sl))
    ws = lerp(w0, w1, sl) / 2 + 44
    b0 = (base[0] + nx * (w0 / 2 + 50), base[1] + ny * (w0 / 2 + 50))
    b1 = (base[0] - nx * (w0 / 2 + 50), base[1] - ny * (w0 / 2 + 50))
    e0 = (s0[0] + nx * ws, s0[1] + ny * ws)
    e1 = (s0[0] - nx * ws, s0[1] - ny * ws)
    c.drawPath(poly([b0, e0, e1, b1]), paint(C(WOOL)))
    c.drawPath(poly([b0, e0, lerp2(e0, e1, 0.3), lerp2(b0, b1, 0.3)]), paint(C(WOOL_LT, 150)))
    c.drawLine(*lerp2(e0, b0, 0.06), *lerp2(e1, b1, 0.06), paint(C(RUST, 230), stroke=10))
    c.drawLine(*lerp2(e0, b0, 0.16), *lerp2(e1, b1, 0.16), paint(C(RUST, 160), stroke=4))
    return ang


def hand(c, wrist, ang, kind='grip', s=1.0, left=False):
    """back of the hand from above; painted lines on the back of the hand"""
    with saved(c):
        c.translate(*wrist)
        c.rotate(math.degrees(ang) + 90)
        c.scale(-s if left else s, s)
        sk, dk = paint(C(SKIN)), paint(C(SKIN_DK))
        if kind == 'grip':
            c.drawPath(smooth_path([(-38, 6), (-42, -40), (-22, -80), (22, -82), (42, -44), (38, 8)]), sk)
            for k in range(4):
                x = -28 + k * 19
                c.drawRoundRect(R(x - 8.5, -98, x + 8.5, -62), 8, 8, sk)
                c.drawLine(x - 6, -86, x + 6, -86, paint(C(SKIN_DK, 120), stroke=1.6))
            c.drawPath(smooth_path([(-36, -20), (-64, -54), (-72, -86), (-58, -94), (-42, -66), (-26, -40)]), dk)
        elif kind == 'flat':      # fingers spread on the page
            c.drawPath(smooth_path([(-38, 6), (-42, -40), (-22, -80), (22, -82), (42, -44), (38, 8)]), sk)
            for k, a in enumerate((-14, -4, 5, 14)):
                with saved(c):
                    c.translate(-28 + k * 19, -70)
                    c.rotate(a)
                    c.drawRoundRect(R(-8.5, -62, 8.5, 6), 8, 8, sk)
            c.drawPath(smooth_path([(-36, -20), (-74, -40), (-84, -58), (-70, -64), (-42, -46), (-26, -36)]), dk)
        # painted marks: a dotted arc + a line down each finger base
        p = skia.Path()
        p.moveTo(-26, -24)
        p.quadTo(0, -52, 26, -24)
        c.drawPath(p, paint(C(LINES, 210), stroke=3))
        for k in range(5):
            c.drawCircle(-24 + k * 12, -12, 2.6, paint(C(LINES, 210)))
        c.drawLine(0, -40, 0, -64, paint(C(LINES, 190), stroke=2.6))


def hands_hold(c, t, lpos=None, rpos=None, lkind='grip', rkind='grip', right=True, left=True, breathe=True):
    by = 3 * math.sin(t * 1.4) if breathe else 0
    if left:
        lw = lpos or (LP[0] + 96, PB + 70 + by)
        a = forearm(c, (LP[0] - 190, H + 260), lw)
        hand(c, lw, a, lkind, 1.65, left=True)
    if right:
        rw = rpos or (RP[2] - 96, PB + 70 + by)
        a = forearm(c, (RP[2] + 190, H + 260), rw)
        hand(c, rw, a, rkind, 1.65)
