import os
import sys

import pytest


def test_environment_check():
    """Verify we are running in the expected environment."""
    assert sys.version_info.major == 3, "Must be running Python 3"

def test_project_root_importable():
    """Verify that we can see the project root files."""
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent
    assert (project_root / ".agent").exists() or (project_root / "src").exists(), \
        "Neither .agent directory nor src directory found at project root"


def test_athena_sdk_import():
    """Verify we can import the core SDK package."""
    try:
        import athena
        assert athena is not None
    except ImportError as e:
        pytest.fail(f"Failed to import athena SDK: {e}")
