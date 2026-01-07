# Athena Changelog

> **Last Updated**: 07 January 2026

This document provides detailed release notes. For the brief summary, see the README changelog.

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
