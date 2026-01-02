# Athena SDK Quickstart

These examples demonstrate core Athena functionality. They run standalone without external dependencies.

## Running the Examples

```bash
# From repository root
cd Athena-Public

# 1. Boot check - verify installation
python examples/quickstart/01_boot.py

# 2. Search demo - hybrid search with mock data
python examples/quickstart/02_search.py "position sizing"

# 3. Commit demo - session logging pattern
python examples/quickstart/03_commit.py
```

## What Each Example Shows

| Script | Purpose |
|--------|---------|
| `01_boot.py` | SDK import, config discovery, directory structure |
| `02_search.py` | Hybrid search with RRF fusion (works in stub mode) |
| `03_commit.py` | Session logging format used by `/end` workflow |

## Going Live

To connect to real infrastructure:

1. Copy `.env.example` to `.env`
2. Add your API keys
3. Set `LOCAL_STUB_MODE = False` in the scripts
4. Install full dependencies: `pip install -e ".[full]"`

## Expected Output

### 01_boot.py

```
🏛️  ATHENA SDK BOOT CHECK
📦 SDK Version: 0.2.0
📂 Project Root: /path/to/Athena-Public
✅ BOOT SUCCESS
```

### 02_search.py

```
🔍 ATHENA SEARCH DEMO
   Query: "position sizing"
   Mode: LOCAL STUB

🏆 TOP 3 RESULTS:
  1. [HIGH] Protocol 46: Trading Methodology
  2. [HIGH] Session 2025-03-14: Risk Framework
  3. [MED] Canonical:L45
```
