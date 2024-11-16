#!/usr/bin/env python3
"""Module contains:
    - classes: Cache.
"""
from functools import wraps
import redis
from typing import Callable, TypeVar, Union
import uuid


T = TypeVar('T')


def call_history(method: Callable) -> Callable:
    """Store calls to method with its input and output.
    """
    @wraps(method)
    def wrapper(self, *args):
        """Wrapper function
        """
        data = tuple(data for data in args)
        output = method(self, *args)
        self._redis.rpush(method.__qualname__ + ":inputs", str(data))
        self._redis.rpush(method.__qualname__ + ":outputs", str(output))
        return output
    return wrapper


def count_calls(method: Callable) -> Callable:
    """Count calls to method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function.
        """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def replay(method: Callable) -> None:
    """
    """
    qualname = method.__qualname__
    instance = method.__self__
    call_count = instance._redis.get(qualname).decode("utf-8")
    inputs = [inpt.decode("utf-8") for inpt in
              instance._redis.lrange(qualname + ":inputs", 0, call_count)]
    outputs = [outpt.decode("utf-8") for outpt in
               instance._redis.lrange(qualname + ":outputs", 0, call_count)]
    print("{} was called {} times:".format(qualname, call_count))
    for i, o in zip(inputs, outputs):
        print(qualname + '(*' + i + ')' + " -> " + o)
    return None


class Cache():
    """Redis cache.
    """
    def __init__(self):
        """Instantiation method.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
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
