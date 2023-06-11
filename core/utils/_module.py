# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.types import bpy_prop_collection as _bpy_collect
from functools import wraps as _wraps
from itertools import chain as _chain
from typing import (
    Any as _Any,
    Callable as _Callable,
    Iterable as _Iter,
    TypeVar as _TypeVar,
)

_T = _TypeVar("_T")
_T2 = _TypeVar("_T2")
_SENTINEL = object()


def constant(value: _T, /) -> _Callable[..., _T]:
    def ret(*_: _Any):
        return value

    return ret


VOID = constant(None)


def ignore_args(func: _Callable[[], _T]) -> _Callable[..., _T]:
    @_wraps(func)
    def func0(*_: _Any):
        return func()

    return func0


def flatmap(func: _Callable[[_T], _Iter[_T2]], iterable: _Iter[_T]) -> _Iter[_T2]:
    return _chain.from_iterable(map(func, iterable))


def clear(collection: _Any) -> _Any | None:
    if callable(getattr(collection, "clear", None)):
        return collection.clear()
    if isinstance(collection, _bpy_collect):
        collection0: _bpy_collect[_Any] = collection
        if callable(getattr(collection0, "remove", None)):
            for item in collection0:
                getattr(collection0, "remove")(item)
            return
        collection = collection0
    raise TypeError(collection)


def copy_attr(to_obj: object, name: str, from_obj: object, default: _Any = _SENTINEL):
    setattr(
        to_obj,
        name,
        getattr(from_obj, name)
        if default is _SENTINEL
        else getattr(from_obj, name, default),
    )


def copy_attrs(
    to_obj: object,
    names: _Iter[str],
    from_obj: object,
    default: _Any = _SENTINEL,
):
    for name in names:
        copy_attr(to_obj, name, from_obj, default)
