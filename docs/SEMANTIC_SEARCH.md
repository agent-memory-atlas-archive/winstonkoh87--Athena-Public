# Semantic Search: Triple-Path Retrieval Architecture

> **Last Updated**: 20 May 2026  
> **Purpose**: How Athena finds and retrieves relevant context using 8-channel hybrid search with RRF fusion

---

## Executive Summary

Athena employs **8-Channel Hybrid Search** with **Reciprocal Rank Fusion (RRF)** to ensure no relevant context is missed. Each channel catches what the others miss, and RRF merges their results into a single ranked list.

```text
                              USER QUERY
                                  │
                                  ▼
              ┌───────────────────┴───────────────────┐
              │        TRIPLE-PATH RETRIEVAL          │
              └───────────────────┬───────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│    PATH 1     │        │    PATH 2     │        │    PATH 3     │
│               │        │               │        │               │
│  🔮 VECTOR    │        │  🏷️ TAG      │        │  🔎 KEYWORD   │
│   SEARCH      │        │   INDEX       │        │    GREP       │
│               │        │               │        │               │
│  (Semantic)   │        │  (Hashtags)   │        │  (Exact)      │
└───────┬───────┘        └───────┬───────┘        └───────┬───────┘
        │                         │                         │
        ▼                         ▼                         ▼
 "decentralized"          "#leadership"           "Protocol 139"
 → finds related           → finds tagged         → finds exact
   concepts                   entities               matches
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
                                  ▼
                        ┌─────────────────┐
                        │  MERGED CONTEXT │
                        └─────────────────┘
```

---

## Why Three Paths?

| Path | Catches | Misses |
|:-----|:--------|:-------|
| **Vector** | Synonyms, paraphrases, concepts | Exact names, entities |
| **TAG_INDEX** | Explicitly tagged entities | Untagged content |
| **Keyword Grep** | Exact string matches | Semantic variations |

**Example**: Searching for a specific entity name

- **Vector search** might return "decentralized leadership" (semantically related)
- **TAG_INDEX** returns `#entity-name → Protocol 139` (exact entity match)
- **Keyword grep** finds any file mentioning the entity literally

---

## Path 1: Vector Semantic Search (VectorRAG)

> **Full Documentation**: [VECTORRAG.md](VECTORRAG.md)

```bash
# Reference: python3 scripts/supabase_search.py "<query>" --limit 5
```

**How it works**:

1. Query is converted to a 768-dimension embedding (Gemini `gemini-embedding-001`, Matryoshka-capable)
2. Cosine similarity search across 11 Supabase tables
3. Results fed into RRF fusion pipeline

**Strengths**: Finds conceptually related content even with different wording.

---

## Path 2: Protocol Summaries Lookup

> **Note**: The `TAG_INDEX.md` system has been **deprecated** as of v9.8.1. Protocol discovery now uses `PROTOCOL_SUMMARIES.md` and `PROTOCOL_HEATMAP.md`.

```bash
grep -i "<entity>" .context/PROTOCOL_SUMMARIES.md
```

**How it works**:

1. `generate_protocol_summaries.py` scans all protocol files
2. Extracts frontmatter metadata and first substantive body paragraph
3. Creates lookup: `Protocol ID → Description + Category`

**Example output**:

```text
| #leadership | `protocols/139-decentralized-command.md` |
| #archetype  | `user_profile/Archetype_Example.md` |
```

**Strengths**: Instant lookup for named protocols, skills, and concepts.

---

## RRF Fusion & Cross-Encoder Reranking

As of v9.8.1, `smart_search.py` implements an **8-channel hybrid search** pipeline:

```text
 Query
   │
   ├── Channel 1: Vector (Supabase pgvector, cosine similarity)
   ├── Channel 2: Keyword (ripgrep exact match)
   ├── Channel 3: Filename (fuzzy filename match)
   ├── Channel 4: Tag (frontmatter tag extraction)
   ├── Channel 5: Semantic Cache (LRU cache of recent queries)
   ├── Channel 6: Protocol Summary (PROTOCOL_SUMMARIES.md lookup)
   ├── Channel 7: Session Log (recent session log grep)
   ├── Channel 8: Case Study (case study index lookup)
   │
   ▼
 RRF Fusion (k=60, score-modulated weights)
   │
   ▼
 Cross-Encoder Reranker (optional: --rerank flag)
   Model: ms-marco-MiniLM-L6-v2
   Enabled by default in /ultrastart (15 candidates)
   Disabled in /start (3 candidates — too few to benefit)
   │
   ▼
 Ranked Results
```

| Metric | Value |
|--------|-------|
| **Search MRR** | 0.44 (vs 0.21 baseline, +105%) |
| **Latency** | < 200ms (p95, without reranker) |
| **Reranker Latency** | ~50-100ms additional |
| **Index Size** | 78MB vectors, 3,544 memory files |

---

## Path 3: Keyword Grep

```bash
grep -ri "<keyword>" .context/ .agent/
```

**How it works**:

- Simple string matching across all files
- Catches content not in Supabase (new files)
- Finds exact phrases

**Strengths**: Zero false negatives for exact matches.

---

## When to Use Each Path

```text
┌─────────────────────────────────────────────────────────────────┐
│                    QUERY TYPE → PATH SELECTION                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "What did we discuss about X?"      →  [VECTOR] primary       │
│  "Find Protocol 139"                 →  [GREP] primary         │
│  "Show me files tagged #leadership"  →  [TAG_INDEX] primary    │
│  "User archetype profile"            →  [TAG_INDEX] + [GREP]   │
│  "Complex analysis of leadership"    →  [VECTOR] + all paths   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration: The Search Protocol (§0.7.1)

Per Core Identity, **every query** triggers semantic context retrieval:

```text
┌──────────────────────────────────────────────────────────────────────┐
│  STEP 1: Vector Search                                               │
│  # Reference: python3 scripts/supabase_search.py "<query>" --limit 5       │
├──────────────────────────────────────────────────────────────────────┤
│  STEP 2: Entity Lookup (if named entities detected)                  │
│  grep -i "<entity_name>" .context/TAG_INDEX.md                       │
├──────────────────────────────────────────────────────────────────────┤
│  STEP 3: Fallback Grep (if above return sparse results)              │
│  grep -ri "<keyword>" .context/ .agent/                              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## The TAG_INDEX Generator

```bash
# Reference: python3 scripts/generate_tag_index.py
```

**Current Stats** (May 2026):

- **389 active protocols** summarized
- **8 channels** in search pipeline
- **Extraction methods**: YAML frontmatter + body paragraph extraction + tag inference

---

## Comparison: Before vs After Triple-Path

| Scenario | Before (Vector Only) | After (Triple-Path) |
|:---------|:---------------------|:--------------------|
| Search entity name | ❌ Missed related protocol | ✅ Found via TAG_INDEX |
| Search archetype | ❌ Missed profile file | ✅ Found via TAG_INDEX |
| Search "decentralized" | ✅ Found semantically | ✅ Still works |
| New unsynced file | ❌ Not in Supabase yet | ✅ Found via grep |

---

## Related Documentation

- [VECTORRAG.md](VECTORRAG.md) — Deep dive into vector embeddings
- [ARCHITECTURE.md](ARCHITECTURE.md) — Overall system design

---

`#semantic-search` `#triple-path` `#vectorrag` `#tag-index` `#retrieval`

---

## About the Author

Built by **Winston Koh** — 10+ years in financial services, now building AI systems.

→ **[About Me](ABOUT_ME.md)** | **[GitHub](https://github.com/winstonkoh87)** | **[LinkedIn](https://www.linkedin.com/in/winstonkoh87/)**
