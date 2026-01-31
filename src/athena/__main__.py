"""
athena.__main__ — CLI Entry Point
==================================

Enables running Athena via: python -m athena

Usage:
    python -m athena              # Boot the orchestrator
    python -m athena --version    # Show version
    python -m athena --help       # Show help
"""

import argparse
import sys
from pathlib import Path

# Load environment variables FIRST (critical fix)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional for minimal installs


def main():
    parser = argparse.ArgumentParser(
        prog="athena",
        description="Athena Bionic OS — Personal AI Operating System with Memory",
    )
    parser.add_argument("--version", "-v", action="store_true", help="Show version and exit")
    parser.add_argument(
        "--boot", "-b", action="store_true", help="Run the boot orchestrator (default action)"
    )
    parser.add_argument("--end", "-e", action="store_true", help="Run the shutdown sequence")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root directory (auto-detected if not specified)",
    )

    args = parser.parse_args()

    if args.version:
        from athena import __version__

        print(f"athena-sdk v{__version__}")
        sys.exit(0)

    if args.end:
        from athena.boot.shutdown import run_shutdown

        success = run_shutdown(project_root=args.root)
        sys.exit(0 if success else 1)

    # Default action: boot
    from athena.boot import create_default_orchestrator

    orchestrator = create_default_orchestrator()
    success = orchestrator.execute(parallel_phases=[4, 5])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
