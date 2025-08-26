"""
Advanced Caching System for Rust Crate Pipeline

Provides intelligent caching with multiple strategies:
- Memory cache (fastest)
- Disk cache (persistent)
- Distributed cache (Redis/Memcached)
- Intelligent cache invalidation
- Cache warming and prefetching
"""

import hashlib
import json
import logging
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
import redis.asyncio as redis
from cachetools import TTLCache


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl: Optional[int] = None  # seconds
    tags: List[str] = field(default_factory=list)
    size_bytes: int = 0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)

    def touch(self) -> None:
        """Update access time and count."""
        self.accessed_at = datetime.utcnow()
        self.access_count += 1


class CacheStrategy(ABC):
    """Abstract base class for cache strategies."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Store value in cache."""

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""

    @abstractmethod
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags."""


class MemoryCache(CacheStrategy):
    """In-memory cache using TTLCache."""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.logger = logging.getLogger(__name__)

    async def get(self, key: str) -> Optional[Any]:
        try:
            return self.cache.get(key)
        except Exception as e:
            self.logger.warning(f"Memory cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            self.cache[key] = value
            return True
        except Exception as e:
            self.logger.warning(f"Memory cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            return self.cache.pop(key, None) is not None
        except Exception as e:
            self.logger.warning(f"Memory cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self.cache.clear()
            return True
        except Exception as e:
            self.logger.warning(f"Memory cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        # Memory cache doesn't support tag-based invalidation
        return 0


class DiskCache(CacheStrategy):
    """Persistent disk cache with intelligent file management."""

    def __init__(self, cache_dir: str = "./cache", max_size_mb: int = 1024):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata: Dict[str, CacheEntry] = {}
        self.logger = logging.getLogger(__name__)
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, "r") as f:
                    data = json.load(f)
                    self.metadata = {}
                    for k, v in data.items():
                        try:
                            # Handle both old and new cache entry formats
                            if isinstance(v, dict):
                                # Ensure required fields exist
                                if "value" not in v:
                                    v["value"] = None  # Default value for old entries
                                if "key" not in v:
                                    v["key"] = k

                                # Convert datetime strings back to datetime objects
                                if "created_at" in v and isinstance(
                                    v["created_at"], str
                                ):
                                    v["created_at"] = datetime.fromisoformat(
                                        v["created_at"]
                                    )
                                if "accessed_at" in v and isinstance(
                                    v["accessed_at"], str
                                ):
                                    v["accessed_at"] = datetime.fromisoformat(
                                        v["accessed_at"]
                                    )

                                self.metadata[k] = CacheEntry(**v)
                            else:
                                # Handle legacy format - create new entry
                                self.metadata[k] = CacheEntry(
                                    key=k,
                                    value=None,
                                    created_at=datetime.utcnow(),
                                    accessed_at=datetime.utcnow(),
                                )
                        except Exception as entry_error:
                            self.logger.debug(
                                f"Skipping invalid cache entry {k}: {entry_error}"
                            )
                            continue
        except Exception as e:
            self.logger.warning(f"Failed to load cache metadata: {e}")
            self.metadata = {}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(
                    {
                        k: {
                            "key": v.key,
                            "created_at": v.created_at.isoformat(),
                            "accessed_at": v.accessed_at.isoformat(),
                            "access_count": v.access_count,
                            "ttl": v.ttl,
                            "tags": v.tags,
                            "size_bytes": v.size_bytes,
                        }
                        for k, v in self.metadata.items()
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            self.logger.warning(f"Failed to save cache metadata: {e}")

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    async def get(self, key: str) -> Optional[Any]:
        try:
            if key not in self.metadata:
                return None

            entry = self.metadata[key]
            if entry.is_expired():
                await self.delete(key)
                return None

            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None

            async with aiofiles.open(cache_path, "rb") as f:
                data = await f.read()
                value = pickle.loads(data)

            # Update access metadata
            entry.touch()
            self._save_metadata()

            return value
        except Exception as e:
            self.logger.warning(f"Disk cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        try:
            # Serialize value
            data = pickle.dumps(value)
            size_bytes = len(data)

            # Check cache size limits
            await self._enforce_size_limit(size_bytes)

            # Save to disk
            cache_path = self._get_cache_path(key)
            async with aiofiles.open(cache_path, "wb") as f:
                await f.write(data)

            # Update metadata
            self.metadata[key] = CacheEntry(
                key=key,
                value=None,  # Don't store value in metadata
                ttl=ttl,
                tags=tags or [],
                size_bytes=size_bytes,
            )
            self._save_metadata()

            return True
        except Exception as e:
            self.logger.warning(f"Disk cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            if key in self.metadata:
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    cache_path.unlink()
                del self.metadata[key]
                self._save_metadata()
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Disk cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        try:
            # Remove all cache files
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()

            # Clear metadata
            self.metadata.clear()
            self._save_metadata()
            return True
        except Exception as e:
            self.logger.warning(f"Disk cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries that match any of the provided tags."""
        try:
            invalidated = 0
            keys_to_delete = []

            for key, entry in self.metadata.items():
                if any(tag in entry.tags for tag in tags):
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                if await self.delete(key):
                    invalidated += 1

            return invalidated
        except Exception as e:
            self.logger.warning(f"Disk cache tag invalidation error: {e}")
            return 0

    async def _enforce_size_limit(self, new_entry_size: int) -> None:
        """Enforce cache size limits by removing least recently used entries."""
        current_size = sum(entry.size_bytes for entry in self.metadata.values())

        if current_size + new_entry_size <= self.max_size_bytes:
            return

        # Sort by access time (oldest first)
        sorted_entries = sorted(self.metadata.items(), key=lambda x: x[1].accessed_at)

        # Remove entries until we have enough space
        for key, entry in sorted_entries:
            if current_size + new_entry_size <= self.max_size_bytes:
                break

            await self.delete(key)
            current_size -= entry.size_bytes


class RedisCache(CacheStrategy):
    """Redis-based distributed cache."""

    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_url = redis_url
        self.db = db
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        self._tag_prefix = "cache_tags:"
        self._key_prefix = "cache_data:"

    async def _connect(self) -> bool:
        """Establish Redis connection."""
        if self.connected and self.redis_client:
            return True

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )

            # Test connection
            await self.redis_client.ping()
            self.connected = True
            self.logger.info("Redis cache connected successfully")
            return True

        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.connected = False
            self.redis_client = None
            return False

    async def _disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except Exception as e:
                self.logger.warning(f"Redis disconnect error: {e}")
            finally:
                self.connected = False
                self.redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from Redis cache."""
        if not await self._connect():
            return None

        try:
            cache_key = f"{self._key_prefix}{key}"
            data = await self.redis_client.get(cache_key)

            if data is None:
                return None

            # Deserialize data
            value = pickle.loads(data)
            return value

        except Exception as e:
            self.logger.warning(f"Redis cache get error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Store value in Redis cache."""
        if not await self._connect():
            return False

        try:
            # Serialize value
            data = pickle.dumps(value)
            cache_key = f"{self._key_prefix}{key}"

            # Store data with TTL
            if ttl:
                await self.redis_client.setex(cache_key, ttl, data)
            else:
                await self.redis_client.set(cache_key, data)

            # Store tags for invalidation
            if tags:
                for tag in tags:
                    tag_key = f"{self._tag_prefix}{tag}"
                    await self.redis_client.sadd(tag_key, key)

                    # Set TTL on tag keys if provided
                    if ttl:
                        await self.redis_client.expire(
                            tag_key, ttl + 300
                        )  # Extra 5 minutes

            return True

        except Exception as e:
            self.logger.warning(f"Redis cache set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        if not await self._connect():
            return False

        try:
            cache_key = f"{self._key_prefix}{key}"
            result = await self.redis_client.delete(cache_key)

            # Also remove from tag sets
            tag_keys = await self.redis_client.keys(f"{self._tag_prefix}*")
            for tag_key in tag_keys:
                await self.redis_client.srem(tag_key, key)

            return result > 0

        except Exception as e:
            self.logger.warning(f"Redis cache delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        if not await self._connect():
            return False

        try:
            # Delete all cache data keys
            data_keys = await self.redis_client.keys(f"{self._key_prefix}*")
            tag_keys = await self.redis_client.keys(f"{self._tag_prefix}*")

            all_keys = data_keys + tag_keys
            if all_keys:
                await self.redis_client.delete(*all_keys)

            return True

        except Exception as e:
            self.logger.warning(f"Redis cache clear error: {e}")
            return False

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags."""
        if not await self._connect():
            return 0

        try:
            invalidated = 0

            for tag in tags:
                tag_key = f"{self._tag_prefix}{tag}"

                # Get all keys associated with this tag
                keys = await self.redis_client.smembers(tag_key)

                if keys:
                    # Delete cache entries
                    cache_keys = [f"{self._key_prefix}{key.decode()}" for key in keys]
                    deleted = await self.redis_client.delete(*cache_keys)
                    invalidated += deleted

                    # Delete the tag set
                    await self.redis_client.delete(tag_key)

            return invalidated

        except Exception as e:
            self.logger.warning(f"Redis cache tag invalidation error: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        if not await self._connect():
            return {}

        try:
            info = await self.redis_client.info()

            # Count our cache keys
            data_keys = await self.redis_client.keys(f"{self._key_prefix}*")
            tag_keys = await self.redis_client.keys(f"{self._tag_prefix}*")

            return {
                "connected": self.connected,
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_connections_received": info.get("total_connections_received", 0),
                "cache_keys": len(data_keys),
                "tag_keys": len(tag_keys),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
            }

        except Exception as e:
            self.logger.warning(f"Redis stats error: {e}")
            return {"connected": False, "error": str(e)}


@dataclass
class CacheMetrics:
    """Cache performance metrics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    clears: int = 0
    errors: int = 0
    total_size_bytes: int = 0

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    @property
    def total_operations(self) -> int:
        """Total cache operations."""
        return self.hits + self.misses + self.sets + self.deletes + self.clears


class AdvancedCache:
    """Multi-level intelligent cache system."""

    def __init__(
        self,
        memory_cache_size: int = 1000,
        memory_ttl: int = 3600,
        disk_cache_dir: str = "./cache",
        disk_max_size_mb: int = 1024,
        redis_url: Optional[str] = None,
        redis_db: int = 0,
        enable_metrics: bool = True,
    ):
        self.logger = logging.getLogger(__name__)
        self.enable_metrics = enable_metrics
        self.metrics = CacheMetrics() if enable_metrics else None

        # Initialize cache strategies
        self.strategies: List[CacheStrategy] = []

        # Memory cache (fastest)
        self.memory_cache = MemoryCache(maxsize=memory_cache_size, ttl=memory_ttl)
        self.strategies.append(self.memory_cache)

        # Disk cache (persistent)
        self.disk_cache = DiskCache(
            cache_dir=disk_cache_dir, max_size_mb=disk_max_size_mb
        )
        self.strategies.append(self.disk_cache)

        # Redis cache (distributed) - optional
        self.redis_cache: Optional[RedisCache] = None
        if redis_url:
            self.redis_cache = RedisCache(redis_url=redis_url, db=redis_db)
            self.strategies.append(self.redis_cache)

        self.logger.info(
            f"Initialized AdvancedCache with {len(self.strategies)} strategies"
        )

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache (tries strategies in order)."""
        for i, strategy in enumerate(self.strategies):
            try:
                value = await strategy.get(key)
                if value is not None:
                    # Cache hit - promote to faster caches
                    await self._promote_to_faster_caches(key, value, i)

                    if self.metrics:
                        self.metrics.hits += 1

                    return value

            except Exception as e:
                self.logger.warning(f"Cache get error in strategy {i}: {e}")
                if self.metrics:
                    self.metrics.errors += 1

        # Cache miss
        if self.metrics:
            self.metrics.misses += 1

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Store value in all cache strategies."""
        success = False

        for i, strategy in enumerate(self.strategies):
            try:
                if await strategy.set(key, value, ttl, tags):
                    success = True

            except Exception as e:
                self.logger.warning(f"Cache set error in strategy {i}: {e}")
                if self.metrics:
                    self.metrics.errors += 1

        if success and self.metrics:
            self.metrics.sets += 1

            # Estimate size for metrics
            try:
                size = len(pickle.dumps(value))
                self.metrics.total_size_bytes += size
            except Exception:
                pass

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from all cache strategies."""
        success = False

        for i, strategy in enumerate(self.strategies):
            try:
                if await strategy.delete(key):
                    success = True

            except Exception as e:
                self.logger.warning(f"Cache delete error in strategy {i}: {e}")
                if self.metrics:
                    self.metrics.errors += 1

        if success and self.metrics:
            self.metrics.deletes += 1

        return success

    async def clear(self) -> bool:
        """Clear all cache strategies."""
        success = False

        for i, strategy in enumerate(self.strategies):
            try:
                if await strategy.clear():
                    success = True

            except Exception as e:
                self.logger.warning(f"Cache clear error in strategy {i}: {e}")
                if self.metrics:
                    self.metrics.errors += 1

        if success and self.metrics:
            self.metrics.clears += 1
            self.metrics.total_size_bytes = 0

        return success

    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate entries by tags across all strategies."""
        total_invalidated = 0

        for i, strategy in enumerate(self.strategies):
            try:
                invalidated = await strategy.invalidate_by_tags(tags)
                total_invalidated += invalidated

            except Exception as e:
                self.logger.warning(
                    f"Cache tag invalidation error in strategy {i}: {e}"
                )
                if self.metrics:
                    self.metrics.errors += 1

        return total_invalidated

    async def _promote_to_faster_caches(
        self, key: str, value: Any, source_index: int
    ) -> None:
        """Promote cache entry to faster cache layers."""
        for i in range(source_index):
            try:
                await self.strategies[i].set(key, value)
            except Exception as e:
                self.logger.warning(f"Cache promotion error to strategy {i}: {e}")

    async def warm_cache(
        self, keys_and_values: Dict[str, Any], ttl: Optional[int] = None
    ) -> int:
        """Warm cache with pre-computed values."""
        warmed = 0

        for key, value in keys_and_values.items():
            try:
                if await self.set(key, value, ttl):
                    warmed += 1
            except Exception as e:
                self.logger.warning(f"Cache warming error for key {key}: {e}")

        self.logger.info(f"Warmed cache with {warmed}/{len(keys_and_values)} entries")
        return warmed

    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = {
            "strategies": len(self.strategies),
            "memory_cache": {"available": True},
            "disk_cache": {"available": True},
            "redis_cache": {"available": self.redis_cache is not None},
        }

        # Add metrics if enabled
        if self.metrics:
            stats["metrics"] = {
                "hits": self.metrics.hits,
                "misses": self.metrics.misses,
                "hit_rate": self.metrics.hit_rate,
                "sets": self.metrics.sets,
                "deletes": self.metrics.deletes,
                "clears": self.metrics.clears,
                "errors": self.metrics.errors,
                "total_operations": self.metrics.total_operations,
                "total_size_bytes": self.metrics.total_size_bytes,
            }

        # Get Redis stats if available
        if self.redis_cache:
            try:
                redis_stats = await self.redis_cache.get_stats()
                stats["redis_cache"].update(redis_stats)
            except Exception as e:
                stats["redis_cache"]["error"] = str(e)

        return stats

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup connections."""
        if self.redis_cache:
            await self.redis_cache._disconnect()


# Global cache instance
_global_cache: Optional[AdvancedCache] = None


def get_cache(
    memory_cache_size: int = 1000,
    disk_cache_dir: str = "./cache",
    redis_url: Optional[str] = None,
) -> AdvancedCache:
    """Get global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = AdvancedCache(
            memory_cache_size=memory_cache_size,
            disk_cache_dir=disk_cache_dir,
            redis_url=redis_url,
        )
    return _global_cache


def set_cache(cache: AdvancedCache) -> None:
    """Set global cache instance."""
    global _global_cache
    _global_cache = cache


async def cache_decorator(
    key_func: Optional[callable] = None,
    ttl: Optional[int] = None,
    tags: Optional[List[str]] = None,
):
    """Decorator for caching function results."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cache = get_cache()
            result = await cache.get(cache_key)

            if result is not None:
                return result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl, tags)

            return result

        return wrapper

    return decorator


# Utility functions for cache management
async def cache_health_check() -> Dict[str, Any]:
    """Perform cache system health check."""
    cache = get_cache()

    health = {"healthy": True, "checks": {}, "timestamp": datetime.utcnow().isoformat()}

    # Test basic operations
    test_key = f"health_check_{int(datetime.utcnow().timestamp())}"
    test_value = {"test": True, "timestamp": datetime.utcnow().isoformat()}

    try:
        # Test set
        set_success = await cache.set(test_key, test_value, ttl=60)
        health["checks"]["set"] = set_success

        # Test get
        retrieved = await cache.get(test_key)
        get_success = retrieved is not None and retrieved.get("test") is True
        health["checks"]["get"] = get_success

        # Test delete
        delete_success = await cache.delete(test_key)
        health["checks"]["delete"] = delete_success

        # Overall health
        health["healthy"] = all(health["checks"].values())

    except Exception as e:
        health["healthy"] = False
        health["error"] = str(e)

    # Add stats
    try:
        health["stats"] = await cache.get_stats()
    except Exception as e:
        health["stats_error"] = str(e)

    return health


async def cache_cleanup(
    max_age_hours: int = 24, max_size_mb: Optional[int] = None
) -> Dict[str, int]:
    """Perform cache cleanup operations."""
    cache = get_cache()

    cleanup_stats = {"expired_cleaned": 0, "size_cleaned": 0, "errors": 0}

    try:
        # This would require additional metadata tracking
        # For now, we rely on individual cache strategies' cleanup

        # Get current stats
        stats = await cache.get_stats()

        # If we have size limits and current size exceeds them
        if (
            max_size_mb
            and stats.get("metrics", {}).get("total_size_bytes", 0)
            > max_size_mb * 1024 * 1024
        ):
            # Clear least recently used items (implementation depends on strategy)
            pass

        return cleanup_stats

    except Exception as e:
        cleanup_stats["errors"] += 1
        cache.logger.error(f"Cache cleanup error: {e}")
        return cleanup_stats
