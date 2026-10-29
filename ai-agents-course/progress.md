# Course progress

Source of truth: `COURSE_MANIFEST.json` (update only with `tools/manifest.py`, and only after real checks).

## Module 1: Python for AI Engineering: COMPLETED

- 7 lessons rendered (1920x1080, 60 fps, H.264 + AAC, about -17 LUFS); full module video 56:58 with 66 chapters
- `validation-report.md`: 69/69 checks passed (formats, durations, captions, loudness, no black frames,
  no long silences, fresh-venv install, 42 tests, mypy, documented CLI commands)
- Lessons 4 and 5 were re-rendered after a fix: compare scenes now show dimmed panels during intro narration
- Videos and audio are not in git (too large); they were delivered from the cloud session

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
