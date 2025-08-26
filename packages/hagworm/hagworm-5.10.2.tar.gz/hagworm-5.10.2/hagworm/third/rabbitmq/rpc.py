# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import asyncio
import inspect
import aio_pika
import async_timeout

from .publish import RabbitMQProducerForExchangePool
from .consume import RabbitMQConsumerForExchange

from ...extend.error import catch_error
from ...extend.struct import Enum
from ...extend.asyncio.base import Utils


STREAM_EOF: bytes = b'\0\0'
ERROR_HEAD: bytes = b'\7\7'

class RpcServerError(Exception): pass


class FunctionType(Enum):
    Unary = r'unary'
    Stream = r'stream'


def get_routing_key(server_name: typing.Optional[str]) -> str:
    return f'rpc_server.{server_name}' if server_name else r'rpc_server'


class RpcServer:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection, exchange_name: str,
            *, server_name: typing.Optional[str] = None, message_ttl: float = 60, max_priority: int = 10
    ):

        self._rpc_function: typing.Dict[str, typing.Callable] = {}

        self._exchange_name: str = exchange_name

        self._queue_config: typing.Dict[str, typing.Any] = {
            r'arguments': {
                r'x-message-ttl': round(message_ttl * 1000),
                r'x-max-priority': max_priority,
            }
        }

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, get_routing_key(server_name), self._exchange_name
        )

    async def open(self):

        self._rpc_function[r'ping'] = lambda: r'pong'

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config=self._queue_config,
            channel_qos_config={r'prefetch_count': self._producer.size}
        )

    async def close(self):

        await self._producer.close()
        await self._consumer.close()

        self._rpc_function.clear()

    async def _reply_message(self, incoming: aio_pika.IncomingMessage, response: typing.Any):

        await self._producer.publish(
            aio_pika.Message(
                body=Utils.msgpack_encode(response),
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _reply_error(self, incoming: aio_pika.IncomingMessage, error: Exception):

        await self._producer.publish(
            aio_pika.Message(
                body=ERROR_HEAD + str(error).encode(),
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _reply_eof(self, incoming: aio_pika.IncomingMessage):

        await self._producer.publish(
            aio_pika.Message(
                body=STREAM_EOF,
                correlation_id=incoming.correlation_id
            ),
            routing_key=incoming.reply_to
        )

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        with catch_error():

            message_body = Utils.msgpack_decode(message.body)

            _func_type = message_body.get(r'type')
            _func_name = message_body.get(r'func')
            _func_args = message_body.get(r'args')
            _func_kwargs = message_body.get(r'kwargs')

            try:

                if not (_function := self._rpc_function.get(_func_name)):
                    raise Exception(f'function {_func_name} not found')

                if _func_type == FunctionType.Unary.value and inspect.iscoroutinefunction(_function):
                    await self._reply_message(message, await _function(*_func_args, **_func_kwargs))
                elif _func_type == FunctionType.Stream.value and inspect.isasyncgenfunction(_function):
                    async for _item in _function(*_func_args, **_func_kwargs):
                        await self._reply_message(message, _item)
                    else:
                        await self._reply_eof(message)
                else:
                    raise Exception(f'function not supported: {message_body}')

            except Exception as err:
                await self._reply_error(message, err)
                raise

        await message.ack()

    def register(self, name: str, func: typing.Callable):

        self._rpc_function[name] = func

        Utils.log.info(f'rpc server register {name} {func}')


class RpcClient:

    def __init__(
            self, pool_size: int, connection: aio_pika.RobustConnection,
            exchange_name: str, message_ttl: float = 60
    ):

        self._unary_monitors: typing.Dict[str, asyncio.Future] = {}
        self._stream_monitors: typing.Dict[str, asyncio.Queue[asyncio.Future]] = {}

        self._exchange_name: str = exchange_name

        self._queue_config: typing.Dict[str, typing.Any] = {
            r'exclusive': True,
            r'arguments': {r'x-message-ttl': round(message_ttl * 1000)}
        }

        self._producer: RabbitMQProducerForExchangePool = RabbitMQProducerForExchangePool(
            pool_size, connection, self._exchange_name
        )

        self._consumer: RabbitMQConsumerForExchange = RabbitMQConsumerForExchange(
            connection, f'rpc_client.{Utils.uuid1()}', self._exchange_name
        )

    async def open(self):

        await self._producer.open(
            exchange_type=aio_pika.ExchangeType.TOPIC
        )

        await self._consumer.open(
            consume_func=self._consume_message,
            consume_no_ack=False,
            queue_config=self._queue_config,
            channel_qos_config={r'prefetch_count': 1}
        )

    async def close(self):

        await self._producer.close()
        await self._consumer.close()

    async def _send_message(self, correlation_id: str, priority: int, server_name: str, message: typing.Any):

        await self._producer.publish(
            aio_pika.Message(
                Utils.msgpack_encode(message),
                priority=priority,
                correlation_id=correlation_id,
                reply_to=self._consumer.queue_name,
            ),
            routing_key=get_routing_key(server_name),
        )

    async def _consume_message(self, message: aio_pika.IncomingMessage):

        with catch_error():

            correlation_id = message.correlation_id
            message_body = message.body

            if correlation_id in self._unary_monitors:

                future = self._unary_monitors[correlation_id]

                if message_body[:2] == ERROR_HEAD:
                    future.set_exception(RpcServerError(message_body[2:].decode()))
                else:
                    future.set_result(Utils.msgpack_decode(message_body))

            elif correlation_id in self._stream_monitors:

                future = asyncio.Future()

                if message_body == STREAM_EOF:
                    future.set_exception(EOFError())
                elif message_body[:2] == ERROR_HEAD:
                    future.set_exception(RpcServerError(message_body[2:].decode()))
                else:
                    future.set_result(Utils.msgpack_decode(message_body))

                self._stream_monitors[correlation_id].put_nowait(future)

            else:

                if message_body == STREAM_EOF:
                    message_data = r'EOF'
                elif message_body[:2] == ERROR_HEAD:
                    message_data = f'ERROR: {message_body[2:].decode()}'
                else:
                    message_data = Utils.msgpack_decode(message_body)

                Utils.log.warning(f'unexpected message: {correlation_id=} {message_data=}')

        await message.ack()

    async def ping(self, priority: int = 0, server_name: typing.Optional[str] = None):
        return await self.call(r'ping', priority=priority, server_name=server_name)

    async def call(
            self, func_name: str, *,
            func_args: typing.Optional[typing.List] = None,
            func_kwargs: typing.Optional[typing.Dict] = None,
            priority: int = 0,
            server_name: typing.Optional[str] = None,
            request_timeout: float = 60
    ):

        correlation_id = Utils.uuid1()

        future = self._unary_monitors[correlation_id] = asyncio.Future()

        try:

            async with async_timeout.timeout(request_timeout):

                await self._send_message(
                    correlation_id, priority, server_name,
                    {
                        r'type': FunctionType.Unary.value,
                        r'func': func_name,
                        r'args': func_args if func_args is not None else [],
                        r'kwargs': func_kwargs if func_kwargs is not None else {},
                    }
                )

                return await future

        except asyncio.TimeoutError:
            Utils.log.error(f'rpc call timeout: {correlation_id=} {func_name=} {func_args=} {func_kwargs=}')
            raise

        except asyncio.CancelledError:
            Utils.log.warning(f'rpc call cancelled: {correlation_id=} {func_name=} {func_args=} {func_kwargs=}')
            raise

        finally:
            del self._unary_monitors[correlation_id]

    async def call_stream(
            self, func_name: str, *,
            func_args: typing.Optional[typing.List] = None,
            func_kwargs: typing.Optional[typing.Dict] = None,
            priority: int = 0,
            server_name: typing.Optional[str] = None,
            request_timeout: float = 3600
    ):

        correlation_id = Utils.uuid1()

        queue = self._stream_monitors[correlation_id] = asyncio.Queue()

        try:

            async with async_timeout.timeout(request_timeout):

                await self._send_message(
                    correlation_id, priority, server_name,
                    {
                        r'type': FunctionType.Stream.value,
                        r'func': func_name,
                        r'args': func_args if func_args is not None else [],
                        r'kwargs': func_kwargs if func_kwargs is not None else {},
                    }
                )

                with Utils.suppress(EOFError):
                    while _future := await queue.get():
                        yield await _future
                        queue.task_done()

        except asyncio.TimeoutError:
            Utils.log.error(f'rpc call stream timeout: {correlation_id=} {func_name=} {func_args=} {func_kwargs=}')
            raise

        except asyncio.CancelledError:
            Utils.log.warning(f'rpc call stream cancelled: {correlation_id=} {func_name=} {func_args=} {func_kwargs=}')
            raise

        finally:
            del self._stream_monitors[correlation_id]
