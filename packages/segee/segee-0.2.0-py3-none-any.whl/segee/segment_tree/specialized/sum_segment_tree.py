"""Sum Segment Tree implementation for the Segee package."""

from __future__ import annotations

import operator

from segee.segment_tree.backbone.generic_segment_tree import GenericSegmentTree
from segee.shared.queries.range_sum_query import RangeSumQueryMixin

__all__ = ["SumSegmentTree"]


class SumSegmentTree(GenericSegmentTree[int | float], RangeSumQueryMixin[int | float]):
    """Specialized Segment Tree for sum range queries.

    A convenience class that pre-configures the segment tree for sum operations
    with identity element 0 and addition operation.

    Examples:
        >>> tree = SumSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 20)
        >>> tree.prod(0, 2)  # Sum of elements from index 0 to 1
        30
        >>> tree.all_prod()  # Sum of all elements
        30
    """

    def __init__(self, size: int) -> None:
        """Initialize a Sum Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, 0, operator.add)

    @property
    def identity(self) -> int | float:
        """Identity element for sum operations (zero)."""
        return 0

    def prefix_sum(self, right: int) -> int | float:
        """Compute the sum of elements from index 0 to right-1 (inclusive).

        Args:
            right: Right boundary (exclusive, 0-based).

        Returns:
            Sum of elements in the range [0, right).

        Time complexity: O(log n)
        """
        return self.prod(0, right)

    def sum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the sum of elements in the range [left, right).

        This is an alias for the prod() method for better readability.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The sum of all elements in the specified range.
        """
        return self.prod(left, right)

    def total(self) -> int | float:
        """Get the sum of all elements in the segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The sum of all elements in the segment tree.
        """
        return self.all_prod()
