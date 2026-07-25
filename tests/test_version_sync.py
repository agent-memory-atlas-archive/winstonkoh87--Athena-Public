"""
Test version consistency across project configuration and Python package.
"""

import re
from pathlib import Path

import athena


def test_version_alignment():
    root = Path(__file__).resolve().parent.parent
    pyproject = root / "pyproject.toml"
    assert pyproject.exists()

    content = pyproject.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    assert match is not None
    ssot_version = match.group(1)

    assert athena.__version__ == ssot_version
