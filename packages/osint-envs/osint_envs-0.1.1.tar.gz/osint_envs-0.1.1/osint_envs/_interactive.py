"""Interactive prompt helpers for collecting configuration values.

Sensitive credentials are requested using :func:`getpass.getpass` so that
secrets are not echoed back to the terminal, helping to avoid accidental
exposure in logs or shell history.
"""

from __future__ import annotations

import getpass
from typing import Optional

from .validators import is_valid_openai_key


BANNER = """
------------------------------------------------------------
osint_envs — Interactive Setup
We'll collect only what's needed and write to your .env
(Values are stored locally in your project; keep them safe)
------------------------------------------------------------
"""


def prompt_openai_key(existing: Optional[str]) -> str:
    """Prompt the user for the OpenAI API key.

    ``getpass`` is used to avoid echoing the key. If ``existing`` is provided
    and the user presses ENTER, the existing value is retained.
    """

    print("\nOpenAI API Key (format typically starts with 'sk-')")
    if existing:
        print("Found an existing value. Press ENTER to keep it or enter a new one to replace.")
    while True:
        entered = getpass.getpass("OPENAI_API_KEY: ").strip()
        if entered:
            if not is_valid_openai_key(entered):
                print("Invalid OpenAI API key format. Please try again.")
                continue
            return entered
        if existing:
            # Keep current on empty input
            return existing
        print("OPENAI_API_KEY cannot be empty. Please paste your key.")


def prompt_telegram_api_id(existing: Optional[str]) -> str:
    """Prompt for the Telegram API ID.

    The API ID is numeric and not secret, so the standard :func:`input` prompt
    is sufficient. If ``existing`` is provided and the user presses ENTER, the
    existing value is preserved.
    """

    print("\nTelegram API ID (numeric).")
    if existing:
        print("Found an existing value. Press ENTER to keep it or enter a new one to replace.")
    while True:
        entered = input("TELEGRAM_API_ID: ").strip()
        if entered:
            return entered
        if existing:
            return existing
        print("TELEGRAM_API_ID cannot be empty.")


def prompt_telegram_api_hash(existing: Optional[str]) -> str:
    """Prompt the user for the Telegram API hash.

    The hash acts like a password, so ``getpass`` is used to keep it hidden. If
    ``existing`` is supplied and the user submits nothing, the existing value is
    kept.
    """

    print("\nTelegram API Hash (32+ alphanumeric chars).")
    if existing:
        print("Found an existing value. Press ENTER to keep it or enter a new one to replace.")
    while True:
        entered = getpass.getpass("TELEGRAM_API_HASH: ").strip()
        if entered:
            return entered
        if existing:
            return existing
        print("TELEGRAM_API_HASH cannot be empty.")

