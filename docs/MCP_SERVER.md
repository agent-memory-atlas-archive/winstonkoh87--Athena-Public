# MCP Tool Server

> **Model Context Protocol integration for Project Athena.**

The MCP Server exposes Athena's core capabilities as standardized [MCP tools](https://modelcontextprotocol.io/), consumable by any MCP-compatible client (Antigravity, Claude Desktop, Cursor, etc.).

---

## Quick Start

### stdio (IDE Integration)

```bash
python -m athena.mcp_server
```

### SSE (Remote / Multi-Client)

```bash
python -m athena.mcp_server --sse --port 8765
```

### IDE Configuration

Add to your IDE's MCP settings (e.g., `.agent/mcp_config.json`):

```json
{
  "mcpServers": {
    "athena": {
      "command": "python",
      "args": ["-m", "athena.mcp_server"],
      "cwd": "/path/to/your/athena/workspace"
    }
  }
}
```

---

## Tools (8)

| Tool | Permission | Sensitivity | Description |
|------|-----------|-------------|-------------|
| `smart_search` | read | internal | Hybrid RAG search (Canonical + Tags + Vectors + Filenames) with RRF fusion |
| `quicksave` | write | internal | Save timestamped checkpoint to session log |
| `health_check` | read | public | Audit Vector API + Database subsystems |
| `recall_session` | read | internal | Retrieve recent session log content |
| `governance_status` | read | internal | Check Triple-Lock compliance state |
| `list_memory_paths` | read | public | List active memory directories |
| `set_secret_mode` | admin | — | Toggle demo/external mode (blocks internal tools) |
| `permission_status` | read | — | Show permission state and tool manifest |

## Resources (2)

| URI | Description |
|-----|-------------|
| `athena://session/current` | Full content of active session log |
| `athena://memory/canonical` | Canonical Memory (CANONICAL.md) |

---

## Permissioning Layer

All tools are gated by the **Permissioning Engine** (`athena.core.permissions`).

### Capability Tokens

4 escalating permission levels:

| Level | Access |
|-------|--------|
| `read` | Query/read data |
| `write` | Modify session logs, checkpoints |
| `admin` | Modify config, clear caches |
| `dangerous` | Delete data, run shell commands (future) |

Default caller level: `write` (can access `read` + `write` tools).

### Sensitivity Labels

3 data classification tiers:

| Label | Description | Examples |
|-------|-------------|----------|
| `public` | Safe for demos, external sharing | Health check, memory paths |
| `internal` | Normal operational data | Session logs, search results |
| `secret` | Credentials, finances, PII | API keys, trading data |

### Secret Mode

Toggle with `set_secret_mode(True)`. When active:

- ✅ `health_check` and `list_memory_paths` remain accessible (PUBLIC)
- 🔒 All INTERNAL/SECRET tools are blocked
- 📝 Content from remaining data sources is auto-redacted (API keys → `[REDACTED]`)

Use case: sharing screen during a demo, external pair-programming, or showing Athena to a client.

### Content Auto-Classification

The engine auto-labels content based on pattern matching:

- **SECRET patterns**: `api_key`, `password`, `SUPABASE_KEY`, `trading`, `.env`, etc.
- **INTERNAL patterns**: `session_log`, `canonical`, `memory_bank`, etc.
- Everything else → `PUBLIC`

### Audit Trail

Every permission check is logged with timestamp, action, target, and outcome. Audit log is bounded at 1,000 entries (auto-truncated to 500).

---

## Dependencies

```bash
pip install fastmcp>=2.0.0
# or
pip install athena-cli[mcp]
```

---

## Architecture

```
┌─────────────────────────────────────┐
│         MCP Client (IDE)            │
│   (Antigravity / Claude Desktop)    │
└──────────────┬──────────────────────┘
               │ stdio / SSE
┌──────────────▼──────────────────────┐
│         MCP Server (FastMCP)        │
│                                     │
│  ┌───────────┐  ┌────────────────┐  │
│  │ Permission │  │   Tool Router  │  │
│  │   Gate     │──│                │  │
│  └───────────┘  │ smart_search   │  │
│                 │ quicksave      │  │
│                 │ health_check   │  │
│                 │ recall_session │  │
│                 │ governance     │  │
│                 │ memory_paths   │  │
│                 │ secret_mode    │  │
│                 │ perm_status    │  │
│                 └───────┬────────┘  │
└─────────────────────────┼───────────┘
                          │
┌─────────────────────────▼───────────┐
│          Athena SDK (core)          │
│  search │ sessions │ governance     │
│  health │ config   │ permissions    │
└─────────────────────────────────────┘
```
