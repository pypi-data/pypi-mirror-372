# --------------- Imports ---------------

from typing import List, Union, Any, Optional, Dict

from macho.models import BaseCache
from macho.utility import create_cache, hash_value
from macho.bloom_filter import BloomFilter
from macho.logging import get_logger

# --------------- Logger Setup ---------------

logger = get_logger(__name__)

# --------------- Main Application ---------------

class Cache():
    """
    A shared in-memory optional Bloom filter support and configurable Eviction Strategies.

    The Cache-class supports time-based expiration, sharding, probabilistic item/value existence
    checks by use of Bloom Filter. Ideal for high-performance caching scenarios wherein memory
    and eviction strategy matters.
    
    ----- Parameters -----
    max_cache_size: int
        Maximum number of items/values that can be stored across shard (Defaults to 100).
    ttl: float
        Time-to-live for each cache entry, portrayed in seconds (Defaults to 600.0).
    shard_count: int
        The number of shards the caching system shares (Defaults to 1).
    strategy: str
        The strategy used to evict/delete expired cache entries (Defaults to 'lru').
    bloom: bool
        Activates the addition of a Bloom Filter for probabilistic membership checking (Defaults to False).
    probability: float
        The probability that the Bloom Filter produces a false positive
        (Bloom Filter must be active to function, and value must be between 0.0 - 1.0). 
        Defaults to 0.0.

    ----- Exceptions -----
    TypeError:
        Raised if the different variables do not match the desired data types.
    ValueError:
        Raised if numerical data types are outside their desired range.
    """
    __slots__ = ("max_cache_size", "ttl", "shard_count", "strategy", "bloom", "probability", "bloom_filter", "cache")

    def __init__(
            self, 
            max_cache_size: int = 100,
            ttl: float = 600.0,
            shard_count: int = 1,
            strategy: str = "lru",
            bloom: bool = False,
            probability: float = 0.5
        ):

        if not isinstance(max_cache_size, int):
            raise TypeError("Parameter 'max_cache_size' must be of type: int")
        if not isinstance(ttl, float):
            raise TypeError("Parameter 'ttl' must be of type: float")
        if not isinstance(shard_count, int):
            raise TypeError("Parameter 'shard_count' must be of type: int")
        if not shard_count > 0:
            raise ValueError("Shard count value must be positive")
        if not isinstance(strategy, str):
            raise TypeError("Parameter 'strategy' must be of type: str")
        if not isinstance(bloom, bool):
            raise TypeError("Parameter 'bloom' must be of type: bool")
        if not isinstance(probability, float):
            raise TypeError("Parameter 'probability' must be of type: float")
        if not 0.00 < probability < 1.00:
            raise ValueError("Probability value must be between 0.00 - 1.00")

        self.max_cache_size = max_cache_size
        self.ttl = ttl
        self.shard_count = shard_count
        self.strategy = strategy
        self.bloom = bloom
        self.probability = probability

        if self.bloom and self.shard_count > 1:
            shard_sizes = self._get_shard_size()
            self.bloom_filter = [BloomFilter(size, self.probability) for size in shard_sizes]
        elif self.bloom and self.shard_count == 1:
            self.bloom_filter = BloomFilter(self.max_cache_size, self.probability)
        else:
            self.bloom_filter = None

        self.cache = self._create_caches()

        logger.info(f"Cache object {repr(self)} successfully initialized")

    def add(self, key: Any, entry: Any) -> None:
        """
        Adds new key-value pair to the current cache.

        If sharding is enabled, the key is allocated to the correct shard based on it's hashed value.
        If Bloom filter is enabled, the key is stored in the filter's bit arry for future existence checks.

        ----- Parameters -----
        key: Any
            The identifying key for the cache entry.
        value: Any
            The item/value stored under the associated key.
        """
        if self.shard_count > 1:
            num = hash_value(key, self.shard_count)
            if self.bloom_filter:
                self.bloom_filter[num].add(key)
            self.cache[num].add(key=key, value=entry)
        else:
            if self.bloom_filter:
                self.bloom_filter.add(key)
            self.cache.add(key=key, value=entry)
        logger.debug(f"Cache entry: {entry} with key: {key} added to cache.")

    def get(self, key: Any) -> Optional[Any]:
        """
        Retrieves the value associated with the given key from the caching system.

        If sharding is enabled, the item/value gets retrieved from the appropriate shard.
        If Bloom Filter is enabled, the caching system initially checks for its existence in the BloomFilter
        bitarry, before making unnecceasry calls.

        ----- Parameters -----
        key: Any
            The key-value associated with the given object.

        ----- Return -----
        Optional[Any]
            The value associated with the object or None if not found or expired.

        ----- Exceptions -----
        BloomFilterException
            Raised if the Bloom Filter determines that the key is not present in the cache.
        """
        if self.shard_count > 1:
            num = hash_value(key, self.shard_count)
            if self.bloom_filter and not self.bloom_filter[num].check(key):
                logger.debug(f"Bloom filter indicates that {key} is not present in shard {num}")
                return None
            return self.cache[num].get(key)
        else:
            if self.bloom_filter and not self.bloom_filter.check(key):
                logger.debug(f"Bloom filter indicates that {key} is not present in cache")
                return None
            logger.debug(f"Cache entry {key} successfully retreived")
            return self.cache.get(key)
        
    def clear(self) -> None:
        if isinstance(self.cache, list):
            for shard in self.cache:
                shard.clear()
        else:
            self.cache.clear()
        logger.info("Cache successfully cleared!")

    def _get_shard_size(self) -> List[int]:
        base = self.max_cache_size // self.shard_count
        remainder = self.max_cache_size % self.shard_count
        shards = []

        for i in range(self.shard_count):
            size = base + (1 if i < remainder else 0)
            shards.append(size)

        return shards
    
    def _create_caches(self) -> Union[BaseCache, List[BaseCache]]:
        if self.shard_count == 1:
            shard_size = None
        else:
            shard_size = self._get_shard_size()
        
        return create_cache(
            max_capacity=self.max_cache_size,
            ttl=self.ttl,
            shards=self.shard_count,
            policy=self.strategy,
            shards_capacity=shard_size
        )
    
    @property
    def current_size(self):
        if isinstance(self.cache, list):
            return sum([shard.current_size for shard in self.cache])
        else:
            return self.cache.current_size
    
    @property
    def total_requests(self):
        if isinstance(self.cache, list):
            return sum([shard.total_requests for shard in self.cache])
        else:
            return self.cache.total_requests
    
    @property
    def latencies(self):
        if isinstance(self.cache, list):
            return [shard.latencies for shard in self.cache]
        else:
            return self.cache.latencies
    
    @property
    def metric_lifespan(self):
        if isinstance(self.cache, list):
            return [shard.metric_lifespan for shard in self.cache]
        else:
            return self.cache.metric_lifespan
    
    @property
    def metrics(self): 
        if isinstance(self.cache, list):
            return [shard.metrics for shard in self.cache]
        else:
            return self.cache.metrics
        
    def get_metrics(self):
        return {
            "max_cache_size": self.max_cache_size,
            "current_size": self.current_size,
            "ttl": self.ttl,
            "shard_count": self.shard_count,
            "bloom": self.bloom,
            "probability": self.probability
        }
    
    def __len__(self):
        return self.current_size
    
    def __contains__(self, key: Any) -> bool:
        return self.get(key) is not None
    
    def __getitem__(self, key: Any) -> Any:
        value = self.get(key)
        if value is None:
            raise KeyError(f"{key} not found!")
        return value

    def __repr__(self):
        return (f"<Cache(size={self.max_cache_size}, ttl={self.ttl}, eviction strategy={self.strategy})>")