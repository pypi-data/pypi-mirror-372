# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio

import aiormq
import aio_pika

from ...extend.asyncio.base import Utils, AsyncCirculatoryForSecond


class RabbitMQConsumer:
    """RabbitMQ消费者
    """

    def __init__(self, connection: aio_pika.RobustConnection, queue_name: str):

        self._connection: aio_pika.RobustConnection = connection
        self._channel: typing.Optional[aio_pika.abc.AbstractRobustChannel] = None

        self._queue: typing.Optional[aio_pika.abc.AbstractRobustQueue] = None
        self._queue_name: str = queue_name

    @property
    def channel(self) -> aio_pika.abc.AbstractRobustChannel:
        return self._channel

    @property
    def queue(self) -> aio_pika.abc.AbstractRobustQueue:
        return self._queue

    @property
    def queue_name(self) -> str:
        return self._queue_name

    async def open(
            self, *,
            consume_func: typing.Optional[typing.Callable] = None,
            consume_no_ack: bool = False,
            channel_qos_config: typing.Optional[typing.Dict] = None,
            queue_config: typing.Optional[typing.Dict] = None
    ):

        await self._connection.ready()

        if channel_qos_config is None:
            channel_qos_config = {r'prefetch_count': 1}
        elif r'prefetch_count' not in channel_qos_config:
            channel_qos_config[r'prefetch_count'] = 1

        if queue_config is None:
            queue_config = {}

        self._channel = await self._connection.channel()

        await self._channel.set_qos(**channel_qos_config)

        self._queue = await self._channel.declare_queue(self._queue_name, **queue_config)

        if consume_func is not None:
            await self._queue.consume(consume_func, no_ack=consume_no_ack)

        Utils.log.info(f"rabbitmq consumer {self._queue_name} initialized: {channel_qos_config[r'prefetch_count']}")

    async def close(self, with_connection: bool = False):

        await self._channel.close()

        if with_connection is True:
            await self._connection.close()

    async def block_pull(
            self,
            consume_func: typing.Callable,
            consume_no_ack: bool = False,
            wait_time: int = 1
    ):

        while not self._connection.is_closed or self._connection.reconnecting:

            try:

                message = await self._queue.get(no_ack=consume_no_ack, fail=False)

                if message is None:
                    await Utils.sleep(wait_time)
                else:
                    await consume_func(message)

            except Exception as err:

                Utils.log.error(str(err))
                await Utils.sleep(wait_time)

        Utils.log.warning(f'rabbitmq consumer block pull exit: {consume_func.__name__}')


class RabbitMQConsumerForExchange(RabbitMQConsumer):
    """RabbitMQ注册到交换机的消费者
    """

    def __init__(self, connection: aio_pika.RobustConnection, queue_name: str, exchange_name: str):
        
        super().__init__(connection, queue_name)

        self._exchange: typing.Optional[aio_pika.abc.AbstractExchange] = None
        self._exchange_name: str = exchange_name

        self._exchange_bind_task: typing.Optional[asyncio.Task] = None

    @property
    def exchange(self) -> aio_pika.abc.AbstractExchange:
        return self._exchange

    @property
    def exchange_name(self) -> str:
        return self._exchange_name

    async def _bind_exchange(self, routing_key: typing.Optional[str] = None):

        async for _ in AsyncCirculatoryForSecond(interval=10):

            try:
                self._exchange = await self._channel.get_exchange(self._exchange_name)
                await self._queue.bind(self._exchange, routing_key)
                break
            except aiormq.exceptions.ChannelNotFoundEntity as err:
                Utils.log.error(f'rabbitmq {self._queue_name} failed to bind {self._exchange_name}: {str(err)}')

        Utils.log.info(f'rabbitmq {self._queue_name} successfully bound {self._exchange_name}')

    async def open(
            self, *,
            consume_func: typing.Optional[typing.Callable] = None,
            consume_no_ack: bool = False,
            channel_qos_config: typing.Optional[typing.Dict] = None,
            queue_config: typing.Optional[typing.Dict] = None,
            routing_key: typing.Optional[str] = None
    ):

        await super().open(
            consume_func=consume_func, consume_no_ack=consume_no_ack,
            channel_qos_config=channel_qos_config, queue_config=queue_config
        )

        self._exchange_bind_task = asyncio.Task(self._bind_exchange(routing_key))

    async def block_pull(
            self,
            consume_func: typing.Callable,
            consume_no_ack: bool = False,
            wait_time: int = 1
    ):

        await self._exchange_bind_task
        await super().block_pull(consume_func, consume_no_ack, wait_time)
