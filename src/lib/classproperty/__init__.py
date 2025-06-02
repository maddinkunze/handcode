import typing

_T = typing.TypeVar("_T")
_O = typing.TypeVar("_O")

class classproperty(typing.Generic[_T, _O]):
    def __init__(self, f: typing.Callable[[_O], _T]):
        self.f = f
    def __get__(self, obj, owner: _O) -> _T:
        return self.f(owner)