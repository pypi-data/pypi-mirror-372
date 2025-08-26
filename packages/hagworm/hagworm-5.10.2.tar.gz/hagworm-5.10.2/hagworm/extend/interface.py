# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import logging
import traceback

from abc import ABC, abstractmethod

from .error import Ignore


class RunnableInterface(ABC):
    """Runnable接口定义
    """

    @abstractmethod
    def run(self, *args, **kwargs):
        """
        逻辑实现
        """


class TaskInterface(ABC):
    """Task接口定义
    """

    @abstractmethod
    def start(self, *args, **kwargs):
        """
        运行任务
        """

    @abstractmethod
    def stop(self, *args, **kwargs):
        """
        停止任务
        """

    @abstractmethod
    def is_running(self, *args, **kwargs):
        """
        是否运行中
        """


class ContextManager(ABC):
    """上下文资源管理器

    子类通过实现_context_release接口，方便的实现with语句管理上下文资源释放

    """

    def __enter__(self):

        self._context_initialize()

        return self

    def __exit__(self, exc_type, exc_value, _traceback):

        self._context_release()

        if exc_type and issubclass(exc_type, Ignore):

            return not exc_value.throw()

        elif exc_value:

            logging.error(traceback.format_exc())

            return True

    def _context_initialize(self):
        pass

    @abstractmethod
    def _context_release(self):
        """
        上下文退出，资源释放
        """


class AsyncContextManager(ABC):
    """异步上下文资源管理器

    子类通过实现_context_release接口，方便的实现with语句管理上下文资源释放

    """

    async def __aenter__(self):

        await self._context_initialize()

        return self

    async def __aexit__(self, exc_type, exc_value, _traceback):

        await self._context_release()

        if exc_type and issubclass(exc_type, Ignore):

            return not exc_value.throw()

        elif exc_value:

            logging.error(traceback.format_exc())

            return True

    async def _context_initialize(self):
        pass

    @abstractmethod
    async def _context_release(self):
        """
        异步上下文退出，资源释放
        """
