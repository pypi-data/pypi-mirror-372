"""Cache factory for configurable diskcache instances."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003
from typing import TYPE_CHECKING, Any, ClassVar

from bear_epoch_time.constants.time_related import SECONDS_IN_MINUTE as MINUTES
from diskcache import Cache

if TYPE_CHECKING:
    from pydantic import BaseModel


class ModifiedCache(Cache):
    """A modified cache class with additional functionality."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the cache with custom parameters."""
        super().__init__(*args, **kwargs)

    def find_and_delete(self, query: Any) -> bool:
        """Find and delete cache entries matching the query.

        Args:
            query: The query string to match against cache keys.
        """
        return any(isinstance(key, tuple | list) and str(query) in str(key) and self.delete(key) for key in self)


class BaseCacheFactory:
    """Factory for creating configured cache instances."""

    _default_size_limit: ClassVar[int] = 1_000_000_000  # bytes
    _default_eviction_policy: ClassVar[str] = "least-recently-used"
    _default_timeout: ClassVar[int] = 5 * MINUTES

    def __init__(self, base_dir: Path, config: BaseModel | None = None) -> None:
        """Initialize the cache factory."""
        self.base_dir: Path = base_dir
        self.config: BaseModel | None = config

    def get_size_limit(self, override: int | None = None) -> int:
        """Get the default size limit for caches."""
        return override or getattr(self.config, "default_size_limit", None) or self._default_size_limit

    def get_eviction_policy(self, override: str | None = None) -> str:
        """Get the default eviction policy for caches."""
        if override is not None:
            return override
        if not hasattr(self.config, "eviction_policy"):
            return self._default_eviction_policy
        return getattr(self.config, "eviction_policy", "")

    def get_timeout(self, override: int | None = None) -> int:
        """Get the default timeout for caches."""
        if override is not None:
            return override
        if not hasattr(self.config, "default_timeout"):
            return self._default_timeout
        return getattr(self.config, "default_timeout", 0)

    def get_cache(self, cache_type: str, **kwargs) -> ModifiedCache:
        """Get a cache instance for the specified type.

        Args:
            cache_type: name of the cache type (used as subdirectory)
            **kwargs: Optional overrides for size_limit, eviction_policy, timeout

        Returns:
            Configured Cache instance
        """
        return ModifiedCache(
            directory=str(self.base_dir / cache_type),
            size_limit=self.get_size_limit(kwargs.get("size_limit")),
            eviction_policy=self.get_eviction_policy(kwargs.get("eviction_policy")),
            ignore_exceptions=kwargs.get("ignore_exceptions", True),
            timeout=self.get_timeout(kwargs.get("timeout")),
        )


__all__ = ["BaseCacheFactory", "ModifiedCache"]
