# 🏷️ TAG_INDEX — Concept Reference

> **Last Updated**: 19 June 2026
> **Status**: Concept reference (the live index is generated, not hand-maintained)

---

## What It Is

`TAG_INDEX` is one of the retrieval channels in Athena's [Parallel Hybrid search](SEMANTIC_SEARCH.md). It is a **reverse lookup** that maps an inline `#hashtag` to every file that carries it:

```text
#leadership → protocols/139-decentralized-command.md
#first-principles → protocols/decision/DEC-115-first-principles-deconstruction.md
```

Where **vector search** finds *meaning* and **grep** finds *exact strings*, the tag index gives **instant, precise retrieval of explicitly-tagged entities** (people, protocols, concepts) without an embedding round-trip. It is the cheapest, highest-precision channel for "show me everything tagged X."

## How It Works

1. A generator scans the workspace for YAML frontmatter tags and inline `#hashtags`.
2. It builds the reverse map (`tag → [files]`) and shards it for fast lookup.
3. At query time, named-entity queries hit the index directly; results are fused into the [RRF ranking](VECTORRAG.md) alongside the other channels.

## Why This File Is a Stub

In a live Athena workspace the index is **machine-generated** from your own files and grows to thousands of tags — it is personal data, regenerated on sync, and not meaningful to ship as a static snapshot. This page documents the *concept*; your own instance materialises the real index locally.

> See also: [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md) (the channel in context) · [VECTORRAG.md](VECTORRAG.md) (vector channel + fusion) · [ARCHITECTURE.md](ARCHITECTURE.md#retrieval-stack) (full retrieval stack).

---

`#tag-index` `#retrieval` `#semantic-search` `#concept`
