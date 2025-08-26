# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import typing

import json
import yaml

from ...extend.config import ConfigureBase

from .client import DEFAULT_PROTOCOL, PROTOCOL_TYPE, DEFAULT_GROUP_NAME, NacosConfig


class Configure(ConfigureBase):
    """配置类
    """

    __slots__ = [r'_format', r'_client']

    def __init__(
            self, servers: str, data_id: str, *,
            username: str = r'', password: str = r'',
            protocol: PROTOCOL_TYPE = DEFAULT_PROTOCOL, endpoint: str = r'',
            group: str = DEFAULT_GROUP_NAME, namespace: str = r'',
            data_format: typing.Literal[r'text', r'json', r'yaml'] = r'yaml'
    ):

        super().__init__()

        self._format: str = data_format

        self._client: typing.Optional[NacosConfig] = None

        if not servers and os.path.isfile(data_id):

            with open(data_id, 'r') as file:
                self._reload_config(file.read())

        else:

            self._client = NacosConfig(
                self._reload_config, servers, data_id,
                username=username, password=password,
                protocol=protocol, endpoint=endpoint, group=group, namespace=namespace
            )

    def _reload_config(self, content: str):

        self._clear_options()

        if self._format == r'text':
            self._parser.read_string(content)
        elif self._format == r'json':
            self._parser.read_dict(json.loads(content))
        elif self._format == r'yaml':
            self._parser.read_dict(yaml.load(content, yaml.Loader))

        self._load_options()

    def open(self):

        if self._client is not None:
            self._client.start()

    def close(self):

        if self._client is not None:
            self._client.stop()

        self._clear_options()
