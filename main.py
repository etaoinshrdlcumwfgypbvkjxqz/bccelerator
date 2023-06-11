# -*- coding: bccelerator-transform-UTF-8 -*-
from .core.tools import items as _items

_modules = tuple(_items())


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
