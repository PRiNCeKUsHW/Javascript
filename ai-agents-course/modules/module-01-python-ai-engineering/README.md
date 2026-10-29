# Module 1: Python for AI Engineering

Part I, Foundations · **AI Agents with Python: Beginner to Production (2026)**

The Python that AI engineering actually uses, taught through one running example: LLM usage
data (chat messages, model settings, request logs). It ends with a complete, tested CLI project.

## Learning objectives

- Use variables, strings, lists, dictionaries, sets and comprehensions; model a chat
  conversation as a list of `{"role", "content"}` dictionaries.
- Write functions, classes, dataclasses and custom exceptions; avoid the mutable-default bug;
  read tracebacks.
- Organise code into modules and packages; read/write files with `pathlib`; convert JSON;
  keep configuration and secrets in environment variables and `.env` files.
- Add type hints and check them with mypy; make HTTP requests with `httpx`; run concurrent
  work with `async`/`await` and `asyncio.gather`.
- Build, demo, test and troubleshoot a multi-module command-line tool.

## Prerequisites and setup

Windows, macOS or Linux; Python 3.11+ (recorded with 3.13.17); a code editor (e.g. VS Code
with the Python extension). No AI experience required. Setup is taught in lesson 1.

## Lessons

| # | Video | Length | Script | Runnable code |
|---|---|---|---|---|
| 1 | Welcome, the Agent Loop, and Your Python Setup | 7:10 | `scripts/lesson-01.yaml` | project preview |
| 2 | Python Core Data: Variables, Lists, Dictionaries and Sets | 7:20 | `scripts/lesson-02.yaml` | `source/lesson-02/` |
| 3 | Functions, Classes and Exceptions | 8:25 | `scripts/lesson-03.yaml` | `source/lesson-03/` |
| 4 | Modules, Packages, Files, JSON and Environment Variables | 7:31 | `scripts/lesson-04.yaml` | `source/lesson-04/` |
| 5 | Type Hints, HTTP Requests and Async | 7:20 | `scripts/lesson-05.yaml` | `source/lesson-05/` |
| 6 | Project, Part 1: Plan, Data Model and Validation | 8:27 | `scripts/lesson-06.yaml` | `project/python-ai-toolkit/` |
| 7 | Project, Part 2: Reports, CLI, Tests and Wrap-up | 10:42 | `scripts/lesson-07.yaml` | `project/python-ai-toolkit/` |

Total: about 57 minutes. Detailed plan: [lesson-plan.md](lesson-plan.md).

## Project: Python AI Toolkit

[`project/python-ai-toolkit/`](project/python-ai-toolkit/README.md) is a CLI that validates a JSON
log of LLM API calls and reports requests, success rate, tokens, estimated cost, latency and top
tags as Markdown or JSON, and downloads several logs concurrently. 42 pytest tests (HTTP mocked
with `httpx.MockTransport`) and a clean mypy run.

```bash
cd project/python-ai-toolkit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m toolkit report data/usage_sample.json
python -m pytest -q
```

## Deliverables

| What | Where |
|---|---|
| Lesson videos (1920×1080, 60 fps, H.264 + AAC) | `renders/lesson-01.mp4` … `lesson-07.mp4` (not committed: large) |
| Full module video | `renders/module-01-full.mp4` (not committed) |
| Narration scripts | `scripts/lesson-NN.yaml` (every `say:` field) |
| Narration audio | `audio/lesson-NN-narration.wav` (not committed; rebuilt by `tools/build_lesson.py`) |
| Captions | `captions/lesson-NN.srt`, `captions/module-01-full.srt` |
| Quiz + answer key | [quiz.md](quiz.md) |
| Thumbnail | `assets/thumbnail-module-01.png` |
| YouTube title, description, chapters, search terms | [youtube.md](youtube.md) |
| Validation report | [validation-report.md](validation-report.md) |

## Common errors covered

`TypeError` (str + int), `KeyError`, mutable default arguments, bare `except`, tracebacks,
`ModuleNotFoundError` (wrong folder, inactive virtual environment), `JSONDecodeError`, missing environment variables,
mypy errors, HTTP 404 / unreachable servers, PowerShell execution policy, relative paths, encodings.

## Extension challenge

Add `--top N`, p95 latency, a per-day breakdown or `--format csv`, each with a test. See [quiz.md](quiz.md).

## Official documentation

[Python tutorial](https://docs.python.org/3/tutorial/) ·
[venv](https://docs.python.org/3/library/venv.html) ·
[dataclasses](https://docs.python.org/3/library/dataclasses.html) ·
[json](https://docs.python.org/3/library/json.html) ·
[pathlib](https://docs.python.org/3/library/pathlib.html) ·
[asyncio](https://docs.python.org/3/library/asyncio.html) ·
[argparse](https://docs.python.org/3/library/argparse.html) ·
[HTTPX](https://www.python-httpx.org/) · [pytest](https://docs.pytest.org/) · [mypy](https://mypy.readthedocs.io/)

## Versions used

Python 3.13.17 · httpx 0.28.1 · pytest 9.2.0 · mypy 2.4.1 · Remotion 4.0.538 · Kokoro v1.0 (voice `am_michael`).
