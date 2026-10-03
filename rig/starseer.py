"""The Starseer - a rigged 2D cut-out character drawn with Skia.
All coordinates are character-local, origin = hip joint on the seat, y down.
"""
import math
import skia

def rgb(r, g, b, a=255):
    return skia.ColorSetARGB(a, r, g, b)

def paint(col, aa=True, stroke=None, cap=None):
    p = skia.Paint(AntiAlias=aa, Color=col)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap is None else cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    return p

def smooth_path(pts, closed=True):
    """Catmull-Rom through points -> cubic path"""
    path = skia.Path()
    n = len(pts)
    if n < 2:
        return path
    path.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        path.cubicTo(*c1, *c2, *p2)
    if closed:
        path.close()
    return path

# palette
ROBE = rgb(58, 66, 86)
ROBE_DK = rgb(40, 45, 60)
ROBE_LT = rgb(78, 88, 112)
TRIM = rgb(222, 212, 190)
GOLD = rgb(216, 179, 92)
SKIN = rgb(214, 172, 136)
SKIN_DK = rgb(186, 142, 108)
HAIR = rgb(236, 230, 218)
HAIR_DK = rgb(198, 192, 182)
INK = rgb(34, 30, 30)
PARCH = rgb(226, 206, 166)
BOOT = rgb(44, 34, 30)

class Pose:
    """all animatable parameters with rest defaults"""
    def __init__(self, **kw):
        self.lean = 0.0          # torso rotation (deg, + = forward/clockwise)
        self.breath = 0.0        # 0..1
        self.head = 12.0         # head rotation (deg, + = looking down)
        self.brow_y = 0.0        # + = raised
        self.brow_ang = 0.0      # + = inner end up (worried/surprised), - = frown
        self.brow2 = 0.0         # extra raise of the (single visible) brow for 'knowing'
        self.eye_s = 1.0         # eye scale
        self.blink = 0.0         # 0 open .. 1 closed
        self.look = 0.0          # pupil offset along view dir (-1 back .. 1 forward)
        self.mouth = 0.0         # 0 closed .. 1 open
        self.smile = 0.0         # -1 frown .. 1 smile
        self.ua = 78.0           # near upper arm angle (deg from +x, screen coords)
        self.fa = -52.0          # near forearm angle relative to upper arm
        self.hand = 0.0          # 0 relaxed fist, 1 pointing, 2 open palm
        self.wrist = 0.0         # hand rotation relative to forearm
        self.far_ua = 84.0
        self.far_fa = -74.0
        self.scroll = 1.0        # 1 = held up reading, 0 = lowered on lap
        self.wind = 0.0          # time for wind motion
        self.hair_sway = 0.0
        for k, v in kw.items():
            setattr(self, k, v)

class Starseer:
    NECK = (16, -250)
    SH_NEAR = (26, -212)
    SH_FAR = (-4, -214)

    def draw(self, c, p, x, y, scale=1.0):
        c.save()
        c.translate(x, y)
        c.scale(scale, scale)
        self._cloak(c, p)
        self._far_arm(c, p)
        self._lap(c, p)
        c.save()
        c.rotate(p.lean)
        self._torso(c, p)
        self._head(c, p)
        self._near_arm(c, p)
        c.restore()
        c.restore()

    # ---------------------------------------------------------------- parts
    def _cloak(self, c, p):
        w = p.wind
        def wv(y, amp=1.0, ph=0.0):
            return math.sin(w * 2.2 + y * 0.025 + ph) * 7 * amp + math.sin(w * 3.7 + y * 0.05) * 3 * amp
        pts = [(-36, -232), (-86, -190), (-124, -110), (-146 + wv(0), -10), (-162 + wv(60, 1.3), 70),
               (-170 + wv(110, 1.6, 1), 120), (-130 + wv(115, 1.5, 2), 128), (-96 + wv(118, 1.2, 3), 116),
               (-62, 108), (-40, -60)]
        c.save()
        c.rotate(p.lean * 0.5)
        c.drawPath(smooth_path(pts), paint(ROBE_DK))
        c.restore()

    def _lap(self, c, p):
        # robe draped over thighs, boots
        c.drawPath(smooth_path([(128, 142), (160, 138), (212, 146), (220, 164), (196, 168), (132, 166)]), paint(BOOT))
        pts = [(-72, 6), (-40, -34), (40, -40), (150, -34), (190, -14), (200, 40), (196, 110), (192, 146),
               (150, 150), (110, 148), (104, 90), (80, 40), (-30, 44), (-70, 40)]
        c.drawPath(smooth_path(pts), paint(ROBE))
        c.drawPath(smooth_path([(40, -40), (150, -34), (188, -16), (150, -26), (60, -28)]), paint(ROBE_LT))
        c.drawPath(smooth_path([(192, 146), (150, 150), (110, 148), (112, 140), (150, 142), (190, 138)]), paint(TRIM))

    def _torso(self, c, p):
        b = 1.0 + 0.018 * p.breath
        c.save()
        c.scale(1.0, b)
        pts = [(-70, 26), (-86, -60), (-76, -160), (-42, -226), (6, -252), (48, -230), (66, -178),
               (74, -110), (70, -30), (60, 30)]
        c.drawPath(smooth_path(pts), paint(ROBE))
        # front trim + belt + star emblem
        c.drawPath(smooth_path([(40, -234), (52, -150), (56, -60), (50, 20), (36, 22), (42, -60), (38, -150), (28, -232)]), paint(TRIM))
        c.drawPath(smooth_path([(-80, -96), (0, -88), (72, -98), (72, -80), (0, -70), (-80, -78)]), paint(ROBE_DK))
        star = skia.Path()
        cx, cy, r1, r2 = -6, -168, 20, 8
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = r1 if k % 2 == 0 else r2
            (star.moveTo if k == 0 else star.lineTo)(cx + math.cos(a) * r, cy + math.sin(a) * r)
        star.close()
        c.drawPath(star, paint(GOLD))
        # hood bunched behind the neck
        c.drawPath(smooth_path([(-52, -214), (-40, -262), (0, -276), (30, -262), (22, -238), (-14, -236)]), paint(ROBE_DK))
        c.restore()

    def _head(self, c, p):
        c.save()
        nx, ny = self.NECK
        c.translate(nx, ny)
        c.rotate(p.head)
        # neck
        c.drawPath(smooth_path([(-14, 8), (-12, -30), (20, -34), (22, 6)]), paint(SKIN_DK))
        # back hair tufts (sway)
        sw = p.hair_sway
        c.drawPath(smooth_path([(-40, -62), (-66 + sw, -58), (-78 + sw * 1.4, -34), (-60 + sw, -26), (-70 + sw * 1.2, -8), (-40, -14)]), paint(HAIR_DK))
        # skull
        c.drawOval(skia.Rect(-60, -130, 60, -14), paint(SKIN))
        # side hair tuft wrapping behind the ear
        c.drawPath(smooth_path([(-58, -84), (-44, -94), (-30, -86), (-34, -56), (-50, -40), (-62, -56)]), paint(HAIR))
        # ear
        c.drawPath(smooth_path([(-22, -84), (-8, -86), (-4, -70), (-10, -58), (-22, -60)]), paint(SKIN_DK))
        c.drawPath(smooth_path([(-16, -78), (-9, -76), (-10, -66)], closed=False), paint(rgb(160, 118, 90), stroke=3))
        # nose
        c.drawPath(smooth_path([(38, -96), (58, -76), (88, -52), (84, -44), (62, -46), (46, -58)]), paint(SKIN))
        c.drawPath(smooth_path([(62, -48), (70, -46), (68, -52)], closed=False), paint(SKIN_DK, stroke=3))
        # mouth (under moustache)
        mo = max(0.0, min(1.0, p.mouth))
        mh = 2 + 13 * mo
        c.drawOval(skia.Rect(40, -44 - 2, 66, -44 + mh), paint(rgb(70, 30, 30)))
        # beard (drops with jaw)
        jaw = 7 * mo
        beard = [(18, -52), (46, -40 + jaw * 0.3), (70, -34 + jaw), (74, 4 + jaw), (58, 52 + jaw), (34 + sw * 0.5, 96 + jaw),
                 (18 + sw * 0.3, 70 + jaw), (-2, 28 + jaw * 0.6), (-8, -18)]
        c.drawPath(smooth_path(beard), paint(HAIR))
        c.drawPath(smooth_path([(30, 10 + jaw), (48, 40 + jaw), (36, 74 + jaw), (26, 44 + jaw)]), paint(HAIR_DK))
        # moustache (smile curls the ends)
        sm = p.smile
        c.drawPath(smooth_path([(38, -52), (62, -54), (84, -44 - 6 * sm), (78, -36 - 4 * sm), (58, -42), (40, -40)]), paint(HAIR))
        # eye
        ex, ey = 34, -80
        es = p.eye_s
        c.drawOval(skia.Rect(ex - 9 * es, ey - 9 * es, ex + 9 * es, ey + 9 * es), paint(rgb(246, 240, 228)))
        px = ex + 3 * p.look
        c.drawCircle(px, ey, 5.2 * es, paint(INK))
        if p.blink > 0.01:
            lid = skia.Rect(ex - 11 * es, ey - 11 * es, ex + 11 * es, ey - 11 * es + 22 * es * min(p.blink, 1))
            c.drawRect(lid, paint(SKIN))
            c.drawLine(ex - 10 * es, ey - 11 * es + 22 * es * min(p.blink, 1), ex + 10 * es, ey - 11 * es + 22 * es * min(p.blink, 1), paint(SKIN_DK, stroke=2))
        # brow
        by = ey - 20 - 9 * p.brow_y - 6 * p.brow2
        a = math.radians(-p.brow_ang * 12 + 4)
        bx0, bx1 = ex - 18, ex + 14
        c.drawLine(bx0, by + math.sin(a) * 16, bx1, by - math.sin(a) * 16, paint(HAIR, stroke=10))
        c.restore()

    def _hand(self, c, p, kind):
        if kind < 0.5:           # relaxed fist
            c.drawPath(smooth_path([(-4, -14), (18, -16), (28, -2), (22, 14), (0, 14), (-8, 0)]), paint(SKIN))
        elif kind < 1.5:         # pointing
            c.drawPath(smooth_path([(-4, -14), (16, -14), (24, -8), (22, 12), (0, 14), (-8, 0)]), paint(SKIN))
            c.drawPath(smooth_path([(14, -12), (52, -12), (56, -7), (52, -3), (16, -2)]), paint(SKIN))
            c.drawPath(smooth_path([(4, -16), (14, -26), (20, -22), (12, -12)]), paint(SKIN_DK))
        else:                    # open palm, fingers spread up
            c.drawPath(smooth_path([(-4, -12), (26, -16), (34, 0), (26, 14), (0, 14), (-8, 0)]), paint(SKIN))
            for k, (dx, dy, ln) in enumerate(((24, -10, 26), (28, -2, 28), (26, 6, 24))):
                a = math.radians(-35 + k * 22)
                c.drawLine(dx, dy, dx + math.cos(a) * ln, dy + math.sin(a) * ln, paint(SKIN, stroke=9))
            c.drawLine(6, -12, 16, -30, paint(SKIN_DK, stroke=9))

    def _arm(self, c, p, sh, ua, fa, hand, col, col_cuff, far=False):
        c.save()
        c.translate(*sh)
        c.rotate(ua)
        L1, L2 = 108, 92
        # upper sleeve
        c.drawPath(smooth_path([(-8, -24), (L1, -20), (L1 + 6, 20), (-8, 26)]), paint(col))
        c.translate(L1, 0)
        c.rotate(fa)
        # hand first (sleeve overlaps wrist)
        c.save()
        c.translate(L2 + 4, 0)
        c.rotate(p.wrist)
        self._hand(c, p, hand)
        c.restore()
        # bell sleeve
        c.drawPath(smooth_path([(-18, -22), (L2 - 10, -26), (L2 + 6, -34), (L2 + 10, 30), (L2 - 12, 24), (-18, 22)]), paint(col))
        c.drawPath(smooth_path([(L2 - 4, -34), (L2 + 8, -35), (L2 + 14, 31), (L2 + 2, 30)]), paint(col_cuff))
        c.restore()

    def _near_arm(self, c, p):
        self._arm(c, p, self.SH_NEAR, p.ua, p.fa, p.hand, ROBE_LT, TRIM)

    def _far_arm(self, c, p):
        # far arm + scroll, drawn behind torso
        c.save()
        c.rotate(p.lean)
        c.translate(*self.SH_FAR)
        c.rotate(p.far_ua)
        c.drawPath(smooth_path([(-8, -22), (104, -18), (108, 18), (-8, 22)]), paint(ROBE_DK))
        c.translate(104, 0)
        c.rotate(p.far_fa)
        c.drawPath(smooth_path([(-16, -20), (86, -24), (94, 26), (-16, 20)]), paint(ROBE_DK))
        c.save()
        c.translate(94, 0)
        # scroll in hand
        c.rotate(-p.far_ua - p.far_fa - p.lean + lerp(8, -20, p.scroll))
        c.drawRect(skia.Rect(-6, -46, 70, 30), paint(PARCH))
        for k in range(5):
            c.drawLine(4, -34 + k * 12, 58 - (k % 2) * 16, -34 + k * 12, paint(rgb(150, 120, 90), stroke=3))
        c.drawRoundRect(skia.Rect(-12, -52, 2, 36), 6, 6, paint(rgb(196, 170, 128)))
        c.drawRoundRect(skia.Rect(64, -52, 78, 36), 6, 6, paint(rgb(196, 170, 128)))
        c.drawPath(smooth_path([(-8, -10), (14, -12), (18, 6), (-4, 10)]), paint(SKIN_DK))
        c.restore()
        c.restore()

def lerp(a, b, u):
    return a + (b - a) * u
