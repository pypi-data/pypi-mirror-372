# --------------- Imports ---------------

import unittest
import time

from src.macho.models import FIFOCache
from src.macho.errors import MetricsLifespanException

# --------------- Test FIFOCache ---------------

class TestFIFOCache(unittest.TestCase):

    def test_initialization(self):
        cache = FIFOCache(5, 10.0)
        cache.add("a", 1)
        cache.add("b", 3)
        cache.add("c", 5)

        self.assertEqual(cache.max_cache_size, 5)
        self.assertEqual(cache.ttl, 10.0)
        self.assertEqual(cache.current_size, 3)

    def test_cache_get(self):
        cache = FIFOCache(5, 5.0)
        cache.add("a", 1)
        cache.add("b", 3)
        cache.add("c", 4)

        self.assertEqual(cache.get("b"), 3)

    def test_fifocache_expiration_purge(self):
        cache = FIFOCache(10, 5.0)
        cache.add("a", 1)
        cache.add("b", 1)
        cache.add("c", 1)
        time.sleep(5.0)
        cache.add("d", 1)
        cache.add("e", 1)

        self.assertEqual(cache.current_size, 2)

    def test_fifiocache_eviction(self):
        cache = FIFOCache(3, 10.0)
        cache.add("a", 1)
        cache.add("b", 1)
        cache.add("c", 1)
        cache.add("d", 1)
        cache.add("e", 1)

        self.assertIn("c", cache)
        self.assertIn("d", cache)
        self.assertIn("e", cache)
        self.assertNotIn("a", cache)
        self.assertNotIn("b", cache)

    def test_fifocache_clear(self):
        cache = FIFOCache(1, 1.0)
        cache.add("a", 1)
        cache.clear()

        self.assertEqual(cache.current_size, 0)

    def test_fifiocache_lifespan_metrics(self):
        cache = FIFOCache(1, 1.0)

        with self.assertRaises(MetricsLifespanException):
            _ = cache.metric_lifespan

    def test_fifocache_hits_and_misses(self):
        cache = FIFOCache(1, 1.0)
        cache.add("a", 1)
        test1 = cache.get("a")
        test2 = cache.get("a")
        test3 = cache.get("b")

        self.assertEqual(cache.hits, 2)
        self.assertEqual(cache.misses, 1)
        self.assertEqual(cache.total_requests, 3)
        self.assertAlmostEqual(cache.hit_ratio, 2/3, places=2)

if __name__ == "__main__":
    unittest.main()