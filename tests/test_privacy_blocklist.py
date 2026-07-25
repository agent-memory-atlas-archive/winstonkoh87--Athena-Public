"""
The privacy gate cannot scan its own blocklist — every pattern would match its
own definition, so the file sits in SKIP_FILES. That exclusion is what let six
real names, a client identifier, a private-topic list and two private folder
names live in a public file, unscanned, for roughly seven weeks.

These tests hold the replacement guard: the committed blocklist may contain
shape-describing matchers only. A literal word in a public blocklist publishes
the thing the blocklist exists to protect.
"""

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCAN_PATH = REPO_ROOT / ".github" / "scripts" / "privacy_scan.py"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("privacy_scan", SCAN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def scanner():
    if not SCAN_PATH.exists():
        pytest.skip("privacy_scan.py not present in this distribution")
    return _load_scanner()


def test_committed_blocklist_publishes_nothing(scanner):
    """The live blocklist must be free of literal words. This is the guard itself."""
    disclosures = scanner.audit_committed_blocklist()
    assert disclosures == [], (
        "The public blocklist names something it is meant to hide: "
        + "; ".join(f"line {d['line']}: {d['tokens']}" for d in disclosures)
    )


# ── The guard must be able to fail ───────────────────────────────────────────
# Every entry below is a real pattern that sat in the public blocklist before
# 2026-07-25, reduced to its shape. If the auditor stops flagging these, it has
# stopped working — a guard that cannot go red is not a guard.

@pytest.mark.parametrize(
    "pattern",
    [
        "Firstname Lastname",       # personal name, two tokens
        "Solomono",                 # client identifier, single token
        "Firstname[\\s-]?Lastname", # name with regex glue — still a name
        "limerance",                # private topic, lowercase
        "some_private_folder",      # private workspace folder
        "Titlecase Phrase",         # private document title
        "\\bkeyword\\b",            # word-boundary wrapper does not make it a shape
    ],
)
def test_auditor_flags_literal_words(scanner, tmp_path, monkeypatch, pattern):
    blocklist = tmp_path / "privacy_blocklist.txt"
    blocklist.write_text(f"# comment line\n{pattern}\n", encoding="utf-8")
    monkeypatch.setattr(scanner, "BLOCKLIST_PATH", blocklist)

    disclosures = scanner.audit_committed_blocklist()
    assert disclosures, f"auditor failed to flag literal-bearing pattern: {pattern}"
    assert disclosures[0]["line"] == 2


@pytest.mark.parametrize(
    "pattern",
    [
        "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}",
        "\\b(\\+?65[\\s-]?)?[89]\\d{3}[\\s-]?\\d{4}\\b",
        "eyJ[A-Za-z0-9_\\-]{10,}\\.[A-Za-z0-9_\\-]{4,}",
        "AKIA[0-9A-Z]{16}",
        "ghp_[A-Za-z0-9]{36}",
        "-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "/Users/winstonkoh/Desktop",
    ],
)
def test_auditor_allows_shape_matchers(scanner, tmp_path, monkeypatch, pattern):
    blocklist = tmp_path / "privacy_blocklist.txt"
    blocklist.write_text(f"{pattern}\n", encoding="utf-8")
    monkeypatch.setattr(scanner, "BLOCKLIST_PATH", blocklist)

    assert scanner.audit_committed_blocklist() == [], (
        f"auditor wrongly flagged a shape matcher: {pattern}"
    )


def test_blocklist_is_still_excluded_from_pattern_matching(scanner):
    """The exclusion stays — the audit replaces it, it does not remove it."""
    assert ".github/privacy_blocklist.txt" in scanner.SKIP_FILES
