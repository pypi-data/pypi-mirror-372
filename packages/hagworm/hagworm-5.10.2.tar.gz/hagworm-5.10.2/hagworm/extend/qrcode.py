# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

import qrcode

from io import BytesIO
from qrcode.image.svg import SvgPathImage


class QRCode:

    @staticmethod
    def make(data: typing.Any, **kwargs) -> bytes:

        code_img = BytesIO()

        qrcode.make(data, **kwargs).save(code_img)

        return code_img.getvalue()

    @staticmethod
    def make_svg(data: typing.Any, **kwargs) -> str:

        code_img = BytesIO()

        kwargs[r'image_factory'] = SvgPathImage

        qrcode.make(data, **kwargs).save(code_img)

        return code_img.getvalue().decode()
