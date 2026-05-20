"""Shared pytest fixtures.

OPENHACK_ROOT is pinned to the repo root so ``paths.root()`` resolves
deterministically regardless of where pytest is invoked from. Modules under
test reach for ``root() / "agents" / "experts"`` and ``root() / "config"``,
so the real on-disk workspace is the simplest fixture.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from openhack.paths import ALL_RUN_DIRS

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(autouse=True)
def _pin_openhack_root(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENHACK_ROOT", str(REPO_ROOT))


@pytest.fixture()
def run_dir(tmp_path: Path) -> Path:
    """A scratch run directory with the standard subdirs created."""
    for name in ALL_RUN_DIRS:
        (tmp_path / name).mkdir(parents=True, exist_ok=True)
    return tmp_path
