# 📦 Atikin-Cache

> ⚡ High-performance in-memory caching library with **TTL**, **LRU eviction**, **thread-safety**, and **persistence**. Created By: Atikin Verse.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7+-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Made by Atikin Verse](https://img.shields.io/badge/made%20by-Atikin%20Verse-ff69b4.svg)](https://github.com/atikinverse)

---

## 🚀 Features

* ⏳ **Time-to-live (TTL):** Automatic expiration of cached items
* 🔄 **LRU eviction:** Least Recently Used items removed when cache is full
* 🧵 **Thread-safe:** Safe for multi-threaded applications
* 💾 **Persistence:** Save and load cache data from disk
* ⚡ **High performance:** O(1) read/write operations, minimal overhead

---

## 📥 Installation

```bash
pip install atikin-cache
```

Or install from source:

```bash
git clone https://github.com/atikinverse/atikin-cache.git
cd atikin-cache
pip install .
```

---

## 📖 Usage

### 🔹 Basic Example

```python
from atikin_cache import AtikinCache

# Create cache with max 1000 items and 5-minute default TTL
cache = AtikinCache(maxsize=1000, default_ttl=300)

# Set a value
cache.set('user:123', {'name': 'John', 'email': 'john@example.com'})

# Get a value
user = cache.get('user:123')
print(user)  # {'name': 'John', 'email': 'john@example.com'}

# Custom TTL
cache.set('temp:data', 'temporary', ttl=10)  # 10 seconds

# Check existence
if cache.exists('user:123'):
    print("User exists in cache")

# Delete key
cache.delete('user:123')

# Clear cache
cache.clear()
```

---

### 🔹 Persistent Cache

```python
# Create cache with persistence
cache = AtikinCache(persist_path='/path/to/cache.dat')

# Store data
cache.set('key', 'value')

# Save to disk
cache.save_to_disk()

# Load from disk
cache.load_from_disk()
```

---

## 🧪 Testing

Run the full test suite:

```bash
python -m unittest discover tests
```

Run the example:

```bash
python examples/basic_usage.py
```

---

## ⚡ Performance

* **O(1)** for get, set, delete operations
* Optimized for minimal locking in multi-threaded environments
* Efficient memory usage with **LRU eviction**

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🌐 Follow Us

| Platform  | Username    |
| --------- | ----------- |
| Facebook  | atikinverse |
| Instagram | atikinverse |
| LinkedIn  | atikinverse |
| Twitter/X | atikinverse |
| Threads   | atikinverse |
| Pinterest | atikinverse |
| Quora     | atikinverse |
| Reddit    | atikinverse |
| Tumblr    | atikinverse |
| Snapchat  | atikinverse |
| Skype     | atikinverse |
| GitHub    | atikinverse |

---

<div align="center">  
Made with ❤️ by <b>Atikin Verse</b> 🚀  
</div>  
