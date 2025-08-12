from __future__ import annotations
import time
from threading import RLock
from typing import Any, Callable, Optional


class SimpleTTLCache:
    def __init__(self, default_ttl_seconds: int = 300):
        self._data: dict[str, tuple[float, Any]] = {}
        self._lock = RLock()
        self._default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            expires_at, value = entry
            if expires_at < now:
                # Expired
                self._data.pop(key, None)
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        with self._lock:
            self._data[key] = (time.time() + ttl, value)

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl_seconds: Optional[int] = None) -> Any:
        value = self.get(key)
        if value is not None:
            return value
        value = factory()
        self.set(key, value, ttl_seconds)
        return value

    def invalidate(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


