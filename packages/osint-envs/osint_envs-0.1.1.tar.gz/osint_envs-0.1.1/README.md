# osint_envs

`osint_envs` is a tiny helper that prepares your project for OpenAI and Telegram integrations.
It locates your project root, loads or creates a `.env`, validates required credentials and
prompts you to fill in anything missing. The resulting configuration is returned as a simple
dataclass so your scripts can immediately wire clients and continue.

## Features

- Auto-detects project root and reads/writes a `.env` file
- Validates presence and format of:
  - `OPENAI_API_KEY`
  - `TELEGRAM_API_ID`
  - `TELEGRAM_API_HASH`

- Interactively prompts for any missing/invalid values
- Writes/updates `.env` at your project root and attempts to set permissions to `600` (owner read/write only)
- Ensures `.env` is added to `.gitignore`
- Provides `init()` for scripts and a CLI `osint-env-setup`
- Supports non-interactive mode via `OSINT_ENVS_NONINTERACTIVE=1` to fail fast when values are missing


## Installation

```bash
pip install -e .

# or: pip install osint-envs  # if published on PyPI
```

## Usage

### Interactive script

```python
from osint_envs import init

def main():
    cfg = init()  # prompts for missing values
    from telethon import TelegramClient
    client = TelegramClient("session_name", int(cfg.telegram_api_id), cfg.telegram_api_hash)
    # continue using client or other services

if __name__ == "__main__":
    main()
```

### CLI setup

```bash
osint-env-setup --help  # usage and instructions
osint-env-setup        # interactive setup
# or
python -m osint_envs.handler
```

### Headless / CI

```python
import os
from osint_envs import init

# Disable prompts and raise RuntimeError if a value is missing
os.environ["OSINT_ENVS_NONINTERACTIVE"] = "1"
cfg = init()
```

## Tips & Notes

- The `.env` file is local to your project and should never be committed.
- Its permissions are set to `600` (read/write for the owner only) when possible; adjust manually if your platform doesn't support it.
- Sensitive prompts use `getpass.getpass()` so secrets aren't echoed to the terminal.
- For OpenAI usage, create a client after calling `init()`:

```python
from openai import OpenAI
cfg = init()
client = OpenAI(api_key=cfg.openai_api_key)
```

- Telethon sessions may prompt for 2FA on first run; subsequent runs reuse the session file.
 
## Security considerations

- Values written to `.env` are sanitized to remove control characters.
- Ensure `.env` remains out of version control and shared repositories.
- Avoid printing full secrets to logs; redact or shorten when necessary.

---

`osint_envs` keeps repeated boilerplate out of your agents, CLIs and scripts, letting you focus on the actual OSINT logic.


