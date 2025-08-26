# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import signal
import socket
import asyncio

import grpc
import msgpack

from abc import abstractmethod
from pydantic import BaseModel

# noinspection PyProtectedMember
from pydantic._internal._model_construction import ModelMetaclass

from ...extend.trace import trace_wrapper
from ...extend.asyncio.base import Utils


UNARY_UNARY_MODE = grpc.unary_unary_rpc_method_handler
UNARY_STREAM_MODE = grpc.unary_stream_rpc_method_handler
STREAM_UNARY_MODE = grpc.stream_unary_rpc_method_handler
STREAM_STREAM_MODE = grpc.stream_stream_rpc_method_handler

GRPC_MODE_TYPE = typing.Union[
    typing.Type[UNARY_UNARY_MODE],
    typing.Type[UNARY_STREAM_MODE],
    typing.Type[STREAM_UNARY_MODE],
    typing.Type[STREAM_STREAM_MODE]
]


class StreamHandler:

    def __init__(
            self, request: typing.AsyncIterator, context: grpc.aio.ServicerContext,
            *, metadata_model: typing.Optional[ModelMetaclass] = None
    ):

        self._request: typing.AsyncIterator = request
        self._context: grpc.aio.ServicerContext = context

        self._context.add_done_callback(self.on_close)

        self._metadata: typing.Dict[str, str] = dict(self._context.invocation_metadata())
        self._metadata_model: typing.Optional[BaseModel] = metadata_model(**self._metadata) if metadata_model is not None else None

        self._remote_peer: str = self._metadata.get(r'remote-peer', context.peer())

    async def join(self, *, timeout: float = 0) -> typing.Any:

        await self.on_connect()

        if timeout > 0:

            while True:
                try:
                    _message = await asyncio.wait_for(anext(self._request), timeout=timeout)
                    await self.on_message(_message)
                except StopAsyncIteration:
                    break
                except asyncio.TimeoutError:
                    await self._context.abort(grpc.StatusCode.CANCELLED, details=f'remote timeout: {self._remote_peer}')

        else:

            async for _message in self._request:
                await self.on_message(_message)

        Utils.log.info(f'grpc remote done writing: {self._remote_peer}')

    def metadata(self) -> typing.Dict[str, str]:
        return self._metadata

    def metadata_model(self) -> BaseModel:
        return self._metadata_model

    @property
    def peer(self) -> str:
        return self._remote_peer

    async def close(self):

        if not self._context.done():
            await self._context.abort(grpc.StatusCode.CANCELLED, details=f'manual close: {self._remote_peer}')

    async def read(self) -> typing.Any:

        data = await self._context.read()

        if data is grpc.aio.EOF:
            Utils.log.info(f'grpc remote done writing: {self._remote_peer}')

        return data

    async def write(self, message: typing.Any):

        if not self._context.done():
            await self._context.write(message)
        else:
            Utils.log.warning(f'grpc stream write cancelled: {message}')

    @abstractmethod
    async def on_message(self, message: typing.Any):
        """
        接收消息回调
        """

    @abstractmethod
    async def on_connect(self):
        """
        与客户端通信连接成功后回调
        """

    @abstractmethod
    def on_close(self, context: grpc.aio.ServicerContext):
        """
        会话关闭回调
        """


class RouterFunction(typing.NamedTuple):
    alias: str
    func: typing.Callable
    mode: GRPC_MODE_TYPE
    request_deserializer: typing.Optional[typing.Callable]
    response_serializer: typing.Optional[typing.Callable]


class Router:

    def __init__(self, service: str):

        self._service: str = service
        self._handlers: typing.Dict[str, RouterFunction] = {}

    @property
    def service(self) -> str:
        return self._service

    @property
    def handlers(self) -> typing.List[RouterFunction]:
        return list(self._handlers.values())

    @staticmethod
    def _get_func_wraps(func: typing.Callable) -> typing.Callable:

        annotations = typing.get_type_hints(func)

        for model in annotations.values():
            if issubclass(model, BaseModel):
                break
        else:
            return func

        @Utils.func_wraps(func)
        async def _func(request, context):
            return await func(model(**request), context)

        return _func

    def register(
            self, func: typing.Callable, mode: GRPC_MODE_TYPE, alias: str = None,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ) -> typing.Callable:

        if alias is None:
            alias = func.__name__

        if alias in self._handlers:
            raise KeyError(f'{alias} has exists')

        self._handlers[alias] = RouterFunction(alias, func, mode, request_deserializer, response_serializer)

        return func

    def unary_unary(
            self, *args,
            alias: str = None,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ) -> typing.Callable:

        if len(args) == 1 and callable(args[0]):
            return self.register(self._get_func_wraps(args[0]), UNARY_UNARY_MODE)

        def _wrapper(func: typing.Callable):
            return self.register(
                self._get_func_wraps(func), UNARY_UNARY_MODE,
                alias, request_deserializer, response_serializer
            )

        return _wrapper

    def unary_stream(
            self, *args,
            alias: str = None,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ) -> typing.Callable:

        if len(args) == 1 and callable(args[0]):
            return self.register(self._get_func_wraps(args[0]), UNARY_STREAM_MODE)

        def _wrapper(func: typing.Callable):
            return self.register(
                self._get_func_wraps(func), UNARY_STREAM_MODE,
                alias, request_deserializer, response_serializer
            )

        return _wrapper

    def stream_unary(
            self, *args,
            alias: str = None,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ) -> typing.Callable:

        if len(args) == 1 and callable(args[0]):
            return self.register(args[0], STREAM_UNARY_MODE)

        def _wrapper(func: typing.Callable):
            return self.register(
                func, STREAM_UNARY_MODE,
                alias, request_deserializer, response_serializer
            )

        return _wrapper

    def stream_stream(
            self, *args,
            alias: str = None,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ) -> typing.Callable:

        if len(args) == 1 and callable(args[0]):
            return self.register(args[0], STREAM_STREAM_MODE)

        def _wrapper(func: typing.Callable):
            return self.register(
                func, STREAM_STREAM_MODE,
                alias, request_deserializer, response_serializer
            )

        return _wrapper


class GRPCServer:

    def __init__(
            self,
            interceptors: typing.Optional[typing.Sequence[typing.Any]] = None,
            options: typing.Optional[grpc.aio.ChannelArgumentType] = None,
            maximum_concurrent_rpcs: typing.Optional[int] = None,
            compression: typing.Optional[grpc.Compression] = None,
            request_deserializer: typing.Optional[typing.Callable] = msgpack.loads,
            response_serializer: typing.Optional[typing.Callable] = msgpack.dumps
    ):

        self._server: grpc.aio.Server = grpc.aio.server(
            interceptors=interceptors,
            options=options,
            maximum_concurrent_rpcs=maximum_concurrent_rpcs,
            compression=compression
        )

        self._request_deserializer: typing.Optional[typing.Callable] = request_deserializer
        self._response_serializer: typing.Optional[typing.Callable] = response_serializer

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    def _exit(self, *_):
        Utils.call_soon(self.stop)

    @property
    def server(self) -> grpc.aio.Server:

        return self._server

    def register(
            self, service: str,
            handlers: typing.Union[typing.List[typing.Callable], typing.Dict[str, typing.Callable]],
            *, mode: GRPC_MODE_TYPE = UNARY_UNARY_MODE,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ):

        if request_deserializer is Ellipsis:
            request_deserializer = self._request_deserializer

        if response_serializer is Ellipsis:
            response_serializer = self._response_serializer

        _handlers = []

        if isinstance(handlers, list):
            _handlers.extend((_func.__name__, _func) for _func in handlers)
        elif isinstance(handlers, dict):
            _handlers.extend((_alias, _func) for _alias, _func in handlers.items())
        else:
            raise TypeError()

        generic_handler = grpc.method_handlers_generic_handler(
            service,
            {
                _alias: mode(
                    trace_wrapper(_func),
                    request_deserializer=request_deserializer,
                    response_serializer=response_serializer,
                )
                for _alias, _func in _handlers
            }
        )

        self._server.add_generic_rpc_handlers([generic_handler])

    def bind_router(
            self, router: Router,
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ):

        if request_deserializer is Ellipsis:
            request_deserializer = self._request_deserializer

        if response_serializer is Ellipsis:
            response_serializer = self._response_serializer

        generic_handler = grpc.method_handlers_generic_handler(
            router.service,
            {
                _handler.alias: _handler.mode(
                    trace_wrapper(_handler.func),
                    request_deserializer = request_deserializer if _handler.request_deserializer is Ellipsis else _handler.request_deserializer,
                    response_serializer = response_serializer if _handler.response_serializer is Ellipsis else _handler.response_serializer,
                )
                for _handler in router.handlers
            }
        )

        self._server.add_generic_rpc_handlers([generic_handler])

    def bind_routers(
            self, routers: typing.List[Router],
            request_deserializer: typing.Optional[typing.Callable] = ...,
            response_serializer: typing.Optional[typing.Callable] = ...
    ):

        if request_deserializer is Ellipsis:
            request_deserializer = self._request_deserializer

        if response_serializer is Ellipsis:
            response_serializer = self._response_serializer

        generic_handlers = []

        for router in routers:
            generic_handlers.append(
                grpc.method_handlers_generic_handler(
                    router.service,
                    {
                        _handler.alias: _handler.mode(
                            trace_wrapper(_handler.func),
                            request_deserializer = request_deserializer if _handler.request_deserializer is Ellipsis else _handler.request_deserializer,
                            response_serializer = response_serializer if _handler.response_serializer is Ellipsis else _handler.response_serializer,
                        )
                        for _handler in router.handlers
                    }
                )
            )

        self._server.add_generic_rpc_handlers(generic_handlers)

    async def start(
            self,
            address: typing.Union[str, typing.Tuple[str, int]],
            *,
            family: int = socket.AF_INET,
            server_credentials: typing.Optional[grpc.ServerCredentials] = None,
            enable_ping: bool = False
    ):

        if family == socket.AF_INET:
            _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _address = f'{address[0]}:{address[1]}'
        elif family == socket.AF_INET6:
            _socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            _address = f'[{address[0]}]:{address[1]}'
        elif family == socket.AF_UNIX:
            _socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            _address = f'unix:{address}'
        else:
            raise ValueError(r'family invalid')

        try:
            _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
        except OSError as err:
            _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            Utils.log.warning(r'socket SO_REUSEPORT not supported')

        _socket.bind(address)

        if server_credentials is None:
            self._server.add_insecure_port(_address)
        else:
            self._server.add_secure_port(_address, server_credentials)

        if enable_ping is True:
            self._server.add_generic_rpc_handlers(
                [
                    grpc.method_handlers_generic_handler(
                        r'_',
                        {
                            r'ping': UNARY_UNARY_MODE(lambda request, context: str(Utils.getpid()).encode())
                        }
                    )
                ]
            )

        await self._server.start()

        Utils.log.success(f'grpc server [pid:{Utils.getpid()}] startup completed: {address}')

    async def stop(self, grace: typing.Optional[float] = None):
        await self._server.stop(grace)

    async def wait(self, timeout: typing.Optional[float] = None):
        return await self._server.wait_for_termination(timeout)
