import time
import threading
from collections import OrderedDict
from typing import Any, Optional, Callable, List, Tuple

class AtikinCache:
    """
    High-performance in-memory caching with TTL and LRU eviction.
    
    Features:
    - Time-to-live (TTL) based expiration
    - LRU (Least Recently Used) eviction policy
    - Thread-safe operations
    - Optional persistence (see persistence.py)
    """
    
    def __init__(self, maxsize: int = 1000, default_ttl: int = 300,
                 persist_path: Optional[str] = None):
        """
        Initialize the cache.
        
        Args:
            maxsize: Maximum number of items to store (0 for unlimited)
            default_ttl: Default time-to-live in seconds for new items
            persist_path: Optional file path for persistent storage
        """
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._expiry_times = {}
        self._lock = threading.RLock()
        
        # Initialize persistence if requested
        self._persistence = None
        if persist_path:
            # Handle both relative and absolute imports
            try:
                from .persistence import PersistenceManager
            except ImportError:
                from persistence import PersistenceManager
            self._persistence = PersistenceManager(persist_path)
            self.load_from_disk()
    
    def set(self, key: Any, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a key-value pair in the cache with optional TTL.
        
        Args:
            key: Cache key
            value: Cache value
            ttl: Time-to-live in seconds (uses default if None)
        """
        with self._lock:
            # Remove if exists to update order
            if key in self._cache:
                self._delete(key)
            
            # Check if we need to evict
            if self.maxsize > 0 and len(self._cache) >= self.maxsize:
                self._evict()
            
            # Set value and expiry
            actual_ttl = ttl if ttl is not None else self.default_ttl
            self._cache[key] = value
            self._expiry_times[key] = time.time() + actual_ttl
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
    
    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get a value from the cache if it exists and hasn't expired.
        
        Args:
            key: Cache key to retrieve
            default: Default value to return if key not found or expired
            
        Returns:
            The cached value or default if not found/expired
        """
        with self._lock:
            # Check if exists and not expired
            if key not in self._cache or self._is_expired(key):
                return default
            
            # Update LRU order and return value
            self._cache.move_to_end(key)
            return self._cache[key]
    
    def delete(self, key: Any) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Key to delete
            
        Returns:
            True if key was deleted, False if it didn't exist
        """
        with self._lock:
            if key in self._cache:
                self._delete(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
            self._expiry_times.clear()
    
    def exists(self, key: Any) -> bool:
        """
        Check if a key exists in the cache and hasn't expired.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists and is not expired
        """
        with self._lock:
            return key in self._cache and not self._is_expired(key)
    
    def ttl(self, key: Any) -> Optional[float]:
        """
        Get the remaining time-to-live for a key.
        
        Args:
            key: Key to check TTL for
            
        Returns:
            Remaining TTL in seconds, or None if key doesn't exist or is expired
        """
        with self._lock:
            if key not in self._cache or self._is_expired(key):
                return None
            
            remaining = self._expiry_times[key] - time.time()
            return max(0, remaining)
    
    def keys(self) -> List[Any]:
        """
        Get all non-expired keys in the cache.
        
        Returns:
            List of keys in LRU order (most recently used last)
        """
        with self._lock:
            self._clean_expired()
            return list(self._cache.keys())
    
    def values(self) -> List[Any]:
        """
        Get all non-expired values in the cache.
        
        Returns:
            List of values in LRU order (most recently used last)
        """
        with self._lock:
            self._clean_expired()
            return list(self._cache.values())
    
    def items(self) -> List[Tuple[Any, Any]]:
        """
        Get all non-expired key-value pairs in the cache.
        
        Returns:
            List of (key, value) tuples in LRU order (most recently used last)
        """
        with self._lock:
            self._clean_expired()
            return list(self._cache.items())
    
    def size(self) -> int:
        """
        Get the number of non-expired items in the cache.
        
        Returns:
            Number of items currently in the cache
        """
        with self._lock:
            self._clean_expired()
            return len(self._cache)
    
    def save_to_disk(self) -> bool:
        """
        Save the cache to disk if persistence is enabled.
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self._persistence:
            return False
        
        with self._lock:
            self._clean_expired()
            return self._persistence.save({
                'cache': dict(self._cache),
                'expiry_times': self._expiry_times
            })
    
    def load_from_disk(self) -> bool:
        """
        Load the cache from disk if persistence is enabled.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self._persistence:
            return False
        
        with self._lock:
            data = self._persistence.load()
            if data:
                self._cache = OrderedDict(data.get('cache', {}))
                self._expiry_times = data.get('expiry_times', {})
                self._clean_expired()
                return True
            return False
    
    def _is_expired(self, key: Any) -> bool:
        """Check if a key has expired."""
        return time.time() > self._expiry_times.get(key, 0)
    
    def _delete(self, key: Any) -> None:
        """Delete a key from internal structures."""
        if key in self._cache:
            del self._cache[key]
        if key in self._expiry_times:
            del self._expiry_times[key]
    
    def _evict(self) -> None:
        """Evict the least recently used item."""
        if self._cache:
            key, _ = next(iter(self._cache.items()))
            self._delete(key)
    
    def _clean_expired(self) -> None:
        """Remove all expired items from the cache."""
        expired_keys = [key for key in self._cache if self._is_expired(key)]
        for key in expired_keys:
            self._delete(key)