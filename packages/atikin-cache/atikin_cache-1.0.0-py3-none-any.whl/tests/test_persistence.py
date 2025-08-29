import unittest
import os
import tempfile
from src.cache import AtikinCache

class TestPersistence(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = os.path.join(self.temp_dir.name, 'test_cache.dat')
    
    def tearDown(self):
        self.temp_dir.cleanup()
    
    def test_persistence_save_load(self):
        # Create cache with persistence
        cache1 = AtikinCache(persist_path=self.test_file)
        cache1.set('key1', 'value1')
        cache1.set('key2', 'value2', ttl=3600)
        cache1.save_to_disk()
        
        # Create new cache and load from disk
        cache2 = AtikinCache(persist_path=self.test_file)
        cache2.load_from_disk()
        
        self.assertEqual(cache2.get('key1'), 'value1')
        self.assertEqual(cache2.get('key2'), 'value2')
    
    def test_persistence_auto_load(self):
        # Create and populate cache
        cache1 = AtikinCache(persist_path=self.test_file)
        cache1.set('key1', 'value1')
        cache1.set('key2', 'value2')
        cache1.save_to_disk()
        
        # New cache should auto-load on creation
        cache2 = AtikinCache(persist_path=self.test_file)
        self.assertEqual(cache2.get('key1'), 'value1')
        self.assertEqual(cache2.get('key2'), 'value2')
    
    def test_persistence_no_file(self):
        # Should not fail when loading non-existent file
        cache = AtikinCache(persist_path='/non/existent/path.dat')
        self.assertFalse(cache.load_from_disk())
        self.assertEqual(cache.size(), 0)

if __name__ == '__main__':
    unittest.main()