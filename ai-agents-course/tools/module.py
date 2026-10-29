"""Render, assemble and validate a whole module.

usage:
  python tools/module.py render 1 [lesson ...]   # render lesson videos (skips ones that are up to date)
  python tools/module.py assemble 1              # full module video, merged captions, YouTube chapters
  python tools/module.py validate 1              # checks everything and writes validation-report.md
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "studio"
VENV_BIN = ".venv/Scripts" if sys.platform == "win32" else ".venv/bin"  # relative to each project folder
VENV_PY = ROOT / VENV_BIN / ("python.exe" if sys.platform == "win32" else "python")


def module_dir(m):
    return next((ROOT / "modules").glob(f"module-{m:02d}-*"))


def lesson_ids(m):
    return sorted(int(p.stem.split("-")[1]) for p in (module_dir(m) / "scripts").glob("lesson-*.yaml"))


def data(m, lesson):
    return json.loads((STUDIO / f"src/data/m{m:02d}-l{lesson:02d}.json").read_text())


def stamp(t):
    t = int(t)
    h, rem = divmod(t, 3600)
    mnt, s = divmod(rem, 60)
    return f"{h}:{mnt:02d}:{s:02d}" if h else f"{mnt:02d}:{s:02d}"


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                          "-show_entries", "format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


# ---------------------------------------------------------------- render
def render(m, lessons):
    out_dir = module_dir(m) / "renders"
    out_dir.mkdir(exist_ok=True)
    for lesson in lessons or lesson_ids(m):
        src = STUDIO / f"src/data/m{m:02d}-l{lesson:02d}.json"
        out = out_dir / f"lesson-{lesson:02d}.mp4"
        if out.exists() and out.stat().st_mtime > src.stat().st_mtime:
            print(f"lesson {lesson}: up to date")
            continue
        start = time.time()
        tmp = out.with_suffix(".partial.mp4")
        subprocess.run(["npx", "remotion", "render", "src/index.ts", f"m{m:02d}-l{lesson:02d}", str(tmp),
                        "--codec=h264", "--crf=18", "--audio-codec=aac", "--audio-bitrate=192k",
                        "--log=error"], cwd=STUDIO, check=True)
        tmp.replace(out)
        print(f"lesson {lesson}: rendered in {(time.time() - start) / 60:.1f} min -> {out}")


# ---------------------------------------------------------------- assemble
def srt_blocks(path):
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = block.splitlines()
        if len(lines) >= 3:
            yield lines[1], lines[2:]


def to_sec(ts):
    h, mm, rest = ts.strip().split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(mm) * 60 + int(s) + int(ms) / 1000


def to_ts(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    mm, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{mm:02d}:{s:02d},{ms:03d}"


def assemble(m):
    mdir = module_dir(m)
    renders = mdir / "renders"
    lessons = lesson_ids(m)
    offset, subs, chapters, lesson_chapters = 0.0, [], [], {}
    for lesson in lessons:
        mp4 = renders / f"lesson-{lesson:02d}.mp4"
        d = data(m, lesson)
        dur = float(probe(mp4)["format"]["duration"])
        lesson_chapters[lesson] = [f"{stamp(c['t'])} {c['title']}" for c in d["chapters"]]
        for c in d["chapters"]:
            title = f"L{lesson} · {d['title']}" if c["t"] == 0 else c["title"]
            chapters.append((offset + c["t"], title))
        for times, text in srt_blocks(mdir / f"captions/lesson-{lesson:02d}.srt"):
            a, b = (to_sec(x) for x in times.split("-->"))
            subs.append((a + offset, b + offset, text))
        offset += dur
    listing = renders / "concat.txt"
    listing.write_text("".join(f"file 'lesson-{n:02d}.mp4'\n" for n in lessons))
    full = renders / f"module-{m:02d}-full.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                    "-c", "copy", "-movflags", "+faststart", str(full)], check=True)
    listing.unlink()
    (mdir / f"captions/module-{m:02d}-full.srt").write_text(
        "\n".join(f"{i}\n{to_ts(a)} --> {to_ts(b)}\n" + "\n".join(t) + "\n" for i, (a, b, t) in enumerate(subs, 1)),
        encoding="utf-8")
    # YouTube needs >= 10 s between chapters: merge chapters that are too close
    yt, last = [], -99.0
    for t, title in chapters:
        if t - last >= 10:
            yt.append((t, title))
            last = t
    (renders / "chapters.json").write_text(json.dumps(
        {"full": [{"t": round(t, 2), "title": x} for t, x in yt], "lessons": lesson_chapters}, indent=2))
    print(f"{full.name}: {stamp(offset)}, {len(yt)} chapters, {len(subs)} captions")
    return yt


# ---------------------------------------------------------------- validate
def run(cmd, cwd, **kw):
    if isinstance(cmd, str) and sys.platform == "win32":
        # the shell steps need POSIX sh (Git Bash), not cmd.exe; python3 there is the Microsoft Store stub
        cmd = ["bash", "-c", cmd.replace("python3 ", "python ")]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str), **kw)


def validate(m):
    mdir = module_dir(m)
    results, problems = [], []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))
        if not ok:
            problems.append(f"{name}: {detail}")

    lessons = lesson_ids(m)
    for lesson in lessons:
        d = data(m, lesson)
        tag = f"lesson {lesson}"
        audio = STUDIO / "public" / d["audio"]
        srt = mdir / f"captions/lesson-{lesson:02d}.srt"
        mp4 = mdir / f"renders/lesson-{lesson:02d}.mp4"
        check(f"{tag} narration audio", audio.exists() and audio.stat().st_size > 100_000, str(audio.name))
        caps = list(srt_blocks(srt)) if srt.exists() else []
        times = [tuple(to_sec(x) for x in t.split("-->")) for t, _ in caps]
        ordered = all(a < b for a, b in times) and all(times[i][1] <= times[i + 1][0] + 1e-6
                                                       for i in range(len(times) - 1))
        within = bool(times) and times[-1][1] <= d["durationInFrames"] / d["fps"]
        check(f"{tag} captions", bool(caps) and ordered and within, f"{len(caps)} cues, ordered={ordered}")
        if not mp4.exists():
            check(f"{tag} video", False, "not rendered")
            continue
        info = probe(mp4)
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
        dur = float(info["format"]["duration"])
        expected = d["durationInFrames"] / d["fps"]
        check(f"{tag} video format", v["codec_name"] == "h264" and (v["width"], v["height"]) == (1920, 1080)
              and v["r_frame_rate"] == "60/1", f"{v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']}")
        check(f"{tag} audio track", a is not None and a["codec_name"] == "aac",
              f"{a['codec_name']} {a['sample_rate']} Hz {a['channels']} ch" if a else "missing")
        check(f"{tag} duration", abs(dur - expected) < 0.5, f"{stamp(dur)} (timeline {expected:.1f} s)")
        black = run(["ffmpeg", "-v", "info", "-i", str(mp4), "-vf", "blackdetect=d=0.5:pix_th=0.02",
                     "-an", "-f", "null", "-"], ROOT).stderr
        n_black = black.count("black_start")
        check(f"{tag} no black frames", n_black == 0, f"{n_black} black segments")
        loud = run(["ffmpeg", "-v", "info", "-i", str(mp4), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                   ROOT).stderr
        lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", loud)
        peak = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", loud)
        il = float(lufs[-1]) if lufs else -99
        tp = float(peak[-1]) if peak else 99
        check(f"{tag} loudness", -18 <= il <= -14 and tp <= -0.5, f"{il} LUFS, true peak {tp} dBFS")
        silent = run(["ffmpeg", "-v", "info", "-i", str(mp4), "-vn", "-af", "silencedetect=n=-45dB:d=6",
                      "-f", "null", "-"], ROOT).stderr.count("silence_start")
        check(f"{tag} no long silences", silent == 0, f"{silent} gaps of 6 s+ below -45 dB")

    full = mdir / f"renders/module-{m:02d}-full.mp4"
    check("full module video", full.exists(), full.name)
    thumb = mdir / f"assets/thumbnail-module-{m:02d}.png"
    check("thumbnail", thumb.exists(), thumb.name)
    for f in ["README.md", "lesson-plan.md", "quiz.md", "youtube.md"]:
        check(f"{f} present", (mdir / f).exists(), f)

    # the project: fresh virtual environment, documented install, tests, type check, documented commands
    for proj in sorted((mdir / "project").iterdir()):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp) / proj.name
            shutil.copytree(proj, work, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache",
                                                                     ".mypy_cache"))
            steps = [
                ("venv + pip install -r requirements.txt",
                 f"python3 -m venv .venv && {VENV_BIN}/pip install -q --disable-pip-version-check -r requirements.txt"),
                ("pytest", f"{VENV_BIN}/python -m pytest -q -p no:cacheprovider"),
                ("mypy", f"{VENV_BIN}/mypy --no-incremental toolkit"),
                ("validate sample (exit 0)", f"{VENV_BIN}/python -m toolkit validate data/usage_sample.json"),
                ("validate broken (exit 1)",
                 f"{VENV_BIN}/python -m toolkit validate data/usage_broken.json; test $? -eq 1"),
                ("report md",
                 f"{VENV_BIN}/python -m toolkit report data/usage_sample.json | grep -q 'Requests: 10'"),
                ("report json --out", f"{VENV_BIN}/python -m toolkit report data/usage_sample.json --format json "
                                      "--out reports/u.json && python3 -m json.tool reports/u.json > /dev/null"),
            ]
            for name, cmd in steps:
                p = run(cmd, work, timeout=600)
                tail = (p.stdout + p.stderr).strip().splitlines()[-1:] if (p.stdout + p.stderr).strip() else [""]
                check(f"project {proj.name}: {name}", p.returncode == 0, tail[0][:120])

    passed = sum(ok for _, ok, _ in results)
    lines = [f"# Module {m} validation report", "",
             f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. {passed}/{len(results)} checks passed.", "",
             "| Check | Result | Detail |", "|---|---|---|"]
    lines += [f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n, ok, d in results]
    (mdir / "validation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[2:3]))
    for p in problems:
        print("FAIL", p)
    return not problems


if __name__ == "__main__":
    action, m = sys.argv[1], int(sys.argv[2])
    if action == "render":
        render(m, [int(x) for x in sys.argv[3:]])
    elif action == "assemble":
        assemble(m)
    elif action == "validate":
        sys.exit(0 if validate(m) else 1)
