# AI Resume Analyzer

Module 3 project of **AI Agents with Python: Beginner to Production (2026)**.

A command-line tool that compares a resume with a job posting and writes a **skills-gap report**.
It shows the prompt-engineering ideas from Module 3 working together:

- **Versioned prompts** (`resume/prompts.py`): each prompt has a name, a version and a fingerprint
  (a short hash of its text). Released versions never change, and `prompts.lock.json` plus a test
  enforce that. Every report says which prompt versions produced it.
- **Structured output** with `client.beta.messages.parse(output_format=...)` into Pydantic models
  (`resume/models.py`). Replies that don't fit the schema become one clear error.
- **Task decomposition**: the model extracts the profile and the requirements, **plain code**
  compares them (`resume/skills.py` handles spellings like Postgres/PostgreSQL), and the model is
  asked for advice only when there are gaps.
- **Grounding check**: an extracted skill that the resume doesn't actually name is dropped.
- **Evaluations** (`resume/evals.py`): hand-labelled cases, graded by code, per prompt version.

## Offline mode (no key needed)

Without `ANTHROPIC_API_KEY`, the analyzer uses `resume/fake_api.py`, a local stand-in that speaks the
Messages API protocol, so the real SDK code runs unchanged. **It is not a model.** It fills the
requested schema with simple keyword rules: it finds skill names from a fixed list, ignores prompt
wording, and misses negation such as "no experience with Kubernetes". Advice text starts with
`(offline demo)`. Token counts are rough estimates (about 4 characters per token).

Because the rules ignore wording, **offline evals score every prompt version the same**. Run the eval
with a real key to compare versions on a real model.

`RESUME_FAKE_FAIL` makes the fake misbehave on purpose, in order, one call each:
`429`, `500`, `401`, `refusal`, `invalid` (breaks a schema constraint), `cutoff` (truncated JSON),
`invented` (adds a skill that is not in the resume). Example: `RESUME_FAKE_FAIL=invented`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # optional; omit for offline mode
```

## Usage

```bash
python -m resume analyze data/resume_sam.md data/job_backend.md
python -m resume analyze data/resume_sam.md data/job_backend.md --format json --out reports/sam.json
python -m resume analyze data/resume_sam.md data/job_backend.md --prompt v1   # older prompt
python -m resume extract data/resume_sam.md        # just the extracted profile, as JSON
python -m resume prompts                           # every prompt version and its fingerprint
python -m resume eval --versions v1,v2             # score extract_profile versions
python -m resume --offline analyze ...             # force offline mode even with a key
```

Reports go to stdout (or `--out`); the offline notice and errors go to stderr. Errors are one line
and exit code 1.

## Changing a prompt

1. Copy the prompt in `resume/prompts.py` to a new version (`v3`) and change the copy.
2. Run `python -m resume eval --versions v2,v3` with a real key and compare.
3. Switch `DEFAULT_VERSIONS` only if the new version is at least as good on the eval.
4. Add the new fingerprint to `prompts.lock.json` (`python -m resume prompts` prints it).

Editing a released version makes `test_released_prompts_never_change` fail.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | (none) | Your API key. Without it: offline mode |
| `RESUME_MODEL` | `claude-opus-5-5` | Model ID (`claude-sonnet-5-5`, `claude-haiku-5-5` are priced too) |
| `RESUME_BUDGET_USD` | `0.50` | Spending limit per run; calls stop once it is used up |
| `RESUME_MAX_RETRIES` | `2` | SDK automatic retries for 429, 5xx and connection errors |

Prices in `resume/pricing.py` are list prices per million tokens as of October 2026
(Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50). Check the official pricing page.

## Tests

```bash
python -m pytest -q      # 27 tests: no key, no network, no cost
mypy resume
```

## Privacy

A resume is personal data. In real use, send only the resumes you are allowed to process, don't
log their full text, and check your provider's data-retention terms. The sample resumes in `data/`
and `evals/cases/` are fictional.

## Layout

```text
resume/
  prompts.py     versioned prompt templates + fingerprints
  models.py      Pydantic schemas: CandidateProfile, JobRequirements, Suggestions
  analyzer.py    extract (model) -> compare (code) -> advise (model); errors, costs
  skills.py      normalising skill names, grounding check
  report.py      Markdown and JSON reports
  evals.py       eval runner and scoring
  fake_api.py    offline stand-in for the Messages API (keyword rules, not a model)
  client.py      real client, or the SDK pointed at the fake API
  config.py, pricing.py, errors.py, cli.py
data/            sample resume and job posting (fictional)
evals/           cases.json + labelled eval cases (fictional)
prompts.lock.json  fingerprints of released prompt versions
```
