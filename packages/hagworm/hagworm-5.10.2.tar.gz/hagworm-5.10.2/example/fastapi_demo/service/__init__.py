# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.extend.trace import get_trace_id
from hagworm.extend.error import Ignore
from hagworm.extend.metaclass import Singleton
from hagworm.extend.asyncio.base import Utils
from hagworm.extend.asyncio.redis import RedisDelegate
from hagworm.extend.asyncio.mongo import MongoDelegate
from hagworm.extend.asyncio.mysql import MySQLDelegate
from hagworm.extend.ntp import NTPClient

from setting import Config


class DataSource(Singleton, RedisDelegate, MongoDelegate, MySQLDelegate):

    def __init__(self):

        # RedisDelegate.__init__(self)
        # MongoDelegate.__init__(self)
        # MySQLDelegate.__init__(self)

        self._ntp_client = NTPClient()

    @property
    def timestamp_ms(self) -> int:
        return self._ntp_client.timestamp_ms

    @classmethod
    async def initialize(cls):

        inst = cls()

        inst._ntp_client.start()

        # (await inst.init_redis_single(
        #     Config.RedisHost[0], Config.RedisHost[1], password=Config.RedisPasswd,
        #     min_connections=Config.RedisMinConn, max_connections=Config.RedisMaxConn
        # )).set_key_prefix(Config.RedisKeyPrefix)
        #
        # inst.init_mongo(
        #     Config.MongoHost, Config.MongoUser, Config.MongoPasswd,
        #     auth_source=Config.MongoAuth,
        #     min_pool_size=Config.MongoMinConn, max_pool_size=Config.MongoMaxConn, max_idle_time=3600
        # )
        #
        # if Config.MySqlMasterServer:
        #
        #     await inst.init_mysql_rw(
        #         Config.MySqlMasterServer[0], Config.MySqlMasterServer[1], Config.MySqlName,
        #         Config.MySqlUser, Config.MySqlPasswd,
        #         minsize=Config.MySqlMasterMinConn, maxsize=Config.MySqlMasterMaxConn,
        #         echo=Config.Debug, pool_recycle=21600
        #     )
        #
        # if Config.MySqlSlaveServer:
        #
        #     await inst.init_mysql_ro(
        #         Config.MySqlSlaveServer[0], Config.MySqlSlaveServer[1], Config.MySqlName,
        #         Config.MySqlUser, Config.MySqlPasswd,
        #         minsize=Config.MySqlSlaveMinConn, maxsize=Config.MySqlSlaveMaxConn,
        #         echo=Config.Debug, pool_recycle=21600
        #     )

    @classmethod
    async def release(cls):

        inst = cls()

        # await inst.close_mysql()
        #
        # inst.close_mongo_pool()
        #
        # await inst.close_redis_pool()

        inst._ntp_client.stop()


class ServiceBase(Singleton, Utils):

    def __init__(self):

        self._data_source = DataSource()

    @property
    def trace_id(self):

        return get_trace_id()

    def Break(self, *args, layers=1):

        raise Ignore(*args, layers=layers)
