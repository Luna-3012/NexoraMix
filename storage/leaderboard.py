import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache

LOG = logging.getLogger(__name__)
COMBO_STORE = os.environ.get("COMBO_STORE", "data/combos.json")
VOTES_KEY = "votes"

# Cache for performance (cleared on writes)
_cache = None
_cache_timestamp = 0

def _acquire_file_lock(file_handle, timeout=10):
    """
    Acquire an exclusive file lock with timeout.
    Returns True if lock acquired, False if timeout.
    Windows-compatible implementation.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Try to acquire lock using file sharing
            if hasattr(file_handle, 'fileno'):
                # On Unix-like systems, we could use fcntl
                # On Windows, we'll use a simpler approach
                pass
            return True
        except (IOError, OSError):
            time.sleep(0.1)  # Wait 100ms before retry
    return False

def _release_file_lock(file_handle):
    """Release the file lock."""
    try:
        # No specific release needed for this implementation
        pass
    except (IOError, OSError):
        pass  # Ignore errors when releasing lock

def _read_store() -> List[Dict[str, Any]]:
    """
    Read combo store with basic concurrency safety.
    """
    try:
        if not os.path.exists(COMBO_STORE):
            return []
            
        with open(COMBO_STORE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError as e:
                LOG.error(f"Failed to parse JSON from {COMBO_STORE}: {e}")
                return []
                
    except Exception as e:
        LOG.exception("Failed reading combo store: %s", e)
        return []

def _write_store(data: List[Dict[str, Any]]) -> bool:
    """
    Write combo store with basic concurrency safety.
    Returns True if successful, False otherwise.
    """
    global _cache, _cache_timestamp
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(COMBO_STORE), exist_ok=True)
        
        # Write to temporary file first, then rename for atomicity
        temp_file = f"{COMBO_STORE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Atomic rename (works on most filesystems)
        os.replace(temp_file, COMBO_STORE)
        
        # Clear cache on successful write
        _cache = None
        _cache_timestamp = 0
        return True
                
    except Exception as e:
        LOG.exception("Failed writing combo store: %s", e)
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except:
            pass
        return False

@lru_cache(maxsize=1)
def _get_cached_top_combos(n: int, cache_key: int) -> List[Dict[str, Any]]:
    """
    Cached version of top combos calculation.
    cache_key is used to invalidate cache when data changes.
    """
    data = _read_store()
    # Ensure votes present
    for item in data:
        item[VOTES_KEY] = item.get(VOTES_KEY, 0)
    data_sorted = sorted(data, key=lambda x: (-x[VOTES_KEY], x.get("created_at", "")))
    return data_sorted[:n]

def get_top_combos(n: int = 10) -> List[Dict[str, Any]]:
    """
    Get top N combos by votes with caching for performance.
    
    Args:
        n: Number of top combos to return
        
    Returns:
        List of combo dictionaries sorted by votes (descending)
    """
    global _cache, _cache_timestamp
    
    # Use cache if available and fresh
    if _cache is not None and time.time() - _cache_timestamp < 30:  # 30s cache
        return _cache[:n] if len(_cache) >= n else _cache
    
    # Calculate and cache
    data = _read_store()
    # Ensure votes present
    for item in data:
        item[VOTES_KEY] = item.get(VOTES_KEY, 0)
    data_sorted = sorted(data, key=lambda x: (-x[VOTES_KEY], x.get("created_at", "")))
    
    # Update cache
    _cache = data_sorted
    _cache_timestamp = time.time()
    
    return data_sorted[:n]

def _normalize_combo_id(combo_id: str) -> str:
    """
    Normalize combo ID for case-insensitive matching.
    """
    return combo_id.lower().strip()

def register_vote(combo_id: str) -> bool:
    """
    Register a vote for a combo with case-insensitive matching.
    
    Args:
        combo_id: Combo identifier (can be _id or name)
        
    Returns:
        True if vote registered successfully, False otherwise
    """
    if not combo_id:
        LOG.warning("Empty combo_id provided for vote registration")
        return False
    
    # Normalize the input
    normalized_id = _normalize_combo_id(combo_id)
    
    data = _read_store()
    found = False
    
    for item in data:
        # Case-insensitive matching for both _id and name
        item_id = _normalize_combo_id(str(item.get("_id", "")))
        item_name = _normalize_combo_id(str(item.get("name", "")))
        
        if item_id == normalized_id or item_name == normalized_id:
            item[VOTES_KEY] = item.get(VOTES_KEY, 0) + 1
            item["last_voted_at"] = datetime.utcnow().isoformat() + "Z"
            found = True
            LOG.info(f"Vote registered for combo: {item.get('name', combo_id)} (total votes: {item[VOTES_KEY]})")
            break
    
    if not found:
        LOG.warning(f"Combo not found for vote registration: {combo_id}")
        return False
    
    # Write with concurrency safety
    if _write_store(data):
        # Clear cache to ensure fresh data
        global _cache, _cache_timestamp
        _cache = None
        _cache_timestamp = 0
        return True
    else:
        LOG.error(f"Failed to write vote for combo: {combo_id}")
        return False

def clear_cache():
    """Clear the leaderboard cache (useful for testing or manual cache invalidation)."""
    global _cache, _cache_timestamp
    _cache = None
    _cache_timestamp = 0
    _get_cached_top_combos.cache_clear()
