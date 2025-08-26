# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import time
import signal
import typing

from multiprocessing import Process, set_start_method
from multiprocessing.shared_memory import SharedMemory

from .base import Utils
from .interface import ContextManager, RunnableInterface
from .struct import ByteArrayAbstract


set_start_method(r'spawn', force=True)


def fork_processes() -> int:

    pid = os.fork()

    if pid == 0:
        Utils.urandom_seed()

    return pid


class Daemon(RunnableInterface):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *,
            cpu_affinity: bool = False, join_timeout: int = 10, **kwargs
    ):

        self._target: typing.Callable = target
        self._kwargs: typing.Dict = kwargs

        self._sub_process: typing.Set = set()
        self._sub_process_num: int = sub_process_num

        self._cpu_affinity: bool = cpu_affinity
        self._join_timeout: int = join_timeout

        signal.signal(signal.SIGINT, self._kill_process)
        signal.signal(signal.SIGTERM, self._kill_process)

        if self._cpu_affinity and sub_process_num > os.cpu_count():
            raise Exception(r'The number of processes exceeds the number of CPU cores')

    def _fill_process(self):

        for idx in range(self._sub_process_num - len(self._sub_process)):

            process = Process(target=self._target, args=(idx,), kwargs=self._kwargs)
            process.start()

            self._sub_process.add(process)

        if self._cpu_affinity:

            for _idx, _process in enumerate(self._sub_process):
                os.sched_setaffinity(_process.pid, [_idx])
                Utils.log.info(f'process {_process.pid} affinity: {os.sched_getaffinity(_process.pid)}')

    def _kill_process(self, *_):

        for process in self._sub_process:
            os.kill(process.ident, signal.SIGINT)

        for process in self._sub_process:
            process.join(self._join_timeout)
            process.kill()

    def _check_process(self):

        for process in self._sub_process.copy():

            if process.is_alive():
                continue

            self._sub_process.remove(process)
            Utils.log.warning(f'kill process {process.ident}')

        return len(self._sub_process) > 0

    def run(self):

        self._fill_process()

        while self._check_process():
            time.sleep(1)


class SharedByteArray(ByteArrayAbstract, ContextManager):

    def __init__(self, name: typing.Optional[str] = None, create: bool = False, size: int = 0):

        ByteArrayAbstract.__init__(self)

        self._shared_memory: SharedMemory = SharedMemory(name, create, size)
        self._create_mode: bool = create

    def _context_release(self):

        self.release()

    def release(self):

        self._shared_memory.close()

        if self._create_mode:
            self._shared_memory.unlink()

    def read(self, size: int) -> memoryview:
        return self._shared_memory.buf[:size]

    def write(self, buffer: memoryview):
        self._shared_memory.buf[:len(buffer)] = buffer
