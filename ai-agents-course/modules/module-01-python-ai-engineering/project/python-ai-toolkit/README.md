# Python AI Toolkit

Module 1 project of **AI Agents with Python: Beginner to Production (2026)**.

A command-line tool that reads a JSON log of language-model API calls, validates every
record, and produces a usage report (requests, success rate, tokens, estimated cost,
latency, top tags) as Markdown or JSON. It can also download several logs concurrently.

## Requirements

- Python 3.11 or newer (recorded with Python 3.13)
- `httpx`, plus `pytest` and `mypy` for development (pinned in `requirements.txt`)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # optional; real environment variables win over .env
```

## Usage

Run every command from this folder (the project root).

```bash
python -m toolkit --help
python -m toolkit validate data/usage_sample.json
python -m toolkit validate data/usage_broken.json            # exit code 1, lists 4 problems
python -m toolkit report data/usage_sample.json              # Markdown to the screen
python -m toolkit report data/usage_sample.json --format json --out reports/usage.json
python -m toolkit report data/usage_broken.json --strict     # fails on any invalid record
python -m toolkit fetch URL [URL ...] --out data/merged.json # concurrent downloads
```

To try `fetch` offline, serve the data folder locally in a second terminal:

```bash
python -m http.server 8765 --bind 127.0.0.1 --directory data
python -m toolkit fetch http://127.0.0.1:8765/usage_sample.json http://127.0.0.1:8765/usage_broken.json --out data/merged.json
```

### Example output

```text
$ python -m toolkit validate data/usage_broken.json
  x record 2 (req-102): prompt_tokens: must be a non-negative integer, got -5
  x record 3 (req-103): status: must be one of ['error', 'ok'], got 'done'
  x record 4 (no id): id: is required
  x record 5 (req-105): tags: must be a list of strings
1 valid, 4 invalid
```

```text
$ python -m toolkit report data/usage_sample.json
# AI Usage Report

Source: data/usage_sample.json
Requests: 10 (8 ok, 2 errors)
Success rate: 80.0%
Tokens: 8,410 prompt + 2,685 completion = 11,095
Estimated cost: 0.0498 USD
Average latency: 4,200 ms
...
```

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `TOOLKIT_PRICES_FILE` | `config/prices.json` | Prices per 1 million tokens, per model |
| `TOOLKIT_CURRENCY` | `USD` | Currency label used in reports; must match the price file |

`config/prices.json` contains **example prices for fictional models** (`model-small`,
`model-large`). They are not real provider prices.

## Input format

A JSON list of records:

```json
{"id": "req-001", "model": "model-small", "prompt_tokens": 420, "completion_tokens": 180,
 "latency_ms": 820, "status": "ok", "tags": ["summarize"], "created_at": "2026-03-02T09:15:00+00:00"}
```

`id`, `model`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `status` (`ok` or `error`)
and `created_at` (ISO 8601) are required; `tags` is optional.

## Project layout

```text
toolkit/
  errors.py   ToolkitError, ValidationError
  models.py   UsageRecord dataclass + validation (from_dict)
  loader.py   read JSON, collect valid records and problems
  config.py   settings from environment variables / .env, price file
  stats.py    summarize(): totals, cost, latency, top tags
  report.py   Markdown and JSON renderers
  fetch.py    concurrent downloads with httpx + asyncio
  cli.py      argparse commands: validate, report, fetch
tests/        42 pytest tests (HTTP is mocked with httpx.MockTransport)
```

## Tests and type checks

```bash
python -m pytest -q     # 42 passed
mypy toolkit            # Success: no issues found
```

## Limitations and extension ideas

- Average latency is distorted by outliers: add a p95 latency.
- Validation stops at the first problem in each record; report all problems per record.
- Add `--top N`, a per-day breakdown, or a CSV output format (each with tests).
- Prices are a static file; Module 2 discusses real provider pricing and token counting.
