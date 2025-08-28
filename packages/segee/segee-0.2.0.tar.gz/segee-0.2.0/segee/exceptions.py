"""Custom exceptions for the Segee package."""

from __future__ import annotations


class SegmentTreeError(Exception):
    """Base exception for all segment tree related errors."""


class SegmentTreeIndexError(SegmentTreeError, IndexError):
    """Raised when an index is out of bounds for the segment tree."""

    def __init__(self, index: int, size: int) -> None:
        """Initialize the exception with index and size information.

        Args:
            index: The invalid index that was accessed.
            size: The size of the segment tree.
        """
        self.index = index
        self.size = size
        super().__init__(f"Index {index} is out of bounds for segment tree of size {size}")


class SegmentTreeRangeError(SegmentTreeError, ValueError):
    """Raised when a range query has invalid bounds."""

    def __init__(self, left: int, right: int, size: int) -> None:
        """Initialize the exception with range and size information.

        Args:
            left: The left bound of the invalid range.
            right: The right bound of the invalid range.
            size: The size of the segment tree.
        """
        self.left = left
        self.right = right
        self.size = size
        super().__init__(f"Invalid range [{left}, {right}) for segment tree of size {size}")


class SegmentTreeInitializationError(SegmentTreeError, ValueError):
    """Raised when segment tree initialization parameters are invalid."""
