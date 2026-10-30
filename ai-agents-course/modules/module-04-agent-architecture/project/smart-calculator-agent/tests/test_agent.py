from conftest import make_agent
from calc_agent.fake_api import FakeAnthropicAPI, plan


def test_loop_calls_tools_then_answers():
    fake = FakeAnthropicAPI(failures=[])
    result = make_agent(fake).run("What is 18 * 1.15 and 5 km to mi?")
    assert result.ok
    assert [s.tool for s in result.steps] == ["calculate", "convert"]
    assert [s.output for s in result.steps] == ["20.7", "3.1069 mi"]
    assert result.turns == 3                  # two tool turns + the answer
    assert "20.7; 3.1069 mi" in result.answer


def test_every_request_sends_tools_system_and_the_growing_history():
    fake = FakeAnthropicAPI(failures=[])
    make_agent(fake).run("What is 2 + 2?")
    first, second = fake.requests
    assert [t["name"] for t in first["tools"]] == ["calculate", "convert"]
    assert first["system"].startswith("You help people with everyday maths")
    assert len(first["messages"]) == 1
    assert len(second["messages"]) == 3       # question, tool call, result


def test_tool_results_answer_the_matching_call():
    fake = FakeAnthropicAPI(failures=[])
    make_agent(fake).run("What is 2 + 2?")
    call = fake.requests[1]["messages"][1]["content"][0]
    result = fake.requests[1]["messages"][2]["content"][0]
    assert result["tool_use_id"] == call["id"]
    assert result["content"] == "4"


def test_tool_error_is_an_observation_the_agent_recovers_from():
    fake = FakeAnthropicAPI(failures=["badexpr"])
    result = make_agent(fake).run("What is 18 * 1.15?")
    assert result.ok
    assert result.steps[0].is_error
    assert result.steps[0].output.startswith("Error: not a valid expression")
    sent = fake.requests[1]["messages"][2]["content"][0]
    assert sent["is_error"] is True


def test_max_steps_stops_a_loop_that_never_ends():
    result = make_agent(FakeAnthropicAPI(failures=["loop"]),
                        max_steps=3).run("What is 2 + 2?")
    assert result.stop == "max_steps"
    assert len(result.steps) == 3


def test_refusal_and_budget_stop_the_loop():
    assert make_agent(FakeAnthropicAPI(failures=["refusal"])).run(
        "2 + 2").stop == "refused"
    assert make_agent(FakeAnthropicAPI(failures=[]), budget=0.0).run(
        "2 + 2").stop == "budget"


def test_question_without_numbers_gets_a_direct_answer():
    fake = FakeAnthropicAPI(failures=[])
    result = make_agent(fake).run("Hello!")
    assert result.ok and result.steps == []
    assert len(fake.requests) == 1


def test_sdk_retries_rate_limits():
    fake = FakeAnthropicAPI(failures=["429", "500"])
    assert make_agent(fake).run("What is 2 + 2?").ok
    assert len(fake.requests) == 4            # 2 failures, tool turn, answer


def test_fake_plan_reads_expressions_and_conversions_in_order():
    assert plan("Convert 3 kg to lb, then 10 / 4") == [
        ("convert", {"value": 3.0, "from_unit": "kg", "to_unit": "lb"}),
        ("calculate", {"expression": "10 / 4"})]


def test_a_failed_planned_call_is_not_repeated_forever():
    fake = FakeAnthropicAPI(failures=[])
    result = make_agent(fake).run("Convert 5 kg to km")
    assert result.ok
    assert len(result.steps) == 1 and result.steps[0].is_error
