"""
test_delta_sync.py — Verification suite for P0 Delta Sync.
"""

import sys
from pathlib import Path

import pytest

# Add src to sys.path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path / "src"))

from athena.memory.delta_manifest import DeltaManifest


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temp workspace for testing."""
    manifest_path = tmp_path / "manifest.json"
    file_a = tmp_path / "file_a.md"
    file_a.write_text("Content A", encoding="utf-8")
    return {"manifest_path": manifest_path, "file_a": file_a}


def test_hash_calculation(temp_workspace):
    """Falsification: Does hashing work and normalize?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])

    # Baseline
    h1 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 is not None

    # Whitespace change -> Same hash
    temp_workspace["file_a"].write_text("Content A\n", encoding="utf-8")
    h2 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 == h2

    # Content change -> New hash
    temp_workspace["file_a"].write_text("Content B", encoding="utf-8")
    h3 = dm.calculate_hash(temp_workspace["file_a"])
    assert h1 != h3


def test_should_sync_logic(temp_workspace):
    """Falsification: Does should_sync return correct booleans?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])
    f = temp_workspace["file_a"]

    # 1. New file -> Sync
    assert dm.should_sync(f) is True

    # 2. Update manifest (Simulate sync)
    dm.update_entry(f)
    dm.save()

    # 3. No change -> Skip
    # Reload manifest to check persistence
    dm2 = DeltaManifest(temp_workspace["manifest_path"])
    assert dm2.should_sync(f) is False

    # 4. Content Change -> Sync
    f.write_text("New Content", encoding="utf-8")
    assert dm2.should_sync(f) is True


def test_stale_detection(temp_workspace):
    """Falsification: Do we detect deleted files?"""
    dm = DeltaManifest(temp_workspace["manifest_path"])
    f = temp_workspace["file_a"]

    # Register file
    dm.update_entry(f)

    # File exists -> Not stale
    assert dm.get_stale_files([f]) == []

    # File not passed in scan -> Stale
    assert len(dm.get_stale_files([])) == 1
    assert str(f) in dm.get_stale_files([])
