import base64
import json
import redis
import threading
from typing import Any, Dict, List, Optional, Union


class CacheService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, redis_url: str):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CacheService, cls).__new__(cls)
                    cls._instance.__init_instance__(redis_url)
        return cls._instance

    def __init_instance__(self, redis_url: str):
        """ Actual initialization of the singleton instance """
        self.redis_url = redis_url
        self.__connect__()

    def __connect__(self):
        """ Establishes the connection with Redis and handles connection errors """
        try:
            print(f"Connecting to Redis at {self.redis_url}...")
            self._cache = redis.Redis.from_url(self.redis_url, decode_responses=True)
            self._cache.ping()
        except redis.ConnectionError as e:
            print(f"Error de conexión a Redis: {e}")
            self._cache = None

    def _ensure_connection(self):
        """ Reconnects if necessary """
        if not self._cache or not self._cache.ping():
            print("Reconnecting to Redis...")
            self.__connect__()

    def add(
        self, key: str, row: Union[List[Any], Dict[str, Any]], expiration_time: Optional[int] = None
    ):
        assert isinstance(key, str), "Only str keys are supported!"
        assert isinstance(row, (list, dict)), "Only dict or list objects are supported!"

        self._ensure_connection()
        if not self._cache:
            print("Could not establish connection with Redis.")
            return

        raw = {
            "content": base64.b64encode(json.dumps(row).encode("ascii")).decode("ascii")
        }
        self._cache.hset(key, mapping=raw)
        if expiration_time:
            self._cache.expire(key, expiration_time)

    def get(self, key: str) -> Optional[Union[List[Any], Dict[str, Any]]]:
        assert isinstance(key, str), "Only str keys are supported!"

        self._ensure_connection()
        if not self._cache:
            print("Could not establish connection with Redis.")
            return None

        row = self._cache.hgetall(key)
        if not row:
            return None

        content = row.get("content")
        if content is None:
            return None
        return json.loads(base64.b64decode(content).decode("ascii"))

    def delete(self, key: str):
        assert isinstance(key, str), "Only str keys are supported!"

        self._ensure_connection()
        if not self._cache:
            print("Could not establish connection with Redis.")
            return

        if self._cache.exists(key):
            self._cache.delete(key)
