# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.types import Library as _Lib, bpy_prop_collection as _bpy_collect
from idprop.types import IDPropertyGroup as _IDPropGrp
from typing import Any as _Any, TypeVar as _TypeVar, overload as _overload

_T = _TypeVar("_T")
PropCollectionKey = str | tuple[str, _Lib | None]


@_overload
def contains(self: _IDPropGrp, item: str) -> bool:
    ...


@_overload
def contains(self: _bpy_collect[_Any], item: PropCollectionKey) -> bool:
    ...


def contains(self: _Any, item: _Any):
    return item in self


@_overload
def getitem(  # type: ignore
    self: _bpy_collect[_T],
    key: PropCollectionKey,
) -> _T:
    ...


def getitem(self: _Any, key: _Any):
    return self[key]
