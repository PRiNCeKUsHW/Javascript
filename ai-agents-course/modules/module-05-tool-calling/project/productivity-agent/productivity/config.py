import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

DEFAULT_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Settings:
    model: str
    offline: bool
    budget_usd: float
    max_retries: int
    max_steps: int
    data_path: Path
    today: date


def load_settings(force_offline: bool = False) -> Settings:
    """Read settings from environment variables. No key means offline mode."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    today = os.environ.get("PROD_TODAY")       # fixed date for tests and demos
    return Settings(
        model=os.environ.get("PROD_MODEL", DEFAULT_MODEL),
        offline=force_offline or not has_key,
        budget_usd=float(os.environ.get("PROD_BUDGET_USD", "0.50")),
        max_retries=int(os.environ.get("PROD_MAX_RETRIES", "2")),
        max_steps=int(os.environ.get("PROD_MAX_STEPS", "6")),
        data_path=Path(os.environ.get("PROD_DATA", "productivity.json")),
        today=date.fromisoformat(today) if today else date.today(),
    )
