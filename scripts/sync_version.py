#!/usr/bin/env python3
"""
Single source of truth version synchronizer.
Syncs version from pyproject.toml -> src/athena/__init__.py -> docs/ARCHITECTURE.md.

Two modes:
  (default)  rewrite the downstream files to match pyproject.toml
  --check    report drift and exit 1 without writing anything (for CI)

The --check mode exists because running the writer in CI is not a check: it
rewrote the files inside the runner, discarded them with the workspace, and
exited 0 whatever the state of the commit. Version drift could never fail the
build. CI now calls --check.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = ROOT / "pyproject.toml"
INIT_FILE = ROOT / "src/athena/__init__.py"

# Both copies carry a version heading and both drifted independently of
# pyproject.toml. Whichever is absent in a given distribution is skipped.
ARCH_FILES = (ROOT / "docs" / "ARCHITECTURE.md", ROOT / "ARCHITECTURE.md")


def read_ssot_version() -> str | None:
    """Return the version declared in pyproject.toml, or None if unreadable."""
    if not PYPROJECT.exists():
        print(f"ERROR: {PYPROJECT.name} not found.", file=sys.stderr)
        return None

    match = re.search(r'version\s*=\s*"([^"]+)"', PYPROJECT.read_text(encoding="utf-8"))
    if not match:
        print(f"ERROR: version not found in {PYPROJECT.name}.", file=sys.stderr)
        return None

    return match.group(1)


def rendered(path: Path, version: str) -> str | None:
    """Return `path`'s content with the version applied, or None if absent."""
    if not path.exists():
        return None

    content = path.read_text(encoding="utf-8")

    if path == INIT_FILE:
        return re.sub(
            r'__version__\s*=\s*"[^"]+"', f'__version__ = "{version}"', content
        )
    if path in ARCH_FILES:
        # The heading is `> **Version**: v9.9.1-gto`. The previous pattern was
        # `Version:\s*v[0-9.]+`, which cannot match across the bold markers, so
        # this file was never actually synced — while the script still printed
        # "Updated ...". Match both spellings and absorb any `-suffix`.
        return re.sub(
            r"(\*\*Version\*\*|Version):\s*v[0-9][0-9A-Za-z.\-]*",
            lambda m: f"{m.group(1)}: v{version}",
            content,
        )
    return content


def sync(check: bool) -> int:
    version = read_ssot_version()
    if version is None:
        return 1

    print(f"SSOT version from pyproject.toml: {version}")

    drifted: list[Path] = []

    for path in (INIT_FILE, *ARCH_FILES):
        updated = rendered(path, version)
        if updated is None:
            print(f"  skipped (not present): {path.relative_to(ROOT)}")
            continue

        rel = path.relative_to(ROOT)
        if updated == path.read_text(encoding="utf-8"):
            print(f"  in sync: {rel}")
            continue

        drifted.append(path)
        if check:
            print(f"  DRIFT: {rel} does not declare v{version}")
        else:
            path.write_text(updated, encoding="utf-8")
            print(f"  updated: {rel} -> v{version}")

    if check and drifted:
        names = ", ".join(str(p.relative_to(ROOT)) for p in drifted)
        print(
            f"\nVersion drift in {len(drifted)} file(s): {names}\n"
            f"Run `python scripts/sync_version.py` and commit the result.",
            file=sys.stderr,
        )
        return 1

    print("\nAll version references consistent." if check else "\nVersion sync complete.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift and exit 1 without writing (CI mode)",
    )
    sys.exit(sync(check=parser.parse_args().check))
