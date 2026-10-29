from pathlib import Path

from toolkit.config import load_dotenv, load_prices, load_settings


def test_defaults(in_project):
    settings = load_settings()
    assert settings.prices_file == Path("config/prices.json")
    assert settings.currency == "USD"


def test_environment_variable_wins(in_project, monkeypatch):
    monkeypatch.setenv("TOOLKIT_CURRENCY", "EUR")
    assert load_settings().currency == "EUR"


def test_dotenv_file(tmp_path, monkeypatch):
    monkeypatch.delenv("TOOLKIT_CURRENCY", raising=False)
    env = tmp_path / ".env"
    env.write_text("# comment\nTOOLKIT_CURRENCY = INR\nnot a pair\n", encoding="utf-8")
    load_dotenv(env)
    import os
    assert os.environ["TOOLKIT_CURRENCY"] == "INR"
    monkeypatch.delenv("TOOLKIT_CURRENCY")


def test_prices_skip_note_keys(in_project):
    prices = load_prices(Path("config/prices.json"))
    assert set(prices) == {"model-small", "model-large"}
