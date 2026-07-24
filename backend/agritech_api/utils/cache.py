import time
import functools
import asyncio
from typing import Dict, Tuple, Any

class TTLCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Any:
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.default_ttl:
                return data
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: Any) -> None:
        self._cache[key] = (time.time(), data)

    def clear() -> None:
        self._cache.clear()

global_cache = TTLCache(default_ttl_seconds=300)

def async_ttl_cache(ttl_seconds: int = 300):
    def decorator(func):
        cache = TTLCache(default_ttl_seconds=ttl_seconds)
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__module__}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_res = cache.get(key)
            if cached_res is not None:
                return cached_res
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator
