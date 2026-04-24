---
description: Guard protocol to prevent destructive pushes to the [AUTHOR]87.github.io repo
created: 2026-02-25
---

# Website Deploy Guard — [AUTHOR]87.github.io

## HARD RULES (No Exceptions)

1. **NEVER `git push --force`** to `[AUTHOR]87/[AUTHOR]87.github.io`. EVER.
2. **NEVER `git init`** inside `dist/` or any build output folder. That wipes history.
3. **ALWAYS clone the repo fresh** from GitHub before making changes.
4. **ALWAYS push SOURCE CODE** (src/, package.json, astro.config.mjs), NOT pre-built dist. Cloudflare Pages runs `npm run build` itself.
5. **ALWAYS verify history** with `git log --oneline -5` before pushing.

## Correct Deploy Workflow

```bash
# 1. Clone fresh
cd /tmp && rm -rf wk-deploy
git clone https://github.com/[AUTHOR]87/[AUTHOR]87.github.io.git wk-deploy

# 2. Copy updated source files from workspace
cp "/Users/[AUTHOR]/Project Athena/[AUTHOR]87.github.io/src/pages/index.astro" /tmp/wk-deploy/src/pages/
cp <other changed files>

# 3. Verify history is intact
cd /tmp/wk-deploy && git log --oneline -5

# 4. Commit and push (NEVER --force)
git add -A && git commit -m "feat: <description>"
git push origin main

# 5. Clean up
rm -rf /tmp/wk-deploy
```

## Two-Repo Architecture

| Repo | Purpose | Deploy |
|------|---------|--------|
| `[AUTHOR]87/Athena` (private) | Tracks source via `git add -f` | Manual |
| `[AUTHOR]87/[AUTHOR]87.github.io` | Cloudflare Pages (auto-builds from source) | Push triggers Cloudflare build |
