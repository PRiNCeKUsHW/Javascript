"""Write compositions/captions.html from assets/vo_words.json.

Groups are 2-3 words (high-energy read), broken at punctuation and at scene
changes; the word being spoken gets a saffron box.

  python tools/build_captions.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "assets/vo_words.json").read_text())
words = data["words"]

# phrases end at punctuation, a scene change or a pause; each phrase is split
# into balanced groups of 2-3 words so no word is left on its own
phrases, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    nxt = words[i + 1] if i + 1 < len(words) else None
    if (nxt is None or re.search(r"[.,?!…]$", w["text"]) or nxt["scene"] != w["scene"]
            or nxt["start"] - w["end"] >= 0.15):
        phrases.append(cur)
        cur = []

def split(n):
    if n <= 3:
        return [n]
    if n == 4:
        return [2, 2]
    return [3] + split(n - 3) if n - 3 != 1 else [2, 2]

groups = []
for ph in phrases:
    k = 0
    for size in split(len(ph)):
        groups.append(ph[k : k + size])
        k += size

spans = []
for gi, g in enumerate(groups):
    start = max(0.1, words[g[0]]["start"] - 0.06)
    end = words[g[-1]]["end"] + 0.3
    if gi + 1 < len(groups):
        end = min(end, words[groups[gi + 1][0]]["start"] - 0.08)
    spans.append((round(start, 3), round(end, 3)))

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

markup = []
for gi, g in enumerate(groups):
    ws = "".join(
        f'<span id="cap-w{i}" class="cap-w"><span class="cap-bg"></span><span class="cap-t">{esc(words[i]["text"])}</span></span>'
        for i in g
    )
    markup.append(f'      <div id="cap-g{gi}" class="cap-g"><div class="cap-plate">{ws}</div></div>')

timing = json.dumps(
    {"groups": [{"words": g, "start": s, "end": e} for g, (s, e) in zip(groups, spans)],
     "words": [{"start": w["start"], "end": w["end"]} for w in words]},
    separators=(",", ":"),
)

html = f'''<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      pointer-events: none;
    }}
    .cap-g {{
      position: absolute;
      left: 0;
      width: 1080px;
      top: 1336px;
      height: 124px;
      display: flex;
      align-items: center;
      justify-content: center;
      opacity: 0;
      visibility: hidden;
    }}
    .cap-plate {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      max-width: 860px;
      padding: 10px 18px;
      border-radius: 18px;
      background: rgba(255, 255, 255, 0.92);
      box-shadow: 0 6px 0 rgba(14, 27, 61, 0.18);
    }}
    .cap-w {{
      position: relative;
      display: inline-block;
      padding: 4px 12px 8px;
      font-family: "Archivo Black", sans-serif;
      font-size: 64px;
      line-height: 1;
      color: #0e1b3d;
      white-space: nowrap;
    }}
    .cap-bg {{
      position: absolute;
      inset: 0;
      border-radius: 10px;
      background: #ff8a1f;
      transform: scaleX(0);
      transform-origin: 0 50%;
    }}
    .cap-t {{
      position: relative;
      display: inline-block;
    }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(markup)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const CAP = {timing};
    CAP.groups.forEach((g, gi) => {{
      const el = "#cap-g" + gi;
      // fit long groups inside the plate
      const plate = document.querySelector(el + " .cap-plate");
      const text = plate.textContent;
      if (window.__hyperframes && window.__hyperframes.fitTextFontSize) {{
        const {{ fontSize }} = window.__hyperframes.fitTextFontSize(text, {{
          fontFamily: "Archivo Black", fontWeight: 400, maxWidth: 780, baseFontSize: 64, minFontSize: 44,
        }});
        plate.querySelectorAll(".cap-w").forEach((w) => (w.style.fontSize = fontSize + "px"));
      }}
      tl.set(el, {{ visibility: "visible" }}, g.start);
      tl.fromTo(el, {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.1, ease: "power2.out" }}, g.start);
      g.words.forEach((wi) => {{
        const w = CAP.words[wi];
        const bg = "#cap-w" + wi + " .cap-bg";
        const t = "#cap-w" + wi + " .cap-t";
        tl.fromTo(bg, {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.08, ease: "power2.out" }}, w.start);
        tl.fromTo(t, {{ scale: 1 }}, {{ scale: 1.06, duration: 0.08, ease: "power2.out" }}, w.start);
        const off = Math.min(w.end, g.end - 0.12);
        tl.to(bg, {{ scaleX: 0, transformOrigin: "100% 50%", duration: 0.08, ease: "power2.in" }}, off);
        tl.to(t, {{ scale: 1, duration: 0.08, ease: "power2.in" }}, off);
      }});
      tl.to(el, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, g.end - 0.1);
      tl.set(el, {{ opacity: 0, visibility: "hidden" }}, g.end);
    }});
    window.__timelines["captions"] = tl;
  </script>
</template>
'''
(ROOT / "compositions/captions.html").write_text(html)
print(len(groups), "caption groups")
for g, (s, e) in zip(groups, spans):
    print(f"{s:6.2f}-{e:6.2f}  " + " ".join(words[i]["text"] for i in g))
