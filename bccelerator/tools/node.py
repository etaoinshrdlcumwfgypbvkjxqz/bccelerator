# -*- coding: bccelerator-transform-UTF-8 -*-

# node editor

import bpy as _bpy
import typing as _typing

from .. import util as _util
from ..util import enums as _util_enums
from ..util import polyfill as _util_polyfill
from ..util import types as _util_types
from ..util import utils as _util_utils


class MakeLinksByName(_bpy.types.Operator):
    '''Make links to selected nodes from the active node by socket name'''
    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'node.make_links_by_name'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Make Links by Name'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({_util_enums.OperatorTypeFlag.REGISTER,
                  _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
        cls: type[_util_polyfill.Self], context: _bpy.types.Context
    ) -> bool:
        return (context.space_data is not None
                and context.space_data.type == _util_enums.SpaceType.NODE_EDITOR
                and context.active_node is not None
                and len(context.selected_nodes) >= 2)

    def execute(  # type: ignore
        self: _util_polyfill.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        node_tree: _bpy.types.NodeTree = _typing.cast(
            _bpy.types.SpaceNodeEditor, context.space_data).edit_tree
        from_node: _bpy.types.Node = context.active_node
        from_sockets: _util.Intersection[_bpy.types.NodeOutputs,
                                         _bpy.types.bpy_prop_collection[_bpy.types.NodeSocket]] = _util.intersection2(from_node.outputs)
        for (from_socket, to_socket) in ((from_sockets[1][to_socket.name], to_socket)
                                         for node in context.selected_nodes if node != from_node
                                         for to_socket in node.inputs if to_socket.name in from_sockets[0]):
            _util.intersection2(node_tree.links)[0].new(from_socket, to_socket)
            processed += 1
        self.report({_util_enums.WMReport.INFO},
                    f'Made {processed} link(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}


class ConfigurePrincipledMaterialDriver(_bpy.types.Operator):
    '''Configure drivers of material properties from active principled node'''
    __slots__: _typing.ClassVar = ()
    bl_idname: _typing.ClassVar[str] = (  # type: ignore
        'node.configure_principled_material_driver'
    )
    bl_label: _typing.ClassVar[str] = (  # type: ignore
        'Configure Principled Material Driver(s)'
    )
    bl_options: _typing.ClassVar[_typing.AbstractSet[_util_enums.OperatorTypeFlag]] = (  # type: ignore
        frozenset({_util_enums.OperatorTypeFlag.REGISTER,
                  _util_enums.OperatorTypeFlag.UNDO, })
    )

    @classmethod
    def poll(  # type: ignore
        cls: type[_util_polyfill.Self], context: _bpy.types.Context
    ) -> bool:
        return (context.space_data is not None
                and context.space_data.type == _util_enums.SpaceType.NODE_EDITOR
                and context.material is not None
                and context.active_node is not None)

    def execute(  # type: ignore
        self: _util_polyfill.Self, context: _bpy.types.Context
    ) -> _typing.AbstractSet[_util_enums.OperatorReturn]:
        processed: int = 0
        material: _bpy.types.Material = context.material
        node: _bpy.types.Node = context.active_node
        node_tree: _bpy.types.NodeTree = _typing.cast(
            _bpy.types.NodeTree, node.id_data)
        inputs: _util.Intersection[_bpy.types.NodeInputs, _bpy.types.bpy_prop_collection[_bpy.types.NodeSocket]] = _util.intersection2(
            node.inputs)
        if 'Base Color' in inputs[0] and not _util_utils.has_driver(material, 'diffuse_color'):
            curves: _typing.Sequence[_bpy.types.FCurve] = _typing.cast(
                _typing.Sequence[_bpy.types.FCurve], material.driver_add('diffuse_color'))
            index: int
            curve: _bpy.types.FCurve
            for index, curve in enumerate(curves):
                _util_utils.configure_driver(curve.driver,
                                             id_type=_util_enums.IDType.NODETREE, id=node_tree,
                                             data_path=f'nodes["{node.name}"].inputs["Base Color"].default_value[{index}]',)
                curve.lock = True
            curves_len: int = len(curves)
            processed += curves_len
            self.report({_util_enums.WMReport.INFO},
                        f'Configured {curves_len} material color driver(s)')
        if 'Metallic' in inputs[0] and not _util_utils.has_driver(material, 'metallic'):
            curve = material.driver_add('metallic')
            _util_utils.configure_driver(curve.driver,
                                         id_type=_util_enums.IDType.NODETREE, id=node_tree,
                                         data_path=f'nodes["{node.name}"].inputs["Metallic"].default_value',
                                         )
            curve.lock = True
            processed += 1
            self.report({_util_enums.WMReport.INFO},
                        'Configured material metallic driver')
        if 'Roughness' in inputs[0] and not _util_utils.has_driver(material, 'roughness'):
            curve = material.driver_add('roughness')
            _util_utils.configure_driver(curve.driver,
                                         id_type=_util_enums.IDType.NODETREE, id=node_tree,
                                         data_path=f'nodes["{node.name}"].inputs["Roughness"].default_value',
                                         )
            curve.lock = True
            processed += 1
            self.report({_util_enums.WMReport.INFO},
                        'Configured material roughness driver')
        if 'Alpha' in inputs[0]:
            if (material.blend_method == _util_enums.Material.BlendMethod.OPAQUE
                    and not _util_utils.has_driver(material, 'blend_method')):
                curve = material.driver_add('blend_method')
                _util_utils.configure_driver(curve.driver,
                                             id_type=_util_enums.IDType.NODETREE, id=node_tree,
                                             data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                                             expr='0 if var == 1 else 5',
                                             )
                curve.lock = True
                processed += 1
                self.report({_util_enums.WMReport.INFO},
                            'Configured material blend mode driver')
            if (material.shadow_method == _util_enums.Material.ShadowMethod.OPAQUE
                    and not _util_utils.has_driver(material, 'shadow_method')):
                curve = material.driver_add('shadow_method')
                _util_utils.configure_driver(curve.driver,
                                             id_type=_util_enums.IDType.NODETREE, id=node_tree,
                                             data_path=f'nodes["{node.name}"].inputs["Alpha"].default_value',
                                             expr='1 if var == 1 else 3',
                                             )
                curve.lock = True
                processed += 1
                self.report({_util_enums.WMReport.INFO},
                            'Configured material shadow mode driver')
        self.report({_util_enums.WMReport.INFO},
                    f'Configured {processed} material driver(s)')
        return {_util_enums.OperatorReturn.FINISHED} if processed > 0 else {_util_enums.OperatorReturn.CANCELLED}


@_util_types.draw_func_class
@_util_types.internal_operator(uuid='d409c199-6017-4a76-a2e1-58628b8a76dd')
class DrawFunc(_bpy.types.Operator):
    __slots__: _typing.ClassVar = ()

    @classmethod
    def NODE_MT_node_draw_func(cls: type[_util_polyfill.Self], self: _typing.Any, context: _bpy.types.Context) -> None:
        layout: _bpy.types.UILayout = self.layout
        layout.separator()
        layout.operator(MakeLinksByName.bl_idname)
        if ConfigurePrincipledMaterialDriver.poll(context):
            layout.operator(ConfigurePrincipledMaterialDriver.bl_idname)


register: _typing.Callable[[], None]
unregister: _typing.Callable[[], None]
register, unregister = _util_utils.register_classes_factory((
    MakeLinksByName,
    ConfigurePrincipledMaterialDriver,
    DrawFunc,
))
