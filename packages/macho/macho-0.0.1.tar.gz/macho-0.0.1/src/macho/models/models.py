# --------------- Imports ---------------

from threading import RLock
from typing import Any, Dict, Optional
from collections import OrderedDict, deque
from statistics import median

from macho.logging import get_logger

import time
import random
import sys

# --------------- Logger Setup ---------------

logger = get_logger(__name__)

# --------------- Entry Model ---------------

class CacheEntry():
    """
    Representing a single cache entry storing a value with an expiration time.

    ----- Parameters -----
    value: Any
        The cache value.
    ttl: float
        How long the cache entry exists, represented in seconds.
    """
    __slots__ = ("value", "expiry", "creation", "last_access_time")

    def __init__(self, value: Any, ttl: float):
        self.value = value
        self.creation = time.monotonic()
        self.expiry = self.creation + ttl
        self.last_access_time = self.creation

    def lifespan(self) -> float:
        return time.monotonic() - self.creation

    def is_expired(self) -> bool:
        return time.monotonic() > self.expiry
    
    def __repr__(self):
        return f"<CacheEntry(value={self.value}, expires_in={self.expiry - time.monotonic():.2f}s)>"
    

# --------------- Caching Models ---------------
    
class BaseCache():
    """
    The base-class all subsequent cache-class inherits from.

    ----- Parameters -----
    max_cache_size: int
        Maximum number of items/values capable of being stored in the cache.
    default_ttl: float
        Time-to-live for individual data entries stored in the cache, protrayed in seconds.
    
    ----- Exceptions -----
    MetricLifespanException
        Raised if no available lifespan data metrics when metric_lifespan() is called.
    MetricLatencyException
        Raised if no available latency data metrics when latencies() is called.
    """
    __slots__ = (
        "max_cache_size",
        "default_ttl",
        "cache",
        "lock",
        "hits",
        "misses",
        "evictions",
        "lifespan",
        "add_latency",
        "get_latency"
    )

    def __init__(self, max_cache_size: int, default_ttl: float):
        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[Any, CacheEntry] = OrderedDict()
        self.lock = RLock()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.lifespan = deque(maxlen=1000)
        self.add_latency = deque(maxlen=1000)
        self.get_latency = deque(maxlen=1000)


    def _purge_expired(self) -> None:
        """
        Iterates through current data storage and deletes expired cache entries.
        """
        for key in list(self.cache.keys()):
            if self.cache[key].is_expired():
                self.evictions += 1
                ls = self.cache[key].lifespan()
                self.lifespan.append(ls)
                del self.cache[key]
    
    def clear(self) -> None:
        """
        Deletes and resets cache-object's individual variables and data metrics.
        Utilizes RLock for Thread safesty.
        """
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
            self.evictions = 0
            self.lifespan.clear()
            self.add_latency.clear()
            self.get_latency.clear()

    def _extract_latency_data(self, data: deque, label: str) -> Dict[str, Any]:
        return {
            f"{label}_latency_seconds": sum(data) / len(data),
            f"max_{label}_latency": max(data),
            f"min_{label}_latency": min(data),
            f"{label}_latency": list(data)
        }

    @property
    def current_size(self) -> int:
        return len(self.cache)
    
    @property
    def max_size(self) -> int:
        return self.max_cache_size
    
    @property
    def ttl(self) -> int:
        return self.default_ttl
    
    @property
    def total_requests(self) -> int:
        return self.hits + self.misses
    
    @property
    def hit_ratio(self) -> float:
        total = self.hits + self.misses
        return round(self.hits / total, 2) if total else 0.00
    
    @property
    def metric_lifespan(self) -> Dict[str, float]:
        if not self.lifespan:
            return {
                "max": 0.0,
                "min": 0.0,
                "count": 0,
                "total": 0,
                "average": 0,
                "median": 0.0,
                "all_lifespans": []
            }
        
        lifespan_values = list(self.lifespan)
        total = sum(lifespan_values)
        count = len(lifespan_values)
        
        return {
            "max": max(lifespan_values),
            "min": min(lifespan_values),
            "count": count,
            "total": total,
            "average": total / count,
            "median": median(lifespan_values),
            "all_lifespans": lifespan_values
        }
    
    @property
    def memory_size(self):
        size = sys.getsizeof(self.cache)
        for k, v in self.cache.items():
            size += (sys.getsizeof(k) + sys.getsizeof(v))
        return size
    
    @property
    def latencies(self) -> Dict[str, float]:
        latencies = {}
        if self.add_latency:
            latencies.update(self._extract_latency_data(self.add_latency, "add"))
        else:
            latencies.update({
                "add_latency_seconds": 0.0,
                "max_add_latency": 0.0,
                "min_add_latency": 0.0,
                "add_latency": []
            })
        if self.get_latency:
            latencies.update(self._extract_latency_data(self.get_latency, "get"))
        else:
            latencies.update({
                "get_latency_seconds": 0.0,
                "max_get_latency": 0.0,
                "min_get_latency": 0.0,
                "get_latency": []
            })
        return latencies
        
    @property
    def metrics(self) -> Dict[str, Any]:
        metrics = {
            "current_size": self.current_size,
            "max_size": self.max_size,
            "ttl": self.ttl,
            "hits": self.hits,
            "misses": self.misses, 
            "total_requests": self.total_requests,
            "hit_ratio": self.hit_ratio,
            "evictions": self.evictions,
            "memory_size": self.memory_size,
            "lifespan_metrics": self.metric_lifespan,
            "latencies": self.latencies
        }

        return metrics
    
    def __contains__(self, key: Any) -> bool:
        with self.lock:
            entry = self.cache.get(key)
            return entry is not None and not entry.is_expired()
        
    def __len__(self) -> int:
        return self.current_size
    
    def __iter__(self):
        with self.lock:
            for key, entry in self.cache.items():
                if not entry.is_expired():
                    yield key, entry.value
        
    
class LRUCache(BaseCache):
    """
    Cache-class that utilizes LRU (Last Recently Used) eviction strategy.
    Inherits functionality and properties from BaseCache.

    ----- Parameters -----
    max_cache_size: int
        Maximum number of items/values capable of being stored in the cache.
    default_ttl: float
        Time-to-live for individual data entries stored in the cache, protrayed in seconds.
    """

    __slots__ = ()      # Initialize Slots to inherit variables from BaseCache

    def __init__(self, max_cache_size: int, default_ttl: float):
        super().__init__(max_cache_size, default_ttl)

    def add(self, key: Any, value: Any) -> None:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            self.cache.pop(key, None)

            while len(self.cache) >= self.max_cache_size:
                removed = self.cache.popitem(last=False)
                self.evictions += 1
                self.lifespan.append(removed[1].lifespan())
            self.cache[key] = CacheEntry(value, self.default_ttl)
            end_time = time.monotonic()
            self.add_latency.append(end_time - start_time)

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            entry = self.cache.get(key)

            if entry is None or entry.is_expired():
                self.cache.pop(key, None)
                self.misses += 1
                return None
            self.cache.move_to_end(key)
            self.hits += 1
            end_time = time.monotonic()
            entry.last_access_time = end_time
            self.get_latency.append(end_time - start_time)
            return entry.value
        
class FIFOCache(BaseCache):
    """
    Cache-class that utilizes FIFO (First in, First out) eviction strategy.
    Inherits functionality and properties from BaseCache.

    ----- Parameters -----
    max_cache_size: int
        Maximum number of items/values capable of being stored in the cache.
    default_ttl: float
        Time-to-live for individual data entries stored in the cache, protrayed in seconds.
    """

    __slots__ = ()      # Initialize Slots to inherit variables from BaseCache

    def __init__(self, max_cache_size: int, default_ttl: float):
        super().__init__(max_cache_size, default_ttl)

    def add(self, key: Any, value: Any) -> None:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            self.cache.pop(key, None)

            while len(self.cache) >= self.max_cache_size:
                removed = self.cache.popitem(last=False)
                self.evictions += 1
                self.lifespan.append(removed[1].lifespan())
            self.cache[key] = CacheEntry(value, self.default_ttl)
            end_time = time.monotonic()
            self.add_latency.append(end_time - start_time)

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            entry = self.cache.get(key)

            if entry is None or entry.is_expired():
                self.cache.pop(key, None)
                self.misses += 1
                return None
            self.hits += 1
            end_time = time.monotonic()
            entry.last_access_time = end_time
            self.get_latency.append(end_time - start_time)
            return entry.value

class RandomCache(BaseCache):
    """
    Cache-class that utilizes Random (Randomized entries) eviction strategy.
    Inherits functionality and properties from BaseCache.

    ----- Parameters -----
    max_cache_size: int
        Maximum number of items/values capable of being stored in the cache.
    default_ttl: float
        Time-to-live for individual data entries stored in the cache, protrayed in seconds.
    """

    __slots__ = ()      # Initialize Slots to inherit variables from BaseCache

    def __init__(self, max_cache_size: int, default_ttl: float):
        super().__init__(max_cache_size, default_ttl)

    def add(self, key: Any, value: Any) -> None:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            self.cache.pop(key, None)

            while len(self.cache) >= self.max_cache_size:
                random_key = random.choice(list(self.cache.keys()))
                removed = self.cache.pop(random_key)
                self.evictions += 1
                self.lifespan.append(removed.lifespan())
            self.cache[key] = CacheEntry(value, self.default_ttl)
            end_time = time.monotonic()
            self.add_latency.append(end_time - start_time)

    def get(self, key: Any) -> Optional[Any]:
        with self.lock:
            start_time = time.monotonic()
            self._purge_expired()

            entry = self.cache.get(key)
            
            if entry is None or entry.is_expired():
                self.cache.pop(key, None)
                self.misses += 1
                return None
            self.hits += 1
            end_time = time.monotonic()
            entry.last_access_time = end_time
            self.get_latency.append(end_time - start_time)
            return entry.value
    

    
        