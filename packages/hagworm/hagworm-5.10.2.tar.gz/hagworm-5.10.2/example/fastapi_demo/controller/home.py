# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.frame.fastapi.base import APIRouter, Request
from hagworm.frame.fastapi.response import ErrorResponse

from service import DataSource


router = APIRouter()


@router.get(r'/')
async def default(request: Request):

    return request.client_ip, DataSource().timestamp_ms


@router.get(r'/error')
async def error(request: Request):

    raise ErrorResponse(-1, request.client_ip, 400)
