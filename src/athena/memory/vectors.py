"""
athena.memory.vectors — Thread-Safe v1.2

Optimizations:
    - Thread-Local Clients: Prevents httpx connection state corruption in parallel loops.
    - Atomic Cache: PersistentEmbeddingCache now uses Locks and Atomic Writes.
"""

import os
import sys
import hashlib
import json
import random
import threading
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

# Global cache instance
_embedding_cache = None
_embedding_cache_lock = threading.Lock()

# Rate limiter: serialize embedding API calls to prevent 429 on free-tier Gemini
_embedding_semaphore = threading.Semaphore(1)


def get_embedding_cache():
    global _embedding_cache
    with _embedding_cache_lock:
        if _embedding_cache is None:
            _embedding_cache = PersistentEmbeddingCache()
        return _embedding_cache


# Thread-local storage for Supabase clients
_thread_local = threading.local()


def get_client() -> Any:
    """Returns a thread-safe Supabase client instance."""
    if not hasattr(_thread_local, "client"):
        from supabase import create_client
        from dotenv import load_dotenv

        load_dotenv()

        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials missing in environment.")
        _thread_local.client = create_client(url, key)
    return _thread_local.client


class PersistentEmbeddingCache:
    """JSON-backed persistent cache with Thread-Safe Atomic Writes and Background Saving."""

    def __init__(self, filename="embedding_cache.json"):
        # Correct pathing via project discovery
        from athena.core.config import AGENT_DIR

        self.cache_file = AGENT_DIR / "state" / filename
        self.lock = threading.Lock()
        self._cache: Dict[str, List[float]] = {}
        self._dirty = False
        self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                with self.lock:
                    self._cache = json.loads(self.cache_file.read_text())
            except Exception:
                self._cache = {}

    def _save_worker(self, content: str):
        """Worker thread for atomic disk operations."""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            # Atomic swap pattern
            fd, temp_path = tempfile.mkstemp(dir=self.cache_file.parent)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(content)
                os.replace(temp_path, self.cache_file)
            except Exception:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception:
            pass

    def _save(self):
        """Schedules a background atomic save."""
        try:
            with self.lock:
                if not self._dirty:
                    return
                cache_copy = dict(self._cache)
                self._dirty = False

            # Serialize outside the lock to prevent thread lock starvation
            content = json.dumps(cache_copy)

            # Offload IO to a daemon thread to avoid blocking caller
            threading.Thread(
                target=self._save_worker, args=(content,), daemon=True
            ).start()
        except Exception:
            pass

    def get(self, text_hash: str) -> Optional[List[float]]:
        with self.lock:
            return self._cache.get(text_hash)

    def set(self, text_hash: str, embedding: List[float]):
        with self.lock:
            self._cache[text_hash] = embedding
            self._dirty = True
        self._save()


def _hash_text(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def get_embedding(text: str, max_retries: int = 7) -> List[float]:
    """Generate embedding with persistent disk caching and exponential backoff.

    Uses gemini-embedding-001 (3072 dimensions).
    Retries on 429 (rate limit) and 5xx (server error) with exponential backoff + jitter.
    Semaphore-gated (1 concurrent) to prevent thundering herd on free-tier Gemini API.
    Backoff ceiling: 60s. Floor delay: 1s per call to avoid burst patterns.
    """
    text_hash = _hash_text(text)
    cache = get_embedding_cache()
    cached = cache.get(text_hash)
    if cached:
        return cached

    # Fetch remote (Gemini) - Lazy load requests
    import requests
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={api_key}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
    }

    last_error = None
    for attempt in range(max_retries):
        with _embedding_semaphore:
            try:
                response = requests.post(url, json=payload, timeout=60)

                if response.status_code == 429 or response.status_code >= 500:
                    # Respect Retry-After header if present, else exponential backoff (cap 60s)
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        wait = min(float(retry_after), 60)
                    else:
                        wait = min((2 ** attempt) + random.uniform(0, 1), 60)
                    last_error = f"HTTP {response.status_code}"
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(wait)
                        continue
                    else:
                        response.raise_for_status()

                response.raise_for_status()
                embedding = response.json()["embedding"]["values"]
                cache.set(text_hash, embedding)
                # Floor delay: prevent burst even on success (free-tier courtesy)
                import time
                time.sleep(1)
                return embedding

            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < max_retries - 1:
                    import time
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait)
                else:
                    raise

    raise RuntimeError(f"get_embedding failed after {max_retries} retries: {last_error}")


def get_embeddings_batch(
    texts: List[str], batch_size: int = 25, max_retries: int = 7
) -> List[Optional[List[float]]]:
    """Embed many texts via Gemini :batchEmbedContents, warming the persistent cache.

    Why this exists: get_embedding() is Semaphore(1)-serialized with a 1s floor delay
    per call, so embedding N files costs ~1.5-2s EACH, serially (the real reason a sync
    takes 20+ min). batchEmbedContents collapses N cache-misses into ceil(N/batch_size)
    requests. Cache hits are skipped entirely (no API). On ANY batch failure it falls
    back to the proven per-item get_embedding(), so correctness/latency is never WORSE
    than the single-call path — only better.

    Returns embeddings aligned to `texts` (None for any that ultimately failed).
    Side effect: populates the on-disk embedding cache, so a subsequent per-file
    get_embedding(text) for the same text is an instant cache hit.
    """
    import time

    cache = get_embedding_cache()
    results: List[Optional[List[float]]] = [None] * len(texts)
    misses = []  # list of (index, text, hash)
    for i, t in enumerate(texts):
        h = _hash_text(t)
        cached = cache.get(h)
        if cached is not None:
            results[i] = cached
        else:
            misses.append((i, t, h))

    if not misses:
        return results

    import requests
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY missing.")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-embedding-001:batchEmbedContents?key={api_key}"
    )

    for start in range(0, len(misses), batch_size):
        group = misses[start : start + batch_size]
        payload = {
            "requests": [
                {"model": "models/gemini-embedding-001", "content": {"parts": [{"text": t}]}}
                for _, t, _ in group
            ]
        }
        got: Optional[List[List[float]]] = None
        for attempt in range(max_retries):
            with _embedding_semaphore:
                try:
                    resp = requests.post(url, json=payload, timeout=120)
                    if resp.status_code == 429 or resp.status_code >= 500:
                        retry_after = resp.headers.get("Retry-After")
                        wait = (
                            min(float(retry_after), 60)
                            if retry_after
                            else min((2 ** attempt) + random.uniform(0, 1), 60)
                        )
                        if attempt < max_retries - 1:
                            time.sleep(wait)
                            continue
                        resp.raise_for_status()
                    resp.raise_for_status()
                    got = [e["values"] for e in resp.json()["embeddings"]]
                    time.sleep(1)  # free-tier courtesy: ONE delay per batch, not per text
                    break
                except Exception:
                    if attempt < max_retries - 1:
                        time.sleep((2 ** attempt) + random.uniform(0, 1))
                    else:
                        got = None

        if got is not None and len(got) == len(group):
            for (i, t, h), emb in zip(group, got):
                results[i] = emb
                cache.set(h, emb)
        else:
            # Safe degrade: per-item via the proven single-call path.
            for i, t, h in group:
                try:
                    results[i] = get_embedding(t)
                except Exception:
                    results[i] = None

    return results


def search_rpc(
    rpc_name: str, query_embedding: List[float], limit: int = 5, threshold: float = 0.3
) -> List[Dict]:
    client = get_client()
    result = client.rpc(
        rpc_name,
        {
            "query_embedding": query_embedding,
            "match_threshold": threshold,
            "match_count": limit,
        },
    ).execute()
    return result.data


# --- Collection-Specific Wrappers ---


def search_sessions(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_sessions", query_embedding, limit, threshold)


def search_case_studies(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_case_studies", query_embedding, limit, threshold)


def search_protocols(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_protocols", query_embedding, limit, threshold)


def search_capabilities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_capabilities", query_embedding, limit, threshold)


def search_playbooks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_playbooks", query_embedding, limit, threshold)


def search_references(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_references", query_embedding, limit, threshold)


def search_frameworks(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_frameworks", query_embedding, limit, threshold)


def search_workflows(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_workflows", query_embedding, limit, threshold)


def search_entities(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_entities", query_embedding, limit, threshold)


def search_user_profile(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_user_profile", query_embedding, limit, threshold)


def search_system_docs(client, query_embedding, limit=5, threshold=0.3):
    return search_rpc("search_system_docs", query_embedding, limit, threshold)


def search_insights(client, query_embedding, limit=5, threshold=0.3):
    """Search insights table (Marketing Analysis, Strategic Notes)."""
    return search_rpc("search_insights", query_embedding, limit, threshold)
