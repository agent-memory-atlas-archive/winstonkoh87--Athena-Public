---
name: conditional-skill-activation
description: Protocol for path-based and context-triggered skill activation to reduce prompt bloat.
created: 2026-03-31
source: "Claude Code loadSkillsDir.ts — conditional skills via paths frontmatter"
---

# Protocol 530: Conditional Skill Activation

> **Source**: Claude Code `loadSkillsDir.ts` (2026-03-31).
> **Problem**: All 30+ skills are listed in the system prompt → ~4K tokens of skill metadata that's irrelevant 90% of the time.
> **Solution**: Skills with a `context_trigger` frontmatter field are **dormant by default** and only activate when matching conditions are met.

---

## Frontmatter Schema

Add these optional fields to any `SKILL.md`:

```yaml
---
name: skill-name
description: What it does

# CONDITIONAL ACTIVATION
context_trigger:
  paths:            # Glob patterns — skill activates when matching files are touched
    - "*.sql"
    - "supabase/**"
  topics:           # Keyword triggers — skill activates when these appear in user messages
    - "database"
    - "migration"
    - "schema"
  projects:         # Project codes — skill activates when these projects are active
    - "E9"
    - "A29"
  always_active: false  # Override: if true, always in prompt (default for skills without context_trigger)
---
```

## Activation Rules

### During Session Boot (`/start`)

1. Load all skill frontmatter (name, description, context_trigger)
2. Partition into:
   - **Unconditional skills** (no `context_trigger` or `always_active: true`) → Include in prompt immediately
   - **Conditional skills** (has `context_trigger`) → Store in dormant registry
3. Check initial context against dormant skills:
   - Scan `activeContext.md` for active project codes → match against `projects:`
   - Scan recent file history → match against `paths:` globs

### During Session (Dynamic Activation)

When a user message or tool result arrives:

1. Check the message content against all dormant skills' `topics:` keywords
2. Check any file paths touched against dormant skills' `paths:` globs
3. If a match is found:
   - Move skill from dormant → active
   - Log: `[skills] Activated conditional skill '{name}' (matched: {trigger})`
   - Skill is now available for invocation

### Once Activated = Stays Active

A skill, once activated, remains active for the rest of the session. No deactivation mid-session.

## Which Skills Should Be Conditional?

| Category | Skills | Trigger Type |
|----------|--------|-------------|
| **Domain-specific** | `statistical-analysis`, `trade-journal-analyzer`, `zenith-execution` | `topics:` + `projects:` |
| **Tool-specific** | `seo-auditor`, `visual-verify-ui` | `topics:` |
| **Workflow-specific** | `academic-delivery`, `academic-humanizer` | `projects:` (academic engagements only) |
| **Always Active** | `context-compactor`, `red-team-review`, `micro-commit` | No trigger (always loaded) |
| **Rare/Expensive** | `marketing-swarm`, `git-worktree-swarm` | `topics:` |

## Expected Token Savings

| State | Skills in Prompt | ~Tokens |
|-------|-----------------|---------| 
| **Before** (all loaded) | 30+ | ~4,000 |
| **After** (conditional) | ~10 unconditional + 0-5 activated | ~1,500-2,500 |
| **Savings** | — | **~40-60%** |

## Implementation Notes

- This protocol is **advisory** for human-in-the-loop agents (Antigravity, Cursor). The agent reads all skill metadata from AGENTS.md; the filtering happens at prompt construction time.
- For true autonomous agents (worktree swarms), conditional activation prevents prompt pollution across workers that only need 2-3 skills each.
- The `paths:` glob evaluation uses the same ignore-pattern matching as `.gitignore`.

---

## Migration Path

1. **Phase 1** (NOW): Document which skills are conditional candidates (this file)
2. **Phase 2**: Add `context_trigger` frontmatter to 15+ skill SKILL.md files
3. **Phase 3**: Update `/start` workflow to partition skills at boot
4. **Phase 4**: Add dynamic activation hook to main query loop

---

`#protocol` `#architecture` `#skill-system` `#token-optimization`
