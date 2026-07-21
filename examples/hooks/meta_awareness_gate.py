#!/usr/bin/env python3
"""
meta_awareness_gate.py — v3: Code-enforced, domain-general meta-awareness trigger.

Claude Code UserPromptSubmit hook. Fires on every user prompt. v2 matched
social-domain keywords only; v3 classifies by ACT STRUCTURE, so the same gate
covers financial, consumer, institutional, commercial, broadcast, and
relational prompts without per-domain regex whack-a-mole.

Trigger classes (structural, domain-agnostic):
    T1 INBOUND-NARRATIVE   received story/act with stakes ("why did they…")
    T2 OUTBOUND-COMMIT     audience-facing act about to be (or just) emitted
    T3 THIRD-PARTY-VERDICT forming/broadcasting judgment of someone else's act
    T4 RESOURCE-COMMIT     novel money/time/reputation deployment
    T5 FELT-EVIDENCE       feeling offered as evidence ("feels like it has to…")

Design notes (research-grounded):
    - The injected reminder is QUESTION-framed, not prohibition-framed:
      "ask, don't tell" phrasing measurably outperforms "don't do X"
      instructions at suppressing agreement bias (arXiv:2602.23971).
    - The receiver-frame step runs perspective-FIRST (list what the receiver
      observes before judging how the act lands) — the ordering shown to
      improve LLM perspective-taking (SimToM, ACL 2024).
    - New domains extend your skill content (arena/base-rate tables), never
      this file. Structure is the mechanism; domains are data.

Why this exists (the auto-invoke fiction):
    A skill can carry `auto-invoke: true` in its frontmatter, but frontmatter
    is prose — nothing in the harness enforces it. In practice the model
    skips the skill exactly when it matters most (emotionally-loaded prompts
    are where discretion fails). This hook is the deterministic trigger that
    the frontmatter only pretended to be. If a doc says "automatically
    activates" and no code fires it, it is agent-discretion dressed as a
    mechanism. Hooks convert `auto-invoke: true` from a claim into a fact.

Epistemic status: code-enforced (the harness runs it on every prompt,
    regardless of model discretion). KNOWN LIMITS, stated honestly:
      - Text-only: cannot fire on an act the user never narrates.
      - Claude Code only: environments without prompt hooks do not run this.
        There it reverts to agent-discretion.
      - Regex tier is high-recall/low-precision by design; the injected
        kernel instructs the model tier to classify structurally on anything
        substantive the regex missed. Biased to over-fire: a false positive
        costs one extra reminder (cheap); a false negative costs an unforced
        error (expensive).
      - NEGATIVE guard: routine-ops prompts (reconciliation, test runs, doc
        chores) suppress a T4-only fire to keep the fire-rate sane.

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
import os
import re
import sys
from datetime import datetime, timezone

# T1 — INBOUND-NARRATIVE: a received story, act, or signal with stakes.
T1_INBOUND = [
    r"why (did|would|does|is|are|won'?t|didn'?t|hasn'?t) (he|she|they|it|the|my|this|that|\w+)",
    r"what does (this|it|that) (mean|say|signal)",
    r"(real|actual|hidden) (reason|meaning|agenda|motive)",
    r"reading between the lines",
    r"am i missing something",
    r"(he|she|they|the \w+) (said|announced|offered|claims?|promised|assured)",
    r"(haven'?t|hasn'?t|didn'?t) (replied|reply|gotten back|responded|texted back)",
    r"left (me )?on read",
    r"(no|zero) (reply|response|reaction)",
    r"reached out",
    r"ghost(ed|ing|s)?",
    r"(are we|we'?re) (friends|besties|close|tight)",
    r"(ignoring|ignored) me",
    r"seen (but|and) (no|never)",
    r"do(es)? (he|she|they) (like|want|value|respect) me",
]

# T2 — OUTBOUND-COMMIT: an audience-facing act about to be emitted (or
# narrated after the fact -> retro decode; the act happened un-gated).
T2_OUTBOUND = [
    r"should i (post|send|text|reply|message|dm|invite|tell|share|forward|call out|confront|expose|announce|publish|sign|quote|accept|agree to|pitch)",
    r"before i (send|post|reply|text|message|sign|submit|commit)",
    r"thinking of (posting|texting|sending|messaging|inviting|reaching out|calling out|confronting|signing|pitching|quoting)",
    r"how (will|does|would|might) (this|it|that) (look|come across|land|read)",
    r"how (this|it|that) (will|would|might|is going to) (look|come across|land|read)",
    r"is it (ok|okay|fine|weird) to (send|post|text|reply|invite|ask|call out|confront|sign|quote)",
    r"about to (post|send|text|message|meet|sign|commit|call out|confront|submit)",
    r"(plan|planning|going|want|intend)(ing)? to (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign|pitch)",
    r"gonna (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign)",
    r"\bi (invited|texted|posted|sent|messaged|confronted|called out|shared|dm'?ed|gifted|signed|quoted|pitched)\b",
    r"call(ing|ed)?[- ]?out\b|\bcall (him|her|them|\w+) out\b",
    r"\bpsa\b",
    r"\boptics\b",
]

# T3 — THIRD-PARTY-VERDICT: soliciting/forming a verdict on someone else's act.
T3_VERDICT = [
    r"(is|was|isn'?t|wasn'?t) (this|that|it|he|she) (ok|okay|not okay|inappropriate|acceptable|out of line|creepy|rude|wrong|cruel)",
    r"(inappropriate|unprofessional|unacceptable), right\b",
    r"how (dare|could) (he|she|they)",
]

# T4 — RESOURCE-COMMIT: novel deployment of money/time/reputation.
# (Position-sizing / capital decisions deserve a dedicated risk gate, not this.)
T4_RESOURCE = [
    r"should i (buy|purchase|get|order|subscribe|upgrade|renew|book|deposit|top ?up|preorder|enroll|register)",
    r"(is it|is this|are they|is the \w+) worth",
    r"worth (it|buying|paying|the (price|money|cost))",
    r"should i (scale|size|double|add) (up|into|down|the)",
    r"(good|fair|reasonable) (deal|price|value)\b",
]

# T5 — FELT-EVIDENCE: a feeling offered as evidence about external reality.
T5_FELT = [
    r"i feel like",
    r"it feels like",
    r"felt like we (\w+ )?(connected|clicked|bonded|vibed)",
    r"it seems like (he|she|they|the|this|everyone)",
    r"obviously (he|she|they|it|nothing|everyone|the)",
    r"i'?m (sure|certain) (he|she|they|it|the)",
    r"my gut (says|tells|feeling)",
    r"vibes? (say|says|is|are|were)",
    r"(has|have) to (bounce|recover|come back|reverse|moon|pump)",
]

CLASSES = [
    ("T1-INBOUND", T1_INBOUND),
    ("T2-OUTBOUND", T2_OUTBOUND),
    ("T3-VERDICT", T3_VERDICT),
    ("T4-RESOURCE", T4_RESOURCE),
    ("T5-FELT", T5_FELT),
]

# NEGATIVE — routine-ops context. If matched and the ONLY fired class is T4,
# suppress (maintenance prompts must not gate; quick lookups stay fast).
NEGATIVE = [
    r"\breconcil\w*",
    r"rebuild (the )?(excel|tracker|dashboard)",
    r"sync (the )?balance",
    r"compile (the )?(index|tracker|report)",
    r"run (the )?tests?",
    r"fix (the )?(test|lint|ci|typo)",
    r"update (the )?changelog",
    r"\bpytest\b",
]

# Kernel reminder — question-framed ("ask don't tell" beats prohibition for
# agreement bias; arXiv:2602.23971), class-tagged, kept concise. Step 8
# (agency/anti-override) guards partisan loyalty from curdling into paternalism
# under an advisory frame (Kelley & Riedl 2026, arXiv:2603.00024).
REMINDER_TEMPLATE = """<system-reminder>
META-AWARENESS GATE (meta_awareness_gate.py v3, code-enforced) — fired: {classes}
Interpreter kernel — answer each question before responding (Prior -> Discriminators -> Payoff):
1. ARENA: What container is this, and what is its IMPLICIT contract (not the stated one)?
2. PRIOR: What is this arena's base rate for what this act usually means?
3. DISCRIMINATORS: Which verifiable details move the prior? List them, or state "none — prior holds".
4. SIGN CHECK: Is the working read inflating (self-flattering) or deflating (self-degrading)?
   Would I accept this read if the sign were flipped? Correct both with equal rigor.
5. RECEIVER FRAME (outbound, perspective-first): What does the receiver OBSERVE, intent stripped?
   What is their worst plausible SELF-referential decode ("what does this say about ME?")?
6. FELT != REAL: Is felt intensity being offered as evidence? It measures the feeler, not the world.
7. PAYOFF: What does each misread cost? Act on the asymmetry, not the point estimate.
8. AGENCY (anti-override): if ranking or advising, weight by the USER'S revealed preferences, not your model of what they should want — surface the weights, hand the choice back.
Guards: capital/position sizing belongs to a dedicated risk gate, not vibes. Keep the sincere read
in the payoff table — cynical-by-default is the same decode failure. Load your deep-read skill
(e.g. social-physics-filter) if depth is needed.
</system-reminder>"""


def classify(prompt: str) -> list:
    p = prompt.lower()
    fired = []
    for name, patterns in CLASSES:
        if any(re.search(pat, p) for pat in patterns):
            fired.append(name)
    if fired == ["T4-RESOURCE"] and any(re.search(pat, p) for pat in NEGATIVE):
        return []
    return fired


def log_fire(fired: list) -> None:
    """Optional fire-rate telemetry — appends class names (never content) to
    .athena/invocations.jsonl if the directory exists. Never raises."""
    try:
        path = os.path.join(os.getcwd(), ".athena", "invocations.jsonl")
        if not os.path.isdir(os.path.dirname(path)):
            return
        record = {
            "type": "hook",
            "name": "meta_awareness_gate",
            "classes": fired,
            "trigger": "UserPromptSubmit",
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    prompt = (payload.get("prompt") or "").strip()
    if prompt:
        fired = classify(prompt)
        if fired:
            sys.stdout.write(REMINDER_TEMPLATE.format(classes=", ".join(fired)) + "\n")
            log_fire(fired)
    sys.exit(0)


if __name__ == "__main__":
    main()
