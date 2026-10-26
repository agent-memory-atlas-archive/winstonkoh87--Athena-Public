# Athena Source Package (`src/athena`)

`src/athena` contains the core Python runtime, memory management, intelligence engines, and governance tools for Project Athena.

## 📦 Subsystems Overview

| Subsystem | Location | Description |
| :--- | :--- | :--- |
| **Core** | [`src/athena/core/`](athena/core/) | Heartbeat, permission gates, governance enforcement, colors, and configuration. |
| **Intelligence** | [`src/athena/intelligence/`](athena/intelligence/) | Decision screening (GTO engine), adversarial wargaming, and hypothesis frame ledger. |
| **Memory** | [`src/athena/memory/`](athena/memory/) | Vector embeddings, contextual chunking, local caching, and Supabase synchronization. |
| **Tools** | [`src/athena/tools/`](athena/tools/) | FastMCP tool bindings, agentic search, trade guardian, contract specs, and citation verification. |
| **Auditors** | [`src/athena/auditors/`](athena/auditors/) | Anti-pattern scanners, personality drift monitors, and codebase staleness checks. |
| **Boot** | [`src/athena/boot/`](athena/boot/) | JIT loader orchestrator, prefetch subsystems, and session lifecycle managers. |

## 🛠️ Development

Install the package in editable mode:

```bash
pip install -e ".[dev]"
```

Run test suite:

```bash
pytest tests/
```
