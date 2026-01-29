# Engineering Depth: Technical Decisions in Athena

> This document explains the **non-obvious engineering decisions** behind Athena.  
> It's designed for technical reviewers who want to understand the "why" behind the architecture.

---

## 1. Hybrid RAG with Reciprocal Rank Fusion (RRF)

### The Problem

Simple vector search fails on **broad queries**. If you ask "What did I decide about X?", pure semantic similarity returns tangentially related documents, not the actual decision log.

### The Solution

Athena uses **Reciprocal Rank Fusion (RRF)** to combine multiple retrieval strategies:

```
RRF_score = Σ (1 / (k + rank_i))
```

| Strategy | Weight | What It Finds |
|----------|--------|---------------|
| **Vector (Semantic)** | 30% | Conceptually similar content |
| **Tag Index** | 25% | Explicitly tagged documents |
| **Filename/Path** | 20% | Direct file references |
| **GraphRAG Communities** | 25% | Entity-relationship clusters |

**Why RRF over simple weighting?**  
RRF is **rank-based**, not score-based. This means it's robust to the wildly different score distributions between vector cosine similarity (0.0–1.0) and BM25 text search (0–100+).

### Implementation

```python
# Simplified RRF fusion
def fuse_results(result_lists: list[list], k: int = 60) -> list:
    scores = defaultdict(float)
    for results in result_lists:
        for rank, doc in enumerate(results):
            scores[doc.id] += 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
```

**Trade-off**: RRF adds latency (~50ms per query). We accept this because **retrieval quality directly impacts reasoning quality**.

---

## 2. Atomic Writes with POSIX Guarantees

### The Problem

Athena writes to markdown files constantly (session logs, quicksaves, protocol updates). In an agentic IDE, the AI can be interrupted mid-write. A corrupted `Core_Identity.md` is catastrophic.

### The Solution

All writes use the **write-temp-fsync-rename** pattern:

```python
def atomic_write(path: Path, content: str) -> None:
    """POSIX-guaranteed atomic write."""
    temp_path = path.with_suffix('.tmp')
    
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())  # Force to disk
    
    temp_path.rename(path)  # Atomic on POSIX
```

**Why this matters:**

- `fsync()` ensures content hits disk before rename
- `rename()` is atomic on POSIX — either old file or new file, never partial
- If power fails mid-write, we get the old file, not corruption

### Concurrency Control

For operations like `supabase_sync.py`, we add **PID-based lockfiles with TTL**:

```python
def acquire_lock(lock_path: Path, ttl_seconds: int = 300) -> bool:
    if lock_path.exists():
        # Check if stale (previous crash)
        age = time.time() - lock_path.stat().st_mtime
        if age < ttl_seconds:
            return False  # Another process is running
        # Stale lock — safe to override
    
    lock_path.write_text(str(os.getpid()))
    return True
```

---

## 3. Sharded Tag Index for O(1) Lookup

### The Problem

With 1000+ files, a single `TAG_INDEX.md` becomes a bottleneck:

- Parsing time increases linearly with file count
- Git diffs become unreadable
- Search requires full file scan

### The Solution

Split the index into **alphabetical shards**:

```
.context/
├── TAG_INDEX_A-M.md   # Tags starting with A-M
└── TAG_INDEX_N-Z.md   # Tags starting with N-Z
```

**Lookup algorithm:**

```python
def find_tag(tag: str) -> list[str]:
    shard = "A-M" if tag[0].lower() <= 'm' else "N-Z"
    shard_content = load(f"TAG_INDEX_{shard}.md")
    return parse_tag_entries(shard_content, tag)
```

**Why not a database?**  
Markdown files are **version-controllable** and **human-readable**. The entire knowledge graph is auditable via `git log`.

---

## 4. Latency Indicator (Λ) for Observability

### The Philosophy

Every AI response should be **transparent about its cognitive effort**. The Λ score is a self-reported complexity metric:

| Score | Meaning |
|-------|---------|
| Λ+1-10 | Simple recall/lookup |
| Λ+20-40 | Multi-framework synthesis |
| Λ+60-80 | Full parallel reasoning |
| Λ+100 | Maximum depth analysis |

### Why This Matters

1. **User calibration**: High Λ = "This took effort, review carefully"
2. **Cost awareness**: High Λ ≈ higher token usage
3. **Audit trail**: Session logs include Λ for retrospective analysis

### Implementation

```python
# Appended to every response
response += f"\n\n[Λ+{complexity_score}]"
if complexity_score > 20:
    response += f"\n{' | '.join(protocols_used)}"
```

---

## 5. Query Archetype Routing (Protocol 133)

### The Problem

Different queries require **different retrieval strategies** and **different tones**:

- "Fix this bug" → Code, precise, no philosophy
- "Why do I feel this way?" → Psychology, empathetic, no code
- "What's the plan?" → Strategy, structured, long-term

### The Solution

Classify queries into **10 archetypes** before processing:

| Archetype | Trigger | RAG Priority | Tone |
|-----------|---------|--------------|------|
| Strategist | "How do I build X?" | Frameworks, Principles | Architect |
| Executor | "Write this code" | Code, Docs | Precise |
| Mirror | "Why do I feel?" | Psychology | Empathetic |
| Skeptic | "Is this a good idea?" | Constraints, Risk | Adversarial |

**Routing is implicit** — the user doesn't invoke archetypes; the system detects intent and adjusts.

---

## 6. The Boot Sequence: Hardened for Failure

### Constraint

`boot.py` **must use only stdlib**. No SDK dependencies. If the SDK has a bug, the boot layer must still work to allow self-repair.

### Components

| Component | Purpose |
|-----------|---------|
| **Watchdog** | 90-second SIGALRM timeout → suggests safe mode |
| **Semantic Prime** | SHA-384 hash verification of Core_Identity.md |
| **Safe Boot Fallback** | Zero-dependency emergency shell script |
| **Health Canary** | `DEAD_MAN_SWITCH.md` with 90-day audit schedule |

### Philosophy

> "If you can't boot, you can't fix."

The boot layer is the **last line of defense**. It must be simple, observable, and resilient.

---

## Summary: Engineering Principles

| Principle | Implementation |
|-----------|----------------|
| **Robustness > Efficiency** | RRF over simple vector search |
| **Transparency > Magic** | Λ scores, reasoning chains |
| **Recoverability > Speed** | Atomic writes, boot hardening |
| **Portability > Platform** | Markdown files, git versioning |

---

*This document is part of the [Athena](https://github.com/winstonkoh87/Athena-Public) project.*
