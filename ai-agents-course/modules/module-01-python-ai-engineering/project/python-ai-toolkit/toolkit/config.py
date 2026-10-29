import os
from dataclasses import dataclass
from pathlib import Path

from toolkit.errors import ToolkitError
from toolkit.loader import read_json


@dataclass(frozen=True)
class Settings:
    prices_file: Path
    currency: str


def load_dotenv(path: Path = Path(".env")) -> None:
    """Copy KEY=VALUE lines from .env into os.environ (real variables win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_settings() -> Settings:
    load_dotenv()
    prices = os.environ.get("TOOLKIT_PRICES_FILE", "config/prices.json")
    return Settings(
        prices_file=Path(prices),
        currency=os.environ.get("TOOLKIT_CURRENCY", "USD"),
    )


def load_prices(path: Path) -> dict[str, dict[str, float]]:
    """Prices are per 1 million tokens, keyed by model name."""
    data = read_json(path)
    if not isinstance(data, dict):
        raise ToolkitError(f"{path} must contain a JSON object")
    return {name: p for name, p in data.items() if not name.startswith("_")}
