import inspect as _inspect, types as _types, bpy as _bpy

library = _bpy.data.libraries['assets.blend'].filepath\
	if 'assets.blend' in _bpy.data.libraries\
	else None
configuration = _types.MappingProxyType({
	'loader': ('loader.py', library),
	'keys': (
		('common.py', library),
		('animation.py', library),
		('library.py', library),
		('link.py', library),
		('node.py', library),
		('object.py', library),
	),
	'link': None,
	'namespace': None,
})

def main():
	loader = _bpy.data.texts[configuration['loader']].as_module()
	modules = loader.load_modules(**{key: val for key, val in configuration.items()
		if val is not None and key in frozenset(p.name for p
			in _inspect.signature(loader.load_modules).parameters.values()
		)
	})
	modules.reregister()

if __name__ == '__main__':
	main()
