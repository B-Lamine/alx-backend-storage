#!/usr/bin/env python3
"""Module contains:
    - classes: Cache.
"""
import redis
from typing import Union
import uuid


class Cache():
    """Redis cache.
    """
    def __init__(self):
        """Instantiation method.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store given data using random key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
