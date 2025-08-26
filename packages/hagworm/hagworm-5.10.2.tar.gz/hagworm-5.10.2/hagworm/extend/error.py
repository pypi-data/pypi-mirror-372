# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import traceback

from loguru import logger
from contextlib import contextmanager


class Ignore(Exception):
    """可忽略的异常

    用于with语句块跳出，或者需要跳出多层逻辑的情况

    """

    def __init__(self, *args, layers=1):

        super().__init__(*args)

        self._layers = layers

    def log(self):

        if info := str(self):
            logger.warning(info)

    def throw(self):

        if self._layers > 0:
            self._layers -= 1

        return self._layers != 0


@contextmanager
def catch_warning():
    """异常捕获，打印warning级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    # noinspection PyBroadException
    try:
        yield
    except Ignore as err:
        err.log()
        if err.throw():
            raise err
    except Exception as _:
        logger.warning(traceback.format_exc())


@contextmanager
def catch_error():
    """异常捕获，打印error级日志

    通过with语句捕获异常，代码更清晰，还可以使用Ignore异常安全的跳出with代码块

    """

    # noinspection PyBroadException
    try:
        yield
    except Ignore as err:
        err.log()
        if err.throw():
            raise err
    except Exception as _:
        logger.error(traceback.format_exc())
