# Copyright 2025 Yunqi Inc
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T", bound=object)


def _register_internal(cls: type[T], signature: str) -> None:
    pass


def annotate(signature: str) -> Callable[[type[T]], type[T]]:
    """Decorator for annotating a UDF class.

    Example:

    >>> @annotate("string,int->string")
    ... class Repeat:
    ...     def evaluate(self, x: str, y: int) -> str:
    ...         return x * y if x and y > 0 else ""

    Args:
        signature: The signature of the UDF.
    """

    def _wrapper(cls: type[T]) -> type[T]:
        _register_internal(cls, signature)
        return cls

    return _wrapper
