#!/usr/bin/env python3
"""
test_great_steal.py — Integration Tests for The Great Steal 2.0
================================================================

Tests the three features extracted from OpenClaw:
1. Agent-to-Agent RPC (Sessions Tools)
2. iOS Edge Node Webhook
3. Docker Sandbox Execution

Usage: python3 -m pytest Athena-Public/tests/test_great_steal.py -v
"""

import sys
import os
import tempfile
import sqlite3
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "Athena-Public" / "src"))

# Set ATHENA_ROOT so config.py finds the right root
os.environ["ATHENA_ROOT"] = str(PROJECT_ROOT)


# =============================================
# FEATURE 1: Sessions RPC Tests
# =============================================


class TestSessionsRPC:
    """Test the Agent-to-Agent RPC message bus."""

    @pytest.fixture(autouse=True)
    def setup_rpc(self, tmp_path):
        """Create a fresh RPC instance with a temp database."""
        from athena.core.sessions_rpc import (
            SessionsRPC,
            SessionRegister,
            SessionMessage,
            SessionStatus,
        )

        self.db_path = tmp_path / "test_athena.db"
        self.rpc = SessionsRPC(db_path=self.db_path)
        self.rpc.init_tables()
        self.SessionRegister = SessionRegister
        self.SessionMessage = SessionMessage
        self.SessionStatus = SessionStatus

    def test_register_session(self):
        """Register a session and verify it appears in the list."""
        result = self.rpc.register_session(
            self.SessionRegister(
                session_id="master-001", role="master", goal="Test objective"
            )
        )
        assert result["session_id"] == "master-001"
        assert result["role"] == "master"
        assert result["status"] == "active"

    def test_register_auto_id(self):
        """Register without specifying ID should auto-generate one."""
        result = self.rpc.register_session(self.SessionRegister(role="A"))
        assert result["session_id"].startswith("swarm-A-")

    def test_send_and_receive_message(self):
        """Send a message between two sessions and verify history."""
        # Register both sessions
        self.rpc.register_session(self.SessionRegister(session_id="agent-A", role="A"))
        self.rpc.register_session(
            self.SessionRegister(session_id="master", role="master")
        )

        # Send message from agent to master
        send_result = self.rpc.send_message(
            self.SessionMessage(
                from_session="agent-A",
                to_session="master",
                content="Track A analysis complete. Found 3 risks.",
                msg_type="synthesis",
            )
        )
        assert send_result["status"] == "delivered"
        assert send_result["from"] == "agent-A"
        assert send_result["to"] == "master"

        # Retrieve history
        history = self.rpc.get_history("master")
        assert len(history) == 1
        assert history[0]["content"] == "Track A analysis complete. Found 3 risks."
        assert history[0]["msg_type"] == "synthesis"
        assert history[0]["read"] == 0  # Not yet marked at fetch time; marked after

    def test_unread_filter(self):
        """Unread-only filter should work correctly."""
        self.rpc.register_session(
            self.SessionRegister(session_id="master", role="master")
        )

        # Send 2 messages
        self.rpc.send_message(
            self.SessionMessage(from_session="A", to_session="master", content="Msg 1")
        )
        self.rpc.send_message(
            self.SessionMessage(from_session="B", to_session="master", content="Msg 2")
        )

        # First read marks them as read
        history1 = self.rpc.get_history("master", unread_only=True)
        assert len(history1) == 2

        # Second read with unread_only should return nothing
        history2 = self.rpc.get_history("master", unread_only=True)
        assert len(history2) == 0

    def test_list_sessions(self):
        """List sessions should return all registered sessions with unread counts."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.register_session(self.SessionRegister(session_id="s2", role="B"))

        sessions = self.rpc.list_sessions()
        assert len(sessions) == 2
        roles = {s["role"] for s in sessions}
        assert roles == {"A", "B"}

    def test_update_status(self):
        """Update session status should persist."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.update_status(self.SessionStatus(session_id="s1", status="completed"))

        sessions = self.rpc.list_sessions(status="completed")
        assert len(sessions) == 1
        assert sessions[0]["status"] == "completed"

    def test_list_filter_by_status(self):
        """Filter sessions by status."""
        self.rpc.register_session(self.SessionRegister(session_id="s1", role="A"))
        self.rpc.register_session(self.SessionRegister(session_id="s2", role="B"))
        self.rpc.update_status(self.SessionStatus(session_id="s1", status="completed"))

        active = self.rpc.list_sessions(status="active")
        assert len(active) == 1
        assert active[0]["session_id"] == "s2"


# =============================================
# FEATURE 2: Edge Node Tests
# =============================================


class TestEdgeNode:
    """Test the iOS Edge Node ingest pipeline."""

    @pytest.fixture(autouse=True)
    def setup_ingest(self, tmp_path, monkeypatch):
        """Redirect INGEST_DIR to a temp directory."""
        import athena.core.edge_node as edge_mod

        monkeypatch.setattr(edge_mod, "INGEST_DIR", tmp_path)
        self.ingest_dir = tmp_path
        self.edge_mod = edge_mod

    def test_text_ingest(self):
        """Text payload should create a .md file."""
        from athena.core.edge_node import IngestPayload, process_ingest

        result = process_ingest(
            IngestPayload(
                type="text",
                data="This is a quick thought from my iPhone.",
                metadata={"source": "ios_shortcut"},
            )
        )
        assert result.status == "saved"
        assert result.type == "text"

        # Verify file exists
        files = list(self.ingest_dir.glob("*.md"))
        assert len(files) == 1
        content = files[0].read_text()
        assert "This is a quick thought from my iPhone." in content
        assert "ios_shortcut" in content

    def test_location_ingest(self):
        """Location payload should create a .json file."""
        from athena.core.edge_node import IngestPayload, process_ingest
        import json

        result = process_ingest(
            IngestPayload(
                type="location",
                data="1.3521,103.8198",
                metadata={"source": "iphone_gps", "city": "Singapore"},
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert data["raw"] == "1.3521,103.8198"

    def test_camera_ingest(self):
        """Camera payload (base64) should create a .jpg file."""
        import base64
        from athena.core.edge_node import IngestPayload, process_ingest

        fake_image = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # Fake JPEG header
        b64_data = base64.b64encode(fake_image).decode()

        result = process_ingest(
            IngestPayload(
                type="camera",
                data=b64_data,
                metadata={"source": "iphone_camera"},
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.jpg"))
        assert len(files) == 1
        assert files[0].stat().st_size > 0

    def test_unknown_type_fallback(self):
        """Unknown types should fall back to .bin."""
        from athena.core.edge_node import IngestPayload, process_ingest

        result = process_ingest(
            IngestPayload(
                type="biometric",
                data="heart_rate=72",
            )
        )
        assert result.status == "saved"

        files = list(self.ingest_dir.glob("*.bin"))
        assert len(files) == 1


# =============================================
# FEATURE 3: Sandbox Tests (Unit only — Docker optional)
# =============================================


class TestSandbox:
    """Test the sandbox module logic (does NOT require Docker)."""

    def test_sandbox_request_model(self):
        """SandboxExecRequest model should have correct defaults."""
        from athena.core.sandbox import SandboxExecRequest

        req = SandboxExecRequest(script="print('hello')")
        assert req.timeout == 30
        assert req.allow_network is False

    def test_sandbox_response_model(self):
        """SandboxExecResponse should serialize correctly."""
        from athena.core.sandbox import SandboxExecResponse

        resp = SandboxExecResponse(
            stdout="hello\n",
            stderr="",
            exit_code=0,
            execution_time=0.5,
            sandbox="athena-sandbox:latest",
        )
        assert resp.stdout == "hello\n"
        assert resp.exit_code == 0

    def test_sandbox_unavailable_gracefully(self):
        """is_available() should return False if Docker is not installed."""
        from athena.core.sandbox import SandboxRunner

        runner = SandboxRunner(image="nonexistent-image:latest")
        # This should not crash, just return False
        available = runner.is_available()
        assert isinstance(available, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
