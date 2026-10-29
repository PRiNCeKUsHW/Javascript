import json
from pathlib import Path
from typing import Any

from toolkit.errors import ToolkitError, ValidationError
from toolkit.models import UsageRecord


def read_json(path: Path) -> Any:
    """Read a JSON file and turn every failure into one clear ToolkitError."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ToolkitError(f"file not found: {path}") from None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        where = f"line {exc.lineno}, column {exc.colno}"
        raise ToolkitError(f"{path} is not valid JSON ({where})") from None


def load_records(path: Path) -> tuple[list[UsageRecord], list[str]]:
    """Return the valid records and a readable message for each invalid one."""
    data = read_json(path)
    if not isinstance(data, list):
        raise ToolkitError(f"{path} must contain a JSON list of records")

    records: list[UsageRecord] = []
    problems: list[str] = []
    for number, item in enumerate(data, start=1):
        try:
            records.append(UsageRecord.from_dict(item))
        except ValidationError as exc:
            label = item.get("id", "no id") if isinstance(item, dict) else "no id"
            problems.append(f"record {number} ({label}): {exc}")
    return records, problems
