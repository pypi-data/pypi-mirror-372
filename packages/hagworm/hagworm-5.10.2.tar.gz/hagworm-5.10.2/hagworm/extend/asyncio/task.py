# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import pytz
import typing
import asyncio
import logging

from datetime import datetime
from abc import abstractmethod
from coredis import PureToken

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.job import Job

from ..interface import TaskInterface

from .base import Utils
from .redis import RedisPool, RedisClusterPool


DEFAULT_SCHEDULER_TIMEZONE = pytz.timezone(r'Asia/Shanghai')

DEFAULT_SCHEDULER_CONFIG = {
    r'job_defaults': {
        r'coalesce': False,
        r'max_instances': 1,
        r'misfire_grace_time': 10
    },
    r'timezone': DEFAULT_SCHEDULER_TIMEZONE
}

logging.getLogger(r'apscheduler').setLevel(logging.ERROR)


class TaskAbstract(TaskInterface):
    """任务基类
    """

    def __init__(self, scheduler: typing.Optional[AsyncIOScheduler] = None):
        self._scheduler: AsyncIOScheduler = AsyncIOScheduler(
            **DEFAULT_SCHEDULER_CONFIG
        ) if scheduler is None else scheduler

    @property
    def scheduler(self) -> AsyncIOScheduler:
        return self._scheduler

    def start(self):
        if not self._scheduler.running:
            self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown()

    def is_running(self):
        return self._scheduler.running

    @abstractmethod
    def add_job(self, *args, **kwargs) -> Job:
        """
        添加任务
        """

    def remove_job(self, job_id):
        self._scheduler.remove_job(job_id)

    def remove_all_jobs(self):
        self._scheduler.remove_all_jobs()


class IntervalTask(TaskAbstract):
    """间隔任务类
    """

    @classmethod
    def create(cls, interval: int, func: typing.Callable, *func_args, **func_kwargs) -> 'IntervalTask':

        inst = cls()

        inst.add_job(interval, func, args=func_args, kwargs=func_kwargs)

        return inst

    def add_job(self, interval: int, func: typing.Callable, *args, **kwargs) -> Job:
        return self._scheduler.add_job(
            func, r'interval', *args, seconds=interval, next_run_time=datetime.now(), **kwargs
        )


class CronTask(TaskAbstract):
    """定时任务类
    """

    @classmethod
    def create(cls, crontab: str, func: typing.Callable, *func_args, **func_kwargs) -> 'CronTask':

        inst = cls()

        inst.add_job(crontab, func, args=func_args, kwargs=func_kwargs)

        return inst

    def add_job(self, crontab: str, func: typing.Callable, *args, **kwargs) -> Job:
        return self._scheduler.add_job(
            func, CronTrigger.from_crontab(crontab, DEFAULT_SCHEDULER_TIMEZONE), *args, **kwargs
        )


class DCSCronTask(TaskInterface):

    def __init__(
            self,
            redis_client: typing.Union[RedisPool, RedisClusterPool],
            name: str,
            crontab: str,
            func: typing.Callable,
            *args, **kwargs
    ):

        self._redis_client: typing.Union[RedisPool, RedisClusterPool] = redis_client

        self._name: str = name
        self._task_func: typing.Callable = func
        self._cron_task: CronTask = CronTask.create(crontab, self._do_job, *args, **kwargs)

    async def _do_job(self, *args, **kwargs):

        key = self._redis_client.get_safe_key(
            r'dcs_cron', self._name, Utils.stamp2time(format_type=r'%Y%m%d%H%M')
        )

        if await self._redis_client.set(key, self._name, condition=PureToken.NX, ex=3600):

            Utils.log.info(f'dcs cron task start: {self._name}')

            if Utils.is_coroutine_function(self._task_func):
                await self._task_func(*args, **kwargs)
            else:
                self._task_func(*args, **kwargs)

            Utils.log.info(f'dcs cron task finish: {self._name}')

        else:

            Utils.log.debug(f'dcs cron task idle: {self._name}')

    def start(self):
        self._cron_task.start()
        Utils.log.info(f'dcs cron task init: {self._name}')

    def stop(self):
        self._cron_task.stop()

    def is_running(self) -> bool:
        return self._cron_task.is_running()


class MultiTasks:
    """多任务并发管理器

    提供协程的多任务并发的解决方案, 通过参数tasks_num控制队列长度

    tasks = MultiTasks()
    tasks.append(func1())
    tasks.append(func2())
    ...
    tasks.append(funcN())
    await tasks

    """

    def __init__(self, tasks_num: int = 10) -> None:

        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max(1, tasks_num))

        self._coroutines: typing.List[typing.Coroutine] = []

    def __await__(self) -> typing.List[typing.Any]:

        result = None

        if len(self._coroutines) > 0:

            tasks = [self._do_task(_task) for _task in self._coroutines]

            result = yield from asyncio.gather(*tasks).__await__()

            self._coroutines.clear()

        return result

    async def _do_task(self, coroutine: typing.Coroutine) -> typing.Any:

        async with self._semaphore:
            return await coroutine

    def append(self, coroutine: typing.Coroutine):
        return self._coroutines.append(coroutine)

    def extend(self, coroutines: typing.List[typing.Coroutine]):
        return self._coroutines.extend(coroutines)


class RateLimiter:
    """流量控制器，用于对计算资源的保护
    进入队列的任务，如果触发限流行为会通过在Future上引发CancelledError传递出来
    """

    def __init__(self, task_limit: int, wait_limit: int = 256, timeout: int = 60):

        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max(1, task_limit))

        self._task_queue: asyncio.Queue[
            typing.Tuple[typing.Callable, typing.Optional[asyncio.Future], float]
        ] = asyncio.Queue(wait_limit)

        self._timeout: int = max(1, timeout)

        self._consume_task: asyncio.Task = asyncio.create_task(self._do_consume_task())

    async def _put_task_queue(
            self, func: typing.Callable, func_args: typing.Tuple, func_kwargs: typing.Dict,
            future: typing.Optional[asyncio.Future] = None
    ) -> bool:

        if not Utils.is_coroutine_function(func):
            raise TypeError('must be a coroutine function')

        if not func_args and not func_kwargs:
            _func = func
        else:
            _func = Utils.func_partial(func, *func_args, **func_kwargs)

        await asyncio.wait_for(
            self._task_queue.put((_func, future, Utils.loop_time())),
            self._timeout
        )

        return True

    def _create_task(self, func: typing.Callable, future: typing.Optional[asyncio.Future]):

        task = asyncio.create_task(func())
        task.add_done_callback(lambda _ : self._task_queue.task_done())
        task.add_done_callback(lambda _ : self._semaphore.release())

        if future is not None:
            task.add_done_callback(lambda _: future.set_result(task.result()))

    async def _do_consume_task(self):

        while True:

            future = None

            try:

                await self._semaphore.acquire()

                func, future, join_time = await self._task_queue.get()
                self._task_queue.task_done()

                if (Utils.loop_time() - join_time) > self._timeout:
                    raise TimeoutError(f'timeout')

                self._create_task(func, future)

            except Exception as err:

                Utils.log.error(f'rate limit error: {str(err)}')

                if future is not None:
                    future.set_exception(err)

    def size(self) -> int:
        return self._task_queue.qsize()

    def close(self):
        self._consume_task.cancel()

    async def join(self):
        await self._task_queue.join()

    async def append(self, func: typing.Callable, *args, **kwargs) -> bool:

        result = False

        try:
            result = await self._put_task_queue(func, args, kwargs)
        except Exception as err:
            Utils.log.error(str(err))

        return result

    async def call(self, func: typing.Callable, *args, **kwargs) -> typing.Any:

        future = asyncio.Future()

        try:
            await self._put_task_queue(func, args, kwargs, future)
        except Exception as err:
            Utils.log.error(str(err))
            future.set_exception(err)

        return await future
