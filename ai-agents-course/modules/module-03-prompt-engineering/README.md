# Module 3: Prompt Engineering and Structured Outputs

Part I, Foundations · **AI Agents with Python: Beginner to Production (2026)**

How to write prompts that behave consistently, get validated data back, split work between the model
and code, version prompts and measure every change with an evaluation set. Delivered as **one
full-module video** (about 30 minutes) and ends with a complete, tested project.

> **About the demos:** no API key was used while recording. Model replies on screen come from the
> project's offline fake API (`project/ai-resume-analyzer/resume/fake_api.py`), which fills the
> requested schema with keyword rules. **It is not a model**: it ignores prompt wording and misses
> negation, so offline eval scores cannot compare prompt versions (the video says so). With
> `ANTHROPIC_API_KEY` set, the same code calls Claude (default model `claude-opus-5-5`).

## Learning objectives

- Name the parts of a prompt; turn vague requests into specific ones with context and reasons
- Recognise outdated advice: shouting, "think step by step", "reply only in JSON" + regex, prefill,
  reasoning fields in JSON
- Separate data from instructions with tags; use varied, labelled examples
- Split a task into model steps (judgment) and code steps (matching, scoring, formatting)
- Design Pydantic schemas; handle cut-off, invalid, refused and invented replies; check meaning in code
- Version prompts with fingerprints and a lock test; evaluate versions with labelled cases and a code grader

## Prerequisites

Module 2 (or equivalent). Python 3.11+. An Anthropic API key is optional.

## Video chapters

| # | Part | Length | Script | Runnable code |
|---|---|---|---|---|
| 1 | Prompt Anatomy: Instructions, Context and Constraints | 5:00 | `scripts/lesson-01.yaml` | `source/lesson-01/` |
| 2 | Examples, XML Tags and Task Decomposition | 4:46 | `scripts/lesson-02.yaml` | `source/lesson-02/` |
| 3 | Structured Outputs: Pydantic Schemas and Parsing Failures | 4:32 | `scripts/lesson-03.yaml` | `source/lesson-03/` |
| 4 | Prompt Versioning and Evaluations | 5:20 | `scripts/lesson-04.yaml` | project |
| 5 | Project, Part 1: Extraction and Comparison | 4:23 | `scripts/lesson-05.yaml` | `project/ai-resume-analyzer/` |
| 6 | Project, Part 2: Reports, Demo, Tests and Wrap-up | 6:30 | `scripts/lesson-06.yaml` | `project/ai-resume-analyzer/` |

Total: 30:32. Plan: [lesson-plan.md](lesson-plan.md).

## Project: AI Resume Analyzer

[`project/ai-resume-analyzer/`](project/ai-resume-analyzer/README.md): compares a resume with a job
posting and writes a skills-gap report (Markdown or JSON). Versioned prompts with fingerprints and a
lock test, structured outputs into Pydantic models, comparison and scoring in code, a grounding check,
an evaluation command, cost tracking, SDK retries. 27 pytest tests, mypy clean.

## Deliverables

| What | Where |
|---|---|
| Full module video (1920×1080, 60 fps, H.264 + AAC) | `renders/module-03-full.mp4` (not committed) |
| Narration scripts / audio | `scripts/*.yaml` / `audio/` (audio not committed) |
| Captions | `captions/module-03-full.srt` (and per part: `captions/lesson-NN.srt`) |
| Quiz + answer key + challenge | [quiz.md](quiz.md) |
| Thumbnail | `assets/thumbnail-module-03.png` |
| YouTube packaging | [youtube.md](youtube.md), [youtube-uploads.md](youtube-uploads.md) |
| Validation report | [validation-report.md](validation-report.md) |

## Versions used

Python 3.13 · anthropic 2.3.0 · pydantic 2.14.1 · pytest 9.2.0 · mypy 2.4.1 · Remotion 4.0.538 ·
Kokoro v1.0 (voice `am_michael`). Prices: October 2026 list prices.
