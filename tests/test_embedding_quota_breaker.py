"""Tests that the 429 quota exhaustion breaker halts embedding attempts."""

from unittest.mock import MagicMock, patch

import pytest

import athena.memory.vectors as vectors


@pytest.fixture(autouse=True)
def reset_breaker(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy_test_key_for_mock")
    with vectors._consecutive_429_lock:
        vectors._consecutive_429_count = 0
    yield
    with vectors._consecutive_429_lock:
        vectors._consecutive_429_count = 0


def test_quota_exhausted_propagates_and_bounds_calls():
    """When Gemini returns 429 consecutively, EmbeddingQuotaExhausted must propagate within 5 calls."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {}
    mock_resp.text = "RESOURCE_EXHAUSTED"

    call_count = 0

    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return mock_resp

    texts = [f"Text item {i}" for i in range(60)]  # 3 batches of 20

    EmbeddingQuotaExhausted = getattr(vectors, "EmbeddingQuotaExhausted", None)
    assert EmbeddingQuotaExhausted is not None, "EmbeddingQuotaExhausted class not defined in vectors.py"

    with (
        patch("requests.post", side_effect=mock_post),
        patch("time.sleep", return_value=None),
        patch.object(vectors.get_embedding_cache(), "get", return_value=None),
        pytest.raises(EmbeddingQuotaExhausted),
    ):
        vectors.get_embeddings_batch(texts, batch_size=20)

    assert call_count <= 5, f"Expected <= 5 calls before halting, got {call_count}"


def test_payment_required_402_alerts_and_fails_immediately(capsys):
    """When Gemini returns HTTP 402 Payment Required, a prominent top-up warning must be printed and raise immediately."""
    import requests

    mock_resp = MagicMock()
    mock_resp.status_code = 402
    mock_resp.text = "PAYMENT_REQUIRED: balance USD 0.00"
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("402 Client Error: Payment Required")

    with (
        patch("requests.post", return_value=mock_resp),
        patch.object(vectors.get_embedding_cache(), "get", return_value=None),
        pytest.raises(requests.exceptions.HTTPError),
    ):
        vectors.get_embedding("test query for payment check", max_retries=5)

    captured = capsys.readouterr()
    assert "🚨 [ACTION REQUIRED: GOOGLE API CREDITS DEPLETED]" in captured.err
    assert "Please top up USD 20 at: https://aistudio.google.com" in captured.err
