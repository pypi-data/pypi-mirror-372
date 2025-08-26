# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import yarl
import logging
import asyncio
import aio_pika


aio_pika.logger.setLevel(logging.INFO)


def create_connection(
        url: yarl.URL, timeout: aio_pika.abc.TimeoutType = None, **kwargs
) -> aio_pika.RobustConnection:

    connection: aio_pika.RobustConnection = aio_pika.RobustConnection(url, **kwargs)

    asyncio.create_task(connection.connect(timeout))

    return connection
