import time
from utils.caching import SimpleCache


def test_simple_cache():
    cache = SimpleCache(default_ttl=10, max_size=3)

    cache.set("ns", "k1", "v1")
    assert cache.get("ns", "k1") == "v1"
    assert cache.get("ns", "nonexistent") is None

    # Expiration test with 0 TTL
    cache.set("ns", "k2", "v2", ttl=-1)
    assert cache.get("ns", "k2") is None

    # Clear test
    cache.set("ns1", "a", 1)
    cache.set("ns2", "b", 2)
    cache.clear("ns1")
    assert cache.get("ns1", "a") is None
    assert cache.get("ns2", "b") == 2
