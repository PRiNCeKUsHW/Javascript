from dataclasses import dataclass
from datetime import datetime
from typing import Any

from toolkit.errors import ValidationError

ALLOWED_STATUS = {"ok", "error"}


def _require(data: dict[str, Any], field: str) -> Any:
    if field not in data:
        raise ValidationError(field, "is required")
    return data[field]


def _non_negative_int(data: dict[str, Any], field: str) -> int:
    value = _require(data, field)
    # bool is a subclass of int, so reject it explicitly
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValidationError(
            field, f"must be a non-negative integer, got {value!r}")
    return value


@dataclass(frozen=True)
class UsageRecord:
    """One call to a language model, as written in a usage log."""

    id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    status: str
    tags: list[str]
    created_at: datetime

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @classmethod
    def from_dict(cls, data: Any) -> "UsageRecord":
        if not isinstance(data, dict):
            raise ValidationError("record", "must be a JSON object")

        record_id = _require(data, "id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValidationError("id", "must be a non-empty string")

        model = _require(data, "model")
        if not isinstance(model, str) or not model.strip():
            raise ValidationError("model", "must be a non-empty string")

        latency = _require(data, "latency_ms")
        if (not isinstance(latency, (int, float))
                or isinstance(latency, bool) or latency < 0):
            raise ValidationError(
                "latency_ms", f"must be a non-negative number, got {latency!r}")

        status = _require(data, "status")
        if status not in ALLOWED_STATUS:
            raise ValidationError(
                "status",
                f"must be one of {sorted(ALLOWED_STATUS)}, got {status!r}")

        tags = data.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValidationError("tags", "must be a list of strings")

        try:
            created_at = datetime.fromisoformat(_require(data, "created_at"))
        except (TypeError, ValueError):
            raise ValidationError(
                "created_at", "must be an ISO 8601 date-time string") from None

        return cls(
            id=record_id,
            model=model,
            prompt_tokens=_non_negative_int(data, "prompt_tokens"),
            completion_tokens=_non_negative_int(data, "completion_tokens"),
            latency_ms=float(latency),
            status=status,
            tags=tags,
            created_at=created_at,
        )
