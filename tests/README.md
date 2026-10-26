# Athena Test Suite (`tests/`)

Comprehensive test suite verifying governance gates, intelligence algorithms, memory synchronizers, and tool interfaces.

## 🧪 Running Tests

Run the full test suite using `pytest` or `make`:

```bash
# Run all tests
make test
# Or with pytest directly
pytest tests/ -v --tb=short

# Run fast unit tests
make test-fast

# Run with test coverage
make test-cov
```

## 📋 Test Structure

- **Core & Governance**: `test_agent_gate.py`, `test_governance.py`, `test_mcp_security.py`, `test_ruin_structured.py`
- **Intelligence & Decision Engine**: `test_gto_engine.py`, `test_gto_engine_capabilities.py`, `test_wargame.py`, `test_frame_ledger.py`
- **Memory & Search**: `test_vectors.py`, `test_fts_search.py`, `test_retrieval_reliability.py`, `test_search_cache_degraded.py`
- **Tools & Safety**: `test_trade_guardian.py`, `test_citation_verifier.py`, `test_cli_contracts.py`
- **Auditors & Harness**: `test_eval_harness.py`, `test_personality.py`, `test_version_sync.py`
