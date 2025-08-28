"""Range add query mixin for data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from segee.shared.protocols import AdditiveProtocol

T = TypeVar("T", bound=AdditiveProtocol)

__all__ = ["RangeAddQueryMixin"]


class RangeAddQueryMixin[T](ABC):
    """Mixin providing range add query operations.

    This mixin defines the interface for data structures that support
    adding values to ranges of indices efficiently.
    """

    @abstractmethod
    def add(self, left: int, right: int, value: T) -> None:
        """Add a value to all elements in the specified range.

        Args:
            left: The left bound of the range (inclusive).
            right: The right bound of the range (exclusive).
            value: The value to add to all elements in the range.

        Raises:
            SegmentTreeRangeError: If the range is invalid.

        Time Complexity:
            O(log n) for segment trees with lazy propagation,
            O(log n) for range-updatable binary indexed trees.
        """
        ...

    @abstractmethod
    def get(self, index: int) -> T:
        """Get the current value at the specified index.

        Args:
            index: The index to query.

        Returns:
            The current value at the specified index.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.

        Time Complexity:
            O(log n)
        """
        ...
