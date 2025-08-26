# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing
import re
import enum
import copy
import struct
import threading
import itertools

from abc import ABCMeta, abstractmethod
from io import BytesIO


class Enum(enum.Enum):

    @classmethod
    def items(cls) -> typing.Iterable:
        return cls.to_dict().items()

    @classmethod
    def keys(cls) -> typing.Iterable:
        return cls.to_dict().keys()

    @classmethod
    def values(cls) -> typing.Iterable:
        return cls.to_dict().values()

    @classmethod
    def to_dict(cls) -> typing.Dict:

        if not hasattr(cls, r'_to_dict'):
            setattr(cls, r'_to_dict', {item.name: item.value for item in cls})

        return getattr(cls, r'_to_dict')

    @classmethod
    def to_keys_dict(cls) -> typing.Dict:

        if not hasattr(cls, r'_to_keys_dict'):
            setattr(cls, r'_to_keys_dict', {item.name: item for item in cls})

        return getattr(cls, r'_to_keys_dict')

    @classmethod
    def to_values_dict(cls) -> typing.Dict:

        if not hasattr(cls, r'_to_values_dict'):
            setattr(cls, r'_to_values_dict', {item.value: item for item in cls})

        return getattr(cls, r'_to_values_dict')

    @classmethod
    def has_key(cls, key) -> bool:
        return key in cls.to_keys_dict()

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls.to_values_dict()


class IntEnum(int, Enum): pass


RoundRobinMemberType = typing.TypeVar('RoundRobinMemberType')

class RoundRobin(typing.Generic[RoundRobinMemberType]):

    def __init__(self, members: typing.Optional[typing.Dict[str, RoundRobinMemberType]] = None):

        self._members: typing.Dict[str, RoundRobinMemberType] = members if members else {}
        self._iterator: typing.Iterator = itertools.cycle(self._members.items())

    def __len__(self) -> int:
        return len(self._members)

    def __contains__(self, key) -> bool:
        return key in self._members

    def append(self, name: str, member: RoundRobinMemberType) -> typing.Optional[RoundRobinMemberType]:

        if name in self._members:
            _member = self._members.pop(name)
        else:
            _member = None

        self._members[name] = member
        self._iterator = itertools.cycle(self._members.items())

        return _member

    def clear(self, names: typing.Optional[typing.List[str]] = None) -> typing.Dict[str, RoundRobinMemberType]:

        members = {}

        if names is None:

            members.update(self._members)
            self._members.clear()

        else:

            for _name in names:
                if _name in self._members:
                    members[_name] = self._members.pop(_name)

        self._iterator = itertools.cycle(self._members.items())

        return members

    def reset(self, members: typing.Optional[typing.Dict[str, RoundRobinMemberType]] = None) -> typing.Dict[str, RoundRobinMemberType]:

        _members = members if members else {}

        _members, self._members = self._members, _members
        self._iterator = itertools.cycle(self._members.items())

        return _members

    def get(self) -> typing.Tuple[str, RoundRobinMemberType]:
        return next(self._iterator)

class RoundRobinSimple(typing.Generic[RoundRobinMemberType]):

    def __init__(self, members: typing.Optional[typing.List[RoundRobinMemberType]] = None):
        self._members: typing.List[RoundRobinMemberType] = members if members else []
        self._iterator: typing.Iterator = itertools.cycle(self._members)

    def __len__(self) -> int:
        return len(self._members)

    def append(self, member: RoundRobinMemberType):
        self._members.append(member)
        self._iterator = itertools.cycle(self._members)

    def clear(self) -> typing.List[RoundRobinMemberType]:

        members = copy.copy(self._members)

        self._members.clear()
        self._iterator = itertools.cycle(self._members)

        return members

    def get(self) -> RoundRobinMemberType:
        return next(self._iterator)


class ThreadList(threading.local):
    """多线程安全的列表
    """

    __slots__ = [r'data']

    def __init__(self):

        self.data: typing.List = []


class ThreadDict(threading.local):
    """多线程安全的字典
    """

    __slots__ = [r'data']

    def __init__(self):

        self.data: typing.Dict = {}


class ByteArrayAbstract(metaclass=ABCMeta):
    """ByteArray抽象类
    """

    NETWORK = r'!'
    NATIVE = r'='
    NATIVE_ALIGNMENT = r'@'
    LITTLE_ENDIAN = r'<'
    BIG_ENDIAN = r'>'

    def __init__(self):

        self._endian: str = self.NETWORK

    def get_endian(self) -> str:

        return self._endian

    def set_endian(self, val: str):

        self._endian = val

    @abstractmethod
    def read(self, size) -> typing.Any:
        """
        读取数据
        """

    @abstractmethod
    def write(self, buffer: typing.Any):
        """
        定稿数据
        """

    def read_pad_byte(self, size: int) -> typing.Tuple:

        return struct.unpack(f'{self._endian}{size}x', self.read(size))

    def write_pad_byte(self, val: typing.Tuple):

        self.write(struct.pack(f'{self._endian}{val}x'))

    def read_char(self) -> int:

        return struct.unpack(f'{self._endian}c', self.read(1))[0]

    def write_char(self, val: int):

        self.write(struct.pack(f'{self._endian}c', val))

    def read_signed_char(self) -> int:

        return struct.unpack(f'{self._endian}b', self.read(1))[0]

    def write_signed_char(self, val: int):

        self.write(struct.pack(f'{self._endian}b', val))

    def read_unsigned_char(self) -> int:

        return struct.unpack(f'{self._endian}B', self.read(1))[0]

    def write_unsigned_char(self, val: int):

        self.write(struct.pack(f'{self._endian}B', val))

    def read_bool(self) -> bool:

        return struct.unpack(f'{self._endian}?', self.read(1))[0]

    def write_bool(self, val: bool):

        self.write(struct.pack(f'{self._endian}?', val))

    def read_short(self) -> int:

        return struct.unpack(f'{self._endian}h', self.read(2))[0]

    def write_short(self, val: int):

        self.write(struct.pack(f'{self._endian}h', val))

    def read_unsigned_short(self) -> int:

        return struct.unpack(f'{self._endian}H', self.read(2))[0]

    def write_unsigned_short(self, val: int):

        self.write(struct.pack(f'{self._endian}H', val))

    def read_int(self) -> int:

        return struct.unpack(f'{self._endian}i', self.read(4))[0]

    def write_int(self, val: int):

        self.write(struct.pack(f'{self._endian}i', val))

    def read_unsigned_int(self) -> int:

        return struct.unpack(f'{self._endian}I', self.read(4))[0]

    def write_unsigned_int(self, val: int):

        self.write(struct.pack(f'{self._endian}I', val))

    def read_long(self) -> int:

        return struct.unpack(f'{self._endian}l', self.read(4))[0]

    def write_long(self, val: int):

        self.write(struct.pack(f'{self._endian}l', val))

    def read_unsigned_long(self) -> int:

        return struct.unpack(f'{self._endian}L', self.read(4))[0]

    def write_unsigned_long(self, val: int):

        self.write(struct.pack(f'{self._endian}L', val))

    def read_long_long(self) -> int:

        return struct.unpack(f'{self._endian}q', self.read(8))[0]

    def write_long_long(self, val: int):

        self.write(struct.pack(f'{self._endian}q', val))

    def read_unsigned_long_long(self) -> int:

        return struct.unpack(f'{self._endian}Q', self.read(8))[0]

    def write_unsigned_long_long(self, val: int):

        self.write(struct.pack(f'{self._endian}Q', val))

    def read_float(self) -> float:

        return struct.unpack(f'{self._endian}f', self.read(4))[0]

    def write_float(self, val):

        self.write(struct.pack(f'{self._endian}f', val))

    def read_double(self) -> float:

        return struct.unpack(f'{self._endian}d', self.read(8))[0]

    def write_double(self, val: float):

        self.write(struct.pack(f'{self._endian}d', val))

    def read_bytes(self, size: int) -> bytes:

        return struct.unpack(f'{self._endian}{size}s', self.read(size))[0]

    def write_bytes(self, val: bytes):

        self.write(struct.pack(f'{self._endian}{len(val)}s', val))

    def read_string(self, size: int):

        return self.read_bytes(size).decode()

    def write_string(self, val: str):

        self.write_bytes(val.encode())

    def read_pascal_bytes(self, size: int):

        return struct.unpack(f'{self._endian}{size}p', self.read(size))[0]

    def write_pascal_bytes(self, val: bytes):

        self.write(struct.pack(f'{self._endian}{len(val)}p', val))

    def read_pascal_string(self, size: int):

        return self.read_pascal_bytes(size).decode()

    def write_pascal_string(self, val: str):

        self.write_pascal_bytes(val.encode())


class ByteArray(BytesIO, ByteArrayAbstract):
    """扩展的BytesIO类
    """

    NETWORK = r'!'
    NATIVE = r'='
    NATIVE_ALIGNMENT = r'@'
    LITTLE_ENDIAN = r'<'
    BIG_ENDIAN = r'>'

    def __init__(self, initial_bytes: typing.Optional[bytes] = None):

        BytesIO.__init__(self, initial_bytes)
        ByteArrayAbstract.__init__(self)


class KeyLowerDict(dict):

    _PATTERN = re.compile(r'(?<=[a-z])([A-Z])')

    def __init__(self, _dict: typing.Dict[str, typing.Any]):

        super().__init__(
            {
                KeyLowerDict._PATTERN.sub(r'_\1', key).lower(): KeyLowerDict(val) if isinstance(val, dict) else val
                for key, val in _dict.items()
            }
        )
