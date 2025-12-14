"""
Caching System for TestGen AI.

This module implements caching for scan results and LLM responses
to improve performance and reduce API costs.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class CacheEntry:
    """Single cache entry."""
    
    key: str
    value: Any
    timestamp: str
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if not self.expires_at:
            return False
        
        expiry = datetime.fromisoformat(self.expires_at)
        return datetime.now() > expiry


class CacheManager:
    """
    Manages caching for scan results and LLM responses.
    
    Implements Task 44 requirements:
    - Cache scan results to avoid re-analysis
    - Cache LLM responses for identical inputs
    - Use file hash as cache key
    
    Example:
        >>> cache = CacheManager()
        >>> cache.set("scan_result_abc123", scan_data)
        >>> result = cache.get("scan_result_abc123")
    """
    
    def __init__(
        self,
        cache_dir: str = ".testgen-cache",
        default_ttl_hours: int = 24
    ):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory for cache files
            default_ttl_hours: Default time-to-live in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        # Create subdirectories
        (self.cache_dir / "scans").mkdir(exist_ok=True)
        (self.cache_dir / "llm").mkdir(exist_ok=True)
    
    def get_file_hash(self, file_path: str) -> str:
        """
        Calculate hash of file for cache key (Task 44 requirement).
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash of file contents
            
        Example:
            >>> cache = CacheManager()
            >>> hash_key = cache.get_file_hash("src/example.py")
        """
        path = Path(file_path)
        
        if not path.exists():
            return hashlib.sha256(file_path.encode()).hexdigest()[:16]
        
        # Hash file contents
        sha256 = hashlib.sha256()
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()[:16]  # Use first 16 chars
    
    def cache_scan_result(
        self,
        file_path: str,
        scan_result: Dict[str, Any],
        ttl_hours: Optional[int] = None
    ) -> str:
        """
        Cache scan result for a file (Task 44 requirement).
        
        Args:
            file_path: Path to scanned file
            scan_result: Scan result data
            ttl_hours: Time-to-live in hours
            
        Returns:
            Cache key
            
        Example:
            >>> cache.cache_scan_result("src/utils.py", scan_data)
        """
        # Generate cache key from file hash
        file_hash = self.get_file_hash(file_path)
        cache_key = f"scan_{file_hash}"
        
        # Set cache entry
        self.set(
            cache_key,
            scan_result,
            ttl_hours=ttl_hours,
            category="scans",
            metadata={"file_path": file_path}
        )
        
        return cache_key
    
    def get_scan_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached scan result (Task 44 requirement).
        
        Args:
            file_path: Path to file
            
        Returns:
            Cached scan result or None
            
        Example:
            >>> result = cache.get_scan_result("src/utils.py")
            >>> if result:
            ...     print("Using cached scan")
        """
        file_hash = self.get_file_hash(file_path)
        cache_key = f"scan_{file_hash}"
        
        return self.get(cache_key, category="scans")
    
    def cache_llm_response(
        self,
        prompt: str,
        response: str,
        model: str = "default",
        ttl_hours: Optional[int] = None
    ) -> str:
        """
        Cache LLM response for identical prompt (Task 44 requirement).
        
        Args:
            prompt: LLM prompt
            response: LLM response
            model: Model name
            ttl_hours: Time-to-live
            
        Returns:
            Cache key
            
        Example:
            >>> cache.cache_llm_response(prompt, response, "gpt-4")
        """
        # Generate cache key from prompt hash
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        cache_key = f"llm_{model}_{prompt_hash}"
        
        self.set(
            cache_key,
            response,
            ttl_hours=ttl_hours,
            category="llm",
            metadata={"model": model, "prompt_length": len(prompt)}
        )
        
        return cache_key
    
    def get_llm_response(
        self,
        prompt: str,
        model: str = "default"
    ) -> Optional[str]:
        """
        Get cached LLM response (Task 44 requirement).
        
        Args:
            prompt: LLM prompt
            model: Model name
            
        Returns:
            Cached response or None
            
        Example:
            >>> cached = cache.get_llm_response(prompt, "gpt-4")
            >>> if cached:
            ...     return cached  # Skip API call!
        """
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        cache_key = f"llm_{model}_{prompt_hash}"
        
        return self.get(cache_key, category="llm")
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_hours: Optional[int] = None,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set cache entry.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_hours: Time-to-live in hours (None = use default)
            category: Cache category (scans, llm, general)
            metadata: Additional metadata
        """
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl
        expires_at = (datetime.now() + ttl).isoformat()
        
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=datetime.now().isoformat(),
            expires_at=expires_at,
            metadata=metadata
        )
        
        # Save to file
        cache_file = self.cache_dir / category / f"{key}.json"
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(entry), f, indent=2)
    
    def get(
        self,
        key: str,
        category: str = "general"
    ) -> Optional[Any]:
        """
        Get cache entry.
        
        Args:
            key: Cache key
            category: Cache category
            
        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self.cache_dir / category / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            entry = CacheEntry(**data)
            
            # Check expiration
            if entry.is_expired():
                self.delete(key, category)
                return None
            
            return entry.value
            
        except Exception:
            return None
    
    def delete(self, key: str, category: str = "general") -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key
            category: Cache category
            
        Returns:
            True if deleted
        """
        cache_file = self.cache_dir / category / f"{key}.json"
        
        if cache_file.exists():
            cache_file.unlink()
            return True
        
        return False
    
    def clear_category(self, category: str) -> int:
        """
        Clear all entries in a category.
        
        Args:
            category: Category to clear
            
        Returns:
            Number of entries deleted
        """
        category_dir = self.cache_dir / category
        
        if not category_dir.exists():
            return 0
        
        count = 0
        for cache_file in category_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        
        return count
    
    def clear_all(self) -> int:
        """
        Clear entire cache.
        
        Returns:
            Number of entries deleted
        """
        count = 0
        
        for category in ["scans", "llm", "general"]:
            count += self.clear_category(category)
        
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "scans": 0,
            "llm": 0,
            "general": 0,
            "total": 0,
            "expired": 0
        }
        
        for category in ["scans", "llm", "general"]:
            category_dir = self.cache_dir / category
            
            if not category_dir.exists():
                continue
            
            for cache_file in category_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    entry = CacheEntry(**data)
                    stats[category] += 1
                    stats["total"] += 1
                    
                    if entry.is_expired():
                        stats["expired"] += 1
                        
                except:
                    pass
        
        return stats


def get_cache() -> CacheManager:
    """
    Get global cache instance.
    
    Returns:
        CacheManager instance
        
    Example:
        >>> cache = get_cache()
        >>> cache.cache_scan_result(file, data)
    """
    return CacheManager()
