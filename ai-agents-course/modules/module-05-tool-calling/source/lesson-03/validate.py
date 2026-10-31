# validate.py: the model's input is never trusted; every call is checked first
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

import project  # noqa: F401
from productivity.errors import ToolError
from productivity.store import Store
from productivity.tools import Context, run_tool

calls = [
    {"title": "Pay rent", "due": "2026-11-05", "priority": "high"},
    {"title": "Pay rent", "due": "next friday", "priority": "high"},
    {"title": "Pay rent", "due": None, "priority": "urgent"},
    {"title": "", "due": None, "priority": "low"},
    {"title": "Pay rent", "due": "2026-01-01", "priority": "low"},
]
with TemporaryDirectory() as folder:
    ctx = Context(Store(Path(folder) / "data.json"), today=date(2026, 10, 31))
    for raw in calls:
        try:
            print("ok   ", run_tool(ctx, "add_task", raw))
        except ToolError as exc:
            print("error", exc)
