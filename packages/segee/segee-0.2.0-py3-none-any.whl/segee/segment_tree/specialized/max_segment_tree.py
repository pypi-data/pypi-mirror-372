"""Max Segment Tree implementation for the Segee package."""

from __future__ import annotations

from segee.segment_tree.backbone.generic_segment_tree import GenericSegmentTree
from segee.shared.queries.range_max_query import RangeMaxQueryMixin

__all__ = ["MaxSegmentTree"]


class MaxSegmentTree(GenericSegmentTree[int | float], RangeMaxQueryMixin[int | float]):
    """Specialized Segment Tree for maximum range queries.

    A convenience class that pre-configures the segment tree for maximum operations
    with identity element negative infinity and max operation.

    Examples:
        >>> tree = MaxSegmentTree(5)
        >>> tree.set(0, 10)
        >>> tree.set(1, 5)
        >>> tree.set(2, 20)
        >>> tree.prod(0, 3)  # Maximum of elements from index 0 to 2
        20
        >>> tree.maximum(1, 3)  # Alternative method name
        20
    """

    def __init__(self, size: int) -> None:
        """Initialize a Max Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
        """
        super().__init__(size, float("-inf"), max)

    def maximum(self, left: int = 0, right: int | None = None) -> int | float:
        """Get the maximum element in the range [left, right).

        Implementation of the abstract method from RangeMaxQueryMixin.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The maximum element in the specified range.
        """
        return self.prod(left, right)

    def global_max(self) -> int | float:
        """Get the maximum element in the entire segment tree.

        This is an alias for the all_prod() method for better readability.

        Returns:
            The maximum element in the segment tree.
        """
        return self.all_prod()
