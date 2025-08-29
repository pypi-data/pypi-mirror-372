import pickle
import json
import threading
from typing import Any, Optional, Dict

class PersistenceManager:
    """Manages persistent storage for the cache."""
    
    def __init__(self, filepath: str, format: str = 'pickle'):
        """
        Initialize the persistence manager.
        
        Args:
            filepath: Path to the persistence file
            format: Serialization format ('pickle' or 'json')
        """
        self.filepath = filepath
        self.format = format
        self._lock = threading.RLock()
    
    def save(self, data: Dict[str, Any]) -> bool:
        """
        Save data to disk.
        
        Args:
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._lock:
                with open(self.filepath, 'wb' if self.format == 'pickle' else 'w') as f:
                    if self.format == 'pickle':
                        pickle.dump(data, f)
                    else:
                        json.dump(data, f, default=str)  # str for non-serializable types
                return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load data from disk.
        
        Returns:
            Loaded data or None if failed
        """
        try:
            with self._lock:
                with open(self.filepath, 'rb' if self.format == 'pickle' else 'r') as f:
                    if self.format == 'pickle':
                        return pickle.load(f)
                    else:
                        return json.load(f)
        except (FileNotFoundError, EOFError, json.JSONDecodeError) as e:
            print(f"Load error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected load error: {e}")
            return None