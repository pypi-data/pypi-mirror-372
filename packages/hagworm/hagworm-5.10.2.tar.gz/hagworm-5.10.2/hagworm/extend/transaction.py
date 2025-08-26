# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from abc import ABCMeta, abstractmethod

from .base import Utils
from .interface import ContextManager


class TransactionAbstract(metaclass=ABCMeta):
    """事务接口
    """

    def __init__(
            self, *,
            commit_callback: typing.Optional[typing.Callable] = None,
            rollback_callback: typing.Optional[typing.Callable] = None
    ):

        self._commit_callbacks: typing.List[typing.Callable] = []
        self._rollback_callbacks: typing.List[typing.Callable] = []

        if commit_callback is not None:
            self._commit_callbacks.append(commit_callback)

        if rollback_callback is not None:
            self._rollback_callbacks.append(rollback_callback)

    def _clear_callbacks(self):

        self._commit_callbacks.clear()
        self._rollback_callbacks.clear()

        self._commit_callbacks = self._rollback_callbacks = None

    def add_commit_callback(self, _callable: typing.Callable, *args, **kwargs):

        if self._commit_callbacks is None:
            return

        if args or kwargs:
            self._commit_callbacks.append(
                Utils.func_partial(_callable, *args, **kwargs)
            )
        else:
            self._commit_callbacks.append(_callable)

    def add_rollback_callback(self, _callable: typing.Callable, *args, **kwargs):

        if self._rollback_callbacks is None:
            return

        if args or kwargs:
            self._rollback_callbacks.append(
                Utils.func_partial(_callable, *args, **kwargs)
            )
        else:
            self._rollback_callbacks.append(_callable)

    @abstractmethod
    def commit(self):
        """
        提交事务
        """

    @abstractmethod
    def rollback(self):
        """
        回滚事务
        """

    def bind(self, trx: 'TransactionAbstract'):

        self.add_commit_callback(trx.commit)
        self.add_rollback_callback(trx.rollback)


class Transaction(TransactionAbstract, ContextManager):
    """事务对象

    使用上下文实现的一个事务对象，可以设置commit和rollback回调
    未显示commit的情况下，会自动rollback

    """

    def _context_release(self):

        self.rollback()

    def commit(self):

        if self._commit_callbacks is None:
            return

        callbacks = self._commit_callbacks.copy()

        self._clear_callbacks()

        for _callable in callbacks:
            try:
                _callable()
            except Exception as err:
                Utils.log.critical(f'transaction commit error:\n{err}')

    def rollback(self):

        if self._rollback_callbacks is None:
            return

        callbacks = self._rollback_callbacks.copy()

        self._clear_callbacks()

        for _callable in callbacks:
            try:
                _callable()
            except Exception as err:
                Utils.log.critical(f'transaction rollback error:\n{err}')
