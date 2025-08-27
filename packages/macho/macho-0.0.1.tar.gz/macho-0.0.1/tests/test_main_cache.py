# --------------- Imports ---------------

import unittest

from src.macho.main import Cache

# --------------- Test Main Cache ---------------

class TestMainCache(unittest.TestCase):

    def test_maincache_initialization(self):
        test_cache = Cache(
            max_cache_size=50,
            ttl=10.0,
            shard_count=2,
            strategy="lru",
            bloom=False
        )

        self.assertEqual(test_cache.max_cache_size, 50) # Checks correct max size
        self.assertEqual(test_cache.ttl, 10.0)          # Checks cache ttl
        self.assertEqual(test_cache.strategy, "lru")    # Checks cache eviction strategy
        self.assertFalse(test_cache.bloom)              # Checks Bloom creation is false
        self.assertIsNone(test_cache.bloom_filter)      # Checks Bloom filter is None
        self.assertEqual(len(test_cache.cache), 2)      # Checks that 2 caches are stored

    def test_maincache_add_and_get(self):
        test_cache = Cache(
            max_cache_size=50,
            ttl=10.0,
            shard_count=1,
            strategy="lru",
            bloom=False
        )

        test_cache.add("test1", "value1")
        result = test_cache.get("test1")

        self.assertEqual(result, "value1")

    def test_maincache_returns_none_without_bloom(self):
        test_cache = Cache(
            max_cache_size=50,
            ttl=10.0,
            shard_count=2,
            strategy="lru",
            bloom=False
        )

        result = test_cache.get("nonexistent")
        self.assertIsNone(result)

    def test_maincache_returns_none_with_bloom(self):
        test_cache = Cache(
            max_cache_size=10,
            ttl=5.0,
            shard_count=1,
            strategy="lru",
            bloom=True,
            probability=0.1
        )

        result = test_cache.get("nonexistent")
        self.assertIsNone(result)

    def test_maincache_clear(self):
        test_cache = Cache(
            max_cache_size=50,
            ttl=10.0,
            shard_count=2,
            strategy="lru",
            bloom=False
        )

        test_cache.add("pikachu", "gen1")
        result = test_cache.get("pikachu")
        self.assertEqual(result, "gen1")
        test_cache.clear()
        self.assertIsNone(test_cache.get("Mistake"))

    def test_maincache_metrics_properties_exist(self):
        test_cache = Cache(
            max_cache_size=2,
            ttl=5.0,
            shard_count=1,
            strategy="lru",
            bloom=False
        )

        test_cache.add("Metagross", "Steven")
        test_cache.add("Milotic", "Wallace")
        test_cache.add("Nosepass", "Roxanne")
        result = test_cache.get("Nosepass")
        self.assertIsInstance(test_cache.current_size, int)
        self.assertIsInstance(test_cache.total_requests, int)
        self.assertTrue(isinstance(test_cache.latencies, dict))

        lifespan = test_cache.metric_lifespan
        self.assertTrue(isinstance(lifespan, dict))
        self.assertIn("average", lifespan)
        self.assertTrue(isinstance(test_cache.metrics, list) or isinstance(test_cache.metrics, dict))

    def test_maincache_invalid_initialization(self):
        with self.assertRaises(TypeError):
            Cache(max_cache_size="100")
        with self.assertRaises(TypeError):
            Cache(ttl="10.0")
        with self.assertRaises(ValueError):
            Cache(shard_count=0)
        with self.assertRaises(TypeError):
            Cache(strategy=100)
        with self.assertRaises(ValueError):
            Cache(probability=1.5)
