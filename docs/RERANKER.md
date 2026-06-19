# Reranker: Cross-Encoder Re-Scoring

> **Last Updated**: 19 June 2026
> **Purpose**: How Athena re-scores fused retrieval candidates for precision

---

## Why a Reranker?

Vector search and RRF fusion are **fast but coarse**. A bi-encoder embeds the query and each document *independently*, then compares vectors — it never sees the query and the document together. This is great for recall (finding the ~50 plausibly-relevant chunks) but weak on precision (ordering those 50 correctly).

A **cross-encoder** fixes the ordering. It takes the `(query, candidate)` pair *jointly* and outputs a single relevance score, attending across both texts at once. It's too slow to run over the whole corpus — but perfect as a **second stage** over the small fused candidate set.

```text
   QUERY
     │
     ▼
┌─────────────────────────────┐
│  Stage 1: Parallel Hybrid   │   recall-oriented, fast
│  (vector + tag + canonical  │   → ~50 candidates
│   + sqlite + web + ...)      │
│  fused via RRF (k=60)        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Stage 2: CrossEncoder      │   precision-oriented
│  re-scores (query, cand)    │   → re-ordered top-N
│  pairs jointly              │
└──────────────┬──────────────┘
               │
               ▼
        TOP-N CONTEXT
```

---

## Implementation

| Property | Value |
|:---------|:------|
| **Model** | `sentence-transformers` CrossEncoder |
| **Stage** | After RRF fusion, before context injection |
| **Input** | `(query, candidate_text)` pairs from the fused set |
| **Output** | Scalar relevance score per candidate → re-sorted |
| **Runs on** | Local CPU; loads once per process |

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, candidates: list[dict]) -> list[dict]:
    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    for c, s in zip(candidates, scores):
        c["rerank_score"] = float(s)
    return sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
```

> [!NOTE]
> Cosmetic `position_ids` warnings emitted on model load do **not** affect scoring — they're a transformers version artifact. The reranker was verified functional locally (resolving an earlier dependency assumption).

---

## Where It Sits

The reranker is the final ranking authority before context reaches the model:

1. **Recall** — parallel channels each return their best matches → [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md)
2. **Fuse** — Reciprocal Rank Fusion (k=60, per-type weights) merges them → [VECTORRAG.md](VECTORRAG.md)
3. **Rerank** — CrossEncoder re-orders the fused set (this document)
4. **Inject** — top-N enters the working context

---

## References

- [ARCHITECTURE.md → Retrieval Stack](ARCHITECTURE.md#retrieval-stack)
- [VECTORRAG.md](VECTORRAG.md) — chunk-level embeddings + RRF
- [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md) — parallel hybrid channels
- [sentence-transformers CrossEncoder](https://www.sbert.net/examples/applications/cross-encoder/README.html)

---

`#reranker` `#cross-encoder` `#retrieval` `#precision` `#rrf`
