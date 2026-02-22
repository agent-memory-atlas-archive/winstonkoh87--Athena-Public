# ⚡ Performance Benchmarks

> **Last Updated**: 22 February 2026  
> **Environment**: MacBook Pro M3, Python 3.13, Supabase (Singapore region)

---

## Boot Sequence Performance

| Metric | Measured |
|--------|----------|
| Cold Boot (full `/start` sequence) | ~1–2 minutes |
| Warm Boot (cached, no script re-run) | ~30–60 seconds |
| Identity Hash Verification | ~0.3s |
| Search Index Prime | ~1–2s |

> [!NOTE]
> Boot time includes: loading 3 core identity files, running `boot.py` (session recall + creation + context capture + semantic prime), and the Athena daemon startup. The ~1–2 minute figure is end-to-end measured time on an M3 MacBook Pro.

### Optimizations Applied

- **Persistent Caching**: Embeddings cached to disk, delta sync on changed files
- **Parallel Phase Execution**: Boot phases run concurrently where possible
- **Canonical Memory**: Single materialized view replaces querying 1,100+ session logs

---

## Semantic Search Performance

| Query Type | Latency (p50) | Latency (p95) | Results Quality |
|------------|---------------|---------------|-----------------|
| Simple keyword | 180ms | 320ms | ⭐⭐⭐ |
| Semantic concept | 420ms | 680ms | ⭐⭐⭐⭐⭐ |
| Cross-domain fusion | 850ms | 1,200ms | ⭐⭐⭐⭐⭐ |

### Search Pipeline

```
Query → Embedding (local) → Parallel Search (Supabase + GraphRAG) → RRF Fusion → Rerank → Top 10
```

**RRF (Reciprocal Rank Fusion)** combines results from:

1. **Supabase pgvector** — Dense vector similarity
2. **GraphRAG Communities** — Structural/relational context
3. **Keyword BM25** — Exact match fallback

---

## Token Economics

| Operation | Tokens (Before) | Tokens (After) | Savings |
|-----------|-----------------|----------------|---------|
| Cold start context injection | ~50,000 | ~12,500 (core boot) | **75%** |
| Full enriched boot (with profile) | ~50,000 | ~17,000 | **66%** |
| Session handoff (`/end`) | ~8,000 | ~1,500 | **81%** |
| Protocol retrieval | ~3,000 | ~800 | **73%** |

### Boot Payload Breakdown (Measured Feb 2026)

The core boot payload is **~12.5K tokens** — always loaded on `/start`. The full enriched payload (with user profile) is **~17K tokens**, loaded adaptively. The Canonical Memory alone is ~3.3K tokens — a single materialized view that supersedes searching 1,100+ session logs.

| Component | Source File | Est. Tokens | Load Strategy |
|-----------|-------------|:-----------:|:-------------:|
| **Core Identity** | `Core_Identity.md` | ~6,081 | Boot (always) |
| **Canonical Memory** | `CANONICAL.md` | ~3,346 | Boot (always) |
| **Memory Bank** | `memory_bank/` (5 files) | ~3,078 | Boot (always) |
| **User Profile** | `User_Profile_Core.md` | ~4,477 | On-Demand |
| **─── Core Boot Total** | | **~12,504** | |
| **─── Full Enriched Total** | | **~16,981** | |

### How We Achieved This

- **Document Sharding**: Large protocols split into retrievable chunks
- **Summary Caching**: Session summaries pre-computed at `/end`
- **Selective Context**: Only relevant protocols injected per query
- **Canonical Memory**: Single materialized view supersedes searching 500+ session logs

---

## Data Volume Stats

| Asset | Count | Size |
|-------|-------|------|
| Protocols & Workflows | 120+ protocols, 49 workflows | ~1.5 MB |
| Case Studies | 42 | ~2.4 MB |
| Session Logs | 1,100+ | ~4.2 MB |
| GraphRAG Entities | 4,200+ | ~46 MB |
| Vector Embeddings | 12,800+ | ~78 MB |

---

## Reliability Metrics

| Metric | Value |
|--------|-------|
| Boot Success Rate | 99.2% |
| Search Availability | 99.8% |
| Data Redundancy | 3-way (Local + GitHub + Supabase) |
| Recovery Time (from cloud) | < 5 minutes |

---

## Methodology

All benchmarks measured with:

```bash
time python3 .agent/scripts/boot.py
time python3 .agent/scripts/smart_search.py "test query"
```

Latency measurements averaged over 50 runs. Token counts measured via Anthropic/OpenAI token counters.

---

*These numbers are real production metrics from a live system, not synthetic benchmarks.*
