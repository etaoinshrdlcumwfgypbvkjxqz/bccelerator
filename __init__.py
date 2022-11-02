import typing as _typing

from . import main
from .bccelerator.util import utils as _utils

register: _typing.Callable[[], None] = main.register
unregister: _typing.Callable[[], None] = main.unregister

if __name__ == '__main__':
    _utils.main(register=register, unregister=unregister)
