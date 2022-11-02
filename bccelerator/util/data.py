import bpy as _bpy
import re as _re
import types as _types
import typing as _typing

_ExtendsID = _typing.TypeVar('_ExtendsID', bound=_bpy.types.ID)
_type_from_blend_data_exceptions: _typing.Mapping[_bpy.types.bpy_prop_collection[_bpy.types.ID], type[_bpy.types.ID]] = _types.MappingProxyType({
    _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], _bpy.data.fonts): _bpy.types.VectorFont,
    _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], _bpy.data.lightprobes): _bpy.types.LightProbe,
    _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], _bpy.data.linestyles): _bpy.types.FreestyleLineStyle,
    _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], _bpy.data.hair_curves): _bpy.types.Curves,
    _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], _bpy.data.shape_keys): _bpy.types.Key,
})


def _type_from_blend_data(data: _bpy.types.bpy_prop_collection[_ExtendsID]) -> type[_ExtendsID]:
    try:
        return _typing.cast(type[_ExtendsID],
                            _type_from_blend_data_exceptions[_typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID],
                                                                          data)])
    except KeyError:
        pass
    type_name_p: str = getattr(data, 'rna_type').identifier[len('BlendData'):]
    p_type_names: _typing.Sequence[str] = (
        _re.sub('s$', '', type_name_p),
        _re.sub('es$', '', type_name_p),
        _re.sub('ies$', 'y', type_name_p),
        type_name_p,
    )
    result: type[_bpy.types.ID]
    for result in (getattr(_bpy.types, name) for name in p_type_names
                   if hasattr(_bpy.types, name)):
        return _typing.cast(type[_ExtendsID], result)
    raise LookupError(data)


@_typing.final
class _BlendDataAll(dict[type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]]):
    def __missing__(self: _typing.Self, key: type[_bpy.types.ID]) -> _bpy.types.bpy_prop_collection[_bpy.types.ID]:
        exist_key: type[_bpy.types.ID]
        value: _bpy.types.bpy_prop_collection[_bpy.types.ID]
        for exist_key, value in self.items():
            if issubclass(key, exist_key):
                self[key] = value
                return value
        raise KeyError(key)


all: _typing.Mapping[type[_bpy.types.ID], _bpy.types.bpy_prop_collection[_bpy.types.ID]] = _types.MappingProxyType(_BlendDataAll(
    {_type_from_blend_data(_typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], attr)):
     _typing.cast(_bpy.types.bpy_prop_collection[_bpy.types.ID], attr)
     for attr in (getattr(_bpy.data, attr_name) for attr_name in dir(_bpy.data))
     if isinstance(attr, _bpy.types.bpy_prop_collection)}
))
