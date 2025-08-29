"""Cache management service."""

import time
import yaml
from typing import Any, Optional, Dict
from pathlib import Path

from ..constants import CACHE_PATH, CACHE_TTL_SECONDS
from ..models import CacheEntry
from ..exceptions import CacheError


class CacheService:
    """Service for managing application cache."""
    
    def __init__(self, cache_path: Path = CACHE_PATH, ttl_seconds: int = CACHE_TTL_SECONDS):
        """Initialize the cache service."""
        self.cache_path = cache_path
        self.ttl_seconds = ttl_seconds
    
    def load_cache(self) -> Dict[str, Any]:
        """Load cache data from file."""
        if not self.cache_path.exists():
            return {}
        
        try:
            return yaml.safe_load(self.cache_path.read_text()) or {}
        except Exception as e:
            # Log warning but don't raise - cache corruption shouldn't break the app
            print(f"Warning: Cache file corrupted, creating new one. Error: {e}")
            return {}
    
    def save_cache(self, cache_data: Dict[str, Any]) -> None:
        """Save cache data to file."""
        try:
            with open(self.cache_path, 'w') as f:
                yaml.dump(cache_data, f, default_flow_style=False)
        except Exception as e:
            # Log warning but don't raise - cache save failure shouldn't break the app
            print(f"Warning: Could not save cache: {e}")
    
    def get_cache_key(self, prefix: str, *args: Any) -> str:
        """Generate a cache key with prefix."""
        if args:
            return f"{prefix}:" + ":".join(str(arg) for arg in args)
        return prefix
    
    def is_cache_valid(self, cache_entry: Any) -> bool:
        """Check if cache entry is still valid."""
        if not isinstance(cache_entry, dict) or 'timestamp' not in cache_entry or 'data' not in cache_entry:
            return False
        return (time.time() - cache_entry['timestamp']) < self.ttl_seconds
    
    def get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached data if valid."""
        cache = self.load_cache()
        cache_entry = cache.get(cache_key)
        if self.is_cache_valid(cache_entry):
            return cache_entry['data']
        return None
    
    def set_cached_data(self, cache_key: str, data: Any) -> None:
        """Store data in cache with timestamp."""
        cache = self.load_cache()
        cache[cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'type': type(data).__name__
        }
        self.save_cache(cache)
    
    def get_cached_data_safe(self, cache_key: str) -> Optional[Any]:
        """Get cached data with error handling for corrupted cache."""
        try:
            return self.get_cached_data(cache_key)
        except Exception as e:
            print(f"Warning: Cache corrupted for {cache_key}, clearing it. Error: {e}")
            # Clear just this cache entry
            cache = self.load_cache()
            if cache_key in cache:
                del cache[cache_key]
                self.save_cache(cache)
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        if self.cache_path.exists():
            self.cache_path.unlink()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache = self.load_cache()
        
        if not cache:
            return {"total_entries": 0, "entries": []}
        
        entries = []
        for key, cache_entry in cache.items():
            if isinstance(cache_entry, dict) and 'timestamp' in cache_entry:
                age_seconds = time.time() - cache_entry['timestamp']
                age_minutes = int(age_seconds / 60)
                data_type = cache_entry.get('type', 'unknown')
                entries.append({
                    "key": key,
                    "age_minutes": age_minutes,
                    "data_type": data_type,
                    "is_valid": self.is_cache_valid(cache_entry)
                })
            else:
                entries.append({
                    "key": key,
                    "age_minutes": -1,
                    "data_type": "invalid",
                    "is_valid": False
                })
        
        return {
            "total_entries": len(cache),
            "entries": entries
        }
