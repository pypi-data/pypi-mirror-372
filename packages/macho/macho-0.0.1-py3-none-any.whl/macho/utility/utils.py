# --------------- Imports ---------------

from typing import List, Optional, Union, Any, Dict

from macho.models import BaseCache, LRUCache, FIFOCache, RandomCache
from macho.errors import ShardException
from macho.logging import get_logger

import mmh3

# --------------- Logger Setup ---------------

logger = get_logger(__name__)

# --------------- Cache-list Function ---------------

cache_list = {      # List of supported Eviction Strategies and corresponding cache-classes
    "lru": LRUCache,                
    "fifo": FIFOCache,
    "random": RandomCache
}

def check_cache_list(policy: str) -> BaseCache:
    if not isinstance(policy, str):
        raise TypeError(f"The Policy parameter must be of type: Str")
    
    policy = policy.casefold()

    if policy in cache_list:
        return cache_list[policy]
    else:
        raise ValueError(f"Eviction Strategy {policy} not supported")
    

# --------------- Hash Function ---------------
    

def hash_value(key: Any, count: int) -> int:
    key_str = str(key)
    return mmh3.hash(key_str, seed=42, signed=False) % count
    
    
# --------------- Cache Creation ---------------
    
def _create_single_cache(capacity_num: int, ttl: float, policy: str) -> BaseCache:
    cache_class = check_cache_list(policy=policy)
    logger.debug(f"Single cache created with eviction policy {policy}")
    return cache_class(max_cache_size=capacity_num, default_ttl=ttl)

    
def _create_sharded_cache(ttl: float, num: int, shards_capacity: List[int], policy: str) -> List[BaseCache]:
    shards_list = []

    cache_class = check_cache_list(policy=policy)

    for n in range(num):
        cap = shards_capacity[n]                                        # Pick the capacity num from list
        new_cache = cache_class(max_cache_size=cap, default_ttl=ttl)    # Create new class instance with capacity
        shards_list.append(new_cache)                                   # Append new cache class to final list
        
    logger.debug(f"{num} Cache Shards created with eviction policy {policy}")

    return shards_list

def extract_general_info(metrics) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    if isinstance(metrics, list):
        return [extract_general_info(m) for m in metrics]
    
    return {
        "Max Cache Size": metrics.get("max_size", "N/A"),
        "Current Cache Size": metrics.get("current_size", "N/A"),
        "Time-to-live (secs)": metrics.get("ttl", "N/A"),
        "Eviction strategy": metrics.get("eviction_strategy", "N/A"),
        "Shard Count": metrics.get("shard_count", "N/A"),
        "Bloom Filter Enable": metrics.get("bloom", "N/A"),
        "False Positive Rate": (
            metrics.get("probability", "N/A")
            if metrics.get("bloom", False)
            else "N/A"
        )
    }

def create_cache(
    max_capacity: int,
    ttl: float,
    shards: int, 
    policy: str,
    shards_capacity: Optional[List[int]] = None
) -> Union[BaseCache, List[BaseCache]]:
    if shards == 1:
        return _create_single_cache(
        capacity_num=max_capacity,
        ttl=ttl,
        policy=policy
        )
    else:
        if shards_capacity is None:
            raise ShardException("Must provide 'shards_capacity' when creating shared cache")
        return _create_sharded_cache(
            ttl=ttl,
            num=shards,
            shards_capacity=shards_capacity,
            policy=policy
        )

