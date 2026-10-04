"""Ton der Testszene Kapitel 4: Stimmen (04-7, Q4, 04-8), Teilmotiv 2, Platzhalter-Geräusche -> mix4.wav"""
import sys, subprocess
sys.path.insert(0, '/home/claude/main/ch4')
from sfxlib import *
import numpy as np
V47, VQ, V48 = 1.2, 9.2, 36.6
def q(r): return VQ + r

VOICE_AF = 'highpass=f=75,lowpass=f=12000,aecho=1.0:0.92:38|74:0.10|0.06'
QUOTE_AF = 'highpass=f=110,lowpass=f=9000,aecho=1.0:0.9:52|96:0.14|0.08'
voice = np.zeros((N, 2), np.float32)
for name, t0, af, lv in (('04-7', V47, VOICE_AF, -16.0), ('Q4', VQ, QUOTE_AF, -16.5), ('04-8', V48, VOICE_AF, -16.0)):
    f = A + f'{name}.mp3'
    L = lufs_of(f, af)
    place(voice, decode(f, 2, af), t0, 10 ** ((lv - L) / 20))

# Musik: Teilmotiv 2 (Entdeckung)
m = decode('/home/claude/tides-of-magic/music/Teilmotiv2.mp3', 2)
mus = np.zeros((N, 2), np.float32)
place(mus, m[:N], 0.0)
mus *= env_db([(0, -60), (0.4, -14), (1.0, -19), (6.4, -19), (7.2, -11), (8.8, -11), (9.3, -21), (19.0, -21), (19.6, -15), (20.6, -21),
               (33.6, -21), (34.0, -12), (36.2, -13), (36.7, -20), (55.4, -20), (56.0, -12), (57.6, -14), (58.6, -60)])[:, None]

amb = np.zeros((N, 2), np.float32)
# Rampenlicht-Flämmchen im Theater
cr = crackle(28.5, 10, 0.18)
place(amb, np.stack([cr, np.roll(cr, 700)], 1), 6.8, 1.0)
lowr = bandnoise(N, 40, 160) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * np.arange(N) / SR))
amb += np.stack([lowr, lowr], 1) * env_db([(0, -80), (q(11.0), -80), (q(12.2), -26), (q(24.6), -24), (34.4, -80), (58.6, -80)])[:, None]

sfx = np.zeros((N, 2), np.float32)
place(sfx, rustle(0.8), 1.9, 0.35)                                 # Umblättern
place(sfx, whoosh(2.6, 150, 1500, 1.2), 4.4, 0.18)                 # Kamerafahrt in die Tafel
place(sfx, shimmer(1.6, 2000), 6.4, 0.35)
for k in range(6):
    place(sfx, pop(0.1), 7.0 + 0.14 * k, 0.4)                      # Pop-up-Wolken
place(sfx, whoosh(0.8, 300, 4000), 8.35, 0.45)                     # Bilderbuch-Blatt fällt
place(sfx, thump(0.5, 70, 0.4), 9.08, 0.45)
place(sfx, rustle(0.5, 600, 5000), q(0.1), 0.25)                   # Opal-Kaiser steigt auf
place(sfx, rustle(0.6, 500, 4000), q(2.2), 0.22)
place(sfx, rustle(0.9, 800, 6000), q(2.6), 0.25)                   # Kaiserin gleitet herein
place(sfx, bell(1320, 1.4, 0.18), q(3.4), 0.4)                     # Nimbus
place(sfx, rustle(0.9, 800, 6000), q(5.3), 0.25)                   # Bruder
place(sfx, whoosh(0.3, 1500, 8000), q(6.25), 0.5)                  # Hieb
place(sfx, click(600, 0.12), q(6.45), 0.6)
place(sfx, thump(0.5, 55, 0.3), q(7.1), 0.45)                      # sie fällt
place(sfx, bell(990, 1.6, 0.2), q(7.0), 0.25)
place(sfx, flap(0.3), q(9.0), 0.3)                                 # Puppe dreht sich
place(sfx, riser(1.2, 200, 5000), q(8.8), 0.35)
place(sfx, crackle(2.2, 60, 0.6), q(9.9), 0.7)                     # Blatt brennt
place(sfx, whoosh(1.8, 80, 2000, 1.0), q(9.9), 0.5)
place(sfx, thump(1.2, 40, 0.2), q(11.9), 0.6)                      # Schreckensherrschaft
place(sfx, shimmer(1.4, 900), q(14.0), 0.45)                       # Zauberkreis
for k in range(10):
    place(sfx, click(2200 + 300 * (k % 3), 0.05), q(15.25) + 0.07 * k, 0.25)   # Knochen klappern
for k in range(18):
    place(sfx, click(3200 + 500 * (k % 4), 0.06), q(15.95) + 0.09 * k + 0.02 * (k % 3), 0.18)  # Ketten
place(sfx, rustle(0.8, 300, 3000), q(17.7), 0.3)                   # Tigerfrau
place(sfx, thump(0.9, 45, 0.1), q(19.8), 0.4)
place(sfx, whoosh(0.4, 200, 2000), q(20.9), 0.4)                   # Seile
place(sfx, riser(0.6, 100, 1500), q(21.0), 0.4)
place(sfx, whoosh(1.0, 60, 1200), q(21.3), 0.6)                    # Statue stürzt
place(sfx, thump(1.2, 42, 0.5), q(22.2), 0.8)
place(sfx, whoosh(1.0, 200, 5000, 1.0), q(22.6), 0.5)              # Stein fällt
place(sfx, crackle(0.9, 70, 0.6), q(22.6), 0.6)
place(sfx, thump(1.4, 38, 0.6), q(23.5), 1.0)                      # Aufschlag
place(sfx, bell(440, 3.0, 0.3), q(23.5), 0.4)
place(sfx, shimmer(1.6, 1400), q(23.6), 0.4)
place(sfx, shimmer(1.2, 2600), 33.9, 0.35)                         # Erstarren zur Radierung
place(sfx, whoosh(1.4, 120, 1500), 35.0, 0.25)
place(sfx, rustle(0.8), 36.15, 0.35)                               # Umblättern
for (tp) in (0.35, 1.35, 1.75, 3.0, 4.5):
    place(sfx, pop(0.11), V48 + tp, 0.45)
place(sfx, rustle(3.0, 3000, 9000) * 0.5, V48 + 10.1, 0.35)        # Feder zieht die Linie
for k in range(5):
    place(sfx, chirp(0.3, 900 + 150 * k, 2200), V48 + 11.7 + k * 0.55 + 0.45, 0.4)
    place(sfx, pop(0.1), V48 + 11.7 + k * 0.55 + 0.9, 0.3)
place(sfx, whoosh(0.8, 300, 3000), V48 + 14.0, 0.25)
for k in range(5):
    place(sfx, bell(880 * 2 ** (k / 12 * 2), 1.4, 0.16), V48 + 16.4 + k * 0.32, 0.4)
place(sfx, shimmer(1.8, 1800), V48 + 17.6, 0.45)

out = voice + mus + amb + sfx
pre = D + 'mix4_pre.wav'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', pre], input=out.astype(np.float32).tobytes())
L = lufs_of(pre)
gain = -14.0 - L
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', pre, '-af', f'volume={gain:.2f}dB,alimiter=limit=0.89:level=false', '-c:a', 'pcm_s16le', D + 'mix4.wav'])
print('pre LUFS', L, 'final', lufs_of(D + 'mix4.wav'))
