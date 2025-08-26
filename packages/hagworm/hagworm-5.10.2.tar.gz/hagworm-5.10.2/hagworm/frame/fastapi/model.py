# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import typing

from inspect import Signature, Parameter

# noinspection PyProtectedMember
from pydantic._internal._model_construction import ModelMetaclass as _ModelMetaclass
from pydantic.main import BaseModel as _BaseModel

from fastapi.params import Depends as _Depends


class ModelMetaclass(_ModelMetaclass):

    def __init__(
        cls,
        cls_name: str,
        bases: typing.Tuple[typing.Type[typing.Any], ...],
        namespace: typing.Dict[str, typing.Any]
    ):

        super().__init__(cls_name, bases, namespace)

        if cls.model_fields:

            # 原始参数类型清单
            annotations = typing.get_type_hints(cls)

            func_params = []

            for name, field in cls.model_fields.items():

                func_params.append(
                    Parameter(
                        name, Parameter.POSITIONAL_OR_KEYWORD,
                        default=field,
                        annotation=annotations.get(name, Parameter.empty)
                    )
                )

            # 更新类方法
            cls.params = lambda **kwargs: kwargs
            cls.params.__signature__ = Signature(func_params)


class BaseModel(_BaseModel, metaclass=ModelMetaclass):
    pass


class Depends(_Depends):

    def __init__(self, dependency: typing.Union[typing.Callable, BaseModel] = None, *, use_cache: bool = True):

        if isinstance(dependency, ModelMetaclass):
            super().__init__(dependency=dependency.params, use_cache=use_cache)
        else:
            super().__init__(dependency=dependency, use_cache=use_cache)
