from typing import *

__all__ = ["Scaevola"]


class Scaevola:
    def __ge__(self: Self, other: Any) -> Any:
        "This magic method implements self>=other."
        return type(self)(other) <= self

    def __gt__(self: Self, other: Any) -> Any:
        "This magic method implements self>other."
        return type(self)(other) < self

    def __radd__(self: Self, other: Any) -> Any:
        "This magic method implements other+self."
        return type(self)(other) + self

    def __rand__(self: Self, other: Any) -> Any:
        "This magic method implements other&self."
        return type(self)(other) & self

    def __rdivmod__(self: Self, other: Any) -> Any:
        "This magic method implements divmod(other, self)."
        return divmod(type(self)(other), self)

    def __rfloordiv__(self: Self, other: Any) -> Any:
        "This magic method implements other//self."
        return type(self)(other) // self

    def __rlshift__(self: Self, other: Any) -> Any:
        "This magic method implements other<<self."
        return type(self)(other) << self

    def __rmatmul__(self: Self, other: Any) -> Any:
        "This magic method implements other@self."
        return type(self)(other) @ self

    def __rmod__(self: Self, other: Any) -> Any:
        "This magic method implements other%self."
        return type(self)(other) % self

    def __rmul__(self: Self, other: Any) -> Any:
        "This magic method implements other*self."
        return type(self)(other) * self

    def __ror__(self: Self, other: Any) -> Any:
        "This magic method implements other|self."
        return type(self)(other) | self

    def __rpow__(self: Self, other: Any) -> Any:
        "This magic method implements pow(other, self)."
        return type(self)(other) ** self

    def __rrshift__(self: Self, other: Any) -> Any:
        "This magic method implements other>>self."
        return type(self)(other) >> self

    def __rsub__(self: Self, other: Any) -> Any:
        "This magic method implements other-self."
        return type(self)(other) - self

    def __rtruediv__(self: Self, other: Any) -> Any:
        "This magic method implements other/self."
        return type(self)(other) / self

    def __rxor__(self: Self, other: Any) -> Any:
        "This magic method implements other^self."
        return type(self)(other) ^ self
