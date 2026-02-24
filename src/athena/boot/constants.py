from pathlib import Path

# Paths
# Assuming src/athena/boot/constants.py -> ../../../.. = PROJECT_ROOT
PROJECT_ROOT = Path(__file__).resolve().parents[3]

LOGS_DIR = PROJECT_ROOT / ".context" / "memories" / "session_logs"
SUPABASE_SEARCH_SCRIPT = PROJECT_ROOT / ".agent" / "scripts" / "smart_search.py"
PROTOCOLS_JSON = PROJECT_ROOT / ".agent" / "protocols.json"
CORE_IDENTITY = (
    PROJECT_ROOT / ".framework" / "v8.2-stable" / "modules" / "Core_Identity.md"
)
SAFE_BOOT_SCRIPT = PROJECT_ROOT / "safe_boot.sh"

# Memory Bank (Token Budget)
MEMORY_BANK_DIR = PROJECT_ROOT / ".context" / "memory_bank"
BOOT_FILES = {
    "userContext.md": MEMORY_BANK_DIR / "userContext.md",
    "productContext.md": MEMORY_BANK_DIR / "productContext.md",
    "activeContext.md": MEMORY_BANK_DIR / "activeContext.md",
}

# Configuration
BOOT_TIMEOUT_SECONDS = 90
EXPECTED_CORE_HASH = "377a465a475ee9440db183fe93437fba89ac9f92dd7abc1b67e6cff911132d09f16de56c2494bf8d7ba76f55353cfdd2"

# Colors (centralized)
from athena.core.colors import GREEN, CYAN, YELLOW, RED, BOLD, DIM, RESET
