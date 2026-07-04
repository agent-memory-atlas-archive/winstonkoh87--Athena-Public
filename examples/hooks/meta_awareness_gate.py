#!/usr/bin/env python3
"""
meta_awareness_gate.py — Code-enforced trigger for socially-loaded prompts.

Claude Code UserPromptSubmit hook. Fires on every user prompt. If the prompt
carries markers of (a) an about-to-be-sent socially-loaded act, or (b) an
emotionally-hot read of an inbound social signal, it INJECTS a system-reminder
forcing the agent to run a meta-awareness check BEFORE responding.

Why this exists (the auto-invoke fiction):
    A skill can carry `auto-invoke: true` in its frontmatter, but frontmatter
    is prose — nothing in the harness enforces it. In practice the model
    skips the skill exactly when it matters most (emotionally-loaded prompts
    are where discretion fails). This hook is the deterministic trigger that
    the frontmatter only pretended to be.

    This is the general pattern: if a doc says "automatically activates" and
    no code fires it, it is agent-discretion dressed as a mechanism. Hooks
    convert `auto-invoke: true` from a claim into a fact.

Epistemic status: code-enforced (the harness runs it on every prompt,
    regardless of model discretion). KNOWN LIMITS, stated honestly:
      - Text-only: cannot fire on an act the user never narrates.
      - Claude Code only: environments without prompt hooks do not run this.
        There it reverts to agent-discretion.
      - Biased to over-fire. A false positive costs one extra reminder
        (cheap); a false negative costs an unforced social error (expensive).

Wiring (.claude/settings.json):
    {
      "hooks": {
        "UserPromptSubmit": [
          { "hooks": [{ "type": "command",
                        "command": "python3 examples/hooks/meta_awareness_gate.py" }] }
        ]
      }
    }

Contract: NEVER blocks (always exit 0), <50ms, stdlib only. Anything printed
    to stdout is injected into model context by the UserPromptSubmit hook.
"""

import json
import re
import sys

# (a) OUTBOUND — about to emit a socially-loaded act.
OUTBOUND = [
    r"should i (post|send|text|reply|message|dm|invite|tell|share|forward)",
    r"before i (send|post|reply|text|message)",
    r"thinking of (posting|texting|sending|messaging|inviting|reaching out)",
    r"how (will|does) (this|it) (look|come across|land|read)",
    r"is it (ok|okay|fine|weird) to (send|post|text|reply|invite|ask)",
    r"about to (post|send|text|message|meet|sign|commit)",
]

# (b) INBOUND — emotionally-hot read of a social signal.
INBOUND = [
    r"(haven'?t|hasn'?t|didn'?t) (replied|reply|gotten back|responded|texted back)",
    r"left (me )?on read",
    r"(no|zero) (reply|response|reaction)",
    r"ghost(ed|ing|s)?",
    r"felt like we (connected|clicked|bonded|vibed)",
    r"(are we|we'?re) (friends|besties|close|tight)",
    r"why (didn'?t|hasn'?t|won'?t) (he|she|they|\w+) (reply|respond|text|answer)",
    r"(ignoring|ignored) me",
    r"do(es)? (he|she|they) (like|want|value|respect) me",
]

REMINDER = """<system-reminder>
META-AWARENESS GATE TRIGGERED (meta_awareness_gate.py — code-enforced).
This prompt carries markers of a socially-loaded act or an emotionally-hot
read of a social signal — the class of prompt where agent discretion is least
reliable. Before responding, run the gate:
  1. OBSERVER-SEAT TEST: reframe the user's own move as a stranger's post on
     a public forum. What does the thread say? (Converts self + high-emotion
     into third-party + low-emotion.)
  2. BOARD CHECK: what are the counterparty's real incentives — not their
     words? How is the user seen, vs how they think they're seen?
  3. FELT != REAL: felt intensity estimates the user's own hunger, not the
     counterparty's state. Weight only costly, reciprocal, unprompted action.
     Treat silence as no-data, not as signal.
  4. If outbound: do NOT validate or send on vibes — decode how the message
     will land before polishing how it reads.
Load the social-physics-filter skill if depth is needed. Do not skip because
it "looks fine by itself" — fine-in-isolation + catastrophic-in-context IS
the failure mode this gate exists for.
</system-reminder>"""


def hit(prompt: str) -> bool:
    p = prompt.lower()
    for group in (OUTBOUND, INBOUND):
        for pat in group:
            if re.search(pat, p):
                return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    prompt = (payload.get("prompt") or "").strip()
    if prompt and hit(prompt):
        sys.stdout.write(REMINDER + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
