"""
Athena Governance Engine

Enforces the Triple-Lock protocol (Semantic Search → Web Search → Quicksave)
to ensure all AI interactions are properly grounded before checkpointing.

Includes Doom Loop Detection (stolen from OpenCode, Feb 2026):
If the same tool call repeats 3+ times with identical input, flag it.
"""

import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("athena.governance")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DOOM_LOOP_THRESHOLD = 3  # Number of identical calls before flagging
DOOM_LOOP_WINDOW = 60  # Seconds — only count repeats within this window


# ---------------------------------------------------------------------------
# Doom Loop Detector (Stolen from OpenCode, Feb 2026)
# ---------------------------------------------------------------------------


class DoomLoopDetector:
    """
    Detects infinite retry loops where the same tool call is repeated
    with identical arguments. This is a circuit breaker for token-burning
    agentic failures.

    Origin: OpenCode (anomalyco/opencode, 109K stars)
    Athena Integration: Feb 2026 (Session 05)
    """

    def __init__(
        self, threshold: int = DOOM_LOOP_THRESHOLD, window: int = DOOM_LOOP_WINDOW
    ):
        self.threshold = threshold
        self.window = window
        self._history: List[Dict[str, Any]] = []
        self._violations: int = 0

    @staticmethod
    def _hash_args(args: Any) -> str:
        """Create a deterministic hash of tool call arguments."""
        try:
            serialized = json.dumps(args, sort_keys=True, default=str)
        except (TypeError, ValueError):
            serialized = str(args)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    def record(self, tool_name: str, args: Any = None) -> bool:
        """
        Record a tool call and check for doom loop.

        Returns True if a doom loop is detected (same tool+args repeated
        >= threshold times within the time window).
        """
        now = time.time()
        args_hash = self._hash_args(args)
        signature = f"{tool_name}:{args_hash}"

        # Prune old entries outside the window
        self._history = [
            entry for entry in self._history if now - entry["timestamp"] <= self.window
        ]

        # Add current call
        self._history.append(
            {
                "signature": signature,
                "tool": tool_name,
                "args_hash": args_hash,
                "timestamp": now,
            }
        )

        # Count occurrences of this signature in the window
        count = sum(1 for e in self._history if e["signature"] == signature)

        if count >= self.threshold:
            self._violations += 1
            logger.warning(
                "🔴 DOOM LOOP DETECTED: '%s' called %d times with identical args "
                "(hash: %s). Violation #%d.",
                tool_name,
                count,
                args_hash,
                self._violations,
            )
            return True

        return False

    def get_stats(self) -> Dict[str, Any]:
        """Return doom loop detection statistics."""
        return {
            "total_violations": self._violations,
            "history_size": len(self._history),
            "threshold": self.threshold,
            "window_seconds": self.window,
        }

    def reset(self):
        """Clear history (e.g., on session end)."""
        self._history.clear()


# ---------------------------------------------------------------------------
# Governance Engine
# ---------------------------------------------------------------------------


class GovernanceEngine:
    """
    Governance Engine for Project Athena.
    Enforces autonomic Triple-Lock protocol (Search → Web → Save)
    and Doom Loop Detection.

    The Triple-Lock ensures:
    1. Semantic Search: Query the knowledge base before responding
    2. Web Research: External grounding when applicable
    3. Quicksave: Checkpoint the session with verified context

    Doom Loop Detection (Law #1 extension):
    Prevents infinite retry loops that burn tokens without progress.
    """

    def __init__(self, state_dir: Path = None):
        if state_dir is None:
            # Backward compat: try importing AGENT_DIR, fall back to ~/.athena
            try:
                from athena.core.config import AGENT_DIR

                self.state_dir = AGENT_DIR / "state"
            except ImportError:
                self.state_dir = Path.home() / ".athena" / "state"
        else:
            self.state_dir = state_dir
        self.state_file = self.state_dir / "exchange_state.json"
        self._state: Dict[str, Any] = self._load_state()

        # Doom Loop Detector
        self.doom_loop = DoomLoopDetector()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception:
                pass
        return {
            "semantic_search_performed": False,
            "web_search_performed": False,
            "last_search_time": 0,
        }

    def _save_state(self):
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.state_file.write_text(json.dumps(self._state))
        except Exception:
            pass

    def mark_search_performed(self, query: str):
        """Register that a semantic search was performed for the current turn."""
        self._state["semantic_search_performed"] = True
        self._state["last_search_time"] = time.time()
        self._save_state()

    def mark_web_search_performed(self, query: str):
        """Register that a web search was performed for the current turn."""
        self._state["web_search_performed"] = True
        self._save_state()

    def record_tool_call(self, tool_name: str, args: Any = None) -> bool:
        """
        Record a tool call for doom loop detection.
        Returns True if a doom loop is detected.
        """
        return self.doom_loop.record(tool_name, args)

    def verify_exchange_integrity(self) -> bool:
        """
        Verify if the Triple-Lock protocols were followed.
        Returns True if both Semantic Search AND Web Search were performed.
        Resets state after check.
        """
        semantic = self._state.get("semantic_search_performed", False)
        web = self._state.get("web_search_performed", False)

        integrity = semantic and web

        # Reset for next turn
        self._state["semantic_search_performed"] = False
        self._state["web_search_performed"] = False
        self._save_state()

        return integrity

    def get_integrity_score(self) -> float:
        """
        Calculate current integrity score based on protocol compliance.
        Returns 1.0 if Triple-Lock is satisfied, 0.0 otherwise.
        """
        semantic = self._state.get("semantic_search_performed", False)
        web = self._state.get("web_search_performed", False)
        return 1.0 if (semantic and web) else 0.0

    def get_status(self) -> Dict[str, Any]:
        """Return full governance status including doom loop stats."""
        return {
            "triple_lock": {
                "semantic_search": self._state.get("semantic_search_performed", False),
                "web_search": self._state.get("web_search_performed", False),
                "integrity_score": self.get_integrity_score(),
            },
            "doom_loop": self.doom_loop.get_stats(),
        }


# Singleton instance (lazy)
_governance_engine = None


def get_governance() -> GovernanceEngine:
    """Get the singleton governance engine instance."""
    global _governance_engine
    if _governance_engine is None:
        _governance_engine = GovernanceEngine()
    return _governance_engine
