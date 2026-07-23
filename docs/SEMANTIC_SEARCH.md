# Semantic Search: Parallel Hybrid Retrieval Architecture

> **Last Updated**: 23 July 2026
> **Purpose**: How Athena finds and retrieves relevant context by fusing multiple complementary channels, then reranking for precision.

---

> [!IMPORTANT]
> **Refresh (23 July 2026)** — This document previously described a "Triple-Path" model (Vector + TAG_INDEX + Grep). That model is superseded. The production engine (`smart_search.py` → `run_search`) fuses **five always-on channels** (plus one opt-in web channel) via **Reciprocal Rank Fusion (RRF, k=60)**, then applies a **CrossEncoder reranker**. The old `TAG_INDEX` and `exocortex` channels were **retired** (dead on disk; `TAG_INDEX` moved to archive). **Vector is now the only *semantic* channel; the rest are lexical.** See [ARCHITECTURE.md → Retrieval Stack](ARCHITECTURE.md#retrieval-stack), [VECTORRAG.md](VECTORRAG.md), and [RERANKER.md](RERANKER.md).

## Executive Summary

Athena employs **parallel hybrid retrieval**: several retrievers with different failure modes run concurrently, each catching what the others miss. Their ranked lists are merged by **Reciprocal Rank Fusion**, and the merged shortlist is re-ordered by a **cross-encoder** before it reaches the model.

This is a deliberate implementation of the 2026 production-RAG consensus — a **two-stage cascade**: a fast, recall-oriented hybrid retrieve, followed by a slow, precision-oriented rerank. (See [How This Maps to 2026 Retrieval SOTA](#how-this-maps-to-2026-retrieval-sota).)

```text
                                USER QUERY
                                    │
              ┌─────────────────────┼─────────────────────────────┐
              │            STAGE 1 — PARALLEL RECALL              │
              └─────────────────────┼─────────────────────────────┘
        ┌──────────┬──────────┬─────┴─────┬──────────┬────────────┐
        ▼          ▼          ▼           ▼          ▼            ▼
  ┌──────────┐┌─────────┐┌─────────┐┌──────────┐┌───────────┐┌─────────┐
  │ 🔮 VECTOR ││ 📜 CANON ││ 🗂 SQLITE││ 📁 FILE   ││ 🧩 FRAME   ││ 🌐 WEB   │
  │ (semantic)││ (facts) ││ (tags/  ││ (name    ││  DOCS      ││ (opt-in) │
  │ pgvector  ││ grep    ││  paths) ││  match)  ││ (grep .md) ││ DuckDuckGo│
  └────┬─────┘└────┬────┘└────┬────┘└────┬─────┘└─────┬─────┘└────┬────┘
       └───────────┴──────────┴────┬─────┴────────────┴───────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │   RECIPROCAL RANK FUSION      │  ranks, not raw scores
                    │   Σ 1/(k+rank), k=60          │  + per-type weights
                    └──────────────┬────────────────┘
                                   ▼
              ┌────────────────────┴─────────────────────┐
              │        STAGE 2 — CROSS-ENCODER RERANK    │  top-50 → top-N
              │        scores (query, candidate) jointly │
              └────────────────────┬─────────────────────┘
                                   ▼
                            TOP-N CONTEXT
```

---

## The Channels

Each channel has a distinct blind spot; the fusion is what makes the whole robust.

| Channel | Mechanism | Catches | Misses |
|:--------|:----------|:--------|:-------|
| **🔮 Vector** *(semantic)* | Gemini embedding → pgvector cosine (`<=>`) across 11 domains | Synonyms, paraphrase, concepts | Rare exact tokens, brand-new files |
| **📜 Canonical** | Keyword grep over `CANONICAL.md` (materialized active facts), 2+ term overlap | Current ground-truth facts | Anything not yet distilled to canon |
| **🗂 SQLite** | Local `athena.db` tag/path index | Tagged files, offline recall | Semantic paraphrase |
| **📁 Filename** | `find` over the workspace by keyword | Exact file/tool/protocol names | Content-only matches |
| **🧩 Framework docs** | Grep over `.framework/`, `.context/`, memory bank | Identity/system docs | Non-doc corpora |
| **🌐 Web** *(opt-in, `--web`)* | DuckDuckGo scrape, fused at weight 2.8 | Real-time external facts | Anything private/internal |

> [!NOTE]
> **Vector is the only semantic channel.** The rest are lexical. That is by design: at a personal-knowledge-base scale, lexical channels are effectively free and eliminate the classic embedding failure mode — missing an exact protocol number, filename, or rare entity that a paraphrase-tuned embedding underweights.

**Vector fans out across 11 domains** — `sessions`, `case_studies`, `protocols`, `capabilities`, `playbooks`, `references`, `frameworks`, `workflows`, `user_profile`, `system_docs`, `entities` — each carrying its own RRF weight so authoritative sources (e.g. `protocol` 3.2, `capability` 3.2) outrank already-in-context boot docs (`system_doc`/`framework` 1.2). Full pipeline in [VECTORRAG.md](VECTORRAG.md).

---

## Two Stages: Recall, Then Precision

The split matters, and it's the same split every serious 2026 RAG stack makes.

- **Stage 1 (fuse for recall).** RRF operates on **ranks, not raw scores**, which sidesteps the score-incompatibility problem — a cosine similarity of 0.62 and a BM25 score of 14.3 aren't on the same axis, so you can't average them. RRF just rewards documents that rank high in *any* list: `score(d) = Σ 1/(k + rank_i(d))` with `k=60` (the near-universal default from the original 2009 RRF paper — and Athena's value). Cheap, robust, order-preserving.
- **Stage 2 (rerank for precision).** Embedding search is optimized for **recall, not precision**: a bi-encoder embeds query and document *separately*, so the query tokens never attend to the document tokens — it measures topical similarity, not intent alignment. A **cross-encoder** re-scores each `(query, candidate)` pair *jointly*, catching relevance the embedding missed. Too slow for the whole corpus, perfect over the fused top-50. Detail in [RERANKER.md](RERANKER.md).

An **adaptive router** short-circuits this: low-entropy queries with a high-confidence local hit skip the deep vector call entirely, so exact lookups stay instant and only genuinely semantic queries pay for embeddings + rerank.

---

## How This Maps to 2026 Retrieval SOTA

Athena's retrieval isn't bespoke cleverness — it's a faithful implementation of what the 2026 production-RAG literature converged on, which is worth stating plainly so the design can be judged against the field:

| 2026 consensus | Athena |
|:---------------|:-------|
| **Two-stage cascade**: hybrid retrieve → cross-encoder rerank is the standard production shape ([AppScale](https://appscale.blog/en/blog/hybrid-search-and-reranking-production-rag-bm25-dense-cross-encoder-2026), [DigitalApplied](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026)) | ✅ RRF fuse → CrossEncoder rerank |
| **RRF on ranks, k=60** solves score-incompatibility; 60 is the near-universal default ([Laforge](https://glaforge.dev/posts/2026/02/10/advanced-rag-understanding-reciprocal-rank-fusion-in-hybrid-search/), [Serghei](https://blog.serghei.pl/posts/reciprocal-rank-fusion-explained/)) | ✅ `RRF_K = 60`, per-type weights |
| **Hybrid = sparse + dense**; keyword catches exact/rare tokens, vector catches paraphrase | ✅ 5 lexical channels + 1 dense vector channel |
| **Rerank top-50, then trim to ~5**; cross-encoder catches intent the ANN recall stage can't ([TDS](https://towardsdatascience.com/advanced-rag-retrieval-cross-encoders-reranking/)) | ✅ top-50 → top-N |
| **pgvector collapses the vector store into Postgres**; cosine distance, same embed model for query and doc ([DEV](https://dev.to/thegdsks/rag-with-postgres-pgvector-in-2026-the-full-typescript-pipeline-2lbd)) | ✅ Supabase pgvector, `gemini-embedding-001` |

Reported gains for exactly this stack (BM25 + dense + RRF + cross-encoder) push **recall@10 from ~78% to ~91%**, while the rerank adds only ~50–200 ms — negligible against 500–2000 ms of LLM generation ([AppScale](https://appscale.blog/en/blog/hybrid-search-and-reranking-production-rag-bm25-dense-cross-encoder-2026)).

**Where Athena deliberately diverges from the textbook:**

- **Exact scan, not ANN.** pgvector's `ivfflat`/`hnsw` approximate indexes are capped below 3,072 dimensions, so at Gemini's 3072-dim embeddings Athena runs an **exact sequential scan** — sub-millisecond under ~10k chunks, with zero index staleness. At personal-KB scale, exact recall beats approximate.
- **Graph channel retired.** 2026 hybrid stacks sometimes add graph-traversal signals (GraphRAG). Athena evaluated and **removed** GraphRAG (2026-06-06, dead 16 months) — the maintenance cost of entity-graph upkeep wasn't justified by the recall it added over vector+lexical. See [GRAPHRAG.md](GRAPHRAG.md). `KNOWLEDGE_GRAPH.md` is now a hand-maintained map, not a queried index.

---

## Privacy: Domain Filtering

Retrieval is **domain-scoped**. Every chunk carries a `domain` tag, and the engine **excludes the `personal` domain from default results** — personal material is indexed but never surfaces in an ordinary search unless the caller explicitly opts in (`--include-personal`). Sensitive context stays partitioned from routine retrieval by default, not by trust.

---

## Agentic Retrieval: Knowing *When* to Search

There is no always-on "retrieve on every token." Athena decides *when* to hit memory — which is itself the direction 2026 research favors (goal-directed retrieval outperforms goal-agnostic compression). Three triggers compose:

1. **Skill context-triggers** — phrases like *"do we have a protocol for…", "recall", "past session", "case study"* activate the `semantic-search` skill.
2. **A code-fired grounding gate** — a hook nudges the agent to ground non-trivial queries in ≥1 external retrieval before answering (scaled by query complexity).
3. **Agent judgment** — the model itself elects to search when a query plausibly touches prior context.

The result is *goal-directed* recall: search fires when it will help, and exact/low-entropy lookups skip the expensive path.

```text
┌──────────────────────────────────────────────────────────────┐
│                 QUERY TYPE → CHANNEL EMPHASIS                 │
├──────────────────────────────────────────────────────────────┤
│  "What did we conclude about X?"    →  VECTOR (semantic)      │
│  "Find Protocol 139"                →  FILENAME + CANONICAL   │
│  "Current facts on my runway"       →  CANONICAL              │
│  "Latest on <external topic>"       →  WEB (--web)            │
│  "Deep analysis of <theme>"         →  ALL, fused + reranked  │
└──────────────────────────────────────────────────────────────┘
```

---

## Worked Example

> **Query**: *"Should I accept this commission-only partnership where the agent takes no risk?"*

1. **Recall** — Vector surfaces `Protocol 33: Principal-Agent Problem` and a structurally similar past case study by *meaning*; Canonical/Filename confirm the exact protocol; the personal domain stays excluded.
2. **Fuse** — RRF merges the lists; the authoritative `protocol` weight lifts P33 above supplementary session chatter.
3. **Rerank** — the cross-encoder, seeing query and candidates together, promotes the case study whose *structure* (zero-downside counterparty) matches the query's intent, not just its keywords.
4. **Answer** — grounded in retrieved memory: *"This matches the Principal-Agent structure from [prior case]; the counterparty bears no downside while you carry the liability. Reject unless they accept a clawback clause (shared risk), per Protocol 33."*

The difference from a generic model isn't eloquence — it's that the answer is anchored to the operator's *own* accumulated patterns.

---

## Related Documentation

- [`examples/engine/`](../examples/engine/) — **the real production code** behind this doc (read-only excerpts: search, vectors, reranker, config, sync)
- [VECTORRAG.md](VECTORRAG.md) — chunk-level embeddings, pgvector schema, sync pipeline
- [RERANKER.md](RERANKER.md) — the cross-encoder second stage
- [ARCHITECTURE.md](ARCHITECTURE.md) — overall system design & retrieval stack
- [GRAPHRAG.md](GRAPHRAG.md) — why the graph channel was evaluated and removed

---

## References

- [Hybrid Search & Re-ranking in Production RAG 2026 — AppScale](https://appscale.blog/en/blog/hybrid-search-and-reranking-production-rag-bm25-dense-cross-encoder-2026)
- [Hybrid Search: BM25, Vector & Reranking Reference 2026 — DigitalApplied](https://www.digitalapplied.com/blog/hybrid-search-bm25-vector-reranking-reference-2026)
- [Advanced RAG — Understanding Reciprocal Rank Fusion — Guillaume Laforge](https://glaforge.dev/posts/2026/02/10/advanced-rag-understanding-reciprocal-rank-fusion-in-hybrid-search/)
- [Reciprocal Rank Fusion Explained — Serghei](https://blog.serghei.pl/posts/reciprocal-rank-fusion-explained/)
- [Advanced RAG Retrieval: Cross-Encoders & Reranking — Towards Data Science](https://towardsdatascience.com/advanced-rag-retrieval-cross-encoders-reranking/)
- [RAG with Postgres pgvector in 2026 — DEV](https://dev.to/thegdsks/rag-with-postgres-pgvector-in-2026-the-full-typescript-pipeline-2lbd)

---

`#semantic-search` `#hybrid-retrieval` `#rrf` `#cross-encoder` `#vectorrag` `#pgvector`

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
