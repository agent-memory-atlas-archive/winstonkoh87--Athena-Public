"""
tests.test_golden_path_e2e
==========================
End-to-end tests for workspace isolation, root resolution, and session lifecycle.
Verifies that Athena operates strictly within the target workspace and never pollutes
the package installation tree or leaks sessions across workspaces (Fix for F1).
"""

from pathlib import Path

import pytest

from athena.boot.shutdown import run_shutdown
from athena.cli.init import init_workspace
from athena.cli.save import run_quicksave
from athena.core.config import get_project_root, set_project_root
from athena.lifecycle.session_service import get_session_service
from athena.sessions import create_session, recall_last_session


def test_workspace_isolation_and_session_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Verify that initializing a workspace in tmp_path creates the session in tmp_path,
    saves checkpoints to it, and shuts it down cleanly without touching package root.
    """
    ws = tmp_path / "my_project"
    ws.mkdir()

    # Initialize workspace
    success = init_workspace(ws)
    assert success is True
    assert (ws / ".athena_root").exists()
    assert (ws / ".context" / "memories" / "session_logs").is_dir()

    # Switch CWD to ws and ensure ATHENA_ROOT is unset
    monkeypatch.chdir(ws)
    monkeypatch.delenv("ATHENA_ROOT", raising=False)

    # Invalidate cached root
    set_project_root(None)

    resolved_root = get_project_root()
    assert resolved_root == ws.resolve(), f"Expected {ws.resolve()}, got {resolved_root}"

    # Verify session service resolves to the workspace sessions dir
    svc = get_session_service()
    expected_sessions_dir = ws.resolve() / ".context" / "memories" / "session_logs"
    assert svc.sessions_dir == expected_sessions_dir

    # Create session
    session_file = create_session(focus="Golden Path E2E Test")
    assert session_file.exists()
    assert session_file.parent.resolve() == expected_sessions_dir.resolve()

    # Recall session
    recalled = recall_last_session()
    assert recalled is not None
    assert recalled.resolve() == session_file.resolve()

    # Run quicksave
    save_ok = run_quicksave("E2E Checkpoint", project_root=ws)
    assert save_ok is True
    content = session_file.read_text(encoding="utf-8")
    assert "E2E Checkpoint" in content

    # Run shutdown
    shutdown_ok = run_shutdown(project_root=ws)
    assert shutdown_ok is True
    closed_content = session_file.read_text(encoding="utf-8")
    assert "Status: Closed" in closed_content or "closed" in closed_content.lower()


def test_athena_root_env_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """
    Verify that ATHENA_ROOT environment variable takes precedence over CWD.
    """
    ws1 = tmp_path / "workspace_cwd"
    ws2 = tmp_path / "workspace_env"
    ws1.mkdir()
    ws2.mkdir()
    init_workspace(ws1)
    init_workspace(ws2)

    monkeypatch.chdir(ws1)
    monkeypatch.setenv("ATHENA_ROOT", str(ws2))
    set_project_root(None)

    assert get_project_root() == ws2.resolve()
    svc = get_session_service()
    assert svc.sessions_dir == ws2.resolve() / ".context" / "memories" / "session_logs"


def test_set_project_root_override(tmp_path: Path):
    """
    Verify that explicit set_project_root call dynamically updates all paths
    and invalidates SessionService singleton.
    """
    custom_ws = tmp_path / "custom_ws"
    custom_ws.mkdir()
    (custom_ws / ".athena_root").touch()

    set_project_root(custom_ws)
    assert get_project_root() == custom_ws.resolve()

    svc = get_session_service()
    assert svc.sessions_dir == custom_ws.resolve() / ".context" / "memories" / "session_logs"

    # Reset cache afterwards
    set_project_root(None)
