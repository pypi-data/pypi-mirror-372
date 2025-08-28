"""Min Segment Tree implementation for the Segee package."""

from __future__ import annotations

from segee.segment_tree.backbone.generic_segment_tree import GenericSegmentTree
from segee.shared.queries.range_min_query import RangeMinQueryMixin

__all__ = ["MinSegmentTree"]


class MinSegmentTree(GenericSegmentTree[int | float], RangeMinQueryMixin[int | float]):
    """Specialized Segment Tree for minimum range queries.

    A convenience class that pre-configures the segment tree for minimum operations
    with identity element positive infinity and min operation.

    Examples:
        >>> tree = MinSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 5)
        >>> tree.set(2, 20)
        >>> tree.prod(0, 3)  # Minimum of elements from index 0 to 2
        5
        >>> tree.minimum(1, 3)  # Alternative method name
        5
    """

    def __init__(self, size: int) -> None:
        """Initialize a Min Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, float("inf"), min)

    def minimum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the minimum element in the range [left, right).

        Implementation of the abstract method from RangeMinQueryMixin.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The minimum element in the specified range.
        """
        return self.prod(left, right)

    def global_min(self) -> int | float:
        """Get the minimum element in the entire segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The minimum element in the segment tree.
        """
        return self.all_prod()
