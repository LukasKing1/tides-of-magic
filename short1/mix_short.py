"""Audio for Short 1: voice (Marie as Doreah), Shadowfall with the drop on 'It was the world',
campfire as a seamless loop, simple placeholder SFX until the real ones arrive.  -> mix.wav (48 kHz stereo, T_TOTAL s)"""
import json, re, subprocess
import numpy as np

SR = 48000
T = 53.0
N = int(T * SR)
D = '/home/claude/short1/'
A = D + 'audio/'
rng = np.random.default_rng(7)


def decode(path, ch=2, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    return x.reshape(-1, ch).copy()


def lufs_of(path, af=None):
    cmd = ['ffmpeg', '-v', 'info', '-i', path, '-af', (af + ',' if af else '') + 'ebur128', '-f', 'null', '-']
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[\d.]+) LUFS', err)
    return float(m[-1])


def env_db(points, n=N):
    t = np.arange(n) / SR
    ts, ds = zip(*points)
    return 10 ** (np.interp(t, ts, ds) / 20)


def place(buf, x, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    i1 = min(N, i0 + len(x))
    if i1 > i0 >= 0:
        buf[i0:i1] += x[:i1 - i0] * gain
    return buf


mix = np.zeros((N, 2), np.float32)

# ------------------------------------------------------------------ voice
OFFS = {1: 0.15, 2: 8.50, 3: 26.30, 4: 33.40, 5: 42.00}
VOICE_AF = 'highpass=f=75,lowpass=f=12000,aecho=1.0:0.92:38|74:0.10|0.06'
voice = np.zeros((N, 2), np.float32)
for i, t0 in OFFS.items():
    f = A + f'S-{i}.mp3'
    L = lufs_of(f, VOICE_AF)
    x = decode(f, 2, VOICE_AF)
    place(voice, x, t0, 10 ** ((-16.0 - L) / 20))

# ------------------------------------------------------------------ music: Shadowfall, drop at 45.09
TRACK_START = 46.05 - 45.09
mus = decode(A + 'shadowfall.mp3', 2)
mus = mus[int(TRACK_START * SR):int(TRACK_START * SR) + N]
if len(mus) < N:
    mus = np.concatenate([mus, np.zeros((N - len(mus), 2), np.float32)])
menv = env_db([(0, -60), (0.25, -60), (0.45, -5), (3.0, -5), (6.0, -7), (25.2, -7), (25.45, -26), (26.35, -26), (26.6, -9),
               (32.0, -10), (32.4, -13.5), (42.0, -13.5), (42.5, -8), (45.0, -8), (45.09, -9.5), (45.95, -9.5), (46.3, -3),
               (47.2, -4), (50.0, -60), (T, -60)])
mus *= menv[:, None]

# ------------------------------------------------------------------ campfire, seamless across the loop
fire = decode(A + 'fire.mp3', 2)
F0, XF = 15.0, 1.5
seg = fire[int(F0 * SR):int((F0 + T + XF) * SR)]
loop = seg[:N].copy()
k = int(XF * SR)
w = np.linspace(0, 1, k, dtype=np.float32)[:, None]
loop[:k] = seg[:k] * np.sqrt(w) + seg[N:N + k] * np.sqrt(1 - w)   # end flows into the start
fenv = env_db([(0, -9), (8, -9), (21.0, -9), (23.5, -4), (25.3, -3), (25.45, -40), (26.35, -40), (26.6, -15),
               (31.9, -15), (32.6, -13), (43.6, -13), (45.0, -18), (46.3, -18), (47.6, -10), (49.7, -9), (T, -9)])
loop *= fenv[:, None]


# ------------------------------------------------------------------ placeholder SFX (synthesised)
def adsr(n, a=0.002, d=0.05):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def noise(n):
    return rng.normal(0, 1, n).astype(np.float32)


def onepole(x, fc, hp=False):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return x - y if hp else y


def bandnoise(n, lo, hi):
    X = np.fft.rfft(noise(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n).astype(np.float32) / 3


def thump(dur=0.5, f0=62):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f0 * t * (1 + 0.6 * np.exp(-t / 0.03))) * np.exp(-t / 0.16)
    slap = bandnoise(n, 200, 2500) * np.exp(-t / 0.03)
    return (0.9 * body + 0.5 * slap).astype(np.float32)


def pop(dur=0.09):
    n = int(dur * SR)
    return (bandnoise(n, 900, 6000) * adsr(n, 0.001, 0.018) * 1.4).astype(np.float32)


def rustle(dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** 1.5 * (0.6 + 0.4 * np.abs(np.sin(t * 60)))
    return (bandnoise(n, 1200, 9000) * e * 0.9).astype(np.float32)


def click(f=900, dur=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) * 0.8 + bandnoise(n, 1500, 5000) * np.exp(-t / 0.006)).astype(np.float32)


def whoosh(dur=0.7, lo=300, hi=3000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** 2
    return (bandnoise(n, lo, hi) * e * 1.6).astype(np.float32)


def bell(f=740, dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dur * d)) for r, a, d in ((1, 1, 0.45), (2.76, 0.5, 0.2), (5.4, 0.25, 0.1), (0.5, 0.3, 0.6)))
    return (y * 0.35).astype(np.float32)


def ping(f=2600, dur=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t / 0.12) * 0.35).astype(np.float32)


def flap(dur=0.12):
    n = int(dur * SR)
    return (bandnoise(n, 120, 900) * adsr(n, 0.01, 0.04) * 1.2).astype(np.float32)


sfx = np.zeros((N, 2), np.float32)
place(sfx, thump(), 0.40, 0.55)                          # cover lands
place(sfx, thump(0.45, 55), 50.45, 0.5)                  # cover closes
place(sfx, rustle(0.45), T - 0.45, 0.25)                 # cover lifting (into the seam)
for t0 in (0.32, 8.40, 8.70, 8.82, 8.94, 9.02, 12.72, 16.95, 17.6, 18.72):
    place(sfx, pop(), t0, 0.35)
for k in range(9):
    place(sfx, pop(0.07), 10.0 + 0.11 * k + 0.02 * (k % 3), 0.22)
place(sfx, rustle(0.6), 7.95, 0.45)                      # page turn
for t0 in (47.0, 47.35, 47.7, 48.05, 48.45, 48.85):
    place(sfx, rustle(0.32), t0, 0.22)
place(sfx, rustle(0.6), 49.9, 0.3)
for t0 in (3.62, 4.42):
    place(sfx, click(520, 0.1), t0, 0.5)                 # finger on stone
place(sfx, thump(0.3, 110), 7.62, 0.45)                  # stamp
for k in range(14):
    place(sfx, bandnoise(int(0.05 * SR), 3000, 9000) * adsr(int(0.05 * SR), 0.003, 0.02), 11.0 + 0.09 * k, 0.12)  # fizzles
place(sfx, bell(), 13.16, 0.5)
place(sfx, whoosh(0.35, 200, 1200), 14.38, 0.25)         # candle out
for t0 in [15.30 + 0.09 * k for k in range(4)] + [15.66, 15.78, 15.90, 16.04, 16.14, 16.55, 16.75]:
    place(sfx, click(820, 0.07), t0 + 0.25, 0.32)          # planks snapping in
place(sfx, whoosh(0.7, 400, 4000), 19.5, 0.5)            # wildfire
for k in range(6):
    place(sfx, click(300 + 60 * k, 0.12), 20.62 + 0.06 * k, 0.35)   # collapse
place(sfx, thump(0.5, 70), 20.8, 0.35)
place(sfx, whoosh(1.4, 150, 1500), 24.2, 0.45)           # page engulfed
place(sfx, whoosh(0.8, 80, 900), 26.40, 0.6)             # ember ignites the pyre
for t0 in (30.62, 30.86, 31.04):
    place(sfx, click(1400, 0.06), t0, 0.35)
place(sfx, click(900, 0.15), T_BURST := 31.25, 0.6)
place(sfx, whoosh(0.5, 300, 5000), 31.25, 0.4)
for k in range(16):
    place(sfx, flap(), 31.45 + 0.17 * k, 0.32 * (1 - k / 20))
for t0 in (34.80, 37.35):
    place(sfx, whoosh(0.4, 500, 3000), t0, 0.3)
for t0 in (35.25, 37.8):
    place(sfx, whoosh(0.7, 100, 1200), t0, 0.55)
place(sfx, ping(), 37.8, 0.4)
place(sfx, whoosh(3.2, 100, 700), 43.7, 0.3)             # wind as the camera rises
# loop safety: nothing may ring over the end of the file except the cover rustle

# ------------------------------------------------------------------ sum
out = voice + mus + loop + sfx
np.save(D + "mix_raw.npy", out); np.save(D + "c_voice.npy", voice); np.save(D + "c_bed.npy", mus + loop); np.save(D + "c_sfx.npy", sfx)
pre = D + 'mix_pre.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', pre], input=out.astype(np.float32).tobytes())
L = lufs_of(pre)
gain = -14.0 - L
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', pre, '-af', f'volume={gain:.2f}dB,alimiter=limit=0.89:level=false', '-c:a', 'pcm_s16le', D + 'mix.wav'])
print('pre LUFS', L, 'gain', round(gain, 2), 'final', lufs_of(D + 'mix.wav'))
