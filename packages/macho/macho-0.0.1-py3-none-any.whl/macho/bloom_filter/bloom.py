# --------------- Imports ---------------

import math
import mmh3

from macho.logging import get_logger

from bitarray import bitarray
from typing import Any
from threading import RLock

# --------------- Logging Setup ---------------

logger = get_logger(__name__)

# --------------- Bloom Filter Mechanism ---------------

class BloomFilter(object):
    """
    A thread-safe Bloom Filter implementation.

    Bloom Filter is a memory-efficient, probabilistic data structure that efficiently checks
    is a given member/value is part of a set.
    The Filter might produce False Positives, but can NOT produce False Negatives.

    ----- Parameters -----
    Items_count: int
        Estimated number of items/values to store within the Bloom Filter.
    Probability: float
        Desired false positive probability rate (must be between 0.0 - 1.0).

    ----- Notes -----
    - False Positives are possible, but not False Negatives.
    - Thread-safe. 
    """

    __slots__ = ("probability", "lock", "size", "hash_count", "bit_array")

    def __init__(self, items_count, probability):
        self.probability = probability
        self.lock = RLock()
        self.size = self.get_size(items_count, probability)
        self.hash_count = self.get_hash_count(self.size, items_count)
        self.bit_array = bitarray(self.size)
        self.bit_array.setall(0)

    def add(self, item: Any) -> None:
        """
        Add the desired item/value to the Bloom Filter.

        ----- Parameters -----
        Item: Any
            The item/value to add to the filter. MUST be convertible to string.

        ----- Return -----
        None
        """
        with self.lock:
            logger.debug(f"Adding item: {item} to Bloom filter")
            for i in range(self.hash_count):
                digest = self._hash(item, i) % self.size

                self.bit_array[digest] = True

    def check(self, item: Any) -> bool:
        """
        Check is the item/value possibly is present in the Bloom Filter.

        ----- Parameters -----
        Item: Any
            The item/value to check if exists in Filter. MUST be convertible to string.

        ----- Return -----
        Bool:
            True - If the item/value is possibly present (Could be False Positive).
            False - If the item/value is definitely NOT present in Filter.
        """
        with self.lock:
            for i in range(self.hash_count):
                digest = self._hash(item, i) % self.size
                if not self.bit_array[digest]:
                    return False
            logger.debug(f"Check hit (Possible False Positive) for item: {item}")
            return True
    
    def _hash(self, item: Any, seed: Any) -> int:
        """
        Generates a hashed-value for the item/value using a hash seed.

        ---- Parameters -----
        Item: Any
            The item/value to be hashed 
        Seed: Any
            The seed value for the hash function.

        ----- Return -----
        Int:
            The finalized hash-value.
        """
        return mmh3.hash(item, seed)

    @staticmethod
    def get_size(n, p):
        """
        Calculates the size of a bit array given an expected number of entries and
        a False Positive probability rate.

        ----- Parameters -----
        N: int
            Expected number of entries to be stored.
        P: float
            Desired False Positivity rate.

        ----- Return -----
        Int:
            Finalized size of the bit array.
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
    
    @staticmethod
    def get_hash_count(m, n):
        """
        Calculates the number of hash functions to use for Filter storage.

        ----- Parameters -----
        M: int
            Size of the bit array
        N: int
            Expected number of entries to sstore in Filter.

        ----- Return -----
        Int:
            Number of hash functions to use. 
        """
        k = (m/n) * math.log(2)
        return int(k)
