# -*- coding: bccelerator-transform-UTF-8 -*-
import types as _types
import typing as _typing

from .core import tools as _core_tools

_modules: _typing.Collection[_types.ModuleType] = tuple(_core_tools.items())


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
