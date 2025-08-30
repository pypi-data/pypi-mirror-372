"""
StrataRegula Kernel: Pull-based Config Processing System

Core design principle: "Config is not passed to applications.
StrataRegula provides only the necessary form at the moment it's needed."

Architecture:
- Compile passes (validation, interning, indexing)
- View materialization (query-driven config access)
- Content-based caching with intelligent invalidation
"""

import hashlib
import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Protocol


class Pass(Protocol):
    """Protocol for compile passes that transform config data."""

    def run(self, model: Mapping[str, Any]) -> Mapping[str, Any]:
        """Transform the config model and return the modified version."""
        ...


class View(Protocol):
    """Protocol for views that materialize specific data from compiled config."""

    key: str  # Unique identifier for this view (e.g., "routes:by_pref")

    def materialize(self, model: Mapping[str, Any], **params) -> Any:
        """Extract and format specific data from the compiled model."""
        ...


# Simple cache implementation
class CacheBackend(Protocol):
    """Protocol for cache backend implementations."""

    def get(self, key: str) -> Any:
        """Get value from cache, return None if not found."""
        ...

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        ...


@dataclass
class LRUCacheBackend:
    """Simple LRU cache backend implementation."""

    max_size: int = 1000

    def __post_init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._access_order: list[str] = []

    def get(self, key: str) -> Any:
        if key in self._cache:
            # Move to end (most recently used)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        if key in self._cache:
            # Update existing
            self._access_order.remove(key)
        elif len(self._cache) >= self.max_size:
            # Evict least recently used
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]

        self._cache[key] = value
        self._access_order.append(key)

    def clear(self) -> None:
        self._cache.clear()
        self._access_order.clear()

    def get_stats(self) -> dict[str, Any]:
        return {
            "type": "LRU",
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": 0.0,  # Would need hit/miss tracking for accurate rate
        }


def generate_content_address(data: Any, algorithm: str = "blake2b") -> str:
    """Generate content-based hash for cache keys."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    if algorithm == "blake2b":
        return hashlib.blake2b(serialized.encode("utf-8")).hexdigest()
    else:
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class CacheStats:
    """Statistics for cache performance monitoring."""

    hits: int = 0
    misses: int = 0
    total_queries: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate as percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.hits / self.total_queries) * 100.0


@dataclass
class Kernel:
    """
    Main StrataRegula kernel for config processing.

    Provides Pull-based API where applications request specific views
    rather than accessing raw config data directly.
    """

    passes: list[Pass] = field(default_factory=list)
    views: dict[str, View] = field(default_factory=dict)
    cache_backend: CacheBackend = field(default_factory=lambda: LRUCacheBackend())
    stats: CacheStats = field(default_factory=CacheStats)

    def _compile(self, raw_cfg: Mapping[str, Any]) -> Mapping[str, Any]:
        """Apply all compile passes to the raw config."""
        model = raw_cfg
        for pass_instance in self.passes:
            model = pass_instance.run(model)
        return model

    def _generate_cache_key(
        self, view_key: str, params: dict[str, Any], raw_cfg: Any
    ) -> str:
        """Generate content-based cache key for query."""
        cache_data = {
            "cfg": raw_cfg,
            "passes": [type(p).__name__ for p in self.passes],
            "view": view_key,
            "params": params,
        }

        # Use content addressing from cache module
        return generate_content_address(cache_data, algorithm="blake2b")

    def query(
        self, view_key: str, params: dict[str, Any], raw_cfg: Mapping[str, Any]
    ) -> Any:
        """
        Query a specific view with parameters.

        Args:
            view_key: The view identifier (must exist in self.views)
            params: Parameters to pass to the view's materialize method
            raw_cfg: Raw configuration data

        Returns:
            Materialized view data (immutable where possible)

        Raises:
            KeyError: If view_key is not found
            ValueError: If view materialization fails
        """
        self.stats.total_queries += 1

        # Generate cache key based on all inputs
        cache_key = self._generate_cache_key(view_key, params, raw_cfg)

        # Check cache backend first
        cached_result = self.cache_backend.get(cache_key)
        if cached_result is not None:
            self.stats.hits += 1
            return cached_result

        # Cache miss - need to compute
        self.stats.misses += 1

        # Verify view exists
        if view_key not in self.views:
            raise KeyError(
                f"View '{view_key}' not found. Available views: {list(self.views.keys())}"
            )

        view = self.views[view_key]

        try:
            # Compile the config through all passes
            compiled = self._compile(raw_cfg)

            # Materialize the view
            result = view.materialize(compiled, **params)

            # Make result immutable if it's a dict (prevents accidental mutation)
            if isinstance(result, dict):
                result = MappingProxyType(result)

            # Cache the result in backend
            self.cache_backend.set(cache_key, result)

            return result

        except Exception as e:
            raise ValueError(f"Failed to materialize view '{view_key}': {e}") from e

    def register_pass(self, pass_instance: Pass) -> None:
        """Register a new compile pass."""
        self.passes.append(pass_instance)

    def register_view(self, view: View) -> None:
        """Register a new view."""
        self.views[view.key] = view

    def clear_cache(self) -> None:
        """Clear all cached results."""
        self.cache_backend.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get kernel performance statistics."""
        cache_stats = self.cache_backend.get_stats()

        return {
            "cache_hits": self.stats.hits,
            "cache_misses": self.stats.misses,
            "total_queries": self.stats.total_queries,
            "hit_rate": self.stats.hit_rate,
            "cache_backend": cache_stats,
            "registered_passes": [type(p).__name__ for p in self.passes],
            "registered_views": list(self.views.keys()),
        }

    def get_stats_visualization(self) -> str:
        """Get formatted cache statistics visualization."""
        hit_rate = self.stats.hit_rate
        total = self.stats.total_queries
        hits = self.stats.hits
        misses = self.stats.misses

        # Get cache backend information
        cache_stats = self.cache_backend.get_stats()
        cache_type = cache_stats.get("type", "Unknown")
        backend_size = cache_stats.get("size", 0)

        # Performance indicator based on hit rate
        if hit_rate >= 80.0:
            perf_indicator = "EXCELLENT"
            perf_bar = "████████"  # 8/8 blocks
        elif hit_rate >= 60.0:
            perf_indicator = "GOOD"
            perf_bar = "██████  "  # 6/8 blocks
        elif hit_rate >= 40.0:
            perf_indicator = "FAIR"
            perf_bar = "████    "  # 4/8 blocks
        elif hit_rate >= 20.0:
            perf_indicator = "POOR"
            perf_bar = "██      "  # 2/8 blocks
        else:
            perf_indicator = "COLD"
            perf_bar = "        "  # 0/8 blocks

        # Cache efficiency visualization
        if backend_size > 0 and total > 0:
            efficiency = hits / max(1, backend_size)  # hits per cached item
            efficiency_desc = f"efficiency={efficiency:.1f}"
        else:
            efficiency_desc = "efficiency=0.0"

        # Build visualization
        lines = [
            "=== StrataRegula Kernel Stats ===",
            f"Cache Performance: {perf_indicator} [{perf_bar}] {hit_rate:.1f}%",
            f"Queries: {total} (hits={hits}, misses={misses})",
            f"Cache: {cache_type} {backend_size} entries, {efficiency_desc}",
            f"System: {len(self.passes)} passes, {len(self.views)} views",
        ]

        return "\n".join(lines)

    def log_stats_summary(self) -> None:
        """Log comprehensive statistics summary to stderr."""
        stats = self.get_stats()
        hit_rate = stats["hit_rate"]
        cache_backend_stats = stats.get("cache_backend", {})

        # Performance classification for logging
        if hit_rate >= 70.0:
            status = "TARGET_MET"
        elif hit_rate >= 50.0:
            status = "ACCEPTABLE"
        elif hit_rate > 0.0:
            status = "WARMING_UP"
        else:
            status = "COLD_START"

        # Extract L1/L2 information if available
        cache_type = cache_backend_stats.get("type", "Unknown")
        backend_hit_rate = cache_backend_stats.get("hit_rate", 0.0)
        backend_size = cache_backend_stats.get("size", 0)

        # Log enhanced StrataRegula format with cache backend details
        print(
            f"[sr-stats] queries={stats['total_queries']} cache={cache_type} "
            f"cache_size={backend_size} kernel_hit_rate={hit_rate:.1f}% "
            f"backend_hit_rate={backend_hit_rate:.1f}% status={status} "
            f"passes={len(stats['registered_passes'])} views={len(stats['registered_views'])}",
            file=sys.stderr,
        )

    def log_query(self, view_key: str, cache_hit: bool, duration_ms: float) -> None:
        """Log query information in StrataRegula format."""
        status = "hit" if cache_hit else "miss"
        passes_str = ",".join(type(p).__name__ for p in self.passes)

        print(
            f"[sr] view={view_key} passes={passes_str} cache={status} time={duration_ms:.1f}ms",
            file=sys.stderr,
        )
