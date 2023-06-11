# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import functools as _functools
import typing as _typing

from . import *
from . import enums as _enums

_T = _typing.TypeVar("_T")


@_typing.final
class Drawer(_typing.Protocol):
    @property
    def layout(self) -> _bpy.types.UILayout:
        ...


def draw_func_class(cls: type[_T]) -> type[_T]:
    register_0 = getattr(cls, "register", classmethod(VOID)).__func__
    unregister_0 = getattr(cls, "unregister", classmethod(VOID)).__func__

    registry: _typing.MutableMapping[
        str, _typing.Callable[[Drawer, _bpy.types.Context], None]
    ] = {}

    @classmethod
    @_functools.wraps(register_0)
    def register(cls: type[_T]):
        register_0(cls)
        for func_name in dir(cls):
            if "_draw_func" in func_name and func_name not in registry:
                func = getattr(cls, func_name)

                @_functools.wraps(func)
                def wrapper(
                    self: Drawer,
                    context: _bpy.types.Context,
                    *,
                    __func: _typing.Callable[[Drawer, _bpy.types.Context], None] = func,
                ) -> None:
                    __func(self, context)

                registry[func_name] = wrapper
                getattr(_bpy.types, func_name[: -len("_draw_func")]).append(wrapper)

    @classmethod
    @_functools.wraps(unregister_0)
    def unregister(cls: type[_T]):
        for func_name, func in registry.items():
            getattr(_bpy.types, func_name[: -len("_draw_func")]).remove(func)
        registry.clear()
        unregister_0(cls)

    setattr(cls, "register", register)
    setattr(cls, "unregister", unregister)
    return cls


def internal_operator(*, uuid: str):
    def decorator(cls: type[_T]) -> type[_T]:
        setattr(cls, "bl_idname", f'internal.{uuid.replace("-", "_")}')
        setattr(cls, "bl_label", "")
        setattr(cls, "bl_options", frozenset({_enums.OperatorTypeFlag.INTERNAL}))

        @classmethod
        def poll(cls: type[_T], context: _bpy.types.Context) -> bool:
            return False

        setattr(cls, "poll", poll)
        return cls

    return decorator
