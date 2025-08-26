# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from abc import ABC, abstractmethod
from typing import Any, Union, Literal, Optional, Iterable, List, Dict, Tuple

from coredis.typing import Node
from coredis import Redis, RedisCluster, Connection
from coredis.recipes.locks import LuaLock as _LuaLock

from .base import Utils

from ..error import catch_error
from ..interface import AsyncContextManager


class LuaLock(AsyncContextManager, _LuaLock):

    def __init__(
            self, client: Any, name: str,
            timeout: Optional[float] = None, sleep: float = 0.1,
            blocking: bool = True, blocking_timeout: Optional[float] = None
    ):
        _LuaLock.__init__(self, client, name, timeout, sleep, blocking, blocking_timeout)

    async def _context_release(self):
        with catch_error():
            await self.release()

    async def acquire(self) -> bool:
        if self.local.get() is None:
            return await super().acquire()
        else:
            return await super().extend(self.timeout)

    async def release(self):
        if self.local.get() is not None:
            await super().release()


class _PoolMixin(ABC):

    def __init__(self):

        self._name: str = Utils.uuid1()[:8]
        self._key_prefix: Optional[str] = None

    # noinspection PyUnresolvedReferences
    async def _init_connection(self):

        connections = []

        for _ in range(self.max_connections):
            connection = await self._get_connection()
            await connection.connect()
            connections.append(connection)

        for connection in connections:
            self.connection_pool.release(connection)

    @abstractmethod
    async def _get_connection(self) -> Connection:
        raise NotImplementedError()

    @staticmethod
    def decode(value: Union[bytes, Tuple[bytes, ...], List[bytes], Dict[bytes, bytes]]) -> Any:

        type_ = type(value)

        if type_ is bytes:
            return value.decode(r'utf-8')
        elif type_ is tuple:
            return tuple(
                _val.decode(r'utf-8') if isinstance(_val, bytes) else _val
                for _val in value
            )
        elif type_ is list:
            return [
                _val.decode(r'utf-8') if isinstance(_val, bytes) else _val
                for _val in value
            ]
        elif type_ is dict:
            return {
                _key.decode(r'utf-8'): _val.decode(r'utf-8') if isinstance(_val, bytes) else _val
                for _key, _val in value.items()
            }
        else:
            return value

    # noinspection PyUnresolvedReferences
    @property
    def max_connections(self) -> int:
        return self.connection_pool.max_connections

    def set_key_prefix(self, value: str):

        self._key_prefix = value

    def get_safe_key(self, key, *args, **kwargs) -> str:

        if self._key_prefix:
            _key = f'{self._key_prefix}:{key}'
        else:
            _key = key

        if args or kwargs:
            _key = f'{_key}:{Utils.params_sign(*args, **kwargs)}'

        return _key

    # noinspection PyUnresolvedReferences
    async def close(self):
        self.connection_pool.disconnect()

    def allocate_lock(
            self, name: str,
            timeout: Optional[float] = None, sleep: float = 0.1,
            blocking: bool = True, blocking_timeout: Optional[float] = None
    ) -> LuaLock:

        return LuaLock(self, name, timeout, sleep, blocking, blocking_timeout)

    # noinspection PyUnresolvedReferences
    async def get_obj(self, name: str) -> Any:

        result = await self.get(name)

        return Utils.pickle_loads(result) if result else result

    # noinspection PyUnresolvedReferences
    async def getset_obj(self, name: str, value: Any) -> Any:

        _value = Utils.pickle_dumps(value)

        result = await self.getset(name, _value)

        return Utils.pickle_loads(result) if result else result

    # noinspection PyUnresolvedReferences
    async def set_obj(self, name: str, value: Any, seconds: Optional[float] = None):

        _value = Utils.pickle_dumps(value)

        if seconds is None:
            return await self.set(name, _value)
        else:
            return await self.setex(name, _value, seconds)


class RedisPool(_PoolMixin, Redis):
    """StrictRedis连接管理
    """

    def __init__(
            self,
            host:str, port:int, db: int = 0,
            username: Optional[str] = None, password: Optional[str] = None,
            max_connections: int =32, max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        Redis.__init__(
            self,
            host, port, db,
            username=username, password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            protocol_version=protocol_version,
            **kwargs
        )

        _PoolMixin.__init__(self)

    async def _get_connection(self) -> Connection:
        return await self.connection_pool.get_connection()

    async def open(self):

        await Redis.initialize(self)

        await self._init_connection()

        config = self.connection_pool.connection_kwargs

        Utils.log.info(
            f"Redis Pool ({self._name}) [{config[r'host']}:{config[r'port']}] initialized: {self.max_connections}"
        )

        return self


class RedisClusterPool(_PoolMixin, RedisCluster):
    """StrictRedisCluster连接管理
    """

    def __init__(
            self,
            host: str, port: int, startup_nodes: Optional[Iterable[Node]] = None,
            username: Optional[str] = None, password: Optional[str] = None,
            max_connections: int = 32, max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        RedisCluster.__init__(
            self,
            host, port, startup_nodes=startup_nodes,
            username=username, password=password, max_connections=max_connections,
            max_idle_time=max_idle_time, idle_check_interval=idle_check_interval,
            protocol_version=protocol_version,
            **kwargs
        )

        _PoolMixin.__init__(self)

    async def _get_connection(self) -> Connection:
        return await self.connection_pool.get_random_connection()

    async def open(self):

        await RedisCluster.initialize(self)

        await self._init_connection()

        nodes = self.connection_pool.nodes.nodes

        Utils.log.info(
            f"Redis Cluster Pool ({self._name}) {list(nodes.keys())} initialized: {self.max_connections}"
        )

        return self


class RedisDelegate:
    """Redis功能组件
    """

    def __init__(self):

        self._redis_pool: Optional[RedisPool, RedisClusterPool] = None

    @property
    def redis_pool(self) -> Union[RedisPool, RedisClusterPool]:

        return self._redis_pool

    async def init_redis_single(
            self,
            host:str, port:int, db: int = 0,
            username: Optional[str] = None, password: Optional[str] = None, *,
            max_connections: int =32, max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        self._redis_pool = await RedisPool(
            host, port, db, username, password,
            max_connections, max_idle_time, idle_check_interval,
            protocol_version,
            **kwargs
        ).open()

        return self._redis_pool

    async def init_redis_cluster(
            self,
            host: str, port: int, startup_nodes: Optional[Iterable[Node]] = None,
            username: Optional[str] = None, password: Optional[str] = None, *,
            max_connections: int = 32, max_idle_time: float = 43200, idle_check_interval: float = 1,
            protocol_version: Literal[2, 3] = 2,
            **kwargs
    ):

        self._redis_pool = await RedisClusterPool(
            host, port, startup_nodes, username, password,
            max_connections, max_idle_time, idle_check_interval,
            protocol_version,
            **kwargs
        ).open()

        return self._redis_pool

    def set_redis_key_prefix(self, value: str):

        self._redis_pool.set_key_prefix(value)

    async def close_redis_pool(self):

        await self._redis_pool.close()

    def get_redis_client(self) -> Union[RedisPool, RedisClusterPool]:

        return self._redis_pool


class ShareCache(AsyncContextManager):
    """共享缓存，使用with进行上下文管理

    基于分布式锁实现的一个缓存共享逻辑，保证在分布式环境下，同一时刻业务逻辑只执行一次，其运行结果会通过缓存被共享

    """

    def __init__(
            self, redis_client: Union[RedisPool, RedisClusterPool], share_key: str,
            lock_timeout: float = 60, lock_blocking_timeout: float = 60
    ):

        self._redis_client: Union[RedisPool, RedisClusterPool] = redis_client
        self._share_key: str = redis_client.get_safe_key(share_key)

        self._lock: LuaLock = self._redis_client.allocate_lock(
            redis_client.get_safe_key(f'share_cache:{share_key}'),
            timeout=lock_timeout, blocking=True, blocking_timeout=lock_blocking_timeout
        )

        self.result = None

    async def _context_release(self):

        await self.release()

    async def get(self) -> Any:

        result = await self._redis_client.get_obj(self._share_key)

        if result is None:

            if await self._lock.acquire():
                result = await self._redis_client.get_obj(self._share_key)

        return result

    async def set(self, value: Any, expire: Optional[float] = None):

        return await self._redis_client.set_obj(self._share_key, value, expire)

    async def release(self):

        if self._lock:
            await self._lock.release()

        self._redis_client = self._lock = None


class PeriodCounter:

    def __init__(
            self, redis_client: Union[RedisPool, RedisClusterPool],
            key_prefix: str, time_slice: int
    ):

        self._redis_client: Union[RedisPool, RedisClusterPool] = redis_client

        self._key_prefix = key_prefix
        self._time_slice = time_slice

    def _get_key(self) -> str:

        time_period = Utils.math.floor(Utils.timestamp() / self._time_slice)

        return self._redis_client.get_safe_key(f'{self._key_prefix}:{time_period}')

    async def get(self):

        return await self._redis_client.get(
            self._get_key()
        )

    async def incr(self, val: int = 1) -> int:

        key = self._get_key()

        async with await self._redis_client.pipeline() as pipeline:

            await pipeline.incrby(key, val)
            await pipeline.expire(key, self._time_slice * 2)

            res, _ = await pipeline.execute()

            return res

    async def decr(self, val: int = 1) -> int:

        key = self._get_key()

        async with await self._redis_client.pipeline() as pipeline:

            await pipeline.decrby(key, val)
            await pipeline.expire(key, self._time_slice * 2)

            res, _ = await pipeline.execute()

            return res
