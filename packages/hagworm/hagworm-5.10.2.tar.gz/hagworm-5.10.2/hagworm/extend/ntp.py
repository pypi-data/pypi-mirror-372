# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import time
import pandas

from datetime import datetime
from ntplib import NTPClient as _NTPClient
from apscheduler.schedulers.background import BackgroundScheduler

from hagworm.extend.base import Utils
from hagworm.extend.error import catch_error
from hagworm.extend.asyncio.task import DEFAULT_SCHEDULER_CONFIG


class NTPClient:
    """异步NTP客户端类
    """

    def __init__(
            self, host: str = r'time.windows.com', *,
            version: int = 4, port: str = r'ntp', timeout: int = 5,
            interval: int = 3600, sampling: int = 5
    ):

        self._client: _NTPClient = _NTPClient()
        self._offset: float = 0
        self._sampling: int = sampling

        self._scheduler: BackgroundScheduler = BackgroundScheduler(**DEFAULT_SCHEDULER_CONFIG)

        self._scheduler.add_job(
            self._do_task, 'interval',
            (host, version, port, timeout),
            seconds=interval, next_run_time=datetime.now()
        )

    def start(self):
        if not self._scheduler.running:
            self._scheduler.start()

    def stop(self):
        if self._scheduler.running:
            self._scheduler.shutdown()

    def _do_task(self, host: str, version: int, port: str, timeout: int):

        with catch_error():

            samples = []

            # 多次采样取中位数，减少抖动影响
            for _ in range(self._sampling):
                try:
                    _response = self._client.request(host, version, port, timeout)
                    samples.append(_response.offset)
                except Exception as err:
                    Utils.log.error(f'NTP server {host} request error: {str(err)}')

            if samples:
                self._offset = pandas.Series(samples).median()
                Utils.log.info(f'NTP server {host} offset median {self._offset} samples: {samples}')
            else:
                Utils.log.error(f'NTP server {host} not available, timestamp uncalibrated')

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def timestamp(self) -> float:
        return time.time() + self._offset

    @property
    def timestamp_ms(self) -> int:
        return round((time.time() + self._offset) * 1000)
