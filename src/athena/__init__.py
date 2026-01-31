"""
Athena SDK
==========

The programmatic core of the Athena Bionic OS.

Modules:
- core: Runtime, identity, and orchestration primitives.
- memory: Context management, vector DB interfaces.
- tools: Agent tool implementations.

Usage:
    python -m athena          # Boot the orchestrator
    python -m athena --end    # Shutdown sequence
    python -m athena --help   # Show help
"""

__version__ = "1.4.0"

# Auto-load environment variables on import
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional for minimal installs
