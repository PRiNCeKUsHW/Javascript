import os
from dataclasses import dataclass

DEFAULT_MODEL = "claude-opus-5-5"


@dataclass(frozen=True)
class Settings:
    model: str
    offline: bool
    budget_usd: float
    max_retries: int


def load_settings(force_offline: bool = False) -> Settings:
    """Read settings from environment variables. No key means offline mode."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    return Settings(
        model=os.environ.get("STUDY_MODEL", DEFAULT_MODEL),
        offline=force_offline or not has_key,
        budget_usd=float(os.environ.get("STUDY_BUDGET_USD", "0.50")),
        max_retries=int(os.environ.get("STUDY_MAX_RETRIES", "2")),
    )
