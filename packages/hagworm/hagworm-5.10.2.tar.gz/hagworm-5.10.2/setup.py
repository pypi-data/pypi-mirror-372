# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import setuptools

from hagworm import __version__


with open(r'README.md', encoding=r'utf8') as stream:
    long_description = stream.read()

setuptools.setup(
    name=r'hagworm',
    version=__version__,
    license=r'Apache License Version 2.0',
    platforms=[r'all'],
    author=r'Shaobo.Wang',
    author_email=r'wsb310@gmail.com',
    description=r'Network Development Suite',
    long_description=long_description,
    long_description_content_type=r'text/markdown',
    url=r'https://gitee.com/wsb310/hagworm',
    packages=setuptools.find_packages(),
    package_data={r'hagworm': [r'static/*.*']},
    python_requires=r'>=3.10',
    install_requires=[
        r'Cython==3.0.10',
        r'APScheduler==3.10.4',
        r'ahocorasick-rs==0.22.0',
        r'Pillow==10.4.0',
        r'PyJWT==2.8.0',
        r'PyYAML==6.0.1',
        r'SQLAlchemy==2.0.31',
        r'coredis==4.17.0',
        r'asyncmy==0.2.9',
        r'aiosmtplib==3.0.1',
        r'aio-pika==9.4.2',
        r'cachetools==5.3.3',
        r'confluent-kafka==2.5.0',
        r'cryptography==42.0.8',
        r'elasticsearch==8.12.1',
        r'fastapi==0.111.1',
        r'filelock==3.15.4',
        r'gunicorn==22.0.0',
        r'grpcio==1.60.0',
        r'httpx==0.27.0',
        r'httptools==0.6.1',
        r'igraph==0.11.6',
        r'loguru==0.7.2',
        r'motor==3.5.1',
        r'msgpack==1.0.8',
        r'ntplib==0.4.0',
        r'psutil==6.0.0',
        r'pandas==2.2.2',
        r'pytest-asyncio==0.23.7',
        r'python-dateutil==2.8.2',
        r'python-stdnum==1.20',
        r'python-multipart==0.0.9',
        r'pymongo==4.8.0',
        r'qrcode==7.4.2',
        r'texttable==1.7.0',
        r'ujson==5.10.0',
        r'uvicorn[standard]==0.30.1',
        r'uvicorn-worker==0.2.0',
        r'uvloop==0.19.0;sys_platform!="win32"',
        r'xmltodict==0.13.0',
    ],
    classifiers=[
        r'Programming Language :: Python :: 3.10',
        r'License :: OSI Approved :: Apache Software License',
        r'Operating System :: POSIX :: Linux',
    ],
)
