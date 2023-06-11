# -*- coding: bccelerator-transform-UTF-8 -*-
import bpy as _bpy
import typing as _typing

from .. import patches as _patches
from ..util import enums as _util_enums
from ..util import types as _util_types
from ..util import utils as _util_utils


class MakeLinksByName(_bpy.types.Operator):
    """Make links to selected nodes from the active node by socket name"""

    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar = "node.make_links_by_name"
    bl_label: _typing.ClassVar = "Make Links by Name"
    bl_options: _typing.ClassVar = {
        _util_enums.OperatorTypeFlag.REGISTER,
        _util_enums.OperatorTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _bpy.types.Context,
    ) -> bool:
        return (
            context.space_data
            and context.space_data.type == _util_enums.SpaceType.NODE_EDITOR
            and context.active_node
            and len(context.selected_nodes) >= 2
        )

    def execute(  # type: ignore
        self,
        context: _bpy.types.Context,
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed = 0
        node_tree = _typing.cast(
            _bpy.types.SpaceNodeEditor, context.space_data
        ).edit_tree
        from_node = context.active_node
        from_sockets = from_node.outputs
        for (from_socket, to_socket) in (
            (from_sockets[to_socket.name], to_socket)
            for node in context.selected_nodes
            if node != from_node
            for to_socket in node.inputs
            if _patches.contains(from_sockets, to_socket.name)
        ):
            node_tree.links.new(from_socket, to_socket)
            processed += 1
        self.report({_util_enums.WMReport.INFO}, f"Made {processed} link(s)")
        return (
            {_util_enums.OperatorReturn.FINISHED}
            if processed > 0
            else {_util_enums.OperatorReturn.CANCELLED}
        )


class ConfigurePrincipledMaterialDriver(_bpy.types.Operator):
    """Configure drivers of material properties from active principled node"""

    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar = "node.configure_principled_material_driver"
    bl_label: _typing.ClassVar = "Configure Principled Material Driver(s)"
    bl_options: _typing.ClassVar = {
        _util_enums.OperatorTypeFlag.REGISTER,
        _util_enums.OperatorTypeFlag.UNDO,
    }

    @classmethod
    def poll(  # type: ignore
        cls,
        context: _bpy.types.Context,
    ) -> bool:
        return bool(
            context.space_data
            and context.space_data.type == _util_enums.SpaceType.NODE_EDITOR
            and context.material
            and context.active_node
        )

    def execute(  # type: ignore
        self,
        context: _bpy.types.Context,
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed = 0
        material = context.material
        node = context.active_node
        node_tree = _typing.cast(_bpy.types.NodeTree, node.id_data)
        inputs = node.inputs
        if _patches.contains(inputs, "Base Color") and not _util_utils.has_driver(
            material, "diffuse_color"
        ):
            curves = _typing.cast(
                _typing.Collection[_bpy.types.FCurve],
                material.driver_add("diffuse_color"),
            )
            for index, curve in enumerate(curves):
                _util_utils.configure_driver(
                    curve.driver,
                    id_type=_util_enums.IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Base Color"].default_value[{index}]',
                )
                curve.lock = True
            curves_len = len(curves)
            processed += curves_len
            self.report(
                {_util_enums.WMReport.INFO},
                f"Configured {curves_len} material color driver(s)",
            )
        if _patches.contains(inputs, "Metallic") and not _util_utils.has_driver(
            material, "metallic"
        ):
            curve = material.driver_add("metallic")
            _util_utils.configure_driver(
                curve.driver,
                id_type=_util_enums.IDType.NODETREE,
                id=node_tree,
                data_path=f'nodes["{node.name}"].inputs["Metallic"].default_value',
            )
            curve.lock = True
            processed += 1
            self.report(
                {_util_enums.WMReport.INFO}, "Configured material metallic driver"
            )
        if _patches.contains(inputs, "Roughness") and not _util_utils.has_driver(
            material, "roughness"
        ):
            curve = material.driver_add("roughness")
            _util_utils.configure_driver(
                curve.driver,
                id_type=_util_enums.IDType.NODETREE,
                id=node_tree,
                data_path=f'nodes["{node.name}"].inputs["Roughness"].default_value',
            )
            curve.lock = True
            processed += 1
            self.report(
                {_util_enums.WMReport.INFO}, "Configured material roughness driver"
            )
        if _patches.contains(inputs, "Alpha"):
            if (
                material.blend_method == _util_enums.Material.BlendMethod.OPAQUE
                and not _util_utils.has_driver(material, "blend_method")
            ):
                curve = material.driver_add("blend_method")
                _util_utils.configure_driver(
                    curve.driver,
                    id_type=_util_enums.IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                    expr="0 if var == 1 else 5",
                )
                curve.lock = True
                processed += 1
                self.report(
                    {_util_enums.WMReport.INFO}, "Configured material blend mode driver"
                )
            if (
                material.shadow_method == _util_enums.Material.ShadowMethod.OPAQUE
                and not _util_utils.has_driver(material, "shadow_method")
            ):
                curve = material.driver_add("shadow_method")
                _util_utils.configure_driver(
                    curve.driver,
                    id_type=_util_enums.IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                    expr="1 if var == 1 else 3",
                )
                curve.lock = True
                processed += 1
                self.report(
                    {_util_enums.WMReport.INFO},
                    "Configured material shadow mode driver",
                )
        self.report(
            {_util_enums.WMReport.INFO}, f"Configured {processed} material driver(s)"
        )
        return (
            {_util_enums.OperatorReturn.FINISHED}
            if processed > 0
            else {_util_enums.OperatorReturn.CANCELLED}
        )


@_util_types.draw_func_class
@_util_types.internal_operator(uuid="d409c199-6017-4a76-a2e1-58628b8a76dd")
class DrawFunc(_bpy.types.Operator):
    __slots__: _typing.ClassVar = ()

    @classmethod
    def NODE_MT_node_draw_func(
        cls,
        self: _util_types.Drawer,
        context: _bpy.types.Context,
    ):
        self.layout.separator()
        self.layout.operator(MakeLinksByName.bl_idname)
        if ConfigurePrincipledMaterialDriver.poll(context):
            self.layout.operator(ConfigurePrincipledMaterialDriver.bl_idname)


register, unregister = _util_utils.register_classes_factory(
    (
        MakeLinksByName,
        ConfigurePrincipledMaterialDriver,
        DrawFunc,
    )
)
