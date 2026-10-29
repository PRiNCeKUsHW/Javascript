"""Turn a lesson script (YAML) into narration audio, captions and a Remotion timeline.

usage:
  python tools/build_lesson.py 1 3          # module 1, lesson 3
  python tools/build_lesson.py 1 all        # every lesson of module 1
  python tools/build_lesson.py 1 3 --no-tts # fail instead of synthesizing narration that is not cached

outputs (per lesson):
  studio/public/mNN/lNN/audio.wav        final mix: narration + music bed + sound effects, -16 LUFS
  studio/src/data/mNN-lNN.json           timeline the Remotion composition renders
  modules/<module>/captions/lesson-NN.srt
  modules/<module>/audio/lesson-NN-narration.wav
"""
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Token

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio"
VENV_BIN = ROOT / ".venv" / ("Scripts" if os.name == "nt" else "bin")  # Windows venvs use Scripts/
VENV_PY = VENV_BIN / ("python.exe" if os.name == "nt" else "python")
TTS_CACHE = ROOT / "shared/tts_cache"
KOKORO = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache/hyperframes/tts"))  # models/ + voices/
SR = 24000
FPS = 60
VOICE, LANG, SPEED = "am_michael", "en-us", 1.0

LEAD, TAIL, GAP = 0.7, 0.6, 0.35       # seconds before the first beat, after the last, between beats
SENTENCE_GAP = 0.22
ENVELOPE_HZ = 30

# words the phonemiser gets wrong, spelled the way they are said (display text is untouched)
SAY_AS = {
    "JSON": "Jason", "venv": "vee-env", ".venv": "dot vee-env", "pip": "pip", "httpx": "H T T P X",
    "CLI": "C L I", "API": "A P I", "APIs": "A P Is", "LLM": "L L M", "LLMs": "L L Ms", "argparse": "arg-parse",
    "dict": "dict", "dicts": "dicts", "kwargs": "keyword args", "async": "a-sync", "asyncio": "a-sync I O",
    "pytest": "pie-test", "PyPI": "pie P I", "stdin": "standard in", "stdout": "standard out",
    "stderr": "standard error", "UTF-8": "U T F eight", "ISO": "I S O", "RAG": "rag", "MCP": "M C P",
    "SQLite": "sequel-lite", "PostgreSQL": "postgres", "YAML": "yammel", "URL": "U R L", "URLs": "U R Ls",
    "HTTP": "H T T P", "f-string": "F-string", "f-strings": "F-strings", "repr": "repper", "VS Code": "V S Code",
    "macOS": "mac O S", "TypeError": "type error", "KeyError": "key error", "ValueError": "value error",
    "FileNotFoundError": "file not found error", "JSONDecodeError": "Jason decode error",
    "ZeroDivisionError": "zero division error", "IndexError": "index error", "AttributeError": "attribute error",
    "NameError": "name error", "ToolkitError": "toolkit error", "ValidationError": "validation error",
    "UsageRecord": "usage record", "mypy": "my-pie", "Pydantic": "pie-dantic", "LangGraph": "lang graph",
    "FastAPI": "fast A P I", "isinstance": "is instance", "enumerate": "ee-numerate", "init": "init",
    "OOP": "O O P", "PATH": "path", "env": "env", "CPU": "C P U", "I/O": "I O", "GPU": "G P U",
}

# pygments token -> CSS class used by the CodePanel component
TOKEN_CLASSES = [
    (Comment, "com"), (String.Doc, "com"), (String, "str"), (Number, "num"), (Keyword.Constant, "con"),
    (Keyword, "kw"), (Name.Builtin.Pseudo, "con"), (Name.Builtin, "bi"), (Name.Function, "fn"),
    (Name.Class, "cls"), (Name.Decorator, "dec"), (Name.Exception, "cls"), (Operator.Word, "kw"),
    (Operator, "op"), (Token.Punctuation, "pun"),
]

_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO / "models/kokoro-v1.0.onnx"), str(KOKORO / "voices/voices-v1.0.bin"))
    return _kokoro


def say_as(text):
    text = text.replace("`", "")
    for k, v in SAY_AS.items():
        text = re.sub(rf"(?<![\w.-]){re.escape(k)}(?![\w-])", v, text)
    return text


def display(text):
    """Caption text: drop markdown backticks/asterisks, keep everything else."""
    return re.sub(r"[`*]", "", text).strip()


def sentences(text):
    text = " ".join(text.split())
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(`])", text) if s.strip()]


def trim(x, thresh=0.008):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.08 * SR)]


def tts(sentence, allow_new):
    spoken = say_as(sentence)
    key = hashlib.sha1(f"{VOICE}|{LANG}|{SPEED}|{spoken}".encode()).hexdigest()[:16]
    path = TTS_CACHE / f"{key}.wav"
    if path.exists():
        return sf.read(path, dtype="float32")[0]
    if not allow_new:
        raise SystemExit(f"narration not cached: {sentence[:70]}")
    audio, sr = kokoro().create(spoken, voice=VOICE, speed=SPEED, lang=LANG)
    assert sr == SR
    audio = trim(np.asarray(audio, dtype=np.float32))
    TTS_CACHE.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, SR, subtype="FLOAT")
    return audio


# ---------------------------------------------------------------- code + terminal helpers
def parse_range(spec, total):
    """'3-5,9' -> [3, 4, 5, 9] (1-based)."""
    if spec in (None, "", "all"):
        return list(range(1, total + 1))
    out = []
    for part in str(spec).split(","):
        a, _, b = part.strip().partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def highlight(code, lang):
    lexer = get_lexer_by_name(lang, stripnl=False, ensurenl=False)
    lines, current = [], []
    for ttype, value in lex(code, lexer):
        cls = next((c for t, c in TOKEN_CLASSES if ttype in t), "")
        parts = value.split("\n")
        for i, part in enumerate(parts):
            if i:
                lines.append(current)
                current = []
            if part:
                if current and current[-1][1] == cls:
                    current[-1][0] += part
                else:
                    current.append([part, cls])
    if current:
        lines.append(current)
    return lines


def load_code(scene, module_dir):
    if "file" in scene:
        text = (module_dir / scene["file"]).read_text(encoding="utf-8")
        all_lines = text.splitlines()
        if "lines" in scene:
            a, b = (int(x) for x in str(scene["lines"]).split("-"))
            all_lines = all_lines[a - 1: b]
            scene.setdefault("first_line", a)
        code = "\n".join(all_lines)
    else:
        code = scene["code"].rstrip("\n")
    return code


def posix_path(path):
    """How bash prints a path: unchanged on Linux/macOS, /c/Users/... under Git Bash."""
    path = Path(path)
    if os.name != "nt":
        return str(path)
    return "/" + path.drive[0].lower() + path.as_posix()[len(path.drive):]


def shell_env(env):
    """Windows only: Git Bash has no python3 (it is the Microsoft Store stub), so add a shim
    that runs whichever `python` is first on PATH, exactly as python3 does in a Linux venv."""
    if os.name != "nt":
        return env
    shim = ROOT / ".venv/shim"
    shim.mkdir(parents=True, exist_ok=True)
    (shim / "python3").write_text('#!/bin/sh\nexec python "$@"\n', newline="\n")
    return dict(env, PATH=f"{shim}{os.pathsep}{env['PATH']}")  # ahead of the WindowsApps stub


def run_terminal(entry, cwd, env):
    """Run the real command and capture what a terminal would show (stdout + stderr interleaved)."""
    if "out" in entry:
        return entry["out"].rstrip("\n").split("\n") if entry["out"] else []
    command = entry.get("run", entry["cmd"])
    if os.name == "nt":  # Git Bash: a Windows venv keeps its scripts in Scripts/, not bin/
        command = command.replace(".venv/bin/", ".venv/Scripts/")
    proc = subprocess.run(["bash", "-c", command], cwd=cwd, env=env, capture_output=False,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
    expected = entry.get("exit", 0)
    if proc.returncode != expected:
        raise SystemExit(f"terminal command {command!r} exited {proc.returncode}, expected {expected}:\n{proc.stdout}")
    lines = proc.stdout.rstrip("\n").split("\n") if proc.stdout.strip() else []
    return pick_lines(lines, entry.get("keep"))


def pick_lines(lines, spec):
    """'1-4,-2' keeps lines 1-4 and the last two (negative = from the end)."""
    if spec is None:
        return lines
    picked = []
    for part in str(spec).split(","):
        if part.startswith("-"):
            picked += lines[int(part):]
        else:
            picked += [lines[i - 1] for i in parse_range(part, len(lines)) if i <= len(lines)]
    return picked


def run_repl(steps, cwd, env):
    """Run every step's statements in ONE interpreter session, like typing at the >>> prompt."""
    statements = [line for step in steps for line in step["cmd"].strip("\n").split("\n")]
    proc = subprocess.run([str(VENV_PY), str(ROOT / "tools/repl_capture.py")],
                          input=json.dumps(statements), cwd=cwd, env=env, capture_output=True, text=True,
                          timeout=120)
    if proc.returncode:
        raise SystemExit(f"repl capture failed:\n{proc.stderr}")
    outputs = iter(json.loads(proc.stdout))
    for step in steps:
        step["pairs"] = []
        for line in step["cmd"].strip("\n").split("\n"):
            out = next(outputs).rstrip("\n")
            lines = out.split("\n") if out else []
            step["pairs"].append({"cmd": line, "out": pick_lines(lines, step.get("keep"))})


# ---------------------------------------------------------------- scene -> beats
def scene_beats(scene):
    """Every scene becomes an ordered list of beats; beat i drives the i-th visual step."""
    kind = scene["type"]
    lists = {"bullets": "items", "recap": "items", "cards": "cards", "code": "steps", "terminal": "steps",
             "diagram": "steps", "compare": "steps", "links": "items", "objectives": "items", "steps": "items",
             "callout": "items"}
    if kind == "quiz":
        return [{"say": scene["say_question"], "kind": "intro"},
                {"pause": scene.get("think", 5), "countdown": True, "kind": "think"},
                {"say": scene["say_answer"], "sfx": "chime", "kind": "reveal"}]
    beats = []
    if scene.get("say"):
        beats.append({"say": scene["say"], "kind": "intro"})
    for item in scene.get(lists.get(kind, ""), []) or []:
        beats.append({"say": item.get("say", ""), "pause": item.get("pause"), "kind": "item"})
    if scene.get("outro"):
        beats.append({"say": scene["outro"], "kind": "outro"})
    return beats or [{"pause": 2, "kind": "intro"}]


def build_scene(scene, module_dir, env):
    kind = scene["type"]
    props = {k: v for k, v in scene.items() if k not in ("say", "outro", "say_question", "say_answer")}
    if kind == "code":
        code = load_code(scene, module_dir)
        props["tokens"] = highlight(code, scene.get("lang", "python"))
        props["first_line"] = scene.get("first_line", 1)
        n = len(props["tokens"])
        offset = props["first_line"] - 1      # step line numbers are file line numbers
        for step in props.get("steps", []):
            hl = parse_range(step.get("lines"), n + offset) if step.get("lines") else []
            step["hl"] = [i - offset for i in hl if 0 < i - offset <= n]
            if "upto" in step:
                step["upto"] -= offset
            step.pop("say", None)
        props.pop("code", None)
    elif kind == "compare":
        for side in ("left", "right"):
            if "code" in props[side]:
                props[side]["tokens"] = highlight(props[side]["code"].rstrip("\n"), props[side].get("lang", "python"))
        for step in props.get("steps", []):
            step.pop("say", None)
    elif kind == "terminal":
        cwd = module_dir / scene.get("cwd", ".")
        if scene.get("cwd") == "tmp":           # a fresh, empty folder shown to viewers as `alias`
            cwd = Path(tempfile.mkdtemp(prefix="term-"))
        alias = scene.get("alias")
        if scene.get("repl"):
            run_repl(props["steps"], cwd, env)
        for step in props["steps"]:
            if not scene.get("repl"):
                out = run_terminal(step, cwd, env) if step.get("cmd") else []
                step["pairs"] = [{"cmd": step.get("cmd", ""), "out": out}] if step.get("cmd") else []
            if alias:
                for pair in step["pairs"]:
                    pair["out"] = [line.replace(str(cwd), alias).replace(posix_path(cwd), alias)
                                   .replace(f"/tmp/{cwd.name}", alias)  # Git Bash mounts %TEMP% at /tmp
                                   for line in pair["out"]]
            for key in ("say", "run", "keep", "exit", "cmd"):
                step.pop(key, None)
    if isinstance(props.get("aside"), dict) and "code" in props["aside"]:
        props["aside"]["tokens"] = highlight(props["aside"]["code"].rstrip("\n"), props["aside"].get("lang", "python"))
    if kind not in ("code", "compare", "terminal"):
        for key in ("items", "cards", "steps"):
            for item in props.get(key, []) or []:
                item.pop("say", None)
    return props


# ---------------------------------------------------------------- audio mix
def load_mono(path):
    x, sr = sf.read(path, dtype="float32")
    assert sr == SR, path
    return x if x.ndim == 1 else x.mean(axis=1)


def mix(narration, events, total_samples):
    out = np.zeros(total_samples, dtype=np.float32)
    out[: len(narration)] += narration
    for name, at, gain in events:
        s = load_mono(ROOT / f"shared/audio/{name}.wav") * gain
        a = int(at * SR)
        out[a: a + len(s)] += s[: max(0, total_samples - a)]
    bed = load_mono(ROOT / "shared/audio/music_bed.wav")
    bed = np.tile(bed, total_samples // len(bed) + 1)[:total_samples]
    # duck the bed under speech: follow the narration envelope with a slow attack/release
    level = np.abs(narration)
    level = np.pad(level, (0, total_samples - len(level)))
    win = int(0.25 * SR)
    smooth = np.convolve(level, np.ones(win) / win, mode="same")
    speaking = np.clip(smooth / 0.02, 0, 1)
    gain = 0.10 - 0.055 * speaking            # about -20 dB under speech, -14 dB in pauses (pre-normalisation)
    fade = np.ones(total_samples)
    f = int(2.5 * SR)
    fade[:f] = np.linspace(0, 1, f)
    fade[-f:] = np.linspace(1, 0, f)
    out += bed * gain * fade
    return out


def envelope(narration, total_frames):
    hop = SR // ENVELOPE_HZ
    n = int(np.ceil(total_frames / FPS * ENVELOPE_HZ))
    padded = np.pad(narration, (0, max(0, n * hop - len(narration))))[: n * hop]
    rms = np.sqrt((padded.reshape(n, hop) ** 2).mean(axis=1))
    return [round(float(v), 3) for v in np.clip(rms / 0.12, 0, 1)]


# ---------------------------------------------------------------- captions
def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def caption_chunks(text, start, end, max_chars=84):
    """Split a long sentence into caption-sized pieces, timed by character share."""
    words = text.split()
    chunks, current = [], []
    for w in words:
        if current and len(" ".join(current + [w])) > max_chars:
            chunks.append(" ".join(current))
            current = []
        current.append(w)
    if current:
        chunks.append(" ".join(current))
    total = sum(len(c) for c in chunks)
    out, t = [], start
    for c in chunks:
        d = (end - start) * len(c) / total
        out.append((t, t + d, c))
        t += d
    return out


def wrap_two_lines(text, width=42):
    if len(text) <= width:
        return text
    words, line1 = text.split(), ""
    for i, w in enumerate(words):
        if len(line1) + len(w) + 1 > len(text) / 2 and line1:
            return line1.strip() + "\n" + " ".join(words[i:])
        line1 += " " + w
    return text


# ---------------------------------------------------------------- build
def module_dir_for(module):
    matches = sorted((ROOT / "modules").glob(f"module-{module:02d}-*"))
    if not matches:
        raise SystemExit(f"no folder for module {module}")
    return matches[0]


def build(module, lesson, allow_new=True):
    mdir = module_dir_for(module)
    spec = yaml.safe_load((mdir / f"scripts/lesson-{lesson:02d}.yaml").read_text(encoding="utf-8"))
    env = dict(os.environ, PATH=f"{VENV_BIN}{os.pathsep}{os.environ['PATH']}", PYTHONDONTWRITEBYTECODE="1",
               VIRTUAL_ENV=str(ROOT / ".venv"), COLUMNS="88", NO_COLOR="1")
    env = shell_env(env)
    # recordings must be reproducible and never use a real key or proxy
    for name in ("TOOLKIT_CURRENCY", "TOOLKIT_PRICES_FILE", "ANTHROPIC_API_KEY",
                 "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "STUDY_MODEL",
                 "STUDY_BUDGET_USD", "STUDY_MAX_RETRIES", "STUDY_FAKE_FAIL"):
        env.pop(name, None)

    pieces, events, captions, scenes, chapters = [], [], [], [], []
    t = 0.0
    total_scenes = len(spec["scenes"])
    for si, scene in enumerate(spec["scenes"]):
        props = build_scene(copy.deepcopy(scene), mdir, env)
        scene_start = t
        if scene.get("chapter"):
            chapters.append({"t": round(scene_start, 3), "title": scene["chapter"]})
        if scene["type"] in ("title", "section"):
            events.append(("sting", scene_start + 0.15, 0.35))
        elif si:
            events.append(("whoosh", scene_start, 0.18))
        t += LEAD
        beats = []
        for bi, beat in enumerate(scene_beats(scene)):
            b_start = t
            if beat.get("say"):
                for s in sentences(beat["say"]):
                    audio = tts(s, allow_new)
                    pieces.append((t, audio))
                    for c in caption_chunks(display(s), t, t + len(audio) / SR):
                        captions.append(c)
                    t += len(audio) / SR + SENTENCE_GAP
                t -= SENTENCE_GAP
            if beat.get("pause"):
                t += float(beat["pause"])
            if beat.get("sfx"):
                events.append((beat["sfx"], b_start, 0.3))
            elif bi and scene["type"] in ("bullets", "cards", "recap", "objectives", "diagram", "steps"):
                events.append(("tick", b_start, 0.12))
            t += GAP
            beats.append({"from": round((b_start - scene_start) * FPS), "kind": beat["kind"]})
        t += TAIL - GAP
        scenes.append({"from": round(scene_start * FPS), "duration": round((t - scene_start) * FPS),
                       "beats": beats, **props})

    total_samples = int(np.ceil(t * SR))
    narration = np.zeros(total_samples, dtype=np.float32)
    for start, audio in pieces:
        a = int(start * SR)
        narration[a: a + len(audio)] += audio[: total_samples - a]
    # keep scene boundaries exact in frames
    total_frames = scenes[-1]["from"] + scenes[-1]["duration"]
    for a, b in zip(scenes, scenes[1:]):
        a["duration"] = b["from"] - a["from"]

    pub = STUDIO / f"public/m{module:02d}/l{lesson:02d}"
    pub.mkdir(parents=True, exist_ok=True)
    (mdir / "audio").mkdir(exist_ok=True)
    (mdir / "captions").mkdir(exist_ok=True)
    sf.write(mdir / f"audio/lesson-{lesson:02d}-narration.wav", narration, SR, subtype="PCM_16")
    raw = pub / "mix_raw.wav"
    sf.write(raw, mix(narration, events, total_samples), SR, subtype="FLOAT")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", str(pub / "audio.wav")], check=True)
    raw.unlink()

    srt = "\n".join(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{wrap_two_lines(text)}\n"
                    for i, (a, b, text) in enumerate(captions, 1))
    (mdir / f"captions/lesson-{lesson:02d}.srt").write_text(srt, encoding="utf-8")

    data = {
        "id": f"m{module:02d}-l{lesson:02d}", "module": module, "lesson": lesson,
        "moduleTitle": spec["module_title"], "title": spec["title"], "fps": FPS,
        "durationInFrames": total_frames, "audio": f"m{module:02d}/l{lesson:02d}/audio.wav",
        "envelope": envelope(narration, total_frames), "envelopeHz": ENVELOPE_HZ,
        "chapters": chapters, "scenes": scenes,
        "captions": [{"from": round(a * FPS), "to": round(b * FPS), "text": text} for a, b, text in captions],
    }
    (STUDIO / "src/data").mkdir(parents=True, exist_ok=True)
    (STUDIO / f"src/data/m{module:02d}-l{lesson:02d}.json").write_text(json.dumps(data), encoding="utf-8")
    register_compositions()
    m, s = divmod(int(t), 60)
    print(f"m{module:02d} lesson {lesson}: {len(scenes)} scenes, {m}:{s:02d}, {len(captions)} captions")
    return data


def register_compositions():
    """Write src/lessons.ts so Root.tsx registers one composition per built lesson."""
    files = sorted((STUDIO / "src/data").glob("m??-l??.json"))
    lines = [f'import {re.sub(r"[^a-z0-9]", "_", f.stem)} from "./data/{f.name}";' for f in files]
    names = ", ".join(re.sub(r"[^a-z0-9]", "_", f.stem) for f in files)
    lines += ["", "// generated by tools/build_lesson.py", f"export const LESSONS = [{names}];", ""]
    (STUDIO / "src/lessons.ts").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    module, which = int(sys.argv[1]), sys.argv[2]
    allow = "--no-tts" not in sys.argv
    if which == "all":
        for p in sorted((module_dir_for(module) / "scripts").glob("lesson-*.yaml")):
            build(module, int(p.stem.split("-")[1]), allow)
    else:
        build(module, int(which), allow)
