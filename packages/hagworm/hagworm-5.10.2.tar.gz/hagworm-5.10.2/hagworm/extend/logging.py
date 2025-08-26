# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import io
import os
import sys
import copy
import signal
import typing
import queue
import logging
import datetime

import loguru

from abc import ABCMeta, abstractmethod
from datetime import timedelta
from contextlib import contextmanager

# noinspection PyProtectedMember
from loguru._file_sink import FileSink

from elasticsearch import Elasticsearch, AsyncElasticsearch, ApiError as ESApiError, NotFoundError as ESNotFoundError, helpers as es_helpers
from confluent_kafka import Producer as KFKProducer
from filelock import FileLock

from .trace import get_trace_id
from .base import Utils
from .asyncio.future import Thread


class LogFileRotator:

    @classmethod
    def make(cls, _size: int = 500, _time: str = r'00:00'):

        return cls(_size, _time).should_rotate

    def __init__(self, _size: int, _time: str):

        _size = _size * (1024 ** 2)
        _time = Utils.split_int(_time, r':')

        now_time = Utils.today()

        self._size_limit: int = _size
        self._time_limit: datetime.datetime = now_time.replace(hour=_time[0], minute=_time[1])

        if now_time >= self._time_limit:
            self._time_limit += timedelta(days=1)

    def should_rotate(self, message: 'loguru.Message', file: io.FileIO):

        file.seek(0, 2)

        if file.tell() + len(message) > self._size_limit:
            return True

        if message.record[r'time'].timestamp() > self._time_limit.timestamp():
            self._time_limit += timedelta(days=1)
            return True

        return False


DEFAULT_LOG_FILE_ROTATOR = LogFileRotator.make()


class InterceptHandler(logging.Handler):
    """日志拦截器
    """

    def emit(self, record: logging.LogRecord):

        Utils.log.opt(
            depth=8,
            exception=record.exc_info
        ).log(
            record.levelname,
            record.getMessage()
        )


class _BaseSink(metaclass=ABCMeta):
    """基础日志投递基类
    """

    def __init__(self, log_maxsize: int = 0xfff, buffer_maxsize: int = 0xfff, bulk_maxsize: int = 0x800, write_max_delay: int = 5):

        self._buffer: queue.Queue = queue.Queue(buffer_maxsize)

        self._log_maxsize: int = log_maxsize
        self._bulk_maxsize: int = bulk_maxsize
        self._write_max_delay: int = write_max_delay

        self._task: Thread = Thread(target=self._do_task)
        self._task.start()

        signal.signal(signal.SIGINT, self.close)
        signal.signal(signal.SIGTERM, self.close)

    def write(self, message: 'loguru.Message'):

        try:

            if message.record[r'thread'].id == self._task.ident or not message.record[r'message'].strip():
                return

            log_extra = message.record[r'extra']

            if r'trace_id' not in log_extra:

                trace_id = get_trace_id()

                if trace_id is not None:
                    log_extra[r'trace_id'] = trace_id

            # 只会影响使用record数据的场景
            if len(message.record[r'message']) > self._log_maxsize:
                message.record[r'message'] = message.record[r'message'][:self._log_maxsize] + r'...'

            self._buffer.put_nowait(message)

        except queue.Full as _:

            if message.record[r'level'].no > logging.INFO:
                sys.stderr.write(message)

        except Exception as err:

            sys.stderr.write(f'{str(err)}\n')

    def close(self, *_):

        self._task.stop(10)

    def _do_task(self):

        messages = []

        while not self._task.is_stopped():

            try:

                for _idx in range(self._write_max_delay):

                    try:

                        messages.append(
                            self._buffer.get(block=True, timeout=1)
                        )

                        self._buffer.task_done()

                    except queue.Empty:

                        if self._task.is_stopped():
                            break

                    finally:

                        if len(messages) >= self._bulk_maxsize or (_idx + 1) >= self._write_max_delay:
                            break

                if messages:
                    self._write_logs(messages)
                    messages.clear()

            except Exception as err:

                sys.stderr.write(f'{str(err)}\n')

    @abstractmethod
    def _write_logs(self, logs: typing.List['loguru.Message']):
        """
        实际写入日志的操作
        """


class QueuedFileSink(_BaseSink):
    """日志文件队列
    """

    def __init__(
            self, path: str, *,
            log_maxsize: int = 0xfff, buffer_maxsize: int = 0xfff, bulk_maxsize: int = 0x800, write_max_delay: int = 5,
            **kwargs
    ):

        super().__init__(log_maxsize, buffer_maxsize, bulk_maxsize, write_max_delay)

        self._file_sink: FileSink = FileSink(path, **kwargs)

    def _write_logs(self, logs: typing.List['loguru.Message']):

        for _log in logs:
            self._file_sink.write(_log)


class KafkaSink(_BaseSink):
    """Kafka日志投递
    """

    def __init__(
            self, servers: typing.Any, topic: str, *,
            log_maxsize: int = 0xfff, buffer_maxsize: int = 0xfff, bulk_maxsize: int = 0x800, write_max_delay: int = 5,
            **kwargs
    ):

        super().__init__(log_maxsize, buffer_maxsize, bulk_maxsize, write_max_delay)

        kwargs[r'bootstrap.servers'] = servers

        self._producer: KFKProducer = KFKProducer(kwargs)

        self._topic: str = topic

    def _write_logs(self, logs: typing.List['loguru.Message']):

        for _log in logs:
            self._producer.produce(
                self._topic,
                Utils.json_encode(
                    {
                        r'extra': _log.record[r'extra'],
                        r'process': {
                            r'id': _log.record[r'process'].id,
                            r'name': _log.record[r'process'].name,
                        },
                        r'thread': {
                            r'id': _log.record[r'thread'].id,
                            r'name': _log.record[r'thread'].name,
                        },
                        r'level': {
                            r'no': _log.record[r'level'].no,
                            r'name': _log.record[r'level'].name,
                        },
                        r'module': f"{_log.record[r'name']}:{_log.record[r'function']}:{_log.record[r'line']}",
                        r'message': _log.record[r'message'],
                        r'timestamp': int(_log.record[r'time'].timestamp() * 1000),
                    }
                ),
            )

            self._producer.poll(0)

        self._producer.flush()


class ElasticsearchDataStreamUtil:

    def __init__(
            self, elasticsearch: typing.Union[Elasticsearch, AsyncElasticsearch],
            stream_name: str, properties: typing.Dict, *,
            timestamp_field: str = r'@timestamp', timestamp_order: str = r'desc',
            rollover_max_age: str = r'7d', rollover_max_primary_shard_size: str = r'50gb', delete_min_age: str = r'30d',
            refresh_interval: str = r'5s', number_of_replicas=0
    ):

        self._elasticsearch: typing.Union[Elasticsearch, AsyncElasticsearch] = elasticsearch

        self._stream_name: str = stream_name
        self._policy_name: str = f'{stream_name}-ilm-policy'

        self._properties: typing.Dict = copy.deepcopy(properties)
        self._properties[r'@timestamp'] = {r'type': r'date'}

        self._rollover_max_age: str = rollover_max_age
        self._rollover_max_primary_shard_size: str = rollover_max_primary_shard_size

        self._delete_min_age: str = delete_min_age
        self._refresh_interval: str = refresh_interval
        self._number_of_replicas: int = number_of_replicas

        self._timestamp_field: str = timestamp_field
        self._timestamp_order: str = timestamp_order

    @contextmanager
    def _file_lock(self):

        if not os.path.exists(r'./.cache'):
            os.makedirs(r'./.cache')

        with FileLock(f'./.cache/log.{self._stream_name}.lock'):
            yield

    def initialize(self):

        with self._file_lock():
            self.create_lifecycle()
            self.create_index_template()

    def create_lifecycle(self):

        try:
            self._elasticsearch.ilm.get_lifecycle(name=self._policy_name)
        except ESNotFoundError as _:
            self._create_lifecycle()
        except ESApiError as err:
            sys.stderr.write(f'create lifecycle error: {str(err.info)}\n')

    def _create_lifecycle(self) -> typing.Any:

        policy = {
            r'phases': {
                r'hot': {
                    r'actions': {
                        r'rollover': {
                            r'max_age': self._rollover_max_age,
                            r'max_primary_shard_size': self._rollover_max_primary_shard_size,
                        },
                        r'set_priority': {
                            r'priority': 100,
                        }
                    },
                    r'min_age': r'0ms',
                },
                r'delete': {
                    r'actions': {
                        r'delete': {}
                    },
                    r'min_age': self._delete_min_age,
                },
            },
        }

        return self._elasticsearch.ilm.put_lifecycle(name=self._policy_name, policy=policy)

    def create_index_template(self):

        try:
            self._elasticsearch.indices.get_index_template(name=self._stream_name)
        except ESNotFoundError as _:
            self._create_index_template()
        except ESApiError as err:
            sys.stderr.write(f'{str(err.info)}\n')

    def _create_index_template(self) -> typing.Any:

        mappings = {
            r'dynamic': r'strict',
            r'properties': self._properties,
        }

        template = {
            r'settings': {
                r'index': {
                    r'lifecycle': {
                        r'name': self._policy_name,
                    },
                    r'refresh_interval': self._refresh_interval,
                    r'number_of_replicas': self._number_of_replicas,
                    r'sort': {
                        r'field': self._timestamp_field,
                        r'order': self._timestamp_order,
                    }
                },
            },
            r'mappings': mappings,
        }

        return self._elasticsearch.indices.put_index_template(
            name=self._stream_name,
            template=template,
            index_patterns=[f'{self._stream_name}*'],
            data_stream={},
        )


class AsyncElasticsearchDataStreamUtil(ElasticsearchDataStreamUtil):

    async def initialize(self):

        with self._file_lock():
            await self.create_lifecycle()
            await self.create_index_template()

    async def create_lifecycle(self):

        try:
            await self._elasticsearch.ilm.get_lifecycle(name=self._policy_name)
        except ESNotFoundError as _:
            await self._create_lifecycle()
        except ESApiError as err:
            sys.stderr.write(f'{str(err.info)}\n')

    async def create_index_template(self):

        try:
            await self._elasticsearch.indices.get_index_template(name=self._stream_name)
        except ESNotFoundError as _:
            await self._create_index_template()
        except ESApiError as err:
            sys.stderr.write(f'{str(err.info)}\n')


class ElasticsearchSink(_BaseSink):
    """Elasticsearch日志投递
    """

    def __init__(
            self, hosts: typing.Any, stream_name: str, *,
            log_maxsize: int = 0xfff, buffer_maxsize: int = 0xfff, bulk_maxsize: int = 0x800, write_max_delay: int = 5,
            rollover_max_age: str = r'7d', rollover_max_primary_shard_size: str = r'50gb', delete_min_age: str = r'30d',
            refresh_interval: str = r'5s', number_of_replicas=0,
            **kwargs):

        super().__init__(log_maxsize, buffer_maxsize, bulk_maxsize, write_max_delay)

        self._stream_name: str = stream_name

        self._elasticsearch: Elasticsearch = Elasticsearch(hosts, **kwargs)

        properties = {
            r'extra': {
                r'type': r'flattened',
            },
            r'process': {
                r'properties': {
                    r'id': {
                        r'type': r'keyword',
                    },
                    r'name': {
                        r'type': r'keyword',
                        r'ignore_above': 64,
                    },
                },
            },
            r'thread': {
                r'properties': {
                    r'id': {
                        r'type': r'keyword',
                    },
                    r'name': {
                        r'type': r'keyword',
                        r'ignore_above': 64,
                    },
                },
            },
            r'level': {
                r'properties': {
                    r'no': {
                        r'type': r'integer',
                    },
                    r'name': {
                        r'type': r'keyword',
                        r'ignore_above': 64,
                    },
                },
            },
            r'module': {
                r'type': r'text',
                r'norms': False,
            },
            r'message': {
                r'type': r'text',
                r'norms': False,
            },
            r'@timestamp': {
                r'type': r'date',
            }
        }

        ElasticsearchDataStreamUtil(
            self._elasticsearch, stream_name, properties,
            timestamp_field=r'@timestamp',
            timestamp_order=r'desc',
            rollover_max_age=rollover_max_age,
            rollover_max_primary_shard_size=rollover_max_primary_shard_size,
            delete_min_age=delete_min_age,
            refresh_interval=refresh_interval,
            number_of_replicas=number_of_replicas,
        ).initialize()

    def _write_logs(self, logs: typing.List['loguru.Message']):

        es_helpers.bulk(
            self._elasticsearch,
            actions=[
                {
                    r'_op_type': r'create',
                    r'_index': self._stream_name,
                    r'extra': _log.record[r'extra'],
                    r'process': {
                        r'id': _log.record[r'process'].id,
                        r'name': _log.record[r'process'].name,
                    },
                    r'thread': {
                        r'id': _log.record[r'thread'].id,
                        r'name': _log.record[r'thread'].name,
                    },
                    r'level': {
                        r'no': _log.record[r'level'].no,
                        r'name': _log.record[r'level'].name,
                    },
                    r'module': f"{_log.record[r'name']}:{_log.record[r'function']}:{_log.record[r'line']}",
                    r'message': _log.record[r'message'],
                    r'@timestamp': int(_log.record[r'time'].timestamp() * 1000),
                }
                for _log in logs
            ]
        )


DEFAULT_LOG_FILE_NAME = r'runtime_{time}.log'


def init_logger(
        level: str, *, handler: typing.Optional[logging.Handler] = None,
        file_path: typing.Optional[str] = None, file_name: str = DEFAULT_LOG_FILE_NAME,
        file_rotation: typing.Callable = DEFAULT_LOG_FILE_ROTATOR, file_retention: int = 0xff,
        extra: typing.Optional[typing.Dict] = None, enqueue: bool = False, debug: bool = False
):

    level = level.upper()

    Utils.log.remove()

    if extra is not None:

        extra = {_key: _val for _key, _val in extra.items() if _val is not None}

        if extra:
            Utils.log.configure(extra=extra)

    if handler or file_path:

        if handler:
            Utils.log.add(
                handler,
                level=level,
                enqueue=enqueue,
                backtrace=debug
            )

        if file_path:

            _file_name, _file_ext_name = os.path.splitext(file_name)

            Utils.log.add(
                QueuedFileSink(
                    Utils.path.join(file_path, _file_name + '.pid-' + str(Utils.getpid()) + _file_ext_name),
                    rotation=file_rotation,
                    retention=file_retention
                ),
                level=level,
                enqueue=enqueue,
                backtrace=debug
            )

    else:

        Utils.log.add(
            sys.stdout,
            level=level,
            enqueue=enqueue,
            backtrace=debug
        )

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(InterceptHandler())
