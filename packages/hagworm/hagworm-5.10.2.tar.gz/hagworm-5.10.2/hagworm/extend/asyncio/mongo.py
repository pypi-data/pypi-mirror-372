# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from .base import Utils


MONGO_POLL_WATER_LEVEL_WARNING_LINE = 0x10


class MongoPool:
    """Mongo连接管理
    """

    def __init__(
            self, host: typing.List[str], username: str, password: str,
            *, name: typing.Optional[str] = None, auth_source: str = r'admin',
            min_pool_size: int = 8, max_pool_size: int = 32, max_idle_time: int = 3600, wait_queue_timeout: int = 10,
            compressors: str = r'zlib', zlib_compression_level: int = 6,
            **settings
    ):

        self._name: str = name if name is not None else Utils.uuid1()[:8]

        settings[r'host'] = host
        settings[r'authSource'] = auth_source
        settings[r'minPoolSize'] = min_pool_size
        settings[r'maxPoolSize'] = max_pool_size
        settings[r'maxIdleTimeMS'] = max_idle_time * 1000
        settings[r'waitQueueTimeoutMS'] = wait_queue_timeout * 1000
        settings[r'compressors'] = compressors
        settings[r'zlibCompressionLevel'] = zlib_compression_level

        if username and password:
            settings[r'username'] = username
            settings[r'password'] = password

        self._pool: AsyncIOMotorClient = AsyncIOMotorClient(**settings)

        for server in self._servers.values():
            server.pool.remove_stale_sockets()

        pool_options = self._pool.options.pool_options

        Utils.log.info(
            f"Mongo {host} ({self._name}) initialized: "
            f"{pool_options.min_pool_size}/{pool_options.max_pool_size}"
        )

    @property
    def _servers(self) -> typing.Dict:

        # noinspection PyProtectedMember
        return self._pool.delegate._topology._servers

    def _echo_pool_info(self):

        global MONGO_POLL_WATER_LEVEL_WARNING_LINE

        for address, server in self._servers.items():

            active_size = server.pool.active_sockets
            max_pool_size = server.pool.max_pool_size

            if (max_pool_size - active_size) < MONGO_POLL_WATER_LEVEL_WARNING_LINE:
                Utils.log.warning(
                    f'Mongo connection pool not enough ({self._name}){address}: '
                    f'{active_size}/{max_pool_size}'
                )
            else:
                Utils.log.debug(
                    f'Mongo connection pool info ({self._name}){address}: '
                    f'{active_size}/{max_pool_size}'
                )

    def close(self):

        if self._pool is not None:
            self._pool.close()
            self._pool = None

    def get_database(self, db_name) -> AsyncIOMotorDatabase:

        self._echo_pool_info()

        return self._pool[db_name]


class MongoDelegate:
    """Mongo功能组件
    """

    def __init__(self):

        self._mongo_pool: typing.Optional[MongoPool] = None

    def init_mongo(self, *args, **kwargs):

        self._mongo_pool = MongoPool(*args, **kwargs)

    @property
    def mongo_pool(self) -> MongoPool:

        return self._mongo_pool

    def close_mongo_pool(self):

        self._mongo_pool.close()

    def get_mongo_database(self, db_name) -> AsyncIOMotorDatabase:

        return self._mongo_pool.get_database(db_name)

    def get_mongo_collection(self, db_name, collection) -> AsyncIOMotorCollection:

        return self.get_mongo_database(db_name)[collection]
