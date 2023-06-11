# -*- coding: bccelerator-transform-UTF-8 -*-
from enum import Enum as _Enum
import sys as _sys
from typing import Any as _Any, ClassVar as _ClassVar, Sequence as _Seq

if _sys.version_info >= (3, 11):
    from enum import StrEnum as StrEnum
else:

    class StrEnum(str, _Enum):
        __slots__: _ClassVar = ()

        """Enum where members are also (and must be) strings."""

        def __new__(cls, *values: _Any):
            value = str(*values)
            self = str.__new__(cls, value)
            self._value_ = value
            return self

        @staticmethod
        def _generate_next_value_(
            name: str,
            start: int,
            count: int,
            last_values: _Seq[_Any],
        ):
            """Return the lower-cased version of the member name."""
            return name.lower()

        def __str__(self):
            return self._value_
