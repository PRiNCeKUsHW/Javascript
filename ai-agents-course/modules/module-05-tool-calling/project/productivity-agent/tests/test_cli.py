import io

from productivity.cli import main


def run(capsys, monkeypatch, tmp_path, *args, stdin=""):
    monkeypatch.setenv("PROD_DATA", str(tmp_path / "data.json"))
    monkeypatch.setenv("PROD_TODAY", "2026-10-31")
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin))
    code = main(list(args))
    out, err = capsys.readouterr()
    return code, out, err


def test_ask_prints_the_trace_and_footer(capsys, monkeypatch, tmp_path):
    code, out, err = run(capsys, monkeypatch, tmp_path, "ask", "add task A and list tasks")
    assert code == 0
    assert "turn 1  act      add_task(title='A', due=None, priority='normal')" in out
    assert "observe  = [ ] 1. A (normal)" in out
    assert "[2 turns · 2 tool calls" in err and "offline mode" in err


def test_piped_no_declines_and_yes_flag_approves(capsys, monkeypatch, tmp_path):
    run(capsys, monkeypatch, tmp_path, "ask", "add task A")
    code, out, _ = run(capsys, monkeypatch, tmp_path, "ask", "delete task 1", stdin="n\n")
    assert code == 0 and "Delete task [ ] 1. A (normal)? [y/N] n" in out
    assert "declined" in out
    code, out, _ = run(capsys, monkeypatch, tmp_path, "ask", "delete task 1", "--yes")
    assert "observe  = deleted" in out


def test_tasks_tools_and_reset(capsys, monkeypatch, tmp_path):
    run(capsys, monkeypatch, tmp_path, "ask", "add task A")
    assert run(capsys, monkeypatch, tmp_path, "tasks")[1] == "[ ] 1. A (normal)\n"
    out = run(capsys, monkeypatch, tmp_path, "tools")[1]
    assert "delete_task    danger timeout 5 s" in out
    code, _, err = run(capsys, monkeypatch, tmp_path, "reset", stdin="n\n")
    assert code == 1 and "nothing was deleted" in err
    assert run(capsys, monkeypatch, tmp_path, "reset", "--yes")[0] == 0
    assert run(capsys, monkeypatch, tmp_path, "tasks")[1] == "no tasks\n"


def test_api_errors_are_one_line(capsys, monkeypatch, tmp_path):
    monkeypatch.setenv("PROD_FAKE_FAIL", "401")
    code, out, err = run(capsys, monkeypatch, tmp_path, "ask", "list tasks")
    assert code == 1 and "error: the API key was rejected" in err
    assert "Traceback" not in err
