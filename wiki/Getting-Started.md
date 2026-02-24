# 🚀 Getting Started

Boot your own AI Operating System in 5 minutes.

*Last Updated: 2026-02-25 · v9.2.4*

---

## Option A: Cloud (Fastest — Zero Setup)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/winstonkoh87/Athena-Public)

1. Click the badge above.
2. Wait for the cloud environment to build (~2 minutes).
3. Type `/start` in the terminal.

> No Python, no GPU required. Runs entirely in the cloud.

---

## Option B: Local Install (Recommended)

### Step 1: Clone the repo

```bash
git clone https://github.com/winstonkoh87/Athena-Public.git MyAgent
cd MyAgent
```

### Step 2: Open in your AI IDE

| IDE | How to Init |
|:----|:------------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `athena init --ide claude` |
| [Antigravity](https://antigravity.google/) | `athena init --ide antigravity` |
| [Cursor](https://cursor.com) | `athena init --ide cursor` |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `athena init --ide gemini` |
| [VS Code + Copilot](https://code.visualstudio.com/) | `athena init --ide vscode` |
| [Kilo Code](https://kilocode.ai/) | `athena init --ide kilocode` |
| [Roo Code](https://roocode.com/) | `athena init --ide roocode` |

Or just open the folder and type `/start` — no init required for basic use.

### Step 3: Run the interview

Type `/brief interview` on your first session. Athena asks about **you** — name, goals, decision style, blind spots — and builds a personal profile that makes every future session compound.

> **Everything stays local.** Your profile is stored as a Markdown file on your machine (`user_profile.md`). No cloud. No tracking.

> See [Your First Session](https://github.com/winstonkoh87/Athena-Public/blob/main/docs/YOUR_FIRST_SESSION.md) for the full onboarding guide — including the guiding question that shapes your entire Athena experience.

---

## Workspace Modes

Athena is your **Brain**. Your project is the **Body**. They don't need to live in the same place.

| Mode | Setup | Best For |
|:-----|:------|:---------|
| **Standalone** | Open `Athena/` as your workspace | Personal brain, all-in-one users |
| **Multi-Root (Sidecar)** | `File → Add Folder to Workspace` → select `Athena/` | Devs with existing repos |
| **Nested** | Drop your project folder inside `Athena/` | Quick prototypes, small projects |

**Recommendation**: Start with **Standalone**. If you need your project visible in the same window, use **Multi-Root**.

---

## CLI Commands

```bash
pip install -e .              # Install SDK
athena                        # Boot session
athena init .                 # Initialize workspace in current directory
athena init --ide claude      # Init with Claude Code agents + CLAUDE.md
athena check                  # Basic health check
athena doctor                 # Full 15-check system diagnostics
athena doctor --fix           # Auto-repair fixable issues
athena save "summary"         # Quicksave checkpoint
athena --end                  # Close session and save
athena --version              # Show version (v9.2.1)
```

---

## Prerequisites (Optional)

The quickstart needs **zero configuration**. These are only needed for advanced cloud features:

```bash
# Required for cloud features
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional (for multi-model validation)
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-api-key
OPENAI_API_KEY=your-openai-key
```

```bash
cp .env.example .env
# Add your keys
```

---

## Import Existing Data

Athena's memory is just Markdown files. Any text you can export becomes part of your memory:

| Source | How to Import |
|:-------|:-------------|
| **ChatGPT** | Settings → Data Controls → Export → Copy `.md` files into `.context/memories/imports/` |
| **Gemini** | [Google Takeout](https://takeout.google.com/) → Select "Gemini Apps" → Extract into `.context/memories/imports/` |
| **Claude** | Settings → Export Data → Copy transcripts into `.context/memories/imports/` |
| **Any Markdown** | Drop `.md` files into `.context/memories/` — indexed on next `/start` |

After importing, run `athena check` to verify files are detected.

---

## Next Steps

- Try the **[Workflow Reference](Workflow-Reference)** for advanced commands.
- Read the **[Architecture Overview](Architecture-Overview)** to understand the OS layers.
- **Customize your AI's identity** — edit `.framework/v8.2-stable/modules/Core_Identity.md` to set your own laws and rules.
- Explore the **[Use Cases](Use-Cases)** to see what Athena can do.
- Check the **[FAQ](FAQ)** for common questions.
