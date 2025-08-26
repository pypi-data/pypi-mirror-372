# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from typing import Any, Dict, List

from re import findall
from ahocorasick_rs import AhoCorasick


class StrUtils:

    SAFE_STRING_BASE: str = r'2346789BCEFGHJKMPQRTVWXY'

    FULL_WIDTH_CHAR_MAPPING: Dict[str, str] = {chr(num): chr(num - 0xfee0) for num in range(0xff01, 0xff5f)}
    FULL_WIDTH_CHAR_MAPPING[chr(0x3000)] = chr(0x20)
    FULL_WIDTH_CHAR_MAPPING[chr(0x3001)] = chr(0x2c)
    FULL_WIDTH_CHAR_MAPPING[chr(0x3002)] = chr(0x2e)
    FULL_WIDTH_CHAR_MAPPING[chr(0x2018)] = chr(0x27)
    FULL_WIDTH_CHAR_MAPPING[chr(0x2019)] = chr(0x27)
    FULL_WIDTH_CHAR_MAPPING[chr(0x201c)] = chr(0x22)
    FULL_WIDTH_CHAR_MAPPING[chr(0x201d)] = chr(0x22)

    HALF_WIDTH_CHAR_MAPPING: Dict[str, str] = {val: key for key, val in FULL_WIDTH_CHAR_MAPPING.items()}

    # 转换成半角字符
    @classmethod
    def to_half_width(cls, value: str) -> str:
        return value.translate(
            value.maketrans(cls.FULL_WIDTH_CHAR_MAPPING)
        )

    # 转换成全角字符
    @classmethod
    def to_full_width(cls, value: str) -> str:
        return value.translate(
            value.maketrans(cls.HALF_WIDTH_CHAR_MAPPING)
        )

    @staticmethod
    def to_camel(val: str) -> str:

        words = val.split(r'_')

        return words[0] + r''.join(word.title() for word in words[1:])

    @staticmethod
    def to_snake(val: str) -> str:

        words = findall(r'([a-zA-Z][^A-Z0-9]*|[0-9]+)', val)

        return r'_'.join(word.lower() for word in words)

    @staticmethod
    def to_upper_camel(val: str) -> str:

        words = val.split(r'_')

        return r''.join(word.title() for word in words)

    @classmethod
    def to_camel_dict(cls, val: Any) -> Any:

        if isinstance(val, dict):
            return {
                cls.to_camel(_key): cls.to_camel_dict(_val)
                for _key, _val in val.items()
            }
        elif isinstance(val, list):
            return [
                cls.to_camel_dict(_val)
                for _val in val
            ]
        else:
            return val

    @classmethod
    def to_snake_dict(cls, val: Any) -> Any:

        if isinstance(val, dict):
            return {
                cls.to_snake(_key): cls.to_snake_dict(_val)
                for _key, _val in val.items()
            }
        elif isinstance(val, list):
            return [
                cls.to_snake_dict(_val)
                for _val in val
            ]
        else:
            return val

    @classmethod
    def to_upper_camel_dict(cls, val: Any) -> Any:

        if isinstance(val, dict):
            return {
                cls.to_upper_camel(_key): cls.to_upper_camel_dict(_val)
                for _key, _val in val.items()
            }
        elif isinstance(val, list):
            return [
                cls.to_upper_camel_dict(_val)
                for _val in val
            ]
        else:
            return val


class TextFinder:

    def __init__(self, words: List[str]):

        self._ahocorasick: AhoCorasick = AhoCorasick(words)

    def find_all(self, content: str) -> List[str]:

        return self._ahocorasick.find_matches_as_strings(content)

    def replace_all(self, content: str, _chars: str = r'*') -> str:

        words = {val for val in self.find_all(content)}

        for key in words:
            content = content.replace(key, _chars * len(key))

        return content
