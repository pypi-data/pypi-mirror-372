# --------------- Imports ---------------

from typing import Any

# --------------- Custom Exceptions ---------------

class BloomFilterException(Exception):
    """
    Error raised when value not present in Bloom Filter.
    """
    def __init__(self, key: Any):
        super().__init__(f"Key: {key} is propably not present (filtered by Bloom Filter)")
        self.key = key

class ShardException(Exception):
    """
    Error raised when shard capacity values are not currently available.
    """

    def __init__(self, message: str = "Must provide 'shards_capacity' when creating shared cache"):
        super().__init__(message)

class MetricsLatencyException(Exception):
    """
    Error raised when latency data is not currently available
    """
    def __init__(self, message: str = "No data related to cache's latency is currently available"):
        super().__init__(message)

class MetricsLifespanException(Exception):
    """
    Error raised when cache's 'lifespan' list is without values.
    """
    def __init__(self, message: str = "No data related to cache's lifespan is currently available"):
        super().__init__(message)