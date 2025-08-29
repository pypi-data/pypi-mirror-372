"""Validation helpers for environment variables."""

import re
from typing import Optional

_OPENAI_PREFIXES = ("sk-", "rk-", "ok-")  # allow common patterns; primarily sk- is used


def is_valid_openai_key(value: str) -> bool:
    """Return ``True`` if ``value`` looks like an OpenAI API key."""

    if not value or not isinstance(value, str):
        return False
    if not value.strip():
        return False
    # Basic sanity: starts with known prefix and long enough
    if not any(value.startswith(p) for p in _OPENAI_PREFIXES):
        return False
    return len(value) >= 20


def is_valid_telegram_api_id(value: Optional[str]) -> bool:
    """Validate that ``value`` is a positive integer string for Telegram API ID."""

    if value is None:
        return False
    value = value.strip()
    if not value.isdigit():
        return False
    try:
        return int(value) > 0
    except ValueError:
        return False


def is_valid_telegram_api_hash(value: Optional[str]) -> bool:
    """Return ``True`` if ``value`` matches Telegram's API hash format."""

    if value is None or not isinstance(value, str):
        return False
    v = value.strip()
    if not v:
        return False
    # Telegram hashes are 32+ hex/alnum chars; allow broader alnum to be safe
    return bool(re.fullmatch(r"[A-Za-z0-9]{20,64}", v))
