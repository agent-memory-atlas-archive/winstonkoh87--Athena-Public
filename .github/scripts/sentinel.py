#!/usr/bin/env python3
"""
Sentinel — Semi-Autonomous GitHub Repo Governance.

Reads GitHub event payloads from Actions, classifies them using Gemini,
and responds with labels + comments. Human-in-the-loop for all merges.

Usage:
  - Triggered by GitHub Actions (see sentinel.yml)
  - Dry-run: SENTINEL_DRY_RUN=1 python3 sentinel.py --test
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRY_RUN = os.getenv("SENTINEL_DRY_RUN", "0") == "1"
REPO = os.getenv("GITHUB_REPOSITORY", "winstonkoh87/Athena-Public")
CONFIG_PATH = Path(__file__).parent.parent / "sentinel_config.yml"

# Tier definitions
TIER_AUTO = "auto_handle"
TIER_REVIEW = "needs_review"
TIER_CRITICAL = "critical"

TIER_LABELS = {
    TIER_AUTO: "triage/auto",
    TIER_REVIEW: "triage/review",
    TIER_CRITICAL: "triage/critical",
}

# Protected paths that auto-escalate PRs to critical
PROTECTED_PATHS = [
    "src/athena/core/",
    ".github/",
    "AGENTS.md",
    "pyproject.toml",
    "docs/SECURITY.md",
    "supabase/",
]

# PR thresholds
MAX_DIFF_LINES_AUTO = 200
MAX_FILES_AUTO = 5


# ---------------------------------------------------------------------------
# Gemini API
# ---------------------------------------------------------------------------


def call_gemini(prompt: str) -> str:
    """Call Gemini API via google-generativeai or fall back to REST."""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    if not api_key:
        print("⚠️  No GOOGLE_API_KEY found. Falling back to rule-based triage.")
        return ""

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except ImportError:
        # Fallback to REST API
        import urllib.request

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
        body = json.dumps(
            {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1024},
            }
        ).encode()
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()


# ---------------------------------------------------------------------------
# GitHub CLI helpers
# ---------------------------------------------------------------------------


def gh(cmd: str) -> str:
    """Run a gh CLI command and return output."""
    if DRY_RUN:
        print(f"  [DRY RUN] gh {cmd}")
        return ""
    result = subprocess.run(
        f"gh {cmd}", shell=True, capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"  ⚠️  gh error: {result.stderr.strip()}")
    return result.stdout.strip()


def add_label(event_type: str, number: int, label: str) -> None:
    """Add a label to an issue or PR."""
    if event_type == "pull_request":
        gh(f'pr edit {number} --add-label "{label}" -R {REPO}')
    else:
        gh(f'issue edit {number} --add-label "{label}" -R {REPO}')


def post_comment(event_type: str, number: int, body: str) -> None:
    """Post a comment on an issue, PR, or discussion."""
    if event_type == "discussion":
        # Discussions require GraphQL
        disc_id = get_discussion_id(number)
        if disc_id:
            escaped = body.replace('"', '\\"').replace("\n", "\\n")
            gh(
                f'api graphql -f query=\'mutation {{ addDiscussionComment(input: {{discussionId: "{disc_id}", body: "{escaped}"}}) {{ comment {{ id }} }} }}\''
            )
    else:
        escaped = body.replace("'", "'\\''")
        gh(f"issue comment {number} --body '{escaped}' -R {REPO}")


def get_discussion_id(number: int) -> str | None:
    """Get the node ID for a discussion by number."""
    result = gh(
        f'api graphql -f query=\'{{ repository(owner: "{REPO.split("/")[0]}", name: "{REPO.split("/")[1]}") {{ discussion(number: {number}) {{ id }} }} }}\''
    )
    try:
        return json.loads(result)["data"]["repository"]["discussion"]["id"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def get_pr_files(number: int) -> list[dict]:
    """Get list of files changed in a PR."""
    result = gh(f"pr diff {number} --name-only -R {REPO}")
    return [{"filename": f} for f in result.strip().split("\n") if f]


def get_pr_diff_stats(number: int) -> dict:
    """Get additions/deletions stats for a PR."""
    result = gh(f"pr view {number} --json additions,deletions,changedFiles -R {REPO}")
    try:
        return json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return {"additions": 0, "deletions": 0, "changedFiles": 0}


# ---------------------------------------------------------------------------
# Event Parsing
# ---------------------------------------------------------------------------


def parse_event() -> dict[str, Any]:
    """Parse the GitHub event payload."""
    event_path = os.getenv("GITHUB_EVENT_PATH", "")
    event_name = os.getenv("GITHUB_EVENT_NAME", "")

    if not event_path or not Path(event_path).exists():
        return {}

    with open(event_path) as f:
        payload = json.load(f)

    return {
        "event_name": event_name,
        "action": payload.get("action", ""),
        "payload": payload,
    }


def extract_event_details(event: dict) -> dict[str, Any]:
    """Extract normalized details from any event type."""
    name = event.get("event_name", "")
    payload = event.get("payload", {})

    if name == "issues":
        issue = payload.get("issue", {})
        return {
            "type": "issue",
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "body": issue.get("body", "")[:2000],  # Truncate for token efficiency
            "author": issue.get("user", {}).get("login", ""),
            "labels": [l.get("name") for l in issue.get("labels", [])],
        }

    elif name == "pull_request":
        pr = payload.get("pull_request", {})
        return {
            "type": "pull_request",
            "number": pr.get("number"),
            "title": pr.get("title", ""),
            "body": pr.get("body", "")[:2000],
            "author": pr.get("user", {}).get("login", ""),
            "labels": [l.get("name") for l in pr.get("labels", [])],
        }

    elif name in ("discussion", "discussion_comment"):
        disc = payload.get("discussion", {})
        return {
            "type": "discussion",
            "number": disc.get("number"),
            "title": disc.get("title", ""),
            "body": disc.get("body", "")[:2000],
            "author": disc.get("user", {}).get("login", ""),
            "labels": [],
            "category": disc.get("category", {}).get("name", ""),
        }

    elif name == "issue_comment":
        issue = payload.get("issue", {})
        comment = payload.get("comment", {})
        return {
            "type": "issue_comment",
            "number": issue.get("number"),
            "title": issue.get("title", ""),
            "body": comment.get("body", "")[:2000],
            "author": comment.get("user", {}).get("login", ""),
            "labels": [l.get("name") for l in issue.get("labels", [])],
        }

    return {"type": "unknown"}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify_pr(details: dict) -> dict:
    """Classify a PR using rules + LLM."""
    number = details["number"]

    # Rule-based: check protected paths
    files = get_pr_files(number)
    filenames = [f["filename"] for f in files]

    for fname in filenames:
        for protected in PROTECTED_PATHS:
            if fname.startswith(protected) or fname == protected.rstrip("/"):
                return {
                    "tier": TIER_CRITICAL,
                    "reason": f"PR modifies protected path: `{fname}`",
                    "type_label": "type/feature",
                }

    # Rule-based: check diff size
    stats = get_pr_diff_stats(number)
    total_lines = stats.get("additions", 0) + stats.get("deletions", 0)
    total_files = stats.get("changedFiles", 0)

    if total_lines > MAX_DIFF_LINES_AUTO or total_files > MAX_FILES_AUTO:
        return {
            "tier": TIER_REVIEW,
            "reason": f"PR is large ({total_lines} lines, {total_files} files) — needs human review.",
            "type_label": "type/feature",
        }

    # Check if docs-only
    all_docs = all(
        fname.endswith(".md")
        or fname.startswith("docs/")
        or fname.startswith("community/")
        for fname in filenames
    )

    if all_docs and total_lines <= 200:
        # Use LLM for final check
        llm_result = classify_with_llm(details, "pull_request")
        if llm_result:
            return llm_result
        return {
            "tier": TIER_AUTO,
            "reason": "Docs-only PR with small diff. Auto-labeled.",
            "type_label": "type/docs",
        }

    # Default: needs review
    llm_result = classify_with_llm(details, "pull_request")
    return llm_result or {
        "tier": TIER_REVIEW,
        "reason": "Code PR — flagged for maintainer review.",
        "type_label": "type/feature",
    }


def classify_issue_or_discussion(details: dict) -> dict:
    """Classify an issue or discussion using LLM."""
    llm_result = classify_with_llm(details, details["type"])
    return llm_result or {
        "tier": TIER_REVIEW,
        "reason": "Unable to auto-classify. Flagged for review.",
        "type_label": "type/question",
    }


def classify_with_llm(details: dict, event_type: str) -> dict | None:
    """Use Gemini to classify an event."""
    prompt = f"""You are Sentinel, an AI triage bot for the Athena-Public GitHub repo.
Classify this {event_type} into exactly ONE tier and provide a brief reason.

TIERS:
- auto_handle: Routine. Simple questions already answered in docs, thank-you posts, duplicates, typo fixes.
- needs_review: Needs maintainer attention. Feature requests, bug reports, code changes, architecture discussions.
- critical: Urgent. Security issues, breaking changes, frustrated/angry users, PRs touching core files.

Also classify the TYPE as one of: bug, feature, question, docs, duplicate.

And classify SENTIMENT as one of: positive, neutral, negative, frustrated.

EVENT:
Title: {details.get("title", "N/A")}
Body: {details.get("body", "N/A")[:1500]}
Author: {details.get("author", "N/A")}
Type: {event_type}

Respond in EXACTLY this JSON format, nothing else:
{{"tier": "auto_handle|needs_review|critical", "reason": "one sentence", "type_label": "bug|feature|question|docs|duplicate", "sentiment": "positive|neutral|negative|frustrated", "suggested_response": "A helpful response to post as a comment. Be direct and friendly. If the question is answered in docs, link to the relevant file (use relative paths like docs/FAQ.md). Keep under 200 words."}}
"""
    response = call_gemini(prompt)
    if not response:
        return None

    # Parse JSON from response (handle markdown code fences)
    text = response
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    try:
        result = json.loads(text.strip())
        return {
            "tier": result.get("tier", TIER_REVIEW),
            "reason": result.get("reason", ""),
            "type_label": f"type/{result.get('type_label', 'question')}",
            "sentiment": result.get("sentiment", "neutral"),
            "suggested_response": result.get("suggested_response", ""),
        }
    except json.JSONDecodeError:
        print(f"  ⚠️  Failed to parse LLM response: {response[:200]}")
        return None


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def execute_triage(details: dict, classification: dict) -> None:
    """Execute the triage actions based on classification."""
    event_type = details["type"]
    number = details["number"]
    tier = classification["tier"]
    reason = classification["reason"]
    type_label = classification.get("type_label", "")
    sentiment = classification.get("sentiment", "")
    suggested_response = classification.get("suggested_response", "")

    print(f"\n📋 Sentinel Classification:")
    print(f"   Event:     {event_type} #{number}")
    print(f"   Title:     {details.get('title', 'N/A')}")
    print(f"   Tier:      {tier}")
    print(f"   Reason:    {reason}")
    print(f"   Type:      {type_label}")
    print(f"   Sentiment: {sentiment}")

    if DRY_RUN:
        print(f"\n   [DRY RUN] Would label: {TIER_LABELS[tier]}, {type_label}")
        if suggested_response:
            print(f"   [DRY RUN] Would respond:\n{suggested_response[:500]}")
        return

    # Apply triage label
    add_label(event_type, number, TIER_LABELS[tier])

    # Apply type label
    if type_label:
        add_label(event_type, number, type_label)

    # Apply sentiment label if notable
    if sentiment in ("positive", "frustrated"):
        add_label(event_type, number, f"sentiment/{sentiment}")

    # Post response based on tier
    if tier == TIER_AUTO and suggested_response:
        post_comment(event_type, number, suggested_response)

    elif tier == TIER_REVIEW:
        summary = f"🤖 **Sentinel Triage**: Flagged for maintainer review.\n\n**Reason**: {reason}\n\n@winstonkoh87 — this needs your eyes."
        post_comment(event_type, number, summary)

    elif tier == TIER_CRITICAL:
        alert = f"🚨 **Sentinel Alert**: Critical item detected.\n\n**Reason**: {reason}\n\n@winstonkoh87 — immediate attention needed."
        post_comment(event_type, number, alert)


# ---------------------------------------------------------------------------
# Test Mode
# ---------------------------------------------------------------------------


def run_test():
    """Run with mock payloads for local testing."""
    print("🧪 Sentinel Test Mode\n")

    test_events = [
        {
            "type": "issue",
            "number": 0,
            "title": "How do I update Athena?",
            "body": "Hi, I cloned the repo a week ago. How do I get the latest version without losing my data?",
            "author": "test_user",
            "labels": [],
        },
        {
            "type": "issue",
            "number": 0,
            "title": "[BUG] Boot script crashes on Windows",
            "body": "Running boot.py on Windows 11 gives a FileNotFoundError. Python 3.12. Stack trace attached.",
            "author": "test_user",
            "labels": [],
        },
        {
            "type": "pull_request",
            "number": 0,
            "title": "Fix typo in README.md",
            "body": "Fixed a small typo in the quickstart section.",
            "author": "test_user",
            "labels": [],
        },
        {
            "type": "discussion",
            "number": 0,
            "title": "This project changed my life",
            "body": "Just wanted to say thank you. Been using Athena for 2 months and it's transformed how I work.",
            "author": "test_user",
            "labels": [],
            "category": "General",
        },
        {
            "type": "issue",
            "number": 0,
            "title": "[SECURITY] API keys exposed in logs",
            "body": "The daemon logs contain my Supabase API key in plaintext. This is a security vulnerability.",
            "author": "test_user",
            "labels": [],
        },
    ]

    for i, event in enumerate(test_events, 1):
        print(f"\n{'=' * 60}")
        print(f"Test {i}/{len(test_events)}: {event['title']}")
        print(f"{'=' * 60}")

        classification = classify_with_llm(event, event["type"]) or {
            "tier": TIER_REVIEW,
            "reason": "Fallback — no LLM available",
            "type_label": "type/question",
            "sentiment": "neutral",
            "suggested_response": "",
        }
        execute_triage(event, classification)

    print(f"\n{'=' * 60}")
    print("✅ Test complete.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if "--test" in sys.argv:
        run_test()
        return

    print("🛡️  Sentinel — AI Repo Governance")
    print(f"   Repo: {REPO}")
    print(f"   Dry Run: {DRY_RUN}\n")

    event = parse_event()
    if not event:
        print("⚠️  No event payload found. Exiting.")
        return

    details = extract_event_details(event)
    if details["type"] == "unknown":
        print(f"⚠️  Unknown event type: {event.get('event_name')}. Skipping.")
        return

    # Skip bot comments (avoid infinite loops)
    if details.get("author") in ("github-actions[bot]", "dependabot[bot]"):
        print("🤖 Bot event — skipping to avoid loops.")
        return

    # Skip already-triaged items
    existing_labels = details.get("labels", [])
    if any(l.startswith("triage/") for l in existing_labels):
        print("📌 Already triaged — skipping.")
        return

    print(
        f"📨 Processing: {details['type']} #{details.get('number')} — {details.get('title', 'N/A')}"
    )

    # Classify
    if details["type"] == "pull_request":
        classification = classify_pr(details)
    else:
        classification = classify_issue_or_discussion(details)

    # Execute
    execute_triage(details, classification)
    print("\n✅ Sentinel complete.")


if __name__ == "__main__":
    main()
