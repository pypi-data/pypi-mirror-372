# --------------- Imports ---------------

import unittest
import time

from src.macho.models import RandomCache
from src.macho.errors import MetricsLifespanException

# --------------- Test RandomCache ---------------

class TestRandomCache(unittest.TestCase):

    def test_randomcache_initialization(self):
        cache = RandomCache(5, 10.0)
        cache.add("a", 1)
        cache.add("b", 3)
        cache.add("c", 5)

        self.assertEqual(cache.max_cache_size, 5)
        self.assertEqual(cache.ttl, 10.0)
        self.assertEqual(cache.current_size, 3)

    def test_randomgcache_get(self):
        cache = RandomCache(1, 5.0)
        cache.add("a", 1)

        self.assertEqual(cache.get("a"), 1)

    def test_randomcache_expiration_purge(self):
        cache = RandomCache(5, 2.0)
        cache.add("a", 1)
        cache.add("b", 1)
        cache.add("c", 1)
        time.sleep(2.0)
        cache.add("d", 1)
        cache.add("e", 1)

        self.assertEqual(cache.current_size, 2)

    def test_randomcache_eviction(self):
        cache = RandomCache(3, 2.0)
        cache.add("a", 1)
        cache.add("b", 2)
        cache.add("c", 3)
        cache.add("d", 4)
        cache.add("e", 5)

        self.assertEqual(cache.current_size, 3)
        
    def test_randomcache_clear(self):
        cache = RandomCache(1, 2.0)
        cache.add("a", 1)

        cache.clear()

        self.assertEqual(cache.current_size, 0)

    def test_randomcache_lifespan_metrics(self):
        cache = RandomCache(1, 1.0)

        with self.assertRaises(MetricsLifespanException):
            _ = cache.metric_lifespan

    def test_randomcache_hits_and_misses(self):
        cache = RandomCache(1, 1.0)
        cache.add("a", 1)
        test1 = cache.get("a")
        test2 = cache.get("a")
        test3 = cache.get("b")

        self.assertEqual(cache.hits, 2)
        self.assertEqual(cache.misses, 1)
        self.assertEqual(cache.total_requests, 3)
        self.assertAlmostEqual(cache.hit_ratio, 2/3, places=2)