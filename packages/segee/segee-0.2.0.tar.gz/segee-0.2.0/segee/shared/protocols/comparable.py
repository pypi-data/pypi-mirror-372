"""Comparable protocol for the Segee package.

This module defines a simple protocol for types that support comparison operations.
This protocol enables min/max operations and ordering-based data structures
like Min/Max Segment Trees.
"""

from __future__ import annotations

from typing import Protocol, Self, TypeVar

__all__ = ["ComparableProtocol"]

T = TypeVar("T", bound="ComparableProtocol")


class ComparableProtocol(Protocol):
    """Protocol for types that support comparison operations.

    This protocol defines the essential operations needed for order-based
    data structures like Min/Max Segment Trees.

    Examples:
        Types that support this protocol: int, float, str, datetime, etc.
    """

    def __lt__(self, other: Self) -> bool:
        """Check if this value is less than another.

        Args:
            other: The value to compare against.

        Returns:
            True if self < other, False otherwise.
        """
        ...

    def __le__(self, other: Self) -> bool:
        """Check if this value is less than or equal to another.

        Args:
            other: The value to compare against.

        Returns:
            True if self <= other, False otherwise.
        """
        ...

    def __gt__(self, other: Self) -> bool:
        """Check if this value is greater than another.

        Args:
            other: The value to compare against.

        Returns:
            True if self > other, False otherwise.
        """
        ...

    def __ge__(self, other: Self) -> bool:
        """Check if this value is greater than or equal to another.

        Args:
            other: The value to compare against.

        Returns:
            True if self >= other, False otherwise.
        """
        ...
