#!/usr/bin/env python3
"""
verify_canon_citations.py — Canonical Citation Verifier
=======================================================

Scans markdown files for `§NNN` citations and verifies each one resolves
to an actual named entry in CANONICAL.md. § numbers represent line numbers,
which can shift on edits, making them fragile references.

Known limitation: Protocol files use §NNN to reference Law numbers (e.g.,
§0 = Law #0), not CANONICAL line numbers. Use --min-ref 50 to suppress
these false positives (CANONICAL table entries start around line 50+).

Usage:
    python3 .agent/scripts/verify_canon_citations.py --all
    python3 .agent/scripts/verify_canon_citations.py --all --min-ref 50
    python3 .agent/scripts/verify_canon_citations.py file1.md file2.md
    python3 .agent/scripts/verify_canon_citations.py --all --fix-suggestions
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONTEXT_DIR = PROJECT_ROOT / ".context"
CANONICAL_FILE = CONTEXT_DIR / "CANONICAL.md"

def load_canonical_lines() -> List[str]:
    """Load CANONICAL.md lines, padding index 0 so indices match line numbers."""
    if not CANONICAL_FILE.exists():
        print(f"Error: {CANONICAL_FILE} not found.", file=sys.stderr)
        sys.exit(1)
    with open(CANONICAL_FILE, "r", encoding="utf-8") as f:
        return [""] + f.read().splitlines()

def parse_canonical_entry(line: str) -> Optional[dict]:
    """Parse a CANONICAL.md table row. Returns a dict if valid, else None."""
    line = line.strip()
    if not line.startswith("|"):
        return None
    # Skip separator lines
    if re.match(r"^\|\s*:?-+.*\|", line):
        return None
    
    parts = [p.strip() for p in line.split("|")]
    if len(parts) < 3:
        return None
        
    name = parts[1].replace("**", "").strip()
    if not name or name in ["Metric", "Framework", "Law", "Decision"]:
        return None
    
    # Try to extract session
    session = None
    session_match = re.search(r"\b(S\d+)\b", line)
    if session_match:
        session = session_match.group(1)
    else:
        # Look for Session \d+
        session_match = re.search(r"Session\s+(\d+)", line, re.IGNORECASE)
        if session_match:
            session = f"S{session_match.group(1)}"
            
    # Try to extract fingerprint
    fp = None
    fp_match = re.search(r"fp:\s*([a-f0-9]+)", line, re.IGNORECASE)
    if fp_match:
        fp = fp_match.group(1)
        
    return {
        "name": name,
        "session": session,
        "fp": fp
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Verify §NNN citations in markdown files.")
    parser.add_argument("files", nargs="*", type=Path, help="Markdown files to scan")
    parser.add_argument("--all", action="store_true", help="Scan .context/ and .agent/ recursively for .md files")
    parser.add_argument("--fix-suggestions", action="store_true", help="Output recommended replacement text")
    parser.add_argument("--min-ref", type=int, default=0, help="Skip §NNN where NNN < this value (use 50 to suppress protocol Law # self-refs)")
    
    args = parser.parse_args()
    
    if not args.files and not args.all:
        parser.print_help()
        return 1
        
    files_to_scan = []
    if args.all:
        for d in [PROJECT_ROOT / ".context", PROJECT_ROOT / ".agent"]:
            if d.exists():
                files_to_scan.extend(d.rglob("*.md"))
    else:
        for f in args.files:
            f_path = Path(f)
            if f_path.is_file():
                files_to_scan.append(f_path)
            else:
                f_path = PROJECT_ROOT / f
                if f_path.is_file():
                    files_to_scan.append(f_path)
                else:
                    print(f"Warning: File {f} not found.", file=sys.stderr)
                    
    # Remove duplicates
    files_to_scan = list(set([f.resolve() for f in files_to_scan]))
    
    if not files_to_scan:
        print("No files to scan.", file=sys.stderr)
        return 0
        
    canonical_lines = load_canonical_lines()
    max_line = len(canonical_lines) - 1
    
    citation_pattern = re.compile(r"§(\d+)")
    has_invalid = False
    
    for md_file in sorted(files_to_scan):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content_lines = f.readlines()
        except Exception as e:
            print(f"Error reading {md_file}: {e}", file=sys.stderr)
            continue
            
        try:
            rel_path = md_file.relative_to(PROJECT_ROOT)
        except ValueError:
            rel_path = md_file
        
        for i, line in enumerate(content_lines, 1):
            matches = citation_pattern.finditer(line)
            for match in matches:
                line_num_str = match.group(1)
                cited_line_num = int(line_num_str)
                
                if cited_line_num < args.min_ref:
                    continue
                
                if 1 <= cited_line_num <= max_line:
                    canon_line = canonical_lines[cited_line_num]
                    entry = parse_canonical_entry(canon_line)
                    
                    if entry:
                        name = entry["name"]
                        session = entry["session"]
                        fp = entry["fp"]
                        
                        ref_parts = []
                        if session:
                            ref_parts.append(session)
                        if fp:
                            ref_parts.append(f"fp: {fp}")
                            
                        ref_str = f" ({', '.join(ref_parts)})" if ref_parts else ""
                        print(f"{rel_path}:{i}  §{cited_line_num} → VALID: '{name}'{ref_str}")
                        
                        if args.fix_suggestions:
                            sugg_ref_parts = []
                            if session:
                                sugg_ref_parts.append(session)
                            if fp:
                                sugg_ref_parts.append(f"fp: {fp[:8]}")
                            sugg_ref_str = f" ({', '.join(sugg_ref_parts)})" if sugg_ref_parts else ""
                            
                            # Shorten name roughly for suggestion
                            short_name = name.split('&')[0].strip() if '&' in name else name
                            if len(short_name) > 30:
                                short_name = short_name[:27] + "..."
                                
                            print(f"  ⚠️  Fragile: §{cited_line_num} is a line number that shifts on edits. Recommend: '{short_name}{sugg_ref_str}'")
                    else:
                        print(f"{rel_path}:{i}  §{cited_line_num} → INVALID: line {cited_line_num} does not contain a named entry in CANONICAL.md")
                        has_invalid = True
                else:
                    print(f"{rel_path}:{i}  §{cited_line_num} → INVALID: line {cited_line_num} does not exist in CANONICAL.md")
                    has_invalid = True
                    
    return 1 if has_invalid else 0

if __name__ == "__main__":
    sys.exit(main())
