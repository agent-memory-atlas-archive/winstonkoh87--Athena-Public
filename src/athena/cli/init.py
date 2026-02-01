#!/usr/bin/env python3
"""
athena.cli.init
===============

Scaffold a new Athena workspace with directory structure and templates.
Fulfills the "5-Minute Quickstart" promise.

Usage:
    python -m athena init [target_dir]
"""

from datetime import datetime
from pathlib import Path


# --- Templates ---

CORE_IDENTITY_TEMPLATE = """# Core Identity

> **Created**: {date}

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
"""

START_WORKFLOW_TEMPLATE = """---
description: Boot the AI assistant with context
---

# /start — Execution Script

> **Automation**: This workflow runs the Athena SDK boot sequence.

## Execution

// turbo

```bash
python -m athena
```

The boot sequence will:
1. Load Core Identity
2. Recall last session context
3. Create a new session log
4. Confirm ready status

## Manual Override (if SDK unavailable)

- [ ] Read `.framework/modules/Core_Identity.md`
- [ ] Find the latest session log in `.context/memories/session_logs/`
- [ ] Create a new session log: `YYYY-MM-DD-session-XX.md`
- [ ] Output: "⚡ Ready. (Session XX started.)"
"""

END_WORKFLOW_TEMPLATE = """---
description: Close session and save learnings
---

# /end — Session Close

> **Automation**: This workflow runs the Athena SDK shutdown sequence.

## Execution

// turbo

```bash
python -m athena --end
```

The shutdown sequence will:
1. Close the current session log
2. Update session status to "Closed"
3. Optionally trigger Supabase sync

## Manual Override (if SDK unavailable)

- [ ] Read all `### ⚡ Checkpoint` entries from current session log
- [ ] Fill in Key Topics, Decisions Made, Action Items
- [ ] Git add and commit the session log
- [ ] Output: "✅ Session XX closed and committed."
"""

SAVE_WORKFLOW_TEMPLATE = """---
description: Save a checkpoint to the current session
---

# /save — Quicksave Checkpoint

> **Automation**: This workflow runs the Athena SDK save command.

## Execution

// turbo

```bash
python -m athena save "Brief summary of what happened"
```

The save command will append a timestamped checkpoint to the current session log.
"""


PROJECT_STATE_TEMPLATE = """---
created: '{date}'
last_updated: '{date}'
framework_version: v1.0.0
---

# Project State (Single Source of Truth)

## 1. System Status

- **Health**: 100%
- **Session Count**: 0
- **Last Session**: None

## 2. Recent Changes

- [{date}] Initialized Athena workspace via `athena init`.

## 3. Notes

_Add project-specific notes here._
"""


def init_workspace(target_dir: Path = None) -> bool:
    """
    Initialize an Athena workspace with the required directory structure.

    Args:
        target_dir: Directory to initialize. Defaults to current directory.

    Returns:
        True if successful, False otherwise.
    """
    root = target_dir or Path.cwd()
    root = Path(root).resolve()

    print("🏛️  ATHENA INIT")
    print(f"   Target: {root}")
    print("=" * 60)

    # Define structure
    directories = [
        ".agent/workflows",
        ".agent/scripts",
        ".agent/skills/protocols",
        ".framework/modules",
        ".context/memories/session_logs",
        ".context/data",
    ]

    # Create directories
    print("\n📁 Creating directories...")
    for dir_path in directories:
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {dir_path}/")

    # Create root marker (for path discovery)
    marker_path = root / ".athena_root"
    marker_path.write_text(f"# Athena Workspace\nCreated: {datetime.now().isoformat()}\n")
    print("   ✅ .athena_root (workspace marker)")

    # Create template files
    today = datetime.now().strftime("%Y-%m-%d")

    templates = [
        (
            ".framework/modules/Core_Identity.md",
            CORE_IDENTITY_TEMPLATE.format(date=today),
        ),
        (".agent/workflows/start.md", START_WORKFLOW_TEMPLATE),
        (".agent/workflows/end.md", END_WORKFLOW_TEMPLATE),
        (".agent/workflows/save.md", SAVE_WORKFLOW_TEMPLATE),
        (
            ".context/project_state.md",
            PROJECT_STATE_TEMPLATE.format(date=today),
        ),
    ]

    print("\n📝 Creating template files...")
    for file_path, content in templates:
        full_path = root / file_path
        if not full_path.exists():
            full_path.write_text(content)
            print(f"   ✅ {file_path}")
        else:
            print(f"   ⏭️  {file_path} (already exists)")

    # Summary
    print("\n" + "=" * 60)
    print("✅ ATHENA WORKSPACE INITIALIZED")
    print("=" * 60)
    print("\n🚀 Next steps:")
    print("   1. Open this folder in your AI IDE (Antigravity, Cursor, etc.)")
    print('   2. Type "/start" to boot your agent')
    print('   3. Work with your agent, then type "/end" to save')
    print("\n📚 Docs: https://github.com/winstonkoh87/Athena-Public/docs/GETTING_STARTED.md")

    return True


if __name__ == "__main__":
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    init_workspace(target)
