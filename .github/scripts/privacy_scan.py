#!/usr/bin/env python3
"""
privacy_scan.py — Athena-Public Privacy Guard
=============================================
Scans staged files (or all tracked files) against the privacy blocklist.
Used as both a pre-commit hook and a standalone audit tool.

Usage:
  Pre-commit hook:  python3 .github/scripts/privacy_scan.py --staged
  Full audit:       python3 .github/scripts/privacy_scan.py --all
  Specific files:   python3 .github/scripts/privacy_scan.py file1.md file2.py
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# === CONFIG ===
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BLOCKLIST_PATH = REPO_ROOT / ".github" / "privacy_blocklist.txt"
ENV_PATH = REPO_ROOT / ".env"

# Patterns supplied out-of-band rather than committed. The blocklist file is
# public, so every name written into it is published by the very gate meant to
# protect it. These variables (from .env locally, repo secrets in CI) let
# name patterns live outside the tree. PRIVACY_EXTRA_PATTERNS holds one regex
# per line.
ENV_PATTERN_VARS = (
    "PRIVACY_EMAIL_PATTERN",
    "PRIVACY_PHONE_PATTERN",
    "PRIVACY_EXTRA_PATTERNS",
)

# File extensions to scan (skip binary/image files)
SCANNABLE_EXTENSIONS = {
    ".md",
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".css",
    ".html",
    ".astro",
    ".txt",
    ".csv",
}

# Directories to always skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist"}

# Files to always skip (e.g., the blocklist itself — it contains the patterns by definition)
SKIP_FILES = {".github/privacy_blocklist.txt"}


def load_blocklist() -> list[re.Pattern]:
    """Load regex patterns from the blocklist file."""
    if not BLOCKLIST_PATH.exists():
        print(f"⚠️  Blocklist not found at {BLOCKLIST_PATH}")
        return []

    patterns = []
    for line in BLOCKLIST_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line, re.IGNORECASE))
        except re.error as e:
            print(f"⚠️  Invalid regex in blocklist: '{line}' — {e}")
    return patterns


def _env_values() -> dict[str, str]:
    """Environment values, with `.env` at the repo root as a fallback source."""
    values = {}

    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw = line.partition("=")
            values[key.strip()] = raw.strip().strip("'\"")

    # A real environment variable always wins over the file.
    values.update({k: v for k, v in os.environ.items() if k in ENV_PATTERN_VARS})
    return values


def load_private_patterns() -> list[re.Pattern]:
    """Compile patterns supplied via environment rather than committed to the tree."""
    values = _env_values()
    patterns = []

    for var in ENV_PATTERN_VARS:
        raw = values.get(var, "").strip()
        if not raw:
            continue
        for entry in raw.splitlines():
            entry = entry.strip()
            if not entry or entry.startswith("#"):
                continue
            try:
                patterns.append(re.compile(entry, re.IGNORECASE))
            except re.error as e:
                print(f"⚠️  Invalid regex in {var}: '{entry}' — {e}")

    return patterns


def get_staged_files() -> list[Path]:
    """Get files staged for commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return [REPO_ROOT / f for f in result.stdout.strip().splitlines() if f]


def get_all_tracked_files() -> list[Path]:
    """Get all tracked files in the repo."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    return [REPO_ROOT / f for f in result.stdout.strip().splitlines() if f]


def should_scan(filepath: Path) -> bool:
    """Check if file should be scanned."""
    if filepath.suffix.lower() not in SCANNABLE_EXTENSIONS:
        return False
    for skip in SKIP_DIRS:
        if skip in filepath.parts:
            return False
    # Skip files that contain the patterns by definition (e.g., blocklist itself)
    try:
        rel = str(filepath.relative_to(REPO_ROOT))
        if rel in SKIP_FILES:
            return False
    except ValueError:
        pass
    return filepath.exists() and filepath.is_file()


def _display_path(filepath: Path) -> str:
    """Repo-relative path where possible, absolute otherwise."""
    try:
        return str(filepath.relative_to(REPO_ROOT))
    except ValueError:
        return str(filepath)


def scan_file(filepath: Path, patterns: list[re.Pattern]) -> list[dict]:
    """Scan a single file for blocklist violations."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
        return violations

    # Path resolution and matching stay outside the read guard: when a targeted
    # file sat outside the repo root, relative_to() raised mid-match, the whole
    # file was reported as unreadable, and its real violations were dropped —
    # the scan then exited 0. A privacy gate must never fail open.
    display = _display_path(filepath)

    for line_num, line in enumerate(content.splitlines(), 1):
        if "pds:allow" in line:  # inline allow marker for documented examples
            continue
        for pattern in patterns:
            if pattern.search(line):
                violations.append(
                    {
                        "file": display,
                        "line": line_num,
                        "pattern": pattern.pattern,
                        "content": line.strip()[:120],
                    }
                )
    return violations


def main():
    file_patterns = load_blocklist()
    private_patterns = load_private_patterns()
    patterns = file_patterns + private_patterns

    if not patterns:
        print("🚨 No blocklist patterns loaded — the gate cannot protect anything.")
        sys.exit(1)

    # Determine which files to scan
    if "--staged" in sys.argv:
        files = get_staged_files()
        mode = "STAGED"
    elif "--all" in sys.argv:
        files = get_all_tracked_files()
        mode = "FULL AUDIT"
    else:
        # Specific files passed as arguments
        files = [Path(f).resolve() for f in sys.argv[1:] if not f.startswith("-")]
        mode = "TARGETED"

    scannable = [f for f in files if should_scan(f)]

    print(
        f"🔍 Privacy Scan ({mode}): {len(scannable)} files against {len(patterns)} patterns "
        f"({len(file_patterns)} from blocklist, {len(private_patterns)} from environment)"
    )
    if not private_patterns:
        print(
            "ℹ️  No environment patterns set — only the committed blocklist is enforced. "
            f"Set {'/'.join(ENV_PATTERN_VARS)} to match names without publishing them."
        )
    print("─" * 60)

    all_violations = []
    for filepath in scannable:
        violations = scan_file(filepath, patterns)
        all_violations.extend(violations)

    if all_violations:
        print(f"\n🚨 BLOCKED — {len(all_violations)} privacy violation(s) found:\n")
        for v in all_violations:
            print(f"  ❌ {v['file']}:{v['line']}")
            print(f"     Pattern: {v['pattern']}")
            print(f"     Content: {v['content']}")
            print()

        if mode == "STAGED":
            print("═" * 60)
            print("🛑 COMMIT REJECTED — Fix violations above before committing.")
            print("   To bypass (emergency only): git commit --no-verify")
            print("═" * 60)

        sys.exit(1)
    else:
        print(f"✅ Clean — no privacy violations found in {len(scannable)} files.")
        sys.exit(0)


if __name__ == "__main__":
    main()
