import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from calc_agent.agent import CalculatorAgent  # noqa: E402
from calc_agent.client import make_client  # noqa: E402
from calc_agent.config import Settings  # noqa: E402
from calc_agent.fake_api import FakeAnthropicAPI  # noqa: E402
from calc_agent.pricing import CostTracker  # noqa: E402


@pytest.fixture(autouse=True)
def no_real_api(monkeypatch):
    """Tests never touch the network or a real key."""
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "CALC_MODEL", "CALC_BUDGET_USD", "CALC_MAX_RETRIES",
                 "CALC_MAX_STEPS", "CALC_FAKE_FAIL"):
        monkeypatch.delenv(name, raising=False)


def make_agent(fake: FakeAnthropicAPI, budget: float = 1.0,
               max_steps: int = 6) -> CalculatorAgent:
    settings = Settings(model="claude-opus-5-5", offline=True,
                        budget_usd=budget, max_retries=2, max_steps=max_steps)
    return CalculatorAgent(make_client(settings, fake), settings.model,
                           CostTracker(budget), max_steps)
