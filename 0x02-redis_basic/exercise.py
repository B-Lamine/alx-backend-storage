#!/usr/bin/env python3
"""Module contains:
    - classes: Cache.
"""
from functools import wraps
import redis
from typing import Callable, TypeVar, Union
import uuid


T = TypeVar('T')


def count_calls(method: Callable) -> Callable:
    """Wrapper generator.
    """
    @wraps(method)
    def wrapper(obj, *args, **kwargs):
        """Decorator function to count calls to method.
        """
        obj._redis.incrby(method.__qualname__)
        return method(obj, *args, **kwargs)
    return wrapper


class Cache():
    """Redis cache.
    """
    def __init__(self):
        """Instantiation method.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store given data using random key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Callable[[str], T] = None) -> T:
        """Get value associated with given key;
        Convert data using given function, if any.
        """
        if fn:
            return fn(self._redis.get(key))
        return self._redis.get(key)

    def get_str(key: str) -> str:
        """Get value as a string.
        """
        return self.get(key, str)

    def get_int(key: str) -> int:
        """Get value as an integer.
        """
        return self.get(key, int)
