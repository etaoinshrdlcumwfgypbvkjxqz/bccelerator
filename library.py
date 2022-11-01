# library management

import types as _types, bpy as _bpy, texts.common as _common

class RemapUserToLibraryByName(_bpy.types.Operator):
	'''Remap selected local data-block(s) to library data-block(s) by name'''
	bl_idname = 'object.remap_user_to_library_by_name'
	bl_rna_id = 'OBJECT_OT_remap_user_to_library_by_name'
	bl_label = 'Remap User(s) to Library Data-Block(s) by Name'
	bl_options = frozenset({'REGISTER', 'UNDO'})
	
	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'OUTLINER'\
			and any(id.library is None for id in context.selected_ids)

	def execute(self, context):
		processed = 0
		local_users = _types.MappingProxyType({(type(id), id.name): id
			for id in context.selected_ids
			if id.library is None})
		for (lib_user, local_user) in (
			(user, local_users[type(user), user.name])
			for lib in context.blend_data.libraries
			for user in lib.users_id
			if (type(user), user.name) in local_users
		):
			local_user.user_remap(lib_user)
			processed += 1
			self.report({'INFO'},
				'Remapped "%s" to "%s"'
				% (local_user.name_full, lib_user.name_full))
		self.report({'INFO'}, 'Remapped %d data-block(s)' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

class RemapUserToLocalByName(_bpy.types.Operator):
	'''Remap selected library data-block(s) to local data-block(s) by name'''
	bl_idname = 'object.remap_user_to_local_by_name'
	bl_rna_id = 'OBJECT_OT_remap_user_to_local_by_name'
	bl_label = 'Remap User(s) to Local Data-Block(s) by Name'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'OUTLINER'\
			and any(id.library is not None for id in context.selected_ids)

	def execute(self, context):
		processed = 0
		for (lib_user, local_user) in (
			(id, _common.data.all[type(id)][id.name, None])
			for id in context.selected_ids
			if id.library is not None
				and (id.name, None) in _common.data.all[type(id)]
		):
			lib_user.user_remap(local_user)
			processed += 1
			self.report({'INFO'},
				'Remapped "%s" to "%s"'
				% (lib_user.name_full, local_user.name_full))
		self.report({'INFO'},
			'Remapped %d data-block(s)' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

class LocalizeLibrary(_bpy.types.Operator):
	'''Make all data-blocks of selected library(s) local'''
	bl_idname = 'outliner.localize_library'
	bl_rna_id = 'OUTLINER_OT_localize_library'
	bl_label = 'Localize Library'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	@classmethod
	def poll(cls, context):
		return context.space_data.type == 'OUTLINER'\
			and any(isinstance(id, _bpy.types.Library) for id in context.selected_ids)

	def execute(self, context):
		users = tuple(user
			for lib in context.selected_ids if isinstance(lib, _bpy.types.Library)
			for user in lib.users_id)
		to_be_processed = len(users)
		while users:
			retry_users = []
			for user in (user.make_local() for user in users):
				if user.library is None:
					self.report({'INFO'},
						'Made "%s" local' % user.name_full)
				else:
					retry_users.append(user)
			if len(retry_users) == len(users):
				for user in users:
					self.report({'WARNING'},
						'Cannot make "%s" local' % user.name_full)
				self.report({'WARNING'},
					'Cannot make "%d" data-block(s) local' % len(users))
				break
			users = retry_users
		processed = to_be_processed - len(users)
		self.report({'INFO'},
			'Made %d data-block(s) local' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

class CleanUpLibraryWeakReference(_bpy.types.Operator):
	'''Clean up unused weak reference(s) to external library(s)'''
	bl_idname = 'wm.clean_up_library_weak_reference'
	bl_rna_id = 'WM_OT_clean_up_library_weak_reference'
	bl_label = 'Clean Up Library Weak References'
	bl_options = frozenset({'REGISTER', 'UNDO'})

	def execute(self, context):
		data = tuple(datum
			for data in _common.data.all.values()
			for datum in data
				if datum.library_weak_reference is not None
					and datum.library is None)
		for datum in data:
			new_datum = datum.copy()
			asset_data = datum.asset_data
			if asset_data is not None:
				new_datum.asset_mark()
				new_asset_data = new_datum.asset_data
				for attr in (
					'active_tag',
					'author',
					'catalog_id',
					'description',
				):
					setattr(new_asset_data, attr, getattr(asset_data, attr))
				for tag in asset_data.tags:
					new_asset_data.tags.new(tag.name)
			datum.user_remap(new_datum)
			datum.asset_clear()
			new_datum.name = datum.name
			self.report({'INFO'},
				'Removed library weak reference of "%s": "%s"'
				% (datum.name, datum.library_weak_reference.filepath))
		processed = len(data)
		self.report({'INFO'},
			'Removed %d library weak reference(s)' % processed)
		return {'FINISHED'} if processed > 0 else {'CANCELLED'}

@_common.types.draw_func_class
@_common.types.internal_operator(uuid='2947869a-43a8-4f91-bb19-20ffca18edce')
class DrawFunc(_bpy.types.Operator):
	@classmethod
	def OUTLINER_MT_context_menu_draw_func(cls, self, context):
		lambdas = []
		if RemapUserToLibraryByName.poll(context):
			lambdas.append(lambda:
				self.layout.operator(RemapUserToLibraryByName.bl_idname))
		if RemapUserToLocalByName.poll(context):
			lambdas.append(lambda:
				self.layout.operator(RemapUserToLocalByName.bl_idname))
		if LocalizeLibrary.poll(context):
			lambdas.append(lambda:
				self.layout.operator(LocalizeLibrary.bl_idname))
		if lambdas:
			self.layout.separator()
			for lamb in lambdas:
				lamb()

	@classmethod
	def OUTLINER_MT_collection_draw_func(cls, self, context):
		cls.OUTLINER_MT_context_menu_draw_func(self, context)

	@classmethod
	def OUTLINER_MT_object_draw_func(cls, self, context):
		cls.OUTLINER_MT_context_menu_draw_func(self, context)

	@classmethod
	def TOPBAR_MT_file_cleanup_draw_func(cls, self, context):
		self.layout.separator()
		self.layout.operator(CleanUpLibraryWeakReference.bl_idname,
			text='Library Weak References')

register, unregister = _common.utils.register_classes_factory((
    RemapUserToLibraryByName,
    RemapUserToLocalByName,
    LocalizeLibrary,
    CleanUpLibraryWeakReference,
    DrawFunc,
))

if __name__ == '__main__':
    _common.utils.main(register=register, unregister=unregister)
