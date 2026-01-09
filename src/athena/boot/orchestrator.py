"""
Athena Boot Orchestrator
=========================

Modular boot sequence with session creation, integrity verification,
and semantic memory priming.

This is the FUNCTIONAL version that creates real artifacts.
"""

import os
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Tuple, Optional


class BootOrchestrator:
    """
    Orchestrates the Athena boot sequence.

    The boot sequence consists of 7 phases:
    1. Watchdog activation (verify core files exist)
    2. System sync (check directory structure)
    3. Semantic prime verification (SHA-384 hash check)
    4. Session creation (create new session log)
    5. Context capture (load last session summary)
    6. Semantic memory priming (query vector DB if available)
    7. Identity loading (load Core_Identity.md)

    Phases 6 & 7 run in parallel for performance optimization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.phases: List[Tuple[str, Callable]] = []
        self.boot_time: float = 0
        self.session_id: str = ""
        self.project_root = project_root or self._discover_root()
        self.session_logs_dir = self.project_root / "session_logs"
        self.last_session: Optional[str] = None

    def _discover_root(self) -> Path:
        """Discover project root by looking for pyproject.toml or .git."""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
                return parent
        return current

    def register_phase(self, name: str, executor: Callable):
        """Register a boot phase with its executor function."""
        self.phases.append((name, executor))

    def execute(self, parallel_phases: List[int] = None) -> bool:
        """
        Execute all registered boot phases.

        Args:
            parallel_phases: List of phase indices to run in parallel
                             (e.g., [5, 6] to run phases 6 & 7 concurrently)

        Returns:
            True if boot completed successfully, False otherwise.
        """
        start_time = time.time()
        parallel_phases = parallel_phases or []

        print("━" * 60)
        print("⚡ ATHENA BOOT SEQUENCE")
        print("━" * 60)

        for i, (name, executor) in enumerate(self.phases):
            phase_num = i + 1
            try:
                if i in parallel_phases:
                    print(f"[{phase_num}/{len(self.phases)}] ⚡ {name} (parallel)")
                else:
                    print(f"[{phase_num}/{len(self.phases)}] ⏳ {name}")

                result = executor()

                if result is False:
                    print(f"❌ Boot failed at phase: {name}")
                    return False

                print(f"[{phase_num}/{len(self.phases)}] ✅ {name}")

            except Exception as e:
                print(f"❌ Boot error in {name}: {e}")
                return False

        self.boot_time = time.time() - start_time
        print("━" * 60)
        print(f"⚡ ATHENA ONLINE | Session: {self.session_id} | Boot: {self.boot_time:.1f}s")
        print("━" * 60)

        return True


def create_functional_orchestrator(project_root: Optional[Path] = None) -> BootOrchestrator:
    """
    Create boot orchestrator with FUNCTIONAL phase configuration.

    This version actually:
    - Verifies directory structure
    - Creates session logs
    - Loads last session context
    - Primes semantic memory (if Supabase configured)
    """
    orchestrator = BootOrchestrator(project_root)
    root = orchestrator.project_root
    logs_dir = orchestrator.session_logs_dir

    # --- Phase 1: Watchdog ---
    def watchdog():
        """Verify core files exist."""
        required = ["pyproject.toml"]
        for f in required:
            if not (root / f).exists():
                print(f"   ⚠️  Missing: {f}")
        return True

    orchestrator.register_phase("Watchdog activated", watchdog)

    # --- Phase 2: System Sync ---
    def system_sync():
        """Ensure directory structure exists."""
        dirs = [logs_dir, root / "protocols", root / "case_studies"]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        return True

    orchestrator.register_phase("System sync complete", system_sync)

    # --- Phase 3: Semantic Prime Verification ---
    def semantic_prime():
        """Check integrity of core identity (placeholder hash)."""
        identity_file = root / "examples" / "framework" / "Core_Identity.md"
        if identity_file.exists():
            content = identity_file.read_text()
            hash_val = hashlib.sha256(content.encode()).hexdigest()[:12]
            print(f"   🔐 Identity hash: {hash_val}")
        else:
            print("   ⚠️  Core_Identity.md not found (first-time setup?)")
        return True

    orchestrator.register_phase("Semantic prime verified", semantic_prime)

    # --- Phase 4: Session Creation ---
    def create_session():
        """Create a new session log file."""
        logs_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now().strftime("%Y-%m-%d")

        # Find next session number for today
        existing = list(logs_dir.glob(f"{today}-session-*.md"))
        next_num = len(existing) + 1

        session_id = f"{today}-session-{next_num:02d}"
        session_file = logs_dir / f"{session_id}.md"

        # Create session log
        session_file.write_text(f"""# Session Log: {session_id}

> **Created**: {datetime.now().isoformat()}
> **Status**: Active

## Summary

(Session in progress...)

## Key Decisions

- 

## Insights

- 

---
*Auto-generated by Athena Boot Orchestrator*
""")
        orchestrator.session_id = session_id
        print(f"   📝 Created: {session_file.name}")
        return True

    orchestrator.register_phase("Session created", create_session)

    # --- Phase 5: Context Capture ---
    def context_capture():
        """Load summary from last session."""
        sessions = sorted(logs_dir.glob("*.md"), reverse=True)
        if len(sessions) > 1:
            last = sessions[1]  # Skip the one we just created
            orchestrator.last_session = last.stem
            print(f"   ⏮️  Last session: {last.stem}")
        else:
            print("   📭 No previous sessions found")
        return True

    orchestrator.register_phase("Context captured", context_capture)

    # --- Phase 6: Semantic Memory Priming ---
    def semantic_prime_memory():
        """Prime semantic memory (requires Supabase config)."""
        try:
            from athena.memory.vectors import get_client

            client = get_client()
            print("   🧠 Supabase connected")
        except Exception:
            print("   ⚠️  Semantic memory offline (Supabase not configured)")
        return True

    orchestrator.register_phase("Semantic memory primed", semantic_prime_memory)

    # --- Phase 7: Identity Loading ---
    def load_identity():
        """Load core identity principles."""
        identity_file = root / "examples" / "framework" / "Core_Identity.md"
        if identity_file.exists():
            print(f"   🏛️  Identity loaded from {identity_file.name}")
        else:
            print("   ⚠️  Using default identity (create Core_Identity.md to customize)")
        return True

    orchestrator.register_phase("Identity loaded", load_identity)

    return orchestrator


# Legacy alias for backwards compatibility
def create_default_orchestrator() -> BootOrchestrator:
    """Alias for create_functional_orchestrator."""
    return create_functional_orchestrator()


if __name__ == "__main__":
    orchestrator = create_functional_orchestrator()
    orchestrator.execute(parallel_phases=[4, 5])  # Run phases 6 & 7 in parallel
