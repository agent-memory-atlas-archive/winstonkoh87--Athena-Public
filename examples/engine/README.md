# Athena Retrieval Engine — Reference Excerpts

> Verbatim, **read-only** excerpts of Athena's private production retrieval engine — the actual code behind [`docs/SEMANTIC_SEARCH.md`](../../docs/SEMANTIC_SEARCH.md), [`docs/VECTORRAG.md`](../../docs/VECTORRAG.md), and [`docs/RERANKER.md`](../../docs/RERANKER.md). Published for transparency and technical review.

## What's here

| File | Real module path | What it does |
|------|------------------|--------------|
| [`search.py`](search.py) | `src/athena/tools/search.py` | The hybrid retrieval orchestrator — fuses five lexical/semantic channels via **Reciprocal Rank Fusion (k=60)**, then cross-encoder reranks. Includes the adaptive router, per-type RRF weighting, parallel channel execution, semantic caching, and retrieval telemetry. |
| [`vectors.py`](vectors.py) | `src/athena/memory/vectors.py` | The embedding + vector layer — Gemini `gemini-embedding-001` (3072-dim) and Supabase pgvector access. Exponential backoff with jitter, semaphore-gated rate limiting, batch embedding with per-item safe-degrade, and a WAL-mode SQLite embedding cache. |
| [`reranker.py`](reranker.py) | `src/athena/tools/reranker.py` | The cross-encoder second stage — quantized **ONNX fast path** (~0.4s cold load) with a `sentence-transformers` fallback. |

Together these are the **read path** of the pipeline: **retrieve → fuse → rerank**.

## What's deliberately omitted

This is a curated excerpt, not the whole package. The internal modules these files import — session lifecycle, governance/safety gates, workspace configuration, and the indexing/sync pipeline — are **intentionally not published**. Athena operates over private personal data (financial records, journals), so the open/closed boundary is drawn on purpose. Consequently:

- These files **reference** internal modules (`athena.core.config`, `athena.core.governance`, `athena.sessions`, …) that aren't included here — so they are for **reading, not running**.
- **No secrets are present.** Every credential (Gemini API key, Supabase URL + service-role key) is loaded from environment variables — see [`.env.example`](../../.env.example).

## Design notes worth a look

- **RRF over ranks, not scores** (`search.py` → `weighted_rrf`) — sidesteps the score-incompatibility problem when fusing a cosine similarity with a keyword-overlap score. `k = 60`, the near-universal default from the 2009 RRF paper.
- **Two-stage recall → precision** — cheap parallel recall across channels, then an expensive cross-encoder over only the top ~50 fused candidates.
- **Secret hygiene** (`vectors.py`) — the API key is passed as a request *header*, never in the URL, so it can't leak into a logged exception's URL repr.
- **Crash-safe indexing** — embeddings are computed *before* the destructive DB delete, so a transient failure can never wipe a document's chunks with no replacement.
- **Exact scan, not ANN** — at 3072 dimensions pgvector's approximate indexes are unavailable, so retrieval runs an exact sequential scan (sub-millisecond under ~10k chunks).

---

Built by **Winston Koh** — [GitHub](https://github.com/winstonkoh87) · [LinkedIn](https://www.linkedin.com/in/winstonkoh87/)
