# -*- coding: bccelerator-transform-UTF-8 -*-
import enum as _enum
import sys as _sys
import typing as _typing

if _sys.version_info >= (3, 11):
    StrEnum = _enum.StrEnum
else:

    class StrEnum(str, _enum.Enum):
        __slots__: _typing.ClassVar = ()

        """Enum where members are also (and must be) strings."""

        def __new__(cls, *values: _typing.Any):
            value = str(*values)
            self = str.__new__(cls, value)
            self._value_ = value
            return self

        @staticmethod
        def _generate_next_value_(
            name: str,
            start: int,
            count: int,
            last_values: _typing.Sequence[_typing.Any],
        ):
            """Return the lower-cased version of the member name."""
            return name.lower()

        def __str__(self):
            return self._value_
