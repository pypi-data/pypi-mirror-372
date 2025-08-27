# tests/test_cache.py
import pytest
from pathlib import Path
from quickquestion.cache import ProviderCache


def test_cache_singleton():
    """Test that ProviderCache is a singleton"""
    cache1 = ProviderCache()
    cache2 = ProviderCache()
    assert cache1 is cache2


def test_cache_operations():
    """Test basic cache operations"""
    cache = ProviderCache()
    
    # Test setting and getting
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    
    # Test non-existent key
    assert cache.get("nonexistent") is None
    
    # Test clearing
    cache.clear()
    assert cache.get("test_key") is None


def test_cache_ttl():
    """Test time-to-live functionality"""
    cache = ProviderCache()
    import time
    
    # Set with default TTL (30 seconds)
    cache.set("quick_expire", "value")
    assert cache.get("quick_expire") == "value"
    
    # Set with providers TTL (1 hour)
    cache.set("providers_test", "value")
    assert cache.get("providers_test") == "value"


def test_cache_info():
    """Test cache info retrieval"""
    cache = ProviderCache()
    cache.set("test_key", "test_value")
    
    info = cache.get_cache_info()
    assert "test_key" in info
    assert "age_seconds" in info["test_key"]
    assert "expires_in_seconds" in info["test_key"]
    assert "ttl" in info["test_key"]