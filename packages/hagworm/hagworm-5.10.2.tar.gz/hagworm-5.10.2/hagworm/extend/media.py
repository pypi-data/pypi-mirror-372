# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from .base import Utils
from .error import catch_error


class M3U8:

    _DEFAULT_CONTENT = """#EXTM3U
#EXT-X-TARGETDURATION:{max_time}
#EXT-X-DISCONTINUITY
{content}
#EXT-X-ENDLIST"""

    def __init__(self, value: str, host: str= r''):

        self._host: str = host

        self._data: typing.List = self._parse(value)

    def __add__(self, other: 'M3U8') -> 'M3U8':

        shadow: 'M3U8' = Utils.deepcopy(self)
        shadow._data.extend(other._data)

        return shadow

    def __iadd__(self, other: 'M3U8') -> 'M3U8':

        self._data.extend(other._data)

        return self

    @staticmethod
    def _parse(value: str) -> typing.List:

        result = None

        with catch_error():

            record_list = []
            extinf_list = []

            for _line in value.strip().splitlines():

                if _line.startswith(r'#EXTINF:'):
                    extinf_list.append(float(_line.split(r':')[1].split(r',')[0]))
                elif not _line.startswith(r'#'):
                    record_list.append(_line)

            if len(extinf_list) == len(record_list):
                result = zip(record_list, extinf_list)
            else:
                raise Exception(r'parse m3u8 content error')

        return result

    def split(self, _start: int, _end: int) -> str:

        timer = 0
        max_time = 0

        infos = []

        for _url, _time in self._data:

            max_time = max(max_time, Utils.math.ceil(_time))

            _next = timer + _time

            if timer < _start and _next < _start:
                timer = _next
                continue
            elif timer > _end:
                break

            infos.append(f'#EXTINF:{_time}\n{self._host}{_url}')
            timer = _next

        return self._DEFAULT_CONTENT.format(max_time=max_time, content='\n'.join(infos))
