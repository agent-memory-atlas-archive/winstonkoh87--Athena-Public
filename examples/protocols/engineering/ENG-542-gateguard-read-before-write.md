---
created: 2026-05-11
last_updated: 2026-05-11
steal_source: "affaan-m/everything-claude-code (178K ⭐), GateGuard Fact-Forcing hook"
context_trigger: "file edit, code modification, schema change, refactor, multi-file change"
---

# Protocol 542: GateGuard — Read-Before-Write Enforcement

> **Purpose**: Eliminate blind edits by demanding investigation before the first modification to any file.
> **Trigger**: First edit to any file in a task — especially unfamiliar files.
> **Complements**: ENG-540 (Forward Trace Gate traces data flow). This protocol gates the **edit action itself**.

---

## The Failure Pattern

```
User: "Fix the user display name in the dashboard"
AI:   * Opens Dashboard.tsx
      * Edits the component
      * Breaks 4 other pages that import the same component
Result: Cascading failure from editing without understanding the dependency graph.
```

**Root cause**: The agent modified a file without understanding who imports it, what schemas it touches, or how the user's instruction maps to the codebase.

---

## The Three-Question Gate

Before the **first edit** to any file, answer these three questions:

```
□ 1. WHO imports this file?
     → Trace dependents. How many consumers does this module have?
     → A shared utility has high blast radius. A leaf component has low.

□ 2. WHAT data schemas does it touch?
     → What types, interfaces, database tables, API contracts flow through this file?
     → Changing a schema shape ripples to every consumer.

□ 3. WHAT did the user actually instruct?
     → Re-read the original request. Is this file even the right target?
     → Often the real fix is in a different file than the obvious one.
```

> **Rule**: If you can't answer all three, you're not ready to edit. Read more first.

---

## Severity Tiers

| File Type | Gate Strength | Rationale |
|-----------|--------------|-----------|
| Shared utility / library | 🔴 HARD gate — answer all 3 | Highest blast radius |
| API route / endpoint | 🟡 MEDIUM gate — answer 1 + 3 | Contract surface |
| Leaf component (no importers) | 🟢 SOFT gate — answer 3 only | Low blast radius |
| Config file | 🔴 HARD gate — answer all 3 + check linter config protection | See anti-pattern below |
| Test file | 🟢 SOFT gate — answer 3 only | Tests are self-contained |

---

## Config Protection Corollary

> **Never weaken a linter/formatter config to suppress warnings. Fix the code instead.**

When an agent encounters lint errors, the path of least resistance is modifying `.eslintrc`, `tsconfig.json`, or `.prettierrc` to suppress the warning. This is almost always wrong.

**Correct action**: Fix the code that violates the lint rule.
**Wrong action**: Disable the lint rule.

---

## Integration with Existing Protocols

| Protocol | Relationship |
|----------|-------------|
| **ENG-540** (Forward Trace Gate) | ENG-540 traces data flow. ENG-542 gates the edit action. Use 540 for "where does data go?", 542 for "should I touch this file?" |
| **ARC-158** (Entity Lookup Before Analysis) | ARC-158 looks up entities before analyzing them. ENG-542 looks up file context before editing it. Same principle, different scope. |
| **ARC-159** (Verification Before Claim) | 159 verifies claims. 542 verifies edit safety. Complementary. |
| **QUA-541** (De-Sloppify Pass) | GateGuard prevents blind edits. De-Sloppify cleans up after generation. Different phases of the same quality pipeline. |

---

## Anti-Patterns

- ❌ Editing a file without checking its importers first
- ❌ Modifying a shared utility based on a single consumer's needs
- ❌ Weakening linter/formatter configs instead of fixing code
- ❌ Assuming "I know this file" without verification (context may have compacted)
- ❌ Skipping the gate because "it's a small change" (small changes to shared files cause large breakages)

---

## Tags

`#engineering` `#protocol` `#safety` `#read-before-write` `#blast-radius` `#steal`
