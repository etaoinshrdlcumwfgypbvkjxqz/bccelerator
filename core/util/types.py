# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy import types as _types
from bpy.types import Context as _Ctx, UILayout as _UILayout
from functools import wraps as _wraps
from typing import (
    Callable as _Callable,
    Protocol as _Protocol,
    TypeVar as _TypeVar,
    final as _final,
)

from . import VOID as _VOID
from .enums import OperatorTypeFlag as _OpTypeFlag

_T = _TypeVar("_T")


@_final
class Drawer(_Protocol):
    @property
    def layout(self) -> _UILayout:
        ...


def draw_func_class(cls: type[_T]) -> type[_T]:
    register_0 = getattr(cls, "register", classmethod(_VOID)).__func__
    unregister_0 = getattr(cls, "unregister", classmethod(_VOID)).__func__

    registry = dict[str, _Callable[[Drawer, _Ctx], None]]()

    @classmethod
    @_wraps(register_0)
    def register(cls: type[_T]):
        register_0(cls)
        for func_name in dir(cls):
            if "_draw_func" in func_name and func_name not in registry:
                func = getattr(cls, func_name)

                @_wraps(func)
                def wrapper(
                    self: Drawer,
                    context: _Ctx,
                    *,
                    __func: _Callable[[Drawer, _Ctx], None] = func,
                ) -> None:
                    __func(self, context)

                registry[func_name] = wrapper
                getattr(_types, func_name[: -len("_draw_func")]).append(wrapper)

    @classmethod
    @_wraps(unregister_0)
    def unregister(cls: type[_T]):
        for func_name, func in registry.items():
            getattr(_types, func_name[: -len("_draw_func")]).remove(func)
        registry.clear()
        unregister_0(cls)

    setattr(cls, "register", register)
    setattr(cls, "unregister", unregister)
    return cls


def internal_operator(*, uuid: str):
    def decorator(cls: type[_T]) -> type[_T]:
        setattr(cls, "bl_idname", f'internal.{uuid.replace("-", "_")}')
        setattr(cls, "bl_label", "")
        setattr(cls, "bl_options", frozenset({_OpTypeFlag.INTERNAL}))

        @classmethod
        def poll(cls: type[_T], context: _Ctx) -> bool:
            return False

        setattr(cls, "poll", poll)
        return cls

    return decorator
