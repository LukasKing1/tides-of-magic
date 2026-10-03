"""The places of chapter 1 (placeholders until Luke's painted 16:9 images arrive), Mirri seen from
behind, paper dragons, smoke, the plate that burns through."""
import math
import numpy as np
import skia
from lib import *
from PIL import Image

PLATE2 = load_img('/home/claude/short1/plate2.png')

# ------------------------------------------------------------------ paper dragon (cut paper silhouette)
def paper_dragon(c, x, y, s, t, ph=0.0, heading=0.0, col=(120, 36, 30), edge=(220, 120, 60), a=255, flap_speed=9.0):
    """small cut-paper dragon flying toward +x (heading in degrees). wing beat from t."""
    if s < 0.02 or a <= 0:
        return
    wing = math.sin(t * flap_speed + ph)
    with saved(c):
        c.translate(x, y)
        c.rotate(heading)
        c.scale(s, s)
        body = paint(C(col, a))
        # tail
        c.drawPath(smooth_path([(-14, 0), (-46, -4), (-74, 6), (-92, -2), (-74, 12), (-44, 8), (-12, 8)]), body)
        c.drawPath(poly([(-92, -2), (-104, -10), (-100, 6)]), body)
        # body + neck + head
        c.drawOval(R(-22, -8, 26, 12), body)
        c.drawPath(smooth_path([(18, -2), (34, -12), (48, -14), (58, -10), (50, -4), (36, 4), (22, 8)]), body)
        c.drawPath(poly([(52, -14), (46, -24), (58, -14)]), body)
        # wings: scale in y by the beat (paper flapping)
        for side, k in ((-1, 1.0), (1, 0.75)):
            with saved(c):
                c.scale(1, side * (0.25 + 0.75 * abs(wing)) * (1 if wing >= 0 else -0.6))
                c.drawPath(poly([(-6, -4), (6, -60), (-14, -52), (-28, -40), (-36, -24), (-20, -6)]), paint(C(mix(col, (40, 12, 10), 0.25 * k), a)))
        # paper edge highlight
        c.drawLine(-20, -8, 24, -8, paint(C(edge, int(a * 0.5)), stroke=1.6))


# ------------------------------------------------------------------ night sky + Dothraki Sea (placeholder for 1-A)
_rs = np.random.default_rng(23)
STARS = [(_rs.uniform(-200, W + 200), _rs.uniform(-60, 700), _rs.uniform(0.7, 2.4), _rs.uniform(0, 6.28)) for _ in range(520)]


def night_sky(c, t, cam=0.0, horizon=760, moon=(1360, 250), moon_r=86, star_a=1.0):
    g = skia.GradientShader.MakeLinear([P(0, 0), P(0, horizon)], [rgb(7, 9, 20), rgb(14, 18, 36), rgb(44, 40, 66)], [0, 0.62, 1])
    c.drawRect(R(-10, -10, W + 10, horizon + 40), skia.Paint(Shader=g))
    # milky band
    mb = skia.Path()
    mb.moveTo(-200, 520); mb.cubicTo(400, 300, 1100, 120, 2100, -40); mb.lineTo(2100, 120); mb.cubicTo(1100, 280, 400, 460, -200, 680); mb.close()
    c.drawPath(mb, blur_paint(rgb(120, 120, 170, 22), 60))
    for (x, y, r, ph) in STARS:
        xx = (x - cam * 0.05) % (W + 400) - 200
        if y > horizon - 30:
            continue
        a = int(star_a * (140 + 90 * math.sin(t * 1.3 + ph)))
        c.drawCircle(xx, y, r, paint(rgb(232, 226, 212, a)))
    mx, my = moon[0] - cam * 0.08, moon[1]
    c.drawCircle(mx, my, moon_r * 3.2, blur_paint(rgb(200, 210, 240, 30), 60))
    c.drawCircle(mx, my, moon_r * 1.5, blur_paint(rgb(220, 226, 240, 40), 26))
    c.drawCircle(mx, my, moon_r, paint(rgb(232, 228, 214)))
    for (dx, dy, rr) in ((-24, -18, 18), (28, 10, 13), (-6, 34, 10), (32, -32, 8), (-40, 22, 7)):
        c.drawCircle(mx + dx, my + dy, rr, paint(rgb(208, 204, 192)))
    c.drawCircle(mx + 18, my - 10, moon_r, paint(rgb(170, 180, 210, 26)))


def grass_band(c, t, y, amp, col, cam, par, seed, blade=26, height=60, wind=1.0, x0=-200, x1=W + 200):
    """a silhouette band with grass tips along its top edge, swaying in wind waves"""
    rng = np.random.default_rng(seed)
    n = int((x1 - x0) / blade) + 2
    off = (cam * par) % blade
    ph = rng.uniform(0, 6.28, n + 4)
    hs = rng.uniform(0.55, 1.0, n + 4)
    p = skia.Path()
    p.moveTo(x0, H + 20)
    p.lineTo(x0, y)
    for i in range(n):
        xb = x0 + i * blade - off
        k = (i + int(cam * par // blade)) % (n + 4)
        wave = math.sin(t * 1.3 * wind + xb * 0.006 + ph[k] * 0.3)
        bend = 14 * wind * wave + 4 * math.sin(t * 3.1 + ph[k])
        hgt = height * hs[k] * (0.9 + 0.1 * wave)
        base_y = y + amp * math.sin(xb * 0.004 + seed)
        p.lineTo(xb, base_y)
        p.quadTo(xb + blade * 0.3 + bend * 0.4, base_y - hgt * 0.6, xb + blade * 0.45 + bend, base_y - hgt)
        p.quadTo(xb + blade * 0.55 + bend * 0.4, base_y - hgt * 0.5, xb + blade * 0.9, base_y)
    p.lineTo(x1, y)
    p.lineTo(x1, H + 20)
    p.close()
    c.drawPath(p, paint(C(col)))


KHAL = [(_rs.uniform(-100, W + 600), _rs.uniform(0, 1), _rs.uniform(0, 6.28)) for _ in range(46)]


def dothraki(c, t, cam=0.0, fade=1.0):
    """placeholder for image 1-A: the Dothraki Sea at night, khalasar fires on the horizon"""
    night_sky(c, t, cam)
    hz = 760
    # far hills
    c.drawPath(smooth_path([(-200, 790), (100, 742), (420, 762), (760, 728), (1100, 756), (1420, 732), (1760, 760), (2120, 740), (2120, 900), (-200, 900)]),
               paint(rgb(28, 30, 46)))
    # far plain
    g = skia.GradientShader.MakeLinear([P(0, 770), P(0, H)], [rgb(30, 32, 44), rgb(16, 16, 22)])
    c.drawRect(R(-10, 770, W + 10, H + 10), skia.Paint(Shader=g))
    # khalasar fires: tiny flickering dots + tents
    for (x, d, ph) in KHAL:
        xx = (x - cam * 0.22) % (W + 700) - 200
        yy = 776 + d * 26
        s = 0.5 + 0.7 * d
        c.drawCircle(xx, yy, 16 * s, blur_paint(rgb(255, 140, 60, int(80 * flicker(t, ph))), 8 * s))
        c.drawCircle(xx, yy, 2.4 * s, paint(rgb(255, 200, 120)))
        c.drawPath(poly([(xx + 10 * s, yy + 2), (xx + 22 * s, yy - 14 * s), (xx + 34 * s, yy + 2)]), paint(rgb(24, 22, 30)))
    grass_band(c, t, 845, 10, (34, 34, 42), cam, 0.45, 3, blade=18, height=26, wind=0.8)
    grass_band(c, t, 900, 16, (26, 25, 32), cam, 0.7, 5, blade=26, height=48, wind=1.0)
    grass_band(c, t, 985, 22, (17, 16, 21), cam, 1.0, 7, blade=40, height=96, wind=1.2)
    # moonlight on the grass tops
    g2 = skia.GradientShader.MakeRadial(P(1360 - cam * 0.08, 250), 1200, [rgb(150, 160, 200, 26), rgb(0, 0, 0, 0)])
    c.drawRect(R(0, 0, W, H), skia.Paint(Shader=g2, BlendMode=skia.BlendMode.kPlus))


# ------------------------------------------------------------------ Qarth (placeholder for plate 1-B)
def qarth_image():
    w, h = 560, 700
    s = skia.Surface(w, h)
    c = s.getCanvas()
    g = skia.GradientShader.MakeLinear([P(0, 0), P(0, h)], [rgb(70, 44, 74), rgb(196, 104, 70), rgb(236, 170, 104)], [0, 0.55, 0.78])
    c.drawRect(R(0, 0, w, h), skia.Paint(Shader=g))
    c.drawCircle(380, 420, 60, blur_paint(rgb(255, 210, 140, 160), 20))
    c.drawCircle(380, 420, 34, paint(rgb(255, 226, 170)))
    # towers and domes
    sil = rgb(70, 36, 40)
    for (x, wd, ht) in ((60, 26, 330), (130, 40, 250), (210, 22, 380), (300, 46, 300), (440, 30, 350), (500, 24, 270)):
        c.drawRect(R(x - wd / 2, h - ht - 60, x + wd / 2, h), paint(sil))
        c.drawPath(poly([(x - wd / 2 - 6, h - ht - 60), (x, h - ht - 110), (x + wd / 2 + 6, h - ht - 60)]), paint(sil))
    for (x, r) in ((170, 60), (360, 74), (260, 48)):
        c.drawCircle(x, h - 230, r, paint(rgb(86, 44, 46)))
        c.drawRect(R(x - r, h - 230, x + r, h), paint(rgb(86, 44, 46)))
    # three walls
    for k, (yy, col) in enumerate(((h - 190, (120, 56, 44)), (h - 130, (104, 92, 90)), (h - 70, (52, 44, 50)))):
        c.drawRect(R(0, yy, w, h), paint(rgb(*col)))
        for x in range(0, w, 24):
            c.drawRect(R(x, yy - 12, x + 12, yy), paint(rgb(*col)))
    # caravan
    for k in range(6):
        x = 70 + k * 60
        c.drawOval(R(x - 18, h - 52, x + 18, h - 30), paint(rgb(30, 22, 26)))
        c.drawRect(R(x - 4, h - 70, x + 4, h - 40), paint(rgb(30, 22, 26)))
    return s.makeImageSnapshot()


QARTH = qarth_image()


def plate_card(c, img, cx, base_y, w, h, label, pop, t, a=1.0):
    """a framed plate that pops up from the ground (fold about its base line)"""
    if pop <= 0.001 or a <= 0:
        return
    with folded(c, cx, base_y, pop), layer_alpha(c, a):
        x0, y0 = cx - w / 2, base_y - h
        c.drawRect(R(x0 + 10, y0 + 14, x0 + w + 10, base_y + 14), blur_paint(rgb(0, 0, 0, 140), 12))
        c.drawRect(R(x0 - 14, y0 - 14, x0 + w + 14, base_y + 14), paint(rgb(206, 186, 146)))
        draw_img(c, img, R(x0, y0, x0 + w, base_y))
        c.drawRect(R(x0, y0, x0 + w, base_y), paint(rgb(150, 110, 60), stroke=5))
        if label:
            f = skia.Font(TF_FELL_SC, 24)
            lw = f.measureText(label)
            ly = y0 + 40
            c.drawRect(R(cx - lw / 2 - 18, ly - 28, cx + lw / 2 + 18, ly + 10), paint(rgb(222, 204, 164)))
            text(c, label, cx, ly, TF_FELL_SC, 24, INK, align='center')
        # stand tab
        c.drawRect(R(cx - 40, base_y, cx + 40, base_y + 16), paint(rgb(170, 150, 112)))


# ------------------------------------------------------------------ dawn at the burnt pyre (placeholder for 1-C)
PYRE = (1250, 868)
_rp = np.random.default_rng(9)
LOGS = [(_rp.uniform(0, 6.28), _rp.uniform(120, 230), _rp.uniform(14, 22)) for _ in range(16)]
SHELLS = [(_rp.uniform(-170, 170), _rp.uniform(-18, 30), _rp.uniform(0, 360), _rp.uniform(0.7, 1.3)) for _ in range(7)]


def dawn_sky(c, t, horizon=760):
    g = skia.GradientShader.MakeLinear([P(0, 0), P(0, horizon)], [rgb(36, 44, 66), rgb(86, 92, 112), rgb(196, 150, 132), rgb(232, 186, 150)], [0, 0.5, 0.86, 1])
    c.drawRect(R(-10, -10, W + 10, horizon + 40), skia.Paint(Shader=g))
    for (x, y, r, ph) in STARS[:90]:
        if y < 280:
            c.drawCircle(x, y, r * 0.8, paint(rgb(232, 226, 212, int(60 + 30 * math.sin(t + ph)))))
    # thin cloud bands
    for k, (yy, x0, x1, a) in enumerate(((560, 200, 900, 50), (610, 1100, 1900, 40), (480, 900, 1500, 30))):
        c.drawRoundRect(R(x0, yy, x1, yy + 14), 7, 7, blur_paint(rgb(240, 200, 180, a), 6))


def dawn_land(c, t):
    hz = 760
    c.drawPath(smooth_path([(-200, 780), (200, 728), (520, 756), (820, 720), (1160, 748), (1500, 716), (1800, 744), (2120, 730), (2120, 900), (-200, 900)]),
               paint(rgb(92, 82, 92)))
    # mud-brick domes of a shepherd town on the far hill
    for (x, r) in ((300, 20), (334, 14), (360, 24), (398, 12), (1620, 18), (1650, 26), (1690, 14)):
        y = 744 if x < 1000 else 732
        c.drawCircle(x, y, r, paint(rgb(120, 96, 92)))
        c.drawRect(R(x - r, y, x + r, y + 22), paint(rgb(120, 96, 92)))
    g = skia.GradientShader.MakeLinear([P(0, 760), P(0, H)], [rgb(120, 104, 100), rgb(70, 60, 58), rgb(44, 38, 38)], [0, 0.4, 1])
    c.drawRect(R(-10, 770, W + 10, H + 10), skia.Paint(Shader=g))
    grass_band(c, t, 800, 6, (104, 92, 88), 0, 0, 11, blade=16, height=14, wind=0.5)
    # ash field
    c.drawOval(R(PYRE[0] - 460, PYRE[1] - 70, PYRE[0] + 460, PYRE[1] + 110), blur_paint(rgb(40, 34, 34, 200), 26))
    c.drawOval(R(PYRE[0] - 330, PYRE[1] - 46, PYRE[0] + 330, PYRE[1] + 80), paint(rgb(58, 52, 52)))
    c.drawOval(R(PYRE[0] - 300, PYRE[1] - 38, PYRE[0] + 300, PYRE[1] + 70), paint(rgb(88, 84, 82)))


def pyre_remains(c, t, glow=1.0):
    px, py = PYRE
    for (ang, ln, wd) in LOGS:
        x1, y1 = px + math.cos(ang) * ln, py + math.sin(ang) * ln * 0.26
        c.drawLine(px + math.cos(ang) * 30, py + math.sin(ang) * 8, x1, y1, paint(rgb(30, 24, 22), stroke=wd))
        c.drawLine(px + math.cos(ang) * 30, py + math.sin(ang) * 8 - 3, x1, y1 - 3, paint(rgb(64, 54, 50), stroke=wd * 0.3))
    # embers in the ash
    for k in range(26):
        a = k * 2.399
        rr = 30 + (k * 37) % 170
        x, y = px + math.cos(a) * rr, py + math.sin(a) * rr * 0.24
        f = 0.5 + 0.5 * math.sin(t * (1.3 + k * 0.17) + k)
        c.drawCircle(x, y, 2.2 + (k % 3), paint(rgb(255, 120 + 60 * f, 50, int(glow * (90 + 120 * f)))))
    additive_glow(c, px, py, 240, (255, 110, 40), int(50 * glow))
    # eggshell fragments
    for (dx, dy, rot, s) in SHELLS:
        with saved(c):
            c.translate(px + dx, py + dy)
            c.rotate(rot)
            c.scale(s, s)
            c.drawPath(smooth_path([(-16, -4), (0, -12), (16, -6), (10, 6), (-10, 7)]), paint(rgb(60, 58, 56)))
            c.drawPath(smooth_path([(-16, -4), (0, -12), (16, -6)], closed=False), paint(rgb(150, 140, 120), stroke=2))


class Smoke:
    def __init__(self, n, seed, x, y, spread=60, rise=55, life=7.0, size=(14, 40), drift=26):
        rng = np.random.default_rng(seed)
        self.p = [dict(x=x + rng.uniform(-spread, spread), t0=rng.uniform(0, life), sz=rng.uniform(*size), ph=rng.uniform(0, 6.28))
                  for _ in range(n)]
        self.y, self.rise, self.life, self.drift = y, rise, life, drift

    def draw(self, c, t, a=1.0, col=(150, 150, 156)):
        if a <= 0:
            return
        for p in self.p:
            age = (t - p['t0']) % self.life
            u = age / self.life
            x = p['x'] + self.drift * age + 30 * math.sin(t * 0.5 + p['ph'])
            y = self.y - self.rise * age
            r = p['sz'] * (0.5 + 2.2 * u)
            al = a * math.sin(math.pi * u) ** 1.5 * 0.55
            c.drawCircle(x, y, r, blur_paint(rgb(*col, int(110 * al)), r * 0.6))


# ------------------------------------------------------------------ Mirri seen from behind (standing)
WOOL = (46, 39, 37)
WOOL2 = (58, 49, 46)
WOOL_DK = (30, 26, 25)
RUST = (150, 64, 44)
SKIN = (112, 74, 56)
SKIN_DK = (86, 56, 42)
HAIR = (18, 16, 18)
HAIR_LT = (52, 48, 54)
COPPER = (190, 120, 74)
LINES = (204, 112, 62)


def mirri_pose(t, keys):
    """keys: list of (t, x, y, scale). returns position + walk phase"""
    x = key_interp([(k[0], k[1]) for k in keys], t, smooth)
    y = key_interp([(k[0], k[2]) for k in keys], t, smooth)
    s = key_interp([(k[0], k[3]) for k in keys], t, smooth)
    # walking speed -> step phase
    dt = 1 / 30
    x2 = key_interp([(k[0], k[1]) for k in keys], t + dt, smooth)
    speed = abs(x2 - x) / dt
    return x, y, s, speed


def mirri_back(c, t, x, y, s, walk=0.0, lift=0.0, head_down=0.0, rim_from=(1250, 860), rim=1.0, light=(200, 150, 120)):
    """Mirri from behind. origin (x, y) = waist centre; walk 0..1 = how much she is walking now.
    lift 0..1 = raises the book in front of her (elbows out, head down)."""
    ph = t * 5.2
    bob = 7 * walk * abs(math.sin(ph))
    sway = 1.4 * walk * math.sin(ph) + 0.6 * math.sin(t * 0.8)
    br = 1 + 0.008 * math.sin(t * 1.6)
    with saved(c):
        c.translate(x, y - bob * s)
        c.rotate(sway)
        c.scale(s, s)
        # ---- shapes
        robe = smooth_path([(-58, -376), (58, -376), (138, -346), (168, -300), (176, -180), (172, -40), (186, 180), (200, 460),
                            (-200, 460), (-186, 180), (-172, -40), (-176, -180), (-168, -300), (-138, -346)])
        hood = smooth_path([(-92, -380), (0, -360), (92, -380), (118, -340), (40, -320), (-40, -320), (-118, -340)])
        # right arm (screen right) hangs, swings with the walk
        swing = 9 * walk * math.sin(ph)
        ra = skia.Path()
        with saved(c):
            pass
        m = skia.Matrix()
        m.setRotate(swing, 150, -320)
        rarm = smooth_path([(128, -336), (176, -320), (200, -200), (204, -60), (190, 20), (150, 22), (150, -80), (138, -220)])
        rarm.transform(m)
        rhand_c = m.mapXY(176, 46)
        # left arm (screen left) holds the book pressed to her side
        la_rot = 4 * lift
        ml = skia.Matrix()
        ml.setRotate(la_rot, -150, -320)
        larm = smooth_path([(-128, -336), (-178, -320), (-214, -210), (-224, -110), (-196, -40), (-160, -60), (-160, -180), (-140, -260)])
        larm.transform(ml)
        book = poly([(-236, -250), (-170, -262), (-160, -50), (-226, -40)])
        mb = skia.Matrix()
        mb.setTranslate(90 * lift, -40 * lift)
        book.transform(mb)
        book_a = 1 - clamp(lift * 1.6)
        head_y = -470 + 12 * head_down
        head = skia.Path().addOval(R(-64, head_y, 64, head_y + 132))
        # braid: chain of lobes swaying
        braid_pts = []
        for k in range(10):
            u = k / 9
            bx = 6 * math.sin(t * 1.1 + u * 2.2) * (0.3 + u) + 5 * walk * math.sin(ph - u * 2) * u
            braid_pts.append((bx, head_y + 120 + u * 330))
        # rim silhouette
        union = skia.Path(robe)
        for pth in (hood, rarm, larm, head) + ((book,) if book_a > 0.5 else ()):
            union = skia.Op(union, pth, skia.PathOp.kUnion_PathOp)
        fx = (rim_from[0] - x) / s
        fy = (rim_from[1] - y) / s
        bloom = paint(rgb(*light, int(22 * rim)))
        bloom.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18))
        c.drawPath(union, bloom)
        c.saveLayer()
        if book_a > 0:
            c.drawPath(book, paint(rgb(70, 40, 27, int(255 * book_a))))
        c.drawPath(larm, paint(C(WOOL2)))
        c.drawPath(robe, paint(C(WOOL)))
        # wool folds
        for k, xx in enumerate((-110, -40, 30, 100)):
            c.drawPath(smooth_path([(xx - 8, -40), (xx + 6, 200), (xx - 4, 460), (xx + 16, 460), (xx + 20, 200), (xx + 8, -40)]), paint(C(WOOL_DK, 150)))
        # rust marks: shoulder band, sign between the shoulder blades, hem stripes
        band = skia.Path()
        band.moveTo(-150, -318); band.quadTo(0, -282, 150, -318)
        c.drawPath(band, paint(C(RUST, 220), stroke=12))
        c.drawPath(band, paint(C((120, 48, 34), 220), stroke=3))
        c.drawCircle(0, -205, 38, paint(C(RUST, 210), stroke=7))
        c.drawCircle(0, -205, 9, paint(C(RUST, 230)))
        for k in range(3):
            c.drawLine(-46, -140 + k * 14, 46, -140 + k * 14, paint(C(RUST, 190), stroke=5))
        for k in range(7):
            xx = -170 + k * 56
            c.drawLine(xx, 320, xx + 10, 460, paint(C(RUST, 160), stroke=8))
        c.drawPath(hood, paint(C(WOOL2)))
        c.drawPath(rarm, paint(C(WOOL2)))
        # hands
        rh = (rhand_c.x(), rhand_c.y())
        ha = 1.0
        if ha > 0:
            c.drawOval(R(rh[0] - 22, rh[1] - 30, rh[0] + 22, rh[1] + 30), paint(C(SKIN, int(255 * ha))))
            c.drawLine(rh[0] - 12, rh[1] - 4, rh[0] + 12, rh[1] - 4, paint(C(LINES, int(220 * ha)), stroke=3))
            for k in range(3):
                c.drawLine(rh[0] - 24, rh[1] - 36 - k * 7, rh[0] + 24, rh[1] - 36 - k * 7, paint(C(COPPER, int(255 * ha)), stroke=4))
        # neck + head + braid
        c.drawRect(R(-26, head_y + 108, 26, head_y + 150), paint(C(SKIN_DK)))
        c.drawPath(head, paint(C(HAIR)))
        c.drawLine(0, head_y + 4, 0, head_y + 60, paint(C(HAIR_LT, 160), stroke=3))
        for k in range(len(braid_pts) - 1):
            (bx0, by0), (bx1, by1) = braid_pts[k], braid_pts[k + 1]
            wdt = lerp(30, 16, k / 9)
            for side in (-1, 1):
                c.drawOval(R(bx0 - wdt + side * 6, by0 - 4, bx0 + wdt * 0.2 + side * 6, by1 + 6), paint(C(HAIR)))
            c.drawLine(bx0 - wdt * 0.6, by0 + 6, bx1 + wdt * 0.6, by1 - 6, paint(C(HAIR_LT, 120), stroke=2.5))
            if k in (3, 6):
                c.drawLine(bx0 - wdt, by0, bx0 + wdt, by0, paint(C(COPPER), stroke=6))
        bx, by = braid_pts[-1]
        c.drawPath(poly([(bx - 12, by), (bx + 12, by), (bx + 4, by + 40), (bx - 6, by + 44)]), paint(C(HAIR)))
        # rim light on the outline toward the light source
        rp = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kSrcATop, Style=skia.Paint.kStroke_Style, StrokeWidth=10)
        dist = max(400.0, math.hypot(fx, fy + 150))
        rp.setShader(skia.GradientShader.MakeRadial(P(fx, fy), dist * 1.05, [rgb(*light, int(240 * rim)), rgb(*light, int(110 * rim)), rgb(*light, 0)], [0, 0.72, 1]))
        rp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 2.5))
        c.drawPath(union, rp)
        wash = skia.Paint(BlendMode=skia.BlendMode.kSrcATop, Shader=skia.GradientShader.MakeRadial(P(fx, fy), dist * 1.1, [rgb(*light, int(44 * rim)), rgb(*light, int(14 * rim)), rgb(*light, 0)], [0, 0.75, 1]))
        c.drawRect(R(-400, -700, 400, 600), wash)
        c.restore()


# ------------------------------------------------------------------ hatchling (from the Short)
def hatchling(c, x, y, s, flip=False, wing=0.0, accent=GLUT, rot=0, a=255):
    c.drawCircle(x, y - 10 * s, 95 * s, blur_paint(C(accent, int(70 * a / 255)), 30 * s))
    with saved(c):
        c.translate(x, y); c.rotate(rot); c.scale(-s if flip else s, s)
        body = rgb(84, 64, 60, a)
        w_up = -60 - 50 * wing
        c.drawPath(poly([(-6, -8), (-40, w_up + 6), (-4, w_up - 20), (30, -14)]), paint(rgb(70, 52, 50, a)))
        c.drawPath(smooth_path([(-30, 4), (-70, 18), (-100, 6), (-116, -8), (-96, 14), (-66, 30), (-26, 18)]), paint(body))
        c.drawPath(poly([(-116, -8), (-128, -20), (-120, 2)]), paint(C(accent, a)))
        c.drawOval(R(-40, -24, 34, 26), paint(body))
        c.drawOval(R(-20, 0, 26, 24), paint(C(accent, int(200 * a / 255))))
        c.drawPath(smooth_path([(16, -10), (36, -38), (52, -52), (66, -50), (60, -34), (40, -12), (28, 8)]), paint(body))
        c.drawPath(smooth_path([(50, -60), (78, -62), (96, -52), (92, -42), (68, -40), (52, -44)]), paint(body))
        c.drawPath(poly([(54, -58), (44, -76), (62, -62)]), paint(C(accent, a)))
        c.drawCircle(70, -53, 4.5, paint(rgb(255, 214, 120, a)))
        c.drawLine(-14, 20, -18, 40, paint(body, stroke=8)); c.drawLine(14, 20, 16, 40, paint(body, stroke=8))
        tip = (-10 - 20 * wing, w_up - 10)
        c.drawPath(poly([(0, -12), tip, (-50, w_up + 40), (-60, -6)]), paint(rgb(88, 62, 58, a)))
        c.drawLine(0, -12, *tip, paint(body, stroke=5))
        c.drawLine(*tip, -50, w_up + 40, paint(body, stroke=3))


# ------------------------------------------------------------------ dissolve mask (for the plate forming out of smoke)
class Dissolve:
    def __init__(self, w, h, seed=4):
        n = 0.6 * value_noise(w, h, max(3, w // 60), max(3, h // 60), seed) + 0.4 * value_noise(w, h, max(3, w // 14), max(3, h // 14), seed + 1)
        self.n = (n - n.min()) / (n.max() - n.min())
        self.w, self.h = w, h

    def apply(self, img_arr, u, soft=0.12):
        """img_arr RGBA uint8 -> alpha * mask(u)"""
        m = np.clip((u * (1 + soft) - self.n) / soft, 0, 1)
        out = img_arr.copy()
        out[..., 3] = (out[..., 3].astype(np.float32) * m).astype(np.uint8)
        return out
