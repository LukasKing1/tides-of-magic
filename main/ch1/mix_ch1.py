"""Audio for chapter 1 (preview): Shadowfall as stand-in for T1 (drop on the title hit), the two voice
files that exist (01-6, 01-7), placeholder SFX until the real ones are chosen.  -> mix.wav"""
import re, subprocess, os
import numpy as np

SR = 48000
T = 91.0
N = int(T * SR)
D = '/home/claude/main/ch1/'
A = '/home/claude/main/audio/'
rng = np.random.default_rng(7)


def decode(path, ch=2, af=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', str(ch), '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()


def lufs_of(path, af=None):
    cmd = ['ffmpeg', '-v', 'info', '-i', path, '-af', (af + ',' if af else '') + 'ebur128', '-f', 'null', '-']
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1])


def env_db(points, n=N):
    t = np.arange(n) / SR
    ts, ds = zip(*points)
    return (10 ** (np.interp(t, ts, ds) / 20)).astype(np.float32)


def place(buf, x, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    i1 = min(len(buf), i0 + len(x))
    if i1 > i0 >= 0:
        buf[i0:i1] += x[:i1 - i0] * gain
    return buf


# ------------------------------------------------------------------ synth helpers
def noise(n):
    return rng.normal(0, 1, n).astype(np.float32)


def bandnoise(n, lo, hi):
    X = np.fft.rfft(noise(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return (np.fft.irfft(X, n) / 3).astype(np.float32)


def adsr(n, a=0.002, d=0.05):
    t = np.arange(n) / SR
    return (np.minimum(t / a, 1) * np.exp(-t / d)).astype(np.float32)


def thump(dur=0.5, f0=62, slap=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f0 * t * (1 + 0.6 * np.exp(-t / 0.03))) * np.exp(-t / 0.16)
    s = bandnoise(n, 200, 2500) * np.exp(-t / 0.03)
    return (0.9 * body + slap * s).astype(np.float32)


def pop(dur=0.09):
    n = int(dur * SR)
    return (bandnoise(n, 900, 6000) * adsr(n, 0.001, 0.018) * 1.4).astype(np.float32)


def rustle(dur=0.5, lo=1200, hi=9000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** 1.5 * (0.6 + 0.4 * np.abs(np.sin(t * 60)))
    return (bandnoise(n, lo, hi) * e * 0.9).astype(np.float32)


def click(f=900, dur=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) * 0.8 + bandnoise(n, 1500, 5000) * np.exp(-t / 0.006)).astype(np.float32)


def whoosh(dur=0.7, lo=300, hi=3000, shape=2.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** shape
    return (bandnoise(n, lo, hi) * e * 1.6).astype(np.float32)


def riser(dur=1.4, lo=200, hi=4000):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = (t / dur) ** 2.2
    return (bandnoise(n, lo, hi) * e * 1.4).astype(np.float32)


def bell(f=740, dur=2.2, a=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(k * np.sin(2 * np.pi * f * r * t) * np.exp(-t / (dur * d)) for r, k, d in ((1, 1, 0.45), (2.76, 0.5, 0.2), (5.4, 0.25, 0.1), (0.5, 0.3, 0.6)))
    return (y * a).astype(np.float32)


def shimmer(dur=1.5, f=2400):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.sin(np.pi * t / dur) ** 2
    y = sum(np.sin(2 * np.pi * f * k * t + k) * (0.5 / k) for k in (1, 1.5, 2.01, 2.97)) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
    return (y * e * 0.18).astype(np.float32)


def flap(dur=0.12):
    n = int(dur * SR)
    return (bandnoise(n, 120, 900) * adsr(n, 0.01, 0.04) * 1.2).astype(np.float32)


def chirp(dur=0.35, f0=900, f1=1900):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** 0.6
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.sin(np.pi * t / dur) ** 0.7 * (0.7 + 0.3 * np.sin(2 * np.pi * 30 * t))
    return (y * 0.25).astype(np.float32)


def crackle(dur, rate=30, amp=0.4):
    """sparse fire/ice crackle"""
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    k = int(rate * dur)
    for _ in range(k):
        i = int(rng.uniform(0, n - 2000))
        m = int(rng.uniform(200, 1400))
        out[i:i + m] += bandnoise(m, 2000, 9000) * adsr(m, 0.0005, rng.uniform(0.002, 0.01)) * rng.uniform(0.3, 1.0)
    return out * amp


def wind(dur, lo=150, hi=1400, speed=0.15):
    n = int(dur * SR)
    t = np.arange(n) / SR
    lfo = 0.55 + 0.45 * np.sin(2 * np.pi * speed * t + 1.3) * np.sin(2 * np.pi * speed * 0.37 * t)
    return (bandnoise(n, lo, hi) * lfo * 0.9).astype(np.float32)


def footstep(dur=0.32):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (bandnoise(n, 80, 1600) * np.exp(-t / 0.06) * 0.9 + bandnoise(n, 2000, 6000) * np.exp(-t / 0.02) * 0.25).astype(np.float32)


# ------------------------------------------------------------------ voice
VOICE_AF = 'highpass=f=75,lowpass=f=12000,aecho=1.0:0.92:38|74:0.10|0.06'
voice = np.zeros((N, 2), np.float32)
for name, t0 in (('01-6', 66.0), ('01-7', 80.0)):
    f = A + f'{name}.mp3'
    if os.path.exists(f):
        L = lufs_of(f, VOICE_AF)
        place(voice, decode(f, 2, VOICE_AF), t0, 10 ** ((-16.0 - L) / 20))

# ------------------------------------------------------------------ music: Shadowfall (stand-in for T1)
mus_src = decode('/home/claude/short1/audio/shadowfall.mp3', 2)
mus = np.zeros((N, 2), np.float32)
# A: intro + first build under the legend and the Dothraki Sea
segA = mus_src[:int(37.0 * SR)]
place(mus, segA, 0.0)
# B: build -> break -> drop exactly on the title hit (track 46.05 s == video 85.5 s)
TB = 46.05 - 85.5 + 66.0
segB = mus_src[int(TB * SR):int((TB + 25.5) * SR)]
mb = np.zeros((N, 2), np.float32)
place(mb, segB, 66.0)
envA = env_db([(0, -60), (0.2, -60), (0.6, -6), (3.0, -8), (17.0, -6), (18.4, -3), (19.2, -9), (34.6, -10), (35.6, -40), (36.6, -70), (T, -70)])
envB = env_db([(0, -70), (65.4, -70), (66.6, -16), (79.4, -14), (79.9, -9), (80.3, -14), (84.4, -12), (85.45, -6), (85.55, -1.5), (87.0, -3),
               (89.6, -5), (91.0, -60)])
mus = mus * envA[:, None] + mb * envB[:, None]

# ------------------------------------------------------------------ ambience
fire = decode(A + 'fire.mp3', 2) if os.path.exists(A + 'fire.mp3') else decode('/home/claude/short1/audio/fire.mp3', 2)
amb = np.zeros((N, 2), np.float32)
fseg = fire[int(5 * SR):int(5 * SR) + N]
amb[:len(fseg)] += fseg * env_db([(0, -60), (0.2, -16), (17.0, -18), (18.4, -40), (36.4, -40), (37.5, -26), (53.2, -24), (53.6, -10),
                                  (58.6, -12), (60.0, -24), (64.0, -24), (65.0, -16), (85.0, -18), (91.0, -40)])[:len(fseg), None]
w1 = wind(T, 180, 1600, 0.12)
amb += np.stack([w1, np.roll(w1, 900)], 1) * env_db([(0, -70), (18.2, -70), (19.2, -28), (35.0, -27), (35.8, -40), (36.6, -32), (63.8, -32),
                                                     (64.8, -70), (T, -70)])[:, None]
grass = bandnoise(N, 2500, 8000) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * np.arange(N) / SR))
amb += np.stack([grass, grass], 1) * env_db([(0, -80), (18.4, -80), (19.4, -40), (35.0, -40), (35.8, -80), (T, -80)])[:, None]

# ------------------------------------------------------------------ SFX (placeholders)
sfx = np.zeros((N, 2), np.float32)
# book opening
place(sfx, rustle(0.9, 400, 4000), 0.45, 0.35)
place(sfx, thump(0.4, 70, 0.3), 1.42, 0.35)
place(sfx, rustle(0.8), 2.0, 0.35)
for t0 in (3.1, 3.35, 3.7):
    place(sfx, pop(), t0, 0.4)
place(sfx, whoosh(4.0, 200, 1500, 1.2), 6.0, 0.12)
place(sfx, riser(2.4, 2000, 9000), 7.9, 0.22)
for k in range(9):
    place(sfx, click(1400 + 120 * k, 0.07), 9.6 + 0.13 * k, 0.28)
place(sfx, click(900, 0.15), 10.9, 0.6)
place(sfx, whoosh(0.6, 300, 6000), 10.88, 0.5)
place(sfx, bell(980, 2.4, 0.3), 10.9, 0.5)
for k in range(40):
    place(sfx, flap(), 11.0 + 0.09 * k + 0.03 * (k % 3), 0.25 * (1 - k / 60))
place(sfx, whoosh(3.0, 200, 2000, 1.0), 14.6, 0.25)
place(sfx, riser(1.4, 150, 3000), 17.2, 0.5)
place(sfx, whoosh(1.2, 100, 1500), 18.2, 0.6)
for k in range(14):
    place(sfx, flap(0.14), 18.9 + 0.17 * k, 0.2 * (1 - k / 16))
place(sfx, crackle(3.0, 20, 0.2), 20.0, 0.6)
place(sfx, pop(0.12), QARTH := 27.3, 0.45)
place(sfx, rustle(0.4), 33.3, 0.3)
place(sfx, whoosh(1.4, 80, 900), 35.2, 0.4)
# dawn: footsteps in the ash, robe, bangles
for k in range(8):
    place(sfx, footstep(), 37.0 + 0.44 * k, 0.32)
    place(sfx, rustle(0.4, 300, 3000), 37.05 + 0.44 * k, 0.07)
for t0 in (37.4, 38.3, 39.2, 40.4):
    place(sfx, bell(2600, 0.5, 0.12), t0, 0.35)
place(sfx, shimmer(1.8, 1800), 49.2, 0.5)
place(sfx, whoosh(1.8, 100, 1800, 1.0), 49.2, 0.25)
place(sfx, riser(0.8, 200, 4000), 52.7, 0.4)
place(sfx, whoosh(1.4, 80, 3000), 53.4, 0.7)
place(sfx, thump(0.8, 48, 0.2), 53.45, 0.5)
for t0 in (55.3, 55.8, 56.3):
    place(sfx, chirp(0.38, 800 + (t0 - 55) * 300, 1800), t0 + 0.2, 0.55)
for k in range(10):
    place(sfx, flap(0.13), 56.0 + 0.2 * k, 0.18)
place(sfx, whoosh(1.0, 100, 1200), 64.2, 0.35)
# the book again
place(sfx, rustle(0.9, 400, 4000), 65.25, 0.35)
place(sfx, thump(0.4, 70, 0.3), 66.25, 0.3)
place(sfx, rustle(1.8, 3000, 9000) * 0.4, 67.0, 0.4)       # quill
place(sfx, rustle(1.8, 3000, 9000) * 0.4, 72.1, 0.35)
place(sfx, crackle(2.2, 40, 0.5), 76.6, 0.45)                 # frost
place(sfx, shimmer(2.0, 3200), 76.7, 0.3)
place(sfx, whoosh(1.4, 200, 3000, 1.0), 78.2, 0.35)           # fire
place(sfx, crackle(1.4, 50, 0.4), 78.3, 0.5)
place(sfx, rustle(0.8), 79.65, 0.4)
for t0 in (80.3, 80.42, 80.54):
    place(sfx, pop(), t0, 0.35)
place(sfx, chirp(0.3, 1200, 2600), 84.75, 0.5)
place(sfx, rustle(0.5, 400, 4000), 85.0, 0.35)
place(sfx, thump(0.9, 46, 0.6), 85.48, 0.95)                  # book shuts on the drop
place(sfx, bell(660, 3.0, 0.32), 85.5, 0.55)
place(sfx, shimmer(1.6, 2200), 85.6, 0.45)
place(sfx, shimmer(1.4, 3000), 86.9, 0.35)
place(sfx, crackle(4.0, 14, 0.3), 85.6, 0.4)

# ------------------------------------------------------------------ sum + loudness
out = voice + mus + amb + sfx
pre = D + 'mix_pre.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', pre], input=out.astype(np.float32).tobytes())
L = lufs_of(pre)
gain = -14.0 - L
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', pre, '-af', f'volume={gain:.2f}dB,alimiter=limit=0.89:level=false', '-c:a', 'pcm_s16le', D + 'mix.wav'])
print('pre LUFS', L, 'gain', round(gain, 2), 'final', lufs_of(D + 'mix.wav'))
