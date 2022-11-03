# -*- coding: bccelerator-transform-UTF-8 -*-

import bpy as _bpy
import re as _re
import types as _types
import typing as _typing

from ..util import polyfill as _util_polyfill

_type_from_data_name_exceptions: _typing.Mapping[str, type[_bpy.types.ID]] = _types.MappingProxyType({
    'fonts': _bpy.types.VectorFont,
    'lightprobes': _bpy.types.LightProbe,
    'linestyles': _bpy.types.FreestyleLineStyle,
    'hair_curves': _bpy.types.Curves,
    'shape_keys': _bpy.types.Key,
})


def _type_from_data_name(data_name: str) -> type[_bpy.types.ID]:
    try:
        return _type_from_data_name_exceptions[data_name]
    except KeyError:
        pass
    type_name_p: str = data_name.capitalize()
    p_type_names: _typing.Sequence[str] = (
        _re.sub('s$', '', type_name_p),
        _re.sub('es$', '', type_name_p),
        _re.sub('ies$', 'y', type_name_p),
        type_name_p,
    )
    result: type[_bpy.types.ID]
    for result in (getattr(_bpy.types, name) for name in p_type_names
                   if hasattr(_bpy.types, name)):
        return result
    raise LookupError(data_name)


@_typing.final
class _BlendDataAll(dict[type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]]):
    __slots__: _typing.ClassVar = ()

    def __missing__(self: _util_polyfill.Self, key: type[_bpy.types.ID]) -> _bpy.types.bpy_prop_collection[_bpy.types.ID]:
        exist_key: type[_bpy.types.ID]
        value: _bpy.types.bpy_prop_collection[_bpy.types.ID]
        for exist_key, value in self.items():
            if issubclass(key, exist_key):
                self[key] = value
                return value
        raise KeyError(key)


def all(context: _bpy.types.Context
        ) -> _typing.Mapping[type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]]:
    return _types.MappingProxyType(_BlendDataAll(
        {_type_from_data_name(attr): _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], attr)
         for attr in dir(context.blend_data)
         if isinstance(getattr(context.blend_data, attr), _bpy.types.bpy_prop_collection)}
    ))
