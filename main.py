# -*- coding: bccelerator-transform-UTF-8 -*-
import types as _types
import typing as _typing

from .bccelerator import tools as _bccelerator_tools

_modules: _typing.Collection[_types.ModuleType] = tuple(_bccelerator_tools.items())


def register() -> None:
    module: _types.ModuleType
    for module in _modules:
        module.register()


def unregister() -> None:
    module: _types.ModuleType
    for module in reversed(_modules):
        module.unregister()
