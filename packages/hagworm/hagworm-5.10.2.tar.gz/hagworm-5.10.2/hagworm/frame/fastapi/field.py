# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from pydantic import AfterValidator
from typing_extensions import Annotated

from ...extend import validator
from ...extend.base import Utils


def _IDCardType(val: str) -> str:

    if not Utils.identity_card(val):
        raise ValueError(r'value is not a valid identity card')

    return val

IDCardType = Annotated[str, AfterValidator(_IDCardType)]


def _BankCardType(val: str) -> str:

    if not Utils.luhn_valid(val):
        raise ValueError(r'value is not a valid bank card')

    return val

BankCardType = Annotated[str, AfterValidator(_BankCardType)]


def _UUIDType(val: str) -> str:

    if not validator.uuid(val):
        raise ValueError(r'value is not a valid uuid')

    return val

UUIDType = Annotated[str, AfterValidator(_UUIDType)]


def _DateType(val: str) -> typing.Any:

    try:
        val = Utils.date_parse(val)
    except Exception:
        raise ValueError(r'value is not a valid date')

    return val

DateType = Annotated[str, AfterValidator(_DateType)]


def _JsonType(val: str) -> typing.Any:

    try:
        val = Utils.json_decode(val)
    except Exception:
        raise ValueError(r'value is not a valid json')

    return val

JsonType = Annotated[str, AfterValidator(_JsonType)]


def _IntListType(val: str) -> typing.List[int]:

    try:
        val = Utils.split_int(val)
    except Exception:
        raise ValueError(r'value is not a valid int list')

    return val

IntListType = Annotated[str, AfterValidator(_IntListType)]


def _FloatListType(val: str) -> typing.List[float]:

    try:
        val = Utils.split_float(val)
    except Exception:
        raise ValueError(r'value is not a valid float list')

    return val

FloatListType = Annotated[str, AfterValidator(_FloatListType)]


def _ASCVisibleType(val: str) -> str:

    if not validator.asc_visible(val):
        raise ValueError(r'value is not a valid asc visible')

    return val

ASCVisibleType = Annotated[str, AfterValidator(_ASCVisibleType)]


def _EmailType(val: str) -> str:

    if not validator.email(val):
        raise ValueError(r'value is not a valid email')

    return val

EmailType = Annotated[str, AfterValidator(_EmailType)]


def _DomainType(val: str) -> str:

    if not validator.domain(val):
        raise ValueError(r'value is not a valid domain')

    return val

DomainType = Annotated[str, AfterValidator(_DomainType)]


def _URLType(val: str) -> str:

    if not validator.url(val):
        raise ValueError(r'value is not a valid url')

    return val

URLType = Annotated[str, AfterValidator(_URLType)]


def _MacAddrType(val: str) -> str:

    if not validator.mac_addr(val):
        raise ValueError(r'value is not a valid mac address')

    return val

MacAddrType = Annotated[str, AfterValidator(_MacAddrType)]


def _IPvAnyType(val: str) -> str:

    if not validator.ipv4(val) and not validator.ipv6(val):
        raise ValueError(r'value is not a valid ip address')

    return val

IPvAnyType = Annotated[str, AfterValidator(_IPvAnyType)]


def _IPv4Type(val: str) -> str:

    if not validator.ipv4(val):
        raise ValueError(r'value is not a valid ipv4 address')

    return val

IPv4Type = Annotated[str, AfterValidator(_IPv4Type)]


def _IPv4CidrType(val: str) -> str:

    if not validator.ipv4_cidr(val):
        raise ValueError(r'value is not a valid ipv4 address')

    return val

IPv4CidrType = Annotated[str, AfterValidator(_IPv4CidrType)]


def _IPv6Type(val: str) -> str:

    if not validator.ipv6(val):
        raise ValueError(r'value is not a valid ipv6 address')

    return val

IPv6Type = Annotated[str, AfterValidator(_IPv6Type)]


def _IPv6CidrType(val: str) -> str:

    if not validator.ipv6_cidr(val):
        raise ValueError(r'value is not a valid ipv6 address')

    return val

IPv6CidrType = Annotated[str, AfterValidator(_IPv6CidrType)]
