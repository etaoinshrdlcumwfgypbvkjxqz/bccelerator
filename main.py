# -*- coding: bccelerator-transform-UTF-8 -*-
from .core import tools as _core_tools

_modules = tuple(_core_tools.items())


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
