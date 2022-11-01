# utilities

import functools as _functools, itertools as _itertools, re as _re, types as _types,\
	bpy as _bpy

data = _types.SimpleNamespace()
types = _types.SimpleNamespace()
utils = _types.SimpleNamespace()

def _type_from_blend_data(data):
	func = _type_from_blend_data
	try:
		return func.exceptions[data]
	except KeyError:
		pass
	type_name_p = data.rna_type.identifier[len('BlendData'):]
	p_type_names = (
		_re.sub('s$', '', type_name_p),
		_re.sub('es$', '', type_name_p),
		_re.sub('ies$', 'y', type_name_p),
		type_name_p
	)
	for result in (getattr(_bpy.types, name) for name in p_type_names
		if hasattr(_bpy.types, name)):
		return result
	raise LookupError(data)
_type_from_blend_data.exceptions = _types.MappingProxyType({
	_bpy.data.fonts: _bpy.types.VectorFont,
	_bpy.data.lightprobes: _bpy.types.LightProbe,
	_bpy.data.linestyles: _bpy.types.FreestyleLineStyle,
	_bpy.data.hair_curves: _bpy.types.Curves,
	_bpy.data.shape_keys: _bpy.types.Key,
})
class _BlendDataAll(dict):
	def __missing__(self, key):
		for (exist_key, value) in self.items():
			if issubclass(key, exist_key):
				self[key] = value
				return value
		raise KeyError(key)
data.all = _types.MappingProxyType(_BlendDataAll(
	{_type_from_blend_data(attr): attr for attr
	   in (getattr(_bpy.data, attr_name) for attr_name in dir(_bpy.data))
	   if isinstance(attr, _bpy.types.bpy_prop_collection)}
))

def _draw_func_class(cls):
	func = _draw_func_class
	register_0 = getattr(cls, 'register', func.noop).__func__
	unregister_0 = getattr(cls, 'unregister', func.noop).__func__
	@classmethod
	@_functools.wraps(register_0)
	def register(cls):
		register_0(cls)
		for func_name in (name for name in dir(cls) if '_draw_func' in name):
			menu_name = func_name[:-len('_draw_func')]
			getattr(_bpy.types, menu_name).append(getattr(cls, func_name))
	@classmethod
	@_functools.wraps(unregister_0)
	def unregister(cls):
		for func_name in (name for name in dir(cls) if '_draw_func' in name):
			menu_name = func_name[:-len('_draw_func')]
			getattr(_bpy.types, menu_name).remove(getattr(cls, func_name))
		unregister_0(cls)
	cls.register = register
	cls.unregister = unregister
	return cls
_draw_func_class.noop = classmethod(lambda cls: None)
types.draw_func_class = _draw_func_class

def _internal_operator(*, uuid):
	def _(cls):
		cls.bl_idname = 'internal.%s' % uuid.replace('-', '_')
		cls.bl_label = ''
		cls.bl_options = frozenset({'INTERNAL'})
		cls.poll = classmethod(lambda cls, context: False)
		return cls
	return _
types.internal_operator = _internal_operator

def _flatmap(func, *iterable):
	return _itertools.chain.from_iterable(map(func, *iterable))
utils.flatmap = _flatmap

def _clear(collection):
	if callable(getattr(collection, 'clear', None)):
		return collection.clear()
	if isinstance(collection, _bpy.types.bpy_prop_collection)\
		and callable(getattr(collection, 'remove', None)):
		for item in collection.values():
			collection.remove(item)
		return
	raise TypeError(collection)
utils.clear = _clear

def _configure_driver(
	driver, *, id_type, id, data_path,
	var_name='var', expr=None
):
	driver.expression = var_name if expr is None else expr
	driver.type = 'AVERAGE' if expr is None else 'SCRIPTED'
	driver.use_self = False if expr is None else 'self' in expr

	variables = driver.variables
	utils.clear(variables)

	variable = variables.new()
	variable.name = var_name
	variable.type = 'SINGLE_PROP'

	target = variable.targets[0]
	target.id_type = id_type
	target.id = id
	target.data_path = data_path
utils.configure_driver = _configure_driver

def _has_driver(id, data_path):
	anim_data = id.animation_data
	if anim_data is None:
		return False
	return any(driver.data_path == data_path for driver in anim_data.drivers)
utils.has_driver = _has_driver

utils.register_class = _bpy.utils.register_class
def _unregister_class(cls):
	# wtf: https://blender.stackexchange.com/a/124838
	if issubclass(cls, _bpy.types.Operator):
		bl_idname_parts = cls.bl_idname.split('.')
		bl_idname_parts[0] = bl_idname_parts[0].upper()
		rna_id = '_OT_'.join(bl_idname_parts)
	else:
		rna_id = cls.bl_idname
	_bpy.utils.unregister_class(_bpy.types.bpy_struct.bl_rna_get_subclass_py(rna_id))
utils.unregister_class = _unregister_class
def _register_classes(classes):
	for cls in classes:
		utils.register_class(cls)
utils.register_classes = _register_classes
def _unregister_classes(classes):
	for cls in classes:
		utils.unregister_class(cls)
utils.unregister_classes = _unregister_classes
def _register_classes_factory(classes, *, class_method=False):
	ret = (lambda: utils.register_classes(classes),
		lambda: utils.unregister_classes(reversed(classes)),)
	return tuple(map(
		lambda func: classmethod(lambda cls: func()),
		ret)) if class_method else ret
utils.register_classes_factory = _register_classes_factory

def _ensure_animation_data(id):
	if id.animation_data is None:
		id.animation_data_create()
utils.ensure_animation_data = _ensure_animation_data

def _main(*, register, unregister):
	try:
		unregister()
	except:
		pass
	register()
utils.main = _main
