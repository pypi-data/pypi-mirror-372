# 📦 Macho - Memory Adept Caching Operations

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI - 0.1.0](https://img.shields.io/badge/PyPI-coming--soon-yellow)](https://pypi.org/)

---

## 🤔 What is Macho?

Macho is a lightweight, high-performance in-memory caching library designed with customizability at its core. Unlike heavyweight distributed caching systems (Redis & Memcached), Macho is entirely self-contained, running directly in your local Python environment without any external dependencies.
Macho enables Python developers to define and fine-tune how their cache behaves, offering powerful and flexible control over evictions, storage and general data life-cycle - all within a compact and memory-efficient infrastructure.

## 🧠 Core Philosophy

Configuration first, Complexity never!
Macho was intentionally constructed for Python developers that desire full control over their caching operations without the overhead of an external server or complex deployment.

## ❓ Why use Macho Caching?

Macho currently aims to fill the gaps between built-in Python caching solutions and full-scale caching servers by offering:
* ✅ **In-memory speed** without any external server requirements.
* 🔧 **Full user configuration** over cache behavior and functionality.
* 🧩 **Modular design** for extensibility and experimentation
* 🐍 **Pure Python implementation**, great for prototyping or lightweight production services.

## 🛠️ Key Features

* ⚡ **Bloom Filter Support**: Probabilistically reduce costly cache lookups and improve performance.
* 🔀 **Sharding**: Partition your cache into independent shards for better concurrency.
* 🔃 **Custom Eviction Strategies**: Currently supports **LRU**, **FIFO** and **Random** (More coming soon).
* ⏳ **Time-to-live (TTL)**: Configure per-cache expiration with automatic clean-up.
* 📊 **Metrics & Data**: Collect cache usage metrics and data for optimization and analysis.

---

## </> Installation
Utilise your preferred package management system to add Macho:

```python
# Pip 
pip install macho
# Conda
conda install macho
# Poetry
poetry add macho
```

## ✅ Initialise caching
Macho utilises a primary Cache-class as the main point of operations and caching.

```python
# ---------- Imports ----------

from macho import Cache         # Main cache-class

# ---------- Create Class ----------

macho_cache = Cache(
    max_cache_size=100,         # Maximum items/entries stores across shards (Default: 100)
    ttl=600.0,                  # Time-to-live for each item/entry (Default: 600.0)
    shard_count=1,              # Number of caching shards shared by the system (Default: 1)
    strategy="lru",             # Eviction policy for deleting data entries (Default: 'lru')
    bloom=True                  # Activate the probabilistic Bloom filter (Default: False)
    probability=0.5             # False positive rate for Bloom Filter (Default: 0.5)
)

# Add items/entries to the Cache
for index in range(5):
    macho_cache.add(f"{index}_key", f"{index}_value")   # Requires key: Any, value: Any

# Get items/entries from the Cache
macho_cache.get(key="1_key")    # Returns 1_value
macho_cache.get(key="2_key")    # Returns 2_value
macho_cache.get(key="6_key")    # Returns None (Key doesn't represent a stored value)

# Clear all items/entries from the current Cache
macho_cache.clear()             # Deletes ALL currently stored items/entries
```

## ❌ Eviction Policies
Currently Macho supports 3 primary eviction policies to handle item/entry deletion behind the scene:
* **LRU (Last Recently Used)** - Evicts/deletes entries that haven't been accessed recently. This is generally useful when recent data is more likely to be re-used.
* **FIFO (First in, First out)** - Evicts/deletes entries in the original order they were added. Treats the cache as a queue, removing the oldest entries first.
* **Random** - Evicts/deletes entries at random. Preferable in scenarios where uniform eviction is acceptable or desired.

```python
from macho import Cache

# LRU policy
LRU_cache = Cache(
    strategy="lru"
)
# FIFO policy
LRU_cache = Cache(
    strategy="fifo"
)
# Random policy
LRU_cache = Cache(
    strategy="random"
)
# Raises ValueError
Error_cache = Cache(
    strategy="something"
)
```

## ♦ Balance cache with Sharding
Sharding separates the original cache into lesser, independent segments distributing entries across them evenly. This feature dramatically improves cache scalability and retention, enabling faster access and better memory usage across large workloads. Enable this feature by specifying the number of distributed shards:

```python
from macho import Cache

# Instantiate the Cache-object
sharded_cache = Cache(
    max_cache_size=100,         # Each shard holds 20 independent entries.
    shard_count=5               # Parameter value MUST be 1 or above. Other will raise error
)
```

**WARNING: Over-sharding (Too many shards vs. actual entries) can severely impact performance and memory efficiency. It's important to balance shard count with the  workload and available resources.** 

## 💯 Bloom Filter Support
Use a probabilistic, memory-efficient data structure behind-the-scenes to quickly determine whether a desired item/entry is *100%* not in the current cache. Utilising this feature helps avoid unnecessary lookups, significantly improving cache hit rates and reducing overall latency. 
Additionally, users can specify the desired rate of False Positives that the Bloom Filter provides by using the 'probability'-parameter exposed in the main 'Cache'-class.

```python
from macho import Cache

# Instantiate the Cache-object
bloom_cache = Cache(
    max_cache_size=50,
    ttl=200.0,
    strategy="lru",
    bloom=True,                 # Enables the use of Bloom Filter for quick lookups
    probability=0.5             # Determines the probability of a False Positive
)

bloom_cache.add("random_key", "Charizard")
bloom_cache.get("not_present")  # Quicker lookup than ordinary cache lookup
```

**NOTE: Bloom Filters generally improve cache performance by trading a small amount of accuracy for speed. They provide quick key membership checks but may return a false positive, this makes them ideal for read-heavy workloads**

## 💡 Cache Metrics & Data Properties
To determine the most efficient optimization strategy, Macho's Cache-class provides several key metrics and data properties:

```python
from macho import Cache

# Instantiate the Cache-object
data_cache = Cache(
    max_cache_size=10,
    ttl=5.0,
    shard_count=2,
    strategy="fifo",
    bloom=False
)

data_cache.current_size         # Returns the current number of stored items across shards.
data_cache.total_requests       # Returns the number of total get() and add() calls made.
data_cache.latencies            # Returns a dictionary representing method-call latency.
data_cache.metric_lifespan      # Returns a dictionary representing individual entry lifespans
data_cache.metrics              # Returns a dictionary filled with general cache information.
```

## 🖥️ Streamlit UI 
To better help individual developers identify potential bottlenecks and/or configuration issues, Macho offers a pre-built data visualisation tool built with Streamlit, designed to provide deeper insight into cache behaviour. These specific performance metrics (e.g., hit ratio, eviction count, memory usage) help fine-tune, optimise and debug your caching system.
Simply pass a 'Cache'-class object into the 'launch_dashboard' function provided by Macho to run the dashboard from a Python subprocess:

```python
from macho import Cache, launch_dashboard

# Instantiate the Cache-object
dashboard_cache = Cache(
    max_cache_size=10,
    ttl=5.0,
    shard_count=2,
    strategy="fifo",
    bloom=False
)

launch_dashboard(dashboard_cache)       # This function launches the Streamlit dashboard 
```

## 🔮 The Future of Macho
Here is a current roadmap for future versions:
* 🔁 Additional probabilistic data structures (e.g., **XOR-filter**, **Cuckoo-filter**).
* 📈 New eviction policies (**LFU**, **MFU**)
* 🧰 CLI tooling for cache inspection and management.
* 📊 Advanced metrics and performance analysis.
* 🖥️ Improved Streamlit-based UI dashboard for data visualisation. 

## 📚 Reading Material
To learn more about the core mechanisms that power Macho, here are some essential resources:
- [Bloom Filter](https://brilliant.org/wiki/bloom-filter/)
- [Sharding](https://en.wikipedia.org/wiki/Shard_(database_architecture))
- [Eviction Policy](https://www.geeksforgeeks.org/system-design/cache-eviction-policies-system-design/)

## 🤝 Contribution
Macho is open to contributions from the Python community! If you'd like to report a bug, request features, or possibly contribute code, please feel free to open an issue or submit a pull request!

## 📄 Licensing
The project is licensed under the MIT License.