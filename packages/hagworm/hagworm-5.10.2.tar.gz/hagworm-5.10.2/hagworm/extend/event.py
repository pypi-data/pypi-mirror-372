# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from .base import Utils, FuncWrapper


class EventDispatcher:
    """事件总线
    """

    def __init__(self):

        self._observers: typing.Dict[str, FuncWrapper] = {}

    def _gen_observer(self) -> FuncWrapper:

        return FuncWrapper()

    def dispatch(self, _type: str, *args, **kwargs):

        if _type in self._observers:
            self._observers[_type](*args, **kwargs)

    def add_listener(self, _type: str, _callable: typing.Callable) -> bool:

        Utils.log.debug(f'add event listener => type({_type}) function({id(_callable)})')

        if _type in self._observers:
            return self._observers[_type].add(_callable)
        else:
            observer = self._observers[_type] = self._gen_observer()
            return observer.add(_callable)

    def remove_listener(self, _type: str, _callable: typing.Callable) -> bool:

        Utils.log.debug(f'remove event listener => type({_type}) function({id(_callable)})')

        result = False

        if _type in self._observers:

            observer = self._observers[_type]

            result = observer.remove(_callable)

            if not observer.is_valid:
                del self._observers[_type]

        return result
