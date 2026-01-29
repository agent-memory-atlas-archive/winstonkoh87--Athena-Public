#!/usr/bin/env python3
"""
Athena Bootstrap Script
=======================
One-click workspace initialization for Athena.

Usage:
    python bootstrap.py

This script creates the standard Athena directory structure inside the current
repository, copies template files, and prepares a starter configuration.
"""

import shutil
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

DIRECTORIES = [
    ".framework/v8.0/modules",
    ".framework/archive",
    ".context/profile",
    ".context/memories/case_studies",
    ".context/memories/session_logs",
    ".context/memories/patterns",
    ".context/references",
    ".context/specs",
    ".agent/skills/protocols/architecture",
    ".agent/skills/protocols/decision",
    ".agent/skills/protocols/engineering",
    ".agent/skills/protocols/workflow",
    ".agent/skills/capabilities",
    ".agent/workflows",
    ".agent/scripts",
]

TEMPLATE_FILES = {
    "examples/templates/core_identity_template.md": ".framework/v8.0/modules/Core_Identity.md",
    "examples/templates/user_profile_template.md": ".context/profile/User_Profile.md",
    "examples/templates/constraints_template.md": ".context/profile/Constraints_Master.md",
    ".env.example": ".env",
}


def create_directories(base_path: Path) -> None:
    """Create the Athena directory structure."""
    print("📁 Creating directory structure...")
    for directory in DIRECTORIES:
        dir_path = base_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")


def copy_templates(base_path: Path) -> None:
    """Copy template files to their destinations."""
    print("\n📄 Copying template files...")
    for src, dest in TEMPLATE_FILES.items():
        src_path = base_path / src
        dest_path = base_path / dest

        if src_path.exists():
            # Don't overwrite existing files
            if dest_path.exists():
                print(f"   ⏭ {dest} (already exists)")
            else:
                shutil.copy(src_path, dest_path)
                print(f"   ✓ {dest}")
        else:
            print(f"   ⚠ {src} not found, skipping")


def create_starter_files(base_path: Path) -> None:
    """Create minimal starter files if templates are missing."""
    print("\n🔧 Creating starter files...")

    # Create a minimal TAG_INDEX.md
    tag_index = base_path / ".context/TAG_INDEX.md"
    if not tag_index.exists():
        tag_index.write_text("""# TAG_INDEX

> Auto-generated. Run `generate_tag_index.py` to refresh.

## Protocol Tags
| Tag | Files |
|-----|-------|
| #workflow | `start.md`, `end.md` |
| #architecture | `Core_Identity.md` |
""")
        print("   ✓ .context/TAG_INDEX.md")

    # Create a session log template
    session_log = base_path / ".context/memories/session_logs/.gitkeep"
    if not session_log.exists():
        session_log.touch()
        print("   ✓ session_logs/.gitkeep")


def print_summary(base_path: Path) -> None:
    """Print setup summary and next steps."""
    print("\n" + "=" * 60)
    print("✅ ATHENA WORKSPACE INITIALIZED")
    print("=" * 60)
    print(f"""
Workspace: {base_path.absolute()}

📂 Structure Created:
   .framework/   → Core identity and laws
   .context/     → Your memories and profiles
   .agent/       → Skills, workflows, scripts

📋 Next Steps:
   1. Edit .env with your API keys (Supabase, Anthropic, etc.)
   2. Customize .framework/v8.0/modules/Core_Identity.md
   3. Start your first session: Type '/start' in your AI IDE

📚 Documentation:
   - docs/GETTING_STARTED.md
   - docs/ARCHITECTURE.md
   - examples/quickstart/

Happy building! 🚀
""")


def main():
    """Main entry point."""
    base_path = Path.cwd()

    print("=" * 60)
    print("⚡ ATHENA BOOTSTRAP v1.0")
    print("=" * 60)
    print(f"Initializing workspace in: {base_path}\n")

    create_directories(base_path)
    copy_templates(base_path)
    create_starter_files(base_path)
    print_summary(base_path)


if __name__ == "__main__":
    main()
