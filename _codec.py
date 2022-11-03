import bpy as _bpy
import codecs as _codecs
import io as _io
import itertools as _itertools
import token as _token
import tokenize as _tokenize
import typing as _typing

_T = _typing.TypeVar('_T')
_Self: _typing.TypeAlias = _typing.Annotated[_T, 'Self']


class BcceleratorTransform(_codecs.Codec):
    __slots__: _typing.ClassVar = ('__codec',)
    __delayed_tokens: _typing.AbstractSet[int] = frozenset(
        {_token.COLON, _token.EQUAL, })

    def __init__(self: _Self['BcceleratorTransform'], codec: _codecs.CodecInfo) -> None:
        super().__init__()
        self.__codec: _codecs.CodecInfo = codec

    def encode(self: _Self['BcceleratorTransform'], input: str, errors: str = 'strict') -> tuple[bytes, int]:
        def gen_tokens() -> _typing.Iterator[tuple[int, str]]:
            comment: bool = False
            token: _tokenize.TokenInfo
            for token in _tokenize.generate_tokens(iter(input.splitlines(keepends=True)).__next__):
                if comment:
                    comment = False
                    if token.exact_type == _token.COMMENT:
                        yield from map(lambda token: token[:2],
                                       _tokenize.generate_tokens(
                                           iter(token.string[1:].splitlines(keepends=True)).__next__)
                                       )
                    elif token.exact_type in self.__delayed_tokens:
                        comment = True
                    else:
                        yield token[:2]
                else:
                    yield token[:2]
                    if token.exact_type == _token.NAME and token.string == _bpy.types.bpy_prop_collection.__name__:
                        comment = True
        return self.__codec.encode(_tokenize.untokenize(gen_tokens()), errors=errors)

    def decode(self: _Self['BcceleratorTransform'], input: bytes, errors: str = 'strict') -> tuple[str, int]:
        inter: str
        consumed: int
        inter, consumed = self.__codec.decode(input, errors=errors)

        def gen_tokens() -> _typing.Iterator[tuple[int, str]]:
            level: int | None = None
            comment: _io.StringIO = _io.StringIO()
            write: bool = False
            token: _tokenize.TokenInfo
            for token in _tokenize.generate_tokens(iter(inter.splitlines(keepends=True)).__next__):
                if level is None:
                    if write:
                        write = False
                        if token.exact_type in self.__delayed_tokens:
                            comment.write(token.string)
                            yield token[:2]
                        yield (_token.COMMENT, ''.join(_itertools.chain.from_iterable(
                            zip(_itertools.repeat('#'),
                                comment.getvalue().splitlines(keepends=True),)
                        )),)
                        yield (_token.NEWLINE, '\n',)
                        comment.seek(0)
                        comment.truncate()
                        if token.exact_type not in self.__delayed_tokens:
                            yield token[:2]
                    else:
                        yield token[:2]
                    if token.exact_type == _token.NAME and token.string == _bpy.types.bpy_prop_collection.__name__:
                        level = 0
                else:
                    if token.exact_type == _token.LSQB:
                        level += 1
                        comment.write(token.string)
                    elif token.exact_type == _token.RSQB:
                        level -= 1
                        comment.write(token.string)
                        if level == 0:
                            level = None
                            write = True
                    elif level == 0:
                        level = None
                        yield token[:2]
                    else:
                        comment.write(token.string)
        return (_tokenize.untokenize(gen_tokens()), consumed,)


def lookup(name: str) -> _codecs.CodecInfo | None:
    codec0: _codecs.CodecInfo | None = None
    if name.startswith('bccelerator_transform'):
        encoding: str = name[len('bccelerator_transform'):]
        if not encoding.startswith('_'):
            encoding = '_UTF-8'
        try:
            codec0 = _codecs.lookup(encoding[1:])
        except LookupError:
            pass
    if codec0 is None:
        return None
    codec: _codecs.Codec = BcceleratorTransform(codec0)
    return _codecs.CodecInfo(encode=codec.encode, decode=codec.decode, name=name)
