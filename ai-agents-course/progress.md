# Course progress

Source of truth: `COURSE_MANIFEST.json` (update only with `tools/manifest.py`, and only after real checks).

## Module 1: Python for AI Engineering (status: IN_PROGRESS → render finishing in the cloud session)

Done and verified:
- 7 lesson scripts (`scripts/lesson-01..07.yaml`), built: narration, captions, timelines (≈57 min total)
- Project `project/python-ai-toolkit`: 42 pytest tests pass, mypy clean, README
- Visual QA by still frames for every lesson; layout fixes applied
- Thumbnail `assets/thumbnail-module-01.png`; `youtube.md`, `youtube-uploads.md` (per-lesson titles,
  descriptions, chapters, tags, ChatGPT thumbnail prompts); `quiz.md`; `lesson-plan.md`; module README
- Rendered and checked so far (cloud session): lessons 1, 2, 3 (1920x1080, 60 fps, H.264 + AAC)

Remaining for Module 1 (being finished in the cloud session; videos are NOT in git):
- render lessons 4–7 → `python tools/module.py assemble 1` → `python tools/module.py validate 1`
- if every check passes: `python tools/manifest.py set 1 COMPLETED`

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
