"""Range Updatable Binary Indexed Tree implementation for common numeric types."""

from __future__ import annotations

from segee.binary_indexed_tree.backbone.generic_range_updatable_binary_indexed_tree import (
    GenericRangeAddBinaryIndexedTree,
)

__all__ = ["RangeAddBinaryIndexedTree"]


class RangeAddBinaryIndexedTree(GenericRangeAddBinaryIndexedTree[int | float]):
    """Range Updatable Binary Indexed Tree with support for range updates.

    A convenience class that pre-configures the range updatable binary indexed tree
    for common numeric operations with int and float types.

    This data structure supports:
    - Point updates in O(log n) time
    - Range updates in O(log n) time
    - Prefix sum queries in O(log n) time
    - Range sum queries in O(log n) time

    Uses two Binary Indexed Trees internally to support efficient range updates
    through difference array technique.

    Examples:
        >>> bit = RangeAddBinaryIndexedTree(5)  # Create tree of size 5
        >>> bit.add(1, 4, value=3)  # Add 3 to range [1, 4)
        >>> bit.sum(1, 4)  # Sum of range [1, 4)
        9
        >>> bit[2]  # Get value at index 2
        3

        >>> bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        >>> bit.add(0, 3, value=10)  # Add 10 to [0, 1, 2]
        >>> bit.to_list()
        [11, 12, 13, 4, 5]
    """

    def __repr__(self) -> str:
        """Return a string representation of the tree."""
        values = list(self)
        return f"RangeAddBinaryIndexedTree({values})"
