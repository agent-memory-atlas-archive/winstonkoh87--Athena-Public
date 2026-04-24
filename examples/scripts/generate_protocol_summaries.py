#!/usr/bin/env python3
"""
Auto-generate PROTOCOL_SUMMARIES.md from protocol frontmatter.
Replaces the manually-maintained version that drifts within 14 days.

Walks .agent/skills/protocols/<category>/<file>.md, extracts:
  - Protocol number (from filename or frontmatter)
  - Description (from frontmatter or first heading)
  - Category (from directory name)

Output: .context/PROTOCOL_SUMMARIES.md
"""

import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROTOCOLS_DIR = REPO_ROOT / ".agent" / "skills" / "protocols"
OUTPUT_FILE = REPO_ROOT / ".context" / "PROTOCOL_SUMMARIES.md"


def extract_frontmatter(filepath: Path) -> dict:
    """Extract YAML-ish frontmatter from a markdown file."""
    content = filepath.read_text(errors="ignore")
    fm = {}

    # Find frontmatter block(s) — handle double-frontmatter files
    blocks = re.findall(r"^---\s*\n(.*?)^---\s*\n", content, re.MULTILINE | re.DOTALL)
    for block in blocks:
        for line in block.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip().lower()
                val = val.strip().strip("\"'")
                if key and val:
                    fm[key] = val

    # Extract first heading as fallback name
    heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if heading_match:
        fm.setdefault("heading", heading_match.group(1).strip())

    return fm


def extract_protocol_name(filename: str, frontmatter: dict) -> str:
    """Derive a human-readable protocol name from filename or frontmatter."""
    # Try frontmatter heading first
    if "heading" in frontmatter:
        return frontmatter["heading"]

    # Fall back to filename
    name = filename.replace(".md", "")
    # Strip leading numbers and dashes
    name = re.sub(r"^\d+-", "", name)
    # Convert kebab-case to title
    return name.replace("-", " ").title()


def extract_protocol_number(filename: str) -> str:
    """Extract protocol number from filename like '075-synthetic-parallel.md'."""
    match = re.match(r"^(\d+)", filename)
    return match.group(1) if match else ""


def build_summary(filepath: Path, category: str) -> dict:
    """Build a summary record for one protocol file."""
    fm = extract_frontmatter(filepath)
    filename = filepath.name
    number = extract_protocol_number(filename)
    name = extract_protocol_name(filename, fm)
    description = fm.get("description", "")

    # If no description in frontmatter, try to extract from heading context
    if not description and "heading" in fm:
        # Use the heading minus any "Protocol NNN:" prefix
        desc = re.sub(r"^Protocol\s+\d+:\s*", "", fm["heading"])
        description = desc

    return {
        "number": number,
        "name": name,
        "description": description,
        "category": category,
        "filename": filename,
        "path": str(filepath.relative_to(REPO_ROOT)),
    }


def main():
    if not PROTOCOLS_DIR.exists():
        print(f"❌ Protocol directory not found: {PROTOCOLS_DIR}")
        return

    # Collect all protocols grouped by category
    categories = defaultdict(list)
    total = 0

    for category_dir in sorted(PROTOCOLS_DIR.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue

        category = category_dir.name

        for md_file in sorted(category_dir.glob("*.md")):
            if md_file.name in ("README.md", "INDEX.md"):
                continue
            summary = build_summary(md_file, category)
            categories[category].append(summary)
            total += 1

    # Generate the output
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "---",
        f"created: 2026-03-16",
        f"last_updated: {now}",
        "description: Quick-lookup summaries for all protocols, grouped by category",
        "auto_generated: true",
        "generator: generate_protocol_summaries.py",
        "---",
        "",
        "# Protocol Summaries",
        "",
        f"> **Purpose**: One-line summaries for rapid protocol discovery. Referenced by `AGENTS.md` for agent retrieval.",
        f"> **Inventory**: {total} protocols across {len(categories)} categories.",
        '> **Path**: `.agent/skills/protocols/<category>/<filename>.md`',
        f"> **Generated**: {now} by `generate_protocol_summaries.py`",
        "",
        "---",
        "",
    ]

    # Sort categories by count (descending) for quick scanning
    sorted_cats = sorted(categories.items(), key=lambda x: -len(x[1]))

    for category, protocols in sorted_cats:
        cat_title = category.replace("-", " ").title()
        lines.append(f"## {cat_title} ({len(protocols)})")
        lines.append("")
        lines.append("| Protocol | Summary |")
        lines.append("|----------|---------|")

        for p in protocols:
            num = p["number"]
            name_clean = re.sub(r"^Protocol\s+\d+:\s*", "", p["name"])
            # Truncate description to first sentence for table readability
            desc = p["description"]
            if not desc:
                desc = name_clean
            # Limit to ~80 chars for table
            if len(desc) > 100:
                desc = desc[:97] + "..."
            label = f"{num} {name_clean}" if num else name_clean
            lines.append(f"| {label} | {desc} |")

        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "> **System Note**: For deep lookup, use `smart_search.py` or browse "
        "`.agent/skills/protocols/<category>/`. This file is a quick-reference index only."
    )
    lines.append("")
    lines.append("#protocols #index #summaries #retrieval")
    lines.append("")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"✅ Generated {OUTPUT_FILE} — {total} protocols across {len(categories)} categories")


if __name__ == "__main__":
    main()
