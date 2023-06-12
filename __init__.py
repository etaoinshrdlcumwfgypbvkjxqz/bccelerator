# -*- coding: UTF-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
from codecs import register as _cdx_reg, unregister as _cdx_unreg
from typing import Mapping as _Map

bl_info: _Map[str, str | tuple[int, int, int]]
# bl_info is parsed with AST so only 'bl_info = {...}' is allowed
# set_default is called on it so it needs to be modifiable
bl_info = {
    "name": "bccelerator",
    "description": "Contains tools to accelerate Blender workflow.",
    "author": "William So",
    "version": (1, 5, 0),
    "blender": (3, 3, 0),
    "location": "Multiple locations",
    "warning": "",
    "doc_url": "",  # template: {BLENDER_MANUAL_URL}/addons/(location)
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "General",
}
VERSION = bl_info["version"]


def register():
    from ._codec import lookup

    _cdx_reg(lookup)
    from .main import register

    register()


def unregister():
    from .main import unregister

    unregister()
    from ._codec import lookup

    _cdx_unreg(lookup)
