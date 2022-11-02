import bpy as _bpy
import functools as _functools
import typing as _typing

from . import *

_T = _typing.TypeVar('_T')


def draw_func_class(cls: type[_T]) -> type[_T]:
    register_0: _typing.Callable[[type[_T]], None] = getattr(
        cls, 'register', classmethod(void)).__func__
    unregister_0: _typing.Callable[[type[_T]], None] = getattr(
        cls, 'unregister', classmethod(void)).__func__

    @classmethod
    @_functools.wraps(register_0)
    def register(cls: type[_T]) -> None:
        register_0(cls)
        func_name: str
        for func_name in (name for name in dir(cls) if '_draw_func' in name):
            getattr(
                _bpy.types, func_name[:-len('_draw_func')]).append(getattr(cls, func_name))

    @classmethod
    @_functools.wraps(unregister_0)
    def unregister(cls: type[_T]) -> None:
        for func_name in (name for name in dir(cls) if '_draw_func' in name):
            getattr(
                _bpy.types, func_name[:-len('_draw_func')]).remove(getattr(cls, func_name))
        unregister_0(cls)

    setattr(cls, 'register', register)
    setattr(cls, 'unregister', unregister)
    return cls


def internal_operator(*, uuid: str) -> _typing.Callable[[type[_T]], type[_T]]:
    def decorator(cls: type[_T]) -> type[_T]:
        setattr(cls, 'bl_idname', f'internal.{uuid.replace("-", "_")}')
        setattr(cls, 'bl_label', '')
        setattr(cls, 'bl_options', frozenset({'INTERNAL'}))
        setattr(cls, 'poll', classmethod(constant(False)))
        return cls
    return decorator
