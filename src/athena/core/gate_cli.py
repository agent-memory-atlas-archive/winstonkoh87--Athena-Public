"""
src/athena/core/gate_cli.py — CLI entrypoint for AgentGate pre-action interception.
=================================================================================
Allows IDEs, middleware, and subagents to execute deterministic tool interception.
Accepts tool_name and args via CLI arguments or JSON stdin.
Exits 0 if allowed; exits 1 with veto explanation on stderr if blocked.
"""

import json
import sys
from pathlib import Path

from athena.core.gate import AgentGate


def main() -> int:
    gate = AgentGate(Path("."))
    tool_name = "generic"
    args: dict = {}

    if len(sys.argv) > 1:
        tool_name = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            args = json.loads(sys.argv[2])
        except Exception:
            args = {"command": " ".join(sys.argv[2:])}
    elif not sys.stdin.isatty():
        try:
            content = sys.stdin.read().strip()
            if content:
                data = json.loads(content)
                if isinstance(data, dict):
                    raw_tool = data.get("tool_name", data.get("tool", tool_name))
                    if raw_tool is not None:
                        tool_name = str(raw_tool)
                    raw_args = data.get("args", data.get("parameters", data))
                    if isinstance(raw_args, dict):
                        args = raw_args
        except Exception:
            pass

    allowed, reason = gate.intercept_tool(tool_name, args)
    if not allowed:
        print(f"[AgentGate VETO] {reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
