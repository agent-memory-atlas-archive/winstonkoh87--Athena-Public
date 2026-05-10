---
created: 2026-05-11
last_updated: 2026-05-11
steal_source: "affaan-m/everything-claude-code (178K ⭐), autonomous-loops skill, De-Sloppify Pattern"
context_trigger: "TDD, test generation, code cleanup, refactor, implementation with tests, multi-step coding task"
---

# Protocol 541: De-Sloppify Pass

> **Purpose**: Eliminate quality degradation caused by negative instructions. Use a separate cleanup pass instead of constraining the implementer.
> **Trigger**: Any multi-step coding workflow where an AI generates both implementation and tests.

---

## The Failure Pattern

```
User: "Implement feature X with TDD. Don't add unnecessary tests."
AI:   * Becomes hesitant about ALL testing
      * Skips legitimate edge case tests
      * Quality degrades unpredictably
Result: Worse code AND worse tests than if no constraint was given.
```

**Root cause**: Negative instructions create downstream degradation. The model can't reliably distinguish "unnecessary" from "necessary" — it errs on the side of skipping.

---

## The Solution: Two-Pass Pattern

Instead of constraining the Implementer, let it be thorough. Then run a **separate cleanup agent in a fresh context**.

### Pass 1: Implement (unconstrained, thorough)

Let the agent write comprehensive code with full tests. No negative instructions.

### Pass 2: De-Sloppify (focused cleanup, fresh context)

A dedicated pass that removes ONLY provably unnecessary artifacts:

```
□ Tests that verify language/framework behavior (not business logic)
□ Redundant type checks the type system already enforces
□ Over-defensive error handling for impossible states
□ Console.log / print statements
□ Commented-out code
□ Dead imports
```

**Critical**: Run the test suite AFTER cleanup to verify nothing breaks.

---

## The Meta-Principle

> **Two focused agents outperform one constrained agent.**
>
> Rather than adding negative instructions which have downstream quality effects,
> add a separate cleanup pass. The cleanup agent has ONE job — removal —
> and no conflicting imperative to also create.

---

## When to Apply

| Scenario | Apply De-Sloppify? |
|----------|-------------------|
| TDD workflow (tests + implementation) | ✅ Yes — cleanup test slop |
| Multi-file feature implementation | ✅ Yes — cleanup defensive overengineering |
| Single-line fix | ❌ No — overkill |
| Documentation-only change | ❌ No — not applicable |
| Refactoring existing code | ⚠️ Maybe — if the refactor generates new patterns worth cleaning |

---

## Integration with Athena Workflows

- **`/plan`**: Add optional de-sloppify phase after implementation steps
- **`/vibe`**: Natural fit — vibe builds fast, de-sloppify cleans the slop
- **`416-agent-swarm`**: Each parallel agent's output gets a cleanup pass before merge
- **`/test`**: After test generation, a de-sloppify pass removes framework-testing tests

---

## Anti-Patterns

- ❌ Using negative instructions to constrain generation quality ("don't add X", "avoid Y")
- ❌ Running cleanup in the SAME context as implementation (author bias)
- ❌ Skipping the post-cleanup test run
- ❌ Applying de-sloppify to non-code artifacts (docs, configs)

---

## Tags

`#quality` `#protocol` `#cleanup` `#tdd` `#two-pass` `#steal`
