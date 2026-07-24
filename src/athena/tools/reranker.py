"""
athena.tools.reranker
=====================

Cross-Encoder Reranking logic.

Two inference paths, tried in order:

1. ONNX fast path (default): tokenizers + onnxruntime against the locally
   exported quantized model in .agent/models/reranker-onnx/. No torch, no
   transformers — ~0.4s cold load vs ~13-58s for the torch path. Scores match
   the torch model within ~0.005 (verified 2026-07-03; qint8_arm64 quantization).
2. sentence_transformers CrossEncoder fallback: used only if the ONNX assets
   or onnxruntime are unavailable.

Regenerate the ONNX assets (e.g. after a model upgrade) by downloading
onnx/model_qint8_arm64.onnx + tokenizer.json from the HF repo
cross-encoder/ms-marco-MiniLM-L6-v2 into .agent/models/reranker-onnx/.
"""

import os

# CRITICAL (S527): force transformers onto the PyTorch backend BEFORE it is imported.
# Without this, transformers probes for TensorFlow, imports it (~20s on this machine),
# then crashes on the Keras 3 incompatibility ("install tf-keras"). Only relevant to
# the CrossEncoder fallback path, but cheap to set unconditionally.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys
from pathlib import Path

from athena.core.models import SearchResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
ONNX_DIR = PROJECT_ROOT / ".agent" / "models" / "reranker-onnx"
# Prefer the arm64-quantized model (4x smaller, faster); fall back to fp32.
ONNX_MODEL_CANDIDATES = ["model_qint8_arm64.onnx", "model.onnx"]
MAX_LENGTH = 512

# Lazy-loaded singletons
_onnx_session = None
_onnx_tokenizer = None
_onnx_failed = False
_model = None  # CrossEncoder fallback

# Cap on how many candidates we rerank. Widened 12→50 (2026-07-03): 12-of-25 sat
# below every published range — 2025 industry norm is 50-100 candidates into the
# cross-encoder (ZeroEntropy/Cohere/Ailog guides); a first-stage miss below the cap
# can never be rescued. The ONNX fast path scores 50 pairs in ~0.1s, so the old
# torch-latency rationale for a tight cap no longer applies.
RERANK_CANDIDATE_CAP = 50


def _get_onnx():
    """Load the ONNX session + tokenizer. Returns (session, tokenizer) or None."""
    global _onnx_session, _onnx_tokenizer, _onnx_failed
    if _onnx_failed:
        return None
    if _onnx_session is not None:
        return _onnx_session, _onnx_tokenizer
    try:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_path = next(
            (ONNX_DIR / name for name in ONNX_MODEL_CANDIDATES if (ONNX_DIR / name).exists()),
            None,
        )
        tokenizer_path = ONNX_DIR / "tokenizer.json"
        if model_path is None or not tokenizer_path.exists():
            _onnx_failed = True
            return None

        tokenizer = Tokenizer.from_file(str(tokenizer_path))
        tokenizer.enable_truncation(max_length=MAX_LENGTH)
        tokenizer.enable_padding()
        session = ort.InferenceSession(str(model_path))
        _onnx_session, _onnx_tokenizer = session, tokenizer
        return session, tokenizer
    except Exception:
        _onnx_failed = True
        return None


def _predict_onnx(pairs: "list[tuple[str, str]]") -> "list[float] | None":
    """Score (query, doc) pairs via the ONNX session. Returns None on failure."""
    loaded = _get_onnx()
    if not loaded:
        return None
    session, tokenizer = loaded
    try:
        import numpy as np

        encodings = tokenizer.encode_batch(list(pairs))
        feeds = {
            "input_ids": np.array([e.ids for e in encodings], dtype=np.int64),
            "attention_mask": np.array([e.attention_mask for e in encodings], dtype=np.int64),
            "token_type_ids": np.array([e.type_ids for e in encodings], dtype=np.int64),
        }
        logits = session.run(None, feeds)[0]
        return [float(x) for x in logits.ravel()]
    except Exception as e:
        print(f"   ⚠️  ONNX rerank failed ({e}); falling back to CrossEncoder.", file=sys.stderr)
        return None


def get_model():
    """CrossEncoder fallback (torch path). Lazy-loaded; None if unavailable."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import CrossEncoder
            model_name = 'cross-encoder/ms-marco-MiniLM-L6-v2'
            _model = CrossEncoder(model_name)
        except ImportError:
            return None
        except Exception:
            return None
    return _model


def _predict(pairs: "list[tuple[str, str]]") -> "list[float] | None":
    """Score pairs: ONNX fast path first, CrossEncoder fallback second."""
    scores = _predict_onnx(pairs)
    if scores is not None:
        return scores
    model = get_model()
    if model is None:
        return None
    return [float(s) for s in model.predict(pairs)]


class SafeCrossEncoder:
    """
    Resilient CrossEncoder wrapper. Handles ONNX fast path, CrossEncoder fallback,
    and graceful degradation on timeout or missing dependencies.
    """
    def __init__(self, timeout_sec: int = 5):
        self.timeout_sec = timeout_sec
        self.fallback_used = False

    def rerank(self, query: str, results: list[SearchResult], top_k: int = 5) -> tuple[list[SearchResult], bool]:
        if not results:
            return results, False

        candidates = results[:RERANK_CANDIDATE_CAP]
        pairs = [(query, doc.content or "") for doc in candidates]

        try:
            scores = _predict_onnx(pairs)
            if scores is None:
                self.fallback_used = True
                model = get_model()
                if model is None:
                    return results[:top_k], True
                scores = [float(s) for s in model.predict(pairs)]

            for doc, score in zip(candidates, scores, strict=False):
                if not doc.signals:
                    doc.signals = {}
                doc.signals['reranker'] = {"score": score}

            reranked = sorted(candidates, key=lambda x: x.signals['reranker']['score'], reverse=True)
            return reranked[:top_k], self.fallback_used

        except Exception as e:
            print(f"   ⚠️  Reranking failed ({e}); returning candidate slice.", file=sys.stderr)
            return results[:top_k], True


def rerank_results(query: str, results: list[SearchResult], top_k: int = 5) -> list[SearchResult]:
    """
    Rerank a list of SearchResult objects using SafeCrossEncoder.
    Returns top_k results.
    """
    safe_encoder = SafeCrossEncoder()
    reranked, _ = safe_encoder.rerank(query, results, top_k=top_k)
    return reranked

