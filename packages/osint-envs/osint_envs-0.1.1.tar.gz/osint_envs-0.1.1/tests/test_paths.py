from pathlib import Path

from osint_envs.paths import find_project_root, ensure_gitignore_has_env


def test_find_project_root(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "pyproject.toml").write_text("", encoding="utf-8")
    nested = root / "a" / "b"
    nested.mkdir(parents=True)

    found = find_project_root(nested)
    assert found == root


def test_ensure_gitignore_has_env(tmp_path):
    ensure_gitignore_has_env(tmp_path)
    gitignore = tmp_path / ".gitignore"
    assert gitignore.exists()
    assert gitignore.read_text(encoding="utf-8") == ".env\n"

    ensure_gitignore_has_env(tmp_path)
    assert gitignore.read_text(encoding="utf-8") == ".env\n"

    other = tmp_path / "other"
    other.mkdir()
    gi = other / ".gitignore"
    gi.write_text("something\n", encoding="utf-8")
    ensure_gitignore_has_env(other)
    assert gi.read_text(encoding="utf-8") == "something\n.env\n"

