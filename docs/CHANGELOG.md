# Athena Changelog

> **Last Updated**: 26 March 2026

This document provides detailed release notes. For the brief summary, see the README changelog.

> **Note**: Versions v1.0–v1.6 predate the v8.x versioning scheme adopted in January 2026. The version jump reflects a complete architectural rewrite, not skipped releases.

---

## v9.6.1 (26 March 2026)

**The Ousen Protocol — Pre-Execution Battle Planning**

### Key Changes

- **`/battleplan` Workflow** (NEW): `examples/workflows/battleplan.md` — 7-phase pre-execution battle planning protocol for complex deliverables. Inspired by General Ou Sen's doctrine: "I only fight battles I can win." Introduces the **Double-Envelope Audit Architecture** — Red-Team #1 audits the *plan* (catches strategic failures before writing begins), Red-Team #2 audits the *output* (catches execution failures after writing). The pipeline: `Brief → Deep Research (scouts) → /battleplan → Red-Team #1 → Execute → Red-Team #2 → Humanize → Ship`.
- **Scout/General Sequencing**: Deep research agents (Gemini, ChatGPT, Perplexity) act as expendable scouts — gather intelligence in 5 minutes at near-zero cost. The premium agent (Athena) then designs the battle plan with full terrain knowledge. "Don't send the General to scout when you have scouts."
- **Examiner Anticipation Matrix**: Phase 3 war-games the evaluator's likely moves — what they're *really* looking for, where students typically fail, trap questions, unmarked minefields. The "opponent's game plan" is mapped before the first word is written.

### The 7 Phases

1. **Intelligence Briefing** — Digest deep research outputs, find consensus/contested positions, flag citation deserts
2. **Terrain Scan** — Read every source document, extract rubric/deadline/constraints
3. **Examiner's Game Plan** — War-game the evaluator's anticipated moves
4. **KSA Gap Map** — Post-research 🟢/🟡/🔴 gap assessment per section
5. **Battle Formation** — Military-style troop deployment (center/left/right wing with kill shots per section)
6. **Win Conditions & Risk Register** — Distinction vs Pass vs Fail markers + risk mitigations
7. **Commander's Intent** — One-line North Star directive that governs all execution decisions

### Design Decisions

- Deep research comes *before* the battle plan (not after) — scouts are cheap, the General's time is not. The 5-minute deep research cost is dominated by the value of a well-informed plan.
- The Double-Envelope architecture catches fundamentally different failure modes: strategic failures (wrong thesis, missing rubric criteria) are caught in Red-Team #1 before any writing begins, preventing costly rewrites. Execution failures (hallucinated citations, tone drift) are caught in Red-Team #2 post-writing, fixable with targeted edits.
- Battle Formation uses military terminology (center army, left/right wing, reserves, defensive positions) — this makes section-importance mapping visceral and immediately legible.

### Files Changed

- `examples/workflows/battleplan.md` — NEW
- `docs/CHANGELOG.md` — This entry
- `README.md` — Version badge (9.6.0 → 9.6.1), changelog entry
- `pyproject.toml` — Version bump (9.6.0 → 9.6.1)

---

## v9.6.0 (25 March 2026)

**The Outcome Economy — Labor Economics of Human Augmentation**

### Key Changes

- **Outcome Economy Concept Page** (NEW): `docs/concepts/Outcome_Economy.md` — The economic thesis for why AI-augmented operators earn more per hour while charging less per deliverable. Grounds the Bionic Unit philosophy in formal labor economics: utility maximisation (`U(C,L)` → `U(C,L,K)`), backward-bending labor supply curve, Ricardian comparative advantage within one person, and the Bionic Pricing Arbitrage (client pays 67% less, operator earns 233% more per hour).
- **Cross-References**: Updated Time Compression Thesis, Grace Protocol, KNOWLEDGE_GRAPH, and TAG_INDEX with Outcome Economy links. 7 new tags added (`#outcome-economy`, `#labor-economics`, `#backward-bending-supply`, `#comparative-advantage`, `#bionic-pricing`), 2 existing tags updated (`#flat-rate-ai`, `#human-augmentation`).
- **Concept Count**: 7 → 8 documented thesis pages.

### Design Decisions

- Titled "Outcome Economy" rather than "Labor Economics" because the labour-leisure model is a _mechanism_ — the concept page's thesis is about the _economic regime shift_ from output-based to outcome-based value.
- The "Third Good" extension (`U(C,L,K)`) is the novel contribution — standard labor economics models only have 2 goods. Adding K (capital/asset building) captures the asymmetry between augmented and unaugmented operators: freed hours enable upstream investment that shifts _future_ budget constraints.
- Backward-bending supply curve explanation uses the user's "enjoy life lor" phrasing (anonymised) as the intuition pump — makes formal economics accessible via lived experience.
- No separate case study — the bionic pricing arbitrage ($3K→$1K worked example) is embedded in the concept page itself because it's a _structural pattern_, not a single narrative.
- All examples fully anonymised: no client names, project codes, or assignment identifiers.

### Files Changed

- `docs/concepts/Outcome_Economy.md` — NEW
- `docs/KNOWLEDGE_GRAPH.md` — Count (7→8), new concept entry, new relationship entry
- `docs/TAG_INDEX.md` — 7 new tags, 2 updated tags, new concept entry
- `docs/concepts/Time_Compression_Thesis.md` — Cross-reference added
- `docs/concepts/Grace_Protocol.md` — Cross-reference added
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump (9.5.8 → 9.6.0)

---

## v9.5.9 (24 March 2026)

**Iteration Arbitrage Framework — Consulting Delivery Model**

### Key Changes

- **Iteration Arbitrage Concept Page** (NEW): `docs/concepts/Iteration_Arbitrage.md` — The structural argument for why flat-rate AI lifts the iteration ceiling on complex problem-solving. Traditional consultants stop iterating when budget runs out, not when they find the answer. Builds on Maximum Depth Doctrine (vertical) by extending it horizontally (unlimited convergence loops per problem).
- **Case Study #7** (NEW): The Consulting Convergence Problem — 8 convergence loops for multi-stakeholder consulting at $375/session vs McKinsey's 3-4 at $30K/loop. Introduces the Paper-Reality Gap (convergent vs divergent problems), loop count scaling formula, and per-session pricing thesis.
- **Compounding Principle**: Updated to reference CS#7 (consulting loops compound context across iterations).

### Design Decisions

- Convergent vs Divergent problem taxonomy: assignments have correct answers (1 loop), consulting has least-wrong answers (N loops). The iteration count is a problem-type property, not an efficiency metric.
- Pricing implication: per-session pricing structurally correct for divergent problems because it aligns price with the iteration count — the variable that actually drives cost.
- Framework extends CANONICAL §260 (private repo) into public documentation.

### Files Changed

- `docs/concepts/Iteration_Arbitrage.md` — NEW
- `docs/CASE_STUDIES.md` — Case Study #7 added, Compounding Principle updated
- `docs/CHANGELOG.md` — This entry
- `docs/TAG_INDEX.md` — New tags and concept entries

---

## v9.5.8 (23 March 2026)

**Red-Team GTO Audit — Workspace Hardening & Hygiene**

### Key Changes

- **`/fix` Workflow** (NEW): Analyzes test failures from `/test` output, classifies them (config/code/infra/flaky), proposes fixes, and re-runs tests. Unblocks the `/test` → `/fix` self-healing chain that was referenced but undefined.
- **Confidence Model Fix** (`Athena_Profile.md`): Resolved duplication between §2.1 (inline rubric) and §7 (canonical rubric). §2.1 now cross-references §7, establishing a single source of truth.
- **Protocol Naming Standardization**: 30 protocol files renamed from Title_Case/SCREAMING_CASE/PascalCase to kebab-case convention. TAG_INDEX and SKILL_INDEX references updated.
- **Deduplication**: Full MD5 scan across 393 protocols found 2 byte-identical duplicates — removed `329-consiglieri-protocol.md` (dupe of P197) and `protocol-webflow-bridge.md` (dupe of P066).
- **Pruning Checklist** (`/audit` workflow): New Phase 4.5 "Inventory Hygiene Check" for `--deep` audit mode. Checks deprecated protocols, stale indexes, context size, and activeContext line count.
- **KNOWLEDGE_GRAPH.md**: Updated stale counts (405→391 protocols, 63→60 workflows, 28→26 skills).

### Design Decisions

- Red-team (Claude Opus 4.6) flagged 3 factual inaccuracies in its own report — wiring ratio was 43% (not 9.9%), WORKFLOW_INDEX was 2 days stale (not 18), and ad-hoc pruning existed (not absent). Only 5 of 12 recommendations accepted — rejected protocol health dashboard, hard cap on protocols, and `/router` workflow as anti-patterns under the "better search > less inventory" principle.
- Protocol number collisions (50+ pairs with same NNN prefix in different domain dirs) confirmed as namespace-only — unique content, just shared numbers. Not worth renumbering since `smart_search.py` discovery is semantic, not numeric.
- Pruning checklist embedded in `/audit` rather than creating a separate `/prune` workflow — avoids the maintenance overhead of another workflow while surfacing hygiene at the right moment.

### Files Changed

- `examples/workflows/fix.md` — NEW
- `.framework/v8.2-stable/modules/Athena_Profile.md` — §2.1 cross-reference fix
- `AGENTS.md` — Version bump (v9.5.7 → v9.5.8), `/fix` workflow added
- `docs/CHANGELOG.md` — This entry

---

## v9.5.7 (21 March 2026)

**Data Compounding Thesis & GTO Metrics Sync**

### Key Changes

- **Data Compounding Thesis**: New wiki page ([The Compounding Effect](../Athena-Public.wiki/The-Compounding-Effect.md)) + README data quality thesis + CASE_STUDIES compounding section + ABOUT_ME advantage #5. Core argument: the moat isn't the code — it's your data. Anyone can fork Athena; nobody can fork your sessions.
- **GTO Metrics Sync**: Version badges, SDK reference, protocol counts, session counts filesystem-verified and synced across README, ARCHITECTURE, SPEC_SHEET, pyproject.toml.
- **Star History Chart Fix**: Replaced broken `<picture>` element with reliable HTML dual-mode rendering (dark/light theme support).
- **Case Studies**: New CS-004 (NTU SDR Analysis) and CS-005 (Min-Max Purchasing Framework) added to CASE_STUDIES.md.
- **Meta-Game Thesis**: New concept doc (`docs/concepts/Meta_Game_Thesis.md`) — generic LLMs optimise within the game; Athena asks whether you should be playing that game at all.
- **Cross-Model Research Arbitrage Protocol (P527)**: Run identical prompts through ≥3 models, intersection = consensus truth, union minus intersection = novel insights.
- **Problem Authentication Gate**: P504 Gate 0 expansion — authenticate the problem before solving it.
- **Security**: Deep PnC audit (16+ scans, 4 files fixed), CANONICAL.md removed from tracking (contained private financial data).

### Design Decisions

- Data Compounding Thesis positioned as the answer to "what's the moat?" — the most common question from GitHub visitors. Empirical data > synthetic data > no data. The coupling data (1,200+ sessions of decisions, outcomes, corrections) is unreplicable.
- Star History chart uses the `<picture>` HTML element with `<source>` media queries for robust dark/light mode rendering across GitHub's themes.

### Files Changed

- `Athena-Public.wiki/The-Compounding-Effect.md` — NEW (wiki page, linked from README)
- `README.md` — Data quality thesis, Star History fix, version/date/counts sync
- `docs/CASE_STUDIES.md` — Compounding section, CS-004, CS-005
- `docs/ABOUT_ME.md` — Advantage #5 (data compounding)
- `docs/concepts/Meta_Game_Thesis.md` — NEW
- `examples/protocols/research/527-cross-model-research-arbitrage.md` — NEW
- `docs/USE_CASES.md` — Problem Authentication Gate refinement
- `pyproject.toml` — Version bump (9.5.6 → 9.5.7)
- `docs/CHANGELOG.md` — This entry

---

## v9.5.6 (19 March 2026)

**Operator Optimization — The Phase 2 Thesis**

### Key Changes

- **CS-006** (NEW): [The Replacement Trap](../examples/case_studies/CS-006-the-replacement-trap.md) — 5 anonymized decision failures documenting the pattern where AI replaces human judgment instead of augmenting it. Root cause analysis ("Mode Confusion"), quantified impact (~$2,300 underpricing + 1 health risk + 1 positioning error), and the 3-Question Pre-Flight fix.
- **USER_DRIVEN_RSI.md**: New "Phase 2: Optimising the Operator" section. Documents the phase transition from AI system optimization to human operator optimization. Three axes: (1) supply richer training data, (2) constant calibration via outcome logging, (3) fine-tune personal thinking process via pre-flight checklist.
- **BEST_PRACTICES.md**: New §10 "Decision Sovereignty (The Pre-Flight Checklist)". Anti-pattern table, 3-question pre-flight, when-to-apply decision matrix. Quick Reference updated with new do/don't items.
- **README.md**: Phase 2 thesis referenced in the Human Augmentation section. Version, date, SDK version, and changelog updated.

### Design Decisions

- CS-006 is fully anonymized — no client, project, or domain identifiers. All references use generic framing ("technical report", "healthcare provider", "consulting engagement") to protect operational security.
- Phase 2 is positioned as an evolution of the Symbiotic RSI thesis, not a replacement. Phase 1 (building the AI) and Phase 2 (optimising the human) are complementary stages in the bilateral loop.
- Decision Sovereignty is placed as §10 in BEST_PRACTICES rather than as a standalone protocol — it's operational guidance for the user, not system behavior for the AI.

### Files Changed

- `examples/case_studies/CS-006-the-replacement-trap.md` — NEW
- `docs/USER_DRIVEN_RSI.md` — Phase 2 section added
- `docs/BEST_PRACTICES.md` — §10 Decision Sovereignty, Quick Reference updated, date synced
- `README.md` — Version badge, date, SDK version, Phase 2 reference, changelog entry
- `pyproject.toml` — Version bump (9.5.5 → 9.5.6)
- `docs/CHANGELOG.md` — This entry

---

## v9.5.5 (16 March 2026)

**Abundance Mindset Alignment & Workspace Hygiene**

### Key Changes

- **P529 Survival HUD Removed**: Deleted `examples/protocols/safety/529-survival-hud.md` — fear-based crisis output mode replaced by existing safety stack (Law #1 + Circuit Breaker + Threat Playbooks). Aligns workspace with thriving/abundance mindset over scarcity framing.
- **`/start` Workflow Fix** (`examples/workflows/start.md`): Removed P529 reference from the Survival routing chain. Chain now correctly terminates at P506 (GTO Execution).
- **Protocol Count**: 128 → 127 active (147 → 146 total including archived). Safety category: 7 → 6 protocols.

### Design Decisions

- P529 was never triggered in practice across 1,000+ sessions. Its function (crisis-mode output compression to ≤15 lines) is redundant with the existing Survival System routing chain (P509 → #14 → P519 → #15 → P521 → P520 → #8 → P506) which already handles crisis contexts with full analytical depth.
- The removal is philosophically aligned: Athena's safety architecture should protect through *better reasoning*, not through *output restriction*.

### Files Changed

- `examples/protocols/safety/529-survival-hud.md` — DELETED
- `examples/workflows/start.md` — P529 reference removed from routing chain
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump

---

## Protocol 525 v1.2 (14 March 2026)

**Red-Team Hardening — Prior Art & Limitations**

### Key Changes

- **Prior Art** (NEW §Prior Art in P525): Cynefin framework (Snowden, 1999) acknowledged as prior art. Delta table specifying what P525 adds beyond Cynefin: AI output posture specification, conviction-decisiveness split (P524), compound decomposition pipeline, band width / anchoring risk mapping.
- **README**: Added "Architecture, not oracle" clarification after the domain classification table — clarifies n=1 architecture-by-design posture and links to P525.
- **References**: Added Snowden (1999, 2007) to P525.

### Files Changed

- `examples/protocols/reasoning/525-cross-domain-weighting.md` — v1.1 → v1.2 (Prior Art section + References)
- `README.md` — n=1 architecture clarification

---

## Protocol 525 v1.1 (14 March 2026)

**Domain-Aware Output Calibration — Cross-Domain Weighting Upgrade**

### Key Changes

- **Output Calibration Table** (NEW §3.5): Maps what Athena *says* and what the human *does* per domain type. Deterministic → direct answer; Semi-deterministic → band with assumptions; Semi-stochastic → structural estimate with fragility warning + human handoff; Stochastic → honest "no estimate."
- **Band Width & Reliability** (NEW §3.6): Framework mapping band width, reliability, and anchoring risk per domain. Semi-stochastic estimates carry high anchoring risk — always packaged with basis, fragility warning, and handoff.
- **Type 5 Declaration**: Explicit framing that most real-world high-stakes problems are compound (mixed-domain) by default. The 4 domain types are atomic building blocks, not categories.
- **Worked Examples**: Added legal (corporate fraud plea bargain — 6 sub-problems across 4 domain types) and trading (EURUSD long — direction stochastic, SL/sizing deterministic). Original S24 Ultra example retained.
- **Anti-Patterns**: Added 2 new entries (anchoring risk, sub-problem blending).

### Files Changed

- `examples/protocols/reasoning/525-cross-domain-weighting.md` — v1.0 → v1.1
- `docs/CHANGELOG.md` — This entry

---

## v9.5.4 (14 March 2026)

**Architecture Integrity Audit — Protocol Index & Routing Sync**

### Key Changes

- **Protocol Index** (`examples/protocols/README.md`): Full rewrite. Corrected stale counts from 109→128 active protocols, 13→15 categories. Added missing Trading (2 protocols) and Content (1 protocol) categories. Updated Featured Protocols to reflect architecturally significant entries (P504, P507, P511, P526, P138).
- **Cluster Index** (`examples/templates/cluster_index_template.md`): Wired P138 (Third Choice Generation) into Problem-Solving Engine (#15) with new triggers ("false binary", "only two options", "dilemma"). Wired P526 (Business Viability Assessment) + P511 into Distribution Engine (#10) with new triggers ("business model", "four fits", "viability", "pro forma").
- **Integrity Fix**: Protocol counts now consistent between `protocols/README.md` (128 active + 18 archived = 146), top-level `README.md` (146+), and `CHANGELOG.md`.

### Design Decisions

- P138 placed in Cluster #15 (Problem-Solving) rather than #9 (Strategic Reasoning) — false binary dissolution is a *framing* operation (upstream) not an *analysis* operation (downstream). It fires *before* options are evaluated, not after.
- P526 placed in Cluster #10 (Distribution Engine) rather than standalone — business viability assessment is part of the GTM pipeline. You assess viability before you distribute.
- Decision category dropped from 28→19 active protocols because the original count included 9 archived files. Reasoning jumped from 3→13 reflecting 10 protocols added since the original index was written.

### Files Changed

- `examples/protocols/README.md` — Full rewrite (counts, categories, featured)
- `examples/templates/cluster_index_template.md` — P138/P526 wiring, date sync
- `docs/CHANGELOG.md` — This entry
- `README.md` — Version badge
- `pyproject.toml` — Version bump

---

## v9.5.3 (14 March 2026)

**Independent Cross-Model Audit — Strategy & Reasoning Protocols**

### Key Changes

- **Protocol 526** (NEW): Business Viability Assessment — The 3-Layer Stack (BMC → Four Fits → Pro Forma P&L). Mandatory pre-qualification gate for business models and client ventures. Validated across 4 empirical cases (FnB, tuition, web design, AI consulting).
- **Protocol 138** (NEW): Third Choice Generation (Kobayashi Maru). Meta-thinking protocol for dissolving false binaries. 5-step framework: name the binary → challenge the frame → generate third options → evaluate expanded set → identify systemic failure.
- **Cold Start Rule** (`BEST_PRACTICES.md`): New §9 — verify all code deliverables from a clean clone before submission. Catches hidden local state dependencies.
- **Protocol Count**: Bumped from 144+ to 146+.

### Design Decisions

- P526 is the _deep_ follow-up to P511 (Business Viability Trinity). P511 is the 3-question pre-filter ("is this worth investigating?"); P526 is the 3-layer assessment ("can this actually work?"). Complementary, not redundant.
- P138 placed in `reasoning/` not `strategy/` — false binary dissolution is a domain-general cognitive tool, not limited to business decisions.
- Cold Start Rule derived from A6 Q2b empirical failure — a delivered project that failed to boot on the client machine. Prevention time: 60 seconds vs 2-hour debug.

### Files Changed

- `examples/protocols/strategy/526-business-viability-assessment.md` — NEW
- `examples/protocols/reasoning/138-third-choice-generation.md` — NEW
- `docs/BEST_PRACTICES.md` — Added §9 (Cold Start Rule), date sync
- `docs/CHANGELOG.md` — This entry
- `README.md` — Version badge, protocol count, date, changelog summary
- `pyproject.toml` — Version bump

---

## v9.5.2 (13 March 2026)

**Ollama Integration, Symbiotic RSI, Metrics Sync**

### Key Changes

- **Ollama Embedding Provider** (`vectors.py`): Added provider pattern — `EMBEDDING_PROVIDER` env var selects between `gemini` (default, 3072 dims) and `ollama` (local, zero-cost, 768 dims). Configurable via `OLLAMA_BASE_URL` and `OLLAMA_EMBED_MODEL`. Fully backward compatible. Closes #29.
- **Symbiotic RSI Codification** (`USER_DRIVEN_RSI.md`, `ARCHITECTURE.md`): Renamed User-Driven RSI → Symbiotic RSI. Added thesis declaration, thermodynamic framing (open vs closed systems), moat analysis (coupling data as defensibility), and Unilateral vs Symbiotic comparison table.
- **Dual Pressure Model** (`BEST_PRACTICES.md`): New §0 best practice — accelerate agent mastery by running open-source projects (adversarial hardening) and paid projects (velocity validation) simultaneously.
- **Metrics Sync**: Full refresh of stale counts across `CAPABILITIES.md` (5 metrics), `BENCHMARKS.md` (case studies 42→417+), `TOP_10_PROTOCOLS.md` (P330 canonical name).
- **VECTORRAG.md Full Refresh**: Corrected embedding model name (`text-embedding-004` → `gemini-embedding-001`), updated all domain counts (sessions ~468→1,100+, protocols ~226→144+, etc.), added Ollama provider documentation.
- **Protocol Count**: Bumped from 141+ to 144+.

### Files Changed

- `src/athena/memory/vectors.py` — Ollama provider + registry pattern
- `docs/USER_DRIVEN_RSI.md` — Symbiotic RSI thesis
- `docs/ARCHITECTURE.md` — Symbiotic RSI top-level section
- `docs/BEST_PRACTICES.md` — Dual Pressure Model
- `docs/CAPABILITIES.md` — 5 metric updates
- `docs/BENCHMARKS.md` — Case study count
- `docs/TOP_10_PROTOCOLS.md` — P330 canonical name
- `docs/VECTORRAG.md` — Full refresh (model, counts, Ollama docs)
- `docs/CHANGELOG.md` — This entry
- `README.md` — Version badge, date
- `AGENTS.md` — Version sync
- `pyproject.toml` — Version bump

---

## v9.5.1 (11 March 2026)

**Conviction-Decisiveness Split & Version Sync**

### Key Changes

- **Protocol 524** (NEW): Conviction-Decisiveness Split. Decouples epistemic conviction from operational decisiveness in semi-stochastic domains. Delivers precise setups while acknowledging outcome uncertainty.
- **`README.md`**: Embedded the conviction-decisiveness insight into the domain uncertainty table. Added compute recommendation for `/ultrastart` (suggesting MAX subscription plans for unbounded deep reasoning).
- **Protocol Count**: Bumped from 140+ to 141+.
- **Version Bump**: Badges, `pyproject.toml`, and this changelog updated to `v9.5.1`.

---

## v9.5.0 (11 March 2026)

**Adaptive Graph of Thoughts — Protocol 75 v5.0**

### Key Changes

- **Protocol 75 v5.0** (NEW): AGoT-Enhanced Parallel Reasoning. Upgrades static 4-track parallel reasoning to dynamic graph-based topology with recursive decomposition, confidence-based pruning, and adaptive convergence gates. Based on Pandey et al. (2025), arXiv:2502.05078.
- **`agot_orchestrator.py`** (NEW): Core AGoT implementation (~530 lines). `AGoTController` manages layered DAG construction, recursive sub-graph spawning, and 4-track persona integration. Three preset tiers: `lite` (Λ 21-40), `full` (Λ 41-60), `tracks` (Λ > 60).
- **Adaptive Convergence Gate**: Replaces fixed ≥85/100 threshold with agreement-adaptive scoring. High consensus → threshold 70. Low consensus → threshold 90 + reconciliation round.
- **`/ultrastart` Integration**: AGoT routing table added. Λ-based automatic mode selection during deep boot sessions.
- **Research Archive**: AGoT research findings archived to `docs/research/agot_research.md` with 7 key paper citations.

### Design Decisions

- AGoT is strictly scoped to `/ultrastart` sessions only — the latency and token cost are acceptable in System-2 deep reasoning mode but inappropriate for lightweight sessions.
- v4.0 (`parallel_orchestrator.py`) remains available as a fallback. v5.0 does not modify or delete it. The two coexist.
- Controller logic is deterministic Python, not LLM. The LLM does strategy/decomposition/resolution/synthesis; Python manages graph state, concurrency, and termination.
- Heritage-based node addressing (`depth-layer-position`) ensures unique identification across nested graphs.
- Inter-track agreement measurement drives adaptive convergence threshold — tracks that agree need less scrutiny; disagreeing tracks demand stronger evidence.

### Files Changed

- `examples/protocols/decision/75-synthetic-parallel-reasoning-v5.md` — NEW
- `scripts/core/reasoning/agot_orchestrator.py` — NEW
- `docs/research/agot_research.md` — NEW
- `docs/CHANGELOG.md` — This entry

---

## v9.4.9 (10 March 2026)

**Deep Session Close — `/ultraend` Workflow**

### Key Changes

- **`/ultraend` Workflow** (NEW): System-2 deep close counterpart to `/ultrastart`. 6-phase sequence: Phase 0 (standard `/end` — safety net), Phase 1 (Cross-Session Pattern Scan — recurring themes, orphaned pendings, decision reversals across last 5 sessions), Phase 2 (CANONICAL Deep Reconciliation — mandatory framework bundling check), Phase 3 (Reflexion Archive — what worked/didn't/counterfactual), Phase 4 (Strategic Portfolio Review — priority alignment, stale project detection, next session seeding), Phase 5 (Shutdown Orchestrator).
- **Session Architecture Symmetry**: The boot/shutdown pair is now complete: `/start` ↔ `/end` (lightweight) and `/ultrastart` ↔ `/ultraend` (System-2 deep). Auto-triggers when session opened with `/ultrastart`, 5+ decisions made, or new frameworks discovered.

### Design Decisions

- `/ultraend` is additive over `/end`, not a replacement. Phase 0 executes the full `/end` sequence first — if synthesis fails, the session is still cleanly closed.
- The "Framework Bundling Check" (Phase 2, Step 3) catches when 3+ related insights should be named and filed as a coherent framework rather than individual data points.
- "Next Session Seeding" (Phase 4, Step 4) writes a `@seeded` hint to the checkpoint, giving `/start` or `/ultrastart` a head start on context loading.

### Files Changed

- `examples/workflows/ultraend.md` — NEW
- `README.md` — Version, date, changelog
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump

---

## v9.4.8 (10 March 2026)

**Boot/Shutdown Architecture Redesign**

### Key Changes

- **`/ultrastart` Workflow** (NEW): System-2 deep boot for cognitively intensive work (`/ultrathink`, complex multi-domain analysis). 4-phase sequence with ≤20K token budget: Phase 1 (Absolute Law — full `Core_Identity.md`), Phase 2 (Materialized Truth — `CANONICAL.md` + `PROJECTS.md`), Phase 3 (Recent State — last `activeContext.md` checkpoint), Phase 4 (Semantic Bridge — `smart_search.py` top 5-7 results for the user's stated objective). Includes complexity gate, optional objective string, and graceful degradation.
- **`/end` GTO v3 Rewrite**: Fixed the Source Reality Gap — `end.md` previously claimed "There is no separate session log file" but `shutdown.py` compiles from `session_logs/`. Established dual-write architecture: session logs (`session_logs/[DATE]-session-[N].md`) for `shutdown.py` compilation + `activeContext.md` checkpoint block for `/start` fast boot. Added `[S]`/`[U]` learning markers for `shutdown.py`'s `extract_learnings()`. Tightened micro-close path.
- **`quicksave.py` Triple-Lock Fix**: Changed governance check from `AND` (require both Semantic Search + Web Search) to `OR` (require either). The previous `AND` gate was a textbook Robustness Theater violation (Protocol 510) — forcing unnecessary web searches for local problems (CSS bugs, refactors) added ~10-15s latency per turn for zero retrieval value.

### Design Decisions

- `/ultrastart` Phase 3 is deliberately thin (~1K tokens) — recency ≠ relevance. Phase 4 (Semantic Bridge) gets the largest flexible budget (~5.5K tokens) because it's the only task-specific phase.
- `/end` dual-write is complementary, not competing: session logs feed the compilation pipeline; activeContext feeds the boot pipeline. Different consumers, different files.
- Triple-Lock `OR` condition means: local problem → Semantic Search only. External facts → Web Search only. ULTRA queries → both. Matches the blast radius heuristic.

### Files Changed

- `examples/workflows/ultrastart.md` — NEW
- `examples/workflows/end.md` — Rewritten (GTO v3)
- `scripts/quicksave.py` — Triple-Lock AND→OR
- `scripts/core/quicksave.py` — Triple-Lock AND→OR
- `examples/scripts/quicksave.py` — Triple-Lock AND→OR
- `README.md` — Version, date, Deep Boot mode, changelog
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump

---

## v9.4.7 (09 March 2026)

**Safety Documentation & Governance Hardening**

### Key Changes

- **`SAFETY.md`** (NEW): Clinical disclaimer, crisis contacts (US/UK/International), clear boundaries on limitations — addresses external audit feedback on therapeutic/financial claims.
- **`README.md`**: Safety disclaimer added to Use Cases section (inline with "$200/hr therapist" claim). Safety link added to header nav and footer. Version bumped. SDK version synced.
- **Governance Tests** (private): 24 MC/DC tests added for Triple-Lock and DoomLoopDetector. Test suite improved from 51 → 76 tests.
- **Compaction Pipeline** (private): Pre-compaction state flush (OpenClaw pattern), head/tail preservation constants in `compact_context.py` v3.0.
- **Git Hygiene** (private): Reflog expired, `git fsck` clean.

### Design Decisions

- Clinical disclaimer placed directly inline with the asymmetry callout (the most likely place a vulnerable user reads). Not hidden in a footer — must scan past it to reach use cases.
- Crisis contacts are international (US/UK/112), not region-specific, since the public repo serves a global audience.

### Files Changed

- `SAFETY.md` — NEW
- `README.md` — Safety disclaimer, version, footer
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump

---

## v9.4.6 (09 March 2026)

**Project Switchboard — Multi-Project GSD Orchestration**

### Key Changes

- **`/project` Workflow** (NEW): Multi-project switchboard with 5 commands (view, add, switch, close, triage). Internal/External zone split matches the mental model of personal vs. client work. Dependency tracking (`Depends On` column) surfaces cross-project blockers. Cross-zone capacity check flags when degraded Internal projects (health, energy) affect External capacity.
- **`PROJECTS.md` Template**: Structured markdown dashboard with visual phase bars (░▓), urgency/EV ranking, and GTD-style next actions. GSD mechanics applied at the portfolio level.
- **README.md**: Upgraded "Work & Projects" use case to feature multi-project orchestration as a core capability. Version badge, SDK version sync.
- **`/start` Integration**: `PROJECTS.md` added to Phase 2 adaptive loading table — auto-loads when user asks about projects or "what should I work on."
- **`/end` Integration**: Step 5 added — prompts for project state updates before shutdown (advance phases, update next actions, adjust urgency, archive completed projects).

### Design Decisions

- `PROJECTS.md` is **user state** (lives in `.context/`), not agent infrastructure (`.agent/`). The workflow template is agent behavior (`.agent/workflows/`).
- Project IDs use `I/E` prefix (`I1`, `E3`) for unambiguous Internal/External identification during `/project switch`.
- Token efficiency: Loading `PROJECTS.md` costs ~500 tokens vs ~5K tokens for conversational context recovery. Over 44 sessions, this saves ~200K tokens.

### Files Changed

- `examples/workflows/project.md` — NEW
- `README.md` — Version, use case, changelog, SDK version
- `docs/CHANGELOG.md` — This entry
- `pyproject.toml` — Version bump

---

## v9.4.5 (09 March 2026)

**Two-Mode Session Architecture & Crisis Architecture Upgrade**

### Session Architecture

- **Two Session Modes**: Introduced Lightweight mode (skip `/start`, just chat, `/end` when done) and Full Boot mode (`/start` → Work → `/end`). Documented in `BEST_PRACTICES.md` and `MULTI_MODEL_STRATEGY.md`.
- **The Framework Tax**: New concept documenting why Athena's ~10K token system prompt is valuable overhead for complex tasks but unnecessary waste for simple ones. Provides clear decision heuristic for mode selection.
- **Orchestrator-Executor Pipeline**: Formal documentation of the Gemini (scoping) → Opus (execution) → Gemini (QA) workflow that cuts frontier token usage by 50-70%.
- **Updated Anti-Patterns**: Added 3 new anti-patterns (brain dumps on Frontier, `/start` for quick questions, raw client briefs to Frontier).
- **Updated Quick Reference**: Quick reference card now includes Lightweight mode and scoping/planning tasks.

### Crisis Architecture

- **Protocol 509 (Emotional Triage)**: First-contact protocol for crisis-flagged queries. Classifies emotional state before routing to cognitive systems.
- **Protocol 519 (Terminal Goal Elicitation)**: Extracts the user's actual desired end-state during crisis, preventing premature solution-jumping.
- **Protocol 520 (Blast Radius Calculator)**: Quantifies potential damage across dimensions (financial, relational, health, career, legal) before recommending action.
- **Protocol 521 (Crisis Domain Constraints)**: Hard-coded domain-specific safety rules for crisis contexts (e.g., never recommend leverage in financial panic).
- **Updated Survival System**: Cluster chain updated from `#14 → #3 → #15 → #8 → P506` to `P509 → #14 → P519 → #15 → P521 → P520 → #8 → P506`.

### Files Changed

- `docs/BEST_PRACTICES.md` — Rewrote §2 Session Discipline
- `docs/MULTI_MODEL_STRATEGY.md` — Added Session Modes, Framework Tax, Orchestrator-Executor Pipeline sections
- `docs/ARCHITECTURE.md` — Updated Survival system cluster chain, version history
- `docs/CHANGELOG.md` — This entry
- `README.md` — Version badge, date, How It Works diagram, changelog
- `pyproject.toml` — Version bump

---

## v9.4.3 (07 March 2026)

**Maintenance Release**: Version sync, file count corrections, date alignment.

### Key Changes

- **`AGENTS.md`**: Version synced from v9.4.1 → v9.4.3. Date updated.
- **`README.md`**: Protocol count corrected from "135+" → "138" (actual audited count). Script count corrected from "530+" → "540+" (actual: 539). Version badge, SDK version, and repo structure counts updated.
- **`pyproject.toml`**: Version bumped to 9.4.3.
- **Date Sync**: All core files updated to 07 March 2026.

---

## v9.4.2 (05 March 2026)

**Cognitive Architecture v2.1**: Introduced the first feedback loop (homeostatic pressure), competitive multi-system routing (LIDA Broadcast), failure memory (reflexion journaling), and agent-controlled memory management (memory paging).

### Key Changes

- **Protocol 517 (Homeostatic Pressure)**: Synthetic hormone system — when context saturation exceeds 80%, a scalar modifier forces SNIPER mode and suppresses expensive cognitive systems. Caps co-activation chains at depth 4. Triggers circuit breaker (P514) after ≥2 consecutive tool failures.
- **Protocol 515 (Reflexion Journaling)**: Failure memory stored via `[REFLEXION]` tags in quicksave. Captures what failed, why, and the corrective lesson. Retrievable via Exocortex to prevent recurring mistakes — the architecture's immune system.
- **Protocol 516 (Memory Paging)**: Agent-controlled page-in/page-out/pin/rewrite operations on working memory. Adapted from MemGPT to the prompt layer — enables active memory management during domain transitions.
- **LIDA Broadcast Routing**: When a query triggers ≥2 Cognitive Systems at comparable relevance, each System generates a 1-sentence framing proposal. Winner is broadcast to all Systems, preventing siloed routing on cross-domain queries.
- **Deterministic Exit Verification**: Trading clusters #3 (Risk Gate) and #4 (Execution) now require arithmetic proof — show the math, don't assert correctness.
- **Ebbinghaus Decay**: Maintenance cluster applies access-weighted decay to retrieval scores. Memories not accessed in >30 days receive a decay penalty; frequently co-activated procedural patterns receive permanence multipliers.
- **Context Clearing (Factory Pipeline)**: `spec-driven-dev` skill now treats the spec artifact as single source of truth after drafting — planning-phase context is discarded to prevent contamination during execution.

### Verification

| Metric | Result |
|--------|--------|
| New Protocols | 3 (P515, P516, P517) ✅ |
| Architecture Protocols Total | 20 ✅ |
| CLUSTER_INDEX version | v2.1 ✅ |
| Boot sequence (homeostatic signals) | Wired ✅ |
| Reflexion format in quicksave | Wired ✅ |

---

## v9.4.1 (05 March 2026)

**Daemon Cleanup & PnC Audit**: Removed deprecated BackgroundIndexer/LightRAG pipeline from `athenad.py`, sanitized leaked private paths, and synchronized version drift across all docs.

### Key Changes

- **`athenad.py` Cleanup**: Removed dead `BackgroundIndexer` class (60 lines), pruned unused imports (`hashlib`, `threading`, `queue`, `subprocess`). The LightRAG vectorization pipeline has been deprecated — the daemon now focuses solely on metadata indexing.
- **PnC Sanitization**: Removed leaked private path `/Winston/` from `EXCLUDED_PATTERNS`. Removed circular `Athena-Public/` self-reference from `WATCH_DIRS`.
- **`AGENTS.md` Sanitization**: Replaced leaked private skills (`moltbook`, `fantasy-framework-detection`, `moltbook-registry`) with canonical public skills (`spec-driven-dev`, `deep-research-loop`, `red-team-review`, `context-compactor`). Updated version from `v8.2-stable` → `v9.4.1`.
- **`ARCHITECTURE.md`**: Updated Daemon section mermaid diagram and description table to reflect BackgroundIndexer removal. Added v9.4.1 to version history.
- **Version Sync**: `pyproject.toml` bumped to `9.4.1`.

### Verification

| Metric | Result |
|--------|--------|
| `pyproject.toml` | v9.4.1 ✅ |
| `athenad.py` syntax | Valid ✅ |
| PnC patterns removed | 2 ✅ |
| Stale skills replaced | 3 → 4 ✅ |

---

## v9.4.0 (04 March 2026)

**Biological Stack Architecture**: Upgraded routing layer from 3 components to a full biological architecture: 8 Cognitive Systems (Organ System), 15 Cognitive Clusters (Organs), and 5 new protocols (P504-P508).

### Key Changes

- **Cognitive Systems Layer (`P507`)**: Added a macro-routing layer above clusters. 8 systems map to human need archetypes: Survival, Life Decision, Trading, Social, Execution, Growth, Learning, and Maintenance.
- **Intent Classifier (`P508`)**: Replaced flat keyword matching with an 8-question top-down diagnostic tree that routes queries to the correct Cognitive System.
- **`CLUSTER_INDEX.md`**: Updated from 3 starter clusters to the full 15-cluster production map. Linked all clusters to their parent Cognitive Systems.
- **Problem Diagnostics (`P504`)**: New 5-gate problem framing framework to prevent solving the wrong problem.
- **`ensure_env.sh` Fix**: Script now falls back to system Python if no `.venv` is found, reducing onboarding friction for users avoiding virtual environments.

### Verification

| Metric | Result |
|--------|--------|
| Cognitive Systems | 8 |
| Cognitive Clusters | 15 |
| New Protocols | 5 |
| `pyproject.toml` | v9.4.0 |

---

## v9.3.1 (03 March 2026)

**Cross-Model Audit Fixes**: Resolved 4 missing GitHub releases (v9.2.7–v9.3.0), corrected stale file count claims, relocated Windows compatibility section, synced dates.

### Key Changes

- **File Count Correction** (`README.md`): Updated "370+ Markdown" → "350+" (actual: 354) and "230+ Python scripts" → "600+" (actual: 651). Counts drifted after v9.2.9 dead-skill pruning.
- **Windows Section Relocation** (`README.md`): Moved dangling `## Windows Compatibility` from below the footer into a collapsible `<details>` block under Quickstart.
- **GitHub Release Sync**: Created v9.3.1 release covering v9.2.7–v9.3.0 changelog summaries.
- **Date Sync**: Updated README and CHANGELOG dates to 03 March 2026.

---

## v9.3.0 (02 March 2026)

**Onboarding Friction Audit**: Restructured dependencies, added virtual environment instructions, and fixed 6 onboarding blockers for new users.

### Key Changes

- **Dependency Restructuring** (`pyproject.toml`): Moved `torch`, `sentence-transformers`, `flashrank`, `dspy-ai`, `anthropic`, `supabase`, `google-generativeai` from core dependencies to optional groups (`[search]`, `[cloud]`, `[full]`). Default `pip install -e .` now completes in ~30s without downloading 2GB of PyTorch.
- **Virtual Environment Instructions** (`README.md`, `GETTING_STARTED.md`, `FAQ.md`): Added explicit `python3 -m venv .venv` step to Quickstart. Prevents PEP 668 `externally-managed-environment` errors on macOS Homebrew and Ubuntu 23.04+.
- **Two-Tier Install Path** (`README.md`): Lightweight install (default) vs `pip install -e ".[full]"` (vector search + reranking).
- **PEP 668 Troubleshooting** (`FAQ.md`): New troubleshooting entry for the most common install blocker.
- **Stale Path Fix** (`examples/workflows/start.md`): Replaced hardcoded `file:///Users/[AUTHOR]/...` absolute paths with relative paths.
- **URL Fix** (`init.py`): Fixed `[AUTHOR]87` placeholder in init output URL.
- **`requirements-lite.txt`** (NEW): Minimal dependency file for users who want the core framework without ML deps.

### Verification

| Metric | Result |
|--------|--------|
| Core install deps | 5 (was 11) ✅ |
| Install time (default) | ~30s (was 5-10 min) ✅ |
| PEP 668 addressed | 3 docs ✅ |
| Stale paths fixed | 3 ✅ |

---

## v9.2.9 (02 March 2026)

**Ultrathink v4.1 HITL Bypass + Micro-Pruning**: Added Human-in-the-Loop manual execution path to `/ultrathink`, pruned 10% dead skills for 100% cognitive cluster coverage, and fixed all broken references.

### Key Changes

- **Ultrathink v4.1**: Added Option B (HITL Manual Sandbox) — users can execute the 4 parallel reasoning tracks directly in the Gemini UI at zero API cost, then paste outputs back.
- **Micro-Pruning**: Removed `ui-ux-pro-max/` workflow (skill deleted from private repo). Fixed broken `file://` path in `refactor-code.md`.
- **`generate_skill_index.py`**: Removed dead `sickn33_collection` vendor block (referencing deleted submodule).
- **Cognitive Cluster Coverage**: Updated from 19/21 (90%) to 19/19 (100%) — all orphan skills eliminated.
- **Orchestrator v4.1**: Top-level imports, modern type hints (`dict`/`list`/`tuple`), rate-limit retry with 30s backoff, async deadlock fix.

### Verification

| Metric | Result |
|--------|--------|
| Broken references fixed | 4 ✅ |
| Security scans passed | 3/3 ✅ |
| Cluster coverage | 100% ✅ |
| Lines removed (net) | -4,192 ✅ |

---

## v9.2.8 (27 February 2026)

**Skill Template Expansion**: Added 5 starter skill templates across 4 categories for new Antigravity users. Skills are copy-paste ready — `cp -r examples/skills/<skill> .agent/skills/`.

### New Skills

| Path | Description |
|------|-------------|
| `examples/skills/coding/spec-driven-dev/` | Build a design spec before writing code |
| `examples/skills/research/deep-research-loop/` | Structured multi-source research workflow |
| `examples/skills/quality/red-team-review/` | Adversarial QA review for any artifact |
| `examples/skills/decision/mcda-solver/` | Multi-criteria decision matrix calculator |
| `examples/skills/workflow/context-compactor/` | Compress context to stay within token limits |

### Other Changes

- **`examples/skills/README.md`**: Rewritten with full directory tree, AG Quick Start instructions, and skill creation guide.

---

## v9.2.7 (26 February 2026)

**Risk-Proportional Triple-Lock + Tier 0 Context Summaries**: Engineered the min-latency × max-effectiveness optimization. The Triple-Lock is no longer a flat tax on every query — it's now risk-proportional with three tiers. Boot sequence gains zero-cost context pre-computation.

### Key Changes

- **Risk-Proportional Triple-Lock** (`governance.py`): Added `RiskLevel` enum (SNIPER / STANDARD / ULTRA). SNIPER queries (Λ < 10) bypass mandatory search — direct answer. STANDARD/ULTRA enforce full Triple-Lock. Default is STANDARD (robustness bias: `cost(false_negative) >> cost(false_positive)`). Risk level auto-resets after each verification.
- **Tier 0 Context Summaries** (`context_summaries.py`, NEW): Pre-computes 500-char compressed summaries of all 6 Memory Bank files at boot. Uses hash-based delta detection — only regenerates when source changes. Cached to `.agent/state/context_cache/`. Zero API cost.
- **Boot Orchestrator** (`orchestrator.py`): Context summary generation integrated as parallel worker #7 in the ThreadPoolExecutor. Zero sequential boot latency added.
- **REFERENCES.md**: Added 3 new academic citations (Shannon, Satisficing, Antifragility).
- **README**: Updated tech stack routing description to "Risk-Proportional Triple-Lock".

### Design Principles (Three Laws)

1. **Measure latency over the full cycle, not per-response.** Rework is the real latency tax.
2. **Phase-separate classification from execution.** Fast routing, robust processing. Never blend.
3. **When the classifier is uncertain, always round toward robustness.** The cost asymmetry makes this the only rational default.

### Verification

| Metric | Result |
|--------|--------|
| Governance SNIPER bypass | Verified ✅ |
| SNIPER auto-reset to STANDARD | Verified ✅ |
| STANDARD/ULTRA enforcement | Verified ✅ |
| Context summaries (6/6 files) | Pre-computed ✅ |
| Cache retrieval | Functional ✅ |
| All new code | Lint-clean ✅ |

---

## v9.2.6 (25 February 2026)

**Kilo Code + Roo Code IDE Integration**: Expanded agent compatibility to include Kilo Code and Roo Code. Fixed Windows encoding issue.

### Key Changes

- **IDE Support**: Added `athena init --ide kilocode` and `athena init --ide roocode` commands.
- **`COMPATIBLE_IDES.md`**: New documentation page listing all supported IDEs with setup instructions.
- **Windows Encoding Fix**: Resolved UTF-8 encoding issue on Windows platforms.
- **Issue #19**: Closed (IDE compatibility question).

---

## v9.2.5 (24 February 2026)

**Life Integration Protocol Stack + Formal Proof Standard**: Extended the reasoning pipeline from domain-specific rigor to domain-general life integration. New protocols for cross-domain constraint propagation, personalized learning, and emotional auditing.

### Key Changes

- **Protocol 381 (Formal Proof Standard)**: New — 6 rules for mathematical proofs and mechanism design (Derive Never Assert, Steelman Alternatives, Numerical Examples, Scope Boundaries, Adversarial Robustness, Dynamic Extensions).
- **Protocol 382 (Cross-Domain Constraint Propagation)**: New — prevents domain-siloed advice by auto-surfacing time/energy/money conflicts across life domains.
- **Protocol 383 (Personalized Learning Acquisition)**: New — 90-day outcome mapping, spaced repetition scaffolding, plateau detection.
- **Protocol 000 Extended (8-Step Audit Loop)**: Added Step 0.3 (Emotional Audit), Step 0.5 (Assumption Register), Step 1.5 (Stakeholder Map), Step 3.7 (Sensitivity Sweep), and "Depth over Checkbox" quality rule.
- **Core Identity §0.4 Expanded**: Added Post-Generation Self-Audit (9-item checklist, Λ > 60) and Life-Domain Protocol Trigger Map (10 autonomic triggers).
- **`/review` Workflow**: New weekly integration review — cross-domain health check, constraint conflict detection, decision triage.

### Verification

| Metric | Result |
| --- | --- |
| Protocol 000 steps | 4 → 8 ✅ |
| New protocols created | 3 (381, 382, 383) ✅ |
| Trigger map coverage | 10 life-domain rules ✅ |
| Benchmark proof (Alderia v2.1) | 87/100 (Red-Team verified) ✅ |

---

## v9.2.3 (21 February 2026)

**Multi-Agent Safety Hardening + Issue Deflection**: Integrated architectural patterns from Claude Code and OpenClaw audits. Added self-service support gates.

### Key Changes

- **Protocol 413 v1.1**: Added Unrecognized File Handling, Lint/Format Auto-Resolution, and Focus Discipline sections (sourced from OpenClaw).
- **AGENTS.md**: Added Multi-Agent Safety section to both root and Athena-Public. Updated pattern source attribution.
- **CLAUDE.md Symlinks**: Created `CLAUDE.md -> AGENTS.md` symlinks for cross-IDE agent compatibility.
- **SUPPORT.md**: New self-service support file — "Ask Athena First" philosophy.
- **Issue Templates**: All 3 templates (bug, question, feature) updated with Athena-first gates. Feature requests now nudge toward PRs.
- **CONTRIBUTING.md**: Added "Before You Open an Issue" section, elevated PR submission to #1 contribution method.
- **SECURITY.md**: Fixed stale version reference (v1.5.x → v9.x).

### Verification

| Metric | Result |
|--------|--------|
| Protocol 413 version | 1.1 ✅ |
| CLAUDE.md symlinks | Created (root + Athena-Public) ✅ |
| Issue templates | 3/3 updated ✅ |

---

## v9.2.2 (21 February 2026)

**S-Tier README Refactor + Docs Restructure**: Rewrote README from 671→224 lines. Created 4 new documentation pages.

### Key Changes

- **README**: Complete rewrite — removed verbose sections, added mermaid flow diagram, Linux analogy table, collapsible use cases.
- **New Docs**: `YOUR_FIRST_SESSION.md`, `TIPS.md`, `IMPORTING.md`, `CLI.md` — content moved from README to dedicated pages.
- **Version Badge**: Bumped to v9.2.2.

---

## v9.2.1 (20 February 2026)

**Deep Audit & PnC Sanitization**: Sanitized 17 patterns across 13 files. Ensured no private-and-confidential data in public repo.

### Key Changes

- **PnC Audit**: Scanned all public files for leaked personal data, credentials, and private references. 17 patterns sanitized across 13 files.
- **Collapsible Use Cases**: Converted 6 detailed use case descriptions into dropdown menus for cleaner README.
- **Reddit Views**: Updated badge to 1M+ (aggregated across all threads).

---

## v9.2.0 (17 February 2026)

**Sovereignty Convergence**: Root↔Public unification via cherry-pick. Security hardening, SDK maturation, and full surface sync.

### Key Changes

- **CVE-2025-69872 Patch**: DSPy DiskCache vulnerability mitigated at SDK level.
- **Semantic Cache**: LRU with disk persistence + cosine similarity matching for repeat queries.
- **FlashRank Reranking**: Local cross-encoder for search quality (no external API calls).
- **8 New SDK Modules**: `security`, `diagnostic_relay`, `shutdown`, `cli/`, `heartbeat`, `agentic_search`, `schema.sql`.
- **5 CodeQL Fixes**: URL sanitization (`archive.py`), clear-text log redaction (`daily_briefing.py`, `self_optimize.py`, `pattern_recognition.py`), file permissions.
- **Wiki Sync**: All 6 wiki pages updated to v9.2.0.
- **Profile/Website Sync**: GitHub profile README, `about.astro`, `athena.astro`, `athena_kb.json` updated.

### Verification

| Metric | Result |
|--------|--------|
| pyproject.toml version | 9.2.0 ✅ |
| CodeQL alerts | 5 fixed ✅ |
| Test suite | 17/17 pass ✅ |

---

## v9.1.0 (17 February 2026)

**Deep Audit & Sync**: Fixed 15 issues including dead links, version drift, dependency sync, AGENTS.md path errors, and workflow count corrections. Cleaned tracked artifacts.

### Key Changes

- **15 Issues Fixed**: Dead links, version drift, dependency sync, workflow counts.
- **AGENTS.md**: Fixed path errors and stale references.
- **Tracked Artifacts**: Cleaned stale build outputs.

---

## v9.0.0 (16 February 2026)

**First-Principles Workspace Refactor**: Complete structural audit and cleanup of the entire workspace. Zero regressions.

### Key Changes

- **Root Cleanup**: Moved 10 loose files (trading sims, drafts, audit docs) to proper `.context/` subdirectories. Deleted 2 root-level duplicates (`safe_boot.sh`, `DEAD_MAN_SWITCH.md`). Root directory reduced from 28 files → 14.
- **Build Artifacts**: Deleted `.agent/athena_sdk.egg-info/`, cleaned `.agent/temp/` and `.agent/temp_backup/`, removed stale `Athena-Public` runtime files (`athenad.log`, `.athenad.pid`).
- **Session Log Hygiene**: Archived 114 stub session logs (<500 bytes) to `session_logs/archive/stubs/`. Deleted 3 duplicate `2.md` files and 1 `.bak`. Fixed extensionless `2026-01-09-session-04`.
- **Dead Weight**: Archived `.framework/v7.0` → `.framework/archive/`. Archived orphan root `skills/` directory. Archived `winstonkoh87_backup/` and `Athena-Public-swarms/` → `.context/archive/`. Removed empty `.context/logs/`.
- **`.gitignore` Hardened**: Added `athenad.log`, `.athenad.pid`, `*.egg-info/` to prevent runtime artifacts in git.

### Verification

| Metric | Result |
|--------|--------|
| Test Suite | 17/17 passed ✅ |
| Boot Sequence | Clean exit ✅ |
| Git Status | 166 tracked changes (all expected) ✅ |

---

## v8.3.1 (11 February 2026)

**Viral Validation Release**: 360K+ Reddit views, 867+ upvotes, 2,900+ shares. #4 r/ChatGPT, #1 r/GeminiAI.

### Key Changes

- **Reddit Viral**: 360K+ views across r/ChatGPT (#4) and r/GeminiAI (#1), 867+ upvotes, 2,900+ shares
- **GitHub Stars**: 114 stars (from 13 pre-launch)
- **Model Upgrade**: Claude Opus 4.5 → 4.6 across all docs
- **Three-Phase Token Budget**: Formalized robustness vs. efficiency philosophy
  - Boot/End: Robustness (deterministic, no shortcuts)
  - Middle: Adaptive Latency (efficiency, scale to query)
- **Stats Verification**: All README stats verified against user-confirmed values

### Verification

| Metric | Result |
|--------|--------|
| Reddit Views | 360K+ ✅ |
| GitHub Stars | 114 ✅ |
| Opus References | All updated to 4.6 ✅ |

---

## v8.2.1 (09 February 2026)

**Metrics Sync & Architecture Refactor**: Updated session count and fixed automation scripts.

### Key Changes

- **Session Count**: Synced to 1073+ sessions
- **Automation Fix**: Repaired `generate_tag_index.py` path in `batch_audit.py` (script migrated to SDK location)
- **Orphan Remediation**: Linked 2 orphan files to Session_Observations.md
- **Tech Debt Reconciliation**: Fixed conflicting status for Hash-Based Delta Sync

### Verification

| Metric | Result |
|--------|--------|
| `batch_audit.py` | 5/5 scripts pass |
| Orphan count | 0 |
| Tag Index | 8,079 tags |

---

## v1.6.0 (08 February 2026)

**Curated Enhancement + Cleanup**: Added new protocols, SDK modules, scripts, and workflows. Removed legacy framework and duplicate files.

### Key Changes

- **+17 Protocols**: Added engineering (git-worktree, micro-commit, context-compaction, vibe-engineering, wizard-of-oz), decision (premise-audit, first-principles, MCDA, base-rate, ergodicity), research (deep-research-loop, cyborg-methodology, agentic-absorption), strategy (validation-triage, product-market-fit, paint-drop, priority-management)
- **+SDK Modules**: Added `src/athena/auditors/` (8 audit scripts) and `src/athena/generators/` (9 generator scripts)
- **+3 Scripts**: `athena_status.py`, `auto_tagger.py`, `code_indexer.py`
- **+2 Workflows**: `/due-diligence`, `/brand-generator`
- **Removed**: `.framework/v7.0/` (vestigial), 9 duplicate Snake_Case protocol files

### New Totals

| Metric | Count |
|--------|-------|
| Protocols | 87 |
| Scripts | 12 |
| Workflows | 14 |
| Case Studies | 11 |

---

## v1.5.2 (04 February 2026)

**Repository Enhancement**: Added skills framework, protocol exports, and knowledge graph.

### Key Changes

- **Protocol 416 (Agent Swarm)**: Exported parallel agent orchestration pattern to `examples/protocols/workflow/`
- **Skills Framework**: New `examples/skills/` directory with:
  - `coding/diagnostic-refactor/SKILL.md` — "Surgeon's Scan" pattern for code analysis before editing
  - README explaining skill structure and usage
- **KNOWLEDGE_GRAPH.md**: Compressed relationship map of Athena concepts and protocols
- **Session Logs Examples**: Added `examples/session_logs/` with example format and README
- **AGENTS.md**: Added passive context pattern (Vercel research)

### New Files

| Path | Description |
|------|-------------|
| `examples/protocols/workflow/416-agent-swarm.md` | Parallel worktree orchestration |
| `examples/skills/README.md` | Skills framework overview |
| `examples/skills/coding/diagnostic-refactor/SKILL.md` | Code diagnosis skill |
| `docs/KNOWLEDGE_GRAPH.md` | Compressed concept index |
| `examples/session_logs/README.md` | Session log format guide |
| `examples/session_logs/example-session.md` | Complete example |

---

## v1.5.1 (01 February 2026)

**SDK Parity & CLI-First Documentation**: Added `athena save` command and refactored GETTING_STARTED.md.

### Key Changes

- **`athena save` Command** (NEW): SDK-native session checkpointing via `python -m athena save "summary"`
- **Workflow Templates**: Updated `/start`, `/end`, `/save` to use SDK commands instead of manual scripts
- **GETTING_STARTED.md**: Refactored from 312 lines (7 steps) to 162 lines (3 steps), CLI-first approach
- **`init` Templates**: Now generates `save.md` workflow alongside `start.md` and `end.md`

---

## v8.1.0 (31 January 2026)

**Metrics Sync & Case Study Expansion**: Updated public metrics to reflect Session 995 and added new case studies.

### Key Changes

- **Metrics Sync**: Updated README and BENCHMARKS to reflect Session 995, 308 Protocols, and 146 Scripts.
- **Case Study Expansion**: Linked CS-120 (Vibe Coding), CS-140 (Silent Partner), and CS-144 (Auto-Blog) in README.
- **Library Consolidation**: Cleaned stale "150+" protocol references to reflect 308 canonical protocols.
- **Date Alignment**: Enforced Jan 31 2026 update across all core documentation.

## v8.0-Stable (30 January 2026)

**Zero-Point Refactor**: Sovereign Environment hardened, score-modulated RRF weights rebalanced.

### Key Changes

- **Sovereign Environment**: Consolidated silos into `.context/`, created `settings.json`, `ensure_env.sh`
- **Score-Modulated RRF**: Formula updated to `contrib = weight * (0.5 + doc.score) * (1/(k+rank))`
- **Weight Rebalance**: GraphRAG 3.5x → 2.0x, Vector 1.3x → 2.0x, Canonical boosted to 3.0x
- **Metrics**: Sessions 995, Protocols 308, Case Studies 42

> **Note on Protocol Count**: The drop from 285 (v1.2.8) to 150+ reflects a \"Great Purge\" audit that removed redundant, experimental, and superseded protocols. The count now reflects only **production-grade, actively-maintained** protocols.

---

## v8.1-Performance (30 January 2026)

**Semantic Cache & Latency Optimization**: Implemented true semantic caching for intelligent query reuse.

### Key Changes

- **Semantic Caching**: Upgraded `QueryCache` to store query embeddings and perform cosine similarity matching (threshold 0.90). Similar queries now return cached results instantly.
- **Search Latency**: Reduced from 30s+ to <5s (exact match) and ~0s (semantic match).
- **Pre-Warming**: Boot sequence now pre-caches 3 "hot" queries (`protocol`, `session`, `user profile`) for instant first-search response.
- **GraphRAG Optimization**: Added `--global-only` flag to skip redundant local model loading.

### Verification

| Query Type | Before | After |
|------------|--------|-------|
| First Search | 30s+ (hanging) | **4.71s** |
| Exact Cache Hit | N/A | **~0.00s** |
| Semantic Cache Hit | N/A | **~0.00s** |

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
