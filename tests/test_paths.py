"""Layer 2: path resolution and run-directory scaffolding."""

from __future__ import annotations

from pathlib import Path

import pytest

from openhack.paths import ALL_RUN_DIRS, ensure_run_dirs, root, run_path


def test_root_resolves_via_openhack_root_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENHACK_ROOT", str(Path(__file__).resolve().parent.parent))
    assert (root() / "agents" / "experts").is_dir()


def test_root_raises_when_env_var_points_at_non_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("OPENHACK_ROOT", str(tmp_path))
    with pytest.raises(RuntimeError, match="OPENHACK_ROOT is not a valid workspace root"):
        root()


def test_root_falls_back_to_walk_up_when_env_unset(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With no env var set, root() walks up from CWD / module location.

    The package is installed editable from this repo, so the module-location
    walk-up will land on the real workspace even when CWD is unrelated.
    """
    monkeypatch.delenv("OPENHACK_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    found = root()
    assert (found / "agents" / "experts").is_dir()
    assert (found / "templates" / "scenario-prompt.md").is_file()


def test_run_path_is_under_root() -> None:
    path = run_path("acme/widget", "2026-05-20-demo")
    assert path == root() / "runs" / "acme/widget" / "2026-05-20-demo"


def test_ensure_run_dirs_creates_every_standard_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``ensure_run_dirs`` materializes the full layout idempotently."""
    monkeypatch.setattr("openhack.paths.run_path", lambda target, run_id: tmp_path / target / run_id)
    created = ensure_run_dirs("acme/widget", "demo")
    for name in ALL_RUN_DIRS:
        assert (created / name).is_dir()
    # Idempotent: a second call must not raise.
    ensure_run_dirs("acme/widget", "demo")
