# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import aiormq
import aio_pika

from abc import abstractmethod

from ...extend.asyncio.pool import ObjectInterface, ObjectPool


class _ProducerBase(ObjectInterface):

    def __init__(self, connection: aio_pika.RobustConnection):

        self._connection: aio_pika.RobustConnection = connection
        self._channel: typing.Optional[aio_pika.abc.AbstractRobustChannel] = None
        self._exchange: typing.Optional[aio_pika.abc.AbstractExchange] = None

    @abstractmethod
    async def open(self, *args, **kwargs):
        """
        启动发布者
        """

    async def close(self, with_connection: bool = False):

        await self._channel.close()

        if with_connection is True:
            await self._connection.close()

    async def publish(
            self,
            message: typing.Union[bytes, aio_pika.Message],
            routing_key: str = r'',
            **kwargs
    ) -> aiormq.abc.ConfirmationFrameType:

        return await self._exchange.publish(
            message if isinstance(message, aio_pika.Message) else aio_pika.Message(message),
            routing_key, **kwargs
        )


class RabbitMQProducer(_ProducerBase):
    """RabbitMQ发布者
    """

    async def open(
            self, *,
            channel_number: typing.Optional[int] = None,
            publisher_confirms: bool = True,
            on_return_raises: bool = False
    ):

        self._channel = await self._connection.channel(channel_number, publisher_confirms, on_return_raises)
        self._exchange = self._channel.default_exchange


class RabbitMQProducerForExchange(_ProducerBase):
    """RabbitMQ交换机发布者
    """

    def __init__(self, connection: aio_pika.RobustConnection, exchange_name: str):

        super().__init__(connection)

        self._exchange_name: str = exchange_name

    async def open(
            self, *,
            exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT,
            exchange_config: typing.Optional[typing.Dict] = None,
            channel_number: int = None,
            publisher_confirms: bool = True,
            on_return_raises: bool = False
    ):

        if exchange_config is None:
            exchange_config = {}

        self._channel = await self._connection.channel(channel_number, publisher_confirms, on_return_raises)
        self._exchange = await self._channel.declare_exchange(self._exchange_name, exchange_type, **exchange_config)

##################################################

class _ProducerPoolBase(ObjectPool):

    def __init__(self, pool_size: int, connection: aio_pika.RobustConnection):

        super().__init__(pool_size)

        self._connection = connection

    @abstractmethod
    def _create(self) -> ObjectInterface:
        """
        创建发布者信道池对象
        """

    async def close(self, with_connection: bool = False):

        await super().close()

        if with_connection is True:
            await self._connection.close()

    async def publish(
            self,
            message: typing.Union[bytes, aio_pika.Message],
            routing_key: str = r'',
            **kwargs
    ) -> aiormq.abc.ConfirmationFrameType:

        async with self.get() as producer:
            return await producer.publish(
                message if isinstance(message, aio_pika.Message) else aio_pika.Message(message),
                routing_key, **kwargs
            )


class RabbitMQProducerPool(_ProducerPoolBase):
    """RabbitMQ发布者连接池
    """

    def _create(self) -> RabbitMQProducer:

        return RabbitMQProducer(self._connection)

    async def open(
            self, *,
            channel_number: typing.Optional[int] = None,
            publisher_confirms: bool = True,
            on_return_raises: bool = False
    ):

        await self._connection.ready()

        await super().open(
            channel_number=channel_number,
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises
        )


class RabbitMQProducerForExchangePool(_ProducerPoolBase):
    """RabbitMQ交换机发布者连接池
    """

    def __init__(self, pool_size: int, connection: aio_pika.RobustConnection, exchange_name: str):

        super().__init__(pool_size, connection)

        self._exchange_name: str = exchange_name

    def _create(self) -> RabbitMQProducerForExchange:

        return RabbitMQProducerForExchange(self._connection, self._exchange_name)

    async def open(
            self, *,
            exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.FANOUT,
            exchange_config: typing.Optional[typing.Dict] = None,
            channel_number: typing.Optional[int] = None,
            publisher_confirms: bool = True,
            on_return_raises: bool = False
    ):

        await self._connection.ready()

        await super().open(
            exchange_type=exchange_type,
            exchange_config=exchange_config,
            channel_number=channel_number,
            publisher_confirms=publisher_confirms,
            on_return_raises=on_return_raises
        )
