# loader

import sys as _sys, types as _types, bpy as _bpy

class LoadedModules:
	'''Contains loaded modules'''
	def __init__(self, modules):
		self.modules = tuple(modules)

	def register(self):
		for module in filter(
			lambda module: callable(getattr(module, 'register', None)),
			self.modules
		):
			module.register()

	def unregister(self):
		for module in filter(
			lambda module: callable(getattr(module, 'unregister', None)),
			self.modules
		):
			module.unregister()

	def reregister(self):
		try:
			self.unregister()
		except:
			pass
		self.register()

	def __iter__(self):
		return self.modules.__iter__()

	def __enter__(self):
		self.reregister()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.unregister()

def _load_module(key, link, namespace_module):
	if isinstance(key, str):
		key = (key, None)
	try:
		module = _bpy.data.texts[key].as_module()
	except KeyError:
		with _bpy.data.libraries.load(key[1], link=True, relative=True)\
			as (data_from, data_to):
			data_to.texts = [key[0]]
		text = data_to.texts[0]
		module = text.as_module()
		if not link:
			_bpy.data.texts.remove(text,
				do_unlink=False, do_id_user=False, do_ui_user=False)
	name = module.__name__
	module.__dict__.update({'__name__': '.'.join((namespace_module.__name__, name))})
	setattr(namespace_module, name, module)
	_sys.modules[module.__name__] = module
	return module

def load_modules(keys, *, link=True, namespace='texts'):
	module = _types.ModuleType(namespace)
	module.__dict__.update({'__file__': _bpy.data.filepath})
	_sys.modules[module.__name__] = module
	return LoadedModules(_load_module(key, link, module) for key in keys)
