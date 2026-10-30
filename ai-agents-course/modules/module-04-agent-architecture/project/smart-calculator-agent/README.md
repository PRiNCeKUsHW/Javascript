# Smart Calculator Agent

Module 4 project of **AI Agents with Python: Beginner to Production (2026)**.

An AI agent built from scratch: you ask an everyday maths question, and the agent works it out with
tools, one step at a time, printing a **trace** of every action and result.

- **The agent loop** (`calc_agent/agent.py`): decide (the model picks an action) → act (your code runs
  a tool) → observe (the result goes back) → repeat, until the model answers.
- **Two tools** (`calc_agent/tools.py`): `calculate`, an arithmetic calculator that uses an
  allow-list of operations (it **never** calls `eval()`), and `convert`, a unit converter.
- **Safe stopping**: a step limit, a budget, clean stops on refusals and cut-off replies, and one clear
  message for every ending.
- **Tool errors are observations**: a failing tool sends its error back to the model (`is_error`)
  instead of crashing, so the model can fix its input.

## Offline mode (no key needed)

Without `ANTHROPIC_API_KEY`, the agent uses `calc_agent/fake_api.py`, a local stand-in that speaks the
Messages API protocol, so the real SDK and the real loop run unchanged. **It is not a model.** It
follows a script: it finds arithmetic (`18 * 1.15`) and conversions (`5 km to mi`) in the question,
asks for one tool per turn, then writes a placeholder answer starting with `(offline demo)` that
lists the tool results. It can't read word problems, plan or check its work. The tools are real.

`CALC_FAKE_FAIL` makes the fake misbehave on purpose: `loop` (asks for tools forever, to show the step
limit), `badexpr` (sends a broken expression first, to show recovery), `refusal`, `429`, `500`, `401`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # optional; omit for offline mode
```

## Usage

```bash
python -m calc_agent ask "What is 18 * 1.15, and how many miles is 42.195 km?"
python -m calc_agent ask "What is 18 * 1.15?" --quiet       # answer only, no trace
python -m calc_agent ask "..." --max-steps 3                # change the step limit
python -m calc_agent calc "(18 * 1.15) / 3"                 # run the calculator tool, no model
python -m calc_agent tools                                  # print the tool definitions
python -m calc_agent --offline ask "..."                    # force offline mode even with a key
```

The trace and the answer go to stdout; the offline notice, the summary line (turns, tool calls,
cost) and errors go to stderr. Every ending other than an answer is one line and exit code 1.

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `ANTHROPIC_API_KEY` | (none) | Your API key. Without it: offline mode |
| `CALC_MODEL` | `claude-opus-5-5` | Model ID |
| `CALC_BUDGET_USD` | `0.50` | Spending limit per run |
| `CALC_MAX_RETRIES` | `2` | SDK automatic retries for 429, 5xx and connection errors |
| `CALC_MAX_STEPS` | `6` | Most turns the loop may take (`--max-steps` overrides it) |

## Tests

```bash
python -m pytest -q      # 34 tests: no key, no network, no cost
mypy calc_agent
```

## Layout

```text
calc_agent/
  agent.py     the loop: decide, act, observe; Step, Result, stop reasons
  tools.py     calculate (allow-list), convert, TOOLS definitions, run_tool dispatcher
  cli.py       ask / calc / tools commands, the trace
  fake_api.py  offline scripted stand-in for the Messages API (not a model)
  client.py, config.py, pricing.py, errors.py
```

In real projects the Anthropic SDK also offers a tool runner that runs this loop for you; this project
builds the loop by hand so every step is visible.
