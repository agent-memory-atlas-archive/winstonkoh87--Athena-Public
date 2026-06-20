"""
athena.tools.reranker
=====================

Cross-Encoder Reranking logic.
"""

import os

# Force transformers onto the PyTorch backend BEFORE it is imported. Otherwise
# transformers probes for TensorFlow, imports it (~20s), then crashes on the Keras 3
# incompatibility ("install tf-keras") — which makes --rerank hang past its timeout
# and return empty. We use torch only; tell transformers so it never touches TF.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_TORCH", "1")
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import sys
import time
from typing import List, Optional
from athena.core.models import SearchResult

# Operational Default: Lazy load model
_model = None

# Cap on how many candidates we rerank; keeps the call bounded under the timeout.
RERANK_CANDIDATE_CAP = 12

def get_model():
    global _model
    if _model is None:
        try:
            from sentence_transformers import CrossEncoder
            model_name = 'cross-encoder/ms-marco-MiniLM-L6-v2' 
            # print(f"   🧠 Loading Reranker: {model_name}...", file=sys.stderr)
            _model = CrossEncoder(model_name)
        except ImportError:
            # print("   ⚠️  Result reranking skipped: 'sentence_transformers' not installed.", file=sys.stderr)
            return None
        except Exception as e:
            # print(f"   ⚠️  Result reranking skipped: Model load failed ({e})", file=sys.stderr)
            return None
    return _model

def rerank_results(query: str, results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
    """
    Rerank a list of SearchResult objects using a Cross-Encoder.
    Returns the top_k results.
    """
    model = get_model()
    if not model or not results:
        return results[:top_k]

    # Only rerank the top candidates (results arrive RRF-sorted); we return top_k anyway.
    candidates = results[:RERANK_CANDIDATE_CAP]

    # Prepare pairs: (query, content)
    pairs = [(query, doc.content) for doc in candidates]

    try:
        scores = model.predict(pairs)

        # Attach scores and re-sort
        for doc, score in zip(candidates, scores):
            if not doc.signals:
                 doc.signals = {}
            doc.signals['reranker'] = {"score": float(score)}

        # Sort descending by reranker score
        reranked = sorted(candidates, key=lambda x: x.signals['reranker']['score'], reverse=True)
        return reranked[:top_k]
        
    except Exception as e:
        print(f"   ⚠️  Reranking failed: {e}", file=sys.stderr)
        return results[:top_k]
