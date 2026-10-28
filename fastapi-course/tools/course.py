"""Parse a chapter script (content/chNN.md) into scenes and beats.

Format
------
Front matter between --- lines: chapter, title, subtitle.

Blocks start with `::: <type> <args>` and end with `:::`.

  ::: title                     `- item` = "in this chapter" point, `> text` = narration
  ::: concept <Heading>         `- point` revealed with the `> narration` lines after it
  ::: recap                     like concept, titled "Key takeaways"
  ::: flow <Heading>            `- node` boxes joined by arrows
  ::: analogy <Heading>         `- real life => in FastAPI` rows (an optional emoji first)
  ::: code <file> | <Heading>   one fenced code block, then beats:
                                  `@3 > ...`    reveal through line 3, focus line 3
                                  `@3-5 > ...`  reveal through line 5, focus 3-5
                                  `@all > ...`  reveal everything, no focus
                                  `> ...`       keep the current state
  ::: terminal <Heading>        `$ command`, `+ continuation of the command`, `| output line`, `> narration`
  ::: practice                  `q:` question, optional fenced code, `a:` then optional
                                fenced code, `- points` and `> narration`
  ::: project <Name>            `- requirement [Concept]`, optional ```text endpoints block,
                                `stretch:` goal, `> narration`. Code blocks that follow it
                                (before the boss round) are its solution walkthrough.
  ::: interview <junior|mid|senior>
                                `q:` question (interviewer voice), then `- point` / `> answer`
  `qsay:` overrides how a question is spoken.

Narration (`>`) is written to be spoken: no symbols the voice would read out.
"""
import re
from pathlib import Path


class ScriptError(Exception):
    pass


def parse_chapter(path):
    text = Path(path).read_text()
    lines = text.splitlines()
    meta, i = {}, 0
    if lines and lines[0].strip() == "---":
        i = 1
        while lines[i].strip() != "---":
            k, _, v = lines[i].partition(":")
            meta[k.strip()] = v.strip()
            i += 1
        i += 1
    scenes = []
    while i < len(lines):
        line = lines[i]
        if line.startswith(":::"):
            head = line[3:].strip()
            body = []
            i += 1
            while i < len(lines) and lines[i].rstrip() != ":::":
                body.append(lines[i])
                i += 1
            if i >= len(lines):
                raise ScriptError(f"{path}: unclosed block '{head}'")
            kind, _, args = head.partition(" ")
            scenes.append(parse_block(kind, args.strip(), body, path))
        i += 1
    meta["chapter"] = int(meta["chapter"])
    return meta, scenes


def take_fence(body, j):
    """Return (lang, code_lines, next_index) for a fenced block starting at body[j]."""
    lang = body[j].strip()[3:].strip() or "text"
    code = []
    j += 1
    while j < len(body) and not body[j].strip().startswith("```"):
        code.append(body[j])
        j += 1
    return lang, code, j + 1


def parse_block(kind, args, body, path):
    if kind in ("title", "concept", "recap", "flow", "analogy"):
        scene = {"type": kind, "heading": args or ("Key takeaways" if kind == "recap" else ""),
                 "items": [], "beats": []}
        for raw in body:
            s = raw.strip()
            if s.startswith("- "):
                item = s[2:]
                if kind == "analogy":
                    if "=>" not in item:
                        raise ScriptError(f"{path}: analogy row needs 'left => right': {item}")
                    left, right = (x.strip() for x in item.split("=>", 1))
                    item = {"left": left, "right": right}
                scene["items"].append(item)
            elif s.startswith(">"):
                scene["beats"].append({"say": s[1:].strip(), "item": len(scene["items"]) - 1})
            elif s:
                raise ScriptError(f"{path}: unexpected line in {kind}: {s}")
        return scene

    if kind == "code":
        fname, _, heading = args.partition("|")
        scene = {"type": "code", "file": fname.strip(), "heading": heading.strip(), "beats": []}
        j = 0
        while j < len(body):
            s = body[j].strip()
            if s.startswith("```"):
                scene["lang"], scene["code"], j = take_fence(body, j)
                continue
            m = re.match(r"@(all|\d+(?:-\d+)?)\s*>\s*(.*)", s)
            if m:
                spec = m.group(1)
                if spec == "all":
                    beat = {"reveal": "all", "focus": None}
                else:
                    a, _, b = spec.partition("-")
                    a, b = int(a), int(b or a)
                    beat = {"reveal": b, "focus": [a, b]}
                beat["say"] = m.group(2)
                scene["beats"].append(beat)
            elif s.startswith(">"):
                scene["beats"].append({"say": s[1:].strip()})
            elif s:
                raise ScriptError(f"{path}: unexpected line in code: {s}")
            j += 1
        if "code" not in scene:
            raise ScriptError(f"{path}: code block without code ({args})")
        if len(scene["code"]) > 18:
            raise ScriptError(f"{path}: {fname} has {len(scene['code'])} lines (max 18)")
        return scene

    if kind == "terminal":
        scene = {"type": "terminal", "heading": args, "steps": [], "beats": []}
        for raw in body:
            s = raw.rstrip()
            st = s.strip()
            if st.startswith("+ "):
                if not scene["steps"]:
                    raise ScriptError(f"{path}: continuation before a command")
                scene["steps"][-1]["cont"].append(st[2:])
            elif st.startswith("$ "):
                scene["steps"].append({"cmd": st[2:], "cont": [], "out": []})
                scene["beats"].append({"step": len(scene["steps"]) - 1, "part": "cmd", "say": None})
            elif st.startswith("|"):
                if not scene["steps"]:
                    raise ScriptError(f"{path}: output before a command")
                step = scene["steps"][-1]
                if not step["out"]:
                    scene["beats"].append({"step": len(scene["steps"]) - 1, "part": "out", "say": None})
                step["out"].append(st[1:].lstrip() if st != "|" else "")
            elif st.startswith(">"):
                # attach narration to the latest command/output beat without one
                for b in reversed(scene["beats"]):
                    if b["say"] is None:
                        b["say"] = st[1:].strip()
                        break
                else:
                    scene["beats"].append({"say": st[1:].strip(), "step": None, "part": None})
            elif st:
                raise ScriptError(f"{path}: unexpected line in terminal: {st}")
        for b in scene["beats"]:
            b["say"] = b["say"] or ""
        return scene

    if kind in ("practice", "interview"):
        scene = {"type": kind, "level": args or None, "q": "", "qsay": None, "qcode": None,
                 "acode": None, "items": [], "beats": []}
        in_answer = kind == "interview"
        j = 0
        while j < len(body):
            s = body[j].strip()
            if s.startswith("q:"):
                scene["q"] = s[2:].strip()
            elif s.startswith("qsay:"):
                scene["qsay"] = s[5:].strip()
            elif s.startswith("a:"):
                in_answer = True
            elif s.startswith("```"):
                lang, code, j = take_fence(body, j)
                scene["acode" if in_answer else "qcode"] = {"lang": lang, "code": code}
                continue
            elif s.startswith("- "):
                scene["items"].append(s[2:])
            elif s.startswith(">"):
                scene["beats"].append({"say": s[1:].strip(), "item": len(scene["items"]) - 1})
            elif s:
                raise ScriptError(f"{path}: unexpected line in {kind}: {s}")
            j += 1
        if not scene["q"]:
            raise ScriptError(f"{path}: {kind} without q:")
        return scene

    if kind == "project":
        scene = {"type": "project", "heading": args, "items": [], "beats": [], "endpoints": None, "stretch": ""}
        j = 0
        while j < len(body):
            st = body[j].strip()
            if st.startswith("```"):
                lang, code, j = take_fence(body, j)
                scene["endpoints"] = code
                continue
            if st.startswith("- "):
                scene["items"].append(st[2:])
            elif st.startswith("stretch:"):
                scene["stretch"] = st[8:].strip()
            elif st.startswith(">"):
                scene["beats"].append({"say": st[1:].strip(), "item": len(scene["items"]) - 1})
            elif st:
                raise ScriptError(f"{path}: unexpected line in project: {st}")
            j += 1
        return scene

    raise ScriptError(f"{path}: unknown block type '{kind}'")


def speakable(text):
    """Strip display markup so a question can be read aloud."""
    t = re.sub(r"`([^`]*)`", r"\1", text)
    t = t.replace("**", "")
    return t
