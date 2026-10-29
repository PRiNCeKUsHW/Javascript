from study.config import DEFAULT_MODEL, load_settings


def test_no_key_means_offline():
    settings = load_settings()
    assert settings.offline is True
    assert settings.model == DEFAULT_MODEL


def test_key_means_online(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    monkeypatch.setenv("STUDY_MODEL", "claude-haiku-5-5")
    settings = load_settings()
    assert settings.offline is False
    assert settings.model == "claude-haiku-5-5"


def test_offline_can_be_forced(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-real")
    assert load_settings(force_offline=True).offline is True
