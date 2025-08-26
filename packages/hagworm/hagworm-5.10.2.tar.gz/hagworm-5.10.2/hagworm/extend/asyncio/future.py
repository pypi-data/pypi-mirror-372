# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import signal
import typing
import asyncio
import copy
import functools
import logging

from threading import Event, Thread as _Thread
from concurrent.futures import ThreadPoolExecutor

from ..interface import RunnableInterface, TaskInterface


class WaitForever(asyncio.Future):

    def __init__(self):

        super().__init__()

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

    def _exit(self, *_):

        if not self.done():
            self.cancel()


class FutureWithTimeout(asyncio.Future):
    """带超时功能的Future
    """

    def __init__(self, delay: float, default: typing.Any = None):

        super().__init__()

        self._timeout_handle = asyncio.get_event_loop().call_later(
            delay,
            self.set_result,
            default
        )

        self.add_done_callback(self._clear_timeout)

    def _clear_timeout(self, *_):

        if self._timeout_handle is not None:
            self._timeout_handle.cancel()
            self._timeout_handle = None


class FutureWithCoroutine(asyncio.Future):
    """Future实例可以被多个协程await，本类实现Future和Coroutine的桥接
    """

    def __init__(self, coroutine: typing.Coroutine):

        super().__init__()

        self._lock = asyncio.Lock()
        self._coroutine: typing.Coroutine = coroutine

    def __await__(self) -> typing.Any:
        return (yield from self._run_coroutine().__await__())

    async def _run_coroutine(self):

        async with self._lock:

            if not self.done():

                try:
                    self.set_result(
                        await self._coroutine
                    )
                except Exception as err:
                    super().cancel()
                    raise err

        return copy.deepcopy(self.result())

    def cancel(self, *args, **kwargs):

        super().cancel()

        self._coroutine.close()


class Thread(_Thread):
    """线程内请及时检查退出标记
    """
    
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):

        super().__init__(group, target, name, args, kwargs, daemon=True)

        self._exit_event: Event = Event()

    def stop(self, timeout: int = None):

        self._exit_event.set()

        if timeout is not None:
            self.join(timeout)

    def is_stopped(self) -> bool:

        return self._exit_event.is_set()


class ThreadPool(RunnableInterface):
    """线程池，桥接线程与协程
    """

    def __init__(self, max_workers: typing.Optional[int] = None):

        self._executor = ThreadPoolExecutor(max_workers)

    async def run(self, _callable: typing.Callable, *args, **kwargs):
        """线程转协程，不支持协程函数
        """

        loop = asyncio.events.get_event_loop()

        if kwargs:

            return await loop.run_in_executor(
                self._executor,
                functools.partial(
                    _callable,
                    *args,
                    **kwargs
                )
            )

        else:

            return await loop.run_in_executor(
                self._executor,
                _callable,
                *args,
            )


class ThreadWorker:
    """通过线程转协程实现普通函数非阻塞的装饰器
    """

    def __init__(self, max_workers: typing.Optional[int] = None):

        self._thread_pool = ThreadPool(max_workers)

    def __call__(self, func: typing.Callable):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return self._thread_pool.run(func, *args, **kwargs)

        return _wrapper


class SubProcess(TaskInterface):
    """子进程管理，通过command方式启动子进程
    """

    @classmethod
    async def create(cls, program, *args, stdin=None, stdout=None, stderr=None, **kwargs):

        inst = cls(program, *args, stdin=stdin, stdout=stdout, stderr=stderr, **kwargs)
        await inst.start()

        return inst

    def __init__(
            self, program: str, *args,
            stdin: int = asyncio.subprocess.DEVNULL,
            stdout: int = asyncio.subprocess.DEVNULL,
            stderr: int= asyncio.subprocess.DEVNULL,
            **kwargs
    ):

        self._program: str = program
        self._args: typing.Tuple = args
        self._kwargs: typing.Dict = kwargs

        self._stdin: int = stdin
        self._stdout: int = stdout
        self._stderr: int = stderr

        self._process: typing.Optional['asyncio.subprocess.Process'] = None
        self._process_id: typing.Optional[int] = None

    @property
    def pid(self) -> int:
        return self._process_id

    @property
    def process(self) -> 'asyncio.subprocess.Process':
        return self._process

    @property
    def stdin(self) -> 'asyncio.streams.StreamWriter':
        return self._process.stdin

    @property
    def stdout(self) -> 'asyncio.streams.StreamReader':
        return self._process.stdout

    @property
    def stderr(self) -> 'asyncio.streams.StreamReader':
        return self._process.stderr

    def create_stdout_task(self) -> asyncio.Task:
        return asyncio.create_task(self._log_stdout())

    async def _log_stdout(self):

        stream = self._process.stdout

        while self._process.returncode is None:

            content = await stream.readline()

            if content:
                content = content.decode().strip()
                if content:
                    logging.info(content)
            else:
                break

    def create_stderr_task(self) -> asyncio.Task:

        return asyncio.create_task(self._log_stderr())

    async def _log_stderr(self):

        stream = self._process.stderr

        while self._process.returncode is None:

            content = await stream.readline()

            if content:
                content = content.decode().strip()
                if content:
                    logging.error(content)
            else:
                break

    def is_running(self) -> bool:
        return self._process is not None and self._process.returncode is None

    async def start(self) -> bool:

        if self.is_running():
            return False

        self._process = await asyncio.create_subprocess_exec(
            self._program, *self._args,
            stdin=self._stdin,
            stdout=self._stdout,
            stderr=self._stderr,
            **self._kwargs
        )

        self._process_id = self._process.pid

        return True

    async def stop(self):

        if self.is_running():
            self._process.kill()
            await self._process.wait()

    def kill(self):

        if self.is_running():
            self._process.kill()

    async def wait(self, timeout: typing.Optional[float] = None):

        if not self.is_running():
            return

        try:
            await asyncio.wait_for(self._process.wait(), timeout=timeout)
        except Exception as err:
            logging.error(err)
        finally:
            await self.stop()
