# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import asyncio
import sqlalchemy

from asyncmy import Connection, Pool, create_pool, cursors, errors

from sqlalchemy.sql import ClauseElement, Select, Insert, Update, Delete

from .base import Utils

from ..interface import AsyncContextManager


MYSQL_POLL_WATER_LEVEL_WARNING_LINE = 0x10

MYSQL_EXECUTE_ARGUMENTS_TYPE = typing.Union[None, typing.Tuple, typing.List, typing.Dict]


# 数据库只读限制异常
class MySQLReadOnlyError(errors.MySQLError):
    pass


class MySQLClient(AsyncContextManager):
    """MySQL客户端对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    def __init__(self, pool: 'MySQLPool'):

        self._pool: MySQLPool = pool

        self._connection: typing.Optional[Connection] = None

        self._readonly: bool = pool.readonly

        self._lock: asyncio.Lock = asyncio.Lock()

    @property
    def readonly(self):

        return self._readonly

    @property
    def insert_id(self) -> int:

        if self._connection is not None:
            return self._connection.insert_id()

    async def _context_release(self):

        await self._close_connection()

    async def release(self):

        async with self._lock:
            await self._close_connection()

    async def _get_connection(self):

        if self._connection is None:
            self._connection = await self._pool.acquire()

        return self._connection

    async def _close_connection(self, discard=False):

        if self._connection is not None:

            if discard is True:
                await self._connection.ensure_closed()

            await self._pool.release(self._connection)

    async def _execute(self, query: str, args: MYSQL_EXECUTE_ARGUMENTS_TYPE = None) -> cursors.Cursor:

        try:

            connection = await self._get_connection()

            cursor = connection.cursor(cursor=self._pool.cursor_class)
            await cursor.execute(query, args)

            return cursor

        except Exception as err:

            await self._close_connection(True)

            raise err

    async def execute(self, query: str, args: MYSQL_EXECUTE_ARGUMENTS_TYPE = None) -> cursors.Cursor:

        async with self._lock:
            return await self._execute(query, args)

    @staticmethod
    def _clause_compile(query: ClauseElement) -> str:

        return query.compile(compile_kwargs={r'literal_binds': True}).string

    async def select(self, query: Select) -> typing.List[typing.Any]:

        async with self._lock:

            cursor = await self._execute(self._clause_compile(query))

            if cursor is not None:

                result = await cursor.fetchall()

                await cursor.close()

                return result

    async def find(self, query: Select) -> typing.Any:

        async with self._lock:

            cursor = await self._execute(self._clause_compile(query.limit(1)))

            if cursor is not None:

                result = await cursor.fetchone()

                await cursor.close()

                return result

    async def count(self, column: sqlalchemy.Column, where_clause: sqlalchemy.ColumnElement[bool] = None) -> int:

        _select = sqlalchemy.select([sqlalchemy.func.count(column).label(r'tbl_row_count')])

        if where_clause is not None:
            _select = _select.where(where_clause)

        cursor = await self.execute(self._clause_compile(_select))

        if cursor is not None:

            result = await cursor.fetchone()

            await cursor.close()

            return result[r'tbl_row_count']

    async def insert(self, query: Insert) -> int:

        if self._readonly:
            raise MySQLReadOnlyError()

        async with self._lock:

            cursor = await self._execute(self._clause_compile(query))

            if cursor is not None:

                result = self.insert_id

                await cursor.close()

                return result

    async def update(self, query: Update) -> int:

        if self._readonly:
            raise MySQLReadOnlyError()

        async with self._lock:

            cursor = await self._execute(self._clause_compile(query))

            if cursor is not None:

                result = cursor.rowcount

                await cursor.close()

                return result

    async def delete(self, query: Delete) -> int:

        if self._readonly:
            raise MySQLReadOnlyError()

        async with self._lock:

            cursor = await self._execute(self._clause_compile(query))

            if cursor is not None:

                result = cursor.rowcount

                await cursor.close()

                return result


class MySQLTransaction(MySQLClient):
    """MySQL客户端事务对象，使用with进行上下文管理

    将连接委托给客户端对象管理，提高了整体连接的使用率

    """

    def __init__(self, pool: 'MySQLPool'):

        super().__init__(pool)

        self._transaction_begin: bool = False

    async def _get_connection(self) -> Connection:

        if self._readonly is True:
            raise MySQLReadOnlyError()

        self._transaction_begin = True

        connection = await super()._get_connection()
        await connection.begin()

        return connection

    async def _context_release(self):

        await self.rollback()

    async def release(self):

        await self.rollback()

    async def commit(self):

        async with self._lock:

            if self._transaction_begin is True:
                await self._connection.commit()

            await self._close_connection()

    async def rollback(self):

        async with self._lock:

            if self._transaction_begin is True:
                await self._connection.rollback()

            await self._close_connection()


class MySQLPool:
    """MySQL连接管理
    """

    def __init__(
            self, host: str, port: int, db: str, user: str, password: str,
            *, name: str = None, minsize: int = 8, maxsize: int = 32, echo: bool = False, pool_recycle: int = 21600,
            charset: str = r'utf8', autocommit: bool = True,
            cursor_class: cursors.Cursor = cursors.DictCursor, readonly: bool = False,
            **settings
    ):

        self._name: str = name if name is not None else (Utils.uuid1()[:8] + (r'_ro' if readonly else r'_rw'))
        self._pool: typing.Optional[Pool] = None

        self._cursor_class: cursors.Cursor = cursor_class
        self._readonly: bool = readonly

        self._settings: typing.Dict[str, typing.Any] = settings

        self._settings[r'host'] = host
        self._settings[r'port'] = port
        self._settings[r'db'] = db

        self._settings[r'user'] = user
        self._settings[r'password'] = password

        self._settings[r'minsize'] = minsize
        self._settings[r'maxsize'] = maxsize

        self._settings[r'echo'] = echo
        self._settings[r'pool_recycle'] = pool_recycle
        self._settings[r'charset'] = charset
        self._settings[r'autocommit'] = autocommit

    @property
    def name(self) -> str:

        return self._name

    @property
    def readonly(self) -> bool:

        return self._readonly

    @property
    def cursor_class(self) -> cursors.Cursor:

        return self._cursor_class

    async def open(self):

        self._pool = await create_pool(**self._settings)

        Utils.log.info(
            f"MySQL [{self._settings[r'host']}:{self._settings[r'port']}] {self._settings[r'db']}"
            f" ({self._name}) initialized: {self._pool.size}/{self._pool.maxsize}"
        )

    async def close(self):

        if self._pool is not None:

            self._pool.close()
            await self._pool.wait_closed()

            self._pool = None

    def _echo_pool_info(self):

        global MYSQL_POLL_WATER_LEVEL_WARNING_LINE

        if (self._pool.maxsize - self._pool.size + self._pool.freesize) > MYSQL_POLL_WATER_LEVEL_WARNING_LINE:
            Utils.log.debug(
                f'MySQL connection pool info ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )
        else:
            Utils.log.warning(
                f'MySQL connection pool not enough ({self._name}): '
                f'{self._pool.freesize}({self._pool.size}/{self._pool.maxsize})'
            )

    async def acquire(self) -> Connection:

        self._echo_pool_info()

        return await self._pool.acquire()

    async def release(self, connection: Connection):

        if self._pool is not None:
            self._pool.release(connection)
        else:
            await connection.close()

    def get_client(self) -> MySQLClient:

        return MySQLClient(self)

    def get_transaction(self) -> MySQLTransaction:

        if self._readonly:
            raise MySQLReadOnlyError()

        return MySQLTransaction(self)


class MySQLDelegate:
    """MySQL功能组件
    """

    def __init__(self):

        self._mysql_rw_pool: typing.Optional[MySQLPool] = None
        self._mysql_ro_pool: typing.Optional[MySQLPool] = None

    @property
    def mysql_rw_pool(self) -> MySQLPool:

        return self._mysql_rw_pool

    @property
    def mysql_ro_pool(self) -> MySQLPool:

        return self._mysql_ro_pool

    async def init_mysql_rw(self, *args, **kwargs):

        self._mysql_rw_pool = MySQLPool(*args, readonly=False, **kwargs)
        await self._mysql_rw_pool.open()

    async def init_mysql_ro(self, *args, **kwargs):

        self._mysql_ro_pool = MySQLPool(*args, readonly=True, **kwargs)
        await self._mysql_ro_pool.open()

    async def close_mysql(self):

        if self._mysql_rw_pool is not None:
            await self._mysql_rw_pool.close()

        if self._mysql_ro_pool is not None:
            await self._mysql_ro_pool.close()

    def get_mysql_client(self, readonly=False) -> MySQLClient:

        if readonly:
            if self._mysql_ro_pool:
                return self._mysql_ro_pool.get_client()
            else:
                return self._mysql_rw_pool.get_client()
        else:
            return self._mysql_rw_pool.get_client()

    def get_mysql_transaction(self) -> MySQLTransaction:

        return self._mysql_rw_pool.get_transaction()
