# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import typing
import socket
import asyncio
import functools

import grpc

from .server import GRPCServer, Router
from .server import GRPC_MODE_TYPE, UNARY_UNARY_MODE, UNARY_STREAM_MODE, STREAM_UNARY_MODE, STREAM_STREAM_MODE
from .client import GRPCClient

from ...extend.asyncio.base import Utils
from ...extend.asyncio.command import MainProcess, SubProcess


def copy_metadata(remote_context: grpc.aio.ServicerContext) -> grpc.aio.Metadata:

    metadata = grpc.aio.Metadata((r'remote-peer', remote_context.peer()))

    for _key, _value in remote_context.invocation_metadata():
        metadata.add(_key, _value)

    return metadata


class _BridgeUpstream:

    def __init__(
            self, remote_request: typing.AsyncIterator,
            server_stream_stub: typing.Union[grpc.aio.StreamUnaryCall, grpc.aio.StreamStreamCall]
    ):

        self._remote_request: typing.AsyncIterator = remote_request

        self._upstream_stub: typing.Union[grpc.aio.StreamUnaryCall, grpc.aio.StreamStreamCall] = server_stream_stub
        self._upstream_task: asyncio.Task = asyncio.create_task(self._do_upstream_task())

    async def _do_upstream_task(self):

        try:
            async for _message in self._remote_request:
                await self._upstream_stub.write(_message)
            await self._upstream_stub.done_writing()
        except Exception as err:
            Utils.log.error(str(err))
        finally:
            if self._upstream_stub is not None:
                self._upstream_stub.cancel()


class _BridgeDownstream:

    def __init__(
            self, remote_context: grpc.aio.ServicerContext,
            server_stream_stub: typing.Union[grpc.aio.UnaryStreamCall, grpc.aio.StreamStreamCall]
    ):

        self._remote_context: grpc.aio.ServicerContext = remote_context

        self._downstream_stub: typing.Union[grpc.aio.UnaryStreamCall, grpc.aio.StreamStreamCall] = server_stream_stub
        self._downstream_task: asyncio.Task = asyncio.create_task(self._do_downstream_task())

    async def _do_downstream_task(self):

        remote_peer = self._remote_context.peer()

        Utils.log.info(f'grpc bridge open stream: {remote_peer}')

        try:
            async for _message in self._downstream_stub:
                await self._remote_context.write(_message)
        except grpc.aio.UsageError:
            pass
        except Exception as err:
            Utils.log.error(str(err))
        finally:
            if self._downstream_stub is not None:
                self._downstream_stub.cancel()

        Utils.log.info(f'grpc bridge close stream: {remote_peer}')


class BridgeUnaryStream(_BridgeDownstream):

    def __init__(
            self, server_bridge: GRPCClient, server_method: str,
            remote_request: typing.Union[str, bytes], remote_context: grpc.aio.ServicerContext
    ):

        super().__init__(
            remote_context,
            server_bridge.unary_stream(
                server_method, remote_request,
                metadata=copy_metadata(remote_context)
            )
        )

    async def join(self):
        await self._downstream_task


class BridgeStreamUnary(_BridgeUpstream):

    def __init__(
            self, server_bridge: GRPCClient, server_method: str,
            remote_request: typing.AsyncIterator, remote_context: grpc.aio.ServicerContext
    ):

        super().__init__(
            remote_request,
            server_bridge.stream_unary(
                server_method,
                metadata=copy_metadata(remote_context)
            )
        )

    async def join(self) -> typing.Any:
        return await self._upstream_stub


class BridgeStreamStream(_BridgeUpstream, _BridgeDownstream):

    def __init__(
            self, server_bridge: GRPCClient, server_method: str,
            remote_request: typing.AsyncIterator, remote_context: grpc.aio.ServicerContext
    ):

        server_stream_stub = server_bridge.stream_stream(
            server_method,
            metadata=copy_metadata(remote_context)
        )

        _BridgeUpstream.__init__(self, remote_request, server_stream_stub)
        _BridgeDownstream.__init__(self, remote_context, server_stream_stub)

    async def join(self):
        await Utils.wait_any_completed(self._upstream_task, self._downstream_task)


class GRPCBridge:

    def __init__(
            self, address: typing.Union[str, typing.Tuple[str, int]], routers: typing.List[Router],
            grpc_family: int = socket.AF_INET, grpc_server_credentials: typing.Optional[grpc.ServerCredentials] = None
    ):

        self._routers: typing.List[Router] = routers

        self._grpc_client: typing.Optional[GRPCClient] = None
        self._grpc_server: typing.Optional[GRPCServer] = None

        self._grpc_address: typing.Union[str, typing.Tuple[str, int]] = address
        self._grpc_family: int = grpc_family
        self._grpc_server_credentials: typing.Optional[grpc.ServerCredentials] = grpc_server_credentials

    async def _unary_unary_handler(self, method: str, request: typing.Union[str, bytes], context: grpc.aio.ServicerContext) -> typing.Any:
        try:
            return await self._grpc_client.unary_unary(method, request, metadata=copy_metadata(context))
        except grpc.aio.AioRpcError as err:
            await context.abort(err.code(), err.details())

    async def _unary_stream_handler(self, method: str, request: typing.Union[str, bytes], context: grpc.aio.ServicerContext) -> typing.Any:
        try:
            return await BridgeUnaryStream(self._grpc_client, method, request, context).join()
        except grpc.aio.AioRpcError as err:
            await context.abort(err.code(), err.details())

    async def _stream_unary_handler(self, method: str, request: typing.AsyncIterator, context: grpc.aio.ServicerContext) -> typing.Any:
        try:
            return await BridgeStreamUnary(self._grpc_client, method, request, context).join()
        except grpc.aio.AioRpcError as err:
            await context.abort(err.code(), err.details())

    async def _stream_stream_handler(self, method: str, request: typing.AsyncIterator, context: grpc.aio.ServicerContext) -> typing.Any:
        try:
            return await BridgeStreamStream(self._grpc_client, method, request, context).join()
        except grpc.aio.AioRpcError as err:
            await context.abort(err.code(), err.details())

    def _get_handler(self, method: str, mode: GRPC_MODE_TYPE) -> grpc.RpcMethodHandler:

        handler = None

        if mode is UNARY_UNARY_MODE:
            handler = functools.partial(self._unary_unary_handler, method)
        elif mode is UNARY_STREAM_MODE:
            handler = functools.partial(self._unary_stream_handler, method)
        elif mode is STREAM_UNARY_MODE:
            handler = functools.partial(self._stream_unary_handler, method)
        elif mode is STREAM_STREAM_MODE:
            handler = functools.partial(self._stream_stream_handler, method)

        return mode(handler)

    def _init_handlers(self):

        generic_handlers = [
            grpc.method_handlers_generic_handler(
                r'_',
                {
                    r'register': STREAM_STREAM_MODE(self._register_worker),
                    r'ping': self._get_handler(r'/_/ping', UNARY_UNARY_MODE),
                }
            )
        ]

        for router in self._routers:
            generic_handlers.append(
                grpc.method_handlers_generic_handler(
                    router.service,
                    {
                        _handler.alias: self._get_handler(f'/{router.service}/{_handler.alias}', _handler.mode)
                        for _handler in router.handlers
                    }
                )
            )

        self._grpc_server.server.add_generic_rpc_handlers(generic_handlers)

    async def _register_worker(self, request: typing.AsyncIterator, context: grpc.aio.ServicerContext):

        target = dict(context.invocation_metadata()).get(r'worker_entrypoint')

        if not target:
            await context.abort(grpc.StatusCode.INTERNAL, details=r'worker entrypoint not found')

        await self._grpc_client.append_target(target)

        Utils.log.success(f'grpc bridge connected: {target}')

        async for _message in request:
            Utils.log.warning(f'grpc bridge received: {_message}')

    async def open(self):

        self._grpc_client: GRPCClient = GRPCClient(request_serializer=None, response_deserializer=None)
        self._grpc_server: GRPCServer = GRPCServer(request_deserializer=None, response_serializer=None)

        self._init_handlers()

        await self._grpc_server.start(
            self._grpc_address,
            family=self._grpc_family,
            server_credentials=self._grpc_server_credentials
        )

    async def close(self):

        await self._grpc_server.stop()
        await self._grpc_client.close()

    async def join(self):
        await self._grpc_server.wait()


class GRPCEntry:

    def __init__(self, bridge_address: typing.Union[str, typing.Tuple[str, int]], routers: typing.List[Router]):

        self._bridge_address: str = self._decode_address(bridge_address)
        self._server_address: str = f'/tmp/grpc_node_{Utils.getpid()}.sock'

        self._grpc_server: typing.Optional[GRPCServer] = None
        self._grpc_routers: typing.List[Router] = routers

        self._bridge_client: typing.Optional[GRPCClient] = None
        self._bridge_client_stub: typing.Optional[grpc.aio.StreamStreamCall] = None

    @staticmethod
    def _decode_address(bridge_address: typing.Union[str, typing.Tuple[str, int]]) -> str:

        if isinstance(bridge_address, str):
            bridge_address = Utils.split_str(bridge_address, r':')

        if bridge_address[0] == r'0.0.0.0':
            bridge_address =(r'localhost', bridge_address[1])

        return Utils.join_str(bridge_address, r':')

    async def start(self):

        if os.path.exists(self._server_address):
            os.remove(self._server_address)

        self._grpc_server = GRPCServer()

        for _router in self._grpc_routers:
            self._grpc_server.bind_router(_router)

        await self._grpc_server.start(self._server_address, family=socket.AF_UNIX, enable_ping=True)

        self._bridge_client = GRPCClient()
        await self._bridge_client.open([self._bridge_address])

        self._bridge_client_stub = self._bridge_client.stream_stream(
            r'/_/register',
            metadata=grpc.aio.Metadata((r'worker_entrypoint', r'unix:' + self._server_address))
        )

    async def stop(self):
        await self._bridge_client.close()
        await self._grpc_server.stop()

    async def join(self):

        async for _message in self._bridge_client_stub:
            Utils.log.warning(f'grpc worker received: {_message}')

        await self._grpc_server.wait()


class GRPCMainProcess(MainProcess):

    def __init__(
            self, address: typing.Union[str, typing.Tuple[str, int]], routers: typing.List[Router],
            worker: typing.Type[r'GRPCWorker'], sub_process_num: int, *,
            grpc_family: int = socket.AF_INET, grpc_server_credentials: typing.Optional[grpc.ServerCredentials] = None,
            cpu_affinity: bool = False, join_timeout: int = 10
    ):

        super().__init__(
            worker.create, sub_process_num,
            cpu_affinity=cpu_affinity, join_timeout=join_timeout,
            bridge_address=address, routers=routers
        )

        self._grpc_bridge: GRPCBridge = GRPCBridge(address, routers, grpc_family, grpc_server_credentials)

    async def initialize(self):
        await self._grpc_bridge.open()

    async def release(self):
        await self._grpc_bridge.close()


class GRPCWorker(SubProcess):

    def __init__(self, process_num: int, bridge_address: typing.Union[str, typing.Tuple[str, int]], routers: typing.List[Router]):

        super().__init__(process_num)

        self._grpc_entry: GRPCEntry = GRPCEntry(bridge_address, routers)

    async def initialize(self):
        await self._grpc_entry.start()

    async def release(self):
        await self._grpc_entry.stop()

    async def _execute(self):
        await self._grpc_entry.join()
