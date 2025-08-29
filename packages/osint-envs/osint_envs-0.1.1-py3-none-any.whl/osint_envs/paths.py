from __future__ import annotations
from pathlib import Path
from collections.abc import Iterable
import logging
from typing import Optional

CANDIDATE_ROOT_MARKERS: Iterable[str] = (
    ".git",
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
)

def find_project_root(start: Optional[Path] = None) -> Path:
    """
    Walk upward to find a project root containing any of the known markers.
    If none found, returns the starting directory (or cwd).
    """
    if start is None:
        start = Path.cwd()
    start = start.resolve()

    current = start
    while True:
        if any((current / marker).exists() for marker in CANDIDATE_ROOT_MARKERS):
            return current
        if current.parent == current:
            # Reached filesystem root; fallback to start_dir
            return start
        current = current.parent

logger = logging.getLogger(__name__)


def ensure_gitignore_has_env(project_root: Path) -> None:
    """Ensure ``.env`` is listed in the project's ``.gitignore`` file."""

    gitignore = project_root / ".gitignore"
    try:
        if gitignore.exists():
            content = gitignore.read_text(encoding="utf-8", errors="ignore")
            lines = [ln.strip() for ln in content.splitlines()]
            if ".env" not in lines:
                with gitignore.open("a", encoding="utf-8") as f:
                    if not content.endswith("\n"):
                        f.write("\n")
                    f.write(".env\n")
        else:
            gitignore.write_text(".env\n", encoding="utf-8")
    except OSError as exc:
        logger.warning("Unable to update %s: %s", gitignore, exc)


def env_path(project_root: Path) -> Path:
    """Return the path to the ``.env`` file within ``project_root``."""

    return project_root / ".env"
