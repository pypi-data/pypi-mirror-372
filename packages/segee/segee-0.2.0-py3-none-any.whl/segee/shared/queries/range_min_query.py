"""Range minimum query mixin for data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from segee.shared.protocols import ComparableProtocol

T = TypeVar("T", bound=ComparableProtocol)

__all__ = ["RangeMinQueryMixin"]


class RangeMinQueryMixin[T](ABC):
    """Mixin providing range minimum query operations.

    This mixin defines the interface for data structures that support
    efficient minimum queries over ranges of indices.
    """

    @abstractmethod
    def minimum(self, left: int = 0, right: int | None = None) -> T:
        """Get the minimum element in the specified range.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The minimum element in the specified range.

        Raises:
            SegmentTreeRangeError: If the range is invalid.

        Time Complexity:
            O(log n)
        """
        ...

    def global_min(self) -> T:
        """Get the minimum element in the entire data structure.

        Returns:
            The minimum element in the data structure.

        Time Complexity:
            O(log n) or O(1) depending on implementation.
        """
        return self.minimum()
