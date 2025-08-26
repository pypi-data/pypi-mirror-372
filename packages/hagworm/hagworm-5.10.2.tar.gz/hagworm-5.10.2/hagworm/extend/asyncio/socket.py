# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import time
import typing
import signal
import socket
import asyncio
import base64
import msgpack

from ...extend.asyncio.base import Utils, install_uvloop
from ...extend.interface import RunnableInterface


DEFAULT_LIMIT = 0xffffff
DEFAULT_UNIX_SOCKET_ENDPOINT = r'/tmp/unix_socket_endpoint'


async def recv_msg(reader: 'asyncio.streams.StreamReader', timeout: typing.Optional[float] = None) -> typing.Any:

    result = None

    with Utils.suppress(asyncio.TimeoutError):

        data = await asyncio.wait_for(reader.readline(), timeout)

        if data:
            result = msgpack.loads(
                base64.b64decode(data)
            )

    return result


async def send_msg(writer: 'asyncio.streams.StreamWriter', data: typing.Any):

    writer.writelines(
        [
            base64.b64encode(
                msgpack.dumps(data)
            ),
            b'\n',
        ]
    )

    await writer.drain()


class UnixSocketServer:

    def __init__(self, client_connected_cb: typing.Callable, path: str, limit: int = DEFAULT_LIMIT):

        self._client_connected_cb: typing.Callable = client_connected_cb

        self._path: str = path
        self._limit: int = limit

        self._server: typing.Optional[asyncio.AbstractServer] = None

    async def open(self):

        if os.path.exists(self._path):
            os.remove(self._path)

        self._server = await asyncio.start_unix_server(
            self._client_connected_cb, self._path, limit=self._limit
        )

        await self._server.start_serving()

    async def close(self):

        if self._server is not None:
            self._server.close()
            self._server = None


class UnixSocketClient:

    def __init__(self, path: str, limit: int = DEFAULT_LIMIT):

        self._path: str = path
        self._limit: int = limit

        self._reader: typing.Optional['asyncio.streams.StreamReader'] = None
        self._writer: typing.Optional['asyncio.streams.StreamWriter'] = None

    @property
    def reader(self) -> 'asyncio.streams.StreamReader':
        return self._reader

    @property
    def writer(self) -> 'asyncio.streams.StreamWriter':
        return self._writer

    async def open(self):

        self._reader, self._writer = await asyncio.open_unix_connection(
            self._path,
            limit=self._limit
        )

    async def close(self):

        self._reader = None

        if self._writer is not None:
            self._writer.close()
            await self._writer.wait_closed()
            self._writer = None

    async def recv_msg(self, timeout: float = None) -> typing.Any:
        return await recv_msg(self._reader, timeout)

    async def send_msg(self, data: typing.Any):
        await send_msg(self._writer, data)


class SocketConfig(typing.NamedTuple):
    client_connected_cb: typing.Callable
    address: typing.Any
    family: int
    backlog: typing.Optional[int]
    reuse_port: bool
    buffer_limit: int


class AsyncTcpServer(RunnableInterface):

    def __init__(
            self, client_connected_cb: typing.Callable, address: typing.Any, *,
            family: int = socket.AF_INET, backlog: typing.Optional[int] = None,
            reuse_port: bool = True, buffer_limit: int = DEFAULT_LIMIT,
            on_startup: typing.Callable = None, on_shutdown: typing.Callable = None
    ):

        self._listeners: typing.List[SocketConfig] = [
            SocketConfig(
                client_connected_cb, address,
                family, backlog, reuse_port, buffer_limit
            )
        ]

        self._on_startup: typing.Callable = on_startup
        self._on_shutdown: typing.Callable = on_shutdown

        self._servers: typing.List[asyncio.AbstractServer] = []

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    async def __aenter__(self):

        for server in self._servers:
            await server.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, _traceback):

        for server in self._servers:
            await server.__aexit__(exc_type, exc_value, _traceback)

    def add_listener(
            self, client_connected_cb: typing.Callable, address: typing.Any, *,
            family: int = socket.AF_INET, backlog: typing.Optional[int] = None,
            reuse_port: bool = True, buffer_limit: int = DEFAULT_LIMIT,
    ):

        self._listeners.append(
            SocketConfig(
                client_connected_cb, address,
                family, backlog, reuse_port, buffer_limit
            )
        )

    def run(self, *, debug=None):

        Utils.print_slogan()

        install_uvloop()

        asyncio.run(self._run(), debug=debug)

    async def _run(self):

        if self._on_startup is not None:
            await self._on_startup()

        for config in self._listeners:

            if config.family == socket.AF_UNIX:

                _socket_server = await asyncio.start_unix_server(
                    config.client_connected_cb, config.address, limit=config.buffer_limit
                )

                Utils.log.success(f'unix server [pid:{Utils.getpid()}] startup complete: {config.address}')

            else:

                _socket = socket.create_server(
                    config.address, family=config.family, backlog=config.backlog, reuse_port=config.reuse_port
                )

                _socket_server = await asyncio.start_server(
                    config.client_connected_cb,
                    limit=config.buffer_limit, sock=_socket
                )

                Utils.log.success(f'socket server [pid:{Utils.getpid()}] startup complete: {config.address}')

            self._servers.append(_socket_server)

        async with self:
            await asyncio.gather(*(_server.wait_closed() for _server in self._servers))

        if self._on_shutdown is not None:
            await self._on_shutdown()

    def _exit(self, *_):

        for _server in self._servers:
            _server.close()


class RobustConnection:

    def __init__(
            self, host: typing.Optional[str] = None, port: typing.Optional[str] = None, *,
            limit: int = DEFAULT_LIMIT, recycle: int = 86400, **kwargs
    ):

        self._host: typing.Optional[str] = host
        self._port: typing.Optional[int] = port
        self._limit: int = limit
        self._recycle: int = recycle
        self._setting: typing.Dict[str, typing.Any] = kwargs

        self._recycle_time: int = 0

        self._reader: typing.Optional[asyncio.StreamReader] = None
        self._writer: typing.Optional[asyncio.StreamWriter] = None

    @property
    def reader(self) -> asyncio.StreamReader:
        return self._reader

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._writer

    async def _check_recycle(self):

        if self._writer is not None and self._recycle_time > time.time():
            self._refresh_recycle_time()
        else:
            raise Exception(f'connection exceeds maximum idle time: {self._host}:{self._port}')

    def _refresh_recycle_time(self):
        self._recycle_time = int(time.time()) + self._recycle

    async def open(self):

        try:

            self._reader, self._writer = await asyncio.open_connection(
                self._host, self._port, limit=self._limit, **self._setting
            )

            self._refresh_recycle_time()

        except Exception as err:

            Utils.log.error(str(err))

    async def close(self):

        if self._writer is not None:

            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception as err:
                Utils.log.error(str(err))

            self._recycle_time = 0

            self._reader = None
            self._writer = None

    async def reset(self):

        await self.close()
        await self.open()

    async def readline(self) -> bytes:

        try:
            await self._check_recycle()
            return await self._reader.readline()
        except Exception as err:
            await self.reset()
            raise err


    # noinspection SpellCheckingInspection
    async def readuntil(self, separator: bytes = b'\n') -> bytes:

        try:
            await self._check_recycle()
            return await self._reader.readuntil(separator)
        except Exception as err:
            await self.reset()
            raise err

    async def read(self, n: int = -1):

        try:
            await self._check_recycle()
            return await self._reader.read(n)
        except Exception as err:
            await self.reset()
            raise err

    async def write(self, data: bytes):

        try:
            await self._check_recycle()
            self._writer.write(data)
            await self._writer.drain()
        except Exception as err:
            await self.reset()
            raise err

    async def writelines(self, data: typing.Iterable[bytes]):

        try:
            await self._check_recycle()
            self._writer.writelines(data)
            await self._writer.drain()
        except Exception as err:
            await self.reset()
            raise err
