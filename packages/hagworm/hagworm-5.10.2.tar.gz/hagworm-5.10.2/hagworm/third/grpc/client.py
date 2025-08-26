# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio
import grpc
import msgpack

from abc import abstractmethod

from ...extend.struct import RoundRobin
from ...extend.error import catch_error


class GRPCClient:

    def __init__(
            self, *,
            credentials: typing.Optional[grpc.ChannelCredentials] = None,
            options: typing.Optional[grpc.aio.ChannelArgumentType] = None,
            compression: typing.Optional[grpc.Compression] = None,
            interceptors: typing.Optional[typing.Sequence[grpc.aio.ClientInterceptor]] = None,
            request_serializer: typing.Optional[typing.Callable] = msgpack.dumps,
            response_deserializer: typing.Optional[typing.Callable] = msgpack.loads
    ):

        self._credentials: typing.Optional[grpc.ChannelCredentials] = credentials
        self._options: typing.Optional[grpc.aio.ChannelArgumentType] = options
        self._compression: typing.Optional[grpc.Compression] = compression
        self._interceptors: typing.Optional[typing.Sequence[grpc.aio.ClientInterceptor]] = interceptors

        self._request_serializer: typing.Optional[typing.Callable] = request_serializer
        self._response_deserializer: typing.Optional[typing.Callable] = response_deserializer

        self._channels: RoundRobin[grpc.aio.Channel] = RoundRobin()

    def _make_channel(self, target: str) -> grpc.aio.Channel:

        if self._credentials is None:
            return grpc.aio.insecure_channel(
                target, self._options, self._compression, self._interceptors
            )
        else:
            return grpc.aio.secure_channel(
                target, self._credentials, self._options, self._compression, self._interceptors
            )

    def _make_channels(self, targets: typing.List[str]) -> typing.Dict[str, grpc.aio.Channel]:
        return {_target: self._make_channel(_target) for _target in set(targets)}

    async def append_target(self, target: str):

        _channel = self._channels.append(target, self._make_channel(target))

        if _channel is not None:
            await _channel.close()

    async def reset_targets(self, targets: typing.List[str]):

        _channels = self._make_channels(targets)

        for _, _channel in self._channels.reset(_channels).items():
            await _channel.close()

    async def clear_targets(self, keys: typing.Optional[typing.List[str]] = None):

        for _, _channel in self._channels.clear(keys).items():
            await _channel.close()

    async def open(self, targets: typing.List[str]):
        await self.reset_targets(targets)

    async def close(self):
        await self.clear_targets()

    def get_channel(self) -> typing.Tuple[str, grpc.aio.Channel]:
        return self._channels.get()

    def ping(self, timout: float = 1):
        _, channel = self.get_channel()
        return channel.unary_unary(r'/_/ping')(b'', timeout=timout)

    def unary_unary(
            self, method: str, call_params: typing.Union[bytes, typing.Dict],
            *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ) -> grpc.aio.UnaryUnaryCall:

        if request_serializer is Ellipsis:
            request_serializer = self._request_serializer

        if response_deserializer is Ellipsis:
            response_deserializer = self._response_deserializer

        _, channel = self.get_channel()

        return channel.unary_unary(
            method,
            request_serializer=request_serializer,
            response_deserializer=response_deserializer,
        )(call_params, timeout=timout, wait_for_ready=True, metadata=metadata)

    def unary_stream(
            self, method: str, call_params: typing.Union[bytes, typing.Dict],
            *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ) -> grpc.aio.UnaryStreamCall:

        if request_serializer is Ellipsis:
            request_serializer = self._request_serializer

        if response_deserializer is Ellipsis:
            response_deserializer = self._response_deserializer

        _, channel = self.get_channel()

        return channel.unary_stream(
            method,
            request_serializer=request_serializer,
            response_deserializer=response_deserializer,
        )(call_params, timeout=timout, wait_for_ready=True, metadata=metadata)

    def stream_unary(
            self, method: str,
            *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ) -> grpc.aio.StreamUnaryCall:

        if request_serializer is Ellipsis:
            request_serializer = self._request_serializer

        if response_deserializer is Ellipsis:
            response_deserializer = self._response_deserializer

        _, channel = self.get_channel()

        return channel.stream_unary(
            method,
            request_serializer=request_serializer,
            response_deserializer=response_deserializer,
        )(timeout=timout, wait_for_ready=True, metadata=metadata)

    def stream_stream(
            self, method: str,
            *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ) -> grpc.aio.StreamStreamCall:

        if request_serializer is Ellipsis:
            request_serializer = self._request_serializer

        if response_deserializer is Ellipsis:
            response_deserializer = self._response_deserializer

        _, channel = self.get_channel()

        return channel.stream_stream(
            method,
            request_serializer=request_serializer,
            response_deserializer=response_deserializer,
        )(timeout=timout, wait_for_ready=True, metadata=metadata)


class StreamClient:

    def __init__(
            self, client: GRPCClient, method: str,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ):

        self._grpc_client: GRPCClient = client
        self._stream_method: str = method
        self._stream_stub: typing.Optional[grpc.aio.StreamStreamCall] = None

        self._request_serializer: typing.Optional[typing.Callable] = request_serializer
        self._response_deserializer: typing.Optional[typing.Callable] = response_deserializer

    async def connect(self, *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None):

        self.close()

        self._stream_stub = self._grpc_client.stream_stream(
            self._stream_method, timout=timout, metadata=metadata,
            request_serializer = self._request_serializer,
            response_deserializer = self._response_deserializer
        )

        self._stream_stub.add_done_callback(self.on_close)

    def close(self):

        if self._stream_stub is not None and not self._stream_stub.done():
            self._stream_stub.cancel()

        self._stream_stub = None

    async def read(self) -> typing.Any:
        return await self._stream_stub.read()

    async def write(self, message: typing.Any):
        await self._stream_stub.write(message)

    async def done_writing(self):
        await self._stream_stub.done_writing()

    @abstractmethod
    def on_close(self, stub: grpc.aio.StreamStreamCall):
        """
        会话关闭回调
        """


class RobustStreamClient(StreamClient):

    def __init__(
            self, client: GRPCClient, method: str,
            request_serializer: typing.Optional[typing.Callable] = ...,
            response_deserializer: typing.Optional[typing.Callable] = ...
    ):
        
        super().__init__(client, method, request_serializer, response_deserializer)
        
        self._stream_task: typing.Optional[asyncio.Task] = None

    async def _do_stream_task(self):

        with catch_error():
            async for _message in self._stream_stub:
                await self.on_message(_message)

    async def join(self) -> typing.Any:
        return await self._stream_task

    async def connect(self, *, timout: typing.Optional[float] = None, metadata: typing.Optional[grpc.aio.Metadata] = None):

        await super().connect(timout=timout, metadata=metadata)

        await self.on_connect()

        self._stream_task = asyncio.create_task(self._do_stream_task())

    def close(self):

        if self._stream_task is not None and not self._stream_task.done():
            self._stream_task.cancel()

        self._stream_task = None
        
        super().close()

    @abstractmethod
    async def on_message(self, message: typing.Any):
        """
        接收消息回调
        """

    @abstractmethod
    async def on_connect(self):
        """
        与服务端通信连接成功后回调
        """
