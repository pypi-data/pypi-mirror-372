from utility_pack.vector_storage_helper import ShardedLmdbStorage
from collections import OrderedDict
import pickle, atexit, xxhash, os

def _hash(key):
    return xxhash.xxh64(key).intdigest()

class VectorCache:
    def __init__(self, path='vector_cache', num_shards=5, max_size=1000000):
        self.path = path
        self.storage = ShardedLmdbStorage(path, num_shards)
        self.max_size = max_size
        self.lru_path = os.path.join(path, 'lru_meta.pkl')
        self.lru = self._load_lru()
        atexit.register(self._save_lru)

    def _load_lru(self):
        if os.path.exists(self.lru_path):
            try:
                with open(self.lru_path, 'rb') as f:
                    return pickle.load(f)
            except Exception:
                pass
        return OrderedDict()

    def _save_lru(self):
        try:
            with open(self.lru_path, 'wb') as f:
                pickle.dump(self.lru, f)
        except Exception:
            pass

    def _evict_if_needed(self):
        overflow = len(self.lru) - self.max_size
        if overflow <= 0:
            return
        ids_to_remove = []
        for _ in range(overflow):
            hid, _ = self.lru.popitem(last=False)
            ids_to_remove.append(hid)
        self.storage.delete_data(ids_to_remove)

    def is_cached(self, key):
        hid = _hash(key)
        exists = len(self.storage.get_vectors([hid])) > 0
        if exists:
            self.lru.pop(hid, None)
            self.lru[hid] = None
        return exists

    def put(self, key, value):
        hid = _hash(key)
        self.lru.pop(hid, None)
        self.lru[hid] = None
        self.storage.store_vectors([value], [hid])
        self._evict_if_needed()

    def get(self, key):
        hid = _hash(key)
        if not self.is_cached(key):
            return None
        return self.storage.get_vectors([hid])[0]
