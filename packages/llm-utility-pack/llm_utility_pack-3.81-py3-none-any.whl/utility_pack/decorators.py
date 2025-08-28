import time, threading, os, cloudpickle, inspect, asyncio, hashlib
from collections import OrderedDict
from functools import wraps
from PIL.Image import Image as PillowImage

def make_hashable(obj):
    """Recursively convert mutable objects to hashable types, including Pillow images with content hash."""
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(e) for e in obj)
    if isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    if isinstance(obj, set):
        return tuple(sorted(make_hashable(e) for e in obj))
    if isinstance(obj, PillowImage):
        # Compute SHA-256 hash of the raw image data
        img_bytes = obj.tobytes()
        img_hash = hashlib.sha256(img_bytes).hexdigest()
        return ("PIL_Image", obj.mode, obj.size, img_hash)
    return obj

def timed_lru_cache(max_size: int, minutes: float):
    """
    A decorator that caches function results (sync or async) up to a maximum
    size and discards them after a specified number of minutes.

    Args:
        max_size (int): Maximum number of items to cache.
        minutes (float): Time in minutes after which cached items expire.

    Returns:
        Decorator function.
    """
    def decorator(func):
        cache = OrderedDict()
        expiration_time = minutes * 60  # Convert minutes to seconds
        is_async = inspect.iscoroutinefunction(func)

        def _clear_expired():
            """Helper to remove expired items from cache."""
            current_time = time.time()
            # Iterate over a copy of keys to allow modification during iteration
            for k in list(cache.keys()):
                cached_time, _ = cache[k]
                if current_time - cached_time > expiration_time:
                    # Use pop with default None to handle potential race conditions gracefully
                    # although the primary access should be guarded by the wrapper's logic
                    cache.pop(k, None)
                else:
                    # Since OrderedDict keeps insertion order, once we hit a
                    # non-expired item, the rest are also likely non-expired
                    # (unless move_to_end changed order significantly relative to expiry)
                    # A full check is safer but slightly less performant.
                    # Let's stick to the original logic for performance.
                    break

        def _update_cache(key, result):
             """Helper to update cache and enforce size limit."""
             current_time = time.time()
             cache[key] = (current_time, result)
             cache.move_to_end(key) # Mark as recently used

             # Enforce max size
             if len(cache) > max_size:
                 cache.popitem(last=False) # Remove the oldest item

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            _clear_expired()

            if key in cache:
                cache.move_to_end(key)
                _, result = cache[key]
                return result

            result = func(*args, **kwargs)
            _update_cache(key, result)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))
            _clear_expired()

            if key in cache:
                cache.move_to_end(key)
                _, result = cache[key]
                return result

            # Await the async function
            result = await func(*args, **kwargs)
            _update_cache(key, result)
            return result

        # Return the appropriate wrapper based on the function type
        return async_wrapper if is_async else sync_wrapper
    return decorator

class DiskLRUCache:
    """
    A thread-safe LRU cache that stores values on disk using cloudpickle.

    Note: File I/O operations (_load_cache, _save_cache) are synchronous
    and will block the event loop when used within an async function via
    the disk_lru_cache decorator. For high-performance async applications,
    consider using an async file I/O library (like aiofiles).
    """
    def __init__(self, max_size: int, cache_file: str):
        """
        Initialize the disk-based LRU cache.

        Args:
            max_size (int): Maximum number of items to cache.
            cache_file (str): Path to the file where the cache is stored.
        """
        if max_size <= 0:
             raise ValueError("max_size must be a positive integer")
        self.max_size = max_size
        self.cache_file = cache_file
        # Ensure cache directory exists
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir and not os.path.exists(cache_dir):
             os.makedirs(cache_dir, exist_ok=True)
        self.lock = threading.Lock()
        self.cache = self._load_cache()
        self._enforce_max_size()

    def _load_cache(self):
        """Load the cache from disk if the file exists."""
        # No lock needed here as it's called only during __init__
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    loaded_cache = cloudpickle.load(f)
                    if isinstance(loaded_cache, OrderedDict):
                        return loaded_cache
                    else:
                         # Handle case where file contains unexpected data
                         print(f"Warning: Cache file '{self.cache_file}' contained unexpected data type. Initializing empty cache.")
                         return OrderedDict()
            except (EOFError, cloudpickle.UnpicklingError, ValueError, TypeError) as e:
                # Handle corrupted or empty file
                print(f"Warning: Could not load cache from '{self.cache_file}' due to error: {e}. Initializing empty cache.")
                return OrderedDict()
            except Exception as e:
                # Catch other potential file reading errors
                print(f"Warning: An unexpected error occurred while loading cache from '{self.cache_file}': {e}. Initializing empty cache.")
                return OrderedDict()
        return OrderedDict()

    def _save_cache(self):
        """Save the cache to disk. Assumes lock is already held."""
        # This is a synchronous blocking I/O operation.
        temp_file = self.cache_file + ".tmp"
        try:
            with open(temp_file, 'wb') as f:
                cloudpickle.dump(self.cache, f)
            # Atomic rename (on most POSIX systems and Windows)
            os.replace(temp_file, self.cache_file)
        except Exception as e:
            print(f"Error saving cache to '{self.cache_file}': {e}")
            # Attempt to remove temporary file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError as remove_err:
                    print(f"Error removing temporary cache file '{temp_file}': {remove_err}")

    def _enforce_max_size(self):
        """Remove oldest items if cache exceeds max_size. Assumes lock is held."""
        while len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get(self, key):
        """Retrieve a value from the cache."""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)  # Mark as recently used
                return self.cache[key]
            return None # Explicitly return None for cache miss

    def put(self, key, value):
        """Add or update a value in the cache."""
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)  # Mark as recently used
            self._enforce_max_size() # Enforce size limit *before* saving
            self._save_cache()  # Persist changes to disk (blocking I/O)

    def clear(self):
        """Remove all items from the cache and delete the cache file."""
        with self.lock:
            self.cache.clear()
            try:
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)
            except OSError as e:
                print(f"Error removing cache file '{self.cache_file}': {e}")

def disk_lru_cache(max_size: int, cache_file: str):
    """
    A decorator that caches function results (sync or async) to disk using
    an LRU policy.

    Note: Uses synchronous file I/O, which will block the asyncio event loop.

    Args:
        max_size (int): Maximum number of items to cache.
        cache_file (str): Path to the file where the cache is stored.

    Returns:
        Decorator function.
    """
    try:
        cache = DiskLRUCache(max_size, cache_file)
    except ValueError as e:
         # Propagate invalid max_size error clearly
         raise ValueError(f"Failed to initialize disk_lru_cache: {e}") from e

    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Convert arguments to a hashable form
            key = (make_hashable(args), make_hashable(kwargs))

            # Check if the result is already cached
            result = cache.get(key)
            if result is not None: # Check explicitly for None cache miss
                return result

            # Compute the result if not cached
            result = func(*args, **kwargs)

            # Add the result to the cache
            cache.put(key, result)

            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Convert arguments to a hashable form
            key = (make_hashable(args), make_hashable(kwargs))

            # Check if the result is already cached (blocking I/O potential here in get)
            result = cache.get(key)
            if result is not None: # Check explicitly for None cache miss
                return result

            # Compute the result if not cached
            result = await func(*args, **kwargs) # Await the async function

            # Add the result to the cache (blocking I/O potential here in put)
            cache.put(key, result)

            return result

        # Return the appropriate wrapper
        return async_wrapper if is_async else sync_wrapper
    return decorator

def retry(retry_count: int, delay: float):
    """
    A decorator that retries a function (sync or async) when it
    raises an exception. Uses asyncio.sleep for async functions.

    Args:
        retry_count (int): Maximum number of retry attempts (total calls = 1 + retry_count).
        delay (float): Time (in seconds) to wait between retries.

    Returns:
        Decorator function.
    """
    if retry_count < 0:
        raise ValueError("retry_count must be non-negative")
    if delay < 0:
        raise ValueError("delay must be non-negative")

    def decorator(func):
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            # Total attempts = initial call + retry_count
            for attempt in range(retry_count + 1):
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_count:
                        print(f"Attempt {attempt + 1} failed for {func.__name__} with error: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay) # Blocking sleep for sync functions
                    else:
                        print(f"Function {func.__name__} failed after {retry_count + 1} attempts.")
                        # Re-raise the last captured exception
                        raise last_exception

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            # Total attempts = initial call + retry_count
            for attempt in range(retry_count + 1):
                try:
                    # Attempt to execute and await the async function
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < retry_count:
                        print(f"Attempt {attempt + 1} failed for {func.__name__} with error: {e}. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay) # Non-blocking sleep for async functions
                    else:
                        print(f"Function {func.__name__} failed after {retry_count + 1} attempts.")
                        # Re-raise the last captured exception
                        raise last_exception

        # Return the appropriate wrapper
        return async_wrapper if is_async else sync_wrapper
    return decorator

def custom_lru_cache(max_size: int = 100):
    """
    A decorator that caches function results (sync or async) up to a maximum
    size using an LRU (Least Recently Used) policy.

    Args:
        max_size (int): Maximum number of items to cache.

    Returns:
        Decorator function.
    """
    def decorator(func):
        cache = OrderedDict()
        is_async = inspect.iscoroutinefunction(func)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)
            if len(cache) > max_size:
                cache.popitem(last=False)
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))

            if key in cache:
                cache.move_to_end(key)
                return cache[key]

            result = await func(*args, **kwargs)
            cache[key] = result
            cache.move_to_end(key)
            if len(cache) > max_size:
                cache.popitem(last=False)
            return result

        return async_wrapper if is_async else sync_wrapper
    return decorator
