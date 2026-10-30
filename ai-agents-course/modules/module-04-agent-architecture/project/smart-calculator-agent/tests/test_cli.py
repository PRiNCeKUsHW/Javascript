import json

from calc_agent.cli import main


def test_ask_prints_trace_and_answer(capsys):
    assert main(["ask", "What is 18 * 1.15?"]) == 0
    out = capsys.readouterr()
    assert "act      calculate(expression='18 * 1.15')" in out.out
    assert "observe  = 20.7" in out.out
    assert out.out.strip().endswith("Tool results: 20.7.")
    assert "offline mode" in out.err


def test_max_steps_is_a_clean_error(capsys, monkeypatch):
    monkeypatch.setenv("CALC_FAKE_FAIL", "loop")
    assert main(["ask", "2 + 2", "--max-steps", "2"]) == 1
    assert "stopped after 2 turns" in capsys.readouterr().err


def test_calc_runs_the_tool_without_a_model(capsys):
    assert main(["calc", "(18 * 1.15) / 3"]) == 0
    assert capsys.readouterr().out == "6.9\n"
    assert main(["calc", "__import__('os')"]) == 1
    assert "not allowed" in capsys.readouterr().err


def test_tools_prints_the_definitions(capsys):
    assert main(["tools"]) == 0
    tools = json.loads(capsys.readouterr().out)
    assert [t["name"] for t in tools] == ["calculate", "convert"]


def test_api_error_is_a_clean_error(capsys, monkeypatch):
    monkeypatch.setenv("CALC_FAKE_FAIL", "401")
    assert main(["ask", "2 + 2"]) == 1
    assert "API key was rejected" in capsys.readouterr().err
