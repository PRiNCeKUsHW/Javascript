import pytest

from study.errors import BudgetExceeded
from study.pricing import CostTracker, cost_usd


def test_cost_per_million_tokens():
    # 1M input at $4 + 1M output at $20
    assert cost_usd("claude-opus-5-5", 1_000_000, 1_000_000) == pytest.approx(24)


def test_small_call():
    assert cost_usd("claude-opus-5-5", 500, 200) == pytest.approx(0.006)


def test_unknown_model():
    with pytest.raises(KeyError):
        cost_usd("mystery-model", 1, 1)


def test_tracker_adds_and_enforces_budget():
    tracker = CostTracker(budget_usd=0.01)
    tracker.check()
    tracker.add("claude-opus-5-5", 500, 200)
    tracker.add("claude-opus-5-5", 500, 200)
    assert tracker.spent_usd == pytest.approx(0.012)
    with pytest.raises(BudgetExceeded):
        tracker.check()
