"""Binary Indexed Tree implementation for common numeric types."""

from __future__ import annotations

from segee.binary_indexed_tree.backbone.generic_binary_indexed_tree import GenericBinaryIndexedTree

__all__ = ["BinaryIndexedTree"]


class BinaryIndexedTree(GenericBinaryIndexedTree[int | float]):
    """Binary Indexed Tree (Fenwick Tree) for efficient prefix sum queries.

    A convenience class that pre-configures the binary indexed tree for common
    numeric operations with int and float types.

    This class is a concrete implementation of GenericBinaryIndexedTree[int | float]
    that provides optimized performance for standard numeric operations.

    Examples:
        >>> bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        >>> bit.add(2, 10)  # Add 10 to index 2
        >>> bit.sum(1, 4)   # Sum from index 1 to 3
        19
        >>> bit[2]          # Get value at index 2
        13

        >>> bit = BinaryIndexedTree(5)  # Create tree of size 5
        >>> bit[0] = 10
        >>> bit[1] = 20
        >>> bit.prefix_sum(2)  # Sum of [0, 1]
        30
    """

    def __repr__(self) -> str:
        """Return a string representation of the tree."""
        values = list(self)
        return f"BinaryIndexedTree({values})"
