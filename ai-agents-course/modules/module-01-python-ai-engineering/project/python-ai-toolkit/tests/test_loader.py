import json

import pytest

from toolkit.errors import ToolkitError
from toolkit.loader import load_records


def test_sample_file_is_fully_valid(in_project):
    records, problems = load_records(in_project / "data/usage_sample.json")
    assert len(records) == 10
    assert problems == []


def test_broken_file_reports_each_bad_record(in_project):
    records, problems = load_records(in_project / "data/usage_broken.json")
    assert [r.id for r in records] == ["req-101"]
    assert len(problems) == 4
    assert problems[0] == "record 2 (req-102): prompt_tokens: must be a non-negative integer, got -5"
    assert problems[2] == "record 4 (no id): id: is required"


def test_missing_file(tmp_path):
    with pytest.raises(ToolkitError, match="file not found"):
        load_records(tmp_path / "nope.json")


def test_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("[1, 2,", encoding="utf-8")
    with pytest.raises(ToolkitError, match="not valid JSON"):
        load_records(path)


def test_top_level_must_be_a_list(tmp_path):
    path = tmp_path / "obj.json"
    path.write_text(json.dumps({"id": "x"}), encoding="utf-8")
    with pytest.raises(ToolkitError, match="JSON list"):
        load_records(path)
