---
description: Manage autonomous daemon agents — list, start, stop, and monitor background loops
created: 2026-03-31
---
# /daemon — Autonomous Loop Manager

> **Philosophy**: "I don't use Athena. I have Athena running."

## Usage

```text
/daemon list              — Show active daemons and their status
/daemon start <workflow> <interval> — Start a new daemon loop
/daemon stop <name>       — Stop a running daemon
/daemon log <name>        — Show recent output for a daemon
```

## Quick Start

```text
/daemon start /reindex 60m     — Sync memory to Supabase every hour
/daemon start /needful 24h     — Autonomous workspace hygiene daily
/daemon start /check 5m        — Continuous verification loop
```

## Implementation

Read the full skill: [daemon-loop/SKILL.md](file:///Users/[AUTHOR]/Project Athena/.agent/skills/daemon-loop/SKILL.md)

## Steps

1. Parse the subcommand (`list`, `start`, `stop`, `log`)
2. For `start`: validate the workflow is daemon-eligible (idempotent, non-interactive)
3. Register in `.agent/temp/daemons.json`
4. Execute the loop (cron or in-session, per daemon-loop skill)
5. Log output to `.agent/temp/daemon.log`

## Safety

- Only idempotent workflows can be daemonized
- No git mutations without explicit pre-auth
- Max autonomous window: 8 hours
- Checkpoint after each iteration
