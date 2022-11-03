# -*- coding: bccelerator-transform-UTF-8 -*-

import enum as _enum
import sys as _sys
import typing as _typing

if _sys.version_info >= (3, 11):
    Self = _typing.Self
    StrEnum: type[_enum.StrEnum] = _enum.StrEnum
else:
    @_typing._SpecialForm
    def Self(self: _typing.Any, parameters: _typing.Sequence[_typing.Any]):
        '''Used to spell the type of "self" in classes.

        Example::
          from typing import Self
          class ReturnsSelf:
              def parse(self, data: bytes) -> Self:
                  ...
                  return self
        '''
        raise TypeError(f'{self} is not subscriptable')

    class StrEnum(str, _enum.Enum):
        __slots__: _typing.ClassVar = ()

        '''Enum where members are also (and must be) strings.'''

        def __new__(cls: type[Self], *values: _typing.Any) -> Self:
            value: str = str(*values)
            self: Self = str.__new__(cls, value)
            self._value_ = value
            return self

        @staticmethod
        def _generate_next_value_(name: str, start: int, count: int, last_values: _typing.Sequence[_typing.Any]) -> str:
            '''Return the lower-cased version of the member name.'''
            return name.lower()

        def __str__(self: Self) -> str:
            return self._value_
