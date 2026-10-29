# Module 1 lesson plan: Python for AI Engineering

Audience: beginners with little or no Python. Target level at the end of the module: comfortable
writing a small, tested, multi-module Python CLI that reads JSON, talks HTTP, and uses async.

Running example across every lesson: **LLM usage data**, meaning chat messages, model settings and request
logs with tokens, latency, status and tags. That is the same data the project processes, and the same
shapes Module 2 sends to real model APIs.

| # | Lesson | Concepts | Runnable source |
|---|---|---|---|
| 1 | Welcome, the agent loop, and setup | what an agent is (decide/act/observe/repeat), 18-module roadmap, module format, prerequisites, `python3 --version`, `venv`, activation (macOS/Linux/Windows), `pip install` with pinned versions, `pip freeze`, project layout | project preview (real `validate` / `report` output) |
| 2 | Core data | variables and types (`str`, `int`, `float`, `bool`, `None`), `type()`, f-strings and format specs, `TypeError` str + int, lists (index, negative index, slice, append, `enumerate`), dicts (`[]`, `.get`, chat message shape, list of dicts = conversation), `KeyError`, sets (dedupe, membership, difference = tool allowlist), list/dict comprehensions, generator in `sum`, choosing list/dict/set/tuple | `source/lesson-02/*.py` |
| 3 | Functions, classes, exceptions | `def`, parameters, `return`, docstrings, keyword and default arguments, function habits, **mutable default argument bug**, classes (`__init__`, `self`, methods, `__len__`), dataclasses (`field(default_factory=...)`), `try/except/else/finally`, custom exception hierarchy, `raise`, catching specific vs bare `except`, reading tracebacks bottom-up | `source/lesson-03/*.py` |
| 4 | Modules, packages, files, JSON, env vars | modules vs packages, `__init__.py`, `__all__`, import styles, standard library vs pip packages, `if __name__ == "__main__"`, `ModuleNotFoundError`, `pathlib` read/write/append, `encoding="utf-8"`, `with`, JSON ↔ Python mapping, `json.dumps/loads`, `JSONDecodeError`, `os.environ.get`, setting variables (bash/PowerShell), `.env`, `.env.example`, `.gitignore` | `source/lesson-04/` |
| 5 | Type hints, HTTP, async | annotations, `list[float]`, `dict[str, float]`, `X \| None`, hints not enforced at runtime, `mypy`, HTTP request/response anatomy, status code families incl. 429, `httpx.get`, timeouts, `raise_for_status`, `.json()`, why async (waiting), `async def`, `await`, `asyncio.gather`, `asyncio.run`, measured 3.0 s vs 1.0 s, `httpx.AsyncClient`, async rules | `source/lesson-05/*.py` (local `http.server`) |
| 6 | Project part 1 | requirements brief, architecture (one job per module), input data, `errors.py`, `models.py` (`frozen` dataclass, `@property`, `@classmethod` constructor, validation, `from None`), REPL exploration, `loader.py`, `config.py` (`.env` loader), `stats.py` (`Counter`, `setdefault`, type alias) | `project/python-ai-toolkit` |
| 7 | Project part 2 + wrap-up | `report.py` (Markdown/JSON), `fetch.py` (async, error mapping, injectable transport), `cli.py` (argparse sub-commands, exit codes, stderr, dispatch dict), `__main__.py`, full demo incl. failures, pytest (fixtures, parametrize, `MockTransport`), mypy, troubleshooting, module recap, 5-question quiz, extension challenge, documentation | `project/python-ai-toolkit` |

Every terminal and REPL output shown in the videos is captured from a real run when the lesson is
built (`tools/build_lesson.py`); nothing is typed in by hand. The only edit is that temporary
folder paths are shown as a short alias such as `~/ai-toolkit` or `.`.

## Common errors covered

`TypeError` (str + int), `KeyError`, mutable default argument, bare `except`, traceback reading,
`ModuleNotFoundError` (wrong folder / package run as a file), `JSONDecodeError` (trailing comma),
missing environment variable, mypy argument error, HTTP 404 / unreachable server, inactive virtual
environment, PowerShell execution policy, file paths relative to the working directory, text encoding.
