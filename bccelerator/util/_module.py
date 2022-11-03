# -*- coding: bccelerator-transform-UTF-8 -*-

import bpy as _bpy
import functools as _functools
import itertools as _itertools
import typing as _typing

_T = _typing.TypeVar('_T')
_T2 = _typing.TypeVar('_T2')


def constant(value: _T, /) -> _typing.Callable[..., _T]:
    def ret(*_: _typing.Any) -> _T:
        return value
    return ret


void: _typing.Callable[..., None] = constant(None)


def ignore_args(func: _typing.Callable[[], _T]) -> _typing.Callable[..., _T]:
    @_functools.wraps(func)
    def func0(*_: _typing.Any) -> _T:
        return func()
    return func0


def flatmap(func: _typing.Callable[[_T], _typing.Iterable[_T2]], iterable: _typing.Iterable[_T]) -> _typing.Iterable[_T2]:
    return _itertools.chain.from_iterable(map(func, iterable))


def clear(collection: _typing.Any) -> _typing.Any | None:
    if callable(getattr(collection, 'clear', None)):
        return collection.clear()
    if isinstance(collection, _bpy.types.bpy_prop_collection):
        collection0: _bpy.types.bpy_prop_collection[_typing.Any] = collection
        if callable(getattr(collection0, 'remove', None)):
            item: _typing.Any
            for item in (
                collection0.values()  # type: ignore
            ):
                getattr(collection0, 'remove')(item)
            return
        collection = collection0
    raise TypeError(collection)


Intersection = tuple


def intersection2(value: _T | _T2) -> Intersection[_T, _T2]:
    return (_typing.cast(_T, value), _typing.cast(_T2, value),)
