# permissions.py: read, write and danger, checked before every call
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import project  # noqa: F401
from productivity.errors import ToolError
from productivity.policy import Policy
from productivity.store import Store
from productivity.tools import Context, run_tool


def attempt(policy, name, raw):
    try:
        print("ok   ", run_tool(policy.ctx, name, raw, policy))
    except ToolError as exc:
        print("error", exc)


with TemporaryDirectory() as folder:
    ctx = Context(Store(Path(folder) / "data.json"), today=date(2026, 10, 31))
    ctx.store.add_task("Pay rent", None, "high")

    read_only = Policy(ctx, read_only=True)
    attempt(read_only, "list_tasks", {"status": "open"})
    attempt(read_only, "complete_task", {"task_id": 1})

    says_no = Policy(ctx, ask_human=lambda question: print("ask  ", question) or False)
    attempt(says_no, "delete_task", {"task_id": 1})

    says_yes = Policy(ctx, ask_human=lambda question: True)
    attempt(says_yes, "delete_task", {"task_id": 1})
