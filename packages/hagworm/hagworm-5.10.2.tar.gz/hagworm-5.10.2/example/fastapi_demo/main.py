# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../../'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hagworm.frame.fastapi.base import uvicorn_run, create_fastapi
from hagworm.extend.logging import LogFileRotator

from setting import Config
from service import DataSource
from controller import router


def app() -> FastAPI:

    fastapi = create_fastapi(
        log_level=Config.LogLevel,
        log_file_path=Config.LogFilePath,
        log_file_rotation=LogFileRotator.make(Config.LogFileSplitSize, Config.LogFileSplitTime),
        log_file_retention=Config.LogFileBackups,
        debug=Config.Debug,
        routes=router.routes,
        on_startup=[DataSource.initialize],
        on_shutdown=[DataSource.release],
    )

    fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=Config.AllowOrigins,
        allow_methods=Config.AllowMethods,
        allow_headers=Config.AllowHeaders,
        allow_credentials=Config.AllowCredentials,
    )

    return fastapi


if __name__ == r'__main__':
    uvicorn_run(app, port=Config.Port)
