# AI Agents with Python — Beginner to Production (2026)

A YouTube course in 18 modules, produced one module at a time. Every module has narrated videos,
captions, a fully implemented and tested practical project, a quiz, an extension challenge and
YouTube packaging.

- Syllabus: [COURSE_SYLLABUS.md](COURSE_SYLLABUS.md)
- Glossary of every term: [GLOSSARY.md](GLOSSARY.md)
- Visual identity: [COURSE_DESIGN_SYSTEM.md](COURSE_DESIGN_SYSTEM.md)
- Progress (machine-readable): [COURSE_MANIFEST.json](COURSE_MANIFEST.json) · human-readable: [progress.md](progress.md)

## How a module is produced

```text
modules/module-NN-*/scripts/lesson-XX.yaml     lesson script: scenes + narration beats
        │  python tools/build_lesson.py NN XX
        ▼   • Kokoro TTS narration (cached in shared/tts_cache)
            • real command output captured for every terminal / >>> scene
            • syntax highlighting, music bed + sound effects, -16 LUFS mix
            • captions/lesson-XX.srt, studio/src/data/mNN-lXX.json
studio/  (Remotion 4)  one composition per lesson, 1920x1080 @ 60 fps
        │  python tools/module.py render NN
        ▼
modules/module-NN-*/renders/lesson-XX.mp4  (H.264 + AAC)
        │  python tools/module.py assemble NN     → module-NN-full.mp4, merged captions, chapters
        │  python tools/module.py validate NN     → validation-report.md
        ▼
COURSE_MANIFEST.json updated only after validation passes (tools/manifest.py)
```

Visual QA: `node studio/snapshots.mjs mNN-lXX` renders one still per scene into `logs/snapshots/`.
Thumbnails: `npx remotion still src/index.ts thumb-mNN <png>` (run in `studio/`).

## Requirements

- Python 3.11+ with `kokoro-onnx soundfile numpy pygments pyyaml` for building lessons
  (the Kokoro model files are read from `~/.cache/hyperframes/tts`, installed by HyperFrames)
- Node 22 + `npm install` in `studio/`; Chromium headless shell (path in `studio/remotion.config.ts`)
- ffmpeg / ffprobe
- `.venv/` (course virtual environment) with the pinned project dependencies, used to run every demo

## Tools: what is used for what

- **Remotion 4.0.538**: all lesson compositions, animation, rendering and thumbnails.
- **HyperFrames 0.8.x** (installed in this workspace): its local Kokoro TTS model is the narration
  voice. Its HTML video engine was used for the earlier FastAPI course; Remotion is the primary
  engine for this course as requested.
- **Claude Code**: curriculum, code, scripts, verification, orchestration.
