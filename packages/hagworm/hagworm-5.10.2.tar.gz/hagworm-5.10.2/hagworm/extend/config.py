# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import typing
import dataclasses
import json
import yaml

from configparser import RawConfigParser

from .base import Utils


class HostType(str):

    @classmethod
    def decode(cls, val: str) -> typing.Tuple[str, int]:

        if val:
            host, port = val.split(r':', 2)
            return host.strip(), int(port.strip())


class JsonType(str):

    @classmethod
    def decode(cls, val: str) -> typing.Union[typing.List, typing.Dict]:
        return Utils.json_decode(val)


class StrListType(str):

    @classmethod
    def decode(cls, val: str) -> typing.List[str]:
        return Utils.split_str(val)


class IntListType(str):

    @classmethod
    def decode(cls, val: str) -> typing.List[int]:
        return Utils.split_int(val)


class FloatListType(str):

    @classmethod
    def decode(cls, val: str) -> typing.List[float]:
        return Utils.split_float(val)


class Field:

    __slots__ = [r'section', r'default']

    def __init__(self, section: str, default: typing.Any = None):

        self.section: str = section
        self.default: typing.Any = default


class ConfigureMetaclass(type):
    """配置类元类，增加dataclass修饰
    """

    def __new__(mcs, name, bases, attrs):
        # noinspection PyTypeChecker
        return dataclasses.dataclass(init=False)(
            type.__new__(mcs, name, bases, attrs)
        )


class KeySection(typing.NamedTuple):

    key: str
    type: typing.Any
    section: str
    default: typing.Any


class ConfigureBase(metaclass=ConfigureMetaclass):
    """配置类
    """

    __slots__ = [r'__dataclass_fields__', r'_parser', r'_key_section']

    def __init__(self):

        super().__init__()

        self._parser = RawConfigParser()

        self._key_section: typing.Dict[str, KeySection] = {
            f'{_field.default.section}_{_key}': KeySection(
                _key,
                _field.type,
                _field.default.section,
                _field.default.default,
            )
            for _key, _field in self.__dataclass_fields__.items()
        }

    def _load_options(self):

        for _key_section in self._key_section.values():

            # 优先处理环境变量
            _env_key = f'{_key_section.section}_{_key_section.key}'.upper()
            _env_val = os.getenv(_env_key, None)

            if _env_val is not None:
                self._parser.set(_key_section.section, _key_section.key, _env_val)
                Utils.log.info(f'load environment variable {_env_key}: {_env_val}')

            if _key_section.type is str:
                _val = self._parser.get(_key_section.section, _key_section.key)
            elif _key_section.type is int:
                _val = self._parser.getint(_key_section.section, _key_section.key)
            elif _key_section.type is float:
                _val = self._parser.getfloat(_key_section.section, _key_section.key)
            elif _key_section.type is bool:
                _val = self._parser.getboolean(_key_section.section, _key_section.key)
            else:
                _val = _key_section.type.decode(self._parser.get(_key_section.section, _key_section.key))

            self.__setattr__(_key_section.key, _val)

    def _clear_options(self):

        self._parser.clear()

        _config = {}

        for _key_section in self._key_section.values():
            if _key_section.default is not None:
                _config.setdefault(_key_section.section, {})[_key_section.key] = _key_section.default

        if _config:
            self._parser.read_dict(_config)

    def to_dict(self, section=None) -> typing.Dict:

        if section is None:
            return {key: dict(val) for key, val in self._parser.items()}
        else:
            return {key: val for key, val in self._parser.items(section)}

    def to_yaml(self, section=None) -> str:
        return yaml.dump(self.to_dict(section))


class Configure(ConfigureBase):
    """配置类
    """

    def get_option(self, section: str, option: str) -> typing.Any:

        return self._parser.get(section, option)

    def get_options(self, section: str) -> typing.Dict:

        parser = self._parser

        options = {}

        for option in parser.options(section):
            options[option] = parser.get(section, option)

        return options

    def set_options(self, section: str, **options: str):

        if not self._parser.has_section(section):
            self._parser.add_section(section)

        for option, value in options.items():
            self._parser.set(section, option, value)

        self._load_options()

    def read(self, path: str, encoding: str = r'utf-8'):

        self._clear_options()

        self._parser.read(path, encoding=encoding)

        self._load_options()

    def read_env(self):

        self._clear_options()

        self._load_options()

    def read_str(self, val: str):

        self._clear_options()

        self._parser.read_string(val)

        self._load_options()

    def read_dict(self, val: typing.Dict):

        self._clear_options()

        self._parser.read_dict(val)

        self._load_options()

    def read_json(self, path: str, encoding: str = r'utf-8'):

        self._clear_options()

        with open(path, encoding=encoding) as fp:
            self._parser.read_dict(json.loads(fp.read()))

        self._load_options()

    def read_yaml(self, path: str, encoding: str = r'utf-8'):

        self._clear_options()

        with open(path, encoding=encoding) as fp:
            self._parser.read_dict(yaml.load(fp.read(), yaml.Loader))

        self._load_options()
