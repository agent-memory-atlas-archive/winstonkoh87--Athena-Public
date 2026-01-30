"""
athena.core.cache
=================

TTL-based LRU Cache for Athena search queries.
Reduces latency for frequent queries by caching results.

Usage:
    from athena.core.cache import QueryCache
    
    cache = QueryCache(ttl_hours=24, max_size=100)
    result = cache.get("law 3 revealed")
    if result is None:
        result = expensive_search(...)
        cache.set("law 3 revealed", result)
"""

import hashlib
import time
from collections import OrderedDict
from typing import Any, Optional
from dataclasses import dataclass

@dataclass
class CacheEntry:
    value: Any
    timestamp: float
    hits: int = 0

class QueryCache:
    """TTL-based LRU cache for search queries."""
    
    def __init__(self, ttl_hours: float = 24, max_size: int = 100):
        self.ttl_seconds = ttl_hours * 3600
        self.max_size = max_size
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._invalidation_timestamp: float = 0.0
    
    def _hash_key(self, query: str) -> str:
        """Create deterministic hash for query."""
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def get(self, query: str) -> Optional[Any]:
        """Get cached result if exists and not expired."""
        key = self._hash_key(query)
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        now = time.time()
        
        # Check TTL expiry
        if now - entry.timestamp > self.ttl_seconds:
            del self._cache[key]
            return None
        
        # Check invalidation (content changed)
        if entry.timestamp < self._invalidation_timestamp:
            del self._cache[key]
            return None
        
        # Hit! Move to end (most recently used)
        entry.hits += 1
        self._cache.move_to_end(key)
        return entry.value
    
    def set(self, query: str, value: Any) -> None:
        """Cache a result."""
        key = self._hash_key(query)
        
        # Evict oldest if at capacity
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        self._cache[key] = CacheEntry(
            value=value,
            timestamp=time.time(),
            hits=0
        )
    
    def invalidate(self) -> None:
        """Invalidate all cached results (call when content changes)."""
        self._invalidation_timestamp = time.time()
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
    
    def stats(self) -> dict:
        """Get cache statistics."""
        total_hits = sum(e.hits for e in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_hits": total_hits,
            "ttl_hours": self.ttl_seconds / 3600
        }

# Global singleton for search cache
_search_cache: Optional[QueryCache] = None

def get_search_cache() -> QueryCache:
    """Get or create the global search cache."""
    global _search_cache
    if _search_cache is None:
        _search_cache = QueryCache(ttl_hours=24, max_size=100)
    return _search_cache
