"""Synthesize the course's music bed and sound effects from scratch (no third-party audio, no licensing questions).

usage: python tools/make_audio_assets.py      # writes shared/audio/*.wav (24 kHz mono)
"""
from pathlib import Path

import numpy as np
import soundfile as sf

SR = 24000
OUT = Path(__file__).resolve().parent.parent / "shared/audio"
rng = np.random.default_rng(7)


def t(seconds):
    return np.arange(int(seconds * SR)) / SR


def env(n, attack, release):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] *= np.linspace(1, 0, r)
    return e


def lowpass(x, cutoff):
    """One-pole low-pass, enough to soften synth edges."""
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def note(freq):
    return 440.0 * 2 ** ((freq - 69) / 12)


def music_bed(seconds_per_chord=8.0):
    """Slow four-chord pad (Cmaj9 - Am9 - Fmaj7 - G6sus), seamless 32 s loop."""
    chords = [[48, 55, 59, 62, 64], [45, 52, 55, 59, 60], [41, 48, 52, 55, 60], [43, 50, 55, 57, 62]]
    total = int(seconds_per_chord * len(chords) * SR)
    out = np.zeros(total)
    n = int(seconds_per_chord * SR)
    xfade = int(2.0 * SR)
    for i, chord in enumerate(chords):
        tt = np.arange(n + xfade) / SR
        seg = np.zeros_like(tt)
        for k, m in enumerate(chord):
            f = note(m)
            detune = 1 + 0.0015 * (k - 2)
            seg += (np.sin(2 * np.pi * f * detune * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt + k)) / len(chord)
        shape = np.ones_like(tt)
        shape[:xfade] = np.linspace(0, 1, xfade) ** 0.5
        shape[-xfade:] = np.linspace(1, 0, xfade) ** 0.5
        seg *= shape * (0.85 + 0.15 * np.sin(2 * np.pi * tt / seconds_per_chord))
        start = i * n
        idx = (np.arange(len(seg)) + start) % total  # wrap the last crossfade onto the start: seamless loop
        np.add.at(out, idx, seg)
    out = lowpass(out, 1400)
    return out / np.max(np.abs(out)) * 0.5


def whoosh():
    n = len(t(0.55))
    noise = rng.standard_normal(n)
    sweep = np.linspace(300, 2600, n)
    y = np.zeros(n)
    acc, cutoff_alpha = 0.0, np.exp(-2 * np.pi * sweep / SR)
    for i in range(n):
        acc = (1 - cutoff_alpha[i]) * noise[i] + cutoff_alpha[i] * acc
        y[i] = acc
    shape = np.sin(np.linspace(0, np.pi, n)) ** 2
    return y * shape / np.max(np.abs(y * shape)) * 0.5


def tick():
    tt = t(0.07)
    y = np.sin(2 * np.pi * 1320 * tt) * np.exp(-tt * 60) + 0.4 * np.sin(2 * np.pi * 2640 * tt) * np.exp(-tt * 90)
    return y / np.max(np.abs(y)) * 0.4


def chime():
    tt = t(1.2)
    y = sum(np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * d) for m, d in [(76, 3.5), (83, 4.5), (88, 5.5)])
    y *= env(len(tt), 0.005, 0.3)
    return y / np.max(np.abs(y)) * 0.45


def sting():
    """Short rising arpeggio for lesson openers."""
    out = np.zeros(len(t(1.6)))
    for i, m in enumerate([60, 64, 67, 71, 74]):
        tt = t(1.6 - i * 0.09)
        y = (np.sin(2 * np.pi * note(m) * tt) + 0.3 * np.sin(2 * np.pi * 2 * note(m) * tt)) * np.exp(-tt * 3.2)
        start = int(i * 0.09 * SR)
        out[start:start + len(y)] += y[: len(out) - start]
    out *= env(len(out), 0.004, 0.4)
    return out / np.max(np.abs(out)) * 0.45


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("music_bed", music_bed), ("whoosh", whoosh), ("tick", tick), ("chime", chime), ("sting", sting)]:
        sf.write(OUT / f"{name}.wav", fn().astype(np.float32), SR, subtype="FLOAT")
        print("wrote", name)


if __name__ == "__main__":
    main()
