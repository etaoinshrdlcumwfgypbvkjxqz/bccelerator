# -*- coding: bccelerator-transform-UTF-8 -*-
from typing import overload as _overload

EnumPropertyItem3 = tuple[str, str, str]
EnumPropertyItem4 = tuple[str, str, str, int]
EnumPropertyItem5 = tuple[str, str, str, str | int, int]
EnumPropertyItem = EnumPropertyItem3 | EnumPropertyItem4 | EnumPropertyItem5


@_overload
def enum_property_item(
    identifier: str, name: str, description: str
) -> EnumPropertyItem3:
    ...


@_overload
def enum_property_item(
    identifier: str, name: str, description: str, *, number: int
) -> EnumPropertyItem4:
    ...


@_overload
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
):
    if icon is None:
        if number is None:
            return (identifier, name, description)
        return (identifier, name, description, number)
    if number is None:
        raise ValueError("number cannot be None if icon is not None")
    return (identifier, name, description, icon, number)
