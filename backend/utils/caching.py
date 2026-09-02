import time
from typing import Any, Dict, Optional


class SimpleCache:
    """
    Lightweight in-memory cache for deterministic operations.
    Supports basic get, set, clear, and TTL expiration.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 500):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, namespace: str, key: str) -> str:
        return f"{namespace}:{key}"

    def get(self, namespace: str, key: str) -> Optional[Any]:
        cache_key = self._make_key(namespace, key)
        entry = self._cache.get(cache_key)
        if not entry:
            return None

        if entry["expires_at"] is not None and time.time() > entry["expires_at"]:
            del self._cache[cache_key]
            return None

        return entry["data"]

    def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if len(self._cache) >= self.max_size:
            # Simple eviction of oldest item
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
            del self._cache[oldest_key]

        cache_key = self._make_key(namespace, key)
        expires_at = time.time() + (ttl if ttl is not None else self.default_ttl) if ttl != 0 else None
        self._cache[cache_key] = {
            "data": value,
            "created_at": time.time(),
            "expires_at": expires_at
        }

    def clear(self, namespace: Optional[str] = None) -> None:
        if namespace is None:
            self._cache.clear()
        else:
            prefix = f"{namespace}:"
            keys_to_del = [k for k in self._cache.keys() if k.startswith(prefix)]
            for k in keys_to_del:
                del self._cache[k]


# Global cache instance for backend reuse
global_cache = SimpleCache()
