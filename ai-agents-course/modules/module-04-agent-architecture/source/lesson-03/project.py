"""Lets the lesson scripts import the project's `calc_agent` package."""
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2] / "project/smart-calculator-agent"
sys.path.insert(0, str(PROJECT))

from calc_agent.client import make_client  # noqa: E402
from calc_agent.config import load_settings  # noqa: E402


def lesson_client():
    """A real client with ANTHROPIC_API_KEY, the offline fake without."""
    return make_client(load_settings())
