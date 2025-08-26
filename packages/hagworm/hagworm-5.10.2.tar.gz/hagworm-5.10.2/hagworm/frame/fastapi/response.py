# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from fastapi.responses import UJSONResponse

from ...extend.trace import get_trace_id
from ...extend.error import Ignore


class Response(UJSONResponse):

    def __init__(self, content: typing.Any = None, status_code: int = 200, *args, **kwargs):

        self._trace_id: str = get_trace_id()

        super().__init__(content, status_code, *args, **kwargs)

    def render(self, content: typing.Any):

        return UJSONResponse.render(
            self,
            dict(code=0, data=content, trace_id=self._trace_id)
        )


class ErrorResponse(Response, Ignore):

    def __init__(self, code: int, content: typing.Any = None, status_code: int = 200, **kwargs):

        self._code: int = code

        Response.__init__(self, content, status_code, **kwargs)
        Ignore.__init__(self, self.body.decode(), layers=-1)

    def render(self, content: typing.Any):

        return UJSONResponse.render(
            self,
            dict(code=self._code, error=content, trace_id=self._trace_id)
        )
