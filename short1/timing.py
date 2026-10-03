"""Word timings for the five voice files (no ASR available): sentence segments come from silence
detection, words are spread over the voiced time inside each segment by syllable weight.
Writes words.json with global times (file offset in the Short added)."""
import json, re, subprocess
import numpy as np

# where each file starts in the Short (seconds)
OFFS = {1: 0.15, 2: 8.50, 3: 26.30, 4: 33.40, 5: 42.00}
TEXT = {
    1: ["For almost a hundred and fifty years, the Targaryens tried to hatch a dragon.", "Every single attempt failed."],
    2: ["Aegon the Third brought nine mages from across the sea.", "Baelor prayed over the eggs.",
        "Aegon the Fourth built dragons out of wood and iron.", "Aerion drank wildfire, and burned.",
        "And at Summerhall,", "the last attempt ended in flames."],
    3: ["Then", "a girl walks into a funeral pyre,", "and walks out with three dragons."],
    4: ["Not because she knew something they didn't.", "Not because her blood was purer.",
        "But because she walked into the fire at the right moment."],
    5: ["What changed wasn't the Targaryens.", "It was the world."],
}
SYL = {'targaryens': 4, 'aegon': 2, 'baelor': 2, 'aerion': 3, 'summerhall': 3, 'wildfire': 2, 'pyre': 1, 'fire': 1,
       'hundred': 2, "didn't": 2, 'fourth': 1, 'iron': 2, 'single': 2, 'every': 3, 'attempt': 2, 'failed': 1,
       'prayed': 1, 'burned': 1, 'changed': 1, "wasn't": 2, 'eggs': 1, 'mages': 2, 'purer': 2, 'moment': 2,
       'walked': 1, 'walks': 1, 'almost': 2, 'fifty': 2, 'years': 1, 'dragons': 2, 'dragon': 2, 'the': 1, 'world': 1}


def syl(w):
    k = re.sub(r"[^a-z']", '', w.lower())
    if k in SYL:
        return SYL[k]
    return max(1, len(re.findall(r'[aeiouy]+', k.rstrip('e'))))


def load(f, sr=16000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768, sr


def segments(x, sr, min_sil=12):
    hop = int(0.01 * sr)
    e = np.array([np.sqrt(np.mean(x[k:k + hop] ** 2) + 1e-12) for k in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(e + 1e-9)
    voiced = db > db.max() - 38
    segs, on, sil, last = [], None, 0, 0
    for k, v in enumerate(voiced):
        if v:
            if on is None:
                on = k
            sil, last = 0, k
        elif on is not None:
            sil += 1
            if sil >= min_sil:
                segs.append((on * 0.01, (last + 1) * 0.01)); on = None; sil = 0
    if on is not None:
        segs.append((on * 0.01, (last + 1) * 0.01))
    return segs, voiced


def main():
    words = []
    for i in range(1, 6):
        x, sr = load(f'/home/claude/short1/audio/S-{i}.mp3')
        segs, voiced = segments(x, sr)
        sents = TEXT[i]
        assert len(segs) == len(sents), (i, len(segs), len(sents))
        for (a, b), sent in zip(segs, sents):
            ws = sent.split()
            # voiced frames inside the segment (fine pauses at commas are skipped automatically)
            fr = [k for k in range(int(a * 100), int(b * 100)) if k < len(voiced) and voiced[k]]
            w_syl = np.array([syl(w) + (0.6 if w.endswith(',') else 0) for w in ws], float)
            cum = np.concatenate([[0], np.cumsum(w_syl)]) / w_syl.sum()
            n = len(fr)
            for j, w in enumerate(ws):
                s = fr[min(int(cum[j] * n), n - 1)] * 0.01
                e = fr[min(int(cum[j + 1] * n), n - 1)] * 0.01 + 0.01
                words.append(dict(w=w, s=round(OFFS[i] + s, 3), e=round(OFFS[i] + e, 3), f=i))
    json.dump(words, open('/home/claude/short1/words.json', 'w'), indent=0)
    for w in words:
        print(f"{w['s']:6.2f}-{w['e']:6.2f} {w['w']}")


if __name__ == '__main__':
    main()
