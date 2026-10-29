import json

from study.cli import main


def test_explain(capsys):
    assert main(["explain", "closures"]) == 0
    out, err = capsys.readouterr()
    assert "closures" in out
    assert "offline mode" in err and "stop: end_turn" in err


def test_quiz_saves_and_grades(tmp_path, capsys):
    out_file = tmp_path / "quiz.json"
    assert main(["quiz", "loops", "--count", "2", "--out", str(out_file),
                 "--answers", "A,B"]) == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert len(data["questions"]) == 2
    assert "Score: 2/2" in capsys.readouterr().out


def test_chat_reads_lines(monkeypatch, capsys):
    import io
    monkeypatch.setattr("sys.stdin", io.StringIO("hi\nagain\nexit\n"))
    assert main(["chat"]) == 0
    out = capsys.readouterr().out
    assert out.count("bot>") == 2
    assert "carried 2 earlier message(s)" in out


def test_errors_are_one_line(monkeypatch, capsys):
    monkeypatch.setenv("STUDY_FAKE_FAIL", "401")
    assert main(["explain", "x"]) == 1
    assert "error: the API key was rejected" in capsys.readouterr().err
