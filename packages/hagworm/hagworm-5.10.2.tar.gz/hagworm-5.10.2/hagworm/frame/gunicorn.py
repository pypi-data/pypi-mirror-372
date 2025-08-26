# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from uvicorn_worker import UvicornWorker


DEFAULT_LOG_CONFIG = {
    'root': {
        'level': 'INFO',
        'handlers': ['loguru'],
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.error',
        },
        'gunicorn.access': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.access',
        },
    },
    'handlers': {
        'loguru': {
            'class': 'hagworm.extend.logging.InterceptHandler',
        },
    },
}

SIMPLE_LOG_CONFIG = {
    'root': {
        'level': 'INFO',
        'handlers': ['loguru'],
    },
    'loggers': {
        'gunicorn.error': {
            'level': 'INFO',
            'handlers': ['loguru'],
            'qualname': 'gunicorn.error',
        },
    },
    'handlers': {
        'loguru': {
            'class': 'hagworm.extend.logging.InterceptHandler',
        },
    },
}

DEFAULT_WORKER_STR = r'hagworm.frame.gunicorn.Worker'


class Worker(UvicornWorker):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.config.server_header = False