# object

import math as _math, types as _types,\
	bmesh as _bmesh, bpy as _bpy, texts.common as _common

def _select_face_doubles(mesh):
	# https://pasteall.org/55201/python
	func = _select_face_doubles

	bm = _bmesh.from_edit_mesh(mesh)
	faces = [(face.calc_center_median(), face) for face in bm.faces]

	#yay, key instead of cmp...
	#no tolerance, precision problems -> round
	faces.sort(key=lambda t: round(t[0].x, func.rounding))
	faces.sort(key=lambda t: round(t[0].y, func.rounding))
	faces.sort(key=lambda t: round(t[0].z, func.rounding))
 
	#find double faces
	for index in range(1, len(faces)):
		prev = faces[index - 1]
		current = faces[index]
		if all(abs(prev[0][j] - current[0][j]) < func.tolerance for j in range(3)):
			current[1].select = True
			prev[1].select = True
 
	_bmesh.update_edit_mesh(mesh, loop_triangles=False, destructive=False)
_select_face_doubles.tolerance = 0.0001
_select_face_doubles.rounding =\
	round(-_math.log(_select_face_doubles.tolerance, 10) + 1)

class ConfigureEEVEEVolumetrics(_bpy.types.Operator):
	'''Configure EEVEE volumetrics for selected object(s)'''
	bl_idname = 'object.configure_eevee_volumetrics'
	bl_label = 'Configure EEVEE Volumetrics'
	bl_options = frozenset({'REGISTER', 'UNDO'})
	bl_property = 'mode'

	mode_items = _types.MappingProxyType({
		'DISABLE': ('DISABLE', 'Disable', 'Disable EEVEE volumetrics', 0),
		'ENABLE': ('ENABLE', 'Enable', 'Enable EEVEE volumetrics', 1),
		'EEVEE': ('EEVEE', 'EEVEE-Only', 'Enable volumetrics for EEVEE only', 2),
	})
	mode: _bpy.props.EnumProperty(
		name='EEVEE Volumetrics Mode',
		items=mode_items.values(),
		description='Volumetrics mode for EEVEE for selected object(s)',
		default=0,
		options={'SKIP_SAVE'}
	)
	mode_min = min(value[-1] for value in mode_items.values())
	mode_max = max(value[-1] for value in mode_items.values())
	mode_name = 'EEVEE volumetrics'

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		processed = 0
		for object in context.selected_objects:
			if self.mode_name in object:
				if object[self.mode_name] == self.mode_items[self.mode][-1]:
					continue
			else:
				object[self.mode_name] = int()
				object.id_properties_ui(self.mode_name).update(
					subtype='NONE',
					min=self.mode_min,
					max=self.mode_max,
					soft_min=self.mode_min,
					soft_max=self.mode_max,
					step=1,
					default=0,
					description='Volumetrics mode for EEVEE'
				)
			object[self.mode_name] = self.mode_items[self.mode][-1]
			processed += 1
			self.report({'INFO'},
				'Configured object "%s"' % object.name_full)
		self.report({'INFO'},
			'Configured %d object(s)' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

class MergeWallCollection(_bpy.types.Operator):
	'''Merge a collection of wall(s) into an object'''
	bl_idname = 'object.merge_wall_collection'
	bl_label = 'Merge Wall Collection'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT' and context.collection is not None

	def execute(self, context):
		data = context.blend_data
		scene = context.scene
		collection = context.collection

		instance = data.objects.new('', object_data=None)
		instance.instance_type = 'COLLECTION'
		instance.instance_collection = collection
		scene.collection.objects.link(instance)
		_bpy.ops.object.select_all(action='DESELECT')
		instance.select_set(True)
		_bpy.ops.object.duplicates_make_real()
		data.objects.remove(instance)

		_bpy.ops.object.make_local(type='SELECT_OBDATA')
		_bpy.ops.object.make_single_user(type='SELECTED_OBJECTS',
			object=True, obdata=True)

		mesh = data.meshes.new(collection.name)
		mesh_obj = data.objects.new(collection.name, object_data=mesh)
		scene.collection.objects.link(mesh_obj)
		mesh_obj.select_set(True)
		context.view_layer.objects.active = mesh_obj
		_bpy.ops.object.convert(target='MESH')
		_bpy.ops.object.join()

		_bpy.ops.object.editmode_toggle()
		_bpy.ops.mesh.select_all(action='DESELECT')
		_select_face_doubles(mesh)
		_bpy.ops.mesh.delete(type='FACE')
		_bpy.ops.mesh.select_all(action='SELECT')
		_bpy.ops.mesh.remove_doubles()
		_bpy.ops.object.editmode_toggle()

		return {'FINISHED'}

class FixRigifyRigAnimationData(_bpy.types.Operator):
	'''Fix animation data of selected rig(s) created by Rigify'''
	bl_idname = 'rigify.fix_animation_data'
	bl_label = 'Fix Rigify Rig Animation Data'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	@classmethod
	def poll(cls, context):
		return context.mode == 'OBJECT'\
			and context.selected_objects\
			and any('rig_ui' in obj for obj in context.selected_objects)

	def execute(self, context):
		processed = 0
		for object in (obj for obj in context.selected_objects if 'rig_ui' in obj):
			_common.utils.ensure_animation_data(object)
			targets = 0
			for target in (target
				for driver in object.data.animation_data.drivers
				for variable in
					object.animation_data.drivers.from_existing(src_driver=driver)
					.driver.variables
				for target in variable.targets if target.id_type == 'OBJECT'
			):
				target.id = object
				targets += 1
			processed += 1
			self.report({'INFO'},
				'Fixed %d driver target(s) in object "%s"'
				% (targets, object.name_full))
		self.report({'INFO'}, 'Fixed %d object(s)' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

@_common.types.draw_func_class
@_common.types.internal_operator(uuid='9c6c6894-c400-4edc-a21a-2bcb230c8f2a')
class DrawFunc(_bpy.types.Operator):
	@classmethod
	def VIEW3D_MT_object_draw_func(cls, self, conltext):
		self.layout.separator()
		self.layout.operator(ConfigureEEVEEVolumetrics.bl_idname)

	@classmethod
	def VIEW3D_MT_object_collection_draw_func(cls, self, context):
		self.layout.separator()
		self.layout.operator(MergeWallCollection.bl_idname)

	@classmethod
	def VIEW3D_MT_object_animation_draw_func(cls, self, context):
		if FixRigifyRigAnimationData.poll(context):
			self.layout.separator()
			self.layout.operator(FixRigifyRigAnimationData.bl_idname)

register, unregister = _common.utils.register_classes_factory((
	ConfigureEEVEEVolumetrics,
	MergeWallCollection,
	FixRigifyRigAnimationData,
	DrawFunc,
))

if __name__ == '__main__':
	_common.utils.main(register=register, unregister=unregister)
