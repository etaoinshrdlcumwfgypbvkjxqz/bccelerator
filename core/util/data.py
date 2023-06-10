# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import dataclasses as _dataclasses
import re as _re
import types as _types
import typing as _typing

from ..util import polyfill as _util_polyfill


@_typing.final
@_dataclasses.dataclass(
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
    pattern: _re.Pattern[str]
    replacement: str

    def apply(self: _util_polyfill.Self, string: str) -> str:
        return self.pattern.sub(self.replacement, string)


_plural_transforms: _typing.Sequence[_RegexTransform] = (
    _RegexTransform(pattern=_re.compile(r"s$", flags=0), replacement=""),
    _RegexTransform(pattern=_re.compile(r"es$", flags=0), replacement=""),
    _RegexTransform(pattern=_re.compile(r"ies$", flags=0), replacement="y"),
    _RegexTransform(pattern=_re.compile(r"^\b$", flags=0), replacement=""),
)
_caseless_types: _typing.Mapping[str, str] = _types.MappingProxyType(
    {attr.casefold(): attr for attr in dir(_bpy.types)}
)
_type_from_data_name_exceptions: _typing.Mapping[
    str, type[_bpy.types.ID]
] = _types.MappingProxyType(
    {
        "fonts": _bpy.types.VectorFont,
        "linestyles": _bpy.types.FreestyleLineStyle,
        "hair_curves": _bpy.types.Curves,
        "shape_keys": _bpy.types.Key,
    }
)


def _type_from_data_name(key: str) -> type[_bpy.types.ID]:
    try:
        return _type_from_data_name_exceptions[key]
    except KeyError:
        pass
    tfed_key: str = key.replace("_", "").casefold()
    names: _typing.Iterator[str] = (tf.apply(tfed_key) for tf in _plural_transforms)
    try:
        return next(
            getattr(_bpy.types, _caseless_types[name])
            for name in names
            if name in _caseless_types
        )
    except StopIteration as ex:
        raise LookupError(
            key, tfed_key, tuple(tf.apply(tfed_key) for tf in _plural_transforms)
        ) from ex


@_typing.final
class _BlendDataAll(
    dict[type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]]
):
    __slots__: _typing.ClassVar = ()

    def __missing__(
        self: _util_polyfill.Self, key: type[_bpy.types.ID]
    ) -> _bpy.types.bpy_prop_collection[_bpy.types.ID]:
        exist_key: type[_bpy.types.ID]
        value: _bpy.types.bpy_prop_collection[_bpy.types.ID]
        for exist_key, value in self.items():
            if issubclass(key, exist_key):
                self[key] = value
                return value
        raise KeyError(key)


def all(
    context: _bpy.types.Context,
) -> _typing.Mapping[
    type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]
]:
    return _types.MappingProxyType(
        _BlendDataAll(
            {
                _type_from_data_name(attr): getattr(context.blend_data, attr)
                for attr in dir(context.blend_data)
                if isinstance(
                    getattr(context.blend_data, attr), _bpy.types.bpy_prop_collection
                )
            }
        )
    )
