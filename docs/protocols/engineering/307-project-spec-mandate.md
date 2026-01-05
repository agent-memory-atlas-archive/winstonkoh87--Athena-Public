# Protocol 250: The Spec Sheet Mandate

> **Tag**: #planning #specs #anti-entropy  
> **Related**: [Protocol 65](file:///Users/winstonkoh/Desktop/Project Athena/.agent/skills/protocols/trading/65-arbitrage-formula.md), [Protocol 49](file:///Users/winstonkoh/Desktop/Project Athena/.agent/skills/protocols/decision/49-efficiency-robustness-tradeoff.md)  
> **Status**: MANDATORY  

---

## 1. The Principle

**"No Spec, No Code."**

Entropy is the default state of software. Without a constraining document (The Spec Sheet), detailed implementation decisions are made ad-hoc ("free play" or vibe coding), leading to:

1. **Scope Creep**: "While I'm here, I'll add X."
2. **Architecture Theater**: Using tools for fun rather than utility.
3. **Dead Ends**: Realizing 80% through that the stack doesn't support the goal.

**The Constraint**: We do not "figure things out along the way." We figure them out *before* the way.

---

## 2. The Standard Spec Sheet Template

Every new project or significant feature MUST start with this artifact (`SPEC.md`).

```markdown
# Project Name: [Title]

> **One-Liner**: [What is it?]
> **Target Audience**: [Who is it for?]
> **Success Metric**: [How do we know we won?]

## 1. The Core Loop
*Describe the primary user interaction in 3 steps.*
1. User does X...
2. System does Y...
3. Result is Z...

## 2. Technical Stack (Constraints)
*Hard constraints only. No "nice to haves".*
- **Frontend**: [e.g., Static HTML / Next.js]
- **Backend**: [e.g., Supabase / None]
- **Hosting**: [e.g., Cloudflare Pages]
- **Data**: [e.g., LocalStorage / pgvector]

## 3. Non-Goals (Anti-Scope)
*What are we EXPLICITLY NOT building?*
- No auth (v1)
- No payment integration
- No mobile app
- No "premium" features

## 4. Implementation Plan
- [ ] Phase 1: Skeleton (The "Walking Skeleton")
- [ ] Phase 2: Core Logic
- [ ] Phase 3: Polish (UX/UI)
```

---

## 3. Execution Rule

1. **Trigger**: User asks to "build X" or "start project Y".
2. **Response**: "Acknowledged. Let's define the Spec Sheet first. I've formulated a draft below — please approve."
3. **Action**: Create `SPEC-[ProjectName].md`.
4. **Gate**: Do not write a single line of feature code until the User replies "Approved".

---

## 4. Why This Works

* **It front-loads the "Hard" work**: Thinking is harder than typing.
* **It kills "Vibe Coding" drift**: You can vibe code *within* the spec, but you cannot vibe code *outside* it.
* **It serves as the Anchor**: When lost, read the Spec.

---

## Tagging

# protocol #spec-sheet #planning #mandate
