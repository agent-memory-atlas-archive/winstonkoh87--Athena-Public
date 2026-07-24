"""
test_archive_manager.py — Verification suite for Phase 2 Hygiene.
"""

# Dynamic import helper
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


def import_archive_manager():
    spec = importlib.util.spec_from_file_location(
        "archive_manager",
        Path(__file__).parent.parent / ".agent" / "scripts" / "archive_manager.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


am = import_archive_manager()


@pytest.fixture
def fake_workspace():
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        hot_dir = tmp_path / "memories" / "session_logs"
        cold_dir = tmp_path / "archive" / "session_logs"
        hot_dir.mkdir(parents=True)

        # Monkeypatch global constants in the loaded module for this test
        # Note: This is hacky but effective for script testing without classes
        orig_hot = am.HOT_MEMORY_DIR
        orig_cold = am.COLD_STORAGE_DIR
        am.HOT_MEMORY_DIR = hot_dir
        am.COLD_STORAGE_DIR = cold_dir

        yield hot_dir, cold_dir

        # Cleanup monkeypatch
        am.HOT_MEMORY_DIR = orig_hot
        am.COLD_STORAGE_DIR = orig_cold


def test_date_extraction():
    """Falsification: Can we parse filenames?"""
    d1 = am.get_session_date("2025-01-01-session-01.md")
    assert d1.year == 2025 and d1.month == 1 and d1.day == 1

    d2 = am.get_session_date("invalid-file.md")
    assert d2 is None


def test_archival_logic(fake_workspace):
    """Falsification: Do old files move and new files stay?"""
    hot_dir, cold_dir = fake_workspace

    # 1. Create a "Old" file (60 days ago)
    old_date = datetime.now() - timedelta(days=60)
    old_name = f"{old_date.strftime('%Y-%m-%d')}-session-old.md"
    (hot_dir / old_name).write_text("Old Content")

    # 2. Create a "New" file (today)
    new_date = datetime.now()
    new_name = f"{new_date.strftime('%Y-%m-%d')}-session-new.md"
    (hot_dir / new_name).write_text("New Content")

    # 3. Run Archive (30 days threshold)
    am.archive_workspace(days=30, dry_run=False)

    # 4. Verify Old File Moved to Correct Path
    expected_year = old_date.strftime("%Y")
    expected_month = old_date.strftime("%m")
    expected_archive_path = cold_dir / expected_year / expected_month / old_name

    assert expected_archive_path.exists()
    assert not (hot_dir / old_name).exists()

    # 5. Verify New File Stayed
    assert (hot_dir / new_name).exists()
