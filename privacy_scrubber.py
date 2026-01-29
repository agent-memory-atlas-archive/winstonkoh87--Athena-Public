#!/usr/bin/env python3
"""
Privacy Scrubber for Athena-Public
==================================
Removes personal identifiers from files before committing to public repo.

Usage:
    python privacy_scrubber.py [--dry-run]

This script scans all text files in the repository and replaces or removes
personal paths, names, and other PII.
"""

import argparse
import re
from pathlib import Path


# ============================================================================
# PATTERNS TO SCRUB
# ============================================================================

SCRUB_PATTERNS = [
    # Personal paths
    (r"[ATHENA_ROOT]", "[ATHENA_ROOT]"),
    (r"[USER_HOME]", "[USER_HOME]"),
    # Personal identifiers (keep name for attribution, scrub from paths)
    (r"winstonkoh87\.github\.io", "[USER_SITE]"),
    # Sensitive directories
    (r"[PROJECT_DIR][s]?", "[PROJECT_DIR]"),
    (r"[ASSIGNMENT_DIR]/]+", "[ASSIGNMENT_DIR]"),
]

# File extensions to process
TEXT_EXTENSIONS = {".md", ".py", ".txt", ".json", ".yaml", ".yml", ".toml", ".html", ".css", ".js"}

# Directories to skip
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}

# Files to skip entirely (keep personal branding)
SKIP_FILES = {"ABOUT_ME.md", "README.md"}


def should_process_file(file_path: Path) -> bool:
    """Check if a file should be processed."""
    # Skip non-text files
    if file_path.suffix.lower() not in TEXT_EXTENSIONS:
        return False

    # Skip certain files
    if file_path.name in SKIP_FILES:
        return False

    # Skip directories
    for skip_dir in SKIP_DIRS:
        if skip_dir in file_path.parts:
            return False

    return True


def scrub_file(file_path: Path, dry_run: bool = False) -> tuple[bool, list[str]]:
    """
    Scrub a single file of personal identifiers.

    Returns:
        (was_modified, list of changes made)
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return False, []

    original_content = content
    changes = []

    for pattern, replacement in SCRUB_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            content = re.sub(pattern, replacement, content)
            changes.append(f"  {pattern} → {replacement} ({len(matches)} occurrences)")

    if content != original_content:
        if not dry_run:
            file_path.write_text(content, encoding="utf-8")
        return True, changes

    return False, []


def main():
    parser = argparse.ArgumentParser(description="Scrub personal identifiers from Athena-Public")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    args = parser.parse_args()

    base_path = Path.cwd()

    print("=" * 60)
    print("🔒 ATHENA PRIVACY SCRUBBER")
    print("=" * 60)
    print(f"Scanning: {base_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    files_processed = 0
    files_modified = 0

    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue

        if not should_process_file(file_path):
            continue

        files_processed += 1
        was_modified, changes = scrub_file(file_path, args.dry_run)

        if was_modified:
            files_modified += 1
            print(f"📝 {file_path.relative_to(base_path)}")
            for change in changes:
                print(change)
            print()

    print("=" * 60)
    print(f"✅ Scan complete. {files_processed} files checked, {files_modified} modified.")
    if args.dry_run:
        print("   (Dry run - no files were actually changed)")
    print("=" * 60)


if __name__ == "__main__":
    main()
