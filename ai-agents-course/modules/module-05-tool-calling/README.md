# Module 5: Tool Calling and Function Execution

Part II, Build Agents from Scratch · **AI Agents with Python: Beginner to Production (2026)**

Tools are how an agent acts. This module goes deep on them: how a model requests a tool, how to define
and describe tools well, how to keep many tools in one registry with schemas generated from Pydantic,
how to run parallel tool calls, and how to make tool execution safe with validation, timeouts,
permission levels and human confirmation. It ends with a complete, tested project.

> **About the demos:** no API key was used while recording. Model turns on screen come from the
> project's offline fake API (`project/productivity-agent/productivity/fake_api.py`), a fixed script
> that is **not a model**: it matches simple phrases ("add task ...", "delete task 2") and asks for all
> the matching tools in one turn. The tools, validation, timeouts and permissions are real code. With
> `ANTHROPIC_API_KEY` set, the same code calls Claude (default model `claude-opus-5-5`).

## Learning objectives

- Explain tool calling: the model requests (`tool_use`), your code runs, the result returns by id
- Write clear tool definitions: name, description, input schema, `strict: true`
- Keep tools in a registry and generate strict schemas from Pydantic classes
- Handle parallel tool calls: run them all, return all results in one message
- Validate every input (strict mode covers shape; your code covers limits and business rules)
- Give every tool a timeout, and know the limits of thread timeouts
- Apply least privilege: read, write and danger levels, read-only mode, human approval

## Prerequisites

Module 4 (or equivalent). Python 3.11+. An Anthropic API key is optional. New terms are in the course
[glossary](../../GLOSSARY.md).

## Video chapters

| # | Part | Script | Runnable code |
|---|---|---|---|
| 1 | Tool Calling: How a Model Uses Your Functions | `scripts/lesson-01.yaml` | `source/lesson-01/` |
| 2 | Many Tools: A Registry, Schemas from Pydantic, Parallel Calls | `scripts/lesson-02.yaml` | `source/lesson-02/` |
| 3 | Validating Tool Inputs: Never Trust, Always Check | `scripts/lesson-03.yaml` | `source/lesson-03/`, project |
| 4 | Timeouts and Failures: When a Tool Never Answers | `scripts/lesson-04.yaml` | `source/lesson-04/`, project |
| 5 | Permissions and Human Confirmation: Ask Before You Act | `scripts/lesson-05.yaml` | `source/lesson-05/`, project |
| 6 | Project, Part 1: Store, Tools and Policy | `scripts/lesson-06.yaml` | `project/productivity-agent/` |
| 7 | Project, Part 2: The Loop, the Demo, Tests and Wrap-up | `scripts/lesson-07.yaml` | `project/productivity-agent/` |

Plan: [lesson-plan.md](lesson-plan.md). Every lesson follows the course teaching style
([TEACHING_STYLE.md](../../TEACHING_STYLE.md)): an analogy, code on the left with its real output on
the right, dry-run tables, a pause-and-try, an interview corner and a quick check.

## Project: Personal Productivity Agent

[`project/productivity-agent/`](project/productivity-agent/README.md): six tools for tasks and notes in
a registry, schemas from Pydantic, validation, per-tool timeouts, read/write/danger permissions with a
read-only mode and human approval for deletes, parallel tool calls, and an atomic JSON store. 43 pytest
tests, mypy clean.

## Deliverables

| What | Where |
|---|---|
| Full module video (1920×1080, 60 fps, H.264 + AAC) | `renders/module-05-full.mp4` (not committed) |
| Narration scripts / audio | `scripts/*.yaml` / `audio/` (audio not committed) |
| Captions | `captions/module-05-full.srt` (and per part: `captions/lesson-NN.srt`) |
| Quiz, practice answers, challenge | [quiz.md](quiz.md) |
| Question bank: every question from the videos, answers hidden (39) | [QUESTIONS.md](QUESTIONS.md) |
| Thumbnail | `assets/thumbnail-module-05.png` |
| YouTube packaging | [youtube.md](youtube.md) |
| Validation report | [validation-report.md](validation-report.md) |

## Versions used

Python 3.13 · anthropic 2.3.0 · pydantic 2.14.1 · pytest 9.2.0 · mypy 2.4.1 · Remotion 4.0.538 ·
Kokoro v1.0 (English voice `am_michael`, speed 0.92) · light "Paper" theme.
