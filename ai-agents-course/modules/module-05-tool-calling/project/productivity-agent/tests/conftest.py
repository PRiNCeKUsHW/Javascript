import sys
from datetime import date
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from productivity.agent import ProductivityAgent  # noqa: E402
from productivity.client import make_client  # noqa: E402
from productivity.config import Settings  # noqa: E402
from productivity.fake_api import FakeAnthropicAPI  # noqa: E402
from productivity.policy import Policy  # noqa: E402
from productivity.pricing import CostTracker  # noqa: E402
from productivity.store import Store  # noqa: E402
from productivity.tools import Context  # noqa: E402

TODAY = date(2026, 10, 31)


@pytest.fixture(autouse=True)
def no_real_api(monkeypatch):
    """Tests never touch the network, a real key, or the user's data file."""
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "PROD_MODEL", "PROD_BUDGET_USD", "PROD_MAX_RETRIES", "PROD_MAX_STEPS",
                 "PROD_FAKE_FAIL", "PROD_FAKE_SLOW", "PROD_DATA", "PROD_TODAY"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def ctx(tmp_path):
    return Context(Store(tmp_path / "data.json"), TODAY)


def make_agent(ctx: Context, fake: FakeAnthropicAPI, read_only: bool = False,
               answer: bool | None = None, budget: float = 1.0,
               max_steps: int = 6) -> tuple[ProductivityAgent, Policy]:
    settings = Settings(model="claude-opus-5-5", offline=True, budget_usd=budget,
                        max_retries=2, max_steps=max_steps,
                        data_path=ctx.store.path, today=ctx.today)
    policy = Policy(ctx, read_only=read_only,
                    ask_human=None if answer is None else (lambda q: answer))
    agent = ProductivityAgent(make_client(settings, fake), settings.model,
                              CostTracker(budget), ctx, policy, max_steps)
    return agent, policy
