# Getting Started

> **Last Updated**: 07 January 2026

> Build your own AI assistant in 30 minutes

---

## Prerequisites

- **Terminal access** (macOS Terminal, Windows PowerShell, or Linux)
- **Git** installed ([download here](https://git-scm.com/))
- **An agentic AI IDE** — [Antigravity](https://deepmind.google/), [Cursor](https://cursor.sh/), or similar

---

## Step 1: Create Your Workspace

```bash
# Create and enter your project folder
mkdir MyAssistant && cd MyAssistant

# Initialize git
git init

# Create the core directory structure
mkdir -p .agent/workflows
mkdir -p .agent/scripts
mkdir -p .agent/skills/protocols
mkdir -p .framework/modules
mkdir -p .context/memories/session_logs
```

Your structure should now look like:

```
MyAssistant/
├── .agent/
│   ├── workflows/
│   ├── scripts/
│   └── skills/protocols/
├── .framework/modules/
└── .context/memories/session_logs/
```

### Setup Flow

```mermaid
flowchart LR
    A[Create Workspace] --> B[Define Identity]
    B --> C[Add Workflows]
    C --> D[Enable Scripts]
    D --> E[Test /start]
    E --> F[✅ Ready]
```

---

## Step 2: Define Core Identity

Create `.framework/modules/Core_Identity.md`:

```markdown
# Core Identity

## Who Am I?
An adaptive AI assistant — your strategic co-pilot, not just a chatbot.

## Operating Principles

1. **Memory First**: Log everything. Context is power.
2. **Proactive**: Anticipate needs, don't just react.
3. **Honest**: Challenge flawed assumptions respectfully.
4. **Modular**: One skill = one file. No monoliths.

## Reasoning Standards

- Consider 3+ perspectives before concluding
- Label assumptions explicitly
- Prioritize signal over noise
- Ask clarifying questions when uncertain

## Success Metric

A good conversation contains mutual corrections.
- I challenge your assumptions → you evaluate
- You correct my errors → I improve
- Both get sharper
```

---

## Step 3: Create Your First Workflow

Create `.agent/workflows/start.md`:

```markdown
---
description: Boot the AI assistant with context
---

# /start — Execution Script

## Phase 1: Load Identity
- [ ] Read `.framework/modules/Core_Identity.md`

## Phase 2: Recall Context
- [ ] Find the latest session log in `.context/memories/session_logs/`
- [ ] Display a summary of the last session

## Phase 3: Create New Session
- [ ] Create a new session log with today's date
- [ ] Format: `YYYY-MM-DD-session-XX.md`

## Phase 4: Confirm Ready
- [ ] Output: "⚡ Ready. (Session XX started.)"
```

---

## Step 4: Add Session Logging

Create `.agent/scripts/create_session.py`:

```python
#!/usr/bin/env python3
"""Create a new session log file."""

from datetime import datetime
from pathlib import Path

def create_session():
    log_dir = Path(".context/memories/session_logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find existing sessions for today
    existing = list(log_dir.glob(f"{today}-session-*.md"))
    session_num = len(existing) + 1
    
    filename = f"{today}-session-{session_num:02d}.md"
    filepath = log_dir / filename
    
    template = f"""# Session Log: {today} (Session {session_num})

**Date**: {today}
**Time**: {datetime.now().strftime("%H:%M")} - ...
**Focus**: ...

---

## Key Topics
- ...

---

## Decisions Made
- ...

---

## Action Items
| Action | Owner | Status |
|--------|-------|--------|
| ... | ... | Pending |

---

## Session Closed
**Status**: Open
"""
    
    filepath.write_text(template)
    print(f"✅ Created: {filepath}")
    print(f"   Session: {today}-session-{session_num:02d}")

if __name__ == "__main__":
    create_session()
```

---

## Step 5: Enable Quicksave

Create `.agent/scripts/quicksave.py`:

```python
#!/usr/bin/env python3
"""Append a checkpoint to the current session log."""

import sys
from datetime import datetime
from pathlib import Path

def quicksave(summary: str):
    log_dir = Path(".context/memories/session_logs")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find today's session logs
    logs = sorted(log_dir.glob(f"{today}-session-*.md"))
    if not logs:
        print(f"⚠️ No session log found for {today}")
        return
    
    current_log = logs[-1]  # Most recent
    timestamp = datetime.now().strftime("%H:%M")
    
    checkpoint = f"\n\n### ⚡ Checkpoint [{timestamp}]\n{summary}\n"
    
    with open(current_log, "a") as f:
        f.write(checkpoint)
    
    print(f"✅ Quicksave [{timestamp}] → {current_log.name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        quicksave(" ".join(sys.argv[1:]))
    else:
        print("Usage: python quicksave.py <summary>")
```

---

## Step 6: Create End Workflow

Create `.agent/workflows/end.md`:

```markdown
---
description: Close session and save learnings
---

# /end — Session Close

## Phase 1: Review Checkpoints
- [ ] Read all `### ⚡ Checkpoint` entries from current session log

## Phase 2: Synthesize
- [ ] Fill in session log sections:
  - Key Topics
  - Decisions Made
  - Action Items

## Phase 3: Commit
- [ ] Git add and commit the session log
- [ ] Message format: "Session XX: <brief summary>"

## Phase 4: Confirm
- [ ] Output: "✅ Session XX closed and committed."
```

---

## Step 7: Test It

1. Open your AI IDE in the `MyAssistant` folder
2. Type `/start`
3. Have a conversation
4. Type `/end`

Check `.context/memories/session_logs/` — you should see your session log!

---

## Next Steps

### Add More Workflows

- `/think` — Deep reasoning mode
- `/research` — Multi-source investigation
- `/save` — Manual checkpoint

### Expand Skills

Create protocol files in `.agent/skills/protocols/`:

- `01-problem-decomposition.md`
- `02-multi-path-reasoning.md`

### Customize Identity

Tune `.framework/modules/Core_Identity.md` to match your preferences.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No session log found" | Run `/start` first to create one |
| Scripts don't run | Check Python is installed: `python3 --version` |
| Workflow not recognized | Ensure file is in `.agent/workflows/` |

---

<div align="center">

*You now have a self-improving AI assistant.*

**[Back to README](../README.md)**

</div>
