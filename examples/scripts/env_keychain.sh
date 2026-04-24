#!/usr/bin/env bash
# ============================================================
# env_keychain.sh — macOS Keychain ↔ .env Bridge
# ============================================================
#
# Purpose: Replaces the flat .env file with macOS Keychain storage.
#
# Usage:
#   ./env_keychain.sh store     # Import current .env into Keychain
#   ./env_keychain.sh load      # Export Keychain secrets to env vars
#   ./env_keychain.sh verify    # Check which keys are stored
#
# After storing, you can delete .env and source this script instead:
#   eval "$(./env_keychain.sh load)"
#
# Security Ref: Audit Tier 0, Item #1
# ============================================================

set -euo pipefail

SERVICE_NAME="athena-workspace"
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# Keys we expect to manage (must match .env exactly)
MANAGED_KEYS=(
    "NEXT_PUBLIC_SUPABASE_URL"
    "SUPABASE_URL"
    "SUPABASE_ANON_KEY"
    "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    "SUPABASE_SERVICE_ROLE_KEY"
    "GOOGLE_API_KEY"
    "GEMINI_API_KEY"
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
)

store() {
    if [[ ! -f "$ENV_FILE" ]]; then
        echo "❌ No .env file found at $ENV_FILE"
        exit 1
    fi

    echo "🔐 Importing .env keys into macOS Keychain (service: $SERVICE_NAME)..."

    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ -z "$line" || "$line" =~ ^# ]] && continue

        key="${line%%=*}"
        value="${line#*=}"
        # Strip surrounding quotes
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"

        if [[ -n "$key" && -n "$value" ]]; then
            # Delete existing entry if present (idempotent)
            security delete-generic-password -s "$SERVICE_NAME" -a "$key" 2>/dev/null || true
            # Add new entry
            security add-generic-password -s "$SERVICE_NAME" -a "$key" -w "$value" -U
            echo "  ✅ Stored: $key"
        fi
    done < "$ENV_FILE"

    echo ""
    echo "✅ All keys stored in Keychain."
    echo ""
    echo "Next steps:"
    echo "  1. Verify:  $0 verify"
    echo "  2. Test:    eval \"\$($0 load)\" && python -c 'import os; print(os.environ.get(\"SUPABASE_URL\", \"NOT SET\"))'"
    echo "  3. Delete:  rm $ENV_FILE  (only after verifying step 2 works)"
    echo "  4. Add to shell profile:  echo 'eval \"\$($0 load)\"' >> ~/.zshrc"
}

load() {
    # Output export statements suitable for eval
    for key in "${MANAGED_KEYS[@]}"; do
        value=$(security find-generic-password -s "$SERVICE_NAME" -a "$key" -w 2>/dev/null || echo "")
        if [[ -n "$value" ]]; then
            echo "export $key=\"$value\""
        fi
    done
}

verify() {
    echo "🔍 Checking Keychain for Athena secrets (service: $SERVICE_NAME)..."
    echo ""
    for key in "${MANAGED_KEYS[@]}"; do
        if security find-generic-password -s "$SERVICE_NAME" -a "$key" -w &>/dev/null; then
            echo "  ✅ $key — stored"
        else
            echo "  ❌ $key — NOT FOUND"
        fi
    done
}

case "${1:-help}" in
    store)  store ;;
    load)   load ;;
    verify) verify ;;
    *)
        echo "Usage: $0 {store|load|verify}"
        echo ""
        echo "  store   Import .env keys into macOS Keychain"
        echo "  load    Output 'export KEY=VALUE' for eval"
        echo "  verify  Check which keys are in Keychain"
        exit 1
        ;;
esac
