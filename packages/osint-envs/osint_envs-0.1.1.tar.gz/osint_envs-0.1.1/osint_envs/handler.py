from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:  # pragma: no cover - dependency presence is assumed during tests
    from dotenv import dotenv_values, load_dotenv, set_key
except ImportError as exc:  # pragma: no cover - runtime guidance
    raise ImportError(
        "python-dotenv is required. Install with: pip install python-dotenv"
    ) from exc

from .paths import env_path, ensure_gitignore_has_env, find_project_root
from .validators import (
    is_valid_openai_key,
    is_valid_telegram_api_id,
    is_valid_telegram_api_hash,
)
from . import _interactive as ui


@dataclass
class APIConfig:
    """Container for validated API configuration values."""

    openai_api_key: str
    telegram_api_id: str
    telegram_api_hash: str
    project_root: Path
    env_file: Path

    def __repr__(self) -> str:  # pragma: no cover - formatting helper
        return (
            "APIConfig("
            f"openai_api_key='{_redact(self.openai_api_key)}', "
            f"telegram_api_id='{self.telegram_api_id}', "
            f"telegram_api_hash='{_redact(self.telegram_api_hash)}', "
            f"project_root={self.project_root!r}, "
            f"env_file={self.env_file!r})"
        )


def _redact(secret: str, visible: int = 4) -> str:
    """Return a partially masked version of ``secret`` for logging.

    Only the first and last ``visible`` characters are shown; the middle portion
    is replaced with ellipsis.  This helps avoid leaking full credentials in
    log messages or stack traces.
    """

    if not secret:
        return ""
    if len(secret) <= visible * 2:
        return "*" * len(secret)
    return f"{secret[:visible]}...{secret[-visible:]}"


NEEDED_KEYS = ("OPENAI_API_KEY", "TELEGRAM_API_ID", "TELEGRAM_API_HASH")


def _is_noninteractive() -> bool:
    """Return True if prompts should be disabled."""
    return os.environ.get("OSINT_ENVS_NONINTERACTIVE", "0") == "1"


def _load_env(env_file: Path) -> Dict[str, str]:
    """
    Loads the .env file into process env for immediate use and returns dict.
    If the file doesn't exist, returns an empty dict.
    """
    if env_file.exists():
        load_dotenv(dotenv_path=env_file, override=False)
        return {**dotenv_values(env_file)}
    return {}


def _sanitize_env_value(value: str) -> str:
    """Remove potentially dangerous characters from env values."""

    if not value:
        return value
    return "".join(
        char for char in value if ord(char) >= 32 or char in "\t\n\r"
    )


def _persist_env_value(env_file: Path, key: str, value: str) -> None:
    """Persist a key/value pair to the ``.env`` file with safe permissions."""

    env_file.parent.mkdir(parents=True, exist_ok=True)
    sanitized = _sanitize_env_value(value)
    # set_key creates or updates the key in .env file
    set_key(str(env_file), key, sanitized)
    try:
        # limit permissions to owner read/write
        os.chmod(env_file, 0o600)
    except OSError as exc:
        logging.getLogger(__name__).warning(
            "Could not set secure permissions on %s: %s", env_file, exc
        )


def _ensure_values(project_root: Path, env_file: Path) -> APIConfig:
    """
    Ensure required values exist and are valid. Prompt if missing/invalid.
    Returns APIConfig and guarantees values are written to .env and loaded in os.environ.
    """
    if not _is_noninteractive():
        print(ui.BANNER)

    current = _load_env(env_file)
    file_keys = set(current.keys())
    missing_from_file = {k for k in NEEDED_KEYS if k not in file_keys}

    # Also check process env as a fallback, but prefer file for persistence
    for k in NEEDED_KEYS:
        if k not in current and k in os.environ and os.environ[k].strip():
            current[k] = os.environ[k].strip()

    # Validate or prompt each value
    # OPENAI_API_KEY
    ok = current.get("OPENAI_API_KEY", "").strip() or None
    if not is_valid_openai_key(ok or ""):
        if _is_noninteractive():
            raise RuntimeError(
                "OPENAI_API_KEY is required but missing. "
                "Either set it in your environment or remove OSINT_ENVS_NONINTERACTIVE=1 "
                "to enable interactive prompts."
            )
        ok = ui.prompt_openai_key(existing=None)
        while not is_valid_openai_key(ok):
            print("That doesn't look like a valid OpenAI key. Try again.")
            ok = ui.prompt_openai_key(existing=None)
        _persist_env_value(env_file, "OPENAI_API_KEY", ok)

    elif "OPENAI_API_KEY" in missing_from_file and ok is not None:
        # Value came from process env but wasn't in the file; persist it.

        _persist_env_value(env_file, "OPENAI_API_KEY", ok)

    # TELEGRAM_API_ID
    tid = current.get("TELEGRAM_API_ID", "").strip() or None
    if not is_valid_telegram_api_id(tid or ""):
        if _is_noninteractive():
            raise RuntimeError(
                "TELEGRAM_API_ID is required but missing. "
                "Either set it in your environment or remove OSINT_ENVS_NONINTERACTIVE=1 "
                "to enable interactive prompts."
            )
        tid = ui.prompt_telegram_api_id(existing=None)
        while not is_valid_telegram_api_id(tid):
            print("Invalid API ID. It must be a positive integer.")
            tid = ui.prompt_telegram_api_id(existing=None)
        _persist_env_value(env_file, "TELEGRAM_API_ID", tid)

    elif "TELEGRAM_API_ID" in missing_from_file and tid is not None:

        _persist_env_value(env_file, "TELEGRAM_API_ID", tid)

    # TELEGRAM_API_HASH
    thash = current.get("TELEGRAM_API_HASH", "").strip() or None
    if not is_valid_telegram_api_hash(thash or ""):
        if _is_noninteractive():
            raise RuntimeError(
                "TELEGRAM_API_HASH is required but missing. "
                "Either set it in your environment or remove OSINT_ENVS_NONINTERACTIVE=1 "
                "to enable interactive prompts."
            )
        thash = ui.prompt_telegram_api_hash(existing=None)
        while not is_valid_telegram_api_hash(thash):
            print("Invalid API hash. It should be 20-64 alphanumeric characters.")
            thash = ui.prompt_telegram_api_hash(existing=None)
        _persist_env_value(env_file, "TELEGRAM_API_HASH", thash)

    elif "TELEGRAM_API_HASH" not in file_keys and thash is not None:

        _persist_env_value(env_file, "TELEGRAM_API_HASH", thash)

    # Reload into process env for immediate access
    load_dotenv(dotenv_path=env_file, override=True)

    # Final values from env
    cfg = APIConfig(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        telegram_api_id=os.environ.get("TELEGRAM_API_ID", ""),
        telegram_api_hash=os.environ.get("TELEGRAM_API_HASH", ""),
        project_root=project_root,
        env_file=env_file,
    )
    return cfg


def init() -> APIConfig:
    """
    Primary entry point for scripts:

        from osint_envs import init
        config = init()

    - Finds project root
    - Ensures `.env` exists with required keys (prompts if missing)
    - Adds `.env` to `.gitignore`
    - Returns an APIConfig dataclass with loaded values
    """
    project_root = find_project_root()
    env_file = env_path(project_root)
    ensure_gitignore_has_env(project_root)
    config = _ensure_values(project_root, env_file)
    return config


def main(argv: Optional[List[str]] = None) -> None:
    """
    CLI entry point:

        osint-env-setup
        # or:
        python -m osint_envs.handler
    """
    parser = argparse.ArgumentParser(
        prog="osint-env-setup",
        description=(
            "Prepare a .env with OpenAI and Telegram credentials. "
            "Prompts for missing values."
        ),
        epilog=(
            "Set OSINT_ENVS_NONINTERACTIVE=1 to fail instead of prompting."
        ),
    )
    parser.parse_args(argv)

    try:
        cfg = init()
        print("\n✅ Setup complete.")
        print(f"Project root: {cfg.project_root}")
        print(f".env file:    {cfg.env_file}")
        print("Keys available in environment now:")
        print("  - OPENAI_API_KEY")
        print("  - TELEGRAM_API_ID")
        print("  - TELEGRAM_API_HASH")
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
