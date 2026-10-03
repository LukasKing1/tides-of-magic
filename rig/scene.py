"""Character test: the Starseer at the campfire sees the comet and speaks one line.
python3 scene.py preview 1,3.6,5.6,8.6,12.3,15   |   python3 scene.py full
"""
import math, sys, os, subprocess, random
import numpy as np
import skia
from starseer import Starseer, Pose, smooth_path, paint, rgb

W, H, FPS = 1920, 1080, 30
DUR = 16.5
T_VO = 7.9
MOUTH = np.load('/home/claude/rig/mouth.npy')

def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def ramp(t, a, b):
    return smooth((t - a) / (b - a)) if b > a else float(t >= a)

def K(keys):
    """keyframe channel with ease-in-out between keys"""
    def f(t):
        if t <= keys[0][0]:
            return keys[0][1]
        for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
            if t <= t1:
                return v0 + (v1 - v0) * ease((t - t0) / (t1 - t0))
        return keys[-1][1]
    return f

CH = dict(
    head=K([(0, 20), (3.0, 20), (3.5, -27), (3.9, -22), (7.2, -22), (7.9, -4), (9.15, -4), (9.4, 4), (9.75, -4), (12.7, -4), (13.4, -18), (16.5, -18)]),
    brow_y=K([(0, -0.3), (3.1, -0.3), (3.4, 1.05), (5.5, 0.8), (7.4, 0.8), (7.9, 0.15), (12.6, 0.15), (13.4, 0.5), (16.5, 0.5)]),
    brow_ang=K([(0, -0.45), (3.1, -0.45), (3.4, 0.6), (7.2, 0.5), (7.9, 0.0), (16.5, 0.0)]),
    brow2=K([(0, 0), (7.6, 0), (8.0, 1.0), (9.0, 1.0), (9.4, 0.3), (11.6, 0.3), (12.0, 0.9), (12.8, 0.9), (13.4, 0), (16.5, 0)]),
    eye_s=K([(0, 1.0), (3.2, 1.0), (3.4, 1.3), (6.8, 1.2), (7.8, 1.0), (16.5, 1.0)]),
    smile=K([(0, 0), (11.5, 0), (12.2, 0.9), (13.2, 0.7), (16.5, 0.5)]),
    look=K([(0, 0.4), (3.2, 0.4), (3.4, 1.0), (7.4, 1.0), (7.9, 0.5), (16.5, 0.6)]),
    lean=K([(0, 7), (3.0, 7), (3.45, -4), (4.3, -2), (5.0, 6), (7.2, 5), (7.9, 2), (12.6, 2), (13.4, 0), (16.5, 0)]),
    ua=K([(0, 68), (4.2, 68), (4.95, -42), (5.08, -45), (5.35, -38), (7.2, -38), (7.85, 22), (11.7, 22), (12.3, 48), (13.0, 60), (16.5, 62)]),
    fa=K([(0, -44), (4.2, -44), (4.55, -74), (5.0, 8), (5.3, 2), (7.2, 2), (7.85, -86), (11.7, -86), (12.3, -60), (13.0, -50), (16.5, -48)]),
    wrist=K([(0, 0), (4.9, 0), (5.0, -8), (7.2, -8), (7.85, -26), (11.7, -26), (12.3, 10), (16.5, 0)]),
    far_ua=K([(0, 66), (3.3, 66), (3.9, 86), (16.5, 86)]),
    far_fa=K([(0, -84), (3.3, -84), (3.9, -70), (16.5, -70)]),
    scroll=K([(0, 1.0), (3.3, 1.0), (3.9, 0.0), (16.5, 0.0)]),
)
BLINKS = [1.3, 4.05, 4.4, 8.35, 10.9, 13.9, 15.6]

def pose_at(t):
    p = Pose()
    for k, f in CH.items():
        setattr(p, k, f(t))
    # drag / overlapping action: forearm and wrist lag behind their parents
    p.fa += 0.35 * (CH['ua'](t - 0.09) - CH['ua'](t))
    p.wrist += 0.4 * (CH['fa'](t - 0.08) - CH['fa'](t))
    # tremble while holding the point
    if 5.3 < t < 7.2:
        p.ua += 0.7 * math.sin(t * 13) + 0.4 * math.sin(t * 29)
    p.hand = 1 if 4.72 <= t < 7.55 else (2 if 7.55 <= t < 12.25 else 0)
    p.blink = max([max(0.0, 1 - abs(t - b) / 0.08) for b in BLINKS] + [0.0])
    i = int((t - T_VO) * FPS)
    p.mouth = float(MOUTH[i]) if 0 <= i < len(MOUTH) else 0.0
    p.breath = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 3.6)
    p.wind = t
    p.hair_sway = 3 * math.sin(t * 1.7) + 2 * math.sin(t * 3.1 + 1)
    return p

# ---------------------------------------------------------------- scene elements
rnd = random.Random(7)
STARS = [(rnd.uniform(0, W), rnd.uniform(0, 620), rnd.uniform(0.8, 2.2), rnd.uniform(0, 6.28)) for _ in range(190)]
EMBERS = [dict(x0=rnd.uniform(-30, 30), t0=rnd.uniform(0, 3.0), sp=rnd.uniform(70, 130), dr=rnd.uniform(-25, 25),
               r=rnd.uniform(1.6, 3.4), life=rnd.uniform(1.6, 3.0)) for _ in range(40)]
FIRE = (470, 905)
HIP = (800, 790)
CS = 1.32
COMET = (1530, 250)

def mountains(c):
    far = [(0, 700), (140, 640), (300, 672), (470, 600), (640, 660), (820, 618), (1010, 676), (1210, 590), (1400, 650), (1600, 606), (1800, 660), (1920, 630), (1920, 800), (0, 800)]
    c.drawPath(smooth_path(far), paint(rgb(38, 42, 56)))
    near = [(0, 780), (200, 740), (420, 770), (700, 730), (980, 772), (1250, 736), (1520, 770), (1760, 742), (1920, 760), (1920, 900), (0, 900)]
    c.drawPath(smooth_path(near), paint(rgb(28, 31, 40)))

def sky(c, t):
    p = skia.Paint(Shader=skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, 760)], [rgb(11, 14, 24), rgb(44, 40, 58)]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    for (x, y, r, ph) in STARS:
        a = int(150 + 90 * math.sin(t * 1.3 + ph))
        c.drawCircle(x, y, r, paint(rgb(230, 223, 208, a)))

def comet(c, t):
    a = ramp(t, 2.0, 3.3)
    if a <= 0:
        return
    hx, hy = COMET
    tx, ty = 1110, 70
    glow = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(skia.Point(hx, hy), 170, [rgb(255, 120, 60, int(120 * a)), rgb(255, 80, 40, 0)]))
    c.drawCircle(hx, hy, 170, glow)
    # tail
    for k, (wd, col, al) in enumerate(((46, (200, 70, 50), 0.55), (26, (240, 150, 70), 0.75), (10, (255, 225, 170), 0.95))):
        ang = math.atan2(ty - hy, tx - hx)
        nx, ny = -math.sin(ang), math.cos(ang)
        sh = 6 * math.sin(t * 2 + k)
        pts = [(hx + nx * wd * 0.5, hy + ny * wd * 0.5), (tx + nx * (wd * 2.2 + sh), ty + ny * (wd * 2.2 + sh)),
               (tx - nx * (wd * 0.6), ty - ny * (wd * 0.6)), (hx - nx * wd * 0.5, hy - ny * wd * 0.5)]
        path = skia.Path()
        path.moveTo(*pts[0]); path.lineTo(*pts[1]); path.lineTo(*pts[2]); path.lineTo(*pts[3]); path.close()
        sh_ = skia.GradientShader.MakeLinear([skia.Point(hx, hy), skia.Point(tx, ty)], [rgb(*col, int(255 * al * a)), rgb(*col, 0)])
        pp = skia.Paint(AntiAlias=True, Shader=sh_)
        pp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6 + 4 * (2 - k)))
        c.drawPath(path, pp)
    core = paint(rgb(255, 238, 205, int(255 * a)))
    core.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
    c.drawCircle(hx, hy, 11, core)

def rock_and_props(c):
    c.save()
    c.translate(*HIP)
    c.scale(CS, CS)
    c.translate(-830, -752)
    rock = [(690, 770), (760, 742), (900, 744), (980, 770), (1000, 860), (960, 920), (720, 924), (672, 860)]
    c.drawPath(smooth_path(rock), paint(rgb(66, 70, 80)))
    c.drawPath(smooth_path([(700, 772), (770, 750), (900, 752), (970, 774), (900, 766), (770, 764)]), paint(rgb(88, 92, 102)))
    # telescope leaning on the rock
    c.save()
    c.translate(1060, 925)
    c.rotate(-58)
    c.drawRoundRect(skia.Rect(0, -13, 250, 13), 6, 6, paint(rgb(196, 160, 84)))
    c.drawRoundRect(skia.Rect(160, -17, 250, 17), 6, 6, paint(rgb(216, 179, 92)))
    for x in (60, 158, 246):
        c.drawRect(skia.Rect(x, -18, x + 8, 18), paint(rgb(120, 92, 50)))
    c.drawOval(skia.Rect(244, -17, 258, 17), paint(rgb(40, 50, 70)))
    c.restore()
    c.restore()

def campfire(c, t):
    fx, fy = FIRE
    c.save(); c.translate(fx, fy); c.scale(1.15, 1.15); c.translate(-fx, -fy)
    # ground glow (additive)
    fl = 1 + 0.08 * math.sin(t * 9.3) + 0.05 * math.sin(t * 15.1 + 1) + 0.04 * math.sin(t * 4.1)
    g = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kPlus,
                   Shader=skia.GradientShader.MakeRadial(skia.Point(fx, fy - 20), 520 * fl, [rgb(120, 52, 16, 150), rgb(60, 24, 8, 60), rgb(0, 0, 0, 0)], [0.0, 0.45, 1.0]))
    c.drawCircle(fx, fy - 20, 520 * fl, g)
    # stones + logs
    for k in range(7):
        a = math.pi * (0.05 + 0.9 * k / 6)
        c.drawOval(skia.Rect(fx + math.cos(a) * 92 - 26, fy + 18 - 14, fx + math.cos(a) * 92 + 26, fy + 18 + 16), paint(rgb(58, 60, 66)))
    for ang in (-18, 16):
        c.save(); c.translate(fx, fy + 8); c.rotate(ang)
        c.drawRoundRect(skia.Rect(-90, -12, 90, 12), 10, 10, paint(rgb(70, 46, 32)))
        c.restore()
    # flames
    for k, (col, sc) in enumerate(((rgb(196, 83, 46), 1.0), (rgb(238, 150, 64), 0.72), (rgb(252, 222, 160), 0.42))):
        for j in range(3):
            ox = (j - 1) * 34 * sc
            h = (150 + 30 * math.sin(t * 7 + j * 2 + k)) * sc * (1.0 if j == 1 else 0.72)
            wdt = 46 * sc
            sway = 14 * math.sin(t * 5.3 + j * 1.7 + k) * sc
            pts = [(fx + ox - wdt, fy), (fx + ox - wdt * 0.6 + sway * 0.3, fy - h * 0.45), (fx + ox + sway, fy - h),
                   (fx + ox + wdt * 0.6 + sway * 0.3, fy - h * 0.5), (fx + ox + wdt, fy)]
            c.drawPath(smooth_path(pts), paint(col))
    # embers
    for e in EMBERS:
        age = (t - e['t0']) % e['life']
        u = age / e['life']
        x = fx + e['x0'] + e['dr'] * u + 10 * math.sin(t * 3 + e['t0'] * 5)
        y = fy - 60 - e['sp'] * age * 1.6
        al = int(255 * (1 - u) * (0.6 + 0.4 * math.sin(t * 11 + e['t0'] * 9)))
        if al > 0:
            pp = paint(rgb(255, 170, 70, max(al, 0)))
            c.drawCircle(x, y, e['r'], pp)
    c.restore()

def foreground(c):
    for (x, s) in ((70, 1.0), (140, 0.8), (1780, 1.1), (1850, 0.9)):
        for k in range(6):
            a = -90 + (k - 2.5) * 12
            ln = (90 + 30 * (k % 3)) * s
            c.drawLine(x + k * 8, 1080, x + k * 8 + math.cos(math.radians(a)) * ln, 1080 + math.sin(math.radians(a)) * ln, paint(rgb(18, 18, 20), stroke=7 * s))

STAR = Starseer()

def render(t):
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    z = 1.0 + 0.07 * smooth(t / DUR) + 0.03 * ease((t - 3.3) / 0.5)
    cx, cy = 940 - 40 * smooth(t / DUR), 560 - 40 * smooth(t / DUR)
    def cam(depth):
        zz = 1 + (z - 1) * depth
        c.translate(W / 2, H / 2)
        c.scale(zz, zz)
        c.translate(-(W / 2 + (cx - W / 2) * depth), -(H / 2 + (cy - H / 2) * depth))
    c.save(); cam(0.25); sky(c, t); comet(c, t); c.restore()
    c.save(); cam(0.55); mountains(c); c.restore()
    c.save(); cam(1.0)
    c.drawRect(skia.Rect(-200, 780, W + 200, H + 200), paint(rgb(22, 22, 26)))
    c.drawOval(skia.Rect(560, 955, 1150, 1015), paint(rgb(10, 10, 12, 150)))
    rock_and_props(c)
    # character on its own layer so light only hits him
    c.saveLayer()
    STAR.draw(c, pose_at(t), *HIP, CS)
    fl = 1 + 0.1 * math.sin(t * 9.3) + 0.06 * math.sin(t * 15.1 + 1)
    fire_light = skia.Paint(BlendMode=skia.BlendMode.kSrcATop,
                            Shader=skia.GradientShader.MakeRadial(skia.Point(FIRE[0] - 40, FIRE[1] - 60), 560, [rgb(255, 150, 70, int(95 * fl)), rgb(255, 130, 60, int(30 * fl)), rgb(255, 120, 40, 0)], [0.0, 0.55, 1.0]))
    c.drawRect(skia.Rect(0, 0, W, H), fire_light)
    ca = ramp(t, 2.3, 3.6)
    if ca > 0:
        cl = skia.Paint(BlendMode=skia.BlendMode.kSrcATop,
                        Shader=skia.GradientShader.MakeRadial(skia.Point(*COMET), 900, [rgb(255, 120, 80, int(42 * ca)), rgb(255, 110, 70, 0)]))
        c.drawRect(skia.Rect(0, 0, W, H), cl)
    c.restore()
    campfire(c, t)
    c.restore()
    c.save(); cam(1.35); foreground(c); c.restore()
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3].astype(np.float32)
    return arr

# grain + vignette + fades
_r = np.random.default_rng(3)
GRAIN = [_r.normal(0, 4.5, (H, W, 1)).astype(np.float32) for _ in range(6)]
YY, XX = np.mgrid[0:H, 0:W]
VIGN = (1 - 0.3 * np.clip(np.sqrt(((XX - W / 2) / (W * 0.7)) ** 2 + ((YY - H / 2) / (H * 0.75)) ** 2) - 0.3, 0, 1) ** 1.4)[..., None].astype(np.float32)

def frame(t):
    a = render(t) * VIGN + GRAIN[int(t * FPS) % 6]
    a *= ramp(t, 0.0, 1.0) * (1 - ramp(t, DUR - 1.2, DUR))
    return np.clip(a, 0, 255).astype(np.uint8)

if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        from PIL import Image
        os.makedirs('prev', exist_ok=True)
        for ts in sys.argv[2].split(','):
            Image.fromarray(frame(float(ts))).save(f'prev/p_{float(ts):05.2f}.png')
        print('ok')
    else:
        cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
               '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', 'video_only.mp4']
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait(); print('done')
