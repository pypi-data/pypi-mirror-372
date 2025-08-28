"""Segee - High-performance segment tree implementation for Python.

This package provides an enterprise-grade Segment Tree data structure that supports
efficient range queries and point updates in O(log n) time complexity.

Examples:
    Basic usage with generic segment tree:

    >>> from segee import GenericSegmentTree
    >>> import operator
    >>> tree = GenericSegmentTree(5, 0, operator.add)
    >>> tree.set(0, 10)
    >>> tree.set(1, 20)
    >>> tree.prod(0, 2)  # Sum of elements from index 0 to 1
    30

    Convenient specialized classes:

    >>> from segee import SumSegmentTree, MinSegmentTree, MaxSegmentTree
    >>> sum_tree = SumSegmentTree(5)
    >>> sum_tree.set(0, 10)
    >>> sum_tree.sum(0, 2)  # More readable than prod()
    10

    Binary Indexed Tree for efficient range sum queries:

    >>> from segee import BinaryIndexedTree, RangeAddBinaryIndexedTree
    >>> bit = BinaryIndexedTree([1, 2, 3, 4, 5])
    >>> bit.add(2, 10)  # Add 10 to index 2
    >>> bit.sum(1, 4)  # Sum from index 1 to 3
    19

    >>> rubit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
    >>> rubit.add(1, 4, value=10)  # Add 10 to range [1, 4)
    >>> rubit.sum(0, 5)  # Sum of entire array
    45
"""

from __future__ import annotations

try:
    from importlib.metadata import version

    __version__ = version("segee")
except ImportError:
    # For Python < 3.8
    try:
        from importlib_metadata import version

        __version__ = version("segee")
    except ImportError:
        __version__ = "unknown"

# Type definitions are now local to each module
from .binary_indexed_tree import BinaryIndexedTree, RangeAddBinaryIndexedTree
from .exceptions import (
    SegmentTreeError,
    SegmentTreeIndexError,
    SegmentTreeInitializationError,
    SegmentTreeRangeError,
)
from .segment_tree import GenericSegmentTree, MaxSegmentTree, MinSegmentTree, SumSegmentTree

__all__ = [
    "BinaryIndexedTree",
    "GenericSegmentTree",
    "MaxSegmentTree",
    "MinSegmentTree",
    "RangeAddBinaryIndexedTree",
    "SegmentTreeError",
    "SegmentTreeIndexError",
    "SegmentTreeInitializationError",
    "SegmentTreeRangeError",
    "SumSegmentTree",
    "__version__",
]
