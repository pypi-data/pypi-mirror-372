"""
XTrade-AI Memory Manager

Handles memory management, caching, and cleanup to prevent memory leaks.
"""

import gc
import threading
import time
import weakref
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional

import numpy as np
import psutil

try:
    from .logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class MemoryManager:
    """Manages memory usage, caching, and cleanup."""

    def __init__(self, max_buffer_size: int = 10000, cleanup_interval: int = 300):
        self.logger = get_logger(__name__)
        self.max_buffer_size = max_buffer_size
        self.cleanup_interval = cleanup_interval
        self.buffers: Dict[str, List[Any]] = {}
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.max_cache_size = 1000
        self.last_cleanup = time.time()
        self._lock = threading.RLock()

        # Memory monitoring
        self.memory_threshold = 0.8  # 80% of available memory
        self.process = psutil.Process()

        # Register cleanup on exit
        import atexit

        atexit.register(self.cleanup_all)

    def add_to_buffer(
        self, buffer_name: str, item: Any, max_age: int = None, max_size: int = None
    ) -> None:
        """
        Add item to a named buffer with automatic cleanup.

        Args:
            buffer_name: Name of the buffer
            item: Item to add
            max_age: Maximum age in seconds for items in this buffer
            max_size: Maximum size for this buffer (overrides global max_buffer_size)
        """
        with self._lock:
            if buffer_name not in self.buffers:
                self.buffers[buffer_name] = []

            # Add timestamp if max_age is specified
            if max_age is not None:
                item_with_timestamp = {
                    "item": item,
                    "timestamp": time.time(),
                    "max_age": max_age,
                }
                self.buffers[buffer_name].append(item_with_timestamp)
            else:
                self.buffers[buffer_name].append(item)

            # Cleanup if buffer is full
            buffer_limit = max_size if max_size is not None else self.max_buffer_size
            if len(self.buffers[buffer_name]) > buffer_limit:
                self._cleanup_buffer(buffer_name, max_size)

    def get_from_buffer(self, buffer_name: str, index: int = -1) -> Optional[Any]:
        """Get item from buffer."""
        with self._lock:
            if buffer_name not in self.buffers or not self.buffers[buffer_name]:
                return None

            item = self.buffers[buffer_name][index]

            # Handle timestamped items
            if isinstance(item, dict) and "item" in item:
                return item["item"]
            return item

    def get_buffer_size(self, buffer_name: str) -> int:
        """Get current size of a buffer."""
        with self._lock:
            return len(self.buffers.get(buffer_name, []))

    def clear_buffer(self, buffer_name: str) -> None:
        """Clear a specific buffer."""
        with self._lock:
            if buffer_name in self.buffers:
                self.buffers[buffer_name].clear()
                self.logger.info(f"Cleared buffer: {buffer_name}")

    def add_to_cache(self, key: str, value: Any, ttl: int = None) -> None:
        """
        Add item to cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self._lock:
            # Remove oldest item if cache is full
            if len(self.cache) >= self.max_cache_size:
                self.cache.popitem(last=False)

            cache_entry = {"value": value, "timestamp": time.time(), "ttl": ttl}

            self.cache[key] = cache_entry

    def get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache with TTL validation."""
        with self._lock:
            if key not in self.cache:
                return None

            entry = self.cache[key]

            # Check TTL
            if entry["ttl"] is not None:
                if time.time() - entry["timestamp"] > entry["ttl"]:
                    del self.cache[key]
                    return None

            # Move to end (LRU)
            self.cache.move_to_end(key)
            return entry["value"]

    def _cleanup_buffer(self, buffer_name: str, max_size: int = None) -> None:
        """Clean up a specific buffer."""
        if buffer_name not in self.buffers:
            return

        buffer = self.buffers[buffer_name]
        current_time = time.time()
        buffer_limit = max_size if max_size is not None else self.max_buffer_size

        # Remove expired items
        if buffer and isinstance(buffer[0], dict) and "timestamp" in buffer[0]:
            # Timestamped items
            valid_items = []
            for item in buffer:
                if current_time - item["timestamp"] <= item["max_age"]:
                    valid_items.append(item)

            # Keep only the most recent items
            if len(valid_items) > buffer_limit // 2:
                valid_items = valid_items[-buffer_limit // 2 :]

            self.buffers[buffer_name] = valid_items
        else:
            # Regular items - keep only the most recent
            if len(buffer) > buffer_limit // 2:
                self.buffers[buffer_name] = buffer[-buffer_limit // 2 :]

    def cleanup_expired_cache(self) -> None:
        """Remove expired items from cache."""
        with self._lock:
            current_time = time.time()
            expired_keys = []

            for key, entry in self.cache.items():
                if entry["ttl"] is not None:
                    if current_time - entry["timestamp"] > entry["ttl"]:
                        expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                self.logger.debug(
                    f"Cleaned up {len(expired_keys)} expired cache entries"
                )

    def check_memory_usage(self) -> Dict[str, float]:
        """Check current memory usage."""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,
            "vms_mb": memory_info.vms / 1024 / 1024,
            "percent": memory_percent,
            "available_mb": psutil.virtual_memory().available / 1024 / 1024,
        }

    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical."""
        memory_usage = self.check_memory_usage()
        return memory_usage["percent"] > self.memory_threshold * 100

    def force_cleanup(self) -> None:
        """Force cleanup of all buffers and cache."""
        with self._lock:
            # Cleanup all buffers
            for buffer_name in list(self.buffers.keys()):
                self._cleanup_buffer(buffer_name)

            # Cleanup expired cache
            self.cleanup_expired_cache()

            # Force garbage collection
            gc.collect()

            self.last_cleanup = time.time()
            self.logger.info("Forced memory cleanup completed")

    def auto_cleanup(self) -> None:
        """Automatic cleanup based on time interval and memory usage."""
        current_time = time.time()

        # Check if cleanup is needed
        if (
            current_time - self.last_cleanup > self.cleanup_interval
            or self.is_memory_critical()
        ):
            self.force_cleanup()

    def cleanup_all(self) -> None:
        """Cleanup all resources."""
        with self._lock:
            self.buffers.clear()
            self.cache.clear()
            gc.collect()
            self.logger.info("All memory resources cleaned up")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        memory_usage = self.check_memory_usage()

        buffer_stats = {}
        for buffer_name, buffer in self.buffers.items():
            buffer_stats[buffer_name] = {
                "size": len(buffer),
                "max_size": self.max_buffer_size,
            }

        return {
            "memory_usage": memory_usage,
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "buffer_stats": buffer_stats,
            "is_critical": self.is_memory_critical(),
        }


# Global memory manager instance
_memory_manager = MemoryManager()


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    return _memory_manager


def auto_cleanup():
    """Convenience function for automatic cleanup."""
    _memory_manager.auto_cleanup()


def force_cleanup():
    """Convenience function for forced cleanup."""
    _memory_manager.force_cleanup()
