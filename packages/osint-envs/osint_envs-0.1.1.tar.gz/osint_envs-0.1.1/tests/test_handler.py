
from osint_envs import handler
import pytest
from osint_envs import handler


VALIDS = {
    "OPENAI_API_KEY": "sk-" + "a" * 50,
    "TELEGRAM_API_ID": "123456",
    "TELEGRAM_API_HASH": "a" * 32,
}


def test_init_noninteractive_persists_env(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    for k, v in VALIDS.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("OSINT_ENVS_NONINTERACTIVE", "1")

    def fail(*args, **kwargs):
        raise AssertionError("interactive prompt was called")

    monkeypatch.setattr(handler.ui, "prompt_openai_key", fail)
    monkeypatch.setattr(handler.ui, "prompt_telegram_api_id", fail)
    monkeypatch.setattr(handler.ui, "prompt_telegram_api_hash", fail)

    cfg = handler.init()

    env_file = tmp_path / ".env"
    assert env_file.exists()
    from dotenv import dotenv_values
    stored = dotenv_values(env_file)
    for k, v in VALIDS.items():
        assert stored.get(k) == v
        monkeypatch.delenv(k, raising=False)

    monkeypatch.setattr(handler.ui, "prompt_openai_key", fail)
    monkeypatch.setattr(handler.ui, "prompt_telegram_api_id", fail)
    monkeypatch.setattr(handler.ui, "prompt_telegram_api_hash", fail)

    cfg2 = handler.init()
    assert cfg2.openai_api_key == VALIDS["OPENAI_API_KEY"]
    assert cfg2.telegram_api_id == VALIDS["TELEGRAM_API_ID"]
    assert cfg2.telegram_api_hash == VALIDS["TELEGRAM_API_HASH"]


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc:
        handler.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "OpenAI" in out and "Telegram" in out


def test_sanitize_env_value():
    dirty = "clean\x00value\x1f"
    cleaned = handler._sanitize_env_value(dirty)
    assert "\x00" not in cleaned and "\x1f" not in cleaned
    assert "cleanvalue" in cleaned
