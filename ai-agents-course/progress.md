# Course progress

Source of truth: `COURSE_MANIFEST.json` (update only with `tools/manifest.py`, and only after real checks).

## Module 1: Python for AI Engineering: COMPLETED

- 7 lessons rendered (1920x1080, 60 fps, H.264 + AAC, about -17 LUFS); full module video 56:58 with 66 chapters
- `validation-report.md`: 69/69 checks passed (formats, durations, captions, loudness, no black frames,
  no long silences, fresh-venv install, 42 tests, mypy, documented CLI commands)
- Lessons 4 and 5 were re-rendered after a fix: compare scenes now show dimmed panels during intro narration
- Videos and audio are not in git (too large); they were delivered from the cloud session

## Local Windows machine (set up 2026-10-29)

- Git Bash runs the demo commands (no WSL). `tools/build_lesson.py` and `tools/module.py` pick
  `.venv/Scripts` on Windows, add a `python3` shim (the Windows `python3` is the Microsoft Store stub),
  and map `.venv/bin/` to `.venv/Scripts/` in `run:` commands. On Linux, nothing changes.
- Two environments. `.venv` (Python 3.14.3) runs every demo shown on screen. `.venv-tools`
  (Python 3.12, kokoro-onnx 0.6.1) runs the build tools, because kokoro-onnx ≥ 0.4.8 needs
  Python < 3.14. Run `.venv-tools/Scripts/python tools/build_lesson.py …` (and module.py the same way).
- Kokoro model: the default `~/.cache/hyperframes/tts` already has it; `KOKORO_DIR` isn't needed.
- Remotion downloads its own Chrome Headless Shell on the first render or still.
- Windows-built captures show Windows details (Python 3.14.3, `.venv/Scripts/python`). Module 1 was
  not rebuilt here. Module 2 lessons avoid OS-specific output where possible.
- Fixed: Module 1 `test_friendly_error_for_missing_file` now builds the expected path with `Path`, so it
  passes on Windows too (project code unchanged, so it still matches the videos).

## Next: Module 2: LLM Fundamentals and API Integration (project: AI Study Assistant)

Notes for the next modules, learned in Module 1:
- Keep project code ≤ 84 characters per line so code panels stay ≥ 27 px.
- Prefer `repl: true` terminal scenes for exploring objects; keep each statement ≤ ~85 characters.
- Terminal commands must fit one line (~95 characters at 28 px; set `font: 25` for longer ones).
- Links scenes: at most 8 items. Code `notes` sit beside short code, below wide code (≤ 2 short lines).
- Edge labels in diagrams sit on the curve midpoint; keep boxes off the curve paths.
- Never use a real API key in recorded output. Module 2 needs an LLM API: use a mock/fake transport
  for tests and recorded demos unless a key is configured in the environment; say clearly on screen
  which outputs come from a real model call.
