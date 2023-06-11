# -*- coding: bccelerator-transform-UTF-8 -*-
from bpy.types import (
    Context as _Ctx,
    FCurve as _FCurve,
    NodeTree as _NodeTree,
    Operator as _Op,
    SpaceNodeEditor as _SpaceNodeEditor,
)
from typing import (
    AbstractSet as _Set,
    Collection as _Collect,
    ClassVar as _ClassVar,
    cast as _cast,
)

from ..patches import contains as _contains
from ..util.enums import (
    IDType as _IDType,
    Material as _Mat,
    OperatorReturn as _OpReturn,
    OperatorTypeFlag as _OpTypeFlag,
    SpaceType as _SpaceType,
    WMReport as _WMReport,
)
from ..util.types import (
    Drawer as _Drawer,
    draw_func_class as _draw_func_class,
    internal_operator as _int_op,
)
from ..util.utils import (
    configure_driver as _cfg_drv,
    has_driver as _has_drv,
    register_classes_factory as _reg_cls_fac,
)


class MakeLinksByName(_Op):
    """Make links to selected nodes from the active node by socket name"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "node.make_links_by_name"
    bl_label: _ClassVar = "Make Links by Name"
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
            context.space_data
            and context.space_data.type == _SpaceType.NODE_EDITOR
            and context.active_node
            and len(context.selected_nodes) >= 2
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0
        node_tree = _cast(_SpaceNodeEditor, context.space_data).edit_tree
        from_node = context.active_node
        from_sockets = from_node.outputs
        for (from_socket, to_socket) in (
            (from_sockets[to_socket.name], to_socket)
            for node in context.selected_nodes
            if node != from_node
            for to_socket in node.inputs
            if _contains(from_sockets, to_socket.name)
        ):
            node_tree.links.new(from_socket, to_socket)
            processed += 1
        self.report({_WMReport.INFO}, f"Made {processed} link(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


class ConfigurePrincipledMaterialDriver(_Op):
    """Configure drivers of material properties from active principled node"""

    __slots__: _ClassVar = ()
    bl_idname: _ClassVar = "node.configure_principled_material_driver"
    bl_label: _ClassVar = "Configure Principled Material Driver(s)"
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
            context.space_data
            and context.space_data.type == _SpaceType.NODE_EDITOR
            and context.material
            and context.active_node
        )

    def execute(  # type: ignore
        self,
        context: _Ctx,
    ) -> _Set[_OpReturn]:
        processed = 0
        material = context.material
        node = context.active_node
        node_tree = _cast(_NodeTree, node.id_data)
        inputs = node.inputs
        if _contains(inputs, "Base Color") and not _has_drv(material, "diffuse_color"):
            curves = _cast(
                _Collect[_FCurve],
                material.driver_add("diffuse_color"),
            )
            for index, curve in enumerate(curves):
                _cfg_drv(
                    curve.driver,
                    id_type=_IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Base Color"].default_value[{index}]',
                )
                curve.lock = True
            curves_len = len(curves)
            processed += curves_len
            self.report(
                {_WMReport.INFO},
                f"Configured {curves_len} material color driver(s)",
            )
        if _contains(inputs, "Metallic") and not _has_drv(material, "metallic"):
            curve = material.driver_add("metallic")
            _cfg_drv(
                curve.driver,
                id_type=_IDType.NODETREE,
                id=node_tree,
                data_path=f'nodes["{node.name}"].inputs["Metallic"].default_value',
            )
            curve.lock = True
            processed += 1
            self.report({_WMReport.INFO}, "Configured material metallic driver")
        if _contains(inputs, "Roughness") and not _has_drv(material, "roughness"):
            curve = material.driver_add("roughness")
            _cfg_drv(
                curve.driver,
                id_type=_IDType.NODETREE,
                id=node_tree,
                data_path=f'nodes["{node.name}"].inputs["Roughness"].default_value',
            )
            curve.lock = True
            processed += 1
            self.report({_WMReport.INFO}, "Configured material roughness driver")
        if _contains(inputs, "Alpha"):
            if material.blend_method == _Mat.BlendMethod.OPAQUE and not _has_drv(
                material, "blend_method"
            ):
                curve = material.driver_add("blend_method")
                _cfg_drv(
                    curve.driver,
                    id_type=_IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                    expr="0 if var == 1 else 5",
                )
                curve.lock = True
                processed += 1
                self.report({_WMReport.INFO}, "Configured material blend mode driver")
            if material.shadow_method == _Mat.ShadowMethod.OPAQUE and not _has_drv(
                material, "shadow_method"
            ):
                curve = material.driver_add("shadow_method")
                _cfg_drv(
                    curve.driver,
                    id_type=_IDType.NODETREE,
                    id=node_tree,
                    data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                    expr="1 if var == 1 else 3",
                )
                curve.lock = True
                processed += 1
                self.report(
                    {_WMReport.INFO},
                    "Configured material shadow mode driver",
                )
        self.report({_WMReport.INFO}, f"Configured {processed} material driver(s)")
        return {_OpReturn.FINISHED} if processed > 0 else {_OpReturn.CANCELLED}


@_draw_func_class
@_int_op(uuid="d409c199-6017-4a76-a2e1-58628b8a76dd")
class DrawFunc(_Op):
    __slots__: _ClassVar = ()

    @classmethod
    def NODE_MT_node_draw_func(
        cls,
        self: _Drawer,
        context: _Ctx,
    ):
        self.layout.separator()
        self.layout.operator(MakeLinksByName.bl_idname)
        if ConfigurePrincipledMaterialDriver.poll(context):
            self.layout.operator(ConfigurePrincipledMaterialDriver.bl_idname)


register, unregister = _reg_cls_fac(
    (
        MakeLinksByName,
        ConfigurePrincipledMaterialDriver,
        DrawFunc,
    )
)
