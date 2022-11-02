# node editor

import bpy as _bpy
import texts.common as _common


class MakeLinksByName(_bpy.types.Operator):
    '''Make links to selected nodes from the active node by socket name'''
    bl_idname = 'node.make_links_by_name'
    bl_label = 'Make Links by Name'
    bl_options = frozenset({'REGISTER', 'UNDO'})

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR'\
            and context.active_node is not None\
            and len(context.selected_nodes) >= 2

    def execute(self, context):
        processed = 0
        node_tree = context.space_data.edit_tree
        from_node = context.active_node
        from_sockets = from_node.outputs
        for (from_socket, to_socket) in ((from_sockets[to_socket.name], to_socket)
                                         for node in context.selected_nodes if node != from_node
                                         for to_socket in node.inputs if to_socket.name in from_sockets):
            node_tree.links.new(from_socket, to_socket)
            processed += 1
        self.report({'INFO'}, 'Made %d link(s)' % processed)
        return {'FINISHED'} if processed > 0 else {'CANCELLED'}


class ConfigurePrincipledMaterialDriver(_bpy.types.Operator):
    '''Configure drivers of material properties from active principled node'''
    bl_idname = 'node.configure_principled_material_driver'
    bl_label = 'Configure Principled Material Driver(s)'
    bl_options = frozenset({'REGISTER', 'UNDO'})

    @classmethod
    def poll(cls, context):
        return context.space_data.type == 'NODE_EDITOR'\
            and context.material is not None\
            and context.active_node is not None

    def execute(self, context):
        processed = 0
        material = context.material
        node = context.active_node
        node_tree = node.id_data
        if 'Base Color' in node.inputs\
                and not _common.utils.has_driver(material, 'diffuse_color'):
            curves = material.driver_add('diffuse_color')
            for (index, curve) in enumerate(curves):
                _common.utils.configure_driver(curve.driver,
                                               id_type='NODETREE', id=node_tree,
                                               data_path='nodes["%s"].inputs["Base Color"].default_value[%d]'
                                               % (node.name, index),
                                               )
                curve.lock = True
            curves_len = len(curves)
            processed += curves_len
            self.report({'INFO'},
                        'Configured %d material color driver(s)' % curves_len)
        if 'Metallic' in node.inputs\
                and not _common.utils.has_driver(material, 'metallic'):
            curve = material.driver_add('metallic')
            _common.utils.configure_driver(curve.driver,
                                           id_type='NODETREE', id=node_tree,
                                           data_path='nodes["%s"].inputs["Metallic"].default_value'
                                           % node.name,
                                           )
            curve.lock = True
            processed += 1
            self.report({'INFO'},
                        'Configured material metallic driver')
        if 'Roughness' in node.inputs\
                and not _common.utils.has_driver(material, 'roughness'):
            curve = material.driver_add('roughness')
            _common.utils.configure_driver(curve.driver,
                                           id_type='NODETREE', id=node_tree,
                                           data_path='nodes["%s"].inputs["Roughness"].default_value'
                                           % node.name,
                                           )
            curve.lock = True
            processed += 1
            self.report({'INFO'},
                        'Configured material roughness driver')
        if 'Alpha' in node.inputs:
            if material.blend_method == 'OPAQUE'\
                    and not _common.utils.has_driver(material, 'blend_method'):
                curve = material.driver_add('blend_method')
                _common.utils.configure_driver(curve.driver,
                                               id_type='NODETREE', id=node_tree,
                                               data_path='nodes["%s"].inputs["Alpha"].default_value'
                                               % node.name,
                                               expr='0 if var == 1 else 5',
                                               )
                curve.lock = True
                processed += 1
                self.report({'INFO'},
                            'Configured material blend mode driver')
            if material.shadow_method == 'OPAQUE'\
                    and not _common.utils.has_driver(material, 'shadow_method'):
                curve = material.driver_add('shadow_method')
                _common.utils.configure_driver(curve.driver,
                                               id_type='NODETREE', id=node_tree,
                                               data_path='nodes["%s"].inputs["Alpha"].default_value'
                                               % node.name,
                                               expr='1 if var == 1 else 3',
                                               )
                curve.lock = True
                processed += 1
                self.report({'INFO'},
                            'Configured material shadow mode driver')
        self.report({'INFO'},
                    'Configured %d material driver(s)' % processed)
        return {'FINISHED'} if processed > 0 else {'CANCELLED'}


@_common.types.draw_func_class
@_common.types.internal_operator(uuid='d409c199-6017-4a76-a2e1-58628b8a76dd')
class DrawFunc(_bpy.types.Operator):
    @classmethod
    def NODE_MT_node_draw_func(cls, self, context):
        self.layout.separator()
        self.layout.operator(MakeLinksByName.bl_idname)
        if ConfigurePrincipledMaterialDriver.poll(context):
            self.layout.operator(ConfigurePrincipledMaterialDriver.bl_idname)


register, unregister = _common.utils.register_classes_factory((
    MakeLinksByName,
    ConfigurePrincipledMaterialDriver,
    DrawFunc,
))

if __name__ == '__main__':
    _common.utils.main(register=register, unregister=unregister)
