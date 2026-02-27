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

import re
import subprocess
import sys
from pathlib import Path

# === CONFIG ===
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BLOCKLIST_PATH = REPO_ROOT / ".github" / "privacy_blocklist.txt"

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
    return filepath.exists() and filepath.is_file()


def scan_file(filepath: Path, patterns: list[re.Pattern]) -> list[dict]:
    """Scan a single file for blocklist violations."""
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern in patterns:
                if pattern.search(line):
                    violations.append(
                        {
                            "file": str(filepath.relative_to(REPO_ROOT)),
                            "line": line_num,
                            "pattern": pattern.pattern,
                            "content": line.strip()[:120],
                        }
                    )
    except Exception as e:
        print(f"⚠️  Could not read {filepath}: {e}")
    return violations


def main():
    patterns = load_blocklist()
    if not patterns:
        print("✅ No blocklist patterns loaded. Exiting.")
        sys.exit(0)

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
        f"🔍 Privacy Scan ({mode}): {len(scannable)} files against {len(patterns)} patterns"
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
