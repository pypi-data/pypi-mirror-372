import pytest
from osint_envs import validators


def test_is_valid_openai_key():
    assert validators.is_valid_openai_key("sk-" + "a" * 30)
    assert not validators.is_valid_openai_key("sk-short")
    assert not validators.is_valid_openai_key("rk-" + "short")
    assert not validators.is_valid_openai_key("")
    assert not validators.is_valid_openai_key(None)


def test_is_valid_telegram_api_id():
    assert validators.is_valid_telegram_api_id("12345")
    assert not validators.is_valid_telegram_api_id("-1")
    assert not validators.is_valid_telegram_api_id("abc")
    assert not validators.is_valid_telegram_api_id("")
    assert not validators.is_valid_telegram_api_id(None)


def test_is_valid_telegram_api_hash():
    assert validators.is_valid_telegram_api_hash("a" * 32)
    assert validators.is_valid_telegram_api_hash("A1" * 16)
    assert not validators.is_valid_telegram_api_hash("short")
    assert not validators.is_valid_telegram_api_hash("" )
    assert not validators.is_valid_telegram_api_hash(None)
