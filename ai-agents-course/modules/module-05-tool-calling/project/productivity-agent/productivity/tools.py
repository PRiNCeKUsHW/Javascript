"""The agent's tools: one registry, schemas from Pydantic, safe execution.

Every call goes through `run_tool`, which runs the same checks in the same
order: does the tool exist, is the input valid, is the call allowed, and does
it finish in time. Any problem becomes a ToolError, which the agent sends back
to the model as an observation instead of crashing.
"""
import os
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Any, Literal

from anthropic.types import ToolParam
from pydantic import BaseModel, Field, ValidationError

from productivity.errors import ToolError
from productivity.store import Store, Task

Permission = Literal["read", "write", "danger"]


@dataclass
class Context:
    """What every tool may use: the data store and today's date."""

    store: Store
    today: date


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    params: type[BaseModel]
    func: Callable[[Context, Any], str]
    permission: Permission
    timeout_s: float
    confirm: Callable[[Context, Any], str] | None = None   # text a human approves


REGISTRY: dict[str, Tool] = {}


def tool(description: str, params: type[BaseModel], permission: Permission = "read",
         timeout_s: float = 5.0, confirm: Callable[[Context, Any], str] | None = None
         ) -> Callable[[Callable[[Context, Any], str]], Callable[[Context, Any], str]]:
    """Register a function as a tool. Its name becomes the tool's name."""
    def register(func: Callable[[Context, Any], str]) -> Callable[[Context, Any], str]:
        REGISTRY[func.__name__] = Tool(func.__name__, description, params, func,
                                       permission, timeout_s, confirm)
        return func
    return register


# ---------------------------------------------------------------- schemas
UNSUPPORTED = ("title", "default", "minLength", "maxLength", "minimum", "maximum")


def _clean(node: Any) -> Any:
    """Strip keywords strict tool schemas don't accept; Pydantic still checks them."""
    if isinstance(node, dict):
        out = {k: ({name: _clean(sub) for name, sub in v.items()} if k == "properties"
                   else _clean(v))                    # property names stay, even "title"
               for k, v in node.items() if k not in UNSUPPORTED}
        if out.get("type") == "object":
            out["additionalProperties"] = False
            out["required"] = list(out.get("properties", {}))
        return out
    if isinstance(node, list):
        return [_clean(v) for v in node]
    return node


def schema_for(params: type[BaseModel]) -> dict[str, Any]:
    """A strict-mode JSON schema for a Pydantic model."""
    return _clean(params.model_json_schema())


def definitions() -> list[ToolParam]:
    """Every registered tool, in the shape the Messages API expects."""
    return [{"name": t.name, "description": t.description,
             "input_schema": schema_for(t.params), "strict": True}
            for t in REGISTRY.values()]


# ---------------------------------------------------------------- execution
def validate(t: Tool, raw: dict[str, Any]) -> BaseModel:
    """Turn the model's raw input into a checked object, or a clear ToolError."""
    try:
        return t.params.model_validate(raw)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in e['loc']) or 'input'}: {e['msg']}"
            for e in exc.errors(include_url=False))
        raise ToolError(f"invalid input for {t.name}: {problems}") from None


def run_with_timeout(func: Callable[[], str], seconds: float, name: str = "the tool") -> str:
    """Run func in a worker thread and stop waiting after `seconds`.

    A thread can't be killed, so a stuck tool keeps running in the background
    (as a daemon, it never blocks exit). For real isolation, run tools in a
    separate process.
    """
    result: list[str] = []
    errors: list[BaseException] = []

    def work() -> None:
        try:
            result.append(func())
        except BaseException as exc:  # noqa: BLE001 - re-raised in the caller
            errors.append(exc)

    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(seconds)
    if worker.is_alive():
        raise ToolError(f"{name} timed out after {seconds:g} s")
    if errors:
        raise errors[0]
    return result[0]


def run_tool(ctx: Context, name: str, raw: dict[str, Any],
             allow: Callable[[Tool, BaseModel], None] | None = None) -> str:
    """Look up, validate, check permission, run with a timeout."""
    t = REGISTRY.get(name)
    if t is None:
        raise ToolError(f"unknown tool {name!r}")
    args = validate(t, raw)                                # 1. valid input?
    if allow:
        allow(t, args)                                     # 2. allowed?
    try:
        return run_with_timeout(lambda: t.func(ctx, args), t.timeout_s, t.name)  # 3. in time?
    except LookupError as exc:                             # e.g. no such task
        raise ToolError(str(exc)) from None


# ---------------------------------------------------------------- the tools
def describe(task: Task) -> str:
    due = f", due {task.due}" if task.due else ""
    mark = "x" if task.done else " "
    return f"[{mark}] {task.id}. {task.title} ({task.priority}{due})"


class AddTask(BaseModel):
    title: str = Field(min_length=1, max_length=120, description="What to do, in a few words")
    due: date | None = Field(description="Due date as YYYY-MM-DD, or null if none")
    priority: Literal["low", "normal", "high"] = Field(description="How urgent it is")


class ListTasks(BaseModel):
    status: Literal["open", "done", "all"] = Field(description="Which tasks to show")


class TaskId(BaseModel):
    task_id: int = Field(ge=1, description="The task's number, as shown by list_tasks")


class AddNote(BaseModel):
    title: str = Field(min_length=1, max_length=80, description="A short title")
    text: str = Field(min_length=1, max_length=2000, description="The note itself")


class SearchNotes(BaseModel):
    query: str = Field(min_length=2, max_length=100, description="Words to look for")


@tool("Adds a task to the user's to-do list and returns it with its number. "
      "Use it when the user asks to remember, schedule or plan something they "
      "must do. The due date must be today or later.", AddTask, "write")
def add_task(ctx: Context, a: AddTask) -> str:
    if a.due and a.due < ctx.today:
        raise ToolError(f"due date {a.due} is in the past (today is {ctx.today})")
    task = ctx.store.add_task(a.title.strip(), a.due.isoformat() if a.due else None,
                              a.priority)
    return f"added {describe(task)}"


@tool("Lists the user's tasks with their numbers, priority and due dates. "
      "Use it before completing or deleting a task, to find its number.", ListTasks)
def list_tasks(ctx: Context, a: ListTasks) -> str:
    tasks = ctx.store.tasks(a.status)
    return "\n".join(describe(t) for t in tasks) if tasks else f"no {a.status} tasks"


@tool("Marks one task as done. Needs the task number from list_tasks.", TaskId, "write")
def complete_task(ctx: Context, a: TaskId) -> str:
    return f"completed {describe(ctx.store.complete_task(a.task_id))}"


@tool("Deletes one task permanently. Only use it when the user clearly asks to "
      "delete or remove a task; to finish a task, use complete_task instead. "
      "A human must approve every deletion.", TaskId, "danger",
      confirm=lambda ctx, a: f"Delete task {describe(ctx.store.get_task(a.task_id))}?")
def delete_task(ctx: Context, a: TaskId) -> str:
    return f"deleted {describe(ctx.store.delete_task(a.task_id))}"


@tool("Saves a note: an idea, a fact or meeting notes the user wants to keep.",
      AddNote, "write")
def add_note(ctx: Context, a: AddNote) -> str:
    note = ctx.store.add_note(a.title.strip(), a.text.strip())
    return f"saved note {note.id}: {note.title}"


@tool("Searches the user's notes for words in the title or text and returns "
      "the matching notes.", SearchNotes, timeout_s=2.0)
def search_notes(ctx: Context, a: SearchNotes) -> str:
    if os.environ.get("PROD_FAKE_SLOW") == "search_notes":   # demo: a slow service
        time.sleep(30)
    found = ctx.store.search_notes(a.query)
    if not found:
        return f"no notes match {a.query!r}"
    return "\n".join(f"{n.id}. {n.title}: {n.text}" for n in found)
