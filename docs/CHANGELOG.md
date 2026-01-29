# Athena Changelog

> **Last Updated**: 29 January 2026

This document provides detailed release notes. For the brief summary, see the README changelog.

---

## v8.0-Stable (29 January 2026)

**Zero-Point Refactor**: Sovereign Environment hardened, score-modulated RRF weights rebalanced.

### Key Changes

- **Sovereign Environment**: Consolidated silos into `.context/`, created `settings.json`, `ensure_env.sh`
- **Score-Modulated RRF**: Formula updated to `contrib = weight * (0.5 + doc.score) * (1/(k+rank))`
- **Weight Rebalance**: GraphRAG 3.5x → 2.0x, Vector 1.3x → 2.0x, Canonical boosted to 3.0x
- **Metrics**: Sessions 861, Protocols 150+, Case Studies 42

---

## v1.3.0 (10 January 2026)

**Framework Materialization**: Made Athena-Public a *functional* framework, not just documentation.

### Key Changes

- **Functional Boot Orchestrator**: Replaced mock `lambda: True` stubs with real logic that:
  - Creates `session_logs/` directory structure
  - Generates timestamped session log files
  - Verifies Core_Identity.md integrity (SHA-256)
  - Primes semantic memory (if Supabase configured)
- **`examples/framework/Core_Identity.md`** (NEW): Sanitized Laws #0-6, Committee of Seats, Λ scoring
- **MANIFESTO.md**: Added "Bionic Unit" and "Law #6: Triple-Lock" sections
- **RISK_PLAYBOOKS.md**: Added Tier Classification legend (Tier 1/2/3 with icons)
- **Metrics**: Sessions 810, Protocols 285

### Philosophy

*From*: "Here is the author's Brain."
*To*: "Here is the Framework to Build Your Own Brain."

The public repo now provides the *engine*, not just the *manual*.

---

## v1.2.9 (09 January 2026)

**Docs & Insights Update**: README enhanced with new positioning insights.

### Key Changes

- **Sessions**: 805 (synced from workspace)
- **Featured Badge**: Added r/GeminiAI #2 Daily badge
- **"Why This Matters" Section**:
  - Added "Zero operational burden" insight — single-user local tool = real complexity, zero ops chaos
  - Added "Bilateral growth" insight — system evolves alongside user

**Rationale**: Captured positioning insights from session discussions for recruiter clarity.

---

## v1.2.8 (06 January 2026)

**Grand Alignment Refactor**: Supabase schema hardened (11 tables + RLS), Memory Insurance layer stabilized.

### Key Changes

- **Metrics Corrected**: Protocols audited to 285, sessions at 768, scripts at 122
- **Memory Insurance**: Formalized the concept of Supabase as disaster recovery layer, not just search
- **Schema Hardening**: All 11 Supabase tables now have RLS enabled and hardened search paths

**Rationale**: The previous protocol count (332) included archived items. This release establishes accurate canonical metrics.

---

## v1.2.6 (05 January 2026)

**Stats Sync**: 605 sessions, 277 protocols, 119 scripts

### Backend Refactor: `athena.memory.sync`

Major architectural cleanup of the Supabase sync pipeline:

- **`supabase_sync.py`**: Refactored to use the `athena` SDK pattern. Cleaner separation between embedding generation and database operations.
- **`public_sync.py`**: New tool for sanitized sync to `Athena-Public`. Ensures private memories never leak to the public repository.
- **`athena.tools.macro_graph`**: Added macro-level knowledge graph tooling for visualizing cross-file relationships.

**Rationale**: The previous sync scripts were monolithic and tightly coupled. This refactor enables:

- Independent testing of embedding vs. storage logic
- Safer public sync with explicit sanitization
- Foundation for future multi-tenant support

### Governance: Cognitive Profile Refinements

Integrated red-team feedback into Athena's cognitive profile:

| Change | Before | After |
|--------|--------|-------|
| **Bionic vs Proxy Mode** | Ambiguous distinction | Explicit: Bionic = independent thinking, Proxy = drafting voice |
| **Confidence Scoring** | Informal | Percentages require empirical data + falsification checks |
| **Dehumanizing Language** | Hard invariant | Relaxed for biological/predatory frames when contextually appropriate |

**Source**: External red-team audit (Session 560-571)

---

## v1.2.5 (04 January 2026)

**Stats Sync**: 277 protocols; Python badge fix (3.13)

---

## v1.2.4 (04 January 2026)

**README Restructure**: Collapsed technical sections into "Further Reading" dropdowns to improve readability for new visitors.

---

## v1.2.3 (03 January 2026)

**Stats Correction**: 269 protocols, 538 sessions, 117 scripts

---

## v1.2.2 (02 January 2026)

**Stats Sync**: 248 protocols, 560 sessions, 97 scripts; removed off-topic content from README.

---

## v1.2.1 (01 January 2026)

**README Overhaul**:

- Added "Process" section (The Schlep) with phase breakdown
- Added Security Model section with data residency options
- Rewrote narrative to emphasize co-development with AI

---

## v1.2.0 (01 January 2026)

**New Year Sync**: 246 protocols, 511 sessions

---

## v1.1.0 (December 2025)

**Year-End Sync**: 238 protocols, 489 sessions

---

## v1.0.0 (December 2025)

**Initial Public Release**:

- SDK architecture (`src/athena/`)
- Quickstart examples
- Core documentation
