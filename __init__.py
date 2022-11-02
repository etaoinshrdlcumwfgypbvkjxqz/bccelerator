# SPDX-License-Identifier: GPL-3.0-or-later

import types as _types
import typing as _typing

from . import main
from .bccelerator.util import utils as _utils

# bl_info is parsed with AST so only 'bl_info = {...}' is allowed
bl_info = {
    'name': 'bccelerator',
    'description': 'Contains tools to accelerate Blender workflow.',
    'author': 'William So',
    'version': (1, 0, 0),
    'blender': (3, 30, 0),
    'location': 'Multiple locations',
    'warning': '',
    'doc_url': '',  # template: {BLENDER_MANUAL_URL}/addons/(location)
    'tracker_url': '',
    'support': 'COMMUNITY',
    'category': 'General',
}
bl_info: _typing.Mapping[str, str | tuple[int,
                                          int, int]] = _types.MappingProxyType(bl_info)
register: _typing.Callable[[], None] = main.register
unregister: _typing.Callable[[], None] = main.unregister

if __name__ == '__main__':
    _utils.main(register=register, unregister=unregister)
