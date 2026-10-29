# AI Study Assistant

Module 2 project of **AI Agents with Python: Beginner to Production (2026)**.

A command-line study assistant built on the official Anthropic Python SDK. It:

- **explains** a programming concept at a chosen level, streamed as it is generated
- writes **quizzes** as structured output (JSON validated into Pydantic models), saves and grades them
- **chats** with conversation history, trimmed to a token budget
- reports tokens and **cost** for every call and stops at a spending **budget**
- maps API errors to one clear message, relies on the SDK's automatic **retries**, and opts in to
  server-side **fallbacks** for refusals

## Offline mode (no key needed)

Without `ANTHROPIC_API_KEY`, the assistant uses `study/fake_api.py`, a local stand-in that speaks the
Messages API protocol. The real SDK code runs unchanged (requests, streaming, structured output,
errors, retries), but **the replies are placeholders, not model output**. They start with
`(offline demo reply)`. Token counts in offline mode are rough estimates (about 4 characters per token).
All tests use offline mode, so they need no key and no network and cost nothing.

`STUDY_FAKE_FAIL` makes the fake API fail on purpose, e.g. `STUDY_FAKE_FAIL=429,500` (two failures
in a row) or `STUDY_FAKE_FAIL=refusal`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # optional; omit for offline mode
```

## Usage

```bash
python -m study explain "Python decorators" --level beginner
python -m study explain "recursion" --max-tokens 300
python -m study quiz "Python dictionaries" --count 5 --out quizzes/dicts.json --answers A,C,B,D,A
printf 'What is a token?\nAnd a context window?\n' | python -m study chat
python -m study tokens "How are tokens counted?"
python -m study --offline explain "anything"       # force offline mode even with a key
```

Output goes to stdout; the offline notice, the per-call footer (model, tokens, cost, stop reason)
and the session cost go to stderr.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | (none) | Your API key. Without it: offline mode |
| `STUDY_MODEL` | `claude-opus-5-5` | Model ID (`claude-sonnet-5-5`, `claude-haiku-5-5` are priced too) |
| `STUDY_BUDGET_USD` | `0.50` | Spending limit per run; calls stop once it is used up |
| `STUDY_MAX_RETRIES` | `2` | SDK automatic retries for 429, 5xx and connection errors |

Prices in `study/pricing.py` are list prices per million tokens as of October 2026
(Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50). Check the official pricing page;
prices change.

## How it calls the API

- Explanations: `client.beta.messages.stream(...)` with `output_config={"effort": "low"}`
- Quizzes: `client.beta.messages.parse(..., output_format=Quiz)` with `effort: "medium"`.
  The SDK turns `study/models.py` into a JSON schema; constraints the API cannot enforce
  (exactly 4 options, answer index 0-3) are moved into field descriptions and validated by the
  SDK with Pydantic afterwards.
- Chat: `client.beta.messages.create(...)` with the whole (trimmed) history
- All requests opt in to server-side fallbacks for refusals:
  `betas=["server-side-fallback-2026-07-01"], fallbacks="default"`
- Token counting: `client.messages.count_tokens(...)`

## Project layout

```text
study/
  config.py     settings from environment variables (no key: offline)
  client.py     real client, or the SDK pointed at the fake API
  fake_api.py   offline stand-in for the Messages API (placeholders, scripted failures)
  pricing.py    price table, cost_usd(), CostTracker with a budget
  prompts.py    system prompts and request templates
  models.py     Quiz / Question schema (Pydantic)
  assistant.py  StudyAssistant (explain, make_quiz, reply, count_tokens), ChatSession, error mapping
  cli.py        argparse commands: explain, quiz, chat, tokens
tests/          23 pytest tests (real SDK + fake API)
```

## Tests and type checks

```bash
python -m pytest -q    # 23 passed
mypy study             # Success: no issues found
```

## Limitations

- Offline replies are placeholders; quality can only be judged with a real key.
- History trimming uses a rough local estimate; use `count_tokens` for exact numbers.
- A valid quiz is well-formed, not necessarily correct: review generated questions.
- Not verified against the live API in the recorded session (no key was available); the request
  shapes follow the official SDK documentation and the SDK's own types.
