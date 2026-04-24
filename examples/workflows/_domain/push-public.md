---
description: Safely push changes to the public Athena-Public GitHub repo
created: 2026-02-24
model: default
tools:
  read: true
  write: false
  bash: true
  search: false
---

# /push-public — Push to Public Repo

> **Purpose**: Safely commit and push changes to `Athena-Public` (public GitHub).
> **Risk Level**: HIGH — public-facing. Secrets = ruin.

## Pre-Flight Checks

// turbo

1. **Verify working directory**: `cd /Users/[AUTHOR]/Project\ Athena/Athena-Public`

// turbo
2. **Verify remote**: Confirm push target is `public` (NOT `origin` which is the private repo):

   ```bash
   git remote get-url public
   ```

   Expected: `https://github.com/[AUTHOR]87/Athena-Public.git`

// turbo
3. **Secret scan**: Run a grep for leaked credentials before committing:

   ```bash
   git diff --cached | grep -iE 'sk-proj-|AIzaSy|eyJhbGci|api_key\s*=\s*["\047][a-zA-Z0-9]' || echo "✅ No secrets detected"
   ```

// turbo
4. **Count verification** (auto-patch protocol/script counts if drifted):

   ```bash
   cd /Users/[AUTHOR]/Project\ Athena/Athena-Public && \
   PROTOCOLS=$(find examples/protocols -name '*.md' -type f | wc -l | tr -d ' ') && \
   SCRIPTS=$(find examples/scripts -name '*.py' -type f | wc -l | tr -d ' ') && \
   echo "📊 Protocols: $PROTOCOLS | Scripts: $SCRIPTS" && \
   echo "Verify these match README claims (use 'X+' format, e.g. 135+ for 138 actual)"
   ```

## Commit & Push

1. **Stage changes**:

   ```bash
   cd /Users/[AUTHOR]/Project\ Athena/Athena-Public && git add -A
   ```

// turbo
5. **Review staged diff** (MANDATORY — never skip):

   ```bash
   cd /Users/[AUTHOR]/Project\ Athena/Athena-Public && git diff --cached --stat
   ```

1. **Commit**:

   ```bash
   cd /Users/[AUTHOR]/Project\ Athena/Athena-Public && git commit -m "<message>"
   ```

2. **Push to PUBLIC remote** (NOT origin):

   ```bash
   cd /Users/[AUTHOR]/Project\ Athena/Athena-Public && git push public main
   ```

## ⛔ Critical Rules

| Rule | Why |
|------|-----|
| **Always push to `public`** | `origin` = private `Athena.git`. Wrong target = private data leaked. |
| **Always run secret scan** | Step 3. Non-negotiable. |
| **Never commit `.env` or `.context/`** | Gitignored, but verify with `git status` before pushing. |
| **Review `--stat` before pushing** | Catches unexpected files (e.g. personal data, large binaries). |

## Git Remote Map

```
origin  → https://github.com/[AUTHOR]87/Athena.git         (PRIVATE)
public  → https://github.com/[AUTHOR]87/Athena-Public.git  (PUBLIC)
```

## Post-Push: Sync Back to Private

> **MANDATORY**: Public repo changes must be mirrored to the private repo to keep capabilities in sync.

After pushing to public, copy any modified shared files back to the private repo:

```bash
# Sync shared docs (adjust paths as needed)
cp Athena-Public/docs/<changed_file>.md docs/
cp Athena-Public/AGENTS.md AGENTS.md  # Only if AGENTS.md was changed
```

**What to sync**: `docs/` content, `AGENTS.md` changes, wiki source files.
**What NOT to sync**: `.framework/` templates (private has full versions), public-only files like `CONTRIBUTING.md`.

Commit the synced files to the private repo separately.

## Tagging

# workflow #git #public #security
