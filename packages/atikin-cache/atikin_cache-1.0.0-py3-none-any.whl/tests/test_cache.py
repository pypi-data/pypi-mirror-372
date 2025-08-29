import unittest
import time
import threading
from src.cache import AtikinCache

class TestAtikinCache(unittest.TestCase):
    
    def setUp(self):
        self.cache = AtikinCache(maxsize=3, default_ttl=1)
    
    def test_basic_set_get(self):
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.get('key1'), 'value1')
    
    def test_expiration(self):
        self.cache.set('key1', 'value1', ttl=0.1)  # 100ms TTL
        time.sleep(0.2)
        self.assertIsNone(self.cache.get('key1'))
    
    def test_lru_eviction(self):
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        self.cache.set('key3', 'value3')
        self.cache.set('key4', 'value4')  # Should evict key1
        
        self.assertIsNone(self.cache.get('key1'))
        self.assertEqual(self.cache.get('key2'), 'value2')
        self.assertEqual(self.cache.get('key3'), 'value3')
        self.assertEqual(self.cache.get('key4'), 'value4')
    
    def test_lru_order_preserved(self):
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        self.cache.get('key1')  # key1 should now be most recently used
        
        self.cache.set('key3', 'value3')
        self.cache.set('key4', 'value4')  # Should evict key2, not key1
        
        self.assertIsNone(self.cache.get('key2'))
        self.assertEqual(self.cache.get('key1'), 'value1')
    
    def test_delete(self):
        self.cache.set('key1', 'value1')
        self.assertTrue(self.cache.delete('key1'))
        self.assertFalse(self.cache.delete('nonexistent'))
        self.assertIsNone(self.cache.get('key1'))
    
    def test_clear(self):
        self.cache.set('key1', 'value1')
        self.cache.set('key2', 'value2')
        self.cache.clear()
        self.assertEqual(self.cache.size(), 0)
    
    def test_exists(self):
        self.cache.set('key1', 'value1', ttl=0.1)
        self.assertTrue(self.cache.exists('key1'))
        time.sleep(0.2)
        self.assertFalse(self.cache.exists('key1'))
    
    def test_ttl(self):
        self.cache.set('key1', 'value1', ttl=1)
        ttl = self.cache.ttl('key1')
        self.assertGreater(ttl, 0.8)
        self.assertLessEqual(ttl, 1.0)
    
    def test_thread_safety(self):
        results = []
        
        def worker(thread_id):
            for i in range(100):
                key = f'key{thread_id}_{i}'
                self.cache.set(key, f'value{thread_id}_{i}')
                results.append(self.cache.get(key) is not None)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # All operations should have been successful
        self.assertTrue(all(results))
    
    def test_size(self):
        self.assertEqual(self.cache.size(), 0)
        self.cache.set('key1', 'value1')
        self.assertEqual(self.cache.size(), 1)
        self.cache.set('key2', 'value2')
        self.assertEqual(self.cache.size(), 2)
        
        # Test expiration reduces size
        self.cache.set('key3', 'value3', ttl=0.1)
        time.sleep(0.2)
        self.assertEqual(self.cache.size(), 2)

if __name__ == '__main__':
    unittest.main()