---
description: Multi-project switchboard — view, add, switch, close, and triage active projects
created: 2026-03-09
last_updated: 2026-03-09
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: false
---

# /project — Project Switchboard

> **Latency Profile**: LOW (~1K tokens)
> **Philosophy**: Make project state explicit. Make context-switching instant.

// turbo

## Commands

### `/project` (default — Dashboard)

1. Load `.context/PROJECTS.md`
2. **Triage**: Sort active projects by urgency tier (🔴 → 🟠 → 🟡 → 🟢 → 🔵), break ties by EV descending
3. **Dependency check**: Skip blocked items, surface what unblocks them
4. **Cross-zone check**: If any Internal project (health, energy) is flagged as degraded, note capacity risk for External projects
5. **Output**:
   - Show **External** table first (revenue-generating), then **Internal**
   - Highlight the **top unblocked item** as "Recommended next"
   - If all 🔴/🟠 items are blocked, surface the blocker reasons
6. Update `Last triaged:` timestamp

### `/project add <name>`

Guided intake (ask each, accept one-line answers):

1. **Zone**: Internal (personal) or External (client/revenue)?
2. **Domain**: 💼 Client | 📣 Growth | 📈 Trading | ⚙️ Execution | 🔄 Maintenance | 🧠 Personal | 🏠 Life
3. **Phase**: Not Started (default) | Phase 1-4
4. **Urgency**: 🔴 TODAY | 🟠 URGENT | 🟡 This Week | 🟢 Backlog | 🔵 Someday
5. **EV**: What's the payoff? (dollar amount, "Learning", "Distribution", "Process", etc.)
6. **Next Action**: One atomic action (GTD-style)
7. **Depends On**: Any blocker or cross-project dependency? (default: —)

Append to the correct section (Internal or External) in `PROJECTS.md`. Assign `I<N>` or `E<N>` ID.

### `/project switch <ID>` (e.g., `E3`, `I1`)

1. Read `PROJECTS.md` to get project name and domain
2. Run Exocortex search: `python3 Athena-Public/examples/scripts/smart_search.py "<project name>" --limit 3 --include-personal`
3. Load the most recent session log mentioning this project
4. **Output**:
   - Project: `<name>`
   - Phase: `<phase bar>`
   - Last session: `<summary of last work>`
   - Next action: `<from PROJECTS.md>`
   - Related context: `<Exocortex top 3 results>`
5. Carry on — the agent is now in this project context

### `/project close <ID>`

1. Ask for **outcome** (one line: "Delivered, $250" or "Cancelled — scope changed")
2. Move the row from Active → Completed table with today's date and outcome
3. Renumber remaining active projects

### `/project triage`

Full re-rank of all active projects:

1. For each project, ask: "Has urgency changed since last triage?" (batch — show all, accept corrections)
1b. For each dependency, ask: "Still blocked?" — clear resolved dependencies
2. Re-sort by urgency tier × EV
3. Identify **blocked** items and surface what unblocks them
4. Update `Last triaged:` timestamp
5. **Output**: Re-ranked table + "Top 3 actions for today"

---

## Integration Points

- **`/start`**: `PROJECTS.md` is loaded on-demand when the user asks "what should I work on", "project", or "switch context"
- **`/end`**: Prompt to update `PROJECTS.md` — advance phases, update next actions, adjust urgency for shifted deadlines
- **`activeContext.md`**: Checkpoint blocks (`[[ S__ |`) should reference `PROJECTS.md` for project-level state instead of inlining `@pending` lists. Session-level `@decided` and `@work_debt` stay in checkpoints.

---

## Design Notes

- **No code, no scripts**. Pure markdown state + agent workflow. Works on any AI provider.
- **Phase bars are visual shorthand**, not numeric. The agent updates them by editing the markdown table.
- **EV column forces prioritization honesty**. "Someday/Maybe" projects with no EV articulated are 🔵 by default.
- **Triage is a verb, not a state**. The switchboard goes stale without periodic re-ranking. `/project triage` or `/end` keeps it fresh.

---

## Tagging

# workflow #project-management #gsd #multi-project
