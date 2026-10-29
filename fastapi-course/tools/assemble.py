"""Join rendered chapters into one full-course video, with YouTube timestamps and merged subtitles.

usage: python tools/assemble.py            # every renders/chNN.mp4 that exists, in order
outputs: renders/fastapi-full-course.mp4, .srt, renders/youtube-chapters.txt, renders/descriptions/chNN.txt
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS = ROOT / "renders"
BUILD = ROOT / "build"
KIND_PREFIX = {"practice": "Challenge", "interview": "Interview", "project": "Project", "mistake": "Common mistake"}


def stamp(t: float) -> str:
    t = int(t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def srt_blocks(path: Path):
    for block in re.split(r"\n\s*\n", path.read_text().strip()):
        lines = block.splitlines()
        if len(lines) >= 3:
            yield lines[1], lines[2:]


def to_sec(ts: str) -> float:
    h, m, rest = ts.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def to_ts(t: float) -> str:
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chapter_description(meta: dict) -> str:
    """Per-episode YouTube description with scene timestamps (first stamp must be 00:00)."""
    lines = [f"Level {meta['chapter']}: {meta['title']} | FastAPI Zero to Production", ""]
    seen = set()
    for sc in meta["scenes"]:
        if sc["kind"] in ("divider", "complete"):
            continue
        label = sc["label"]
        if sc["kind"] in ("practice", "interview"):
            label = {"practice": "Practice challenges", "interview": "Mock interview (boss round)"}[sc["kind"]]
            if label in seen:
                continue
        elif sc["kind"] in KIND_PREFIX and not label.lower().startswith(KIND_PREFIX[sc["kind"]].lower()):
            label = f"{KIND_PREFIX[sc['kind']]}: {label}"
        seen.add(label)
        lines.append(f"{stamp(sc['t'])} {label}")
    return "\n".join(lines) + "\n"


def main():
    parts = sorted(RENDERS.glob("ch[0-9][0-9].mp4"))
    if not parts:
        raise SystemExit("no renders/chNN.mp4 yet")
    (RENDERS / "descriptions").mkdir(exist_ok=True)
    offset, toc, subs = 0.0, [], []
    for mp4 in parts:
        ch = mp4.stem
        meta = json.loads((BUILD / ch / "chapters.json").read_text())
        (RENDERS / "descriptions" / f"{ch}.txt").write_text(chapter_description(meta))
        name = "Welcome & course plan" if meta["chapter"] == 0 else f"Level {meta['chapter']}: {meta['title']}"
        toc.append(f"{stamp(offset)} {name}")
        srt = RENDERS / f"{ch}.srt"
        if srt.exists():
            for times, text in srt_blocks(srt):
                a, b = (to_sec(x.strip()) for x in times.split("-->"))
                subs.append((a + offset, b + offset, text))
        offset += duration(mp4)

    listing = RENDERS / "concat.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in parts))
    out = RENDERS / "fastapi-full-course.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    listing.unlink()
    (RENDERS / "fastapi-full-course.srt").write_text(
        "\n".join(f"{i}\n{to_ts(a)} --> {to_ts(b)}\n" + "\n".join(t) + "\n" for i, (a, b, t) in enumerate(subs, 1)))
    (RENDERS / "youtube-chapters.txt").write_text("\n".join(toc) + "\n")
    print(f"{out.name}: {len(parts)} chapters, {stamp(offset)}")
    print("\n".join(toc))


if __name__ == "__main__":
    main()
