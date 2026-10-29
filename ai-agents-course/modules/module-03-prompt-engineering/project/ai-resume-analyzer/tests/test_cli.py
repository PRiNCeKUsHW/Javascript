import json

from conftest import PROJECT
from resume.cli import main


def test_analyze_prints_report(capsys, monkeypatch):
    monkeypatch.chdir(PROJECT)
    assert main(["analyze", "data/resume_sam.md", "data/job_backend.md"]) == 0
    out = capsys.readouterr()
    assert "# Skills-gap report: Sam Rivera" in out.out
    assert "offline mode" in out.err


def test_analyze_saves_json(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(PROJECT)
    out = tmp_path / "r.json"
    assert main(["analyze", "data/resume_sam.md", "data/job_backend.md",
                 "--format", "json", "--out", str(out)]) == 0
    assert json.loads(out.read_text())["score"] == 83
    assert "must-have match 83%" in capsys.readouterr().out


def test_missing_file_is_a_clean_error(capsys):
    assert main(["extract", "nope.md"]) == 1
    assert "error: cannot read nope.md" in capsys.readouterr().err


def test_unknown_prompt_version(capsys, monkeypatch):
    monkeypatch.chdir(PROJECT)
    assert main(["extract", "data/resume_sam.md", "--prompt", "v9"]) == 1
    assert "no extract_profile version 'v9'" in capsys.readouterr().err


def test_prompts_lists_fingerprints(capsys):
    assert main(["prompts"]) == 0
    assert "extract_profile@v2" in capsys.readouterr().out


def test_eval_command(capsys, monkeypatch):
    monkeypatch.chdir(PROJECT)
    assert main(["eval", "--versions", "v1,v2"]) == 0
    out = capsys.readouterr().out
    assert out.count("total 21/22 (95%)") == 2
