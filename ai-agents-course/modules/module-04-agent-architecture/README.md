# Module 4: AI Agent Architecture

Part II, Build Agents from Scratch · **AI Agents with Python: Beginner to Production (2026)**

What an AI agent is, when to use one (and when not to), and how to build one from scratch: the model,
the instructions, the tools and the state, connected by the agent loop (decide, act, observe, repeat)
with safe stopping. Delivered as **one full-module video** (36:45) with **beginner pacing**: a slower
voice, longer pauses, every new term explained, and a "Pause and try" moment in every part.

> **About the demos:** no API key was used while recording. Model turns on screen come from the
> project's offline fake API (`project/smart-calculator-agent/calc_agent/fake_api.py`), a fixed script
> that is **not a model**: it finds arithmetic and unit conversions in the question and asks for one tool
> per turn. The tools and the agent loop are real code. With `ANTHROPIC_API_KEY` set, the same code calls
> Claude (default model `claude-opus-5-5`).

## Learning objectives

- Tell a chatbot, a workflow and an agent apart, and choose the simplest design that works
- Name the four parts of an agent; read a tool definition and a `tool_use` block
- Write the agent loop: decide, act, observe with matching `tool_use_id`, stop when no tools are requested
- Stop safely: step limits, budgets, refusals, cut-off replies, clear errors
- Treat tool errors as observations (`is_error`); never `eval` tool input (allow-list instead)

## Prerequisites

Modules 2 and 3 (or equivalent). Python 3.11+. An Anthropic API key is optional. New terms are in the
course [glossary](../../GLOSSARY.md).

## Video chapters

| # | Part | Length | Script | Runnable code |
|---|---|---|---|---|
| 1 | Chatbots, Workflows and Agents | 5:28 | `scripts/lesson-01.yaml` | concepts |
| 2 | Inside an Agent: Model, Instructions, Tools and State | 6:26 | `scripts/lesson-02.yaml` | `source/lesson-02/` |
| 3 | The Agent Loop: Decide, Act, Observe, Repeat | 4:49 | `scripts/lesson-03.yaml` | `source/lesson-03/` |
| 4 | Stopping Safely: Step Limits, Tool Errors and Safe Tools | 6:38 | `scripts/lesson-04.yaml` | `source/lesson-04/`, project |
| 5 | Project, Part 1: Tools and the Loop | 6:00 | `scripts/lesson-05.yaml` | `project/smart-calculator-agent/` |
| 6 | Project, Part 2: Traces, Demo, Tests and Wrap-up | 7:22 | `scripts/lesson-06.yaml` | `project/smart-calculator-agent/` |

Total: 36:45. Plan: [lesson-plan.md](lesson-plan.md).

## Project: Smart Calculator Agent

[`project/smart-calculator-agent/`](project/smart-calculator-agent/README.md): an agent loop built by
hand with two tools (an allow-list calculator and a unit converter), a trace of every action, a step
limit, a budget and one clear message for every ending. 34 pytest tests, mypy clean.

## Deliverables

| What | Where |
|---|---|
| Full module video (1920×1080, 60 fps, H.264 + AAC) | `renders/module-04-full.mp4` (not committed) |
| Narration scripts / audio | `scripts/*.yaml` / `audio/` (audio not committed) |
| Captions | `captions/module-04-full.srt` (and per part: `captions/lesson-NN.srt`) |
| Quiz, pause-and-try answers, challenge | [quiz.md](quiz.md) |
| Question bank: every question from the videos, answers hidden (21) | [QUESTIONS.md](QUESTIONS.md) |
| Thumbnail | `assets/thumbnail-module-04.png` |
| YouTube packaging | [youtube.md](youtube.md), [youtube-uploads.md](youtube-uploads.md) |
| Validation report | [validation-report.md](validation-report.md) |

## Versions used

Python 3.13 · anthropic 2.3.0 · pydantic 2.14.1 · pytest 9.2.0 · mypy 2.4.1 · Remotion 4.0.538 ·
Kokoro v1.0 (voice `am_michael`, speed 0.92 from this module on).
