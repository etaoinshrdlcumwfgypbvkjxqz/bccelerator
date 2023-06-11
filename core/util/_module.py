# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import functools as _functools
import itertools as _itertools
import typing as _typing

_T = _typing.TypeVar("_T")
_T2 = _typing.TypeVar("_T2")
_SENTINEL = object()


def constant(value: _T, /) -> _typing.Callable[..., _T]:
    def ret(*_: _typing.Any):
        return value

    return ret


VOID = constant(None)


def ignore_args(func: _typing.Callable[[], _T]) -> _typing.Callable[..., _T]:
    @_functools.wraps(func)
    def func0(*_: _typing.Any):
        return func()

    return func0


def flatmap(
    func: _typing.Callable[[_T], _typing.Iterable[_T2]], iterable: _typing.Iterable[_T]
) -> _typing.Iterable[_T2]:
    return _itertools.chain.from_iterable(map(func, iterable))


def clear(collection: _typing.Any) -> _typing.Any | None:
    if callable(getattr(collection, "clear", None)):
        return collection.clear()
    if isinstance(collection, _bpy.types.bpy_prop_collection):
        collection0: _bpy.types.bpy_prop_collection[_typing.Any] = collection
        if callable(getattr(collection0, "remove", None)):
            for item in collection0:
                getattr(collection0, "remove")(item)
            return
        collection = collection0
    raise TypeError(collection)


def copy_attr(
    to_obj: object, name: str, from_obj: object, default: _typing.Any = _SENTINEL
):
    setattr(
        to_obj,
        name,
        getattr(from_obj, name)
        if default is _SENTINEL
        else getattr(from_obj, name, default),
    )


def copy_attrs(
    to_obj: object,
    names: _typing.Iterable[str],
    from_obj: object,
    default: _typing.Any = _SENTINEL,
):
    for name in names:
        copy_attr(to_obj, name, from_obj, default)
