#!/usr/bin/env python3
"""Bewegungstest Kino-Look: Startband 3-2-1, Zwischentitel, Fahrt ins Lichtspielhaus (ca. 9 s).

python3 anim11.py <out.mp4>
"""
import math, subprocess, sys
import numpy as np
import skia
from PIL import Image
import rich as R
import frames11 as K
from rich_base import *


def weave(arr, frame, amp=3):
    rng = np.random.default_rng(1000 + frame)
    dx, dy = int(rng.integers(-amp, amp + 1)), int(rng.integers(-amp, amp + 1))
    out = np.roll(np.roll(arr, dy, axis=0), dx, axis=1)
    f = rng.uniform(.93, 1.04)
    out[..., :3] = np.clip(out[..., :3].astype(np.float32) * f, 0, 255).astype(np.uint8)
    return out


def fade(arr, k):
    out = arr.copy()
    out[..., :3] = (out[..., :3].astype(np.float32) * k).astype(np.uint8)
    return out


def main(out):
    P.init_assets()
    R.init_layers()
    surf = skia.Surface(W, H)
    frames = []
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                             '-r', str(FPS), '-i', '-', '-vf', 'scale=1280:720', '-c:v', 'libx264', '-preset', 'medium',
                             '-crf', '20', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], stdin=subprocess.PIPE)

    def emit(arr):
        proc.stdin.write(np.ascontiguousarray(arr[..., :3]).tobytes())

    n = 0
    for f in range(3 * FPS):
        t = f / FPS
        cv = surf.getCanvas()
        P.G.zoom = 1.0
        K.leader(cv, 3 - int(t), t % 1.0)
        arr = K.film_look(K.snap(surf), 'bw', seed=n, scratches=7, dust=60, vign=.5)
        emit(weave(arr, n))
        n += 1
    cv = surf.getCanvas()
    K.intertitle(cv)
    clean = K.snap(surf)
    D = int(3.4 * FPS)
    for f in range(D):
        k = min(1.0, f / 6) * min(1.0, (D - f) / 8)
        arr = K.film_look(clean, 'sepia', seed=200 + n, scratches=6, dust=50, vign=.45)
        emit(fade(weave(arr, n, 2), k))
        n += 1
    cinema = K.to_img(K.load('frames11/cinema.png'))
    D = int(3.2 * FPS)
    for f in range(D):
        u = f / (D - 1)
        cv = surf.getCanvas()
        cv.clear(skia.ColorBLACK)
        z = lerp(1.0, 1.12, eio(u))
        cv.save()
        cv.translate(W / 2, H * .55)
        cv.scale(z, z)
        cv.translate(-W / 2, -H * .55)
        cv.drawImage(cinema, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear))
        rng = np.random.default_rng(500 + f)
        cv.drawRect(skia.Rect.MakeXYWH(560, 120, 800, 450), fillp(cv, '#fff2cf', rng.uniform(0, .07), False))
        cv.restore()
        arr = K.snap(surf)
        emit(fade(arr, min(1.0, f / 6) * min(1.0, (D - f) / 10)))
        n += 1
    proc.stdin.close()
    proc.wait()
    print('saved', out, n, 'frames')


if __name__ == '__main__':
    main(sys.argv[1])
