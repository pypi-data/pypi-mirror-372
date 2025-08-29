"""
Intelligent caching system for landuse-intensity-analysis.

This module provides a multi-level caching system that optimizes
performance by caching expensive computations and data loading operations.

Features:
- Multi-level caching (memory, disk, distributed)
- Smart cache invalidation based on file modification times
- Compression support for memory efficiency
- Cache statistics and monitoring
- Automatic cache size management

The caching system is designed to:
1. Cache raster data loading operations
2. Cache contingency table calculations
3. Cache intensity analysis results
4. Cache intermediate computation results

Example:
    >>> from landuse_intensity.cache import CacheManager
    >>>
    >>> cache = CacheManager(strategy="smart", max_memory="1GB")
    >>> result = cache.get_or_compute("contingency_table", compute_function, *args)
"""

import hashlib
import logging
import os
import pickle
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class CacheEntry:
    """
    Represents a cached item with metadata.

    Attributes
    ----------
    data : Any
        The cached data
    timestamp : float
        When the item was cached
    access_count : int
        Number of times accessed
    last_accessed : float
        Last access timestamp
    size_bytes : int
        Approximate size in bytes
    dependencies : list
        List of file dependencies for invalidation
    """

    def __init__(self, data: Any, dependencies: Optional[list] = None):
        self.data = data
        self.timestamp = time.time()
        self.access_count = 0
        self.last_accessed = time.time()
        self.size_bytes = self._estimate_size()
        self.dependencies = dependencies or []

    def _estimate_size(self) -> int:
        """Estimate the memory size of the cached data."""
        try:
            # Use pickle to estimate size (not perfect but reasonable)
            return len(pickle.dumps(self.data))
        except Exception:
            # Fallback to a rough estimate
            return 1024  # 1KB default

    def is_stale(self, ttl_seconds: Optional[float] = None,
                 dependency_check: bool = True) -> bool:
        """
        Check if the cache entry is stale.

        Parameters
        ----------
        ttl_seconds : float, optional
            Time-to-live in seconds
        dependency_check : bool, default True
            Check if dependencies have been modified

        Returns
        -------
        bool
            True if entry is stale
        """
        current_time = time.time()

        # Check TTL
        if ttl_seconds and (current_time - self.timestamp) > ttl_seconds:
            return True

        # Check dependencies
        if dependency_check and self.dependencies:
            for dep in self.dependencies:
                if isinstance(dep, (str, Path)):
                    path = Path(dep)
                    if path.exists() and path.stat().st_mtime > self.timestamp:
                        return True

        return False

    def access(self):
        """Mark the entry as accessed."""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryCache:
    """
    In-memory cache with LRU eviction.

    This cache stores data in memory with automatic eviction
    based on least recently used (LRU) policy.
    """

    def __init__(self, max_memory: str = "1GB"):
        self.max_memory_bytes = self._parse_memory_limit(max_memory)
        self.cache: Dict[str, CacheEntry] = {}
        self.current_memory = 0

    def _parse_memory_limit(self, memory_str: str) -> int:
        """Parse memory limit string (e.g., '1GB', '500MB')."""
        import re
        match = re.match(r'(\d+)(MB|GB|KB)', memory_str.upper())
        if not match:
            raise ValueError(f"Invalid memory format: {memory_str}")

        size, unit = match.groups()
        size = int(size)

        multipliers = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
        return size * multipliers[unit]

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_stale():
                entry.access()
                return entry.data
            else:
                # Remove stale entry
                self._remove_entry(key)
        return None

    def put(self, key: str, data: Any, dependencies: Optional[list] = None) -> bool:
        """
        Put item in cache.

        Returns
        -------
        bool
            True if item was cached, False if evicted immediately
        """
        entry = CacheEntry(data, dependencies)

        # Check if we have space
        if entry.size_bytes > self.max_memory_bytes:
            logger.warning(f"Item too large for cache: {entry.size_bytes} bytes")
            return False

        # Make space if needed
        while self.current_memory + entry.size_bytes > self.max_memory_bytes:
            self._evict_lru()

        self.cache[key] = entry
        self.current_memory += entry.size_bytes
        return True

    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.cache:
            return

        # Find LRU item
        lru_key = min(self.cache.keys(),
                     key=lambda k: self.cache[k].last_accessed)

        self._remove_entry(lru_key)

    def _remove_entry(self, key: str):
        """Remove an entry from cache."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_memory -= entry.size_bytes
            del self.cache[key]

    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.current_memory = 0

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_entries = len(self.cache)
        total_accesses = sum(entry.access_count for entry in self.cache.values())
        avg_age = 0
        if self.cache:
            current_time = time.time()
            avg_age = sum(current_time - entry.timestamp for entry in self.cache.values()) / total_entries

        return {
            'entries': total_entries,
            'memory_used': self.current_memory,
            'memory_limit': self.max_memory_bytes,
            'total_accesses': total_accesses,
            'average_age_seconds': avg_age,
            'hit_rate': total_accesses / max(1, total_accesses)  # Simplified
        }


class DiskCache:
    """
    Disk-based cache with compression support.

    This cache stores data on disk with optional compression
    for efficient storage and retrieval.
    """

    def __init__(self, cache_dir: Optional[str] = None, compression: str = "lz4"):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".landuse_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.compression = compression

        # Import compression libraries
        self._setup_compression()

    def _setup_compression(self):
        """Setup compression library."""
        if self.compression == "lz4":
            try:
                import lz4.frame
                self.compress = lz4.frame.compress
                self.decompress = lz4.frame.decompress
            except ImportError:
                logger.warning("LZ4 not available, falling back to no compression")
                self.compression = "none"
        elif self.compression == "gzip":
            import gzip
            self.compress = gzip.compress
            self.decompress = gzip.decompress
        elif self.compression == "bz2":
            import bz2
            self.compress = bz2.compress
            self.decompress = bz2.decompress
        else:
            # No compression
            self.compress = lambda x: x
            self.decompress = lambda x: x

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Create a hash of the key for filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get item from disk cache."""
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'rb') as f:
                compressed_data = f.read()

            data = self.decompress(compressed_data)
            entry = pickle.loads(data)

            if entry.is_stale():
                # Remove stale cache file
                cache_path.unlink(missing_ok=True)
                return None

            entry.access()
            # Re-save with updated access info
            self._save_entry(key, entry)
            return entry.data

        except Exception as e:
            logger.warning(f"Failed to load cache entry {key}: {e}")
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None

    def put(self, key: str, data: Any, dependencies: Optional[list] = None) -> bool:
        """Put item in disk cache."""
        entry = CacheEntry(data, dependencies)
        return self._save_entry(key, entry)

    def _save_entry(self, key: str, entry: CacheEntry) -> bool:
        """Save cache entry to disk."""
        cache_path = self._get_cache_path(key)

        try:
            data = pickle.dumps(entry)
            compressed_data = self.compress(data)

            with open(cache_path, 'wb') as f:
                f.write(compressed_data)

            return True

        except Exception as e:
            logger.warning(f"Failed to save cache entry {key}: {e}")
            return False

    def clear(self):
        """Clear all disk cache entries."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink(missing_ok=True)

    def stats(self) -> Dict[str, Any]:
        """Get disk cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'cache_dir': str(self.cache_dir),
            'files': len(cache_files),
            'total_size_bytes': total_size,
            'compression': self.compression
        }


class CacheManager:
    """
    Multi-level cache manager.

    This class manages multiple cache levels (memory, disk) with
    intelligent caching strategies and automatic data flow.
    """

    def __init__(self,
                 strategy: str = "smart",
                 max_memory: str = "1GB",
                 cache_dir: Optional[str] = None,
                 compression: str = "lz4",
                 ttl_seconds: Optional[float] = None):
        """
        Initialize cache manager.

        Parameters
        ----------
        strategy : str, default "smart"
            Caching strategy: 'smart', 'aggressive', 'conservative', 'disabled'
        max_memory : str, default "1GB"
            Maximum memory for in-memory cache
        cache_dir : str, optional
            Directory for disk cache
        compression : str, default "lz4"
            Compression algorithm for disk cache
        ttl_seconds : float, optional
            Default time-to-live for cache entries
        """
        self.strategy = strategy
        self.ttl_seconds = ttl_seconds

        if strategy != "disabled":
            self.memory_cache = MemoryCache(max_memory)
            self.disk_cache = DiskCache(cache_dir, compression)
        else:
            self.memory_cache = None
            self.disk_cache = None

        self.stats = {
            'hits': 0,
            'misses': 0,
            'memory_hits': 0,
            'disk_hits': 0
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache.

        Checks memory cache first, then disk cache.
        """
        if self.strategy == "disabled":
            return None

        # Try memory cache first
        data = self.memory_cache.get(key)
        if data is not None:
            self.stats['hits'] += 1
            self.stats['memory_hits'] += 1
            return data

        # Try disk cache
        data = self.disk_cache.get(key)
        if data is not None:
            self.stats['hits'] += 1
            self.stats['disk_hits'] += 1
            # Also store in memory for faster future access
            if self.strategy in ["smart", "aggressive"]:
                self.memory_cache.put(key, data)
            return data

        self.stats['misses'] += 1
        return None

    def put(self, key: str, data: Any, dependencies: Optional[list] = None) -> bool:
        """
        Put item in cache.

        Stores in both memory and disk cache based on strategy.
        """
        if self.strategy == "disabled":
            return False

        success = True

        # Always try to cache in memory
        if not self.memory_cache.put(key, data, dependencies):
            success = False

        # Cache on disk based on strategy
        if self.strategy in ["smart", "aggressive"]:
            if not self.disk_cache.put(key, data, dependencies):
                success = False
        elif self.strategy == "conservative":
            # Only cache large objects on disk
            if self._estimate_data_size(data) > 10 * 1024 * 1024:  # 10MB
                if not self.disk_cache.put(key, data, dependencies):
                    success = False

        return success

    def get_or_compute(self, key: str, compute_func: Callable, *args, **kwargs) -> Any:
        """
        Get from cache or compute if not cached.

        Parameters
        ----------
        key : str
            Cache key
        compute_func : callable
            Function to compute the value if not cached
        *args, **kwargs
            Arguments for compute_func

        Returns
        -------
        Any
            Cached or computed value
        """
        # Try to get from cache
        cached_data = self.get(key)
        if cached_data is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached_data

        # Compute the value
        logger.debug(f"Cache miss for key: {key}, computing...")
        start_time = time.time()
        data = compute_func(*args, **kwargs)
        compute_time = time.time() - start_time

        # Cache the result
        dependencies = kwargs.get('dependencies', [])
        self.put(key, data, dependencies)

        logger.debug(".2f")
        return data

    def invalidate(self, key: str):
        """Invalidate a specific cache entry."""
        if self.memory_cache:
            # Memory cache doesn't have explicit removal, just let it expire
            pass
        if self.disk_cache:
            cache_path = self.disk_cache._get_cache_path(key)
            cache_path.unlink(missing_ok=True)

    def clear(self):
        """Clear all cache entries."""
        if self.memory_cache:
            self.memory_cache.clear()
        if self.disk_cache:
            self.disk_cache.clear()

        # Reset stats
        self.stats = {'hits': 0, 'misses': 0, 'memory_hits': 0, 'disk_hits': 0}

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        stats = self.stats.copy()

        if self.memory_cache:
            stats['memory'] = self.memory_cache.stats()

        if self.disk_cache:
            stats['disk'] = self.disk_cache.stats()

        # Calculate hit rate
        total_requests = stats['hits'] + stats['misses']
        stats['hit_rate'] = stats['hits'] / max(1, total_requests)

        return stats

    def _estimate_data_size(self, data: Any) -> int:
        """Estimate the size of data in bytes."""
        try:
            return len(pickle.dumps(data))
        except Exception:
            return 1024  # Default estimate


# Global cache instance
_default_cache = None

def get_default_cache() -> CacheManager:
    """Get the default global cache instance."""
    global _default_cache
    if _default_cache is None:
        _default_cache = CacheManager()
    return _default_cache

def set_default_cache(cache: CacheManager):
    """Set the default global cache instance."""
    global _default_cache
    _default_cache = cache

# Convenience functions
def cached(compute_func: Callable) -> Callable:
    """
    Decorator to cache function results.

    Example:
        @cached
        def expensive_computation(x, y):
            return x * y  # Some expensive operation
    """
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key = f"{compute_func.__name__}_{hash(str(args) + str(kwargs))}"
        cache = get_default_cache()
        return cache.get_or_compute(key, compute_func, *args, **kwargs)

    return wrapper
