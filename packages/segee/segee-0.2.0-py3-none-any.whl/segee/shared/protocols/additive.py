"""Additive protocol for the Segee package.

This module defines a simple protocol for types that support additive operations.
This protocol enables static type checking for types used in data structures
requiring addition and subtraction operations.
"""

from __future__ import annotations

from typing import Protocol, Self, TypeVar

__all__ = ["AdditiveProtocol"]

T = TypeVar("T", bound="AdditiveProtocol")


class AdditiveProtocol(Protocol):
    """Protocol for types that support addition and subtraction operations.

    This protocol defines the essential operations needed for additive data structures
    like Binary Indexed Trees and Sum Segment Trees.

    Examples:
        Types that support this protocol: int, float, Decimal, complex, etc.
    """

    def __add__(self, other: Self) -> Self:
        """Add two values together.

        Args:
            other: The value to add to this value.

        Returns:
            The result of the addition.
        """
        ...

    def __sub__(self, other: Self) -> Self:
        """Subtract another value from this value.

        Args:
            other: The value to subtract from this value.

        Returns:
            The result of the subtraction.
        """
        ...
