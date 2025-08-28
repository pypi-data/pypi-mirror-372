"""Multiplicative protocol for the Segee package.

This module defines a simple protocol for types that support multiplicative operations.
This protocol enables static type checking for types used in data structures
requiring multiplication operations.
"""

from __future__ import annotations

from typing import Protocol, Self

__all__ = ["MultiplicativeProtocol"]


class MultiplicativeProtocol(Protocol):
    """Protocol for types that support multiplication operations.

    This protocol defines the essential operations needed for multiplicative
    data structures and mathematical computations.

    Examples:
        Types that support this protocol: int, float, Decimal, complex, etc.
    """

    def __mul__(self: Self, other: Self) -> Self:
        """Multiply this value with another.

        Args:
            other: The value to multiply with this value.

        Returns:
            The result of the multiplication.
        """
        ...

    def __inv__(self: Self) -> Self:
        """Return the multiplicative inverse of this value.

        Returns:
            The multiplicative inverse of this value.
        """
        ...
