"""Check the course code before rendering.

  python tools/verify_code.py           # all chapters
  python tools/verify_code.py 3 4       # some chapters

1. Every ```python block in content/chNN.md (lessons, challenge and boss-round code) must
   compile.
2. code/test_chNN.py, the runnable version of each chapter's examples, must pass under pytest.
"""
import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from course import parse_chapter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def blocks(scenes):
    for sc in scenes:
        if sc["type"] == "code" and sc.get("lang") in ("python", "py"):
            yield sc.get("heading") or sc["file"], sc["code"]
        for key in ("qcode", "acode"):
            c = sc.get(key)
            if c and c["lang"] in ("python", "py"):
                yield f'{sc["type"]}: {sc["q"][:50]}', c["code"]


def main(chapters):
    bad = 0
    for ch in chapters:
        path = ROOT / f"content/ch{ch:02d}.md"
        if not path.exists():
            continue
        _, scenes = parse_chapter(path)
        n = 0
        for label, code in blocks(scenes):
            n += 1
            try:
                compile("\n".join(code), f"ch{ch:02d}:{label}", "exec")
            except SyntaxError as e:
                bad += 1
                print(f"ch{ch:02d} {label}: {e}")
        print(f"ch{ch:02d}: {n} python blocks compiled")
    tests = [str(ROOT / f"code/test_ch{ch:02d}.py") for ch in chapters if (ROOT / f"code/test_ch{ch:02d}.py").exists()]
    if tests:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", *tests], cwd=ROOT / "code")
        bad += r.returncode != 0
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    args = [int(a) for a in sys.argv[1:]] or list(range(0, 13))
    main(args)
