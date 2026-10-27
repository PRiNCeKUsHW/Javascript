"""Build the voiceover track and word timings from tools/vo_script.json.

Each phrase is synthesised separately with Kokoro (the model `hyperframes tts`
downloads), trimmed, and placed back to back from its scene's start time.
Word timings inside a phrase are spread by letter count, which is close enough
for 2-3 word caption groups.

  python tools/build_vo.py            # writes assets/audio/vo.wav + assets/vo_words.json
  python tools/build_vo.py --measure  # only prints phrase lengths and scene fit
"""
import json, re, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path.home() / ".cache/hyperframes/tts"
SR_OUT = 48000
TOTAL = 60.0
GAP = 0.06  # breath between phrases

spec = json.loads((ROOT / "tools/vo_script.json").read_text())
k = Kokoro(str(CACHE / "models/kokoro-v1.0.onnx"), str(CACHE / "voices/voices-v1.0.bin"))

def trim(x, sr, thresh=0.012):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.015 * sr))
    b = min(len(x), idx[-1] + int(0.04 * sr))
    return x[a:b]

def resample(x, sr_in, sr_out):
    n = int(round(len(x) * sr_out / sr_in))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)

measure = "--measure" in sys.argv
track = np.zeros(int(TOTAL * SR_OUT), dtype=np.float32)
words, phrases_out = [], []
scenes = spec["scenes"]
for si, sc in enumerate(scenes):
    t = sc["start"]
    limit = scenes[si + 1]["start"] if si + 1 < len(scenes) else TOTAL
    speed = sc.get("speed", spec["speed"])
    for spoken, shown in sc["phrases"]:
        audio, sr = k.create(spoken, voice=spec["voice"], speed=speed, lang=spec["lang"])
        audio = resample(trim(np.asarray(audio, dtype=np.float32), sr), sr, SR_OUT)
        dur = len(audio) / SR_OUT
        phrases_out.append({"scene": sc["id"], "text": shown, "start": round(t, 3), "end": round(t + dur, 3)})
        if not measure:
            a = int(t * SR_OUT)
            seg = audio[: max(0, len(track) - a)]
            track[a : a + len(seg)] += seg
            toks = shown.split()
            w = np.array([len(re.sub(r"[^\w=]", "", x)) + 2.0 for x in toks])
            edges = t + np.concatenate([[0], np.cumsum(w)]) / w.sum() * dur
            for i, tok in enumerate(toks):
                words.append({"id": f"w{len(words)}", "text": tok, "start": round(float(edges[i]), 3),
                              "end": round(float(edges[i + 1]), 3), "scene": sc["id"]})
        t += dur + GAP
    end = t - GAP
    flag = "OK" if end <= limit - 0.05 else f"OVER by {end - limit + 0.05:.2f}s"
    print(f"{sc['id']:8s} {sc['start']:6.2f} -> {end:6.2f}  (next {limit:5.2f})  {flag}")

if not measure:
    peak = np.max(np.abs(track))
    track *= 0.89 / peak  # about -1 dBFS
    (ROOT / "assets/audio").mkdir(parents=True, exist_ok=True)
    sf.write(ROOT / "assets/audio/vo.wav", track, SR_OUT, subtype="PCM_16")
    (ROOT / "assets/vo_words.json").write_text(json.dumps({"phrases": phrases_out, "words": words}, indent=1))
    print("wrote assets/audio/vo.wav and assets/vo_words.json:", len(words), "words")
