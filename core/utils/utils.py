# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy import types as _types
from bpy.types import (
    bpy_struct as _bpy_struct,
    AnimData as _AnimData,
    Driver as _Driver,
    ID as _ID,
    Operator as _Op,
)
from bpy.utils import (
    register_class as _reg_class,
    unregister_class as _unreg_class,  # type: ignore
)
from functools import partial as _partial
from typing import Callable as _Callable, Iterable as _Iter, Sequence as _Seq

from .enums import (
    Driver as _EDriver,
    DriverVariable as _EDriverVariable,
    IDType as _IDType,
)
from . import clear as _clear


def configure_driver(
    driver: _Driver,
    *,
    id_type: _IDType,
    id: _ID,
    data_path: str,
    var_name: str = "var",
    expr: str | None = None
):
    driver.expression = var_name if expr is None else expr
    driver.type = _EDriver.Type.AVERAGE if expr is None else _EDriver.Type.SCRIPTED
    driver.use_self = False if expr is None else "self" in expr

    variables = driver.variables
    _clear(variables)

    variable = variables.new()
    variable.name = var_name
    variable.type = _EDriverVariable.Type.SINGLE_PROP

    target = variable.targets[0]
    target.id_type = id_type
    target.id = id
    target.data_path = data_path


def has_driver(id: _ID, data_path: str):
    animd: _AnimData | None = getattr(id, "animation_data", None)
    if animd is None:
        return False
    return any(driver.data_path == data_path for driver in animd.drivers)


def register_class(cls: type):
    _reg_class(cls)


def unregister_class(cls: type[_bpy_struct]):
    # wtf: https://blender.stackexchange.com/a/124838
    if issubclass(cls, _Op):
        bl_idname_parts = cls.bl_idname.split(".", 2)
        bl_idname_parts[0] = bl_idname_parts[0].upper()
        rna_id = "_OT_".join(bl_idname_parts)
    else:
        rna_id = getattr(cls, "bl_idname")
    _unreg_class(getattr(_types, rna_id))


def register_classes(classes: _Iter[type[_bpy_struct]]):
    for cls in classes:
        register_class(cls)


def unregister_classes(classes: _Iter[type[_bpy_struct]]):
    for cls in classes:
        unregister_class(cls)


def register_classes_factory(
    classes: _Seq[type[_bpy_struct]],
) -> tuple[_Callable[[], None], _Callable[[], None]]:
    return (
        _partial(register_classes, classes),
        _partial(unregister_classes, tuple(reversed(classes))),
    )


def ensure_animation_data(id: _ID) -> _AnimData:
    animd: _AnimData | None = getattr(id, "animation_data", None)
    if animd is None:
        animd = id.animation_data_create()
    return animd
