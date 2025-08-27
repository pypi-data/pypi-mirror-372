# --------------- Imports ---------------

import unittest
import math

from bitarray import bitarray

from src.macho.bloom_filter import BloomFilter

# --------------- Test BloomFilter ---------------

class TestBloomFilter(unittest.TestCase):

    def test_bloomfilter_initialization(self):
        item_count = 100
        probability = 0.1

        bloom = BloomFilter(item_count, probability)
        expected_size = bloom.get_size(item_count, probability)
        expected_hash = bloom.get_hash_count(expected_size, item_count)

        self.assertEqual(bloom.size, expected_size)
        self.assertEqual(bloom.hash_count, expected_hash)
        self.assertIsInstance(bloom.bit_array, bitarray)
        self.assertEqual(bloom.bit_array.count(), 0)

    def test_bloomfilter_add_bits(self):
        item_count = 100
        probability = 0.1
        item = "to_be_hashed"

        bloom = BloomFilter(item_count, probability)
        pre_set_count = bloom.bit_array.count()

        bloom.add(item)
        post_set_count = bloom.bit_array.count()

        self.assertGreater(post_set_count, pre_set_count)

    def test_bloomfilter_returns_true_adding(self):
        item_count = 100
        probability = 0.1
        item = "test_hash"

        bloom = BloomFilter(item_count, probability)
        bloom.add(item)
        result_int_filter = bloom.check(item)
        result_not_in_filter = bloom.check("not_in_filter_test")

        self.assertTrue(result_int_filter)
        self.assertFalse(result_not_in_filter)

    def test_bloomfilter_size_creation(self):
        n = 100
        p = 0.1

        bloom = BloomFilter(n, p)
        size = bloom.get_size(n, p)
        expected_size = -(n * math.log(p)) / (math.log(2) ** 2)

        self.assertEqual(size, int(expected_size))

    def test_bloomfilter_multiple_items(self):
        item_count = 100
        probability = 0.1
        items_list = ["Gengar", "Gyarados", "Rapidash", "Mewtwo", "Golem"]
        not_present_item = "Feraligatr"

        bloom = BloomFilter(item_count, probability)
        for item in items_list:
            bloom.add(item)

        for item in items_list:
            self.assertTrue(bloom.check(item))

        result_not_in_filter = bloom.check(not_present_item)
        self.assertIn(result_not_in_filter, [True, False]) # Could be false positive

    def test_bloomfilter_multiple_hashes(self):
        item_count = 100
        probability = 0.1
        item = "deterministic"

        bloom = BloomFilter(item_count, probability)
        hashes = [bloom._hash(item, i) for i in range(bloom.hash_count)]
        again = [bloom._hash(item, i) for i in range(bloom.hash_count)]

        self.assertEqual(hashes, again)

    def test_bloomfilter_raises_math_error(self):

        with self.assertRaises(ValueError):
            BloomFilter(100, 0)

        with self.assertRaises(ValueError):
            BloomFilter(100, -0.1)