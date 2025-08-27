# --------------- Imports ---------------

import unittest
import time

from src.macho.models import CacheEntry

# --------------- Test CacheEntry ---------------

class TestCacheEntry(unittest.TestCase):
    
    def test_initialization(self):
        ttl = 2.0
        value = "test"
        entry = CacheEntry(value, ttl)

        self.assertEqual(entry.value, value)
        self.assertAlmostEqual(entry.expiry - entry.creation, ttl, places=2)
        self.assertEqual(entry.creation, entry.last_access_time)
        self.assertFalse(entry.is_expired())
    
    def test_lifespan_increases(self):
        entry = CacheEntry("test", 1.0)
        first_time = entry.lifespan()
        time.sleep(1.0)
        last_time = entry.lifespan()
        self.assertGreater(last_time, first_time)

    def test_entry_expiration(self):
        ttl = 1.0
        entry = CacheEntry("test", ttl)
        self.assertFalse(entry.is_expired())
        time.sleep(ttl + 1.0)
        self.assertTrue(entry.is_expired())

if __name__ == "__main__":
    unittest.main()