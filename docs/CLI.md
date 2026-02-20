# CLI Reference

## Installation

```bash
pip install -e .
```

## Commands

| Command | Description |
|:--------|:-----------|
| `athena` | Boot a new session |
| `athena init .` | Initialize workspace in current directory |
| `athena init --ide claude` | Init with Claude Code agents + `CLAUDE.md` |
| `athena init --ide antigravity` | Init with Antigravity config (`AGENTS.md`) |
| `athena init --ide cursor` | Init with Cursor-specific config (`.cursor/rules.md`) |
| `athena init --ide gemini` | Init with Gemini CLI config (`.gemini/AGENTS.md`) |
| `athena init --ide vscode` | Init with VS Code + Copilot config |
| `athena check` | Basic health check |
| `athena doctor` | Full 15-check system diagnostics |
| `athena doctor --fix` | Auto-repair fixable issues |
| `athena doctor --json` | Machine-readable diagnostics output |
| `athena save "summary"` | Quicksave checkpoint with message |
| `athena --end` | Close session and save |
| `athena --version` | Show version |

## Slash Commands (In-Session)

These commands are used inside your IDE during an active Athena session:

| Command | Effect | Tokens |
|:--------|:-------|:-------|
| `/start` | Boot session — loads identity + JIT routing | ~10K |
| `/end` | Close session — finalize, sync, commit | — |
| `/think` | Escalate reasoning depth | +5K |
| `/ultrathink` | Maximum depth + full context stack | +30K |
| `/brief interview` | Run the initial profiling interview | — |
| `/research` | Deep research loop | — |

> 👉 Full list of all 48 slash commands: [WORKFLOWS.md](WORKFLOWS.md)
