# -*- coding: UTF-8 -*-
from bpy.types import bpy_prop_collection as _bpy_collection
from codecs import Codec as _Codec, CodecInfo as _CodecInfo, lookup as _lookup
from io import StringIO as _StringIO
from itertools import chain as _chain, repeat as _repeat
from json import dumps as _dumps, loads as _loads
from re import MULTILINE as _MULTILINE, compile as _compile
from token import (
    COMMENT as _COMMENT,
    ENDMARKER as _ENDMARKER,
    LSQB as _LSQB,
    NAME as _NAME,
    NEWLINE as _NEWLINE,
    RSQB as _RSQB,
)
from tokenize import generate_tokens as _gen_tokens, untokenize as _untokenize
from typing import (
    ClassVar as _ClassVar,
    Iterator as _Itor,
    Literal as _Literal,
    Sequence as _Seq,
)


class BcceleratorTransform(_Codec):
    __slots__: _ClassVar = ("__codec",)
    __SeralizedType: _ClassVar = _Seq[str]
    __format: _ClassVar = "# bccelerator-transform: {}\n"
    __regex: _ClassVar = _compile(r"^# bccelerator-transform: (.+)$", flags=_MULTILINE)

    def __init__(self, codec: _CodecInfo):
        super().__init__()
        self.__codec = codec

    def encode(self, input: str, errors: str = "strict"):
        match = self.__regex.search(input)
        if match:
            serialized: BcceleratorTransform.__SeralizedType = _loads(
                input[match.start(1) : match.end(1)]
            )
        else:
            serialized = ()

        def gen_tokens() -> _Itor[tuple[int, str]]:
            inserts = _chain(iter(serialized), _repeat(""))
            state: _Literal["", "match", "alias"] = ""
            aliases = {
                _bpy_collection.__name__,
            }
            for token in _gen_tokens(iter(input.splitlines(keepends=True)).__next__):
                if state == "match":
                    if token.exact_type == _NAME and token.string == "as":
                        state = "alias"
                    else:
                        state = ""
                        yield from map(
                            lambda token: token[:2],
                            _gen_tokens(
                                iter(next(inserts).splitlines(keepends=True)).__next__
                            ),
                        )
                elif state == "alias":
                    state = ""
                    aliases.add(token.string)
                else:
                    if token.exact_type == _NAME and token.string in aliases:
                        state = "match"
                yield token[:2]

        return self.__codec.encode(_untokenize(gen_tokens()), errors=errors)

    def decode(self, input: bytes, errors: str = "strict"):
        inter, consumed = self.__codec.decode(input, errors=errors)

        def gen_tokens():
            state: _Literal["", "alias"] | int = ""
            deleted = list[_StringIO]()
            aliases = {
                _bpy_collection.__name__,
            }
            for token in _gen_tokens(iter(inter.splitlines(keepends=True)).__next__):
                if isinstance(state, int):
                    if token.exact_type == _NAME and token.string == "as":
                        state = "alias"
                        deleted.pop()
                        yield token[:2]
                    elif token.exact_type == _LSQB:
                        state += 1
                        deleted[-1].write(token.string)
                    elif token.exact_type == _RSQB:
                        state -= 1
                        deleted[-1].write(token.string)
                        if state == 0:
                            state = ""
                    elif state == 0:
                        state = ""
                        yield token[:2]
                    else:
                        deleted[-1].write(token.string)
                else:
                    if token.exact_type == _ENDMARKER:
                        yield (_NEWLINE, "\n")
                        seralized: BcceleratorTransform.__SeralizedType = tuple(
                            map(_StringIO.getvalue, deleted)
                        )
                        yield (
                            _COMMENT,
                            self.__format.format(_dumps(seralized, ensure_ascii=True)),
                        )
                    yield token[:2]
                    if token.exact_type == _NAME and token.string in aliases:
                        state = 0
                        deleted.append(_StringIO())
                    if state == "alias":
                        state = ""
                        aliases.add(token.string)

        return _untokenize(gen_tokens()), consumed


def lookup(name: str):
    codec0 = None
    if name.startswith("bccelerator_transform"):
        encoding = name[len("bccelerator_transform") :]
        if not encoding.startswith("_"):
            encoding = "_UTF-8"
        try:
            codec0 = _lookup(encoding[1:])
        except LookupError:
            pass
    if codec0 is None:
        return None
    codec = BcceleratorTransform(codec0)
    return _CodecInfo(encode=codec.encode, decode=codec.decode, name=name)
