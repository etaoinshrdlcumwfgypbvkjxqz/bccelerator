import bpy as _bpy
import typing as _typing

_T = _typing.TypeVar('_T')


@_typing.overload
def get(prop: _bpy.types.EnumProperty, /, *, t: type[_T] | None = None) -> _T:
    ...


@_typing.overload
def get(prop: _bpy.types.BoolProperty, /) -> bool:
    ...


def get(prop: _typing.Any, /, *, t: type | None = None) -> _typing.Any:
    if t is not None:
        assert isinstance(prop, t)
    return prop


@_typing.final
class EnumPropertyItem(_typing.NamedTuple, _typing.Generic[_T]):
    identifier: _T
    name: str
    description: str
    icon: str | int | None = None
    number: int | None = None
