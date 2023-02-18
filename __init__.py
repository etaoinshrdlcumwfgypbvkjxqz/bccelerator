# -*- coding: UTF-8 -*-
import codecs as _codecs
import typing as _typing

from . import _codec

bl_info: _typing.Mapping[str, str | tuple[int, int, int]]
# bl_info is parsed with AST so only 'bl_info = {...}' is allowed
# set_default is called on it so it needs to be modifiable
bl_info = {
    "name": "bccelerator",
    "description": "Contains tools to accelerate Blender workflow.",
    "author": "William So",
    "version": (1, 2, 3),
    "blender": (3, 3, 0),
    "location": "Multiple locations",
    "warning": "",
    "doc_url": "",  # template: {BLENDER_MANUAL_URL}/addons/(location)
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "General",
}


def register() -> None:
    _codecs.register(_codec.lookup)
    from . import main

    main.register()


def unregister() -> None:
    from . import main

    main.unregister()
    _codecs.unregister(_codec.lookup)


if __name__ == "__main__":
    register()
