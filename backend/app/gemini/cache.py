"""LRU cache for repeated Gemini prompts to reduce API cost and latency.

Caches FAQ-style queries that are likely to be asked repeatedly.
Cache keys are normalized (lowercase, stripped) to maximize hit rate.
"""

import hashlib
import logging
from collections import OrderedDict
from threading import Lock

logger = logging.getLogger(__name__)

# Maximum number of cached responses
MAX_CACHE_SIZE = 200


class PromptCache:
    """Thread-safe LRU cache for Gemini prompt responses.

    Uses an OrderedDict for O(1) access and LRU eviction.
    """

    def __init__(self, max_size: int = MAX_CACHE_SIZE) -> None:
        self._cache: OrderedDict[str, str] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _normalize_key(prompt: str) -> str:
        """Normalize a prompt into a consistent cache key.

        Lowercases, strips whitespace, and hashes for fixed-size keys.
        """
        normalized = prompt.lower().strip()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def get(self, prompt: str) -> str | None:
        """Retrieve a cached response for the given prompt.

        Args:
            prompt: The user prompt to look up.

        Returns:
            Cached response string, or None if not cached.
        """
        key = self._normalize_key(prompt)
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                logger.debug("Cache hit (total: %d)", self._hits)
                return self._cache[key]
            self._misses += 1
            return None

    def put(self, prompt: str, response: str) -> None:
        """Store a prompt-response pair in the cache.

        Evicts the least recently used entry if cache is full.

        Args:
            prompt: The user prompt (will be normalized for the key).
            response: The Gemini response to cache.
        """
        key = self._normalize_key(prompt)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = response
            else:
                if len(self._cache) >= self._max_size:
                    evicted_key, _ = self._cache.popitem(last=False)
                    logger.debug("Cache evicted entry: %s", evicted_key[:16])
                self._cache[key] = response

    @property
    def stats(self) -> dict[str, int]:
        """Return cache performance statistics."""
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
        }

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0


# Singleton cache instance
prompt_cache = PromptCache()
