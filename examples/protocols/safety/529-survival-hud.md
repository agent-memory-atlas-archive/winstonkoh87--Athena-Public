---
name: Survival HUD
description: Auto-triggered stripped output mode when the Survival cognitive system activates. Reduces output to ≤15 lines. Zero hedging. Maximum decisiveness under crisis.
trigger: "Auto-triggered by Survival system activation (Cluster #14 → P509 → #15 → #8). Not manually invoked."
created: 2026-03-15
version: 1.0
---

# Protocol 529: Survival HUD (Crisis Output Mode)

> **Problem Statement**: Under extreme stress, nuanced multi-paragraph output is cognitive poison. The system has no mechanism to automatically strip output to bare essentials when the Survival cognitive system activates. Protocol 524 (Conviction-Decisiveness Split) mandates high decisiveness, but it's not enforced at the output format level.

## Trigger Conditions

This protocol activates **automatically** when intent classification routes to the **🛡️ Survival** cognitive system (Priority 1 in ARCHITECTURE.md).

### Detection Heuristics

| Category | Keywords / Signals |
| :--- | :--- |
| **Explicit Crisis** | "emergency", "crisis", "I'm fucked", "help now", "what do I do", "SOS" |
| **Financial Ruin** | "margin call", "liquidated", "stop out", "blown account", "bankrupt" |
| **Legal Threat** | "lawsuit", "police", "arrested", "threat", "blackmail", "cease and desist" |
| **Psychological Crisis** | "can't breathe", "losing it", "panic", "breaking down", circuit-breaker trigger words |
| **Ruin-Adjacent** | Any context triggering Law #1 probability check (P(ruin) > 5%) |

**Rule**: If ANY detection heuristic matches AND intent classification confirms Survival routing → activate HUD. When uncertain, default to HUD (false positive is less dangerous than false negative).

## HUD Output Format

When activated, ALL conversational output is replaced by this exact structure:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ SURVIVAL MODE ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THREAT:    [One-line threat description]
P(RUIN):   [X%] — [basis: Law #1 calc or stated]
SEVERITY:  [CRITICAL / HIGH / MODERATE]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL PATH:
  1. [Immediate action — within minutes]
  2. [Short-term action — within hours]
  3. [Stabilization action — within days]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DO NOT:
  - [Anti-pattern 1 — the most common mistake in this crisis type]
  - [Anti-pattern 2]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTE? (confirm before acting)
```

## Hard Rules

1. **Maximum 15 lines total.** No exceptions. If the crisis is complex, prioritize the FIRST action.
2. **Zero hedging language.** "You might consider" is BANNED. "It depends" is BANNED. Protocol 524 (Conviction-Decisiveness Split) is mandatory: HIGH decisiveness, defer conviction to user via EXECUTE? gate.
3. **Every action is numbered and sequenced.** The user does Step 1, then Step 2, then Step 3. No branching.
4. **"DO NOT" section is mandatory.** Under panic, people make the most common mistake. Name it. Prevent it.
5. **EXECUTE? gate preserves Law #0.** The system recommends. The user decides. This is not autopilot.
6. **No reasoning display.** The 4-track multi-track reasoning still runs internally, but only the converged output appears. The user doesn't need to see Track B (Adversarial) under crisis — they need the answer.

## Severity Classification

| Level | Criteria | Time Horizon |
| :--- | :--- | :--- |
| **CRITICAL** | P(ruin) > 5% OR irreversible action within minutes | Minutes |
| **HIGH** | P(ruin) 1-5% OR significant loss within hours | Hours |
| **MODERATE** | P(ruin) < 1% but crisis demands immediate attention | Days |

## Follow-Up Protocol

After the user confirms EXECUTE or asks a follow-up question:

1. **If follow-up is still crisis-mode**: Continue in HUD format. Do not revert to prose.
2. **If follow-up is analytical** ("why?", "explain", "what if"): Switch to normal multi-track output with a header note: `🛡️ Survival Mode → Analysis Mode. HUD available on request.`
3. **If crisis is resolved**: User explicitly says it's resolved, OR next query routes to a non-Survival system → exit HUD, return to normal output.

## Pre-Positioned Playbook Integration

If `threatPlaybooks.md` exists in the memory bank (see Intervention 4), the HUD should:

1. Match the detected threat category to the playbook
2. Pull the pre-positioned CRITICAL PATH from the playbook (instead of generating one from scratch)
3. This reduces HUD generation latency to near-zero for known threat types

## Integration Points

| Workflow | Where | What |
| :--- | :--- | :--- |
| `/start` (start.md) | Phase 3, Cognitive Systems routing table | Add `→ P529 HUD output` to Survival row |
| `/ultrastart` (ultrastart.md) | Phase 6, Multi-Track Reasoning | Note: internal reasoning still runs 4-track, but HUD output replaces conversational synthesis |

## Design Rationale

- **Why auto-trigger?** Under crisis, the user won't remember to type `/survival`. The system must detect and adapt.
- **Why 15 lines max?** Cognitive load research: under stress, humans process ~3-5 action items reliably. 15 lines accommodates header + 3 actions + 2 anti-patterns + gate.
- **Why ban hedging?** Protocol 524 lesson: "Setup: [spec]. Your calibration: Y/N?" is more useful than "You might consider..." The EXECUTE? gate handles uncertainty — the words before it must be decisive.
- **Why keep EXECUTE?** Law #0 (Subjective Utility Supreme). Even in crisis, the user's judgment on their own situation may override the system's recommendation. The gate is non-negotiable.

## Relationship to Other Protocols

- **Protocol 524 (Conviction-Decisiveness Split)**: P529 is the output-format enforcement of P524's principle. P524 says "be decisive"; P529 specifies exactly what decisive output looks like.
- **Circuit Breaker**: If the crisis detection matches circuit-breaker triggers AND cumulative threshold is met, circuit-breaker fires first (forced pause). P529 handles the acute response before/after circuit-breaker assessment.
- **Protocol 528 (Execution Enforcement)**: Different domain. P528 handles chronic avoidance. P529 handles acute crisis. They don't overlap.

## Anti-Patterns

- ❌ Displaying reasoning tracks in HUD mode (the user doesn't need Track B under panic)
- ❌ Adding caveats or disclaimers to CRITICAL PATH steps (hedging under crisis = paralysis)
- ❌ Generating more than 3 CRITICAL PATH steps (cognitive overload)
- ❌ Staying in HUD mode after the crisis is explicitly resolved (annoying, not helpful)
- ❌ Using HUD for non-crisis queries that happen to contain crisis keywords in a non-crisis context

## Tags

`#protocol` `#safety` `#survival` `#hud` `#crisis` `#output-format`
