import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from resume.analyzer import Analyzer  # noqa: E402
from resume.client import make_client  # noqa: E402
from resume.config import Settings  # noqa: E402
from resume.fake_api import FakeAnthropicAPI  # noqa: E402
from resume.pricing import CostTracker  # noqa: E402


@pytest.fixture(autouse=True)
def no_real_api(monkeypatch):
    """Tests never touch the network or a real key."""
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "RESUME_MODEL", "RESUME_BUDGET_USD", "RESUME_MAX_RETRIES",
                 "RESUME_FAKE_FAIL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def fake() -> FakeAnthropicAPI:
    return FakeAnthropicAPI(failures=[])


def make_analyzer(fake: FakeAnthropicAPI, budget: float = 1.0,
                  versions: dict[str, str] | None = None) -> Analyzer:
    settings = Settings(model="claude-opus-5-5", offline=True,
                        budget_usd=budget, max_retries=2)
    return Analyzer(make_client(settings, fake), settings.model,
                    CostTracker(budget), versions)


@pytest.fixture
def analyzer(fake) -> Analyzer:
    return make_analyzer(fake)


@pytest.fixture
def sam() -> str:
    return (PROJECT / "data/resume_sam.md").read_text(encoding="utf-8")


@pytest.fixture
def job() -> str:
    return (PROJECT / "data/job_backend.md").read_text(encoding="utf-8")
