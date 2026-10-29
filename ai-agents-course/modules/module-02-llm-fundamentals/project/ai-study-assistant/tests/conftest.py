import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from study.assistant import StudyAssistant  # noqa: E402
from study.client import make_client  # noqa: E402
from study.config import Settings  # noqa: E402
from study.fake_api import FakeAnthropicAPI  # noqa: E402
from study.pricing import CostTracker  # noqa: E402


@pytest.fixture(autouse=True)
def no_real_api(monkeypatch):
    """Tests never touch the network or a real key."""
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL",
                 "STUDY_MODEL", "STUDY_BUDGET_USD", "STUDY_MAX_RETRIES",
                 "STUDY_FAKE_FAIL"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def fake() -> FakeAnthropicAPI:
    return FakeAnthropicAPI(failures=[])


@pytest.fixture
def assistant(fake) -> StudyAssistant:
    settings = Settings(model="claude-opus-5-5", offline=True, budget_usd=1.0,
                        max_retries=2)
    return StudyAssistant(make_client(settings, fake), settings.model,
                          CostTracker(settings.budget_usd))
