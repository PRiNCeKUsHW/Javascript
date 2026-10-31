# Personal Productivity Agent

Module 5 project of **AI Agents with Python: Beginner to Production (2026)**.

Tell the agent in plain words what to do with your tasks and notes. It uses six tools to do it, and it
does it **safely**: every input is validated, every tool has a timeout, every tool has a permission
level, and nothing is deleted without a human "yes".

- **A tool registry** (`productivity/tools.py`): each tool is a function registered with `@tool(...)`,
  with a description, a Pydantic class for its input, a permission level and a timeout. The JSON schemas
  sent to the API are generated from the Pydantic classes (`schema_for`), in strict mode.
- **One pipeline for every call** (`run_tool`): does the tool exist → is the input valid → is the call
  allowed → run it with a timeout. Every problem becomes a `ToolError`, which the agent sends back to the
  model as an observation (`is_error`) instead of crashing.
- **Permissions** (`productivity/policy.py`): `read` tools always run, `write` tools are blocked in
  `--read-only` mode, and `danger` tools (`delete_task`) need a human to approve **every** call, with a
  clear question ("Delete task [ ] 1. Pay rent (high, due 2026-11-05)?").
- **Parallel tool calls** (`productivity/agent.py`): when one reply asks for several tools, all of them
  run, and all the results go back in **one** user message.
- **A safe store** (`productivity/store.py`): tasks and notes in one JSON file, saved atomically
  (temporary file, then `os.replace`).

## Offline mode (no key needed)

Without `ANTHROPIC_API_KEY`, the agent uses `productivity/fake_api.py`, a local stand-in that speaks the
Messages API protocol, so the real SDK and the real loop run unchanged. **It is not a model.** It follows
a script: it splits the request on "and" or ";", matches each part against a few patterns
(`add task ...`, `list tasks`, `complete task 2`, `delete task 2`, `note title: text`,
`search notes for ...`), asks for all the matching tools in one turn, then writes a placeholder answer
starting with `(offline demo)`. It can't understand free-form requests. The tools, validation,
timeouts and permissions are real.

Demo switches: `PROD_FAKE_FAIL` = `badinput` (an invalid call first, to show recovery), `loop`,
`refusal`, `401`, `429`, `500`; `PROD_FAKE_SLOW=search_notes` (the tool sleeps 30 s, to show the 2 s
timeout).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."   # optional; omit for offline mode
```

## Usage

```bash
python -m productivity ask "add task Pay rent due 2026-11-05 high priority and add task Buy milk"
python -m productivity ask "complete task 2 and note wifi: password is on the router"
python -m productivity ask "list all tasks and search notes for wifi"
python -m productivity ask "delete task 1"              # asks: Delete task ...? [y/N]
python -m productivity ask "add task X" --read-only     # writes are blocked
python -m productivity ask "delete task 1" --yes        # approve dangerous actions (scripts you trust)
python -m productivity tasks | notes                    # show the data, no model
python -m productivity tools [--json]                   # tools, permissions, timeouts (or API definitions)
python -m productivity reset [--yes]                    # empty the store (asks first)
```

| Setting | Default |
|---|---|
| `PROD_DATA` | `productivity.json` (in the current folder) |
| `PROD_MODEL` | `claude-opus-5-5` |
| `PROD_BUDGET_USD` | `0.50` |
| `PROD_MAX_STEPS` / `PROD_MAX_RETRIES` | `6` / `2` |
| `PROD_TODAY` | today (set a fixed date for tests and demos) |

## Tests

```bash
python -m pytest -q      # 43 tests, offline, never touch your real data file
mypy productivity
```

## Files

| File | What it does |
|---|---|
| `productivity/tools.py` | Registry, `@tool`, `schema_for`, `validate`, `run_with_timeout`, `run_tool`, the six tools |
| `productivity/policy.py` | read · write · danger, read-only mode, human approval, decision log |
| `productivity/agent.py` | The agent loop: parallel calls, step limit, budget, clean stops |
| `productivity/store.py` | Tasks and notes in a JSON file, atomic saves |
| `productivity/cli.py` | Commands, the trace, the y/N prompt |
| `productivity/fake_api.py` | The offline, scripted stand-in for the API (not a model) |
| `productivity/client.py`, `config.py`, `pricing.py`, `errors.py` | Client, settings, costs, errors |
