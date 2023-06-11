# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import idprop as _idprop
import typing as _typing

_T = _typing.TypeVar("_T")
PropCollectionKey = str | tuple[str, _bpy.types.Library | None]


@_typing.overload
def contains(self: _idprop.types.IDPropertyGroup, item: str) -> bool:
    ...


@_typing.overload
def contains(
    self: _bpy.types.bpy_prop_collection[_typing.Any], item: PropCollectionKey
) -> bool:
    ...


def contains(self: _typing.Any, item: _typing.Any):
    return item in self


@_typing.overload
def getitem(  # type: ignore
    self: _bpy.types.bpy_prop_collection[_T],
    key: PropCollectionKey,
) -> _T:
    ...


def getitem(self: _typing.Any, key: _typing.Any):
    return self[key]
