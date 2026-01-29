# Knowledge Graph Architecture

> Visual representation of Athena's hybrid retrieval system.

---

## System Overview

```mermaid
graph TB
    subgraph Input["User Query"]
        Q[Query Text]
    end

    subgraph Retrieval["Hybrid Retrieval Layer"]
        V[Vector Search<br/>Semantic Similarity]
        T[Tag Index<br/>Explicit Labels]
        G[GraphRAG<br/>Entity Clusters]
        F[Filename<br/>Direct Reference]
    end

    subgraph Fusion["RRF Fusion Engine"]
        RRF[Reciprocal Rank Fusion<br/>k=60]
    end

    subgraph Rerank["Reranking"]
        R[Cross-Encoder<br/>Relevance Scoring]
    end

    subgraph Output["Final Output"]
        O[Top-K Results<br/>+ Λ Score]
    end

    Q --> V
    Q --> T
    Q --> G
    Q --> F

    V --> RRF
    T --> RRF
    G --> RRF
    F --> RRF

    RRF --> R
    R --> O
```

---

## RRF Fusion Formula

```text
RRF_score(doc) = Σ (1 / (k + rank_i))
```

Where:

- `k` = 60 (smoothing constant)
- `rank_i` = document rank in retrieval source `i`

---

## Retrieval Source Weights

| Source | Weight | Description |
| ------ | ------ | ----------- |
| Vector (Semantic) | 30% | pgvector cosine similarity |
| Tag Index | 25% | Explicit hashtag matching |
| GraphRAG | 25% | Leiden community detection |
| Filename | 20% | Direct path matching |

---

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant Q as Query Router
    participant V as Vector DB
    participant T as Tag Index
    participant G as GraphRAG
    participant F as Fusion
    participant R as Reranker
    participant L as LLM

    U->>Q: "What was my decision on X?"
    par Parallel Retrieval
        Q->>V: Embed & Search
        Q->>T: Tag Lookup
        Q->>G: Community Search
    end
    V->>F: Results + Scores
    T->>F: Results + Scores
    G->>F: Results + Scores
    F->>F: RRF Fusion
    F->>R: Fused Results
    R->>L: Top-K Reranked
    L->>U: Response + [Λ+XX]
```

---

## Component Details

### Vector Search (Supabase + pgvector)

- **Embedding Model**: Google `text-embedding-004` (768-dim)
- **Distance Metric**: Cosine similarity
- **Index Type**: IVFFlat

### Tag Index (Sharded Markdown)

- **Format**: Alphabetically sharded `.md` files
- **Lookup**: O(1) via shard routing
- **Git-friendly**: Human-readable diffs

### GraphRAG (NetworkX + Leiden)

- **Community Detection**: Leiden algorithm
- **Entity Extraction**: LLM-based NER
- **Resolution**: 0.5 (balanced granularity)

---

## Architecture Principles

| Principle | Implementation |
| --------- | -------------- |
| **Robustness > Speed** | RRF handles score-distribution mismatch |
| **Portability > Platform** | Markdown files are version-controlled |
| **Transparency > Magic** | Λ scores expose cognitive effort |
| **Recoverability > Efficiency** | Atomic writes prevent corruption |

---

*See [ENGINEERING_DEPTH.md](ENGINEERING_DEPTH.md) for implementation details.*
