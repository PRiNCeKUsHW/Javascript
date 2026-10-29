import json
from pathlib import Path

from toolkit.cli import main


def test_validate_good_file(in_project, capsys):
    assert main(["validate", "data/usage_sample.json"]) == 0
    assert capsys.readouterr().out == "10 valid, 0 invalid\n"


def test_validate_broken_file(in_project, capsys):
    assert main(["validate", "data/usage_broken.json"]) == 1
    out = capsys.readouterr().out
    assert "1 valid, 4 invalid" in out
    assert "status: must be one of ['error', 'ok'], got 'done'" in out


def test_report_to_file(in_project, tmp_path, capsys):
    out_file = tmp_path / "report.json"
    assert main(["report", "data/usage_sample.json", "--format", "json", "--out", str(out_file)]) == 0
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["requests"] == 10
    assert data["tokens"]["total"] == 11_095


def test_report_strict_fails_on_invalid(in_project, capsys):
    assert main(["report", "data/usage_broken.json", "--strict"]) == 1
    assert "skipped 4 invalid" in capsys.readouterr().err


def test_friendly_error_for_missing_file(in_project, capsys):
    assert main(["validate", "data/missing.json"]) == 1
    # Path() prints with the OS separator: data/missing.json, or data\missing.json on Windows
    expected = f"error: file not found: {Path('data/missing.json')}\n"
    assert capsys.readouterr().err == expected
