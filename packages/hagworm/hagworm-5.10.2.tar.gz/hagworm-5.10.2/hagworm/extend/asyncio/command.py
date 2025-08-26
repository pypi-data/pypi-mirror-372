# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio
import contextlib

from abc import abstractmethod

from .base import install_uvloop, Utils
from .future import WaitForever
from .socket import UnixSocketServer, UnixSocketClient, DEFAULT_LIMIT, DEFAULT_UNIX_SOCKET_ENDPOINT

from ..interface import RunnableInterface
from ..process import Daemon


class MainProcess(Daemon):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *,
            cpu_affinity: bool = False, join_timeout: int = 10,
            **kwargs
    ):

        super().__init__(
            target, sub_process_num,
            cpu_affinity=cpu_affinity, join_timeout=join_timeout,
            **kwargs
        )

    async def initialize(self):
        pass

    async def release(self):
        pass

    async def _execute(self):

        self._fill_process()

        while self._check_process():
            await Utils.sleep(1)

    def run(self):

        Utils.print_slogan()

        install_uvloop()

        loop = asyncio.get_event_loop()

        loop.run_until_complete(self.initialize())
        loop.run_until_complete(self._execute())
        loop.run_until_complete(self.release())


class SubProcess(RunnableInterface):

    @classmethod
    def create(cls, *args, **kwargs):
        cls(*args, **kwargs).run()

    def __init__(self, process_num: int, *args, **kwargs):

        self._process_id: int = Utils.getpid()
        self._process_num: int = process_num

        self._blocker: typing.Optional[WaitForever] = None

    def close(self, *_):

        if self._blocker and not self._blocker.done():
            self._blocker.cancel()

    async def initialize(self):
        pass

    async def release(self):
        pass

    async def _execute(self):

        with contextlib.suppress(asyncio.CancelledError):
            self._blocker = WaitForever()
            await self._blocker

    def run(self):

        Utils.log.success(f'Started worker process [id:{self._process_id} num:{self._process_num}]')

        install_uvloop()

        loop = asyncio.get_event_loop()

        loop.run_until_complete(self.initialize())
        loop.run_until_complete(self._execute())
        loop.run_until_complete(self.release())

        Utils.log.success(f'Stopped worker process [id:{self._process_id} num:{self._process_num}]')


class MainProcessWithIPC(MainProcess):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *,
            cpu_affinity: bool = False, join_timeout: int = 10,
            unix_socket_path: str = DEFAULT_UNIX_SOCKET_ENDPOINT, unix_socket_limit: int = DEFAULT_LIMIT,
            **kwargs
    ):

        super().__init__(
            target, sub_process_num,
            cpu_affinity=cpu_affinity, join_timeout=join_timeout,
            unix_socket_path=unix_socket_path,
            **kwargs
        )

        self._socket_server: UnixSocketServer = UnixSocketServer(
            self._client_connected_cb, unix_socket_path, unix_socket_limit
        )

    @abstractmethod
    async def _client_connected_cb(
            self,
            reader: 'asyncio.streams.StreamReader',
            writer: 'asyncio.streams.StreamWriter'
    ):
        """
        连接成功后的回调函数
        """

    async def initialize(self):
        await self._socket_server.open()

    async def release(self):
        await self._socket_server.close()


class SubProcessWithIPC(SubProcess):

    def __init__(self, process_num: int, unix_socket_path: str):

        super().__init__(process_num)

        self._socket_client: UnixSocketClient = UnixSocketClient(unix_socket_path)

    async def initialize(self):
        await self._socket_client.open()

    async def release(self):
        await self._socket_client.close()
