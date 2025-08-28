from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from typing import TypeVar

from segee.shared.protocols.additive import AdditiveProtocol

T = TypeVar("T", bound=AdditiveProtocol)


class RangeSumQueryMixin[T](ABC):
    """Mixin for data structures supporting range sum queries."""

    @property
    @abstractmethod
    def identity(self) -> T:
        """Identity element for the sum operation."""
        ...

    @abstractmethod
    def prefix_sum(self, right: int) -> T:
        """Compute the sum of elements from index 0 to right-1 (inclusive).

        Args:
            right: Right boundary (exclusive, 0-based).

        Returns:
            Sum of elements in the range [0, right).

        Time complexity: O(log n)
        """
        ...

    def sum(self, left: int = 0, right: int | None = None) -> T:
        """Compute the sum of elements in the specified range.

        Unified method for both point and range sum queries.

        Args:
            left: Left boundary (inclusive, 0-based). Defaults to 0.
            right: Right boundary (exclusive, 0-based). If None, sums to the end.

        Returns:
            Sum of elements in the range [left, right).

        Time complexity: O(log n)
        """
        if right is None:
            # Get the size from the implementing class
            right = len(self)  # type: ignore[arg-type]

        if left == right:
            return self.identity
        if left > right:
            raise IndexError

        # For additive operations, this works correctly
        # However, for other monoids this may need overriding
        return self.prefix_sum(right) - self.prefix_sum(left)
