# using libraries

import collections as _collections, itertools as _itertools, types as _types,\
	bpy as _bpy, texts.common as _common

class LinkModifierByName(_bpy.types.Operator):
	'''Link modifiers from active modifier to modifiers of selected object(s) by name'''
	bl_idname = 'object.link_modifier_by_name'
	bl_label = 'Link Modifier By Name'
	bl_options = frozenset({'REGISTER', 'UNDO'})
	exclude_attrs = frozenset({
		'__doc__', '__module__', '__slots__',
		'bl_rna', 'rna_type',
		'is_active', 'is_override_data',
		'name', 'show_expanded', 'type',
	})

	@classmethod
	def poll(cls, context):
		active_object = context.active_object
		return len(context.selected_objects) >= 2\
			and active_object is not None\
			and active_object.modifiers.active is not None

	def execute(self, context):
		modifiers = 0
		drivers = 0
		
		from_object = context.active_object
		from_modifier = from_object.modifiers.active
		modifier_name = from_modifier.name
		modifier_type = from_modifier.type
		modifier_attrs = tuple(filter(lambda attr: attr not in self.exclude_attrs,
			dir(from_modifier)))
		for to_object in filter(
			lambda obj: obj != from_object and modifier_name in obj.modifiers,
			context.selected_objects
		):
			to_modifier = to_object.modifiers[modifier_name]
			if to_modifier.type == modifier_type:
				to_drivers = 0
				for modifier_attr in modifier_attrs:
					data_path = 'modifiers["%s"].%s' % (modifier_name, modifier_attr)
					if _common.utils.has_driver(to_object, data_path):
						continue
					try:
					   curves = to_object.driver_add(data_path)
					except TypeError:
						continue
					multiple = isinstance(curves, _collections.abc.Iterable)
					curves = curves if multiple else (curves,)
					for (index, curve) in enumerate(curves):
						_common.utils.configure_driver(curve.driver,
							id_type='OBJECT', id=from_object,
							data_path=''.join((data_path, '[', str(index), ']'))
								if multiple else data_path 
						)
						curve.lock = True
					to_drivers += len(curves)
				modifiers += 1
				drivers += to_drivers
				self.report({'INFO'},
					'Linked modifier of "%s" using %d driver(s)'
					% (to_object.name_full, to_drivers))
		self.report({'INFO'},
			'Linked %d modifier(s) using %d driver(s)' % (modifiers, drivers))
		return {'FINISHED'} if drivers > 0 else {'CANCELLED'}

class ChangeLibraryOverrideEditable(_bpy.types.Operator):
	'''Change editability of selected library override(s)'''
	bl_idname = 'outliner.liboverride_editable_operation'
	bl_label = 'Change Library Override(s) Editability'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	editable: _bpy.props.BoolProperty(
		name='Editable',
		description='Editability',
		default=False,
		options={'SKIP_SAVE'},
	)
	selection_set_items = _types.MappingProxyType({
		'SELECTED': ('SELECTED', 'Selected',
			'Apply the operation over selected data-block(s) only', 0),
		'CONTENT': ('CONTENT', 'Content',
			'Apply the operation over content of the selected item(s) only (the data-block(s) in their sub-tree(s))', 1),
		'SELECTED_AND_CONTENT': ('SELECTED_AND_CONTENT', 'Selected & Content',
			'Apply the operation over selected data-block(s) and all their dependency(s)', 2),
	})
	selection_set: _bpy.props.EnumProperty(
		name='Selection Set',
		items=selection_set_items.values(),
		description='Over which part of the tree item(s) to apply the operation',
		default=0,
		options={'SKIP_SAVE'}
	)

	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'OUTLINER'\
			and any(id.override_library is not None for id in context.selected_ids)

	def execute(self, context):
		processed = 0

		if self.selection_set == 'SELECTED':
			data = context.selected_ids
		elif self.selection_set == 'CONTENT':
			data = _common.utils.flatmap(
				lambda id: id.objects
					if isinstance(id, _bpy.types.Collection)
					else (id,),
				context.selected_ids
			)
		elif self.selection_set == 'SELECTED_AND_CONTENT':
			data = _common.utils.flatmap(
				lambda id: _itertools.chain((id,), id.objects)
					if isinstance(id, _bpy.types.Collection)
					else (id,),
				context.selected_ids
			)
		else:
			self.report({'ERROR_INVALID_INPUT'},
				f'Invalid selection set "{self.selection_set}"')
			return {'CANCELLED'}

		for datum in (datum for datum in data if datum.override_library is not None):
			datum.override_library.is_system_override = not self.editable
			processed += 1
			self.report({'INFO'},
				f'Changed editability of library override "{datum.name_full}"')

		self.report({'INFO'},
			f'Changed editability of {processed} data-block(s)')
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

class _LibraryOverrideEditableMenu(_bpy.types.Menu):
	def __init_subclass__(cls, editable, **kwargs):
		super().__init_subclass__(**kwargs)
		cls.__editable = editable
		cls.bl_idname = 'OUTLINER_MT_liboverride_editable_%s'\
			% ('editable' if editable else 'noneditable')
		cls.bl_label = 'Editable' if editable else 'Non-Editable'

	def draw(self, context):
		for selection_set in ChangeLibraryOverrideEditable.selection_set_items.values():
				op = self.layout.operator(ChangeLibraryOverrideEditable.bl_idname,
					text=selection_set[1])
				op.editable = self.__editable
				op.selection_set = selection_set[0]

@_common.types.draw_func_class
@_common.types.internal_operator(uuid='06211866-d898-46d8-b253-14e4cd41dd77')
class DrawFunc(_bpy.types.Operator):
	editable_menu, noneditable_menu = (
		type('', (_LibraryOverrideEditableMenu,), dict(), editable=editable)
		for editable in (True, False)
	)

	register, unregister = _common.utils.register_classes_factory((
		editable_menu,
		noneditable_menu
	), class_method=True)

	@classmethod
	def VIEW3D_MT_make_links_draw_func(cls, self, context):
		self.layout.separator()
		self.layout.operator(LinkModifierByName.bl_idname)

	@classmethod
	def OUTLINER_MT_liboverride_draw_func(cls, self, context):
		self.layout.separator()
		self.layout.menu(cls.editable_menu.bl_idname)
		self.layout.menu(cls.noneditable_menu.bl_idname)

register, unregister = _common.utils.register_classes_factory((
	LinkModifierByName,
	ChangeLibraryOverrideEditable,
	DrawFunc,
))

if __name__ == '__main__':
	_common.utils.main(register=register, unregister=unregister)
