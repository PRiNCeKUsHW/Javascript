from conftest import make_agent

from productivity.fake_api import FakeAnthropicAPI, plan


def test_plan_splits_on_and():
    assert plan("add task Pay rent due 2026-11-05 high priority and list tasks") == [
        ("add_task", {"title": "Pay rent", "due": "2026-11-05", "priority": "high"}),
        ("list_tasks", {"status": "open"})]


def test_parallel_calls_run_in_one_turn_and_return_in_one_message(ctx):
    fake = FakeAnthropicAPI([])
    agent, _ = make_agent(ctx, fake)
    result = agent.run("add task A and add task B and note x: y")
    assert result.ok and result.turns == 2
    assert [s.turn for s in result.steps] == [1, 1, 1]
    sent = fake.requests[1]["messages"]
    assert [m["role"] for m in sent] == ["user", "assistant", "user"]
    results = sent[2]["content"]
    assert [r["tool_use_id"] for r in results] == \
        [b["id"] for b in sent[1]["content"] if b["type"] == "tool_use"]


def test_every_request_sends_strict_tool_definitions(ctx):
    fake = FakeAnthropicAPI([])
    agent, _ = make_agent(ctx, fake)
    agent.run("list tasks")
    tools = fake.requests[0]["tools"]
    assert {t["name"] for t in tools} >= {"add_task", "delete_task", "search_notes"}
    assert all(t["strict"] for t in tools)
    assert "2026-10-31" in fake.requests[0]["system"]


def test_invalid_input_is_returned_as_an_error_and_corrected(ctx):
    agent, _ = make_agent(ctx, FakeAnthropicAPI(["badinput"]))
    result = agent.run("add task Pay rent due 2026-11-05 high priority")
    assert [s.is_error for s in result.steps] == [True, False]
    assert "priority" in result.steps[0].output
    assert [t.title for t in ctx.store.tasks("all")] == ["Pay rent"]


def test_declined_delete_keeps_the_task(ctx):
    ctx.store.add_task("Pay rent", None, "high")
    agent, policy = make_agent(ctx, FakeAnthropicAPI([]), answer=False)
    result = agent.run("delete task 1")
    assert result.ok and result.steps[0].is_error
    assert len(ctx.store.tasks("all")) == 1
    assert policy.log == ["declined delete_task"]


def test_approved_delete_removes_the_task(ctx):
    ctx.store.add_task("Pay rent", None, "high")
    agent, _ = make_agent(ctx, FakeAnthropicAPI([]), answer=True)
    assert agent.run("delete task 1").ok
    assert ctx.store.tasks("all") == []


def test_read_only_agent_changes_nothing(ctx):
    agent, _ = make_agent(ctx, FakeAnthropicAPI([]), read_only=True)
    result = agent.run("add task A and list tasks")
    assert [s.is_error for s in result.steps] == [True, False]
    assert ctx.store.tasks("all") == []


def test_step_limit_stops_a_loop(ctx):
    agent, _ = make_agent(ctx, FakeAnthropicAPI(["loop"]), max_steps=3)
    result = agent.run("list tasks")
    assert result.stop == "max_steps" and result.turns == 3


def test_refusal_and_budget(ctx):
    agent, _ = make_agent(ctx, FakeAnthropicAPI(["refusal"]))
    assert agent.run("list tasks").stop == "refused"
    agent, _ = make_agent(ctx, FakeAnthropicAPI([]), budget=0)
    assert agent.run("list tasks").stop == "budget"
