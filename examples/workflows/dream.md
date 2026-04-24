---
description: Background memory consolidation — the "Dream" pass. Stolen from Claude Code autoDream system (2026-04-01).
created: 2026-04-01
last_updated: 2026-04-01
---

# /dream — Memory Consolidation Daemon

> **Source**: Claude Code `services/autoDream/consolidationPrompt.ts` (leaked 2026-03-31).
> **Philosophy**: "Synthesize what you've learned recently into durable, well-organized memories so that future sessions can orient quickly."

## What This Is

A reflective pass over memory files — distinct from `/end` session close. While `/end` writes session logs and propagates `[S]`/`[U]` markers, `/dream` is a *background consolidation* that merges, deduplicates, prunes, and resolves contradictions across the entire memory system.

**`/end` = record what happened NOW. `/dream` = consolidate what matters ACROSS sessions.**

---

## Three-Gate Trigger

All three gates must pass before a dream runs:

| Gate | Condition | Rationale |
|------|-----------|-----------|
| **Time** | ≥ 24 hours since last dream | Prevents over-dreaming |
| **Session** | ≥ 5 sessions since last dream | Ensures enough new signal |
| **Lock** | No concurrent dream running | Prevents duplicate consolidation |

Track state in `.agent/temp/dream_state.json`:

```json
{
  "last_dream": "2026-04-01T02:00:00+08:00",
  "sessions_since_dream": 0,
  "lock": false
}
```

---

## The Four Phases

### Phase 1 — Orient

- `ls` the memory directories (`.context/memories/`, `.context/`)
- Read `activeContext.md` to understand current state
- Skim existing files to improve them rather than creating duplicates
- Review recent session logs in `session_logs/`

### Phase 2 — Gather Recent Signal

Find new information worth persisting. Sources in priority order:

1. **Session logs** (`session_logs/*.md`) — the append-only stream from `/end`
2. **Drifted memories** — facts in `.context/` files that contradict what's now in the codebase
3. **Protocol/skill usage** — check `protocol_heatmap.json` for protocols that were invoked but have no corresponding learnings

> Don't exhaustively read everything. Look only for things you already suspect matter.

### Phase 3 — Consolidate

For each thing worth remembering:

- **Merge** new signal into existing topic files rather than creating near-duplicates
- **Convert** relative dates ("yesterday", "last week") to absolute dates
- **Delete** contradicted facts — if today's investigation disproves an old memory, fix it at the source
- **Propagate** any un-propagated `[S]` or `[U]` markers that `shutdown.py` may have missed

### Phase 4 — Prune and Index

- Keep `activeContext.md` checkpoint history manageable (compact sessions older than last 5)
- Keep `CANONICAL.md` entries tight — remove stale pointers, resolve contradictions
- Keep `TAG_INDEX.md` accurate — remove dead links, add new tags
- Resolve contradictions — if two files disagree, fix the wrong one

---

## Safety Rules

- **READ-ONLY for source code** — dream can read the codebase but must NOT modify any source files
- **CAN write to**: `.context/`, `.agent/temp/`, session logs
- **CANNOT**: commit, push, or modify anything outside the memory system
- **Blocking budget**: 15 seconds max for any single operation (stolen from KAIROS)
- **Total budget**: 5 minutes max per dream pass

---

## Daemon Registration

Add to `.agent/temp/daemons.json`:

```json
{
  "name": "memory-dream",
  "workflow": "/dream",
  "interval": "24h",
  "trigger": "three-gate",
  "last_run": null,
  "status": "registered"
}
```

---

## Manual Invocation

User can trigger a dream manually:

```
/dream
```

This bypasses the time and session gates (but still respects the lock gate).

---

## Output

Return a brief summary of what was consolidated, updated, or pruned:

```
🌙 Dream complete:
- Consolidated 3 session logs into existing memory files
- Updated CANONICAL.md: removed stale entry for Protocol 319 (archived)
- Resolved contradiction: activeContext.md said Project E9 was "paused" but session log 2026-03-31 shows active work
- Pruned TAG_INDEX.md: removed 2 dead links
- No action needed on 12 other memory files (already tight)
```

If nothing changed: "🌙 Dream pass: memories are already tight. No changes."

---

## References

- [/end](file:///Users/[AUTHOR]/Project Athena/.agent/workflows/end.md) — Session close (writes raw signal)
- [/daemon](file:///Users/[AUTHOR]/Project Athena/.agent/workflows/daemon.md) — Daemon management
- [daemon-loop](file:///Users/[AUTHOR]/Project Athena/.agent/skills/daemon-loop/SKILL.md) — Background loop infrastructure
- [Protocol 215 — Canonical Memory](file:///Users/[AUTHOR]/Project Athena/.agent/skills/protocols/architecture/215-canonical-memory.md)

---

`#workflow` `#memory` `#consolidation` `#stolen-claude-code`
