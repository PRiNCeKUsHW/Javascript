import pytest

from toolkit.errors import ValidationError
from toolkit.models import UsageRecord


def test_valid_row_becomes_a_record(good_row):
    record = UsageRecord.from_dict(good_row)
    assert record.id == "req-1"
    assert record.total_tokens == 150
    assert record.created_at.year == 2026


REQUIRED = ["id", "model", "prompt_tokens", "status", "created_at"]


@pytest.mark.parametrize("field", REQUIRED)
def test_missing_required_field(good_row, field):
    del good_row[field]
    with pytest.raises(ValidationError) as info:
        UsageRecord.from_dict(good_row)
    assert info.value.field == field


@pytest.mark.parametrize("field, value", [
    ("prompt_tokens", -5),
    ("prompt_tokens", "100"),
    ("completion_tokens", True),
    ("latency_ms", -1),
    ("status", "done"),
    ("tags", "support"),
    ("tags", ["ok", 3]),
    ("created_at", "yesterday"),
    ("id", "   "),
])
def test_invalid_values(good_row, field, value):
    good_row[field] = value
    with pytest.raises(ValidationError) as info:
        UsageRecord.from_dict(good_row)
    assert info.value.field == field


def test_tags_are_optional(good_row):
    del good_row["tags"]
    assert UsageRecord.from_dict(good_row).tags == []


def test_non_object_is_rejected():
    with pytest.raises(ValidationError):
        UsageRecord.from_dict(["not", "a", "dict"])
