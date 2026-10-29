import pytest

from toolkit.models import UsageRecord
from toolkit.stats import estimate_cost, summarize


def make(good_row, **changes):
    return UsageRecord.from_dict({**good_row, **changes})


def test_cost_uses_price_per_million_tokens(good_row, prices):
    record = make(good_row, prompt_tokens=1_000_000, completion_tokens=1_000_000)
    assert estimate_cost(record, prices) == pytest.approx(2.0)


def test_unknown_model_has_no_price(good_row, prices):
    assert estimate_cost(make(good_row, model="mystery"), prices) is None


def test_summary_totals(good_row, prices):
    records = [
        make(good_row, id="a", latency_ms=100, tags=["x", "y"]),
        make(good_row, id="b", latency_ms=300, status="error", tags=["x"]),
        make(good_row, id="c", model="model-large", latency_ms=200, tags=[]),
    ]
    summary = summarize(records, prices)
    assert (summary.requests, summary.ok, summary.errors) == (3, 2, 1)
    assert summary.total_tokens == 450
    assert summary.avg_latency_ms == pytest.approx(200)
    assert summary.success_rate == pytest.approx(2 / 3)
    assert summary.top_tags == [("x", 2), ("y", 1)]
    assert list(summary.by_model) == ["model-large", "model-small"]
    assert summary.by_model["model-small"].requests == 2


def test_unpriced_models_are_listed_not_crashing(good_row, prices):
    summary = summarize([make(good_row, model="mystery")], prices)
    assert summary.unpriced_models == {"mystery"}
    assert summary.cost == 0


def test_empty_input(prices):
    summary = summarize([], prices)
    assert summary.requests == 0
    assert summary.success_rate == 0
    assert summary.avg_latency_ms == 0
