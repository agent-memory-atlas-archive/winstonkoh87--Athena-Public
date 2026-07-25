"""
gate_meta.py — Meta-awareness classification engine module.
Exposes classify() and REMINDER_TEMPLATE for SDK-wide use.
"""

import re

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

T2_OUTBOUND = [
    r"should i (post|send|text|reply|message|dm|invite|tell|share|forward|call out|confront|expose|announce|publish|sign|quote|accept|agree to|pitch)",
    r"before i (send|post|reply|text|message|sign|submit|commit)",
    r"thinking of (posting|texting|sending|messaging|inviting|reaching out|calling out|confronting|signing|pitching|quoting)",
    r"how (will|does|would|might) (this|it|that) (look|come across|land|read)",
    r"how (this|it|that) (will|would|might|is going to) (look|come across|land|read)",
    r"is it (ok|okay|fine|weird) to (send|post|text|reply|invite|ask|call out|confront|sign|quote)",
    r"draft (this|a|my|the)",
    r"about to (post|send|text|message|meet|sign|commit|call out|confront|submit)",
    r"(plan|planning|going|want|intend)(ing)? to (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign|pitch)",
    r"gonna (post|send|text|message|invite|call out|confront|announce|publish|share|gift|sign)",
    r"\bi (invited|texted|posted|sent|messaged|confronted|called out|shared|dm'?ed|gifted|signed|quoted|pitched)\b",
    r"call(ing|ed)?[- ]?out\b|\bcall (him|her|them|\w+) out\b",
    r"\bpsa\b",
    r"\boptics\b",
]

T3_VERDICT = [
    r"(is|was|isn'?t|wasn'?t) (this|that|it|he|she) (ok|okay|not okay|inappropriate|acceptable|out of line|creepy|rude|wrong|cruel)",
    r"(inappropriate|unprofessional|unacceptable), right\b",
    r"how (dare|could) (he|she|they)",
    r"am i being pryce",
    r"is this a hummer",
    r"out of context|\booc\b|taboo",
]

T4_RESOURCE = [
    r"should i (buy|purchase|get|order|subscribe|upgrade|renew|book|deposit|top ?up|preorder|enroll|register)",
    r"(is it|is this|are they|is the \w+) worth",
    r"worth (it|buying|paying|the (price|money|cost))",
    r"should i (scale|size|double|add) (up|into|down|the)",
    r"(good|fair|reasonable) (deal|price|value)\b",
]

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

NEGATIVE = [
    r"\breconcil\w*",
    r"rebuild (the )?(excel|tracker|dashboard)",
    r"sync (the )?balance",
    r"compile (the )?(index|tracker|report|case stud)",
    r"run (the )?tests?",
    r"fix (the )?(test|lint|ci|typo)",
    r"update (the )?changelog",
    r"\bpytest\b",
]

REMINDER_TEMPLATE = """<system-reminder>
META-AWARENESS GATE (hook v3, code-enforced) — fired: {classes}
Interpreter kernel — answer each question before responding (Prior -> Discriminators -> Payoff):
1. ARENA: What container is this, and what is its IMPLICIT contract (not the stated one)?
2. PRIOR: What is this arena's base rate? (substance-decode Module 3 library.)
3. DISCRIMINATORS: Which verifiable details move the prior? List them, or state "none — prior holds".
4. SIGN CHECK (MP-16): Is the working read inflating (self-flattering) or deflating (self-degrading)?
   Would I accept this read if the sign were flipped? Correct both with equal rigor.
5. RECEIVER FRAME (outbound, SimToM order): What does the receiver OBSERVE, intent stripped?
   What is their worst plausible SELF-referential decode ("what does this say about ME?")?
6. F != R: Is felt intensity being offered as evidence? It measures the feeler, not the world.
7. PAYOFF: What does each misread cost? Act on the asymmetry, not the point estimate.
8. AGENCY (anti-override): if ranking or advising, weight by the USER'S revealed preferences, not your model of what they should want — surface the weights, hand the choice back.
Guards: capital/position sizing -> trading-risk-gate owns the verdict. Keep the sincere read in the
payoff table — cynical-by-default is the same decode failure. Load substance-decode for depth.
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
