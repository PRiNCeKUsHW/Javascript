import pytest

from productivity.errors import ToolError
from productivity.policy import Policy
from productivity.tools import run_tool


def test_read_tools_always_run(ctx):
    policy = Policy(ctx, read_only=True)
    assert run_tool(ctx, "list_tasks", {"status": "all"}, policy) == "no all tasks"
    assert policy.log == []


def test_read_only_blocks_writes(ctx):
    policy = Policy(ctx, read_only=True)
    with pytest.raises(ToolError, match="read-only"):
        run_tool(ctx, "add_task", {"title": "x", "due": None, "priority": "low"}, policy)
    assert ctx.store.tasks("all") == []
    assert policy.log == ["blocked add_task (read-only)"]


def test_danger_asks_with_a_clear_question_and_runs_on_yes(ctx):
    ctx.store.add_task("Pay rent", None, "high")
    questions = []
    policy = Policy(ctx, ask_human=lambda q: questions.append(q) or True)
    assert run_tool(ctx, "delete_task", {"task_id": 1}, policy).startswith("deleted")
    assert questions == ["Delete task [ ] 1. Pay rent (high)?"]
    assert policy.log == ["approved delete_task"]


def test_danger_declined_changes_nothing(ctx):
    ctx.store.add_task("Pay rent", None, "high")
    policy = Policy(ctx, ask_human=lambda q: False)
    with pytest.raises(ToolError, match="declined delete_task"):
        run_tool(ctx, "delete_task", {"task_id": 1}, policy)
    assert len(ctx.store.tasks("all")) == 1


def test_danger_with_nobody_to_ask_is_denied(ctx):
    ctx.store.add_task("Pay rent", None, "high")
    with pytest.raises(ToolError, match="declined"):
        run_tool(ctx, "delete_task", {"task_id": 1}, Policy(ctx))


def test_confirming_a_missing_task_is_a_tool_error_not_a_question(ctx):
    asked = []
    policy = Policy(ctx, ask_human=lambda q: asked.append(q) or True)
    with pytest.raises(ToolError, match="no task 4"):
        run_tool(ctx, "delete_task", {"task_id": 4}, policy)
    assert asked == []


def test_validation_runs_before_permission(ctx):
    asked = []
    policy = Policy(ctx, ask_human=lambda q: asked.append(q) or True)
    with pytest.raises(ToolError, match="invalid input"):
        run_tool(ctx, "delete_task", {"task_id": "two"}, policy)
    assert asked == []
