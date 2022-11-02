import bpy as _bpy
import functools as _functools
import typing as _typing

from . import enums as _enums
from . import *


def configure_driver(
    driver: _bpy.types.Driver, *, id_type: _enums.IDType, id: _bpy.types.ID, data_path: str,
    var_name: str = 'var', expr: str | None = None
) -> None:
    driver.expression = var_name if expr is None else expr
    driver.type = _enums.Driver.Type.AVERAGE if expr is None else _enums.Driver.Type.SCRIPTED
    driver.use_self = False if expr is None else 'self' in expr

    variables: Intersection[_bpy.types.ChannelDriverVariables,
                            _bpy.types.bpy_prop_collection[_bpy.types.DriverVariable]] = intersection2(driver.variables)
    clear(variables[1])

    variable: _bpy.types.DriverVariable = variables[0].new()
    variable.name = var_name
    variable.type = _enums.DriverVariable.Type.SINGLE_PROP

    target: _bpy.types.DriverTarget = variable.targets[0]
    target.id_type = id_type
    target.id = id
    target.data_path = data_path


def has_driver(id: _bpy.types.ID, data_path: str) -> bool:
    animd: _bpy.types.AnimData | None = getattr(id, 'animation_data', None)
    if animd is None:
        return False
    return any(driver.data_path == data_path for driver in animd.drivers)


def register_class(cls: type) -> None:
    (_bpy.utils.register_class  # type: ignore
     )(cls)


def unregister_class(cls: type[_bpy.types.bpy_struct]) -> None:
    # wtf: https://blender.stackexchange.com/a/124838
    if issubclass(cls, _bpy.types.Operator):
        bl_idname_parts: _typing.MutableSequence[str] = cls.bl_idname.split(
            '.')
        bl_idname_parts[0] = bl_idname_parts[0].upper()
        rna_id: str = '_OT_'.join(bl_idname_parts)
    else:
        rna_id = getattr(cls, 'bl_idname')

    (_bpy.utils.unregister_class  # type: ignore
     )((cls.bl_rna_get_subclass_py  # type: ignore
        )(rna_id)
       )


def register_classes(classes: _typing.Iterable[type[_bpy.types.bpy_struct]]) -> None:
    cls: type[_bpy.types.bpy_struct]
    for cls in classes:
        register_class(cls)


def unregister_classes(classes: _typing.Iterable[type[_bpy.types.bpy_struct]]) -> None:
    cls: type[_bpy.types.bpy_struct]
    for cls in classes:
        unregister_class(cls)


def register_classes_factory(classes: _typing.Sequence[type[_bpy.types.bpy_struct]], *,
                             class_method: bool = False
                             ) -> tuple[_typing.Callable[[], None], _typing.Callable[[], None]]:
    def decorate(func: _typing.Callable[[], None]) -> _typing.Callable[[], None]:
        if class_method:
            func0: classmethod[None] = classmethod(ignore_args(func))
            assert isinstance(func0, _typing.Callable)
            func = func0
        return func
    return (decorate(_functools.partial(register_classes, classes)), _functools.partial(unregister_classes, reversed(classes)))


def ensure_animation_data(id: _bpy.types.ID) -> _bpy.types.AnimData:
    animd: _bpy.types.AnimData | None = getattr(id, 'animation_data', None)
    if animd is None:
        animd = id.animation_data_create()
    return animd


def main(*, register: _typing.Callable[[], None], unregister: _typing.Callable[[], None]) -> None:
    try:
        unregister()
    except Exception:
        pass
    register()
