#!/usr/bin/env python3
"""
Single source of truth version synchronizer.
Syncs version from pyproject.toml -> src/athena/__init__.py -> docs/ARCHITECTURE.md.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
INIT_FILE = ROOT / "src/athena/__init__.py"
ARCH_FILE = ROOT / "docs" / "ARCHITECTURE.md"

def sync():
    if not PYPROJECT.exists():
        print("pyproject.toml not found.")
        return

    content = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        print("Version not found in pyproject.toml.")
        return

    version = match.group(1)
    print(f"SSOT Version from pyproject.toml: {version}")

    # Update src/athena/__init__.py
    if INIT_FILE.exists():
        init_content = INIT_FILE.read_text(encoding="utf-8")
        updated_init = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{version}"', init_content)
        INIT_FILE.write_text(updated_init, encoding="utf-8")
        print(f"Updated {INIT_FILE.relative_to(ROOT)} to {version}")

    # Update docs/ARCHITECTURE.md if present
    if ARCH_FILE.exists():
        arch_content = ARCH_FILE.read_text(encoding="utf-8")
        updated_arch = re.sub(r'Version:\s*v[0-9.]+', f'Version: v{version}', arch_content)
        ARCH_FILE.write_text(updated_arch, encoding="utf-8")
        print(f"Updated {ARCH_FILE.relative_to(ROOT)} to v{version}")

if __name__ == "__main__":
    sync()
