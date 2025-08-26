# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import typing
import logging
import uvicorn
import fastapi

from starlette.requests import Request as _Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles
from starlette.datastructures import Headers, Address

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html

from ... import hagworm_label

from ...extend.trace import refresh_trace_id
from ...extend.asyncio.base import Utils, install_uvloop
from ...extend.logging import DEFAULT_LOG_FILE_NAME, DEFAULT_LOG_FILE_ROTATOR, init_logger
from ...frame.stress_tests import TimerMS

from .response import Response, ErrorResponse


get_swagger_ui_html.__kwdefaults__.update(
    {
        r'swagger_js_url': r'/static/swagger-ui-bundle.js',
        r'swagger_css_url': r'/static/swagger-ui.css',
    }
)


def uvicorn_run(app: typing.Callable, host: str = r'0.0.0.0', port: int = 8080):
    Utils.log.warning(r'THE PRODUCTION ENVIRONMENT IS STARTED USING GUNICORN')
    uvicorn.run(app, host=host, port=port, log_config=None, server_header=False, factory=True)


def create_fastapi(
        log_level: str = r'info', log_handler: typing.Optional[logging.Handler] = None,
        log_file_path: typing.Optional[str] = None, log_file_name: str =DEFAULT_LOG_FILE_NAME,
        log_file_rotation: typing.Callable = DEFAULT_LOG_FILE_ROTATOR, log_file_retention: int = 0xff,
        log_extra: typing.Optional[typing.Dict] = None, log_enqueue: bool = False,
        debug: bool = False, routes: typing.Optional[typing.List] = None,
        **setting: typing.Any
) -> fastapi.FastAPI:

    init_logger(
        log_level.upper(),
        handler=log_handler,
        file_path=log_file_path,
        file_name=log_file_name,
        file_rotation=log_file_rotation,
        file_retention=log_file_retention,
        extra=log_extra,
        enqueue=log_enqueue,
        debug=debug
    )

    Utils.print_slogan()

    install_uvloop()

    _fastapi = fastapi.FastAPI(debug=debug, routes=routes, **setting)

    _fastapi.middleware(r'http')(http_default_middleware)

    _fastapi.exception_handler(ErrorResponse)(response_exception_handler)
    _fastapi.exception_handler(HTTPException)(http_exception_handler)
    _fastapi.exception_handler(RequestValidationError)(request_validation_exception_handler)

    _fastapi.mount(r'/static', StaticFiles(directory=f'{os.path.split(__file__)[0]}/../../static'))

    return _fastapi


class APIRouter(fastapi.APIRouter):
    """目录可选末尾的斜杠访问
    """

    def __init__(
            self, *,
            prefix: str = r'',
            default_response_class: typing.Type[Response] = Response,
            **kwargs
    ):

        super().__init__(
            prefix=prefix,
            default_response_class=default_response_class,
            **kwargs
        )

    def _get_path_alias(self, path: str) -> typing.List[str]:

        _path = path.rstrip(r'/')

        if not self.prefix and not _path:
            return [path]

        _path_split = os.path.splitext(_path)

        if _path_split[1]:
            return [_path]

        return [_path, _path + r'/']

    def api_route(self, path: str, *args, **kwargs) -> typing.Callable:

        def _decorator(func):

            for index, _path in enumerate(self._get_path_alias(path)):

                self.add_api_route(_path, func, *args, **kwargs)

                # 兼容的URL将不会出现在docs中
                if index == 0:
                    kwargs[r'include_in_schema'] = False

            return func

        return _decorator


class _RequestMixin:

    headers: Headers
    client: Address

    @property
    def referer(self) -> str:
        return self.headers.get(r'Referer')

    @property
    def client_ip(self) -> str:

        if self.x_forwarded_for:
            return self.x_forwarded_for[0]
        else:
            return self.client_host

    @property
    def client_host(self) -> str:
        return self.headers.get(r'X-Real-IP', self.client.host)

    @property
    def x_forwarded_for(self) -> typing.List[str]:
        return Utils.split_str(self.headers.get(r'X-Forwarded-For', r''), r',')

    @property
    def content_type(self) -> str:
        return self.headers.get(r'Content-Type')

    @property
    def content_length(self) -> int:

        result = self.headers.get(r'Content-Length', r'')

        return int(result) if result.isdigit() else 0

    def get_header(self, name: str, default: typing.Optional[str] = None) -> str:
        return self.headers.get(name, default)


class Request(_Request, _RequestMixin):
    pass

_Request.__bases__ += (_RequestMixin,)


async def http_default_middleware(request: Request, call_next: typing.Callable) -> typing.Any:

    trace_id = refresh_trace_id(request.headers.get(r'x-request-id', None))

    with TimerMS() as timer:
        response = await call_next(request)

    response.headers.update(
        {
            r'server': hagworm_label,
            r'x-trace-id': trace_id,
            r'x-request-ttl-ms': r'{:.3f}'.format(timer.value),
            r'x-request-payload': request.headers.get(r'x-request-payload', r''),
        }
    )

    return response


def response_exception_handler(request: Request, exc: ErrorResponse) -> ErrorResponse:

    Utils.log.warning(f'{request.client_host} response exception: {request.url.path} => {str(exc)}')

    return exc


def http_exception_handler(request: Request, exc: HTTPException) -> ErrorResponse:

    Utils.log.warning(f'{request.client_host} http exception: {request.url.path} => {str(exc)}')

    return ErrorResponse(
        -1,
        content=exc.detail,
        status_code=exc.status_code,
        headers=exc.headers
    )


def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> ErrorResponse:

    Utils.log.warning(f'{request.client_host} request validation exception: {request.url.path} => {str(exc)}')

    return ErrorResponse(
        -1,
        content=jsonable_encoder(exc.errors()),
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
    )
