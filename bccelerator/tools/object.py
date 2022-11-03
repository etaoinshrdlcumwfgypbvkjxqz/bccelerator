# -*- coding: bccelerator-transform-UTF-8 -*-

# object

import bmesh as _bmesh
import bpy as _bpy
import itertools as _itertools
import math as _math
import mathutils as _mathutils
import types as _types
import typing as _typing

from .. import util as _util
from ..util import enums as _util_enums
from ..util import polyfill as _util_polyfill
from ..util import props as _util_props
from ..util import types as _util_types
from ..util import utils as _util_utils

_select_face_doubles_tolerance: float = 0.0001
_select_face_doubles_rounding: int = round(
    -_math.log(_select_face_doubles_tolerance, 10) + 1)


def _select_face_doubles(mesh: _bpy.types.Mesh) -> None:
    # https://pasteall.org/55201/python
    bm: _bmesh.types.BMesh = _bmesh.from_edit_mesh(mesh)
    bm_faces: _util.Intersection[_typing.Sequence[_bmesh.types.BMFace], _bmesh.types.BMFaceSeq] = _util.intersection2(
        bm.faces  # type: ignore
    )

    @_typing.final
    class VecFace(_typing.NamedTuple):
        vec: _mathutils.Vector
        face: _bmesh.types.BMFace
    faces: _typing.MutableSequence[VecFace] = [
        VecFace(vec=face.calc_center_median(), face=face) for face in bm_faces[0]]

    def vec_x(vec: _mathutils.Vector) -> float: return vec.x
    def vec_y(vec: _mathutils.Vector) -> float: return vec.y
    def vec_z(vec: _mathutils.Vector) -> float: return vec.z
    vec_xyz: tuple[_typing.Callable[[_mathutils.Vector], float], _typing.Callable[[
        _mathutils.Vector], float], _typing.Callable[[_mathutils.Vector], float]] = (vec_x, vec_y, vec_z,)

    # yay, key instead of cmp...
    # no tolerance, precision problems -> round
    vec_f: _typing.Callable[[_mathutils.Vector], float]
    for vec_f in vec_xyz:
        faces.sort(key=lambda vf: round(
            vec_f(vf.vec), _select_face_doubles_rounding))

    # find double faces
    index: int
    vf: VecFace
    for index, vf in _itertools.islice(enumerate(faces), 1, None):
        pvf = faces[index - 1]
        if all(abs(vec_f(pvf.vec) - vec_f(vf.vec)) < _select_face_doubles_tolerance for vec_f in vec_xyz):
            vf.face.select = pvf.face.select = True
    _bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)


class ConfigureEEVEEVolumetrics(_bpy.types.Operator):
    '''Configure EEVEE volumetrics for selected object(s)'''
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'object.configure_eevee_volumetrics'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Configure EEVEE Volumetrics'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({
            _util_enums.OperatorTypeFlag.REGISTER, _util_enums.OperatorTypeFlag.UNDO, })
    )
    bl_property: _typing.ClassVar[str] = (  # type: ignore
        'mode'
    )

    mode_items: _typing.ClassVar[_typing.Mapping[str, _util_props.EnumPropertyItem4]] = _types.MappingProxyType({
        'DISABLE': _util_props.enum_property_item('DISABLE', 'Disable', 'Disable EEVEE volumetrics', number=0),
        'ENABLE': _util_props.enum_property_item('ENABLE', 'Enable', 'Enable EEVEE volumetrics', number=1),
        'EEVEE': _util_props.enum_property_item('EEVEE', 'EEVEE-Only', 'Enable volumetrics for EEVEE only', number=2),
    })
    mode: _typing.Annotated[str,
                            _bpy.props.EnumProperty  # type: ignore
                            ]
    mode_min: _typing.ClassVar[int] = min(
        value[-1] for value in mode_items.values())
    mode_max: _typing.ClassVar[int] = max(
        value[-1] for value in mode_items.values())
    mode_name: _typing.ClassVar[str] = 'EEVEE volumetrics'

    @classmethod
    def poll(  # type: ignore
            cls: type[_util_polyfill.Self], context: _bpy.types.Context
    ) -> bool:
        return bool(context.selected_objects)

    def execute(  # type: ignore
        self: _util_polyfill.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        object: _bpy.types.Object
        for object in context.selected_objects:
            if self.mode_name in object:
                if object[self.mode_name] == self.mode_items[self.mode][-1]:
                    continue
            else:
                object[self.mode_name] = int()
                getattr(object, 'id_properties_ui')(self.mode_name).update(
                    subtype=_util_enums.PropertySubtype.NONE,
                    min=self.mode_min,
                    max=self.mode_max,
                    soft_min=self.mode_min,
                    soft_max=self.mode_max,
                    step=1,
                    default=self.mode_items['DISABLE'][-1],
                    description='Volumetrics mode for EEVEE',
                )
            object[self.mode_name] = self.mode_items[self.mode][-1]
            processed += 1
            self.report({str(_util_enums.WMReport.INFO)},
                        f'Configured object "{object.name_full}"')
        self.report({str(_util_enums.WMReport.INFO)},
                    f'Configured {processed} object(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}

    def invoke(  # type: ignore
        self: _util_polyfill.Self, context: _bpy.types.Context, event: _bpy.types.Event
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        return _typing.cast(_typing.AbstractSet[_util_enums.OperatorReturn], context.window_manager.invoke_props_dialog(self))


ConfigureEEVEEVolumetrics.__annotations__['mode'] = (_bpy.props.EnumProperty  # type: ignore
                                                     )(
    name='EEVEE Volumetrics Mode',
    items=ConfigureEEVEEVolumetrics.mode_items.values(),  # type: ignore
    description='Volumetrics mode for EEVEE for selected object(s)',
    default='DISABLE',
    options={_util_enums.PropertyFlagEnum.SKIP_SAVE, },
)


class MergeWallCollection(_bpy.types.Operator):
    '''Merge a collection of wall(s) into an object'''
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'object.merge_wall_collection'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Merge Wall Collection'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({_util_enums.OperatorTypeFlag.REGISTER,
                  _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
            cls: type[_util_polyfill.Self], context: _bpy.types.Context) -> bool:
        return context.mode == _util_enums.ContextMode.OBJECT and context.collection is not None

    def execute(  # type: ignore
            self: _util_polyfill.Self, context: _bpy.types.Context) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        data: _bpy.types.BlendData = context.blend_data
        scene: _bpy.types.Scene = context.scene
        collection: _bpy.types.Collection = context.collection

        instance = _util.intersection2(data.objects)[0].new(
            '', object_data=_typing.cast(_bpy.types.ID, None))
        instance.instance_type = _util_enums.Object.InstanceType.COLLECTION
        instance.instance_collection = collection
        _util.intersection2(scene.collection.objects)[0].link(instance)
        (_bpy.ops.object.select_all  # type: ignore
         )(action='DESELECT')
        instance.select_set(True)
        (_bpy.ops.object.duplicates_make_real  # type: ignore
         )()
        _util.intersection2(data.objects)[0].remove(instance)

        (_bpy.ops.object.make_local  # type: ignore
         )(type='SELECT_OBDATA')
        (_bpy.ops.object.make_single_user  # type: ignore
         )(type='SELECTED_OBJECTS', object=True, obdata=True)

        mesh = _util.intersection2(data.meshes)[0].new(collection.name)
        mesh_obj = _util.intersection2(data.objects)[0].new(
            collection.name, object_data=mesh)
        _util.intersection2(scene.collection.objects)[0].link(mesh_obj)
        mesh_obj.select_set(True)
        _util.intersection2(context.view_layer.objects)[0].active = mesh_obj
        (_bpy.ops.object.convert  # type: ignore
         )(target='MESH')
        (_bpy.ops.object.join  # type: ignore
         )()

        (_bpy.ops.object.editmode_toggle  # type: ignore
         )()
        (_bpy.ops.mesh.select_all  # type: ignore
         )(action='DESELECT')
        _select_face_doubles(mesh)
        (_bpy.ops.mesh.delete  # type: ignore
         )(type='FACE')
        (_bpy.ops.mesh.select_all  # type: ignore
         )(action='SELECT')
        (_bpy.ops.mesh.remove_doubles  # type: ignore
         )()
        (_bpy.ops.object.editmode_toggle  # type: ignore
         )()

        return {_util_enums.OperatorReturn.FINISHED}


class FixRigifyRigAnimationData(_bpy.types.Operator):
    '''Fix animation data of selected rig(s) created by Rigify'''
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'rigify.fix_animation_data'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Fix Rigify Rig Animation Data'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({_util_enums.OperatorTypeFlag.REGISTER,
                  _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
            cls: type[_util_polyfill.Self], context: _bpy.types.Context) -> bool:
        return (context.mode == _util_enums.ContextMode.OBJECT
                and bool(context.selected_objects)
                and any('rig_ui' in obj for obj in context.selected_objects))

    def execute(  # type: ignore
        self: _util_polyfill.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        object: _bpy.types.Object
        for object in (obj for obj in context.selected_objects if 'rig_ui' in obj):
            animd: _bpy.types.AnimData = _util_utils.ensure_animation_data(
                object)
            targets: int = 0
            target: _bpy.types.DriverTarget
            for target in (target
                           for driver in _util.intersection2(_util_utils.ensure_animation_data(object.data).drivers)[1]
                           for variable in _util.intersection2(_util.intersection2(animd.drivers)[0].from_existing(src_driver=driver).driver.variables)[1]
                           for target in variable.targets if target.id_type == _util_enums.IDType.OBJECT
                           ):
                target.id = object
                targets += 1
            processed += 1
            self.report({str(_util_enums.WMReport.INFO)},
                        f'Fixed f{targets} driver target(s) in object "{object.name_full}"')
        self.report({str(_util_enums.WMReport.INFO)},
                    f'Fixed {processed} object(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}


@_util_types.draw_func_class
@_util_types.internal_operator(uuid='9c6c6894-c400-4edc-a21a-2bcb230c8f2a')
class DrawFunc(_bpy.types.Operator):
    @classmethod
    def VIEW3D_MT_object_draw_func(cls: type[_util_polyfill.Self], self: _typing.Any, context: _bpy.types.Context) -> None:
        layout: _bpy.types.UILayout = self.layout
        layout.separator()
        layout.operator(ConfigureEEVEEVolumetrics.bl_idname)

    @classmethod
    def VIEW3D_MT_object_collection_draw_func(cls: type[_util_polyfill.Self], self: _typing.Any, context: _bpy.types.Context) -> None:
        layout: _bpy.types.UILayout = self.layout
        layout.separator()
        layout.operator(MergeWallCollection.bl_idname)

    @classmethod
    def VIEW3D_MT_object_animation_draw_func(cls: type[_util_polyfill.Self], self: _typing.Any, context: _bpy.types.Context) -> None:
        layout: _bpy.types.UILayout = self.layout
        if FixRigifyRigAnimationData.poll(context):
            layout.separator()
            layout.operator(FixRigifyRigAnimationData.bl_idname)


register: _typing.Callable[[], None]
unregister: _typing.Callable[[], None]
register, unregister = _util_utils.register_classes_factory((
    ConfigureEEVEEVolumetrics,
    MergeWallCollection,
    FixRigifyRigAnimationData,
    DrawFunc,
))
