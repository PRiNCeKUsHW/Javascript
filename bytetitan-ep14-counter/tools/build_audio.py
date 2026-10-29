"""Build the music bed and sound effects for Ep 14, and write the <audio> tags.

  python tools/build_audio.py

- assets/audio/music.wav: an original 120 BPM "results night" theme (brass
  stabs, drums, bass) synthesised here, because no music source is reachable
  from the build machine. Replace it with ./assets/music.mp3 if you have a
  licensed track: put the file there and re-run; it is used instead.
- assets/sfx/*: bundled HyperFrames effects copied in, plus the four the
  library lacks (paper thup, tally scratch, crowd cheer, camera shutter,
  game-show buzzer), synthesised.
- index.html: the block between AUDIO:BEGIN and AUDIO:END is rewritten with
  the music (ducked under the voice with a volume lane), the voiceover and
  every effect cue.
"""
import json, re, shutil, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
TOTAL = 60.0
rng = np.random.default_rng(14)

# Scene cuts (seconds). Must match the hosts in index.html.
CUTS = [3.3, 13.0, 24.0, 36.0, 46.0, 54.4]

def t_axis(d):
    return np.arange(int(d * SR)) / SR

def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)

def env_adsr(n, a=0.01, d=0.08, s=0.6, r=0.1, hold=None):
    t = np.arange(n) / SR
    total = n / SR
    hold = total - r if hold is None else hold
    e = np.where(t < a, t / a, 1.0)
    e = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / d, e)
    e = np.where((t >= a + d) & (t < hold), s, e)
    e = np.where(t >= hold, s * np.clip(1 - (t - hold) / r, 0, 1), e)
    return e

def fft_filter(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))

def brass(notes, dur, bright=1.0):
    """Detuned additive-saw chord with a filter-like brightness envelope."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    # brightness: opens fast on the attack, closes over the note
    c = np.clip(0.10 + 0.25 * (1 - np.exp(-t / (0.25 * bright))) - 0.05 * np.exp(-t / 0.03), 0.06, 0.6)
    out = np.zeros(n)
    for note in notes:
        for det in (-0.004, 0.004):
            f0 = midi(note) * (1 + det)
            vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.3, 0, 1)
            phase = 2 * np.pi * f0 * np.cumsum(vib) / SR
            for h in range(1, 18):
                if f0 * h > 9000:
                    break
                out += np.sin(h * phase) * (1 / h) * np.exp(-(h - 1) * c)
    out *= env_adsr(n, a=0.012, d=0.09, s=0.55, r=min(0.12, dur * 0.4))
    return out / max(1e-9, np.max(np.abs(out)))

def kick():
    t = t_axis(0.32)
    f = 48 + 90 * np.exp(-t / 0.035)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    x += 0.3 * rng.standard_normal(len(t)) * np.exp(-t / 0.004)
    return x

def snare():
    t = t_axis(0.25)
    noise = fft_filter(rng.standard_normal(len(t)), lo=1200, hi=9000) * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05)
    return 0.8 * noise / np.max(np.abs(noise)) + 0.5 * body

def hat(open_=False):
    t = t_axis(0.25 if open_ else 0.05)
    x = fft_filter(rng.standard_normal(len(t)), lo=7000) * np.exp(-t / (0.08 if open_ else 0.012))
    return x / np.max(np.abs(x))

def crash():
    t = t_axis(1.8)
    x = fft_filter(rng.standard_normal(len(t)), lo=3500, hi=14000) * np.exp(-t / 0.55)
    return x / np.max(np.abs(x))

def timp(note=34):
    t = t_axis(0.9)
    f = midi(note) * (1 + 0.15 * np.exp(-t / 0.05))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    x += 0.4 * np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR) * np.exp(-t / 0.2)
    return x / np.max(np.abs(x))

def bass_note(note, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f0 = midi(note)
    x = sum(np.sin(2 * np.pi * f0 * h * t) / h for h in range(1, 7))
    return x * env_adsr(n, a=0.005, d=0.05, s=0.7, r=0.04) / 2.2

def place(buf, x, at, gain=1.0, pan=0.0):
    a = int(at * SR)
    if a >= len(buf):
        return
    x = x[: len(buf) - a]
    buf[a : a + len(x), 0] += x * gain * (1 - max(0, pan))
    buf[a : a + len(x), 1] += x * gain * (1 + min(0, pan))

# Bb, Gb, Ab, F (one chord per 2 s bar)
CHORDS = [[70, 74, 77], [66, 70, 73], [68, 72, 75], [65, 69, 72]]
ROOTS = [46, 42, 44, 41]

def build_music():
    buf = np.zeros((int(TOTAL * SR), 2))
    K, S, HC, HO, CR = kick(), snare(), hat(), hat(True), crash()
    beat = 0.5

    def section(t):
        if t < 3.3:
            return "hook"
        if t < 13.0:
            return "old"
        if t < 54.4:
            return "full"
        return "outro"

    # opening sting: da-da-DAAA on the first chord
    for at, d in ((0.0, 0.16), (0.2, 0.16), (0.42, 0.9)):
        place(buf, brass(CHORDS[0], d), at, 0.55)
    place(buf, timp(34), 0.42, 0.7)
    place(buf, CR, 0.42, 0.25)

    for i in range(int(TOTAL / beat)):
        t = i * beat
        if t < 1.0 or t >= 59.0:
            continue
        sec = section(t)
        bar = int(t // 2.0) % 4
        pos = i % 4  # beat in bar
        if sec == "old":
            # the old way: tired, half-time, no brass
            if pos == 0:
                place(buf, K, t, 0.45)
            place(buf, HC, t + 0.25, 0.10)
            if pos in (0, 2):
                place(buf, bass_note(ROOTS[bar], 0.9), t, 0.30)
            continue
        if pos in (0, 2):
            place(buf, K, t, 0.75)
        if pos == 3:
            place(buf, K, t + 0.25, 0.45)
        if pos in (1, 3):
            place(buf, S, t, 0.45)
        place(buf, HC, t, 0.16, pan=0.3)
        place(buf, HC, t + 0.25, 0.10, pan=0.3)
        for e in (0, 0.25):
            place(buf, bass_note(ROOTS[bar], 0.2), t + e, 0.42)
        if pos == 0:
            place(buf, brass(CHORDS[bar], 0.14), t, 0.30)
        if pos == 1:
            place(buf, brass(CHORDS[bar], 0.14), t + 0.25, 0.26)
        if pos == 3 and bar % 2 == 1:
            place(buf, brass(CHORDS[(bar + 1) % 4], 0.12), t + 0.25, 0.22)

    # transition hits: tom pickup, then brass chord + crash on the cut
    for i, c in enumerate(CUTS):
        ch = CHORDS[i % 4]
        for k, off in enumerate((-0.375, -0.25, -0.125)):
            place(buf, timp(41 - k * 2), c + off, 0.35)
        place(buf, brass(ch, 0.55, bright=1.6), c, 0.5)
        place(buf, CR, c, 0.22)
        place(buf, K, c, 0.8)

    # ending: final hit and ring-out
    place(buf, brass(CHORDS[0], 0.12), 58.75, 0.4)
    place(buf, brass(CHORDS[0], 1.15, bright=2.0), 59.0, 0.6)
    place(buf, timp(34), 59.0, 0.7)
    place(buf, CR, 59.0, 0.3)

    # gentle fade over the last 0.4 s so it closes on the end card
    n = len(buf)
    fade = np.ones(n)
    a = int(59.6 * SR)
    fade[a:] = np.linspace(1, 0, n - a)
    buf *= fade[:, None]
    # high-pass the mud below 60 Hz, keep the bed audible on phone speakers
    for ch in range(2):
        buf[:, ch] = fft_filter(buf[:, ch], lo=55)
    buf *= 0.89 / np.max(np.abs(buf))
    return buf

# ---------- synthesised effects ----------
def sfx_thup():
    t = t_axis(0.18)
    body = np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t / 0.05) + 70) / SR) * np.exp(-t / 0.04)
    paper = fft_filter(rng.standard_normal(len(t)), lo=500, hi=4000) * np.exp(-t / 0.025)
    x = body + 0.6 * paper / np.max(np.abs(paper))
    return x / np.max(np.abs(x))

def sfx_scratch():
    t = t_axis(0.42)
    x = fft_filter(rng.standard_normal(len(t)), lo=2500, hi=9000)
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 38 * t + 3 * np.sin(2 * np.pi * 5 * t))
    x *= am * env_adsr(len(t), a=0.02, d=0.05, s=0.9, r=0.08)
    return x / np.max(np.abs(x))

def sfx_cheer():
    d = 2.8
    t = t_axis(d)
    out = np.zeros(len(t))
    swell = np.clip(t / 0.25, 0, 1) * np.exp(-np.maximum(t - 0.6, 0) / 1.1)
    for v in range(36):
        f1 = rng.uniform(450, 900)
        voice = fft_filter(rng.standard_normal(len(t)), lo=f1 * 0.7, hi=f1 * 2.6)
        rate = rng.uniform(3, 7)
        mod = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + rng.uniform(0, 6.28))
        start = rng.uniform(0, 0.3)
        out += voice * mod * (t > start)
    claps = np.zeros(len(t))
    for c in range(70):
        at = rng.uniform(0.05, 2.3)
        cl = fft_filter(rng.standard_normal(int(0.03 * SR)), lo=900, hi=5000) * np.exp(-t_axis(0.03) / 0.006)
        a = int(at * SR)
        claps[a : a + len(cl)] += cl * rng.uniform(0.4, 1.0)
    out = out / np.max(np.abs(out)) + 0.6 * claps / np.max(np.abs(claps))
    out *= swell
    return out / np.max(np.abs(out))

def sfx_shutter():
    t = t_axis(0.22)
    x = np.zeros(len(t))
    for at, g in ((0.0, 1.0), (0.07, 0.7)):
        click = fft_filter(rng.standard_normal(int(0.025 * SR)), lo=1500, hi=10000)
        click *= np.exp(-t_axis(0.025) / 0.004)
        a = int(at * SR)
        x[a : a + len(click)] += click * g
    return x / np.max(np.abs(x))

def sfx_buzzer():
    t = t_axis(0.65)
    sq = np.sign(np.sin(2 * np.pi * 110 * t)) + 0.6 * np.sign(np.sin(2 * np.pi * 116.5 * t))
    x = fft_filter(sq, hi=3000) * env_adsr(len(t), a=0.005, d=0.02, s=1.0, r=0.06)
    return x / np.max(np.abs(x))

BUNDLED = Path.home() / ".claude/skills/media-use/audio/assets/sfx"

def write_sfx():
    out = ROOT / "assets/sfx"
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in [("thup", sfx_thup), ("tally-scratch", sfx_scratch), ("cheer", sfx_cheer),
                     ("shutter", sfx_shutter), ("buzzer", sfx_buzzer)]:
        sf.write(out / f"{name}.wav", (fn() * 0.89).astype(np.float32), SR, subtype="PCM_16")
    for name in ["whoosh", "whoosh-short", "ping", "pop", "sparkle", "typing", "key-press",
                 "impact-bass-1", "notification"]:
        src = BUNDLED / f"{name}.mp3"
        if src.exists():
            shutil.copy(src, out / f"{name}.mp3")

# ---------- cue sheet: (time, file, volume, id) ----------
def cues():
    c = []
    def add(t, f, v):
        c.append((round(t, 3), f, v))
    # hook
    add(0.30, "whoosh-short.mp3", 0.45)
    for t in (1.55, 1.95, 2.35, 2.70):
        add(t, "thup.wav", 0.55)
    # ticker-slide transition into the old way
    add(3.25, "whoosh.mp3", 0.45)
    add(4.30, "typing.mp3", 0.30)
    add(6.00, "typing.mp3", 0.28)
    add(7.40, "typing.mp3", 0.28)
    for t in (5.4, 6.6, 7.8, 9.0, 10.2, 11.4):
        add(t, "tally-scratch.wav", 0.40)
        add(t + 0.45, "thup.wav", 0.42)
    add(9.75, "pop.mp3", 0.45)
    add(12.15, "key-press.mp3", 0.2)
    # news swoosh + Counter
    add(12.95, "whoosh-short.mp3", 0.55)
    add(13.35, "whoosh.mp3", 0.35)
    add(14.30, "typing.mp3", 0.28)
    add(16.95, "sparkle.mp3", 0.40)
    for t in (18.55, 19.05, 19.55):
        add(t, "ping.mp3", 0.45)
    add(20.60, "pop.mp3", 0.50)
    # bar-chart wipe + winner
    add(23.95, "whoosh-short.mp3", 0.50)
    add(25.30, "typing.mp3", 0.28)
    add(26.55, "ping.mp3", 0.45)
    add(27.00, "shutter.wav", 0.60)
    add(27.05, "pop.mp3", 0.55)
    add(27.10, "cheer.wav", 0.40)
    add(28.10, "typing.mp3", 0.28)
    add(29.05, "ping.mp3", 0.45)
    add(30.25, "pop.mp3", 0.40)
    add(30.55, "pop.mp3", 0.35)
    # ballot-box drop + strings
    add(35.95, "whoosh-short.mp3", 0.45)
    add(36.25, "thup.wav", 0.75)
    add(37.10, "typing.mp3", 0.28)
    for t in (39.6, 39.9, 40.2, 40.5, 40.8, 41.1):
        add(t, "thup.wav", 0.45)
    add(41.45, "ping.mp3", 0.45)
    add(42.85, "pop.mp3", 0.45)
    # swoosh + bonus
    add(45.95, "whoosh.mp3", 0.45)
    add(47.05, "typing.mp3", 0.28)
    add(47.95, "ping.mp3", 0.45)
    add(48.35, "typing.mp3", 0.28)
    add(49.15, "buzzer.wav", 0.35)
    add(49.95, "ping.mp3", 0.50)
    add(50.90, "notification.mp3", 0.35)
    add(52.40, "sparkle.mp3", 0.35)
    # flash + outro
    add(54.40, "shutter.wav", 0.60)
    add(54.45, "impact-bass-1.mp3", 0.45)
    add(54.70, "pop.mp3", 0.50)
    add(54.75, "cheer.wav", 0.32)
    add(55.20, "pop.mp3", 0.40)
    add(56.40, "whoosh-short.mp3", 0.40)
    add(57.20, "typing.mp3", 0.22)
    add(57.70, "pop.mp3", 0.30)
    return c

def music_lane():
    """Volume lane: 0.24 with no voice, 0.12 under the voice, 60 ms ramps."""
    words = json.loads((ROOT / "assets/vo_words.json").read_text())["phrases"]
    spans = []
    for p in words:
        s, e = p["start"] - 0.08, p["end"] + 0.15
        if spans and s - spans[-1][1] < 0.6:
            spans[-1][1] = e
        else:
            spans.append([s, e])
    pts = [{"t": 0, "v": 0.24}]
    for s, e in spans:
        pts += [{"t": round(max(0, s - 0.06), 3), "v": 0.24}, {"t": round(max(0, s), 3), "v": 0.12},
                {"t": round(e, 3), "v": 0.12}, {"t": round(e + 0.25, 3), "v": 0.24}]
    pts.append({"t": TOTAL, "v": 0.24})
    # drop duplicates / non-increasing times
    clean = []
    for p in pts:
        if clean and p["t"] <= clean[-1]["t"]:
            clean[-1] = p
        else:
            clean.append(p)
    return {"version": 1, "lanes": [{"target": "volume", "points": clean}]}

def write_index(music_src):
    lane = json.dumps(music_lane(), separators=(",", ":")).replace('"', "&quot;")
    lines = [
        f'<audio id="music" class="clip" src="{music_src}" data-start="0" data-duration="60" '
        f'data-track-index="20" data-volume="1" data-fade-out="0.4" data-automation="{lane}"></audio>',
        '<audio id="vo" class="clip" src="assets/audio/vo.wav" data-start="0" data-duration="60" '
        'data-track-index="21" data-volume="1"></audio>',
    ]
    lane_end = []
    for i, (t, f, v) in enumerate(cues()):
        d = round(sf.info(str(ROOT / "assets/sfx" / f)).duration, 3)
        lane = next((k for k, e in enumerate(lane_end) if e <= t), None)
        if lane is None:
            lane = len(lane_end)
            lane_end.append(0)
        lane_end[lane] = t + d
        lines.append(
            f'<audio id="sfx-{i:02d}" class="clip" src="assets/sfx/{f}" data-start="{t}" '
            f'data-duration="{d}" data-track-index="{22 + lane}" data-volume="{v}"></audio>'
        )
    html = (ROOT / "index.html").read_text()
    block = "\n      ".join(lines)
    html = re.sub(r"(<!-- AUDIO:BEGIN -->)(.*?)(<!-- AUDIO:END -->)",
                  lambda m: f"{m.group(1)}\n      {block}\n      {m.group(3)}", html, flags=re.S)
    (ROOT / "index.html").write_text(html)

if __name__ == "__main__":
    write_sfx()
    user_track = ROOT / "assets/music.mp3"
    if user_track.exists():
        music_src = "assets/music.mp3"
    else:
        sf.write(ROOT / "assets/audio/music.wav", build_music().astype(np.float32), SR, subtype="PCM_16")
        music_src = "assets/audio/music.wav"
    write_index(music_src)
    print("music:", music_src, "| cues:", len(cues()))
