# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from cachetools import TTLCache


class StackCache:
    """堆栈缓存

    使用运行内存作为高速缓存，可有效提高并发的处理能力

    """

    def __init__(self, maxsize: float = 0xff, ttl: float = 60):

        self._cache: TTLCache = TTLCache(maxsize, ttl)

    def has(self, key: str) -> bool:

        return key in self._cache

    def get(self, key: str, default: typing.Any = None) -> typing.Any:

        return self._cache.get(key, default)

    def set(self, key: str, val: typing.Any):

        self._cache[key] = val

    def incr(self, key: str, val: float = 1) -> float:

        res = self.get(key, 0) + val

        self.set(key, res)

        return res

    def decr(self, key: str, val: float = 1) -> float:

        res = self.get(key, 0) - val

        self.set(key, res)

        return res

    def delete(self, key: str):

        del self._cache[key]

    def size(self) -> int:

        return len(self._cache)

    def clear(self):

        return self._cache.clear()
