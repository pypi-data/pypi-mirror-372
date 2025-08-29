import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from osint_envs import handler


def _setup_tmp_root(tmp_path, monkeypatch):
    """Prepare an isolated project root for init()."""
    (tmp_path / "pyproject.toml").write_text("")
    monkeypatch.chdir(tmp_path)


def test_missing_openai_raises(tmp_path, monkeypatch):
    _setup_tmp_root(tmp_path, monkeypatch)
    monkeypatch.setenv("OSINT_ENVS_NONINTERACTIVE", "1")
    for key in ("OPENAI_API_KEY", "TELEGRAM_API_ID", "TELEGRAM_API_HASH"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        handler.init()


def test_missing_telegram_id_raises(tmp_path, monkeypatch):
    _setup_tmp_root(tmp_path, monkeypatch)
    monkeypatch.setenv("OSINT_ENVS_NONINTERACTIVE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "a" * 30)
    monkeypatch.delenv("TELEGRAM_API_ID", raising=False)
    monkeypatch.delenv("TELEGRAM_API_HASH", raising=False)
    with pytest.raises(RuntimeError, match="TELEGRAM_API_ID"):
        handler.init()


def test_noninteractive_success(tmp_path, monkeypatch):
    _setup_tmp_root(tmp_path, monkeypatch)
    monkeypatch.setenv("OSINT_ENVS_NONINTERACTIVE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "a" * 30)
    monkeypatch.setenv("TELEGRAM_API_ID", "123456")
    monkeypatch.setenv("TELEGRAM_API_HASH", "a" * 32)
    cfg = handler.init()
    assert cfg.openai_api_key.startswith("sk-")
    assert cfg.telegram_api_id == "123456"
    assert cfg.telegram_api_hash == "a" * 32
