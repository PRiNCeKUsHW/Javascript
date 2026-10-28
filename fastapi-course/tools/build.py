"""Build one chapter of the course into a HyperFrames project.

  python tools/build.py 1          # content/ch01.md -> build/ch01/
  python tools/build.py 1 --no-tts # reuse cached narration only (fails on new lines)

Steps: parse the script, synthesise every narration line (cached), lay the lines end to
end, time every on-screen reveal to the start of its line, write the scenes, the voice
track, sound cues and Hinglish subtitles.
Needs: kokoro-onnx, soundfile, numpy, pygments (see README).
"""
import hashlib, html, json, re, shutil, sys
from pathlib import Path

import numpy as np
import soundfile as sf
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

sys.path.insert(0, str(Path(__file__).parent))
from course import parse_chapter, speakable  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TTS_CACHE = ROOT / "build/tts_cache"
KOKORO = Path.home() / ".cache/hyperframes/tts"
SR = 24000

INSTRUCTOR = ("hf_alpha", "hi", 1.05)
INTERVIEWER = ("hm_omega", "en-us", 1.0)

# words the phonemiser gets wrong, spelled the way they are said
SAY_AS = {
    "ASGI": "A S G I", "WSGI": "W S G I", "pytest": "pie test", "Uvicorn": "you-vee-corn",
    "uvicorn": "you-vee-corn", "PyJWT": "pie J W T", "pwdlib": "password lib", "SQLModel": "sequel model",
    "SQLAlchemy": "sequel alchemy", "SQLite": "sequel lite", "PostgreSQL": "postgres", "CRUD": "crud",
    "PATCH": "patch", "kwargs": "keyword arguments", "async": "a-sync", "Gunicorn": "green unicorn",
    "OAuth2": "O auth two", "ORM": "O R M", "UUID": "U U I D", "nginx": "engine x", "Nginx": "engine x",
}

# ---------------------------------------------------------------- narration
_kokoro = None


def kokoro():
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(str(KOKORO / "models/kokoro-v1.0.onnx"), str(KOKORO / "voices/voices-v1.0.bin"))
    return _kokoro


def say_as(text):
    for k, v in SAY_AS.items():
        text = re.sub(rf"(?<![\w-]){re.escape(k)}(?![\w-])", v, text)
    return text


def trim(x, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    return x[max(0, idx[0] - int(0.02 * SR)) : idx[-1] + int(0.06 * SR)]


def tts(text, speaker, allow_new=True):
    voice, lang, speed = speaker
    key = hashlib.sha1(f"{voice}|{lang}|{speed}|{text}".encode()).hexdigest()[:16]
    path = TTS_CACHE / f"{key}.wav"
    if path.exists():
        return sf.read(path, dtype="float32")[0]
    if not allow_new:
        raise SystemExit(f"narration not cached: {text[:60]}")
    parts = [p for p in re.split(r"(?<=[.!?।])\s+", say_as(text)) if p.strip()]
    out = []
    for p in parts:
        audio, sr = kokoro().create(p, voice=voice, speed=speed, lang=lang)
        assert sr == SR
        out.append(trim(np.asarray(audio, dtype=np.float32)))
        out.append(np.zeros(int(0.16 * SR), dtype=np.float32))
    audio = np.concatenate(out[:-1]) if out else np.zeros(int(0.3 * SR), dtype=np.float32)
    TTS_CACHE.mkdir(parents=True, exist_ok=True)
    sf.write(path, audio, SR, subtype="FLOAT")
    return audio


# ---------------------------------------------------------------- markup helpers
def inline(text):
    """Display markup: `code` and **bold**; everything else escaped."""
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`|\*\*([^*]+)\*\*", text):
        out.append(html.escape(text[pos : m.start()]))
        if m.group(1) is not None:
            out.append(f'<span class="ic">{html.escape(m.group(1))}</span>')
        else:
            out.append(f"<b>{html.escape(m.group(2))}</b>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


TOKEN_CLASS = [
    (Token.Comment, "c"), (Token.Literal.String, "s"), (Token.Literal.Number, "n"),
    (Token.Name.Decorator, "d"), (Token.Name.Function, "f"), (Token.Name.Class, "t"),
    (Token.Name.Builtin, "b"), (Token.Keyword, "k"), (Token.Operator.Word, "k"),
    (Token.Generic.Prompt, "k"), (Token.Name.Tag, "f"), (Token.Name.Attribute, "d"),
]


def highlight(code_lines, lang):
    lexer = get_lexer_by_name({"py": "python", "sh": "bash", "shell": "bash", "text": "text"}.get(lang, lang))
    lines = [[]]
    for ttype, value in lexer.get_tokens("\n".join(code_lines)):
        cls = next((c for t, c in TOKEN_CLASS if ttype in t), "")
        for k, chunk in enumerate(value.split("\n")):
            if k:
                lines.append([])
            if chunk:
                esc = html.escape(chunk)
                lines[-1].append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    lines = lines[: len(code_lines)]
    while len(lines) < len(code_lines):
        lines.append([])
    return ["".join(l) or "&#8203;" for l in lines]


def code_metrics(code_lines, max_h, max_w=1560):
    n = max(1, len(code_lines))
    longest = max((len(l) for l in code_lines), default=1)
    lh = min(54, max_h / (n + 0.6))
    fs = min(lh / 1.5, max_w / (max(longest, 20) * 0.6))
    fs = max(26, round(fs))
    return fs, round(fs * 1.5)


# ---------------------------------------------------------------- styles
CSS = """
    @font-face { font-family: "Noto Color Emoji"; src: local("Noto Color Emoji"), local("Apple Color Emoji"), local("Segoe UI Emoji"); }
    #root { position: absolute; inset: 0; overflow: hidden; background: #f4f6f8; }
    .dots { position: absolute; inset: 0; background-image: radial-gradient(#d3dbe4 1.6px, transparent 1.7px);
      background-size: 36px 36px; opacity: 0.6; }
    .emoji { font-family: "Noto Color Emoji", sans-serif; }
    .h { position: absolute; left: 120px; top: 116px; width: 1680px; font-family: "Outfit", sans-serif;
      font-weight: 700; font-size: 58px; line-height: 1.12; color: #0f1b2d; white-space: nowrap; }
    .hbar { position: absolute; left: 120px; top: 194px; width: 96px; height: 8px; border-radius: 4px; background: #05998b; }
    .ic { font-family: "JetBrains Mono", monospace; font-weight: 600; font-size: 0.86em; background: #def3ef;
      color: #04665d; padding: 0.02em 0.26em; border-radius: 8px; }
    b { font-weight: 700; color: #04776c; }
    .list { position: absolute; left: 120px; top: 270px; width: 1660px; }
    .it { display: flex; gap: 30px; align-items: flex-start; margin-bottom: 40px; opacity: 0; }
    .mk { flex: 0 0 24px; height: 24px; margin-top: 21px; border-radius: 6px; background: #05998b; }
    .ck { flex: 0 0 46px; height: 46px; margin-top: 4px; border-radius: 50%; background: #05998b; color: #fff;
      font-family: "Inter", sans-serif; font-weight: 800; font-size: 28px; line-height: 46px; text-align: center; }
    .tx { font-family: "Inter", sans-serif; font-weight: 500; font-size: 46px; line-height: 1.36; color: #0f1b2d; }
    .panel { position: absolute; border-radius: 22px; background: #0e1726; overflow: hidden;
      box-shadow: 0 18px 40px rgba(15, 27, 45, 0.18); }
    .bar { position: absolute; left: 0; right: 0; top: 0; height: 56px; background: #1a2436; }
    .dot { position: absolute; top: 20px; width: 16px; height: 16px; border-radius: 50%; }
    .fname { position: absolute; left: 110px; top: 0; height: 56px; padding: 0 22px; line-height: 56px;
      background: #0e1726; color: #c9d4e3; font-family: "JetBrains Mono", monospace; font-size: 28px; }
    .code { position: absolute; left: 0; right: 0; top: 80px; font-family: "JetBrains Mono", monospace; font-weight: 500; }
    .cl { position: relative; height: var(--lh); line-height: var(--lh); font-size: var(--fs); white-space: pre;
      color: #e5e9f0; padding-left: 108px; clip-path: inset(0 100% 0 0); }
    .cl .ln { position: absolute; left: 0; width: 76px; text-align: right; color: #7a8aa3; }
    .band { position: absolute; left: 0; right: 0; top: 80px; height: var(--lh); background: rgba(5, 153, 139, 0.24);
      border-left: 7px solid #19c2b0; opacity: 0; transform-origin: 50% 0; }
    .k { color: #d19bf5; } .s { color: #b5e08c; } .c { color: #7d8ba1; font-style: italic; } .n { color: #f7a26b; }
    .d { color: #ffcf6b; } .f { color: #7fb2ff; } .t { color: #ffcf6b; } .b { color: #6fd8f0; }
    .tl { height: var(--lh); line-height: var(--lh); font-size: var(--fs); white-space: pre; color: #a9b6c8; padding-left: 40px; }
    .tl.cmd { color: #f1f5f9; clip-path: inset(0 100% 0 0); }
    .tl.cmd::before { content: "$ "; color: #19c2b0; }
    .tl.cmd.cont::before { content: "  "; }
    .tl.out { opacity: 0; }
    .pill { position: absolute; height: 52px; padding: 0 22px; border-radius: 26px; font-family: "Inter", sans-serif;
      font-weight: 800; font-size: 28px; letter-spacing: 0.04em; line-height: 52px; color: #ffffff; white-space: nowrap; }
"""


def scene_html(sid, css, body, js):
    return f"""<template>
  <style>{CSS}{css}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
    <div class="dots"></div>
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
"""


def heading(sid, text, top=116):
    return (f'    <div id="{sid}-h" class="h" style="top:{top}px">{inline(text)}</div>\n'
            f'    <div id="{sid}-hb" class="hbar" style="top:{top + 78}px"></div>')


def heading_js(sid):
    return (f'    tl.fromTo("#{sid}-h", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, 0.05);\n'
            f'    tl.fromTo("#{sid}-hb", {{ scaleX: 0, transformOrigin: "0 50%" }}, {{ scaleX: 1, duration: 0.4, ease: "power3.out" }}, 0.2);')


def code_panel(sid, code_lines, lang, fname, left, top, width, height):
    fs, lh = code_metrics(code_lines, height - 110, width - 160)
    hl = highlight(code_lines, lang)
    rows = "\n".join(
        f'        <div id="{sid}-l{i + 1}" class="cl"><span class="ln">{i + 1}</span>{h}</div>'
        for i, h in enumerate(hl))
    return f"""    <div id="{sid}-panel" class="panel" style="left:{left}px;top:{top}px;width:{width}px;height:{height}px;--fs:{fs}px;--lh:{lh}px">
      <div class="bar"><div class="dot" style="left:24px;background:#ff5f57"></div><div class="dot" style="left:50px;background:#febc2e"></div><div class="dot" style="left:76px;background:#28c840"></div>
        <div class="fname">{html.escape(fname)}</div></div>
      <div id="{sid}-band" class="band"></div>
      <div class="code">
{rows}
      </div>
    </div>""", lh


def reveal_lines_js(sid, lines, t, stagger=0.06):
    js = []
    for k, ln in enumerate(lines):
        js.append(f'    tl.fromTo("#{sid}-l{ln}", {{ clipPath: "inset(0 100% 0 0)" }}, '
                  f'{{ clipPath: "inset(0 0% 0 0)", duration: 0.3, ease: "steps(16)" }}, {t + k * stagger:.3f});')
    return js


def item_js(sid, idx, t, prev, marker=".mk"):
    js = [f'    tl.fromTo("#{sid}-i{idx}", {{ opacity: 0, x: -36 }}, {{ opacity: 1, x: 0, duration: 0.36, ease: "power3.out" }}, {t:.3f});']
    if prev is not None:
        js.append(f'    tl.to("#{sid}-i{prev} .tx", {{ color: "#6b7a8c", duration: 0.3 }}, {t:.3f});')
    return js


# ---------------------------------------------------------------- scene builders
LEVEL_COL = {"junior": "#2f9e44", "mid": "#e08e0b", "senior": "#e5484d"}
NUM_HI = ["एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ"]


def plan_scene(scene, meta, practice_n, interview_n):
    """Return (clips, duration, layout) where clips are [(t, text, speaker, beat_index)]."""
    clips, t = [], 0.6
    kind = scene["type"]

    def add(text, speaker, bi):
        nonlocal t
        audio = tts(text, speaker)
        clips.append({"t": round(t, 3), "text": text, "speaker": speaker, "beat": bi, "audio": audio})
        t += len(audio) / SR + 0.32

    if kind == "practice":
        n = practice_n
        q = scene["qsay"] or f"सवाल नंबर {NUM_HI[n - 1]}. {speakable(scene['q'])}"
        if n == 1:
            q += " Video pause कीजिए और पहले खुद try कीजिए।"
        add(q, INSTRUCTOR, "q")
        scene["countdown"] = round(t, 3)
        t += 5.0
        scene["answer_at"] = round(t, 3)
        t += 0.5
        for bi, b in enumerate(scene["beats"]):
            add(b["say"], INSTRUCTOR, bi)
    elif kind == "interview":
        add(scene["qsay"] or speakable(scene["q"]), INTERVIEWER, "q")
        t += 0.3
        scene["answer_at"] = round(t - 0.2, 3)
        for bi, b in enumerate(scene["beats"]):
            add(b["say"], INSTRUCTOR, bi)
    else:
        if kind == "divider":
            t = 0.5
        for bi, b in enumerate(scene["beats"]):
            add(b["say"], INSTRUCTOR, bi)
    duration = round(t + 0.5, 3)
    return clips, duration


def build_title(sid, scene, meta, clips):
    ch = meta["chapter"]
    items = scene["items"]
    two_col = len(items) > 3
    li = []
    for i, it in enumerate(items):
        col, row = (i % 2, i // 2) if two_col else (0, i)
        li.append(f'    <div id="{sid}-i{i}" class="it" style="position:absolute;left:{120 + col * 860}px;top:{720 + row * 96}px;width:{820 if two_col else 1660}px">'
                  f'<div class="ck">✓</div><div class="tx" style="font-size:36px">{inline(it)}</div></div>')
    css = """
    #SID-num { position: absolute; left: 112px; top: 170px; font-family: "Outfit", sans-serif; font-weight: 800;
      font-size: 240px; line-height: 1; color: #05998b; }
    #SID-title { position: absolute; left: 120px; top: 428px; width: 1300px; font-family: "Outfit", sans-serif;
      font-weight: 800; font-size: 92px; line-height: 1.05; color: #0f1b2d; }
    #SID-sub { position: absolute; left: 124px; top: 560px; width: 1400px; font-family: "Inter", sans-serif;
      font-weight: 500; font-size: 38px; color: #4b5a70; }
    #SID-art { position: absolute; left: 1440px; top: 170px; width: 340px; height: 374px; }
LEVELCSS
    #SID-label { position: absolute; left: 1430px; top: 560px; width: 360px; text-align: center; font-family: "Inter", sans-serif;
      font-weight: 800; font-size: 28px; letter-spacing: 0.1em; color: #04776c; }
""".replace("SID", sid).replace("LEVELCSS", LEVEL_CSS)
    label = "START HERE" if ch == 0 else f"LEVEL {ch}"
    body = f"""    <div id="{sid}-num">{'00' if ch == 0 else f'{ch:02d}'}</div>
    <div id="{sid}-title">{inline(meta['title'])}</div>
    <div id="{sid}-sub">{inline(meta.get('subtitle', ''))}</div>
    <div id="{sid}-art">{byte_svg(sid + "-byte", 340)}</div>
    <div id="{sid}-label">{label}</div>
    <div id="{sid}-map">{level_map(sid, ch, top=96)}</div>
""" + "\n".join(li)
    end = max((c["t"] + len(c["audio"]) / SR for c in clips), default=4.0)
    # frame 0 is the thumbnail: the title is already on screen, it only settles
    js = [f'    tl.fromTo("#{sid}-title", {{ scale: 1.04, transformOrigin: "0 50%" }}, {{ scale: 1, duration: 0.6, ease: "power3.out" }}, 0);',
          f'    tl.fromTo("#{sid}-num", {{ y: 16 }}, {{ y: 0, duration: 0.6, ease: "power3.out" }}, 0);',
          f'    tl.fromTo("#{sid}-lv{ch}", {{ scale: 1 }}, {{ scale: 1.25, duration: 0.3, ease: "power2.out", yoyo: true, repeat: {max(3, int(end / 0.6) | 1)} }}, 0.4);',
          f'    tl.to("#{sid}-byte", {{ y: -14, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: {max(5, int(end / 0.5) | 1)} }}, 0.3);']
    n_items = max(1, len(items))
    for i in range(len(items)):
        t = 0.9 + i * max(0.6, (end - 1.6) / n_items)
        js += item_js(sid, i, t, None, ".ck")
    return css, body, "\n".join(js)


def items_by_beats(sid, scene, clips, marker=".mk", dim=True):
    """Reveal item i at the first narration line that points at it (or later)."""
    js, shown, prev = [], set(), None
    beat_t = {c["beat"]: c["t"] for c in clips if isinstance(c["beat"], int)}
    end_t = max((c["t"] for c in clips), default=0.6)
    for bi, b in enumerate(scene["beats"]):
        idx = b.get("item", -1)
        if idx is None or idx < 0:
            continue
        for k in range(idx + 1):
            if k not in shown:
                t = beat_t.get(bi, end_t) + (0.0 if k == idx else -0.2)
                js += item_js(sid, k, max(0.3, t), prev if (dim and k == idx) else None, marker)
                shown.add(k)
                if k == idx:
                    prev = k
    for k in range(len(scene["items"])):
        if k not in shown:
            js += item_js(sid, k, end_t, None, marker)
    return js


def build_concept(sid, scene, meta, clips):
    recap = scene["type"] == "recap"
    marker = '<div class="ck">✓</div>' if recap else '<div class="mk"></div>'
    body = heading(sid, scene["heading"]) + '\n    <div class="list">\n' + "\n".join(
        f'      <div id="{sid}-i{i}" class="it">{marker}<div class="tx">{inline(it)}</div></div>'
        for i, it in enumerate(scene["items"])) + "\n    </div>"
    js = [heading_js(sid)] + items_by_beats(sid, scene, clips, dim=not recap)
    return "", body, "\n".join(js)


def build_analogy(sid, scene, meta, clips):
    css = f"""
    .an-head {{ position: absolute; top: 234px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 28px;
      letter-spacing: 0.1em; color: #4b5a70; }}
    .an-row {{ position: absolute; left: 120px; width: 1680px; height: 112px; opacity: 0; }}
    .an-cell {{ position: absolute; top: 0; height: 112px; border-radius: 20px; background: #ffffff; border: 3px solid #dfe6ee;
      display: flex; align-items: center; padding: 0 30px; font-family: "Inter", sans-serif; font-weight: 600;
      font-size: 36px; color: #0f1b2d; }}
    .an-cell.r {{ border-color: #05998b; background: #e9f7f5; }}
    .an-arrow {{ position: absolute; left: 790px; top: 30px; width: 100px; height: 52px; }}
"""
    rows = []
    for i, it in enumerate(scene["items"]):
        top = 290 + i * 134
        rows.append(f'''    <div id="{sid}-i{i}" class="an-row" style="top:{top}px">
      <div class="an-cell" style="left:0;width:770px"><span>{inline(it["left"])}</span></div>
      <svg class="an-arrow" viewBox="0 0 100 52"><path d="M6 26 H80 M62 8 L84 26 L62 44" fill="none" stroke="#05998b" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <div class="an-cell r" style="left:910px;width:770px"><span>{inline(it["right"])}</span></div>
    </div>''')
    body = (heading(sid, scene["heading"]) +
            '\n    <div class="an-head" style="left:124px">REAL LIFE</div><div class="an-head" style="left:1034px">IN FASTAPI</div>\n' +
            "\n".join(rows))
    js = [heading_js(sid)]
    beat_t = {c["beat"]: c["t"] for c in clips if isinstance(c["beat"], int)}
    shown = set()
    for bi, b in enumerate(scene["beats"]):
        idx = b.get("item", -1)
        if idx is not None and idx >= 0 and idx not in shown:
            t = beat_t[bi]
            js.append(f'    tl.fromTo("#{sid}-i{idx}", {{ opacity: 0, y: 24 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t:.3f});')
            shown.add(idx)
    end_t = max((c["t"] for c in clips), default=0.6)
    for k in range(len(scene["items"])):
        if k not in shown:
            js.append(f'    tl.fromTo("#{sid}-i{k}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {end_t:.3f});')
    return css, body, "\n".join(js)


def build_flow(sid, scene, meta, clips):
    n = len(scene["items"])
    gap = 74
    w = min(320, (1680 - (n - 1) * gap) / n)
    x0 = 120 + (1680 - (n * w + (n - 1) * gap)) / 2
    css = f"""
    .fl-node {{ position: absolute; top: 450px; width: {w:.0f}px; height: 190px; border-radius: 24px; background: #ffffff;
      border: 4px solid #cfd9e3; display: flex; align-items: center; justify-content: center; text-align: center;
      padding: 0 18px; font-family: "Inter", sans-serif; font-weight: 700; font-size: {32 if w > 250 else 28}px;
      line-height: 1.25; color: #0f1b2d; opacity: 0; }}
    .fl-arrow {{ position: absolute; top: 520px; width: {gap}px; height: 50px; transform-origin: 0 50%; }}
"""
    parts = []
    for i, it in enumerate(scene["items"]):
        x = x0 + i * (w + gap)
        parts.append(f'    <div id="{sid}-i{i}" class="fl-node" style="left:{x:.0f}px">{inline(it)}</div>')
        if i < n - 1:
            parts.append(f'    <svg id="{sid}-a{i}" class="fl-arrow" style="left:{x + w:.0f}px" viewBox="0 0 74 50"><path d="M8 25 H58 M44 10 L62 25 L44 40" fill="none" stroke="#05998b" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    body = heading(sid, scene["heading"]) + "\n" + "\n".join(parts)
    js = [heading_js(sid)]
    for i in range(n - 1):
        js.append(f'    tl.set("#{sid}-a{i}", {{ scaleX: 0 }}, 0);')
    beat_t = {c["beat"]: c["t"] for c in clips if isinstance(c["beat"], int)}
    end_t = max((c["t"] for c in clips), default=0.6)
    shown, prev = set(), None
    order = [(b.get("item", -1), beat_t.get(bi, end_t)) for bi, b in enumerate(scene["beats"])]
    order += [(k, end_t) for k in range(n)]
    for idx, t in order:
        if idx is None or idx < 0 or idx in shown:
            continue
        for k in range(idx + 1):
            if k in shown:
                continue
            tt = t if k == idx else max(0.3, t - 0.25)
            if k > 0:
                js.append(f'    tl.fromTo("#{sid}-a{k - 1}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.25, ease: "power2.out" }}, {tt - 0.15:.3f});')
            js.append(f'    tl.fromTo("#{sid}-i{k}", {{ opacity: 0, y: 30, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "back.out(1.6)" }}, {tt:.3f});')
            js.append(f'    tl.to("#{sid}-i{k}", {{ backgroundColor: "#05998b", borderColor: "#05998b", color: "#ffffff", duration: 0.25 }}, {tt + 0.1:.3f});')
            if prev is not None:
                js.append(f'    tl.to("#{sid}-i{prev}", {{ backgroundColor: "#e9f7f5", borderColor: "#05998b", color: "#0f1b2d", duration: 0.25 }}, {tt + 0.1:.3f});')
            prev = k
            shown.add(k)
    return css, body, "\n".join(js)


def build_code(sid, scene, meta, clips):
    code = scene["code"]
    top = 230 if scene["heading"] else 120
    body_h = 1010 - top
    panel, lh = code_panel(sid, code, scene.get("lang", "python"), scene["file"], 120, top, 1680, body_h)
    body = (heading(sid, scene["heading"]) + "\n" if scene["heading"] else "") + panel
    js = [heading_js(sid)] if scene["heading"] else []
    js.append(f'    tl.fromTo("#{sid}-panel", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 0.15);')
    beat_t = {c["beat"]: c["t"] for c in clips if isinstance(c["beat"], int)}
    shown = 0
    band_on = False
    n = len(code)
    if not any("reveal" in b for b in scene["beats"]):
        js += reveal_lines_js(sid, range(1, n + 1), 0.45, 0.05)
        shown = n
    for bi, b in enumerate(scene["beats"]):
        if "reveal" not in b:
            continue
        t = beat_t[bi]
        target = n if b["reveal"] == "all" else min(n, b["reveal"])
        if target > shown:
            js += reveal_lines_js(sid, range(shown + 1, target + 1), t)
            shown = target
        if b["focus"]:
            a, z = b["focus"]
            y = (a - 1) * lh
            if not band_on:
                js.append(f'    tl.set("#{sid}-band", {{ y: {y}, scaleY: {z - a + 1} }}, {t:.3f});')
                js.append(f'    tl.to("#{sid}-band", {{ opacity: 1, duration: 0.25 }}, {t:.3f});')
            else:
                js.append(f'    tl.to("#{sid}-band", {{ y: {y}, scaleY: {z - a + 1}, duration: 0.3, ease: "power2.inOut" }}, {t:.3f});')
            band_on = True
            dim = [i for i in range(1, n + 1) if not (a <= i <= z)]
            lit = [i for i in range(a, z + 1)]
            if dim:
                js.append(f'    tl.to([{",".join(f"{chr(34)}#{sid}-l{i}{chr(34)}" for i in dim)}], {{ opacity: 0.4, duration: 0.25 }}, {t:.3f});')
            js.append(f'    tl.to([{",".join(f"{chr(34)}#{sid}-l{i}{chr(34)}" for i in lit)}], {{ opacity: 1, duration: 0.25 }}, {t:.3f});')
        else:
            if band_on:
                js.append(f'    tl.to("#{sid}-band", {{ opacity: 0, duration: 0.25 }}, {t:.3f});')
                band_on = False
            js.append(f'    tl.to("#{sid} .cl", {{ opacity: 1, duration: 0.25 }}, {t:.3f});'.replace(f'"#{sid} .cl"', f'"#{sid}-panel .cl"'))
    if shown < n:
        end_t = max((c["t"] for c in clips), default=0.6)
        js += reveal_lines_js(sid, range(shown + 1, n + 1), end_t)
    return "", body, "\n".join(js)


def build_terminal(sid, scene, meta, clips):
    rows = []
    all_lines = []
    for st in scene["steps"]:
        all_lines += ["$ " + st["cmd"]] + ["  " + c for c in st["cont"]] + st["out"]
    fs, lh = code_metrics(all_lines + ["x" * 40], 1010 - 230 - 110, 1560)
    idx = {}
    k = 0
    for si, st in enumerate(scene["steps"]):
        rows.append(f'        <div id="{sid}-c{si}" class="tl cmd">{html.escape(st["cmd"])}</div>')
        for ci, cl in enumerate(st["cont"]):
            rows.append(f'        <div id="{sid}-c{si}-{ci}" class="tl cmd cont">{html.escape(cl)}</div>')
        for oi, o in enumerate(st["out"]):
            rows.append(f'        <div id="{sid}-o{si}-{oi}" class="tl out">{html.escape(o) or "&#8203;"}</div>')
    top = 230 if scene["heading"] else 120
    body = (heading(sid, scene["heading"]) + "\n" if scene["heading"] else "") + f"""    <div id="{sid}-panel" class="panel" style="left:120px;top:{top}px;width:1680px;height:{1010 - top}px;--fs:{fs}px;--lh:{lh}px;background:#0b111c">
      <div class="bar"><div class="dot" style="left:24px;background:#ff5f57"></div><div class="dot" style="left:50px;background:#febc2e"></div><div class="dot" style="left:76px;background:#28c840"></div>
        <div class="fname">terminal</div></div>
      <div class="code" style="top:84px;font-family:'JetBrains Mono',monospace">
{chr(10).join(rows)}
      </div>
    </div>"""
    js = ([heading_js(sid)] if scene["heading"] else []) + [
        f'    tl.fromTo("#{sid}-panel", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, 0.15);']
    beat_t = {c["beat"]: c["t"] for c in clips if isinstance(c["beat"], int)}
    for bi, b in enumerate(scene["beats"]):
        if b.get("step") is None:
            continue
        t = beat_t[bi]
        st = scene["steps"][b["step"]]
        if b["part"] == "cmd":
            n = max(4, len(st["cmd"]))
            d = min(1.2, n * 0.03)
            js.append(f'    tl.fromTo("#{sid}-c{b["step"]}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: {d:.2f}, ease: "steps({n})" }}, {t:.3f});')
            for ci, cl in enumerate(st["cont"]):
                m = max(4, len(cl))
                js.append(f'    tl.fromTo("#{sid}-c{b["step"]}-{ci}", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: {min(1.2, m * 0.03):.2f}, ease: "steps({m})" }}, {t + d + ci * 0.9:.3f});')
        else:
            for oi in range(len(st["out"])):
                js.append(f'    tl.fromTo("#{sid}-o{b["step"]}-{oi}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, {t + oi * 0.07:.3f});')
    return "", body, "\n".join(js)


def build_divider(sid, scene, meta, clips):
    big, small, glyph = scene["big"], scene["small"], scene["glyph"]
    css = f"""
    #{sid}-bg {{ position: absolute; inset: 0; background: {scene['color']}; }}
    #{sid}-glyph {{ position: absolute; right: 360px; top: 170px; font-family: "Outfit", sans-serif; font-weight: 800;
      font-size: 620px; line-height: 1; color: rgba(255, 255, 255, 0.12); }}
    #{sid}-byte {{ position: absolute; left: 1500px; top: 330px; }}
    #{sid}-big {{ position: absolute; left: 120px; top: 380px; font-family: "Outfit", sans-serif; font-weight: 800;
      font-size: 130px; line-height: 1; color: #ffffff; white-space: nowrap; }}
    #{sid}-small {{ position: absolute; left: 126px; top: 540px; width: 1300px; font-family: "Inter", sans-serif;
      font-weight: 600; font-size: 42px; line-height: 1.35; color: #ffffff; }}
    #{sid}-ch {{ position: absolute; left: 126px; top: 300px; font-family: "Inter", sans-serif; font-weight: 800;
      font-size: 30px; letter-spacing: 0.12em; color: rgba(255, 255, 255, 0.85); }}
"""
    body = f"""    <div id="{sid}-bg"></div>
    <div id="{sid}-glyph">{glyph}</div>
    <div id="{sid}-ch">LEVEL {meta['chapter']} · {html.escape(meta['title'].upper())}</div>
    <div id="{sid}-big">{big}</div>
    <div id="{sid}-small">{small}</div>
    {byte_svg(sid + "-byte", 300, scene.get("mood", "happy"))}"""
    js = f"""    tl.fromTo("#{sid}-bg", {{ clipPath: "inset(0 100% 0 0)" }}, {{ clipPath: "inset(0 0% 0 0)", duration: 0.45, ease: "power3.inOut" }}, 0);
    tl.fromTo("#{sid}-glyph", {{ opacity: 0, scale: 0.8 }}, {{ opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.6)" }}, 0.3);
    tl.fromTo("#{sid}-ch", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.35);
    tl.fromTo("#{sid}-big", {{ opacity: 0, x: -60 }}, {{ opacity: 1, x: 0, duration: 0.45, ease: "power3.out" }}, 0.4);
    tl.fromTo("#{sid}-small", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0.65);
    tl.fromTo("#{sid}-byte", {{ y: 300, opacity: 0, rotation: -10 }}, {{ y: 0, opacity: 1, rotation: 0, duration: 0.55, ease: "back.out(1.7)" }}, 0.5);
    tl.to("#{sid}-byte", {{ rotation: 6, duration: 0.25, ease: "sine.inOut", yoyo: true, repeat: 3 }}, 1.2);
    tl.to("#{sid}-byte", {{ y: -16, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: {max(3, int((clips[-1]["t"] + len(clips[-1]["audio"]) / SR) / 0.5)) | 1} }}, 2.3);"""
    return css, body, js


def build_complete(sid, scene, meta, clips):
    ch = meta["chapter"]
    css = f"""
    #{sid}-bg {{ position: absolute; inset: 0; background: radial-gradient(circle at 50% 42%, #ffffff 0%, #e9f7f5 55%, #cdeee8 100%); }}
    #{sid}-top {{ position: absolute; left: 0; right: 0; top: 150px; text-align: center; font-family: "Inter", sans-serif;
      font-weight: 800; font-size: 30px; letter-spacing: 0.14em; color: #04776c; }}
    #{sid}-big {{ position: absolute; left: 0; right: 0; top: 196px; text-align: center; font-family: "Outfit", sans-serif;
      font-weight: 800; font-size: 120px; line-height: 1; color: #0f1b2d; }}
    .lc-star {{ position: absolute; top: 350px; width: 120px; height: 120px; }}
    #{sid}-badge {{ position: absolute; left: 610px; top: 520px; width: 700px; height: 150px; border-radius: 75px;
      background: #0f1b2d; display: flex; align-items: center; gap: 26px; padding: 0 40px; box-shadow: 0 16px 40px rgba(15,27,45,.25); }}
    #{sid}-medal {{ flex: 0 0 96px; height: 96px; border-radius: 50%; background: #f5a524; border: 6px solid #ffd27a;
      font-family: "Outfit", sans-serif; font-weight: 800; font-size: 44px; line-height: 84px; text-align: center; color: #0f1b2d; }}
    #{sid}-bt {{ font-family: "Inter", sans-serif; color: #ffffff; }}
    #{sid}-bt small {{ display: block; font-weight: 800; font-size: 28px; letter-spacing: 0.1em; color: #19c2b0; }}
    #{sid}-bt span {{ font-family: "Outfit", sans-serif; font-weight: 700; font-size: 46px; }}
    #{sid}-next {{ position: absolute; left: 0; right: 0; top: 720px; text-align: center; font-family: "Inter", sans-serif;
      font-weight: 600; font-size: 40px; color: #0f1b2d; }}
    #{sid}-next b {{ color: #04776c; }}
    #{sid}-cta {{ position: absolute; left: 560px; top: 810px; width: 800px; height: 84px; border-radius: 42px; background: #f5a524;
      text-align: center; line-height: 84px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 32px; color: #0f1b2d; }}
    #{sid}-byte {{ position: absolute; left: 1440px; top: 470px; }}
    #{sid}-byte2 {{ position: absolute; left: 160px; top: 520px; }}
"""
    star = '<svg viewBox="0 0 120 120"><path d="M60 6 L75 42 L114 45 L84 70 L94 108 L60 87 L26 108 L36 70 L6 45 L45 42 Z" fill="#f5a524" stroke="#b26a00" stroke-width="5" stroke-linejoin="round"/></svg>'
    stars = "".join(f'<div id="{sid}-st{i}" class="lc-star" style="left:{780 + i * 120}px">{star}</div>' for i in range(3))
    title = "READY TO START" if ch == 0 else f"LEVEL {ch} COMPLETE"
    body = f"""    <div id="{sid}-bg"></div>
    <div id="{sid}-top">{"FASTAPI ZERO TO PRODUCTION" if ch == 0 else html.escape(meta["title"].upper())}</div>
    <div id="{sid}-big">{title}</div>
    {stars}
    <div id="{sid}-badge"><div id="{sid}-medal">{ch}</div><div id="{sid}-bt"><small>BADGE UNLOCKED</small><span>{html.escape(meta.get("badge", "FastAPI Learner"))}</span></div></div>
    <div id="{sid}-next">Next level: <b>{html.escape(meta.get("next", ""))}</b></div>
    <div id="{sid}-cta">Comment your challenge answers 💬</div>
    <div id="{sid}-byte">{byte_svg(sid + "-b1", 280, "happy")}</div>"""
    js = [f'    tl.fromTo("#{sid}-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, 0);',
          f'    tl.fromTo("#{sid}-top", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.2);',
          f'    tl.fromTo("#{sid}-big", {{ scale: 1.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.8)" }}, 0.3);']
    for i in range(3):
        js.append(f'    tl.fromTo("#{sid}-st{i}", {{ scale: 0, rotation: -90 }}, {{ scale: 1, rotation: 0, duration: 0.4, ease: "back.out(2.4)" }}, {0.8 + i * 0.25:.2f});')
    js += [f'    tl.fromTo("#{sid}-badge", {{ y: 60, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }}, 1.7);',
           f'    tl.fromTo("#{sid}-medal", {{ rotation: -180 }}, {{ rotation: 0, duration: 0.6, ease: "back.out(1.6)" }}, 1.75);',
           f'    tl.fromTo("#{sid}-next", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 2.3);',
           f'    tl.fromTo("#{sid}-cta", {{ scale: 0.6, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }}, 2.7);',
           f'    tl.to("#{sid}-cta", {{ scale: 1.05, duration: 0.3, ease: "sine.inOut", yoyo: true, repeat: 5 }}, 3.2);',
           f'    tl.fromTo("#{sid}-byte", {{ y: 320, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "back.out(1.7)" }}, 1.2);',
           f'    tl.to("#{sid}-byte", {{ y: -30, duration: 0.22, ease: "power2.out", yoyo: true, repeat: 5 }}, 1.9);',
           f'    tl.to("#{sid}-byte", {{ rotation: 5, duration: 0.5, ease: "sine.inOut", yoyo: true, repeat: {max(3, int((clips[-1]["t"] + len(clips[-1]["audio"]) / SR) / 0.5)) | 1} }}, 3.3);']
    return css, body, "\n".join(js)


def build_project(sid, scene, meta, clips):
    css = f"""
    #{sid}-name {{ position: absolute; left: 120px; top: 186px; width: 1680px; font-family: "Outfit", sans-serif; font-weight: 800;
      font-size: 60px; line-height: 1.1; color: #0f1b2d; white-space: nowrap; }}
    .pj-head {{ position: absolute; font-family: "Inter", sans-serif; font-weight: 800; font-size: 28px; letter-spacing: 0.08em; color: #4b5a70; }}
    .pj-chip {{ display: inline-block; margin-left: 14px; padding: 2px 14px; border-radius: 14px; background: #e3edfb; color: #1f56b3;
      font-family: "Inter", sans-serif; font-weight: 700; font-size: 26px; vertical-align: 4px; white-space: nowrap; }}
    .pj-box {{ display: inline-block; flex: 0 0 34px; height: 34px; margin-top: 10px; border-radius: 8px; border: 4px solid #2f6fdb; }}
    #{sid}-ep {{ position: absolute; left: 1180px; top: 330px; width: 620px; border-radius: 20px; background: #0e1726; padding: 22px 28px;
      font-family: "JetBrains Mono", monospace; font-weight: 600; font-size: 28px; line-height: 1.7; color: #e5e9f0; white-space: pre; }}
    #{sid}-ep .m {{ color: #7fb2ff; }}
    #{sid}-st {{ position: absolute; left: 1180px; width: 620px; border-radius: 20px; background: #fff4e0; border: 4px solid #f5a524;
      padding: 18px 26px; font-family: "Inter", sans-serif; font-weight: 600; font-size: 30px; line-height: 1.35; color: #0f1b2d; }}
    #{sid}-st small {{ display: block; font-weight: 800; font-size: 26px; letter-spacing: 0.08em; color: #b26a00; }}
"""
    def req(text):
        m = re.match(r"(.*?)\s*\[([^\]]+)\]\s*$", text)
        if m:
            return f'{inline(m.group(1))}<span class="pj-chip">{html.escape(m.group(2))}</span>'
        return inline(text)
    items = "\n".join(
        f'      <div id="{sid}-i{i}" class="it" style="margin-bottom:26px"><div class="pj-box"></div><div class="tx" style="font-size:36px">{req(it)}</div></div>'
        for i, it in enumerate(scene["items"]))
    ep_lines = scene["endpoints"] or []
    ep = "\n".join(re.sub(r"^(GET|POST|PUT|PATCH|DELETE|WS)\b", r'<span class="m">\1</span>', html.escape(l)) for l in ep_lines)
    ep_h = 44 + int(len(ep_lines) * 28 * 1.7)
    st_top = 330 + (ep_h + 40 if ep_lines else 0)
    body = f"""    <div id="{sid}-pill" class="pill" style="left:120px;top:118px;background:#2f6fdb">LEVEL PROJECT</div>
    <div id="{sid}-name">{inline(scene["heading"])}</div>
    <div class="pj-head" style="left:124px;top:290px">YOU WILL BUILD</div>
    <div class="list" style="top:340px;width:1010px">
{items}
    </div>
    {f'<div class="pj-head" style="left:1184px;top:290px">ENDPOINTS</div><div id="{sid}-ep">{ep}</div>' if ep_lines else ""}
    {f'<div id="{sid}-st" style="top:{st_top}px"><small>STRETCH GOAL</small>{inline(scene["stretch"])}</div>' if scene["stretch"] else ""}"""
    js = [f'    tl.fromTo("#{sid}-pill", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.05);',
          f'    tl.fromTo("#{sid}-name", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, 0.15);']
    if ep_lines:
        js.append(f'    tl.fromTo("#{sid}-ep", {{ opacity: 0, x: 40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, 0.4);')
    js += items_by_beats(sid, scene, clips, dim=False)
    if scene["stretch"]:
        end_t = max((c["t"] for c in clips), default=0.6)
        js.append(f'    tl.fromTo("#{sid}-st", {{ opacity: 0, scale: 0.9 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }}, {end_t:.3f});')
    return css, body, "\n".join(js)


def answer_layout(sid, scene, top, prefix):
    """Answer area: code panel and/or points. Returns (html, js_for(t))."""
    has_code, has_items = scene["acode"] is not None, bool(scene["items"])
    parts = []
    code_w = 1680 if not has_items else 1000
    if has_code:
        panel, _ = code_panel(f"{sid}{prefix}", scene["acode"]["code"], scene["acode"]["lang"],
                              "answer.py" if scene["acode"]["lang"] in ("python", "py") else scene["acode"]["lang"],
                              120, top, code_w, 1010 - top)
        parts.append(panel)
    if has_items:
        left = 1160 if has_code else 120
        width = 640 if has_code else 1660
        fsz = 36 if has_code else 42
        parts.append(f'    <div class="list" style="left:{left}px;top:{top + 6}px;width:{width}px">\n' + "\n".join(
            f'      <div id="{sid}-i{i}" class="it" style="margin-bottom:22px"><div class="mk" style="margin-top:{int(fsz * 0.42)}px"></div><div class="tx" style="font-size:{fsz}px">{inline(it)}</div></div>'
            for i, it in enumerate(scene["items"])) + "\n    </div>")
    return "\n".join(parts), has_code


def build_practice(sid, scene, meta, clips, n, total):
    q_top = 196
    css = f"""
    #{sid}-q {{ position: absolute; left: 120px; top: {q_top}px; width: 1420px; font-family: "Outfit", sans-serif;
      font-weight: 600; font-size: {50 if len(scene['q']) < 110 else 44}px; line-height: 1.22; color: #0f1b2d; }}
    #{sid}-timer {{ position: absolute; left: 1560px; top: 150px; width: 260px; height: 236px; opacity: 0; }}
    #{sid}-timer svg {{ position: absolute; left: 50px; top: 0; width: 160px; height: 160px; }}
    .tm-n {{ position: absolute; left: 50px; top: 0; width: 160px; height: 160px; line-height: 160px; text-align: center;
      font-family: "Outfit", sans-serif; font-weight: 800; font-size: 72px; color: #0f1b2d; opacity: 0; }}
    #{sid}-timer .lab {{ position: absolute; left: 0; width: 260px; top: 176px; white-space: nowrap; text-align: center; font-family: "Inter", sans-serif;
      font-weight: 800; font-size: 28px; letter-spacing: 0.04em; color: #b26a00; }}
"""
    body = [f'    <div id="{sid}-pill" class="pill" style="left:120px;top:118px;background:#05998b">CHALLENGE {n} / {total}</div>',
            f'    <div id="{sid}-q">{inline(scene["q"])}</div>',
            f'''    <div id="{sid}-timer"><svg viewBox="0 0 160 160"><circle cx="80" cy="80" r="70" fill="#ffffff" stroke="#e6ebf0" stroke-width="14"/>
      <circle id="{sid}-ring" cx="80" cy="80" r="70" fill="none" stroke="#f5a524" stroke-width="14" stroke-linecap="round"
        transform="rotate(-90 80 80)" stroke-dasharray="439.8" stroke-dashoffset="0"/></svg>
      {''.join(f'<div id="{sid}-tn{k}" class="tm-n">{k}</div>' for k in range(5, 0, -1))}
      <div class="lab">PAUSE &amp; SOLVE</div></div>''']
    qcode_top = 420 if len(scene["q"]) < 110 else 470
    if scene["qcode"]:
        panel, _ = code_panel(f"{sid}q", scene["qcode"]["code"], scene["qcode"]["lang"], "question.py", 120, qcode_top, 1680, 1010 - qcode_top)
        body.append(panel)
    a_top = 470 if len(scene["q"]) < 110 else 520
    body.append(f'    <div id="{sid}-apill" class="pill" style="left:120px;top:{a_top - 76}px;background:#f5a524;color:#0f1b2d">SOLUTION</div>')
    ahtml, has_acode = answer_layout(sid, scene, a_top, "a")
    body.append(ahtml)
    js = [f'    tl.fromTo("#{sid}-pill", {{ opacity: 0, y: -20 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, 0.05);',
          f'    tl.fromTo("#{sid}-q", {{ opacity: 0, x: -40 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, 0.15);',
          f'    tl.set("#{sid}-apill", {{ opacity: 0 }}, 0);']
    if scene["qcode"]:
        js.append(f'    tl.fromTo("#{sid}q-panel", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, 0.3);')
        js += reveal_lines_js(f"{sid}q", range(1, len(scene["qcode"]["code"]) + 1), 0.4, 0.04)
    c0, a0 = scene["countdown"], scene["answer_at"]
    js.append(f'    tl.fromTo("#{sid}-timer", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {c0 - 0.1:.3f});')
    js.append(f'    tl.fromTo("#{sid}-ring", {{ strokeDashoffset: 0 }}, {{ strokeDashoffset: 439.8, duration: 5, ease: "none" }}, {c0:.3f});')
    for k in range(5, 0, -1):
        tk = c0 + (5 - k)
        js.append(f'    tl.set("#{sid}-tn{k}", {{ opacity: 1 }}, {tk:.3f});')
        js.append(f'    tl.set("#{sid}-tn{k}", {{ opacity: 0 }}, {tk + 1:.3f});')
    js.append(f'    tl.to("#{sid}-timer", {{ opacity: 0, scale: 0.8, duration: 0.25 }}, {a0:.3f});')
    if scene["qcode"]:
        js.append(f'    tl.to("#{sid}q-panel", {{ opacity: 0, y: -20, duration: 0.3 }}, {a0:.3f});')
    js.append(f'    tl.fromTo("#{sid}-apill", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }}, {a0 + 0.1:.3f});')
    if has_acode:
        js.append(f'    tl.fromTo("#{sid}a-panel", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {a0 + 0.2:.3f});')
        js += reveal_lines_js(f"{sid}a", range(1, len(scene["acode"]["code"]) + 1), a0 + 0.3, 0.05)
    js += items_by_beats(sid, scene, clips)
    return css, "\n".join(body), "\n".join(js)


def build_interview(sid, scene, meta, clips, n, total):
    level = (scene["level"] or "mid").lower()
    qlen = len(scene["q"])
    css = f"""
    #{sid}-av {{ position: absolute; left: 120px; top: 126px; width: 120px; height: 120px; border-radius: 50%; background: #1d2b45; }}
    #{sid}-avl {{ position: absolute; left: 70px; top: 254px; width: 220px; text-align: center; font-family: "Inter", sans-serif;
      font-weight: 700; font-size: 28px; color: #4b5a70; }}
    #{sid}-bub {{ position: absolute; left: 290px; top: 120px; width: 1510px; min-height: 170px; border-radius: 26px;
      background: #ffffff; border: 3px solid #dfe6ee; padding: 30px 40px; box-shadow: 0 12px 30px rgba(15, 27, 45, 0.08); }}
    #{sid}-bub::before {{ content: ""; position: absolute; left: -22px; top: 50px; border: 18px solid transparent;
      border-right: 22px solid #ffffff; border-left: none; }}
    #{sid}-qt {{ font-family: "Outfit", sans-serif; font-weight: 600; font-size: {46 if qlen < 100 else 40}px; line-height: 1.22; color: #0f1b2d; }}
"""
    a_top = 420 if qlen < 100 else 470
    body = [f'    <svg id="{sid}-av" viewBox="0 0 120 120"><circle cx="60" cy="60" r="60" fill="#1d2b45"/><circle cx="60" cy="48" r="20" fill="#cfd9e3"/><path d="M24 104 C28 78 92 78 96 104" fill="#cfd9e3"/></svg>',
            f'    <div id="{sid}-avl">INTERVIEWER</div>',
            f'    <div id="{sid}-bub"><div id="{sid}-qt">{inline(scene["q"])}</div></div>',
            f'    <div id="{sid}-pill" class="pill" style="left:120px;top:{a_top - 80}px;background:{LEVEL_COL.get(level, "#e08e0b")}">BOSS Q{n}/{total} · {level.upper()}</div>',
            f'    <div id="{sid}-apill" class="pill" style="left:{120 + 400}px;top:{a_top - 80}px;background:#05998b">MODEL ANSWER</div>']
    ahtml, has_acode = answer_layout(sid, scene, a_top, "a")
    body.append(ahtml)
    a0 = scene["answer_at"]
    js = [f'    tl.fromTo("#{sid}-av", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.35, ease: "back.out(2)" }}, 0.05);',
          f'    tl.fromTo("#{sid}-avl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, 0.15);',
          f'    tl.fromTo("#{sid}-bub", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, 0.15);',
          f'    tl.fromTo("#{sid}-pill", {{ opacity: 0, y: -10 }}, {{ opacity: 1, y: 0, duration: 0.3 }}, 0.3);',
          f'    tl.fromTo("#{sid}-apill", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.2)" }}, {a0:.3f});']
    if has_acode:
        js.append(f'    tl.fromTo("#{sid}a-panel", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4 }}, {a0 + 0.1:.3f});')
        js += reveal_lines_js(f"{sid}a", range(1, len(scene["acode"]["code"]) + 1), a0 + 0.2, 0.05)
    js += items_by_beats(sid, scene, clips)
    return css, "\n".join(body), "\n".join(js)



def byte_svg(id_, size=220, mood="happy"):
    """Byte, the course guide: a small round robot."""
    mouth = {"happy": "M86 150 Q110 168 134 150", "think": "M92 156 L128 152", "wow": "M104 150 a8 8 0 1 0 16 0 a8 8 0 1 0 -16 0"}[mood]
    return f'''<svg id="{id_}" data-layout-ignore viewBox="0 0 220 240" width="{size}" height="{size * 240 / 220:.0f}" aria-hidden="true">
  <line x1="110" y1="40" x2="110" y2="18" stroke="#0f1b2d" stroke-width="7" stroke-linecap="round"/>
  <circle cx="110" cy="14" r="11" fill="#f5a524" stroke="#0f1b2d" stroke-width="5"/>
  <rect x="14" y="120" width="30" height="62" rx="15" fill="#d7f2ee" stroke="#0f1b2d" stroke-width="6"/>
  <rect x="176" y="120" width="30" height="62" rx="15" fill="#d7f2ee" stroke="#0f1b2d" stroke-width="6"/>
  <rect x="34" y="40" width="152" height="176" rx="70" fill="#ffffff" stroke="#0f1b2d" stroke-width="7"/>
  <rect x="58" y="78" width="104" height="58" rx="29" fill="#0f1b2d"/>
  <rect x="80" y="92" width="18" height="26" rx="9" fill="#19c2b0"/><rect x="122" y="92" width="18" height="26" rx="9" fill="#19c2b0"/>
  <path d="{mouth}" fill="none" stroke="#0f1b2d" stroke-width="6" stroke-linecap="round"/>
  <rect x="78" y="176" width="64" height="22" rx="8" fill="#05998b"/>
  <text x="110" y="193" text-anchor="middle" font-family="JetBrains Mono" font-weight="700" font-size="16" fill="#ffffff">BYTE</text>
</svg>'''


LEVEL_NAMES = ["Welcome", "Getting Started", "Path & Query", "Pydantic", "Responses", "Dependencies",
               "Databases", "Big Apps", "Auth", "Async & Tasks", "Testing", "Advanced", "Production", "Portfolio"]


def level_map(sid, current, top=60, left=120, width=1680):
    n = len(LEVEL_NAMES)
    step = width / (n - 1)
    nodes = []
    for i in range(n):
        x = left + i * step
        state = "done" if i < current else "now" if i == current else "todo"
        fill = {"done": "#05998b", "now": "#f5a524", "todo": "#ffffff"}[state]
        stroke = {"done": "#05998b", "now": "#0f1b2d", "todo": "#c3cdd8"}[state]
        txt = {"done": "#ffffff", "now": "#0f1b2d", "todo": "#8a99ab"}[state]
        nodes.append(f'<div id="{sid}-lv{i}" class="lv" style="left:{x - 26:.0f}px;top:{top}px;background:{fill};border-color:{stroke};color:{txt}">{i}</div>')
    path = f'<div class="lv-path" style="left:{left}px;top:{top + 24}px;width:{width}px"></div>'
    done = f'<div id="{sid}-lvdone" class="lv-path" style="left:{left}px;top:{top + 24}px;width:{max(0, current) * step:.0f}px;background:#05998b"></div>'
    return path + done + "".join(nodes)


LEVEL_CSS = """
    .lv-path { position: absolute; height: 6px; border-radius: 3px; background: #d5dde6; }
    .lv { position: absolute; width: 52px; height: 52px; border-radius: 50%; border: 4px solid; text-align: center;
      line-height: 44px; font-family: "Outfit", sans-serif; font-weight: 800; font-size: 28px; }
"""


# ---------------------------------------------------------------- chrome
def chrome_html(meta, segments, hidden, total, speech=()):
    ch = meta["chapter"]
    title = f"LEVEL {ch} · {meta['title']}" if ch else "START HERE · Welcome"
    names = {"lesson": "LEARN", "practice": "CHALLENGE", "project": "PROJECT", "interview": "BOSS ROUND"}
    seg_spans = "".join(f'<span id="cr-seg-{k}" class="seg seg-{k}">{v}</span>' for k, v in names.items())
    js = [f'    tl.fromTo("#cr-xp", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {total:.3f}, ease: "none" }}, 0);',
          '    tl.set(".seg", { opacity: 0 }, 0);', '    tl.set(".cr-w", { scaleY: 0.25 }, 0);']
    for t, seg in segments:
        js.append(f'    tl.set(".seg", {{ opacity: 0 }}, {t:.3f});')
        js.append(f'    tl.fromTo("#cr-seg-{seg}", {{ opacity: 0, y: -12 }}, {{ opacity: 1, y: 0, duration: 0.25, immediateRender: false }}, {t:.3f});')
    for a, d in speech:
        for k in range(5):
            dur = 0.2 + 0.04 * k
            reps = int(d / dur) - 1          # (reps + 1) half-cycles must fit inside the clip
            if reps % 2 == 0:
                reps -= 1                    # odd repeat count: ends back at rest
            if reps < 1:
                continue
            js.append(f'    tl.fromTo("#cr-w{k}", {{ scaleY: 0.25 }}, {{ scaleY: {0.55 + 0.45 * ((k * 37) % 5) / 4:.2f}, duration: {dur:.2f}, ease: "sine.inOut", yoyo: true, repeat: {reps}, immediateRender: false }}, {a:.3f});')
        js.append(f'    tl.set(".cr-w", {{ scaleY: 0.25 }}, {a + d:.3f});')
    for a, b in hidden:
        js.append(f'    tl.set("#cr-top", {{ opacity: 0 }}, {a:.3f});')
        js.append(f'    tl.set("#cr-top", {{ opacity: 1 }}, {b:.3f});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; }}
    #cr-top {{ position: absolute; left: 120px; right: 120px; top: 36px; height: 52px; display: flex; align-items: center;
      justify-content: space-between; }}
    #cr-left {{ display: flex; align-items: center; gap: 16px; font-family: "Outfit", sans-serif; font-weight: 700; font-size: 26px;
      color: #0f1b2d; white-space: nowrap; }}
    #cr-lvl {{ width: 50px; height: 50px; border-radius: 50%; background: #f5a524; border: 4px solid #0f1b2d; text-align: center;
      line-height: 42px; font-weight: 800; font-size: 28px; }}
    #cr-right {{ display: flex; align-items: center; gap: 22px; }}
    #cr-segs {{ position: relative; width: 240px; height: 42px; }}
    .seg {{ position: absolute; right: 0; top: 0; height: 42px; padding: 0 18px; border-radius: 21px; color: #ffffff;
      font-family: "Inter", sans-serif; font-weight: 800; font-size: 28px; letter-spacing: 0.04em; line-height: 42px; white-space: nowrap; }}
    .seg-lesson {{ background: #05998b; }} .seg-practice {{ background: #b26a00; }} .seg-project {{ background: #2f6fdb; }} .seg-interview {{ background: #1d2b45; }}
    #cr-xpbox {{ display: flex; align-items: center; gap: 10px; font-family: "Inter", sans-serif; font-weight: 800; font-size: 28px; color: #04776c; }}
    #cr-xptrack {{ position: relative; width: 240px; height: 18px; border-radius: 9px; background: #dbe4ec; overflow: hidden; }}
    #cr-xp {{ position: absolute; inset: 0; background: linear-gradient(90deg, #05998b, #19c2b0); transform-origin: 0 50%; }}
    #cr-logo {{ width: 40px; height: 40px; }}
    #cr-wave {{ display: flex; align-items: center; gap: 5px; height: 40px; padding: 0 14px; border-radius: 20px; background: #e2f4f1; }}
    .cr-w {{ width: 7px; height: 30px; border-radius: 4px; background: #05998b; }}
  </style>
  <div id="root" data-composition-id="chrome" data-width="1920" data-height="1080">
    <div id="cr-top">
      <div id="cr-left"><div id="cr-lvl">{ch}</div>{html.escape(title)}<div id="cr-wave">{"".join(f'<div id="cr-w{k}" class="cr-w"></div>' for k in range(5))}</div></div>
      <div id="cr-right"><div id="cr-segs">{seg_spans}</div>
        <div id="cr-xpbox">XP<div id="cr-xptrack"><div id="cr-xp"></div></div></div>
        <img id="cr-logo" src="assets/logo.svg" alt="ByteTitan" /></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["chrome"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- chapter
DIVIDERS = {
    "practice": dict(big="Challenge Time!", glyph="?", color="#05998b", mood="think",
                     small="5 practice challenges. Timer aate hi video pause karo, khud solve karo, phir solution dekho.",
                     say="चलो अब practice करते हैं। हर सवाल के बाद पाँच seconds का timer आएगा। Video pause कीजिए, पहले खुद solve कीजिए, फिर answer देखिए।"),
    "project": dict(big="Project Time", glyph="{ }", color="#2f6fdb", mood="happy",
                    small="Is level ke concepts se ek chhota real project. Pehle khud banao, phir solution walkthrough dekho.",
                    say="अब Project Time। इस level में जो भी सीखा, उसे एक छोटे real project में use करेंगे। पहले brief देखिए, खुद बनाने की कोशिश कीजिए, फिर मेरे साथ solution देखिए।"),
    "interview": dict(big="Boss Round", glyph="Q", color="#1d2b45", mood="wow",
                      small="Mock interview: 5 sawaal, junior se senior tak. Pehle khud socho, phir model answer se compare karo.",
                      say="अब mock interview round। Interviewer English में सवाल पूछेगा, बिल्कुल real interview की तरह। आप पहले खुद सोचिए कि आप क्या बोलेंगे, फिर model answer से compare कीजिए।"),
}


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def build(ch, allow_new=True):
    src = ROOT / f"content/ch{ch:02d}.md"
    meta, scenes = parse_chapter(src)
    out = ROOT / f"build/ch{ch:02d}"
    if out.exists():
        shutil.rmtree(out)
    (out / "compositions").mkdir(parents=True)
    (out / "assets/sfx").mkdir(parents=True)
    shutil.copy(ROOT / "assets/gsap.min.js", out / "assets/gsap.min.js")
    shutil.copy(ROOT / "assets/logo.svg", out / "assets/logo.svg")
    for f in (ROOT / "assets/sfx").iterdir():
        shutil.copy(f, out / "assets/sfx" / f.name)
    (out / "hyperframes.json").write_text((ROOT / "assets/hyperframes.json").read_text())
    (out / "meta.json").write_text(json.dumps({"id": f"fastapi-ch{ch:02d}", "name": f"FastAPI course ch{ch:02d}"}))

    # insert section dividers
    seq, seen = [], set()
    for sc in scenes:
        if sc["type"] in DIVIDERS and sc["type"] not in seen:
            d = DIVIDERS[sc["type"]]
            seq.append({"type": "divider", "section": sc["type"], **d, "beats": [{"say": d["say"]}], "items": []})
            seen.add(sc["type"])
        seq.append(sc)
    if meta["chapter"] == 0:
        done_say = f"तो चलिए, Level one से शुरू करते हैं। Comments में बताइए कि आप FastAPI क्यों सीख रहे हैं।"
    else:
        done_say = (f"Congratulations! Level {meta['chapter']} complete। आपने {meta.get('badge', '')} badge unlock कर लिया है। "
                    f"अपने challenge answers comments में ज़रूर लिखिए। Next level में हम {meta.get('next', '')} सीखेंगे।")
    seq.append({"type": "complete", "beats": [{"say": done_say}], "items": []})
    n_prac = sum(1 for s in seq if s["type"] == "practice")
    n_int = sum(1 for s in seq if s["type"] == "interview")

    t0, hosts, voice, cues, srt, segments, hidden, chapters = 0.0, [], [], [], [], [], [], []
    pc = ic = 0
    for k, sc in enumerate(seq):
        sid = f"s{k + 1:02d}"
        if sc["type"] == "practice":
            pc += 1
        if sc["type"] == "interview":
            ic += 1
        clips, dur = plan_scene(sc, meta, pc, ic)
        kind = sc["type"]
        if kind == "title":
            css, body, js = build_title(sid, sc, meta, clips)
        elif kind in ("concept", "recap"):
            css, body, js = build_concept(sid, sc, meta, clips)
        elif kind == "analogy":
            css, body, js = build_analogy(sid, sc, meta, clips)
        elif kind == "flow":
            css, body, js = build_flow(sid, sc, meta, clips)
        elif kind == "code":
            css, body, js = build_code(sid, sc, meta, clips)
        elif kind == "terminal":
            css, body, js = build_terminal(sid, sc, meta, clips)
        elif kind == "divider":
            css, body, js = build_divider(sid, sc, meta, clips)
        elif kind == "practice":
            css, body, js = build_practice(sid, sc, meta, clips, pc, n_prac)
        elif kind == "interview":
            css, body, js = build_interview(sid, sc, meta, clips, ic, n_int)
        elif kind == "complete":
            css, body, js = build_complete(sid, sc, meta, clips)
        elif kind == "project":
            css, body, js = build_project(sid, sc, meta, clips)
        (out / f"compositions/{sid}.html").write_text(scene_html(sid, css, body, js))
        hosts.append((sid, t0, dur))
        if kind == "divider":
            seg = sc["section"]
        elif kind in ("practice", "interview", "project"):
            seg = kind
        elif kind == "complete":
            seg = segments[-1][1] if segments else "lesson"
        else:
            seg = "project" if segments and segments[-1][1] == "project" else "lesson"
        if not segments or segments[-1][1] != seg:
            segments.append((t0, seg))
        if kind in ("title", "divider", "complete"):
            hidden.append((t0, t0 + dur))
        label = {"title": meta["title"], "divider": sc.get("big"), "complete": "Level complete",
                 "project": f"Project: {sc.get('heading', '')}"}.get(kind) or sc.get("heading") or \
            (f"Practice Q{pc}" if kind == "practice" else f"Interview Q{ic}" if kind == "interview" else kind)
        chapters.append({"t": round(t0, 3), "kind": kind, "label": speakable(label)})
        for c in clips:
            voice.append((t0 + c["t"], c["audio"]))
            words = c["text"].split()
            # subtitles in chunks of ~12 words, timed by word share
            dur_c = len(c["audio"]) / SR
            for w0 in range(0, len(words), 12):
                chunk = words[w0 : w0 + 12]
                a = t0 + c["t"] + dur_c * w0 / len(words)
                b = t0 + c["t"] + dur_c * min(len(words), w0 + 12) / len(words)
                srt.append((a, b, " ".join(chunk)))
        if kind == "divider":
            cues.append((t0 + 0.0, "whoosh-short.mp3", 0.35))
        if kind == "complete":
            cues += [(t0 + 0.3, "whoosh-short.mp3", 0.3)] + [(t0 + 0.8 + i * 0.25, "pop.mp3", 0.3) for i in range(3)] + [(t0 + 1.7, "sparkle.mp3", 0.3)]
        if kind == "practice":
            for s in range(5):
                cues.append((t0 + sc["countdown"] + s, "tick.wav", 0.35))
            cues.append((t0 + sc["answer_at"] + 0.1, "ping.mp3", 0.3))
        if kind == "interview":
            cues.append((t0 + sc["answer_at"], "pop.mp3", 0.25))
        t0 += dur
    total = round(t0, 3)

    # voice track
    track = np.zeros(int((total + 0.5) * SR), dtype=np.float32)
    for t, a in voice:
        i = int(t * SR)
        track[i : i + len(a)] += a[: len(track) - i]
    peak = float(np.max(np.abs(track))) or 1.0
    track *= 0.89 / peak
    sf.write(out / "assets/vo.wav", track, SR, subtype="PCM_16")

    host_tags = "\n".join(
        f'      <div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
        f'data-start="{st:.3f}" data-duration="{d:.3f}" data-track-index="1" data-track-kind="graphics" '
        f'data-width="1920" data-height="1080" style="z-index: 2"></div>'
        for sid, st, d in hosts)
    audio_tags = [f'      <audio id="vo" class="clip" src="assets/vo.wav" data-start="0" data-duration="{total:.3f}" data-track-index="10" data-volume="1"></audio>']
    lane_end = []
    for i, (t, f, v) in enumerate(cues):
        d = round(sf.info(str(out / "assets/sfx" / f)).duration, 3)
        lane = next((k for k, e in enumerate(lane_end) if e <= t), None)
        if lane is None:
            lane = len(lane_end)
            lane_end.append(0)
        lane_end[lane] = t + d
        audio_tags.append(f'      <audio id="sfx-{i:03d}" class="clip" src="assets/sfx/{f}" data-start="{t:.3f}" '
                          f'data-duration="{d}" data-track-index="{11 + lane}" data-volume="{v}"></audio>')
    speech = [(t, len(a) / SR) for t, a in voice]
    (out / "compositions/chrome.html").write_text(chrome_html(meta, segments, hidden, total, speech))
    index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>FastAPI Zero to Production · Chapter {ch}</title>
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #f4f6f8; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-fps="30" data-width="1920" data-height="1080">
{host_tags}
      <div id="chrome" class="clip" data-composition-id="chrome" data-composition-src="compositions/chrome.html" data-start="0" data-duration="{total:.3f}" data-track-index="2" data-track-kind="graphics" data-width="1920" data-height="1080" style="z-index: 4"></div>
{chr(10).join(audio_tags)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    (out / "index.html").write_text(index)
    (out / "subtitles.srt").write_text("\n".join(
        f"{i + 1}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n" for i, (a, b, txt) in enumerate(srt)))
    (out / "chapters.json").write_text(json.dumps({"chapter": ch, "title": meta["title"], "duration": total, "scenes": chapters}, ensure_ascii=False, indent=1))
    print(f"ch{ch:02d}: {len(seq)} scenes, {total / 60:.1f} min -> {out}")
    return total


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for a in args:
        build(int(a), allow_new="--no-tts" not in sys.argv)
