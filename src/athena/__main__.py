"""
athena.__main__ — CLI Entry Point
==================================

Enables running Athena via: python -m athena

Usage:
    python -m athena              # Boot the orchestrator
    python -m athena init         # Initialize a new workspace
    python -m athena --doctor     # Run system health check
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


def run_doctor():
    """Run system health diagnostics."""
    from athena import __version__

    print("🩺 ATHENA SYSTEM DOCTOR")
    print("=" * 60)
    print(f"   SDK Version: {__version__}")

    # Check for .athena_root marker
    root_marker = Path.cwd() / ".athena_root"
    if root_marker.exists():
        print("   ✅ Workspace marker: Found")
    else:
        print("   ⚠️  Workspace marker: Missing (run `athena init` first)")

    # Check key directories
    dirs_to_check = [".agent", ".context", ".framework"]
    for d in dirs_to_check:
        if (Path.cwd() / d).exists():
            print(f"   ✅ {d}/: Found")
        else:
            print(f"   ❌ {d}/: Missing")

    # Check environment variables
    import os

    env_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "ANTHROPIC_API_KEY"]
    print("\n🔑 Environment Variables:")
    for var in env_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: Set")
        else:
            print(f"   ⚠️  {var}: Not set (optional for cloud features)")

    print("\n" + "=" * 60)
    print("📚 Docs: https://github.com/winstonkoh87/Athena-Public")
    return True


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
    parser.add_argument("--doctor", "-d", action="store_true", help="Run system health check")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root directory (auto-detected if not specified)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init subcommand
    init_parser = subparsers.add_parser("init", help="Initialize a new Athena workspace")
    init_parser.add_argument(
        "target",
        nargs="?",
        type=Path,
        default=None,
        help="Target directory (defaults to current directory)",
    )

    # save subcommand
    save_parser = subparsers.add_parser("save", help="Quicksave checkpoint to session log")
    save_parser.add_argument(
        "summary",
        nargs="*",
        help="Brief summary of the checkpoint",
    )

    args = parser.parse_args()

    if args.version:
        from athena import __version__

        print(f"athena-sdk v{__version__}")
        sys.exit(0)

    if args.doctor:
        run_doctor()
        sys.exit(0)

    if args.command == "init":
        from athena.cli.init import init_workspace

        success = init_workspace(args.target)
        sys.exit(0 if success else 1)

    if args.end:
        from athena.boot.shutdown import run_shutdown

        success = run_shutdown(project_root=args.root)
        sys.exit(0 if success else 1)

    if args.command == "save":
        from athena.cli.save import run_quicksave

        summary = " ".join(args.summary) if args.summary else "Checkpoint"
        success = run_quicksave(summary, project_root=args.root)
        sys.exit(0 if success else 1)

    # Default action: boot
    from athena.boot import create_default_orchestrator

    orchestrator = create_default_orchestrator()
    success = orchestrator.execute(parallel_phases=[4, 5])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
