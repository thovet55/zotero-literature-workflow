import pytest

from zotero_workflow.config import ConfigurationError, load_settings, redact_secret


def test_load_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    with pytest.raises(ConfigurationError, match="ZOTERO_API_KEY"):
        load_settings()


def test_load_settings_defaults_to_user_library(monkeypatch):
    monkeypatch.setenv("ZOTERO_API_KEY", "secret-value")
    monkeypatch.setenv("ZOTERO_LIBRARY_ID", "12345")
    settings = load_settings()
    assert settings.library_type == "user"
    assert settings.library_id == "12345"


def test_load_settings_reads_dotenv_from_zotero_dotenv(monkeypatch, tmp_path):
    env = tmp_path / "custom.env"
    env.write_text("ZOTERO_API_KEY=abc123\nZOTERO_LIBRARY_ID=42\n")
    monkeypatch.setenv("ZOTERO_DOTENV", str(env))
    monkeypatch.delenv("ZOTERO_API_KEY", raising=False)
    monkeypatch.delenv("ZOTERO_LIBRARY_ID", raising=False)
    settings = load_settings()
    assert settings.api_key == "abc123"
    assert settings.library_id == "42"


def test_redact_secret_never_returns_full_value():
    assert redact_secret("secret-value") == "sec...lue"
    assert "secret-value" not in redact_secret("secret-value")
