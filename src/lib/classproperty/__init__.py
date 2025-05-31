import typing

_T = typing.TypeVar("_T")

class classproperty(typing.Generic[_T]):
    def __init__(self, f: typing.Callable[[], _T]):
        self.f = f
    def __get__(self, obj, owner) -> _T:
        return self.f(owner)