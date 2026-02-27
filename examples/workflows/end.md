---
description: Close session and update System Prompt files with new insights (lightweight)
created: 2025-12-09
last_updated: 2026-02-23
model: default
temperature: 0.5
tools:
  read: true
  write: true
  bash: true
  search: true
---

# /end — Session Close Script (Lightweight)

> [!IMPORTANT]
> **Manual Synthesis Required.** The `shutdown.py` orchestrator will **FAIL** and abort if it detects placeholders (`...`) in the Agenda, Decisions, or Action Items. You MUST synthesize the session content before initiating technical closure.

> **Latency Profile**: LOW (~2K tokens)  
> **Core Principle**: "Fast close. Deep work deferred to /refactor."  
> **Change Log**: 2025-12-27 — Added Canonical Memory Sync (Protocol 215).
> **Change Log**: 2025-12-18 — Moved heavy audits to `/refactor` for faster session close.

## 1. Session Log Finalization

> **Rule**: Slow down to speed up. Synthesize deeply.
> **Philosophy**: A bad end = A bad next start.

1. **Read** the current session log (created at `/start`).
2. **Synthesize** key bullets (Do NOT copy-paste; distill):
   * Main topics covered
   * Key decisions made (Update `decisionLog.md` if critical)
   * Notable insights (if any)
3. **Canonical Check**:
   * "Did we learn a new fact that contradicts `.context/CANONICAL.md`?"
   * If YES: Update Canonical Memory immediately.
4. **Add** closure block:

```markdown
## Session Closed

**Status**: ✅ Closed  
**Time**: [HH:MM SGT]
```

## 1.2 Canonical Memory Sync (Protocol 215)

> **Rule**: Check for stale data. Update the Materialized View.

1. **Diff**: Did we establish new costs, decisions, or facts that contradict `.context/CANONICAL.md`?
2. **Sync**: If yes, **update `.context/CANONICAL.md` immediately**.
3. **Log**: "Updated Canonical: [Fact A] -> [Fact B]"

## 1.3 Session Checkpoint (S__)

> **Rule**: Generate a compressed state block for the next session.

1. **Context**: What *must* the next session know immediately?
2. **Generate**:

   ```text
   [[ S__ |
   @focus: [Current Task/Project]
   @status: [Active/Paused]
   
   @decided: [Key Decision A], [Key Decision B]
   @pending: [Next Step X], [Next Step Y]
   
   !checkpoint ]]
   ```

3. **Append**: Add this block to the end of the Session Log.

## 1.4 Self-Reflection & Learning Extraction

> **Rule**: Before ending, ask yourself: *"What did I learn this session and how can I incorporate my learnings into this workspace and into future sessions?"*
> **Philosophy**: The AI is the second strand of the dual helix. If it doesn't learn, the helix stalls.

**MANDATORY** — Do NOT skip this step. Work on it before formal closure.

1. **Reflect**: Answer these questions honestly:
   * What friction/mistakes did I encounter? (e.g., wrong remote, leaked files, dead links)
   * What new patterns or constraints did I discover? (e.g., "always sync public → private")
   * What would make the next session start smarter?

2. **File the learnings** — Pick the right destination:

   | Learning Type | Where to File |
   |:-------------|:-------------|
   | New workflow step | Update the relevant `.agent/workflows/*.md` |
   | New constraint/rule | Update `AGENTS.md` or `.framework/` modules |
   | New protocol | Create/update `.agent/skills/protocols/` |
   | Reusable pattern | Add to `.context/CANONICAL.md` or `PROTOCOL_SUMMARIES.md` |
   | Bug/tech debt | Append to `.context/TECH_DEBT.md` |

3. **Commit the learnings** before running shutdown. These are high-value — don't defer them.

4. **Log**: Add a brief "Session Learnings" section to the session log:

   ```markdown
   ## Session Learnings
   - [Learning 1]: Filed to [destination]
   - [Learning 2]: Filed to [destination]
   ```

## 1.4.5 Bilateral Repo Sync Check

> **Rule**: Public and private repos must stay in sync. Changes flow both directions.
> **Philosophy**: The repos are two expressions of the same system. Drift = debt.

**MANDATORY** — Check BOTH directions before shutdown.

### Direction 1: Private → Public (with Privacy Filter)

If you modified shared files in the **private** repo this session, sync to public:

```bash
# Check what changed in private this session
cd /Users/winstonkoh/Desktop/Project\ Athena
git diff --name-only HEAD~1
```

**What to sync**:

| Sync? | File/Directory | Notes |
|:------|:-------------|:------|
| ✅ Yes | `docs/*.md` | Strip personal data before copying |
| ✅ Yes | `AGENTS.md` | Public version should only list shipped modules |
| ✅ Yes | `wiki/*.md` | Copy to wiki repo too |
| ⚠️ Carefully | `.agent/workflows/*.md` | Only if workflow is public-relevant |
| ❌ Never | `.framework/` full modules | Public has template versions only |
| ❌ Never | `.context/` | Private state, memories, profiles |
| ❌ Never | `User_Profile*.md` | Personal data |

**Privacy filter** — before copying ANY file to public, run the privacy scanner:

```bash
cd /Users/winstonkoh/Project\ Athena/Athena-Public
python3 .github/scripts/privacy_scan.py <file_to_sync>
```

If it blocks, **scrub personal content** or **do not sync**.

### Direction 2: Public → Private

If you modified shared files in the **public** repo this session, sync to private:

```bash
# Check what changed in public this session
cd /Users/winstonkoh/Desktop/Project\ Athena/Athena-Public
git diff --name-only HEAD~1
```

Copy changed `docs/`, `AGENTS.md`, and wiki files to the private repo. No filter needed (private is the superset).

> See also: `/push-public` workflow → "Post-Push: Sync Back to Private" section.

## 1.5 Shutdown Orchestrator

> **Rule**: Single script handles harvest check, git commit, and compliance.

// turbo

```bash
python3 .agent/scripts/shutdown.py
./Athena-Public/scripts/launch_athena.sh --stop
```

**What it does**:

1. Harvest check (§0.7 enforcement)
2. Git commit & push (triggers cloud sync)
3. Protocol compliance report
4. Reset violations for next session

**Output**: "✅ Session closed. Time: [HH:MM SGT]"

---

## What Moved to /refactor

> **Philosophy**: `/end` is for fast exit. `/refactor` is for deep maintenance.

| Previously in /end | Now in /refactor |
|--------------------|-----------------|
| `batch_audit.py` | ✅ Moved |
| `orphan_detector.py` verification gate | ✅ Moved |
| Living Doc metabolic scans | ✅ Moved |
| Cross-pollination scans (Protocol 67) | ✅ Moved |
| GraphRAG re-indexing | Already in /refactor |
| `compress_memory.py` | ✅ Moved |
| `compress_sessions.py` | ✅ Moved |
| `supabase_sync.py` | ✅ Moved |

**When to use /refactor**:

* After multiple light sessions
* Before major new work phases
* Weekly maintenance (recommended)

---

## Summary

| Phase | Action | Tokens |
|-------|--------|--------|
| 1. Session Log | Quick finalize | ~300 |
| 1.5 Harvest Check | Gate unharvested knowledge | ~100 |
| 2. Git Commit | Commit changes | ~100 |
| 3. Compliance Report | Surface protocol violations | ~100 |
| **Total** | — | **~600** |

---

## References

* [/refactor](file:///Users/winstonkoh/Project Athena/Athena-Public/examples/workflows/refactor.md) — Deep system optimization (audits, scans, integrity)
* [/save](file:///Users/winstonkoh/Project Athena/Athena-Public/examples/workflows/save.md) — Mid-session checkpoint

---

## Tagging

# workflow #automation #end #lightweight
