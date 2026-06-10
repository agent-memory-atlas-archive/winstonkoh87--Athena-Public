---
description: Public Repo Synchronization & Sanitization (Allowlist Model)
created: 2025-12-25
last_updated: 2026-06-10
---

# /deploy — Public Repo Synchronization (Allowlist v2.0)

> **Architecture**: ALLOWLIST — only files explicitly listed in `public_manifest.yaml` are synced.
> **Predecessor**: v1.0 used a BLOCKLIST (`.syncignore`). TD-027 proved this fails silently — 11 skills with clinical data nearly went public.
> **Safety model**: Anything NOT listed = blocked. The safe direction of failure is over-blocking, not over-exposing.

---

## Step 0: Pre-Flight Gate (Mandatory)

Before ANY file transfer:

// turbo

```bash
bash .agent/scripts/pre_deploy_scan.sh ~/Athena-Public
```

**If Gate 1 (Secrets) fails**: ❌ ABORT. Fix violations first.
**If Gate 2 (PII) warns**: ⚠️ Review warnings. Proceed only if all flagged content is intentionally public.
**If Gate 3 (Blocked files) fails**: ❌ ABORT. Remove blocked files from staging.

> [!CAUTION]
> Do NOT bypass this gate. TD-027 happened because a manual review missed dense PII embedded in 8 skill files. The scanner catches what human review misses.

---

## Step 1: Allowlist Manifest Check

1. **Load** `.agent/config/public_manifest.yaml`
2. **Verify** every file being synced is present in the manifest
3. **If a file is NOT in the manifest**: It does NOT get synced. Period.

To add new files to the public release:
1. Add the path to `public_manifest.yaml`
2. Run `pre_deploy_scan.sh` against the specific file
3. Manually review for PII per §2 below
4. Commit the updated manifest

---

## Step 2: Sanitization Protocol (The "Consent Wall" Rule)

For any NEW file being added to the public manifest:

- **PII Stripping**: Remove all real names (e.g., specific people, specific clients). Replace with `[Client A]`, `[Target B]`, `[Creator]`.
- **Financial Stripping**: Remove exact dollar amounts (e.g., `$4,500`). Replace with `$X` or `$High-4-Figures`.
- **Location Stripping**: Remove specific addresses or non-public venues.
- **Tone Polish**: Remove internal "Commanding Officer" harshness if it reflects poorly on optics. Maintain "Strategic Realism."

### Explicit Exclusions (NEVER Sanitize — Just Block)

These categories are too personal even when sanitized:

- **Psychology Profiles** (e.g., `[PRIVATE_MODULE].md`) — Clinical data
- **Risk Playbooks** (e.g., `RISK_PLAYBOOKS.md`) — Internal governance
- **Private Case Studies** — Unless fully sanitized and generic
- **Behavioral State** (e.g., `accountability_status.json`, `trigger_log.md`) — Personal tracking <!-- pds:allow -->
- **Session Logs** — Raw session data with unfiltered personal content

---

## Step 3: Deployment Execution

- **Target Repo**: `~/Athena-Public`
- **Method**: Copy ONLY allowlisted files. Do NOT bulk-copy directories.

```bash
# For each file in public_manifest.yaml:
# 1. Verify file passes pre_deploy_scan.sh
# 2. Copy sanitized version to target repo structure
# 3. Verify diff before committing
```

**Structure Mapping**:
- `Athena/.agent/skills/protocols/` → `Athena-Public/docs/protocols/` (sanitized)
- `Athena/.context/memories/case_studies/` → `Athena-Public/docs/case-studies/` (sanitized, selected)
- Source code (`src/`, `scripts/`) → Direct copy (already public-safe)

---

## Step 4: Pre-Commit Review

Before committing to Athena-Public:

```bash
cd ~/Athena-Public
git diff --stat        # Review what changed
git diff               # Spot-check for any PII that slipped through
```

Only commit after confirming the diff is clean.

---

## Step 5: Git Synchronization

// turbo

1. `cd ~/Athena-Public`
2. `git add .`
3. `git commit -m "Deployment: [Summary of Changes]"`
4. `git push origin main`

---

## Step 6: Post-Deploy Verification

1. Confirm push succeeded
2. Run `pre_deploy_scan.sh` against `~/Athena-Public` one more time as post-deploy sanity check
3. Verify public URL if necessary

---

## Safety Net Stack

| Layer | Mechanism | Catches |
|-------|-----------|---------|
| **L1: Allowlist** | `public_manifest.yaml` | Anything not explicitly approved |
| **L2: Pre-deploy scanner** | `pre_deploy_scan.sh` | Secrets, PII patterns, blocked files |
| **L3: Pre-commit hook** | `.git/hooks/pre-commit` | Secrets in staged diffs (private repo) |
| **L4: Syncignore** | `.syncignore` (supplementary) | Legacy safety net — backup |
| **L5: Manual review** | Step 4 diff check | Final human gate |

> [!IMPORTANT]
> **The Athena-Public `.gitignore` is NOT a safety mechanism.** It only prevents accidental inclusion in the public repo's git. The primary gate is `public_manifest.yaml` (what gets copied) + `pre_deploy_scan.sh` (what passes inspection).

---

## Cross-References

- [public_manifest.yaml](file:///Users/[AUTHOR]/Project%20Athena/.agent/config/public_manifest.yaml) — Allowlist
- [pre_deploy_scan.sh](file:///Users/[AUTHOR]/Project%20Athena/.agent/scripts/pre_deploy_scan.sh) — Scanner
- [TD-027](file:///Users/[AUTHOR]/Project%20Athena/.context/TECH_DEBT.md) — The incident that proved blocklists fail
- [.syncignore](file:///Users/[AUTHOR]/Athena-Public/.syncignore) — Legacy safety net

## Tagging

`#workflow` `#automation` `#deploy` `#security`
