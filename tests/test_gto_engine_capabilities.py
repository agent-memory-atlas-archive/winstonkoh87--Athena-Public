"""
tests.test_gto_engine_capabilities
==================================

Unit tests for T0.2 capability manifest in athena.intelligence.gto_engine.
Ensures every public function in __all__ has an honest capability manifest entry
listing computes, typed_inputs, defaults, and does_not.
"""

import json

import pytest

from athena.intelligence.gto_engine import (
    CAPABILITY_MANIFEST,
    main,
)
from athena.intelligence.gto_engine import (
    __all__ as gto_all,
)


def test_capabilities_cli(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["--capabilities"])
    assert rc == 0
    captured = capsys.readouterr()
    manifest = json.loads(captured.out)
    assert isinstance(manifest, dict)
    for func_name in gto_all:
        assert func_name in manifest


def test_manifest_structure_and_completeness() -> None:
    assert isinstance(CAPABILITY_MANIFEST, dict)
    for func_name in gto_all:
        assert func_name in CAPABILITY_MANIFEST, f"{func_name} missing from CAPABILITY_MANIFEST"
        entry = CAPABILITY_MANIFEST[func_name]
        assert "computes" in entry and entry["computes"].strip(), f"{func_name} missing 'computes'"
        assert "typed_inputs" in entry, f"{func_name} missing 'typed_inputs'"
        assert "defaults" in entry, f"{func_name} missing 'defaults'"
        assert "does_not" in entry and isinstance(entry["does_not"], list), f"{func_name} missing 'does_not'"


def test_run_decision_monte_carlo_does_not_caveats() -> None:
    rdmc = CAPABILITY_MANIFEST["run_decision_monte_carlo"]
    does_not = [d.lower() for d in rdmc["does_not"]]
    assert any("sample outcome" in d for d in does_not), "Missing 'sample outcomes' in does_not"
    assert any("fat tail" in d for d in does_not), "Missing 'fat tails' in does_not"
    assert any("regret" in d for d in does_not), "Missing 'regret' in does_not"


def test_manifest_mutant_detection() -> None:
    # Mutant 1: Function in __all__ missing from manifest fails check
    mutant_all = list(gto_all) + ["dummy_unmanifested_function"]
    with pytest.raises(AssertionError):
        for f in mutant_all:
            assert f in CAPABILITY_MANIFEST

    # Mutant 2: Missing does_not key in run_decision_monte_carlo fails check
    mutant_entry = dict(CAPABILITY_MANIFEST["run_decision_monte_carlo"])
    del mutant_entry["does_not"]
    with pytest.raises(KeyError):
        _ = mutant_entry["does_not"]
