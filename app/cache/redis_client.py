"""app/cache/redis_client.py — Redis Client with In-Memory fallback."""

import json
import time
from typing import Optional, Any
from app.config import settings

try:
    import redis
    _redis_client = redis.from_url(settings.REDIS_URL, socket_timeout=2)
    _redis_client.ping()
    _HAS_REDIS = True
except Exception:
    _HAS_REDIS = False


class CacheManager:
    def __init__(self):
        self.has_redis = _HAS_REDIS
        self._memory = {}

    def get(self, key: str) -> Optional[Any]:
        if self.has_redis:
            try:
                val = _redis_client.get(key)
                return json.loads(val) if val else None
            except Exception:
                pass
        if key in self._memory:
            data, expiry = self._memory[key]
            if time.time() < expiry:
                return json.loads(data)
            del self._memory[key]
        return None

    def set(self, key: str, value: Any, ttl: int = settings.CACHE_DEFAULT_TTL_SECONDS):
        val_json = json.dumps(value, default=str)
        if self.has_redis:
            try:
                _redis_client.setex(key, ttl, val_json)
                return
            except Exception:
                pass
        self._memory[key] = (val_json, time.time() + ttl)

    def delete(self, key: str):
        if self.has_redis:
            try:
                _redis_client.delete(key)
            except Exception:
                pass
        self._memory.pop(key, None)

    @property
    def status(self) -> str:
        return "Redis Container ⚡" if self.has_redis else "In-Memory Fallback 🧠"


cache = CacheManager()