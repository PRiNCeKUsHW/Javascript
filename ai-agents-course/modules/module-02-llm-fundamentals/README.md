# Module 2: LLM Fundamentals and API Integration

Part I, Foundations · **AI Agents with Python: Beginner to Production (2026)**

How language models work and how to call them from Python reliably: tokens, context windows,
message history, output limits, streaming, structured output, errors, rate limits, retries and costs.
It ends with a complete, tested project.

> **Video language:** the videos are narrated in **Hinglish** (Hindi + English) with Hinglish captions.
> On-screen text, code and these docs are in English.

> **About the demos:** no API key was used while recording. Every reply on screen comes from the
> project's offline fake API (`project/ai-study-assistant/study/fake_api.py`), which speaks the Messages
> API protocol, so the real Anthropic SDK code runs unchanged. Replies are marked
> `(offline demo reply)` and offline token counts are estimates. With `ANTHROPIC_API_KEY` set, the same
> code calls Claude (default model `claude-opus-5-5`).

## Learning objectives

- Explain next-token prediction, tokens and context windows, and why the model has no memory
- Call the Messages API with the official SDK and read content blocks, `stop_reason` and `usage`
- Manage multi-turn history and its growing cost
- Control output: `max_tokens`, streaming, structured output with Pydantic, refusals
- Handle errors, rate limits and retries; calculate and budget costs

## Prerequisites

Module 1 (or comfortable basic Python). Python 3.11+. An Anthropic API key is optional.

## Lessons

| # | Video | Length | Script | Runnable code |
|---|---|---|---|---|
| 1 | How LLMs Work: Tokens, Context Windows and Generation | 5:35 | `scripts/lesson-01.yaml` | concepts |
| 2 | Your First API Call: Keys, Requests and Responses | 5:30 | `scripts/lesson-02.yaml` | `source/lesson-02/` |
| 3 | Conversations: Message History and the Growing Context | 3:54 | `scripts/lesson-03.yaml` | `source/lesson-03/` |
| 4 | Controlling Output: Limits, Streaming and Structured JSON | 5:42 | `scripts/lesson-04.yaml` | `source/lesson-04/` |
| 5 | Production Basics: Errors, Rate Limits, Retries and Costs | 6:42 | `scripts/lesson-05.yaml` | `source/lesson-05/` |
| 6 | Project, Part 1: AI Study Assistant, Client, Costs and Explanations | 6:03 | `scripts/lesson-06.yaml` | `project/ai-study-assistant/` |
| 7 | Project, Part 2: Quizzes, Chat, Tests and Wrap-up | 7:37 | `scripts/lesson-07.yaml` | `project/ai-study-assistant/` |

Total: about 41 minutes. Plan: [lesson-plan.md](lesson-plan.md). The lesson scripts use
`source/lesson-NN/offline.py`: a real client with a key, the offline fake without.

## Project: AI Study Assistant

[`project/ai-study-assistant/`](project/ai-study-assistant/README.md): explain (streaming), quiz
(structured output + grading), chat (trimmed history), tokens; cost per call, budget, error mapping,
SDK retries, refusal fallbacks. 23 pytest tests, mypy clean.

## Deliverables

| What | Where |
|---|---|
| Lesson videos (1920×1080, 60 fps, H.264 + AAC) | `renders/lesson-01.mp4` … `lesson-07.mp4` (not committed) |
| Full module video | `renders/module-02-full.mp4` (not committed) |
| Narration scripts / audio | `scripts/*.yaml` / `audio/` (audio not committed) |
| Captions | `captions/lesson-NN.srt`, `captions/module-02-full.srt` |
| Quiz + answer key | [quiz.md](quiz.md) |
| Question bank: every question from the videos, answers hidden (47) | [QUESTIONS.md](QUESTIONS.md) |
| Thumbnail | `assets/thumbnail-module-02.png` |
| YouTube packaging | [youtube.md](youtube.md), [youtube-uploads.md](youtube-uploads.md) |
| Validation report | [validation-report.md](validation-report.md) |

## Versions used

Python 3.13 · anthropic 2.3.0 · pydantic 2.14.1 · pytest 9.2.0 · mypy 2.4.1 · Remotion 4.0.538 ·
Kokoro v1.0 (voice `am_michael`). Prices: October 2026 list prices.
