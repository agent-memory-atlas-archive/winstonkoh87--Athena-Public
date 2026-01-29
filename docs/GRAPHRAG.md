# GraphRAG: Knowledge Graph Layer

> **Status**: ✅ Active (Jan 2026)  
> **Weight**: 2.0x in RRF fusion (balanced with Vector)

---

## Overview

Unlike flat vector search, GraphRAG extracts **entities** from your documents and clusters them into **communities** using the Leiden algorithm. This enables:

| Capability | Description |
|------------|-------------|
| **Cross-domain synthesis** | "How does X relate to Y?" queries |
| **Community detection** | Auto-discovers concept clusters |
| **Entity fan-out** | Expands queries to related concepts |

---

## Architecture

```
Documents → Entity Extraction → Knowledge Graph → Community Detection → Search
                                    ↓
                              ChromaDB Vectors
```

### Components

| Component | Format | Size | Purpose |
|-----------|--------|------|---------|
| `communities.json` | JSON | ~800KB | 1,460 auto-detected clusters |
| `entities.json` | JSON | ~2.3MB | Named entity index |
| `knowledge_graph.gpickle` | NetworkX | ~46MB | Graph structure |
| `chroma.sqlite3` | SQLite | ~78MB | Entity vector embeddings |

---

## Retrieval Weight

GraphRAG is weighted **2.0x** in the RRF fusion algorithm — at parity with Vector for balanced retrieval:

| Source | Weight | Rationale |
|--------|--------|-----------|
| **Canonical** | 3.0x | Curated single source of truth |
| **GraphRAG** | 2.0x | Structured knowledge clusters |
| **Vector** | 2.0x | Semantic similarity (parity with Graph) |
| Tags | 1.5x | Explicit keyword matches |
| Filename | 1.0x | Literal file matching |

---

## How It Works

### 1. Community Matching

When you query "sovereignty arbitrage":

```
Query → Tokenize → ["sovereignty", "arbitrage"]
                        ↓
    Search 1,460 communities for keyword matches
                        ↓
    Results: Community 1 (2 hits), Community 0 (1 hit)
```

### 2. ChromaDB Entity Search

Parallel to community matching, the system queries ChromaDB for semantically similar entities:

```
Query → Embed → Vector similarity search → Top 5 entities
```

### 3. RRF Fusion

Both GraphRAG results are fused with other sources using Reciprocal Rank Fusion:

```
Score = Σ (weight × 1/(k + rank))
```

Where `k = 60` (the RRF constant).

---

## Example Output

```
🔍 SMART SEARCH: "sovereignty arbitrage"
============================================================

🏆 TOP 3 RESULTS:

  1. [HIGH] [RRF:0.0574] Community 1 (1712 members, 2 hits)
     Signals: {"graphrag": {"rank": 1, "contrib": 0.05738}}
     📄 Matched: sovereignty, arbitrage | Cluster: #lmarena, #dismissive-avoidant...

  2. [HIGH] [RRF:0.0565] Community 0 (21 members, 1 hits)
     Signals: {"graphrag": {"rank": 2, "contrib": 0.05645}}
     📄 Matched: arbitrage | Cluster: #4, Last Updated, #5...

  3. [HIGH] [RRF:0.0556] Community 504 (13 members, 1 hits)
     Signals: {"graphrag": {"rank": 3, "contrib": 0.05556}}
     📄 Matched: arbitrage | Cluster: 1. Outcome Framing, outcome...
```

---

## When GraphRAG Helps Most

| Query Type | GraphRAG Value | Example |
|------------|----------------|---------|
| Cross-domain | ⭐⭐⭐ High | "How do trading and psychology connect?" |
| Concept clusters | ⭐⭐⭐ High | "What relates to sovereignty?" |
| Specific lookup | ⭐ Low | "Where is Agentic Engineering Strategy?" (use filename search) |
| Semantic match | ⭐⭐ Medium | "Find protocols about risk" (vector also works) |

---

## Re-indexing

To rebuild the knowledge graph after adding new content:

```bash
python3 .agent/scripts/index_graphrag.py
```

This regenerates:

- Entity extraction from all Markdown files
- Community detection via Leiden algorithm
- ChromaDB vector embeddings

---

## Related Documentation

- [VECTORRAG.md](VECTORRAG.md) — Semantic vector search layer
- [ARCHITECTURE.md](ARCHITECTURE.md) — Overall system design
- [SEMANTIC_SEARCH.md](SEMANTIC_SEARCH.md) — Hybrid RAG implementation

---

## Tags

# graphrag #knowledge-graph #rag #search #communities #entities
