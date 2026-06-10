#!/bin/bash
# =============================================================================
# pre_deploy_scan.sh — Pre-Deployment Secret & PII Scanner
# =============================================================================
# Runs against the Athena-Public staging area BEFORE any git add/commit/push.
# Catches secrets, PII, and sensitive patterns that should never go public.
#
# Usage:
#   ./pre_deploy_scan.sh [target_dir]
#   ./pre_deploy_scan.sh                  # defaults to ~/Athena-Public
#   ./pre_deploy_scan.sh --dry-run        # scan only, no exit code
#
# Exit codes:
#   0 = clean (safe to deploy)
#   1 = violations found (BLOCK deployment)
#
# Filed: 2026-06-10 | Source: R2 Privacy Hard Wall implementation
# =============================================================================

set -euo pipefail

TARGET_DIR="${1:-$HOME/Athena-Public}"
DRY_RUN=false
VIOLATIONS=0

if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN=true
    TARGET_DIR="${2:-$HOME/Athena-Public}"
fi

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════╗"
echo "║  Athena Pre-Deploy Secret & PII Scanner v1.0 ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Target: $TARGET_DIR"
echo "Mode: $(if $DRY_RUN; then echo 'DRY RUN (advisory)'; else echo 'ENFORCE (will block on violations)'; fi)"
echo ""

# --- Gate 1: API Keys & Secrets ---
echo "━━━ Gate 1: Secrets & API Keys ━━━"

# Patterns that indicate ACTUAL secrets (not just env var name references)
# We look for actual values, not documentation references
SECRET_PATTERNS=(
    'sk-[a-zA-Z0-9]{20,}'        # OpenAI key pattern (actual key value)
    'eyJhbGciOi'                  # JWT pattern (actual token)
    'AIzaSy[a-zA-Z0-9_-]{33}'    # Google API key pattern (actual key value)
    'ghp_[a-zA-Z0-9]{36}'        # GitHub PAT (actual token)
    'ghu_[a-zA-Z0-9]{36}'        # GitHub user token
    'BEGIN RSA PRIVATE KEY'       # Actual private key block
    'BEGIN OPENSSH PRIVATE KEY'   # Actual private key block
)

# Patterns that are only violations when they contain actual values (not docs)
# These check for KEY=actual_value assignments, not just mentioning the name
ASSIGNMENT_PATTERNS=(
    'SUPABASE_SERVICE_ROLE_KEY\s*=\s*eyJ'    # Actual JWT value assigned
    'GOOGLE_API_KEY\s*=\s*AIza'              # Actual Google key assigned
    'OPENAI_API_KEY\s*=\s*sk-'               # Actual OpenAI key assigned
    'ANTHROPIC_API_KEY\s*=\s*sk-'            # Actual Anthropic key assigned
    'password\s*[:=]\s*["\x27][^"\x27]{8,}' # password = "actual_value"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' --include='*.py' --include='*.yaml' --include='*.yml' \
              --include='*.json' --include='*.toml' --include='*.sh' --include='*.sql' \
              --include='*.ts' --include='*.js' --include='*.env*' \
              -E "$pattern" "$TARGET_DIR" 2>/dev/null | grep -v 'pds:allow' | grep -v '/pre_deploy_scan.sh:' || true)
    if [[ -n "$matches" ]]; then
        echo -e "${RED}✗ VIOLATION: Secret pattern '$pattern' found:${NC}"
        echo "$matches" | head -5
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# Check assignment patterns (actual secrets, not doc references)
for pattern in "${ASSIGNMENT_PATTERNS[@]}"; do
    matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' --include='*.py' --include='*.yaml' --include='*.yml' \
              --include='*.json' --include='*.toml' --include='*.sh' --include='*.sql' \
              --include='*.ts' --include='*.js' --include='*.env*' \
              -E "$pattern" "$TARGET_DIR" 2>/dev/null | grep -v 'pds:allow' | grep -v '/pre_deploy_scan.sh:' || true)
    if [[ -n "$matches" ]]; then
        echo -e "${RED}✗ VIOLATION: Actual secret value assigned '$pattern':${NC}"
        echo "$matches" | head -5
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [[ $VIOLATIONS -eq 0 ]]; then
    echo -e "${GREEN}✓ No secrets detected.${NC}"
fi

echo ""

# --- Gate 2: PII Patterns ---
echo "━━━ Gate 2: PII & Personal Data ━━━"

PII_VIOLATIONS=0

# Dollar amounts > $100 (specific pricing data)
# Dollar amounts alone are usually illustrative; only flag when transaction context co-occurs
dollar_matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' --include='*.py' --include='*.yaml' \
    -E '\$[0-9]{3,}' "$TARGET_DIR" 2>/dev/null | \
    grep -iE 'client|quote|quoted|paid|revenue|invoice|charg|collected|fee|salary' | \
    grep -v 'node_modules' | grep -v '.git/' | grep -v 'package-lock' | grep -v 'pds:allow' || true)
if [[ -n "$dollar_matches" ]]; then
    echo -e "${YELLOW}⚠ WARNING: Dollar amounts > \$100 found (potential pricing PII):${NC}"
    echo "$dollar_matches" | head -5
    PII_VIOLATIONS=$((PII_VIOLATIONS + 1))
fi

# Assignment numbers (A30, A39, etc.)
assignment_matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' --include='*.py' \
    -E '\bA[0-9]{2}\b' "$TARGET_DIR" 2>/dev/null | \
    grep -v 'node_modules' | grep -v '.git/' | \
    grep -v 'A11y' | grep -v 'A10' | grep -v 'pds:allow' || true)  # Exclude common non-assignment patterns
if [[ -n "$assignment_matches" ]]; then
    echo -e "${YELLOW}⚠ WARNING: Assignment numbers (A##) found:${NC}"
    echo "$assignment_matches" | head -5
    PII_VIOLATIONS=$((PII_VIOLATIONS + 1))
fi

# Known personal names blocklist
NAME_BLOCKLIST="REPLACE_NAME_1|REPLACE_NAME_2"  # Customize: pipe-separated names that must never go public
name_matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' --include='*.py' \
    -E "$NAME_BLOCKLIST" "$TARGET_DIR" 2>/dev/null | \
    grep -v 'node_modules' | grep -v '.git/' || true)
if [[ -n "$name_matches" ]]; then
    echo -e "${RED}✗ VIOLATION: Personal names found:${NC}"
    echo "$name_matches" | head -5
    VIOLATIONS=$((VIOLATIONS + 1))
fi

# Psychology/therapy patterns
psych_matches=$(grep -rn --exclude='pre_deploy_scan.sh' --include='*.md' \
    -E 'cPTSD|trigger_log|REPLACE_PERSONAL_PATTERN'  # Customize: terms from your private domains "$TARGET_DIR" 2>/dev/null | \
    grep -v 'node_modules' | grep -v '.git/' | grep -v 'pds:allow' | grep -v '/pre_deploy_scan.sh:' || true)
if [[ -n "$psych_matches" ]]; then
    echo -e "${RED}✗ VIOLATION: Therapy/psychology PII found:${NC}"
    echo "$psych_matches" | head -5
    VIOLATIONS=$((VIOLATIONS + 1))
fi

if [[ $PII_VIOLATIONS -eq 0 && $VIOLATIONS -eq 0 ]]; then
    echo -e "${GREEN}✓ No PII violations detected.${NC}"
elif [[ $PII_VIOLATIONS -gt 0 && $VIOLATIONS -eq 0 ]]; then
    echo -e "${YELLOW}⚠ $PII_VIOLATIONS PII warnings (review recommended).${NC}"
fi

echo ""

# --- Gate 3: Blocked Files ---
echo "━━━ Gate 3: Blocked File Patterns ━━━"

BLOCKED_FILES=(
    "REPLACE_PRIVATE_MODULE"  # Customize: your private module filenames
    "User_Profile"
    "trigger_log"
    "accountability_status"
)

# Files that are blocked UNLESS inside examples/ (intentional public examples)
BLOCKED_OUTSIDE_EXAMPLES=(
    "Constraints_Master"
    "Session_Observations"
    "session_logs"
)

for blocked in "${BLOCKED_FILES[@]}"; do
    found=$(find "$TARGET_DIR" -name "*${blocked}*" -not -path '*/.git/*' 2>/dev/null || true)
    if [[ -n "$found" ]]; then
        echo -e "${RED}✗ VIOLATION: Blocked file found: $found${NC}"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# Check files blocked outside examples/
for blocked in "${BLOCKED_OUTSIDE_EXAMPLES[@]}"; do
    found=$(find "$TARGET_DIR" -name "*${blocked}*" -not -path '*/.git/*' -not -path '*/examples/*' 2>/dev/null || true)
    if [[ -n "$found" ]]; then
        echo -e "${RED}✗ VIOLATION: Blocked file outside examples/: $found${NC}"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# Check for .env files (but allow .env.example)
found_env=$(find "$TARGET_DIR" -name ".env" -not -name ".env.example" -not -path '*/.git/*' 2>/dev/null || true)
if [[ -n "$found_env" ]]; then
    echo -e "${RED}✗ VIOLATION: .env file found: $found_env${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
fi

if [[ $VIOLATIONS -eq 0 ]]; then
    echo -e "${GREEN}✓ No blocked files detected.${NC}"
fi

echo ""

# --- Summary ---
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOTAL=$((VIOLATIONS + PII_VIOLATIONS))
if [[ $VIOLATIONS -gt 0 ]]; then
    echo -e "${RED}✗ DEPLOYMENT BLOCKED: $VIOLATIONS critical violations found.${NC}"
    if $DRY_RUN; then
        echo -e "${YELLOW}  (Dry run — no action taken. Fix violations before real deploy.)${NC}"
        exit 0
    else
        exit 1
    fi
elif [[ $PII_VIOLATIONS -gt 0 ]]; then
    echo -e "${YELLOW}⚠ DEPLOYMENT ALLOWED with $PII_VIOLATIONS warnings. Review recommended.${NC}"
    exit 0
else
    echo -e "${GREEN}✓ ALL GATES PASSED. Safe to deploy.${NC}"
    exit 0
fi
