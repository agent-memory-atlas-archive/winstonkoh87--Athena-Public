"""
athena.core.config
==================

Centralized configuration and path discovery.
"""

from pathlib import Path
from typing import Optional
import os


def get_project_root() -> Path:
    """
    Discover project root by looking for 'pyproject.toml'.
    """
    # Start from this file
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent

    # Fallback to CWD if not found (risky but usually works in dev)
    return Path.cwd()


PROJECT_ROOT = get_project_root()

# Key Directories
AGENT_DIR = PROJECT_ROOT / ".agent"
CONTEXT_DIR = PROJECT_ROOT / ".context"
FRAMEWORK_DIR = PROJECT_ROOT / ".framework"
PUBLIC_DIR = PROJECT_ROOT / "Athena-Public"
SCRIPTS_DIR = AGENT_DIR / "scripts"
MEMORIES_DIR = CONTEXT_DIR / "memories"
SESSIONS_DIR = MEMORIES_DIR / "session_logs"
MEMORY_DIR = PROJECT_ROOT / ".athena" / "memory"
STATE_DIR = AGENT_DIR / "state"
MANIFEST_PATH = STATE_DIR / "sync_manifest.json"
SYSTEM_LEARNINGS_FILE = MEMORY_DIR / "SYSTEM_LEARNINGS.md"
USER_PROFILE_FILE = MEMORY_DIR / "USER_PROFILE.yaml"


# Key Files (Sharded for token efficiency)
TAG_INDEX_AM_PATH = CONTEXT_DIR / "TAG_INDEX_A-M.md"
TAG_INDEX_NZ_PATH = CONTEXT_DIR / "TAG_INDEX_N-Z.md"
CANONICAL_PATH = CONTEXT_DIR / "CANONICAL.md"


def get_current_session_log() -> Optional[Path]:
    """
    Find the most recent session log file (pattern: YYYY-MM-DD-session-XX.md).
    """
    if not SESSIONS_DIR.exists():
        return None

    import re

    pattern = re.compile(r"(\d{4}-\d{2}-\d{2})-session-(\d{2,3})\.md")
    session_files = []

    for f in SESSIONS_DIR.glob("*.md"):
        match = pattern.match(f.name)
        if match:
            date_str, session_num = match.groups()
            session_files.append((date_str, int(session_num), f))

    if not session_files:
        return None

    # Sort by date then session number descending
    session_files.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return session_files[0][2]
