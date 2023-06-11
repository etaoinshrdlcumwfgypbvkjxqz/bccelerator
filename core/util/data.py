# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy import types as _types
from bpy.types import (
    Context as _Ctx,
    Curves as _Curves,
    FreestyleLineStyle as _FreestyleLineStyle,
    ID as _ID,
    Key as _Key,
    VectorFont as _VecFont,
    bpy_prop_collection as _bpy_collect,
)
from dataclasses import dataclass as _dataclass
from re import Pattern as _Pattern, compile as _compile
from typing import ClassVar as _ClassVar, Mapping as _Map, final as _final


@_final
@_dataclass(
    init=True,
    repr=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    frozen=True,
    match_args=True,
    kw_only=True,
    slots=True,
)
class _RegexTransform:
    pattern: _Pattern[str]
    replacement: str

    def apply(self, string: str):
        return self.pattern.sub(self.replacement, string)


_plural_transforms = (
    _RegexTransform(pattern=_compile(r"s$", flags=0), replacement=""),
    _RegexTransform(pattern=_compile(r"es$", flags=0), replacement=""),
    _RegexTransform(pattern=_compile(r"ies$", flags=0), replacement="y"),
    _RegexTransform(pattern=_compile(r"^\b$", flags=0), replacement=""),
)
_caseless_types = {attr.casefold(): attr for attr in dir(_types)}
_type_from_data_name_exceptions = {
    "fonts": _VecFont,
    "linestyles": _FreestyleLineStyle,
    "hair_curves": _Curves,
    "shape_keys": _Key,
}


def _type_from_data_name(key: str) -> type[_ID]:
    try:
        return _type_from_data_name_exceptions[key]
    except KeyError:
        pass
    tfed_key = key.replace("_", "").casefold()
    names = tuple(tf.apply(tfed_key) for tf in _plural_transforms)
    try:
        return next(
            getattr(_types, _caseless_types[name])
            for name in names
            if name in _caseless_types
        )
    except StopIteration as ex:
        raise LookupError(key, tfed_key, names) from ex


@_final
class _BlendDataAll(dict[type[_ID], _bpy_collect[_ID]]):
    __slots__: _ClassVar = ()

    def __missing__(self, key: type[_ID]):
        for exist_key, value in self.items():
            if issubclass(key, exist_key):
                self[key] = value
                return value
        raise KeyError(key)


def all(
    context: _Ctx,
) -> _Map[type[_ID], _bpy_collect[_ID]]:
    return _BlendDataAll(
        {
            _type_from_data_name(attr): getattr(context.blend_data, attr)
            for attr in dir(context.blend_data)
            if isinstance(getattr(context.blend_data, attr), _bpy_collect)
        }
    )
