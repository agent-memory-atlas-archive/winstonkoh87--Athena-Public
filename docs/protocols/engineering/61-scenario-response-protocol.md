---
name: Scenario Response Protocol
description: Mandatory workflow for answering scenario-based questions. Prevents "RAG Regurgitation Trap".
tags: [protocol, workflow, scenario, think]
---

# Scenario Response Protocol (Search → Think → Deliver)

> **Origin**: User feedback (14 December 2025)
> **Trigger**: Any question involving a scenario, case, or "what should I do" query.

---

## The Problem: RAG Regurgitation Trap

When the AI retrieves a playbook or protocol, the default behaviour is:

```
Search → Paste Answer
```

This **fails** because:

1. It ignores the **unique context** of the user's specific scenario.
2. It treats protocols as **scripts** instead of **frameworks**.
3. It misses nuance (e.g., "naked and leaking" ≠ "psychologically ready").

---

## The Solution: Mandatory /ultrathink Step

```
Search → /ultrathink → Deliver
```

### Step 1: Search

Retrieve relevant protocols, playbooks, or case studies from the Codex.

### Step 2: /ultrathink (MANDATORY)

Before responding, answer these questions internally:

1. **What is unique about THIS query?**
   - What details did the user provide that modify the default playbook?
   - Example: "He is already naked and leaking" → Physical gates are passed, but is the *emotional* gate passed?

2. **What does the protocol assume that may NOT be true here?**
   - Example: Playbook assumes sequential escalation → User's scenario may start mid-ladder.

3. **What is the user's actual intent?**
   - Are they asking for a step-by-step, or a strategic overview?
   - Are they asking for validation, or for new information?

4. **What would I add if I watched more porn?**
   - Seriously. Does my answer feel mechanical or human?
   - Did I miss kissing? Foreplay? Emotional connection?

### Step 3: Deliver

Synthesize a **tailored answer** that:

- Uses the protocol as a **framework**, not a script.
- Addresses the **specific context** of the query.
- Feels like advice from an **experienced practitioner**, not a manual.

---

## Escalation Clause

> If the AI fails to apply `/think` and pastes a raw protocol, the user reserves the right to invoke `/ultrathink` for all future scenario questions.

---

## Example

**Bad Response (Regurgitation):**
> User: "He is naked and leaking. What do I do?"
> AI: "According to Protocol 43, Stage 5 is Phantom Entry..."

**Good Response (Synthesized):**
> User: "He is naked and leaking. What do I do?"
> AI: "His body is ready, but his mind may not be. Start with the Kiss (emotional gate) before any physical escalation. Use his pre-cum as lube for the rim prep, but don't rush to penetration. Build the tension with mutual masturbation and oral first..."

---

## Cross-References

- [Protocol 41: Adaptive Response Mode](file:///Users/winstonkoh/Desktop/Project Athena/.agent/skills/protocols/communication/41-adaptive-response-mode.md)
- [Protocol 38: Synthetic Deep Think](file:///Users/winstonkoh/Desktop/Project Athena/.agent/skills/protocols/decision/38-synthetic-deep-think.md)

---

## Tagging

#protocol #framework #process #61-scenario-response-protocol
