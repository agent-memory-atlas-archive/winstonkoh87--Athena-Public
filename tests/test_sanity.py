import os
import sys

import pytest


def test_environment_check():
    """Verify we are running in the expected environment."""
    assert sys.version_info.major == 3, "Must be running Python 3"

def test_project_root_importable(project_root):
    """Verify that we can see the project root files."""
    assert os.path.exists(os.path.join(project_root, '.agent')), ".agent directory not found"
    # Athena package is installed as a dependency (likely editable), not necessarily a root folder


def test_athena_sdk_import():
    """Verify we can import the core SDK package."""
    try:
        import athena
        assert athena is not None
    except ImportError as e:
        pytest.fail(f"Failed to import athena SDK: {e}")
