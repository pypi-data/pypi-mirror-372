# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import os
import re
import sys
import platform
import uuid
import time
import math
import string
import random
import hashlib
import base64
import hmac
import textwrap
import itertools
import copy
import pytz
import pickle
import psutil
import functools
import binascii
import ujson
import msgpack
import zlib
import socket
import struct
import unicodedata
import calendar
import jwt
import yaml
import loguru
import warnings
import xmltodict
import xml.dom.minidom

from datetime import datetime, timedelta
from contextlib import closing, suppress
from collections import OrderedDict
from collections.abc import Iterable
from cachetools import cached, TTLCache
from urllib.parse import urlparse
from zipfile import ZipFile, ZIP_DEFLATED

from stdnum import luhn
from dateutil.parser import parse as date_parse

from .text import StrUtils
from .. import hagworm_slogan


class Utils:
    """基础工具类

    集成常用的工具函数

    """

    _BYTES_TYPES = (bytes, type(None),)

    _STRING_TYPES = (str, type(None),)

    _FALSE_VALUES = (r'null', r'none', r'nil', r'false', r'0', r'', False, 0,)

    log = loguru.logger

    math = math
    random = random
    textwrap = textwrap
    itertools = itertools

    path = os.path

    urlparse = staticmethod(urlparse)
    deepcopy = staticmethod(copy.deepcopy)

    func_wraps = staticmethod(functools.wraps)
    func_partial = staticmethod(functools.partial)

    randint = staticmethod(random.randint)
    randstr = staticmethod(random.sample)

    getenv = staticmethod(os.getenv)
    getpid = staticmethod(os.getpid)
    getppid = staticmethod(os.getppid)

    date_parse = staticmethod(date_parse)

    suppress = staticmethod(suppress)

    @staticmethod
    def get_class_name(val: typing.Type) -> str:
        return f'{val.__module__}.{val.__name__}'

    @staticmethod
    def environment() -> typing.Dict:

        return {
            r'python': sys.version,
            r'system': [platform.system(), platform.release(), platform.version(), platform.machine()],
        }

    @staticmethod
    def print_slogan():

        environment = Utils.environment()

        Utils.log.info(
            f'{hagworm_slogan}'
            f'python {environment["python"]}\n'
            f'system {" ".join(environment["system"])}'
        )

    @staticmethod
    def deprecation_warning(val: str):
        warnings.warn(val, DeprecationWarning)

    @classmethod
    def get_node_id(cls) -> str:

        return cls.md5(f'{cls.getpid()}@{uuid.getnode()}')

    @classmethod
    def utf8(cls, val: typing.AnyStr) -> bytes:

        if isinstance(val, cls._BYTES_TYPES):
            return val

        if isinstance(val, str):
            return val.encode(r'utf-8')

        raise TypeError(
            r'Expected str, bytes, or None; got %r' % type(val)
        )

    @classmethod
    def basestring(cls, val: typing.AnyStr) -> str:

        type_ = type(val)

        if type_ in cls._STRING_TYPES:
            return val
        elif type_ is bytes:
            return val.decode(r'utf-8')
        else:
            raise TypeError(f'Expected str, bytes, or None; got {type_}')

    @classmethod
    def vague_string(
            cls, val: str,
            vague_str: str = r'*', vague_len: float = 0.5,
            min_vague: int = 1, max_vague: int = 10
    ):

        val_len = len(val)
        vague_len = max(min_vague, min(max_vague, cls.math.ceil(val_len * vague_len)))

        r_show = (val_len - vague_len) // 2
        l_show = max(1, val_len - r_show - vague_len) if val_len > min_vague else 0

        return val[:l_show] + vague_str * vague_len + val[val_len - r_show:]

    @staticmethod
    def json_encode(val: typing.Any, **kwargs):
        return ujson.dumps(val, **kwargs)

    @classmethod
    def json_decode(cls, val: typing.AnyStr, **kwargs):
        return ujson.loads(cls.basestring(val), **kwargs)

    @staticmethod
    def msgpack_encode(val: typing.Any, **kwargs):
        return msgpack.dumps(val, **kwargs)

    @staticmethod
    def msgpack_decode(val: typing.AnyStr, **kwargs):
        return msgpack.loads(val, **kwargs)

    @staticmethod
    def today() -> datetime:

        result = datetime.now()

        return result.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def yesterday() -> datetime:

        result = datetime.now() - timedelta(days=1)

        return result.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def localnow() -> datetime:

        result = datetime.now()

        return result.replace(second=0, microsecond=0)

    @staticmethod
    def localnow_on_hour() -> datetime:

        result = datetime.now()

        return result.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def utcnow() -> datetime:

        result = datetime.utcnow()

        return result.replace(second=0, microsecond=0)

    @staticmethod
    def utcnow_on_hour() -> datetime:

        result = datetime.utcnow()

        return result.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def timestamp() -> int:
        return int(time.time())

    @staticmethod
    def timestamp_ms() -> int:
        return int(time.time() * 1000)

    @classmethod
    def convert_bool(cls, val: typing.Any) -> bool:

        if isinstance(val, str):
            val = val.lower()

        return val not in cls._FALSE_VALUES

    @staticmethod
    def convert_int(val: typing.Any, default: int = 0) -> int:

        result = default

        # noinspection PyBroadException
        try:
            if not isinstance(val, float):
                result = int(val)
        except Exception as _:
            pass

        return result

    @staticmethod
    def convert_float(val: typing.Any, default: float = 0) -> float:

        result = default

        # noinspection PyBroadException
        try:
            if not isinstance(val, float):
                result = float(val)
        except Exception as _:
            pass

        return result

    @staticmethod
    def interval_limit(
            val: typing.Union[int, float],
            min_val: typing.Union[int, float],
            max_val: typing.Union[int, float]
    ) -> typing.Union[int, float]:

        result = val

        if min_val is not None:
            result = max(result, min_val)

        if max_val is not None:
            result = min(result, max_val)

        return result

    @classmethod
    def split_float(cls, val: str, sep: str = r',', min_split: int = 0, max_split: int = -1) -> typing.List[float]:

        result = [
            float(item.strip()) for item in val.split(sep, max_split)
            if cls.re_match(r'[\d\.]+', item.strip().lstrip(r'-'))
        ]

        fill = min_split - len(result)

        if fill > 0:
            result.extend(0 for _ in range(fill))

        return result

    @classmethod
    def join_float(cls, val: typing.Iterable, sep: str = r',') -> str:

        result = []

        for _v in val:

            _type = type(_v)

            if _type is float:

                result.append(str(_v))

            elif _type is str:

                _v = _v.strip()

                if cls.re_match(r'[\d\.]+', _v):
                    result.append(_v)

        return sep.join(result)

    @classmethod
    def split_int(cls, val: str, sep: str = r',', min_split: int = 0, max_split: int = -1) -> typing.List[int]:

        result = [int(item.strip()) for item in val.split(sep, max_split) if item.strip().lstrip(r'-').isdigit()]

        fill = min_split - len(result)

        if fill > 0:
            result.extend(0 for _ in range(fill))

        return result

    @classmethod
    def join_int(cls, val: typing.Iterable, sep: str = r',') -> str:

        result = []

        for _v in val:

            _type = type(_v)

            if _type is int:

                result.append(str(_v))

            elif _type is str:

                _v = _v.strip()

                if _v.isdigit():
                    result.append(_v)

        return sep.join(result)

    @classmethod
    def split_str(cls, val: str, sep: str = r'|', min_split: int = 0, max_split: int = -1) -> typing.List[str]:

        if val:
            result = [item.strip() for item in val.split(sep, max_split)]
        else:
            result = []

        fill = min_split - len(result)

        if fill > 0:
            result.extend(r'' for _ in range(fill))

        return result

    @staticmethod
    def join_str(val, sep=r'|') -> str:
        return sep.join(str(_v).replace(sep, r'') for _v in val)

    @classmethod
    def list_extend(cls, iterable: typing.List, val: typing.Any):

        if cls.is_iterable(val, True):
            iterable.extend(val)
        else:
            iterable.append(val)

    @staticmethod
    def str_len(str_val: str) -> int:

        result = 0

        for val in str_val:

            if unicodedata.east_asian_width(val) in (r'A', r'F', r'W'):
                result += 2
            else:
                result += 1

        return result

    @staticmethod
    def sub_str(val: str, length: int, suffix: str = r'...') -> str:

        result = []
        strlen = 0

        for _v in val:

            if unicodedata.east_asian_width(_v) in (r'A', r'F', r'W'):
                strlen += 2
            else:
                strlen += 1

            if strlen > length:

                if suffix:
                    result.append(suffix)

                break

            result.append(_v)

        return r''.join(result)

    @classmethod
    def re_match(cls, pattern: str, value: str) -> bool:

        result = re.match(pattern, value)

        return True if result else False

    @classmethod
    def rand_hit(cls, val: typing.List, prob: typing.Union[typing.List, typing.Callable]) -> typing.Any:

        if callable(prob):
            prob = [prob(_v) for _v in val]

        prob_sum = sum(prob)

        if prob_sum > 0:

            prob_hit = 0
            prob_sum = cls.randint(0, prob_sum)

            for index in range(0, len(prob)):

                prob_hit += prob[index]

                if prob_hit >= prob_sum:
                    return val[index]

        return cls.random.choice(val)

    @classmethod
    def urandom_seed(cls) -> int:

        seed_num = None

        # noinspection PyBroadException
        try:

            with open(r'/dev/urandom', r'rb') as f:
                seed_num = struct.unpack(f'!I', f.read(4))[0]
                random.seed(seed_num)

        except Exception as _:

            cls.log.warning(r'SYSTEM DOES NOT SUPPORT URANDOM')

        return seed_num

    @classmethod
    def read_urandom(cls, size: int) -> typing.AnyStr:

        result = None

        # noinspection PyBroadException
        try:

            with open(r'/dev/urandom', r'rb') as f:
                result = f.read(size)

        except Exception as _:

            cls.log.warning(r'SYSTEM DOES NOT SUPPORT URANDOM')

        return result

    @staticmethod
    def get_host_ip() -> str:

        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as _socket:
            _socket.connect((r'223.5.5.5', 53))
            return _socket.getsockname()[0]

    @staticmethod
    def ip2int(val: str) -> int:

        try:
            return int(binascii.hexlify(socket.inet_aton(val)), 16)
        except socket.error:
            return int(binascii.hexlify(socket.inet_pton(socket.AF_INET6, val)), 16)

    @staticmethod
    def int2ip(val: int) -> str:

        try:
            return socket.inet_ntoa(binascii.unhexlify(r'%08x' % val))
        except socket.error:
            return socket.inet_ntop(socket.AF_INET6, binascii.unhexlify(r'%032x' % val))

    @staticmethod
    def time2stamp(
            time_str: str,
            format_type: str = r'%Y-%m-%d %H:%M:%S',
            timezone: typing.Optional[str] = None
    ) -> int:

        if timezone is None:
            return int(datetime.strptime(time_str, format_type).timestamp())
        else:
            return int(datetime.strptime(time_str, format_type).replace(tzinfo=pytz.timezone(timezone)).timestamp())

    @staticmethod
    def stamp2time(
            time_int: typing.Optional[int] = None,
            format_type: str = r'%Y-%m-%d %H:%M:%S',
            timezone: typing.Optional[str] = None
    ) -> str:

        if time_int is None:
            time_int = int(time.time())

        if timezone is None:
            return time.strftime(format_type, datetime.fromtimestamp(time_int).timetuple())
        else:
            return time.strftime(format_type, datetime.fromtimestamp(time_int, pytz.timezone(timezone)).timetuple())

    @classmethod
    def radix24(cls, val: int, align: int = 0) -> str:

        base = StrUtils.SAFE_STRING_BASE

        return cls.radix_n(val, base, 24, align)

    @classmethod
    def radix24_to_10(cls, val: str) -> int:

        base = StrUtils.SAFE_STRING_BASE

        return cls.radix_n_to_10(val, base, 24)

    @classmethod
    def radix36(cls, val: int, align: int = 0) -> str:

        base = string.digits + string.ascii_uppercase

        return cls.radix_n(val, base, 36, align)

    @classmethod
    def radix36_to_10(cls, val: str) -> int:

        base = string.digits + string.ascii_uppercase

        return cls.radix_n_to_10(val, base, 36)

    @classmethod
    def radix62(cls, val: int, align: int = 0) -> str:

        base = string.digits + string.ascii_letters

        return cls.radix_n(val, base, 62, align)

    @classmethod
    def radix62_to_10(cls, val: str) -> int:

        base = string.digits + string.ascii_letters

        return cls.radix_n_to_10(val, base, 62)

    @staticmethod
    def radix_n(val: int, base: str, radix: int, align: int = 0) -> str:

        num = abs(int(val))

        result = ''

        while num > 0:
            num, rem = divmod(num, radix)
            result = base[rem] + result

        return r'{0:0>{1:d}s}'.format(result, align)

    @classmethod
    def radix_n_to_10(cls, val: str, base: str, radix: int) -> int:

        result = 0

        for _str in val.strip():
            rem = base.index(_str)
            result = result * radix + rem

        return result

    @staticmethod
    def xml_encode(dict_val: typing.Dict, root_tag: str = r'root') -> xml.dom.minidom.Document:

        xml_doc = xml.dom.minidom.Document()

        root_node = xml_doc.createElement(root_tag)
        xml_doc.appendChild(root_node)

        def _convert(_doc, _node, _dict):

            for key, val in _dict.items():

                temp = _doc.createElement(key)

                if isinstance(val, dict):
                    _convert(_doc, temp, val)
                else:
                    temp.appendChild(_doc.createTextNode(str(val)))

                _node.appendChild(temp)

        _convert(xml_doc, root_node, dict_val)

        return xml_doc

    @classmethod
    def xml_decode(cls, val: str) -> typing.Dict:
        return xmltodict.parse(cls.utf8(val))

    @classmethod
    def b32_encode(cls, val: typing.AnyStr, standard: bool = False) -> str:

        val = cls.utf8(val)

        result = base64.b32encode(val)

        if not standard:
            result = result.rstrip(b'=')

        return cls.basestring(result)

    @classmethod
    def b32_decode(cls, val: typing.AnyStr, standard: bool = False, for_bytes: bool = False) -> typing.AnyStr:

        val = cls.utf8(val)

        if not standard:

            num = len(val) % 8

            if num > 0:
                val = val + b'=' * (8 - num)

        if for_bytes:
            return base64.b32decode(val)
        else:
            return cls.basestring(base64.b32decode(val))

    @classmethod
    def b64_encode(cls, val: typing.AnyStr, standard: bool = False, for_bytes: bool = False) -> typing.AnyStr:

        val = cls.utf8(val)

        if standard:

            result = base64.b64encode(val)

        else:

            result = base64.urlsafe_b64encode(val)

            result = result.rstrip(b'=')

        if not for_bytes:
            result = cls.basestring(result)

        return result

    @classmethod
    def b64_decode(cls, val: typing.AnyStr, standard: bool = False, for_bytes: bool = False) -> typing.AnyStr:

        val = cls.utf8(val)

        if standard:

            result = base64.b64decode(val)

        else:

            num = len(val) % 4

            if num > 0:
                val = val + b'=' * (4 - num)

            result = base64.urlsafe_b64decode(val)

        if for_bytes:
            return result
        else:
            return cls.basestring(result)

    @classmethod
    def jwt_encode(cls, val: str, key: str, algorithms: str = r'HS256') -> str:

        result = jwt.encode(val, key, algorithms)

        return cls.basestring(result)

    @classmethod
    def jwt_decode(cls, val: str, key: str, algorithms: str = r'HS256') -> str:

        val = cls.utf8(val)

        return jwt.decode(val, key, algorithms)

    @staticmethod
    def yaml_encode(data: typing.Any, stream: typing.Any = None):
        return yaml.safe_dump(data, stream)

    @staticmethod
    def yaml_decode(stream: typing.Any) -> typing.Any:
        return yaml.safe_load(stream)

    @staticmethod
    def pickle_dumps(val: typing.Any) -> bytes:

        stream = pickle.dumps(val)

        return zlib.compress(stream)

    @staticmethod
    def pickle_loads(val: bytes) -> typing.Any:

        stream = zlib.decompress(val)

        return pickle.loads(stream)

    @staticmethod
    def uuid1(node: typing.Optional[str] = None, clock_seq: typing.Optional[str] = None) -> str:
        return uuid.uuid1(node, clock_seq).hex

    @staticmethod
    def uuid1_urn(node: typing.Optional[str] = None, clock_seq: typing.Optional[str] = None) -> str:
        return str(uuid.uuid1(node, clock_seq))

    @classmethod
    def crc32(cls, val: typing.AnyStr) -> int:
        return binascii.crc32(cls.utf8(val))

    @classmethod
    def md5(cls, val: typing.AnyStr) -> str:
        return hashlib.md5(cls.utf8(val)).hexdigest()

    @classmethod
    def md5_u32(cls, val: typing.AnyStr) -> int:
        return int(hashlib.md5(cls.utf8(val)).hexdigest(), 16) >> 96

    @classmethod
    def md5_u64(cls, val: typing.AnyStr) -> int:
        return int(hashlib.md5(cls.utf8(val)).hexdigest(), 16) >> 64

    @classmethod
    def sha1(cls, val: typing.AnyStr) -> str:
        return hashlib.sha1(cls.utf8(val)).hexdigest()

    @classmethod
    def sha256(cls, val: typing.AnyStr) -> str:
        return hashlib.sha256(cls.utf8(val)).hexdigest()

    @classmethod
    def sha512(cls, val: typing.AnyStr) -> str:
        return hashlib.sha512(cls.utf8(val)).hexdigest()

    @classmethod
    def hmac_md5(cls, key: typing.AnyStr, data: typing.AnyStr, b64_std: bool = False) -> str:

        _hmac = hmac.new(cls.utf8(key), cls.utf8(data), r'md5').digest()

        return cls.basestring(cls.b64_encode(_hmac, b64_std))

    @classmethod
    def hmac_sha1(cls, key: typing.AnyStr, data: typing.AnyStr, b64_std: bool = False) -> str:

        _hmac = hmac.new(cls.utf8(key), cls.utf8(data), r'sha1').digest()

        return cls.basestring(cls.b64_encode(_hmac, b64_std))

    @staticmethod
    def ordered_dict(val: typing.Optional[typing.Dict] = None) -> OrderedDict:

        if val is None:
            return OrderedDict()
        else:
            return OrderedDict(sorted(val.items(), key=lambda x: x[0]))

    @staticmethod
    def is_iterable(obj: typing.Any, standard: bool = False) -> bool:

        if standard:
            return isinstance(obj, Iterable)
        else:
            return isinstance(obj, (list, tuple,))

    @staticmethod
    def luhn_valid(val: str) -> bool:
        return luhn.is_valid(val)

    @staticmethod
    def luhn_sign(val: str) -> str:
        return val + luhn.calc_check_digit(val)

    @staticmethod
    def identity_card(val: str) -> bool:

        result = False

        val = val.strip().upper()

        if len(val) == 18:

            weight_factor = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1,)

            verify_list = r'10X98765432'

            check_sum = 0

            for index in range(17):
                check_sum += int(val[index]) * weight_factor[index]

            result = (verify_list[check_sum % 11] == val[17])

        return result

    @staticmethod
    def params_join(params: typing.Dict, excludes: typing.Optional[typing.List] = None) -> str:

        if excludes is not None:
            params = {key: val for key, val in params.items() if key not in excludes}

        return r'&'.join(f'{key}={val}' for key, val in sorted(params.items(), key=lambda x: x[0]))

    @classmethod
    def params_sign(cls, *args, **kwargs) -> str:

        result = []

        if args:
            result.extend(str(val) for val in args)
            result.sort()

        if kwargs:
            result.append(cls.params_join(kwargs))

        return cls.md5(r'&'.join(result))

    @classmethod
    def get_today_region(cls, today: typing.Optional[datetime] = None) -> typing.Tuple[int, int]:

        if today is None:
            today = cls.today()

        start_date = today
        end_date = today + timedelta(days=1)

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return start_time, end_time

    @classmethod
    def get_month_region(cls, today: typing.Optional[datetime] = None) -> typing.Tuple[int, int]:

        if today is None:
            today = cls.today()

        start_date = today.replace(day=1)

        _, days_in_month = calendar.monthrange(
            start_date.year, start_date.month)

        end_date = start_date + timedelta(days=days_in_month)

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return start_time, end_time

    @classmethod
    def get_week_region(cls, today: typing.Optional[datetime] = None) -> typing.Tuple[int, int]:

        if today is None:
            today = cls.today()

        week_pos = today.weekday()

        start_date = today - timedelta(days=week_pos)
        end_date = today + timedelta(days=(7 - week_pos))

        start_time = int(time.mktime(start_date.timetuple()))
        end_time = int(time.mktime(end_date.timetuple())) - 1

        return start_time, end_time

    @staticmethod
    def zip_file(zip_file: str, *file_paths: str):

        def _add_to_zip(_zf: ZipFile, _path: str, _zip_path: str):

            if os.path.isfile(_path):

                _zf.write(_path, _zip_path, ZIP_DEFLATED)

            elif os.path.isdir(_path):

                if _zip_path:
                    _zf.write(_path, _zip_path)

                for nm in os.listdir(_path):
                    _add_to_zip(_zf, os.path.join(_path, nm), os.path.join(_zip_path, nm))

        with ZipFile(zip_file, r'w') as _zf:

            for path in file_paths:

                zippath = os.path.basename(path)

                if not zippath:
                    zippath = os.path.basename(os.path.dirname(path))
                if zippath in (r'', os.curdir, os.pardir):
                    zippath = r''

                _add_to_zip(_zf, path, zippath)

    @staticmethod
    def unzip_file(zip_file: str, file_paths: str):

        with ZipFile(zip_file, r'r') as _zf:
            _zf.extractall(file_paths)

    @staticmethod
    @cached(cache=TTLCache(maxsize=0xf, ttl=1))
    def get_cpu_percent() -> float:
        return psutil.cpu_percent()

    @staticmethod
    def kill_process(*names):

        process_names = [name.lower() for name in names]

        for pid in psutil.pids():

            process = psutil.Process(pid)

            if process.name().lower() in process_names:
                process.kill()


class FuncWrapper:
    """函数包装器

    将多个函数包装成一个可调用对象

    """

    def __init__(self):

        self._callables = set()

    def __call__(self, *args, **kwargs):

        for func in self._callables:
            try:
                func(*args, **kwargs)
            except Exception as err:
                Utils.log.exception(str(err))

    @property
    def is_valid(self) -> bool:

        return len(self._callables) > 0

    def add(self, func: typing.Callable) -> bool:

        if func in self._callables:
            return False
        else:
            self._callables.add(func)
            return True

    def remove(self, func: typing.Callable) -> bool:

        if func in self._callables:
            self._callables.remove(func)
            return True
        else:
            return False
