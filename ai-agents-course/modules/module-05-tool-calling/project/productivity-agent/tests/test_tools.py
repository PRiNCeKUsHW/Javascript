import time
from dataclasses import replace

import pytest

from productivity.errors import ToolError
from productivity.tools import REGISTRY, definitions, run_tool, run_with_timeout, schema_for


def test_every_definition_is_strict_and_closed():
    for d in definitions():
        schema = d["input_schema"]
        assert d["strict"] is True
        assert schema["additionalProperties"] is False
        assert schema["required"] == list(schema["properties"])


def test_schema_drops_unsupported_keywords_but_keeps_a_property_called_title():
    schema = schema_for(REGISTRY["add_task"].params)
    assert list(schema["properties"]) == ["title", "due", "priority"]
    text = str(schema)
    for word in ("minLength", "maxLength", "'default'", "'title': 'AddTask'"):
        assert word not in text


def test_nullable_due_date_is_allowed():
    due = schema_for(REGISTRY["add_task"].params)["properties"]["due"]
    assert {"type": "null"} in due["anyOf"]


def test_add_and_list(ctx):
    out = run_tool(ctx, "add_task", {"title": "Pay rent", "due": "2026-11-05",
                                     "priority": "high"})
    assert out == "added [ ] 1. Pay rent (high, due 2026-11-05)"
    assert run_tool(ctx, "list_tasks", {"status": "open"}) == \
        "[ ] 1. Pay rent (high, due 2026-11-05)"


def test_empty_list_says_so(ctx):
    assert run_tool(ctx, "list_tasks", {"status": "done"}) == "no done tasks"


@pytest.mark.parametrize("raw, problem", [
    ({"title": "", "due": None, "priority": "low"}, "title"),
    ({"title": "x", "due": "next friday", "priority": "low"}, "due"),
    ({"title": "x", "due": None, "priority": "urgent"}, "priority"),
    ({"title": "x", "due": None}, "priority: Field required"),
    ({"title": "x" * 121, "due": None, "priority": "low"}, "at most 120"),
])
def test_invalid_input_becomes_a_clear_tool_error(ctx, raw, problem):
    with pytest.raises(ToolError, match="invalid input for add_task") as err:
        run_tool(ctx, "add_task", raw)
    assert problem in str(err.value)


def test_task_id_must_be_positive(ctx):
    with pytest.raises(ToolError, match="greater than or equal to 1"):
        run_tool(ctx, "complete_task", {"task_id": 0})


def test_business_rule_due_date_in_the_past(ctx):
    with pytest.raises(ToolError, match="in the past"):
        run_tool(ctx, "add_task", {"title": "x", "due": "2026-10-01", "priority": "low"})


def test_missing_task_is_a_tool_error(ctx):
    with pytest.raises(ToolError, match="there is no task 9"):
        run_tool(ctx, "complete_task", {"task_id": 9})


def test_unknown_tool_is_refused(ctx):
    with pytest.raises(ToolError, match="unknown tool 'send_email'"):
        run_tool(ctx, "send_email", {})


def test_notes_save_and_search(ctx):
    assert run_tool(ctx, "add_note", {"title": "wifi", "text": "on the router"}) == \
        "saved note 1: wifi"
    assert run_tool(ctx, "search_notes", {"query": "router"}) == "1. wifi: on the router"
    assert run_tool(ctx, "search_notes", {"query": "pizza"}) == "no notes match 'pizza'"


def test_timeout_stops_waiting():
    start = time.monotonic()
    with pytest.raises(ToolError, match="slow timed out after 0.2 s"):
        run_with_timeout(lambda: time.sleep(5) or "late", 0.2, "slow")
    assert time.monotonic() - start < 1


def test_timeout_passes_results_and_errors_through():
    assert run_with_timeout(lambda: "fast", 1) == "fast"
    with pytest.raises(ZeroDivisionError):
        run_with_timeout(lambda: str(1 / 0), 1)


def test_slow_search_times_out(ctx, monkeypatch):
    monkeypatch.setenv("PROD_FAKE_SLOW", "search_notes")
    fast = replace(REGISTRY["search_notes"], timeout_s=0.2)   # don't wait 2 s in tests
    monkeypatch.setitem(REGISTRY, "search_notes", fast)
    with pytest.raises(ToolError, match="search_notes timed out after 0.2 s"):
        run_tool(ctx, "search_notes", {"query": "wifi"})
