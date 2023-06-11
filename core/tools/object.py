# -*- coding: bccelerator-transform-UTF-8 -*-
from bmesh import (
    from_edit_mesh as _from_e_mesh,
    update_edit_mesh as _upd_e_mesh,
)
from bmesh.types import BMFace as _BMFace
from bpy.ops import mesh as _mesh, object as _object
from bpy.props import (
    EnumProperty as _EnumProp,  # type: ignore
)
from bpy.types import (
    Context as _Ctx,
    Event as _Evt,
    Mesh as _Mesh,
    Operator as _Op,
)
from idprop.types import IDPropertyGroup as _IDPropGrp
from itertools import islice as _islice
from math import log10 as _log10
from mathutils import Vector as _Vec
from typing import (
    AbstractSet as _Set,
    Annotated as _Annotated,
    Callable as _Callable,
    Collection as _Collect,
    ClassVar as _ClassVar,
    NamedTuple as _NamedTuple,
    cast as _cast,
    final as _final,
)

from ..patches import contains as _contains
from ..utils.data import all as _all
from ..utils.enums import (
    IDType as _IDType,
    ContextMode as _CtxMode,
    Object as _EObj,
    OperatorReturn as _OpReturn,
    OperatorTypeFlag as _OpTypeFlag,
    PropertyFlagEnum as _PropFlag,
    PropertySubtype as _PropStype,
    WMReport as _WMReport,
)
from ..utils.props import enum_property_item as _enum_prop_item
from ..utils.types import (
    Drawer as _Drawer,
    draw_func_class as _draw_func_class,
    internal_operator as _int_op,
)
from ..utils.utils import (
    ensure_animation_data as _ensure_anim_d,
    register_classes_factory as _reg_cls_fac,
)

_MESH_DELETE = _mesh.delete  # type: ignore
_MESH_REMOVE_DOUBLES = _mesh.remove_doubles  # type: ignore
_MESH_SELECT_ALL = _mesh.select_all  # type: ignore
_OBJECT_CONVERT = _object.convert  # type: ignore
_OBJECT_DUPLICATES_MAKE_REAL = _object.duplicates_make_real  # type: ignore
_OBJECT_EDITMODE_TOGGLE = _object.editmode_toggle  # type: ignore
_OBJECT_JOIN = _object.join  # type: ignore
_OBJECT_MAKE_LOCAL = _object.make_local  # type: ignore
_OBJECT_MAKE_SINGLE_USER = _object.make_single_user  # type: ignore
_OBJECT_SELECT_ALL = _object.select_all  # type: ignore
_SELECT_FACE_DOUBLES_TOLERANCE = 0.0001
_SELECT_FACE_DOUBLES_ROUNDING = round(-_log10(_SELECT_FACE_DOUBLES_TOLERANCE) + 1)


def _select_face_doubles(mesh: _Mesh):
    # https://pasteall.org/55201/python
    bm = _from_e_mesh(mesh)
    bm_faces = _cast(_Collect[_BMFace], bm.faces)

    @_final
    class VecFace(_NamedTuple):
        vec: _Vec
        face: _BMFace

    faces = [VecFace(vec=face.calc_center_median(), face=face) for face in bm_faces]

    def vec_x(vec: _Vec):
        return vec.x

    def vec_y(vec: _Vec):
        return vec.y

    def vec_z(vec: _Vec):
        return vec.z

    vec_xyz: tuple[
        _Callable[[_Vec], float],
        _Callable[[_Vec], float],
        _Callable[[_Vec], float],
    ] = (
        vec_x,
        vec_y,
        vec_z,
    )

    # yay, key instead of cmp...
    # no tolerance, precision problems -> round
    for vec_f in vec_xyz:
        faces.sort(key=lambda vf: round(vec_f(vf.vec), _SELECT_FACE_DOUBLES_ROUNDING))

    # find double faces
    for index, vf in _islice(enumerate(faces), 1, None):
        pvf = faces[index - 1]
        if all(
            abs(vec_f(pvf.vec) - vec_f(vf.vec)) < _SELECT_FACE_DOUBLES_TOLERANCE
            for vec_f in vec_xyz
        ):
            vf.face.select = pvf.face.select = True
    _upd_e_mesh(mesh, loop_triangles=False, destructive=False)


class ConfigureEEVEEVolumetrics(_Op):
    """Configure EEVEE volumetrics for selected object(s)"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "object.configure_eevee_volumetrics"
    bl_label: _ClassVar = "Configure EEVEE Volumetrics"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }
    bl_property: _ClassVar = "mode"

    mode_items: _ClassVar = {
        "DISABLE": _enum_prop_item(
            "DISABLE", "Disable", "Disable EEVEE volumetrics", number=0
        ),
        "ENABLE": _enum_prop_item(
            "ENABLE", "Enable", "Enable EEVEE volumetrics", number=1
        ),
        "EEVEE": _enum_prop_item(
            "EEVEE", "EEVEE-Only", "Enable volumetrics for EEVEE only", number=2
        ),
    }
    mode: _Annotated[str, _EnumProp]
    mode_min: _ClassVar = min(value[-1] for value in mode_items.values())
    mode_max: _ClassVar = max(value[-1] for value in mode_items.values())
    mode_name: _ClassVar = "EEVEE volumetrics"

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return bool(context.selected_objects)

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0
        for object in context.selected_objects:
            if self.mode_name in object:
                if object[self.mode_name] == self.mode_items[self.mode][-1]:
                    continue
            else:
                object[self.mode_name] = int()
                object.id_properties_ui(self.mode_name).update(
                    subtype=_PropStype.NONE,
                    min=self.mode_min,
                    max=self.mode_max,
                    soft_min=self.mode_min,
                    soft_max=self.mode_max,
                    step=1,
                    default=self.mode_items["DISABLE"][-1],
                    description="Volumetrics mode for EEVEE",
                )
            object[self.mode_name] = self.mode_items[self.mode][-1]
            processed += 1
            self.report({_WMReport.INFO}, f'Configured object "{object.name_full}"')
        self.report({_WMReport.INFO}, f"Configured {processed} object(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}

    def invoke(  # type: ignore
        self,
        context: _Ctx,
        event: _Evt,
    ):
        return context.window_manager.invoke_props_dialog(self)


ConfigureEEVEEVolumetrics.__annotations__["mode"] = _EnumProp(
    name="EEVEE Volumetrics Mode",
    items=ConfigureEEVEEVolumetrics.mode_items.values(),  # type: ignore
    description="Volumetrics mode for EEVEE for selected object(s)",
    default="DISABLE",
    options={
        _PropFlag.SKIP_SAVE,
    },
)


class MergeWallCollection(_Op):
    """Merge a collection of wall(s) into an object"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "object.merge_wall_collection"
    bl_label: _ClassVar = "Merge Wall Collection"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return (
            context.mode == _CtxMode.OBJECT
            and context.collection
            and "wall" in context.collection.name
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        data = context.blend_data
        scene = context.scene
        collection = context.collection

        instance = data.objects.new("", object_data=None)
        instance.instance_type = _EObj.InstanceType.COLLECTION
        instance.instance_collection = collection
        scene.collection.objects.link(instance)
        _OBJECT_SELECT_ALL(action="DESELECT")
        instance.select_set(True)
        _OBJECT_DUPLICATES_MAKE_REAL()
        data.objects.remove(instance)

        _OBJECT_MAKE_LOCAL(type="SELECT_OBDATA")
        _OBJECT_MAKE_SINGLE_USER(type="SELECTED_OBJECTS", object=True, obdata=True)

        mesh = data.meshes.new(collection.name)
        mesh_obj = data.objects.new(collection.name, object_data=mesh)
        scene.collection.objects.link(mesh_obj)
        mesh_obj.select_set(True)
        context.view_layer.objects.active = mesh_obj
        _OBJECT_CONVERT(target="MESH")
        _OBJECT_JOIN()

        _OBJECT_EDITMODE_TOGGLE()
        _MESH_SELECT_ALL(action="DESELECT")
        _select_face_doubles(mesh)
        _MESH_DELETE(type="FACE")
        _MESH_SELECT_ALL(action="SELECT")
        _MESH_REMOVE_DOUBLES()
        _OBJECT_EDITMODE_TOGGLE()

        return {_OpReturn.FINISHED}


class FixRigifyRigAnimationData(_Op):
    """Fix animation data of selected rig(s) created by Rigify"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "rigify.fix_animation_data"
    bl_label: _ClassVar = "Fix Rigify Rig Animation Data"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _Ctx,
    ) -> bool:
        return bool(
            context.mode == _CtxMode.OBJECT
            and context.selected_objects
            and any("rig_ui" in obj for obj in context.selected_objects)
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0
        for object in (obj for obj in context.selected_objects if "rig_ui" in obj):
            animd = _ensure_anim_d(object)
            targets = 0
            for target in (
                target
                for driver in _ensure_anim_d(object.data).drivers
                for variable in animd.drivers.from_existing(
                    src_driver=driver
                ).driver.variables
                for target in variable.targets
                if target.id_type == _IDType.OBJECT
            ):
                target.id = object
                targets += 1
            processed += 1
            self.report(
                {_WMReport.INFO},
                f'Fixed f{targets} driver target(s) in object "{object.name_full}"',
            )
        self.report({_WMReport.INFO}, f"Fixed {processed} object(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class CleanUpCustomProperties(_Op):
    """Clean up temporary custom properties created by extensions"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "wm.clean_up_custom_properties"
    bl_label: _ClassVar = "Clean Up Custom Properties"
    bl_options: _ClassVar = {
        _OpTypeFlag.REGISTER,
        _OpTypeFlag.UNDO,
    }

    delete_keys: _ClassVar = frozenset(
        {
            # A.N.T. Landscape
            "ant_landscape",
            # RetopoFlow
            "RetopFlow",
            # Archimesh
            "DoorObjectGenerator",
            "WindowObjectGenerator",
            "archimesh.hole_enable",
        }
    )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0
        p_data = 0
        for datum in (
            datum
            for data in _all(context).values()
            for datum in data
            if not datum.library
        ):
            p_keys = 0
            prop = _cast(_IDPropGrp, datum.id_properties_ensure())
            for delete_key in self.delete_keys:
                if _contains(prop, delete_key):
                    val = prop.pop(delete_key, None)
                    p_keys += 1
                    self.report(
                        {_WMReport.INFO},
                        f'Removed custom property "{delete_key}" from data-block "{datum.name_full}": {val}',
                    )
            if p_keys > 0:
                processed += p_keys
                p_data += 1
                self.report(
                    {_WMReport.INFO},
                    f'Removed {p_keys} custom property(s) from data-block "{datum.name_full}"',
                )
        self.report(
            {_WMReport.INFO},
            f"Removed {processed} custom property(s) from {p_data} data-block(s)",
        )
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


@_draw_func_class
@_int_op(uuid="9c6c6894-c400-4edc-a21a-2bcb230c8f2a")
class DrawFunc(_Op):
    __slots__: _ClassVar = ()

    @classmethod
    def VIEW3D_MT_object_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(ConfigureEEVEEVolumetrics.bl_idname)

    @classmethod
    def OUTLINER_MT_context_menu_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        if MergeWallCollection.poll(context):
            self.layout.separator()
            self.layout.operator(MergeWallCollection.bl_idname)

    @classmethod
    def VIEW3D_MT_object_animation_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        if FixRigifyRigAnimationData.poll(context):
            self.layout.separator()
            self.layout.operator(FixRigifyRigAnimationData.bl_idname)

    @classmethod
    def TOPBAR_MT_file_cleanup_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(
            CleanUpCustomProperties.bl_idname, text="Custom Properties"
        )

    @classmethod
    def OUTLINER_MT_collection_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        cls.OUTLINER_MT_context_menu_draw_func(self, context)

    @classmethod
    def OUTLINER_MT_object_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        cls.OUTLINER_MT_context_menu_draw_func(self, context)


register, unregister = _reg_cls_fac(
    (
        CleanUpCustomProperties,
        ConfigureEEVEEVolumetrics,
        MergeWallCollection,
        FixRigifyRigAnimationData,
        DrawFunc,
    )
)
