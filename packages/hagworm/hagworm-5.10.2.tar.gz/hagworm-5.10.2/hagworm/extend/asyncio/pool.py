# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from abc import ABCMeta, abstractmethod
from asyncio import Queue
from contextlib import asynccontextmanager

from ...extend.base import Utils


class ObjectInterface(metaclass=ABCMeta):

    @abstractmethod
    async def open(self, *args, **kwargs):
        """
        构造池元素对象
        """

    @abstractmethod
    async def close(self, *args, **kwargs):
        """
        析构池元素对象
        """


class ObjectPool(metaclass=ABCMeta):
    """对象池实现
    """

    def __init__(self, maxsize: int):

        self._queue: Queue[ObjectInterface] = Queue(maxsize=maxsize)

    @abstractmethod
    def _create(self) -> ObjectInterface:
        """
        创建池元素对象
        """

    async def open(self, *args, **kwargs):

        while not self._queue.full():
            obj = self._create()
            await obj.open(*args, **kwargs)
            self._queue.put_nowait(obj)

        Utils.log.info(f'ObjectPool {type(self)} initialized: {self._queue.qsize()}')

    async def close(self, *args, **kwargs):

        while not self._queue.empty():
            await self._queue.get_nowait().close(*args, **kwargs)

    @property
    def size(self) -> int:

        return self._queue.maxsize

    @asynccontextmanager
    async def get(self) -> ObjectInterface:

        obj = await self._queue.get()

        try:
            yield obj
        finally:
            await self._queue.put(obj)
