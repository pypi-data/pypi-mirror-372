from typing import *

__all__ = ["unhash"]


def __hash__(self: Self, /) -> int:
    "This magic method implements hash(self) and raises a TypeError when it is called."
    raise TypeError("unhashable type: %r" % type(self).__name__)


unhash = __hash__
