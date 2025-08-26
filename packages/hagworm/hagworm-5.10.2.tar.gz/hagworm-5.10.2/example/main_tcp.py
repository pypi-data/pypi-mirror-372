# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import os
import sys
import asyncio

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../'))

from hagworm.extend.asyncio.base import Utils
from hagworm.extend.asyncio.socket import AsyncTcpServer


async def connection_handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

    client_info = writer.transport.get_extra_info(r'socket').getpeername()

    Utils.log.info(f'create connection: {client_info}')

    try:

        while True:

                request = await reader.readline()

                if not request:
                    break

                writer.write(request)

                await writer.drain()

    except Exception as err:

        Utils.log.error(err)

    finally:

        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

    Utils.log.info(f'lost connection: {client_info}')


def main():

    server = AsyncTcpServer(connection_handle, (r'0.0.0.0', 8080))
    server.run()


if __name__ == r'__main__':

    main()
