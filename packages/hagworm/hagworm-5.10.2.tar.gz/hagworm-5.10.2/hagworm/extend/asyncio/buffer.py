# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio
import threading

from tempfile import TemporaryFile

from .base import Utils
from .task import RateLimiter

from ..interface import ContextManager


class QueueBuffer:

    def __init__(
        self, handler: typing.Callable, slice_size: int, slice_time: float,
        task_limit: int, wait_limit: int = 0, timeout: int = 60
    ):

        self._lock: threading.Lock = threading.Lock()

        self._handler: typing.Callable = handler
        self._rate_limiter: RateLimiter = RateLimiter(task_limit, wait_limit, timeout)

        self._slice_data: asyncio.Queue[typing.Any] = asyncio.Queue(wait_limit)
        self._slice_size: int = slice_size
        self._slice_time: float = slice_time

        self._consume_task: asyncio.Task = asyncio.create_task(self._do_consume_task())
        self._condition: asyncio.Condition = asyncio.Condition()

    def size(self) -> int:
        return self._slice_data.qsize()

    async def close(self):

        await self._slice_data.join()
        self._consume_task.cancel()

        await self._rate_limiter.close()

    async def _do_consume_task(self):

        while True:

            try:

                async with self._condition:

                    with Utils.suppress(asyncio.TimeoutError):
                        await asyncio.wait_for(
                            self._condition.wait(),
                            self._slice_time
                        )

                    while True:

                        slice_data = []

                        while not self._slice_data.empty() and len(slice_data) < self._slice_size:
                            slice_data.append(
                                self._slice_data.get_nowait()
                            )
                            self._slice_data.task_done()

                        if slice_data:
                            await self._rate_limiter.append(self._handler, slice_data)

                        if self._slice_data.qsize() < self._slice_size:
                            break

            except Exception as err:
                Utils.log.error(str(err))

    def safe_append(self, data: typing.Any):

        with self._lock:
            self._slice_data.put_nowait(data)

    async def append(self, data: typing.Any, timeout: typing.Union[int, float] = None):

        await asyncio.wait_for(
            self._slice_data.put(data),
            timeout
        )

        if self._slice_data.qsize() >= self._slice_size:
            if self._condition.locked():
                self._condition.notify_all()


class FileBuffer(ContextManager):
    """文件缓存类
    """

    def __init__(self, slice_size: int = 0x1000000):

        self._buffers: typing.List[TemporaryFile] = []

        self._slice_size: int = slice_size

        self._read_offset: int = 0

        self._append_buffer()

    def _context_release(self):
        self.close()

    def _append_buffer(self):
        self._buffers.append(TemporaryFile())

    def close(self):

        while len(self._buffers) > 0:
            self._buffers.pop(0).close()

        self._read_offset = 0

    def write(self, data: typing.AnyStr):

        buffer = self._buffers[-1]

        buffer.seek(0, 2)
        buffer.write(data)

        if buffer.tell() >= self._slice_size:
            buffer.flush()
            self._append_buffer()

    def read(self, size: typing.Optional[int] = None) -> typing.AnyStr:

        buffer = self._buffers[0]

        buffer.seek(self._read_offset, 0)

        result = buffer.read(size)

        if len(result) == 0 and len(self._buffers) > 1:
            self._buffers.pop(0).close()
            self._read_offset = 0
        else:
            self._read_offset = buffer.tell()

        return result
