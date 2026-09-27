"""Tests for maintenance_ratio.py — P0 classifier fix (TD-045 reforge).

Red Run proof (recorded in commit message):
  PRE-FIX:  test_classify_session_heartbeat_is_bookkeeping      → FAIL (returned 'maintenance')
            test_session_heartbeats_do_not_skew_active_ratio     → FAIL (active_total == 20, not 10)
  POST-FIX: Both pass. The property is: session heartbeats are neutral.
"""
import sys
from pathlib import Path

# Ensure .agent/scripts is on sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".agent" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import maintenance_ratio

# ---------------------------------------------------------------------------
# 1. Basic classification (the 4 buckets)
# ---------------------------------------------------------------------------

class TestClassifyConventionalTypes:
    """Output / maintenance / unlabeled classification for standard prefixes."""

    def test_feat_is_output(self):
        assert maintenance_ratio.classify("feat(case-study): add CS-628") == "output"

    def test_fix_is_output(self):
        assert maintenance_ratio.classify("fix(ci): upgrade setuptools") == "output"

    def test_feat_bare_no_scope_is_output(self):
        assert maintenance_ratio.classify("feat: add new feature") == "output"

    def test_fix_bare_no_scope_is_output(self):
        assert maintenance_ratio.classify("fix: patch bug") == "output"

    def test_feat_breaking_change_is_output(self):
        assert maintenance_ratio.classify("feat!: breaking API change") == "output"

    def test_feat_scoped_breaking_change_is_output(self):
        assert maintenance_ratio.classify("feat(api)!: breaking change") == "output"

    def test_chore_is_maintenance(self):
        assert maintenance_ratio.classify("chore(manifest): sync file hashes") == "maintenance"

    def test_refactor_is_maintenance(self):
        assert maintenance_ratio.classify("refactor(workflow): clean up steps") == "maintenance"

    def test_docs_non_session_is_maintenance(self):
        assert maintenance_ratio.classify("docs(projects): update switchboard") == "maintenance"

    def test_style_is_maintenance(self):
        assert maintenance_ratio.classify("style(lint): fix formatting") == "maintenance"

    def test_test_prefix_is_maintenance(self):
        assert maintenance_ratio.classify("test(core): add unit tests") == "maintenance"

    def test_ci_is_maintenance(self):
        assert maintenance_ratio.classify("ci(github): update workflow") == "maintenance"

    def test_unlabeled(self):
        assert maintenance_ratio.classify("Random commit message without prefix") == "unlabeled"

    def test_merge_commit_is_unlabeled(self):
        assert maintenance_ratio.classify("Merge branch 'main' into feature") == "unlabeled"


# ---------------------------------------------------------------------------
# 2. Bookkeeping scope exemptions (the reconciliation fix)
# ---------------------------------------------------------------------------

class TestClassifyBookkeeping:
    """Session closes, checkpoints, and ultraend are logging heartbeats — neutral.

    These scopes are exempted in BOTH:
    - maintenance_ratio.py (BOOKKEEPING_SCOPES)
    - .agent/hooks/commit-msg (case $SCOPE in session|checkpoint|ultraend)
    """

    def test_chore_session_is_bookkeeping(self):
        assert maintenance_ratio.classify("chore(session): close 2026-09-11 18:20") == "bookkeeping"

    def test_docs_session_is_bookkeeping(self):
        assert maintenance_ratio.classify("docs(session): close S961 via /ultraend") == "bookkeeping"

    def test_chore_checkpoint_is_bookkeeping(self):
        assert maintenance_ratio.classify("chore(checkpoint): reconcile S950 checkpoint") == "bookkeeping"

    def test_docs_ultraend_is_bookkeeping(self):
        assert maintenance_ratio.classify("docs(ultraend): complete S933 System-2 close") == "bookkeeping"

    def test_chore_ultraend_is_bookkeeping(self):
        assert maintenance_ratio.classify("chore(ultraend): S778 deep session close") == "bookkeeping"

    def test_feat_session_is_still_output(self):
        """A feat(session) commit is real output, not bookkeeping — prefix wins."""
        assert maintenance_ratio.classify("feat(session): S910 deep close") == "output"

    def test_fix_session_is_still_output(self):
        """A fix(session) commit is real output, not bookkeeping — prefix wins."""
        assert maintenance_ratio.classify("fix(session): repair broken checkpoint") == "output"


# ---------------------------------------------------------------------------
# 3. Ratio computation: the property under test
# ---------------------------------------------------------------------------

class TestMaintenanceRatioComputation:
    """The ratio must be computed over active work only (maintenance + output).
    Bookkeeping commits must not inflate the maintenance share."""

    def test_session_heartbeats_do_not_skew_ratio(self):
        """10 session closes + 8 output + 2 maintenance = 20% maintenance, not 80%+."""
        commits = [
            ("c01", "chore(session): close 1"),
            ("c02", "chore(session): close 2"),
            ("c03", "chore(session): close 3"),
            ("c04", "chore(session): close 4"),
            ("c05", "chore(session): close 5"),
            ("c06", "chore(session): close 6"),
            ("c07", "chore(session): close 7"),
            ("c08", "chore(session): close 8"),
            ("c09", "chore(session): close 9"),
            ("c10", "chore(session): close 10"),
            ("c11", "feat(revenue): client deliverable"),
            ("c12", "feat(trading): statement audit"),
            ("c13", "feat(fitness): log gym scan"),
            ("c14", "feat(pipeline): stage assignment"),
            ("c15", "fix(bug): fix runtime error"),
            ("c16", "feat(client): close deal"),
            ("c17", "feat(analysis): run Monte Carlo"),
            ("c18", "feat(code): ship deliverable"),
            ("c19", "chore(manifest): sync hashes"),
            ("c20", "refactor(infra): tidy config"),
        ]
        buckets = {"output": 0, "maintenance": 0, "bookkeeping": 0, "unlabeled": 0}
        for _, s in commits:
            buckets[maintenance_ratio.classify(s)] += 1

        assert buckets["bookkeeping"] == 10
        assert buckets["output"] == 8
        assert buckets["maintenance"] == 2

        active_total = buckets["output"] + buckets["maintenance"]
        assert active_total == 10
        maintenance_share = buckets["maintenance"] / active_total
        assert maintenance_share == 0.20
        assert maintenance_share < maintenance_ratio.ADVISORY_THRESHOLD

    def test_all_bookkeeping_yields_zero_maintenance(self):
        """If the only commits are session closes, active_total is 0 → 0% maintenance."""
        commits = [
            ("c1", "chore(session): close 1"),
            ("c2", "chore(session): close 2"),
            ("c3", "docs(session): close S999"),
        ]
        buckets = {"output": 0, "maintenance": 0, "bookkeeping": 0, "unlabeled": 0}
        for _, s in commits:
            buckets[maintenance_ratio.classify(s)] += 1

        active_total = buckets["output"] + buckets["maintenance"]
        assert active_total == 0
        # The script handles this with a ternary: 0.0 if active_total == 0
        maintenance_share = buckets["maintenance"] / active_total if active_total > 0 else 0.0
        assert maintenance_share == 0.0

    def test_pure_output_yields_zero_maintenance(self):
        """All feat/fix → 0% maintenance."""
        commits = [
            ("c1", "feat(api): ship endpoint"),
            ("c2", "fix(ui): patch layout"),
        ]
        buckets = {"output": 0, "maintenance": 0, "bookkeeping": 0, "unlabeled": 0}
        for _, s in commits:
            buckets[maintenance_ratio.classify(s)] += 1

        active_total = buckets["output"] + buckets["maintenance"]
        assert active_total == 2
        assert buckets["maintenance"] / active_total == 0.0

    def test_pure_maintenance_trips_threshold(self):
        """All chore/docs (non-session) → 100% maintenance, exceeds 70% threshold."""
        commits = [
            ("c1", "chore(manifest): sync"),
            ("c2", "docs(readme): update"),
            ("c3", "refactor(core): tidy"),
        ]
        buckets = {"output": 0, "maintenance": 0, "bookkeeping": 0, "unlabeled": 0}
        for _, s in commits:
            buckets[maintenance_ratio.classify(s)] += 1

        active_total = buckets["output"] + buckets["maintenance"]
        maintenance_share = buckets["maintenance"] / active_total
        assert maintenance_share == 1.0
        assert maintenance_share > maintenance_ratio.ADVISORY_THRESHOLD
