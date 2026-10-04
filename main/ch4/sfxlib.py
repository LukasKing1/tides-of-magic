"""Synth-Helfer (aus Kapitel 1) (preview): Shadowfall as stand-in for T1 (drop on the title hit), the two voice
files that exist (01-6, 01-7), placeholder SFX until the real ones are chosen.  -> mix.wav"""
import re, subprocess, os
import numpy as np

SR = 48000
T = 58.6
N = int(T * SR)
D = '/home/claude/main/ch4/'
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


