# Module 2 lesson plan: LLM Fundamentals and API Integration

Audience: learners who finished Module 1 (or know basic Python). Target level: call a language model
from Python reliably, with streaming, structured output, history, error handling, retries and cost
control, in a tested program.

Provider: Anthropic Claude via the official Python SDK (`anthropic==2.3.0`), default model
`claude-opus-5-5`. API facts (models, prices, parameters) were checked against the official SDK
documentation and the installed SDK; prices are October 2026 list prices.

**Honesty rule for demos:** no API key was available while recording. Every reply shown on screen comes
from the project's offline fake API (`study/fake_api.py`), which speaks the Messages API protocol so the
**real SDK code runs unchanged**. Replies are marked `(offline demo reply)`, token counts are labelled
estimates, and the narration says so explicitly (lesson 2 callout, demos in lessons 3-7).

| # | Lesson | Concepts | Runnable source |
|---|---|---|---|
| 1 | How LLMs work | next-token prediction loop, plausible text vs facts (hallucination, cut-off), tokens (illustrative split, ~4 chars/token, `count_tokens`), why tokens matter (cost, limits, speed), context window (1M on Opus 5.5, 128K output), no memory between requests, controls (system, max_tokens, effort, model; sampling params not accepted on current models) | concepts only |
| 2 | First API call | key creation and storage, SDK install, offline mode explained, `messages.create` (model, max_tokens, messages), response anatomy (id, model, role, content blocks, stop_reason, usage), block types (text, thinking, tool_use), system prompt | `source/lesson-02/` |
| 3 | Conversations | stateless API, alternating roles, history list, input tokens grow per turn, forgotten-reply bug (consecutive user turns are merged), sliding window / summary / stored facts / prompt caching, trim in pairs | `source/lesson-03/` |
| 4 | Controlling output | stop reasons (end_turn, max_tokens, refusal, stop_sequence, tool_use, pause_turn), `max_tokens` truncation, streaming with `messages.stream` / `text_stream` / `get_final_message`, structured outputs with `messages.parse(output_format=...)` + Pydantic (SDK moves unsupported constraints into descriptions and validates), refusals and fallbacks | `source/lesson-04/` |
| 5 | Production basics | error classes by status, retry vs fix, catching most-specific first, rate limits, exponential backoff with jitter, SDK `max_retries` (default 2) shown with `ANTHROPIC_LOG=info`, timeouts, request IDs, key hygiene, prices per million tokens, `count_tokens`, cost formula, cost controls | `source/lesson-05/` |
| 6 | Project part 1 | brief, architecture, fake API design, real/offline client, settings, pricing + budget, `Answer`, error mapping, fallbacks opt-in, streaming `explain`, demo incl. truncation and budget stop | `project/ai-study-assistant/` |
| 7 | Project part 2 | quiz schema, `make_quiz` with `beta.messages.parse`, `ChatSession` with trimming, CLI, demo (quiz, chat, tokens, retries, refusal), tests with the fake API, mypy, troubleshooting, module recap, 5-question quiz, challenge, docs | `project/ai-study-assistant/` |
