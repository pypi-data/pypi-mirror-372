# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import abc
import time
import math
import typing
import itertools
import pandas

from texttable import Texttable

from ..extend.base import Utils
from ..extend.asyncio.socket import recv_msg, DEFAULT_UNIX_SOCKET_ENDPOINT
from ..extend.asyncio.command import MainProcessWithIPC, SubProcessWithIPC


class TimerMS:

    __slots__ = [r'_initial', r'_consume']

    def __init__(self):
        self._initial: float = time.monotonic()
        self._consume: float = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.done()

    def done(self):
        self._consume = (time.monotonic() - self._initial) * 1000

    @property
    def value(self) -> float:
        return self._consume


class RunnerAbstract(SubProcessWithIPC):

    @abc.abstractmethod
    async def _execute(self):
        """
        实际测试的业务逻辑
        """

    async def success(self, name: str, resp_time: typing.Union[int, float]):

        await self._socket_client.send_msg(
            [name, True, resp_time]
        )

    async def failure(self, name: str, resp_time: typing.Union[int, float]):

        await self._socket_client.send_msg(
            [name, False, resp_time]
        )


class Launcher(MainProcessWithIPC):

    def __init__(
            self, target: typing.Callable, sub_process_num: int, *args,
            time_unit: str = r'ms', shard_table_bins: typing.List[float] = None,
            unix_socket_path: str = DEFAULT_UNIX_SOCKET_ENDPOINT, **kwargs
    ):

        super().__init__(target, sub_process_num, *args, unix_socket_path=unix_socket_path, **kwargs)

        self._data_frame: pandas.DataFrame = pandas.DataFrame(
            columns=[r'name', r'success', r'response_time']
        )

        self._time_unit: str = time_unit

        self._shard_table_bins: typing.List[float] = shard_table_bins if shard_table_bins else list(range(0, 100, 20))
        self._shard_table_bins.append(math.inf)

    async def _client_connected_cb(self, reader, writer):

        while True:

            request = await recv_msg(reader)

            if request:
                self._data_frame.loc[self._data_frame.size] = request
            else:
                break

    def _get_base_table(self) -> str:

        table = Texttable(max_width=0)

        table.header(
            [
                r'Event Name',
                r'Success Total',
                r'Failure Total',
                r'Success Ratio',
                r'Success Ave',
                r'Success Std',
                r'Success Min',
                r'Success Max',
            ]
        )

        for _name, _data_frame in self._data_frame.groupby(self._data_frame.name):

            _success_data_frame = _data_frame[_data_frame.apply(lambda x: x[r'success'], axis=1)]
            _failure_data_frame = _data_frame[_data_frame.apply(lambda x: not x[r'success'], axis=1)]

            table.add_row(
                [
                    _name,
                    _success_data_frame.shape[0],
                    _failure_data_frame.shape[0],
                    r'{:.2%}'.format(_success_data_frame.shape[0] / max(_data_frame.shape[0], 1)),
                    r'{:.3f}{}'.format(_success_data_frame[r'response_time'].mean(), self._time_unit),
                    r'{:.3f}'.format(_success_data_frame[r'response_time'].std()),
                    r'{:.3f}{}'.format(_success_data_frame[r'response_time'].min(), self._time_unit),
                    r'{:.3f}{}'.format(_success_data_frame[r'response_time'].max(), self._time_unit),
                ]
            )

        return table.draw()

    def _get_series_table(self) -> str:

        table = Texttable(max_width=0)

        labels = [f'{v1}-{v2}({self._time_unit})' for v1, v2 in itertools.pairwise(self._shard_table_bins)]

        table.header([r'Event Name'] + labels)

        for _name, _data_frame in self._data_frame[
            self._data_frame.apply(lambda x: x[r'success'], axis=1)
        ].groupby(self._data_frame.name):

            _series = pandas.cut(
                _data_frame[r'response_time'], self._shard_table_bins, labels=labels, retbins=True
            )[0].value_counts(sort=False, normalize=True)

            _rows = [_name]

            for _label in labels:
                _rows.append(
                    r'{:.2%}'.format(_series.get(_label, 0))
                )

            table.add_row(_rows)

        return table.draw()

    async def _execute(self):

        with TimerMS() as timer:
            await super()._execute()

        _time = max(round(timer.value / 1000), 1)
        _count = self._data_frame.shape[0]

        Utils.log.info(
            f'\nTotal: {_count}, Time: {_time}s, Qps: {round(_count / _time)}'
            f'\n{self._get_base_table()}\nSuccess Data Distribution\n{self._get_series_table()}\n'
        )
