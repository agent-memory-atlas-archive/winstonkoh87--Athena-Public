# Scripts

> **Note**: Production implementations are not included in this public repository.

This folder previously contained 87 automation scripts that power Athena's core functionality, including:

- Session orchestration (`boot.py`, `shutdown.py`, `quicksave.py`)
- Semantic search (`smart_search.py`, `supabase_search.py`)
- Memory sync (`supabase_sync.py`)
- Knowledge graph operations (`query_graphrag.py`, `build_graph.py`)

## Why Not Included?

These scripts represent months of iterative refinement and are the "execution layer" that makes Athena's conceptual frameworks operational. Sharing them would provide competitors with a free MVP.

## What's Available

- **Protocols**: Framework patterns and decision models (see `examples/protocols/`)
- **Workflows**: Process documentation (see `examples/workflows/`)
- **Architecture**: System design explanations (see `docs/`)

## Building Your Own

The [GETTING_STARTED.md](docs/GETTING_STARTED.md) guide explains the architecture patterns. Implementation is left as an exercise — the real value is in the iteration, not the code.

---

# private #implementation
