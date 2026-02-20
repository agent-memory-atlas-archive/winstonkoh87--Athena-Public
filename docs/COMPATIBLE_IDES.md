---
created: 2026-02-20
last_updated: 2026-02-20
tags: #compatibility #ide #agents #setup
---

# Compatible IDEs & Coding Agents

> **Purpose**: Athena is model-agnostic and IDE-agnostic. This page lists every coding agent and IDE that can plug into Athena's memory layer — from fully integrated (native config generation) to universally compatible (reads Markdown).
>
> **The rule**: If it can read a Markdown file, it can run Athena.

---

## How Compatibility Works

Athena is a **memory card**, not a game. Any "console" (IDE/agent) that can read files from disk can use it. The `athena init --ide <name>` command generates native configuration files so the agent discovers Athena automatically — but this is a convenience, not a requirement.

```text
┌─────────────────────────────────────────────┐
│  Your IDE / Coding Agent                    │
│                                             │
│  reads → .framework/modules/Core_Identity   │
│  reads → .context/memories/session_logs/    │
│  reads → .agent/workflows/                  │
│  writes → session log on /end               │
│                                             │
│  That's it. That's the integration.         │
└─────────────────────────────────────────────┘
```

---

## Fully Integrated (Native Config Generation)

These agents have first-class support via `athena init`. One command generates the config files your agent expects.

| Coding Agent | Init Command | What Gets Generated | Notes |
|:-------------|:-------------|:--------------------|:------|
| **[Claude Code](https://docs.anthropic.com/en/docs/claude-code)** | `athena init --ide claude` | `CLAUDE.md` + `.claude/agents/cos-*.md` (6 COS sub-agents) | CLI-native, Git-aware, multi-repo reasoning. The reference integration. |
| **[Antigravity](https://antigravity.google/)** | `athena init --ide antigravity` | `AGENTS.md` | Google's VS Code fork with agentic features, built-in browser, Gemini-powered. |
| **[Cursor](https://cursor.com)** | `athena init --ide cursor` | `.cursor/rules.md` | The OG agentic IDE. VS Code-based, full-codebase reasoning, multi-model support. |
| **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** | `athena init --ide gemini` | `.gemini/AGENTS.md` | Terminal-native, Gemini-powered. Lightweight alternative to Claude Code. |
| **[VS Code + GitHub Copilot](https://code.visualstudio.com/)** | `athena init --ide vscode` | `.vscode/settings.json` | Most popular editor. Copilot handles autocomplete; Athena handles memory. |

---

## Planned Integration

These agents are on the roadmap for native `athena init` config generation.

| Coding Agent | Type | Why It's Coming | ETA |
|:-------------|:-----|:----------------|:----|
| **[OpenAI Codex](https://openai.com/index/codex/)** | CLI + VS Code extension | GA since Oct 2025. Cloud sandboxes, PR automation, o-series reasoning. Major player. | Q1 2026 |
| **[Kiro](https://kiro.dev)** | VS Code-based IDE | AWS's spec-driven agentic IDE. Structured workflows with specs and hooks. Enterprise-focused. | Q2 2026 |
| **[Windsurf](https://codeium.com/windsurf)** | VS Code-based IDE | "Cascade" agent indexes your codebase and watches your terminal. Acquired by Cognition. | Q1 2026 |
| **[Zed](https://zed.dev)** | Rust-native editor | Hyper-fast. Not a VS Code fork — built from scratch. Multi-agent workflows via Agent Client Protocol. | Q2 2026 |
| **[Firebase Studio](https://firebase.google.com/studio)** | Browser IDE | Google's cloud-native dev workspace. Gemini-embedded, full-stack. Great for prototyping. | Q2 2026 |
| **[Aider](https://aider.chat)** | CLI | Terminal-native pair programming. Git-aware, multi-model. Popular with CLI-first developers. | Q1 2026 |
| **[Cline](https://github.com/cline/cline)** | VS Code extension | Autonomous coding agent that runs in VS Code. Supports Claude, GPT, Gemini. | Q2 2026 |
| **[Amazon Q Developer](https://aws.amazon.com/q/developer/)** | IDE plugin | AWS's enterprise coding assistant. Integrates with AWS services natively. | Q2 2026 |

---

## Universal Compatibility

**Any agent that can read Markdown files works with Athena.** You don't need `athena init` — just point the agent at:

1. `.framework/modules/Core_Identity.md` — the constitution
2. `.context/memories/session_logs/` — the latest session log
3. `.agent/workflows/` — slash commands

This means tools like **Replit Agent**, **Bolt.new**, **v0.dev**, **Lovable**, and any future agent will work out of the box. The memory layer is plain text — it's universally readable.

---

## Choosing an Agent

| If You Want... | Use |
|:---------------|:----|
| **Maximum agentic power** (CLI) | Claude Code or OpenAI Codex |
| **Familiar VS Code experience** | Cursor, Windsurf, or VS Code + Copilot |
| **Google ecosystem** | Antigravity or Firebase Studio |
| **Enterprise / AWS** | Kiro or Amazon Q Developer |
| **Raw speed** | Zed |
| **Zero-install, browser-only** | [GitHub Codespaces](https://codespaces.new/winstonkoh87/Athena-Public) or Firebase Studio |
| **Free + open source** | Gemini CLI, Aider, or Zed |

> [!TIP]
> **Start with whatever you already use.** Athena's value comes from the memory layer, not the IDE. You can switch agents mid-project and lose nothing — your memory travels with you because it's just Git.

---

## How to Request a New Integration

If your preferred agent isn't listed, open an issue on [GitHub](https://github.com/winstonkoh87/Athena-Public/issues) with:

1. Agent name and link
2. How it reads project config (e.g., `.cursorrules`, `CLAUDE.md`, etc.)
3. Whether it supports MCP (Model Context Protocol)

We'll prioritize based on community demand.
