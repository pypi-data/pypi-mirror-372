# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import time
import typing
import logging

import httpx

from abc import abstractmethod

from ...extend.base import Utils
from ...extend.struct import RoundRobinSimple
from ...extend.interface import TaskInterface
from ...extend.asyncio.future import Thread


DEFAULT_GROUP_NAME = r'DEFAULT_GROUP'
DEFAULT_PROTOCOL = r'http'

PROTOCOL_TYPE = typing.Literal[r'http', r'https']

DEFAULT_REQUEST_TIMEOUT = 10
DEFAULT_PULLING_TIMEOUT = 30
DEFAULT_WEIGHT = 1

WORD_SEPARATOR = u'\x02'
LINE_SEPARATOR = u'\x01'


logging.getLogger(r'httpx').setLevel(r'ERROR')
logging.getLogger(r'httpx').propagate = False


class _NacosInterface(TaskInterface):

    def __init__(
            self, servers: str, username: str, password: str,
            protocol: str, endpoint: str, group: str, namespace: str,
            request_timeout: float
    ):

        self._task: Thread = Thread(target=self._do_task)

        self._http_client: httpx.Client = httpx.Client(timeout=httpx.Timeout(request_timeout))

        self._servers: RoundRobinSimple[str] = RoundRobinSimple(
            Utils.split_str(servers, r',')
        )

        self._username: str = username
        self._password: str = password

        self._access_token: str = r''
        self._access_expires: int = 0

        self._protocol: str = protocol
        self._endpoint: str = endpoint
        self._group: str = group
        self._namespace: str = namespace

        self._request_timeout: float = request_timeout

    def _get_url_prefix(self) -> str:
        return f'{self._protocol}://{self._servers.get()}{self._endpoint}/nacos/v1'

    def _get_access_token(self) -> typing.Optional[str]:

        if not self._username or not self._password:
            return

        now_time = Utils.timestamp()

        if self._access_expires > now_time:
            return self._access_token

        server = self._servers.get()

        try:

            resp = self._http_client.post(
                f'{self._protocol}://{server}/nacos/v1/auth/login',
                data={r'username': self._username, r'password': self._password}
            )

            if resp.status_code == 200:

                content = resp.json()

                self._access_token = content[r'accessToken']
                self._access_expires = now_time + content[r'tokenTtl']

                Utils.log.info(f'nacos refresh access token expires: {Utils.stamp2time(self._access_expires)}')

            else:

                raise Exception(f'status code {resp.status_code}')

        except Exception as err:
            Utils.log.error(f'nacos {server} login error: {str(err)}')

        return self._access_token

    @abstractmethod
    def _do_task(self):
        """
        执行后台任务
        """

    def start(self):
        self._task.start()

    def stop(self):
        self._task.stop()
        self._http_client.close()

    def is_running(self) -> bool:
        return self._task.is_alive()


class NacosConfig(_NacosInterface):

    def __init__(
            self, listener: typing.Callable, servers: str, data_id: str, *,
            username: str = r'', password: str = r'',
            protocol: PROTOCOL_TYPE = DEFAULT_PROTOCOL, endpoint: str = r'',
            group: str = DEFAULT_GROUP_NAME, namespace: str = r'',
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT, pulling_timeout: float = DEFAULT_PULLING_TIMEOUT
    ):

        super().__init__(servers, username, password, protocol, endpoint, group, namespace, request_timeout)

        self._listener: typing.Callable = listener

        self._data_id: str = data_id

        self._content: typing.Optional[str] = None
        self._content_has: typing.Optional[str] = None

        self._pulling_timeout: float = pulling_timeout

        self._cache_path: str = f'./.cache/nacos/{self._namespace}/{self._group}'

        self._flush()

    def _flush(self):

        self._content, self._content_hash = self.get_config()
        self._listener(self._content)

        Utils.log.info(f'nacos flush config: {self._content_hash}')

    def _write_cache(self, content: str):

        if not content:
            return

        if not os.path.exists(self._cache_path):
            os.makedirs(self._cache_path)

        with open(f'{self._cache_path}/{self._data_id}', 'wb') as file:
            file.write(content.encode())

    def _read_cache(self) -> typing.Optional[str]:

        if not os.path.exists(f'{self._cache_path}/{self._data_id}'):
            return None

        Utils.log.warning(f'nacos config used cache: {self._data_id}')

        with open(f'{self._cache_path}/{self._data_id}', 'rb') as file:
            return file.read().decode()

    def _do_task(self):

        while not self._task.is_stopped():

            url_prefix = self._get_url_prefix()

            payload = {
                r'Listening-Configs': WORD_SEPARATOR.join(
                    [
                        self._data_id,
                        self._group,
                        self._content_hash,
                        self._namespace,
                    ]
                ) + LINE_SEPARATOR,
            }

            params = {}

            if access_token := self._get_access_token():
                params[r'accessToken'] = access_token

            headers = {
                r'Long-Pulling-Timeout': str(self._pulling_timeout * 1000),
            }

            try:

                resp = self._http_client.post(
                    f'{url_prefix}/cs/configs/listener',
                    data=payload, params=params, headers=headers,
                    timeout=httpx.Timeout(self._request_timeout + self._pulling_timeout)
                )

                if resp.status_code == 200:
                    if resp.text:
                        Utils.log.info(f'nacos config pulling: {resp.text.strip()}')
                        self._flush()
                else:
                    raise Exception(r'nacos config pulling error')

            except httpx.TimeoutException:
                Utils.log.warning(f'nacos {url_prefix} config pulling timeout')
            except Exception as err:
                Utils.log.error(f'nacos {url_prefix} config pulling error: {str(err)}')
                time.sleep(self._request_timeout)

    def get_config(self) -> typing.Tuple[str, str]:

        content = content_hash = None

        url_prefix = self._get_url_prefix()

        params = {
            r'dataId': self._data_id,
            r'group': self._group,
        }

        if self._namespace:
            params[r'tenant'] = self._namespace

        if access_token := self._get_access_token():
            params[r'accessToken'] = access_token

        try:

            resp = self._http_client.get(f'{url_prefix}/cs/configs', params=params)

            if resp.status_code == 200:
                content = resp.text
                self._write_cache(content)
            else:
                raise Exception(f'status code {resp.status_code}')

        except Exception as err:
            Utils.log.error(f'nacos {url_prefix} get config error: {str(err)}')
            content = self._read_cache()

        if content is not None:
            content_hash = Utils.md5(content)

        return content, content_hash


class NacosInstanceRegister(_NacosInterface):

    def __init__(
            self, servers: str, service_name: str, service_ip: str, service_port: int, heartbeat_interval: int = 10, *,
            username: str = r'', password: str = r'',
            protocol: PROTOCOL_TYPE = DEFAULT_PROTOCOL, endpoint: str = r'',
            group: str = DEFAULT_GROUP_NAME, namespace: str = r'',
            cluster: typing.Optional[str] = None, weight: typing.Optional[int] = None,
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    ):

        super().__init__(servers, username, password, protocol, endpoint, group, namespace, request_timeout)

        self._service_name: str = service_name
        self._service_ip: str = service_ip
        self._service_port: int = service_port

        self._cluster: str = cluster
        self._weight: int = weight if weight is not None else DEFAULT_WEIGHT

        self._heartbeat_interval: int = heartbeat_interval

    def _do_task(self):

        while not self._task.is_stopped():

            url_prefix = self._get_url_prefix()

            payload = {
                r'serviceName': self._service_name,
                r'namespaceId': self._namespace,
                r'groupName': self._group,
                r'beat': Utils.json_encode(
                    {
                        r'serviceName': self._service_name,
                        r'ip': self._service_ip,
                        r'port': str(self._service_port),
                        r'weight': self._weight,
                        r'ephemeral': True,
                    }
                ),
            }

            params = {}

            if access_token := self._get_access_token():
                params[r'accessToken'] = access_token

            try:

                resp = self._http_client.put(f'{url_prefix}/ns/instance/beat', data=payload, params=params)

                if resp.status_code != 200:
                    raise Exception(f'status code {resp.status_code}')

            except Exception as err:
                Utils.log.error(f'nacos {url_prefix} instance beat error: {str(err)}')

            time.sleep(self._heartbeat_interval)

    def start(self):

        url_prefix = self._get_url_prefix()

        payload = {
            r'serviceName': self._service_name,
            r'ip': self._service_ip,
            r'port': self._service_port,
            r'namespaceId': self._namespace,
            r'weight': self._weight,
            r'enabled': True,
            r'healthy': True,
            r'groupName': self._group,
            r'ephemeral': True,
        }

        if self._cluster:
            payload[r'clusterName'] = self._cluster

        params = {}

        if access_token := self._get_access_token():
            params[r'accessToken'] = access_token

        try:

            resp = self._http_client.post(f'{url_prefix}/ns/instance', data=payload, params=params)

            if resp.status_code == 200:
                self._task.start()
                Utils.log.info(f'nacos instance register: {payload}')
            else:
                raise Exception(f'status code {resp.status_code}')

        except Exception as err:
            Utils.log.error(f'nacos {url_prefix} instance register error: {str(err)}')


class NacosInstanceQuery(_NacosInterface):

    def __init__(
            self, servers: str, service_name: str, listener_interval: int = 10, *,
            username: str = r'', password: str = r'',
            protocol: PROTOCOL_TYPE = DEFAULT_PROTOCOL, endpoint: str = r'',
            group: str = DEFAULT_GROUP_NAME, namespace: str = r'',
            cluster: typing.Optional[str] = None,
            request_timeout: float = DEFAULT_REQUEST_TIMEOUT
    ):

        super().__init__(servers, username, password, protocol, endpoint, group, namespace, request_timeout)

        self._service_name: str = service_name

        self._cluster: typing.Optional[str] = cluster

        self._content: typing.Optional[typing.List[typing.Dict]] = None
        self._content_hash: typing.Optional[str] = None

        self._listener_interval: int = listener_interval
        self._listener_callbacks: typing.List[typing.Callable] = []

        self._content, self._content_hash = self._send_query()

    def _do_task(self):

        while not self._task.is_stopped():

            content, content_hash = self._send_query()

            if content_hash != self._content_hash:

                self._content, self._content_hash = content, content_hash

                for _callback in self._listener_callbacks:
                    _callback(self._content)

            time.sleep(self._listener_interval)

    def _send_query(self) -> typing.Tuple[typing.List[typing.Dict], str]:

        content = content_hash = None

        url_prefix = self._get_url_prefix()

        params = {
            r'serviceName': self._service_name,
            r'namespaceId': self._namespace,
            r'groupName': self._group,
            r'healthyOnly': True,
        }

        if self._cluster:
            params[r'clusterName'] = self._cluster

        if access_token := self._get_access_token():
            params[r'accessToken'] = access_token

        try:

            resp = self._http_client.get(f'{url_prefix}/ns/instance/list', params=params)

            Utils.log.info(f'nacos instance query: {resp.text.strip()}')

            if resp.status_code == 200:
                content = sorted(
                    [
                        {
                            r'ip': _item[r'ip'],
                            r'port': _item[r'port'],
                            r'weight': _item[r'weight'],
                            r'metadata': _item[r'metadata'],
                        } for _item in resp.json()[r'hosts']
                    ],
                    key=lambda x: f"{x['ip']}:{x['port']}"
                )
                content_hash = Utils.md5(Utils.json_encode(content))
            else:
                raise Exception(f'status code {resp.status_code}')

        except Exception as err:
            Utils.log.error(f'nacos {url_prefix} instance query error: {str(err)}')

        return content, content_hash

    def add_listener(self, callback: typing.Callable):
        self._listener_callbacks.append(callback)

    def clear_listeners(self):
        self._listener_callbacks.clear()

    def get_host(self) -> typing.Dict:

        if self._content:
            return Utils.rand_hit(self._content, lambda x: int(x[r'weight'] * 100))

    def get_hosts(self) -> typing.List[typing.Dict]:
        return self._content
