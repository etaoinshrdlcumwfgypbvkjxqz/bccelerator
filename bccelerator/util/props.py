# -*- coding: bccelerator-transform-UTF-8 -*-
import typing as _typing

EnumPropertyItem3: _typing.TypeAlias = tuple[str, str, str]
EnumPropertyItem4: _typing.TypeAlias = tuple[str, str, str, int]
EnumPropertyItem5: _typing.TypeAlias = tuple[str, str, str, str | int, int]
EnumPropertyItem: _typing.TypeAlias = (
    EnumPropertyItem3 | EnumPropertyItem4 | EnumPropertyItem5
)


@_typing.overload
def enum_property_item(
    identifier: str, name: str, description: str
) -> EnumPropertyItem3:
    ...


@_typing.overload
def enum_property_item(
    identifier: str, name: str, description: str, *, number: int
) -> EnumPropertyItem4:
    ...


@_typing.overload
def enum_property_item(
    identifier: str, name: str, description: str, *, icon: str | int, number: int
) -> EnumPropertyItem5:
    ...


def enum_property_item(
    identifier: str,
    name: str,
    description: str,
    *,
    icon: str | int | None = None,
    number: int | None = None
) -> EnumPropertyItem:
    if icon is None:
        if number is None:
            return (identifier, name, description)
        return (identifier, name, description, number)
    if number is None:
        raise ValueError("number cannot be None if icon is not None")
    return (identifier, name, description, icon, number)
