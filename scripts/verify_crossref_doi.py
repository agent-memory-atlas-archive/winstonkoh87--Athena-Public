#!/usr/bin/env python3
"""
scripts/verify_crossref_doi.py
==============================

CLI entry point for Crossref DOI and citation verification.
Can scan individual DOIs or whole markdown / docx files.

Usage:
    python3 scripts/verify_crossref_doi.py 10.1038/s41586-020-2649-2
    python3 scripts/verify_crossref_doi.py --file path/to/paper.md
    python3 scripts/verify_crossref_doi.py --search "attention is all you need vaswani"
"""

import sys
from pathlib import Path

# Ensure src/ is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if not (REPO_ROOT / "src").exists():
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from athena.tools.citation_verifier import main

if __name__ == "__main__":
    sys.exit(main())
