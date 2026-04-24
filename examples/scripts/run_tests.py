#!/usr/bin/env python3
"""
run_tests.py — Regression Test Runner for Core Identity Validation

Validates that Core_Identity.md contains required structural elements.
Part of /refactor Phase 6.6 validation.

Usage: python3 .agent/scripts/run_tests.py
"""

import sys
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).resolve().parent.parent.parent
CORE_IDENTITY = (
    WORKSPACE / ".framework" / "v8.2-stable" / "modules" / "Core_Identity.md"
)

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_section(content: str, marker: str, name: str) -> bool:
    """Check if a section marker exists in content."""
    found = marker in content
    status = f"{GREEN}✓{RESET}" if found else f"{RED}✗{RESET}"
    print(f"  {status} {name}")
    return found


def check_line_count(filepath: Path, max_lines: int, name: str) -> bool:
    """Check if a file is under the line count threshold."""
    if not filepath.exists():
        print(f"  {RED}✗{RESET} {name} (file not found)")
        return False
    lines = len(filepath.read_text(encoding="utf-8").splitlines())
    ok = lines <= max_lines
    status = f"{GREEN}✓{RESET}" if ok else f"{RED}✗{RESET}"
    print(f"  {status} {name} ({lines}/{max_lines} lines)")
    return ok


def main():
    print("\n" + "=" * 60)
    print("🧪 REGRESSION TEST SUITE — Core Identity + Memory Bank")
    print("=" * 60 + "\n")

    passed = 0
    failed = 0

    # --- Phase 1: Core Identity Validation ---
    if not CORE_IDENTITY.exists():
        print(f"{RED}❌ Core_Identity.md not found!{RESET}")
        print(f"   Expected: {CORE_IDENTITY}")
        return 1

    print(f"📋 Phase 1: Core Identity ({CORE_IDENTITY.name})\n")

    content = CORE_IDENTITY.read_text(encoding="utf-8")

    # Define required sections
    checks = [
        ("## 0.3 四大絕對法則", "Laws #0-4 Section"),
        ("⛔ 法則#1", "Law #1: Ruin Prevention"),
        ("🎯 法則#2", "Law #2: Arena Physics"),
        ("📊 法則#3", "Law #3: Revealed Preference"),
        ("💎 法則#0", "Law #0: Subjective Utility"),
        ("🧩 法則#4", "Law #4: Modular Architecture"),
        ("📚 法則#5", "Law #5: Epistemic Rigor"),
        ("### 0.6 Checkpoint Protocol", "Quicksave Section"),
        ("### 0.7 Auto-Documentation", "Auto-Documentation Section"),
        ("### 0.7.1 Semantic Search", "Semantic Search Section"),
        ("### 0.5.1 Estimated Complexity Score", "Λ Latency Section"),
        ("Committee Seats", "COS Structure"),
    ]

    print("Structural Checks:")
    for marker, name in checks:
        if check_section(content, marker, name):
            passed += 1
        else:
            failed += 1

    # --- Phase 2: Memory Bank Validation ---
    MEMORY_BANK = WORKSPACE / ".context" / "memory_bank"

    print(f"\n📋 Phase 2: Memory Bank ({MEMORY_BANK.name}/)\n")

    # userContext.md checks
    user_ctx = MEMORY_BANK / "userContext.md"
    if user_ctx.exists():
        uc = user_ctx.read_text(encoding="utf-8")
        mb_checks = [
            (uc, "Anti-Sycophancy", "userContext: Anti-Sycophancy Constraints"),
            (uc, "Core Axioms (Immutable)", "userContext: Core Axioms Section"),
            (uc, "Half-Kelly Criterion", "userContext: Half-Kelly Axiom"),
            (uc, "Distribution First", "userContext: Distribution First Axiom"),
        ]
        print("Identity Layer:")
        for content_str, marker, name in mb_checks:
            if check_section(content_str, marker, name):
                passed += 1
            else:
                failed += 1

    # productContext.md checks
    prod_ctx = MEMORY_BANK / "productContext.md"
    if prod_ctx.exists():
        pc = prod_ctx.read_text(encoding="utf-8")
        print("\nMission Layer:")
        if check_section(pc, "Circuit Breaker", "productContext: Circuit Breaker"):
            passed += 1
        else:
            failed += 1

    # activeContext.md compaction gate
    active_ctx = MEMORY_BANK / "activeContext.md"
    print("\nState Layer:")
    if check_line_count(active_ctx, 250, "activeContext: Compaction Gate (≤250 lines)"):
        passed += 1
    else:
        failed += 1

    # Summary
    print("\n" + "-" * 40)
    total = passed + failed

    if failed == 0:
        print(f"{GREEN}✅ All tests passed ({passed}/{total}){RESET}")
        verdict = 0
    elif failed <= 2:
        print(f"{YELLOW}⚠️ Some tests failed ({passed}/{total} passed){RESET}")
        verdict = 0  # Soft fail
    else:
        print(f"{RED}❌ Critical failures ({failed}/{total} failed){RESET}")
        verdict = 1

    print("=" * 60 + "\n")
    return verdict


if __name__ == "__main__":
    sys.exit(main())
