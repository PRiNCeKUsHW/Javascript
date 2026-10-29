import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))


@pytest.fixture
def good_row() -> dict:
    return {"id": "req-1", "model": "model-small", "prompt_tokens": 100, "completion_tokens": 50,
            "latency_ms": 500, "status": "ok", "tags": ["summarize"],
            "created_at": "2026-03-02T09:15:00+00:00"}


@pytest.fixture
def prices() -> dict:
    return {"model-small": {"input": 0.5, "output": 1.5}, "model-large": {"input": 3.0, "output": 15.0}}


@pytest.fixture
def in_project(monkeypatch):
    """Run from the project folder, with no toolkit settings leaking in from the shell."""
    monkeypatch.chdir(PROJECT)
    monkeypatch.delenv("TOOLKIT_PRICES_FILE", raising=False)
    monkeypatch.delenv("TOOLKIT_CURRENCY", raising=False)
    return PROJECT
