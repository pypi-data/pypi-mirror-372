"""Generic Binary Indexed Tree (Fenwick Tree) implementation for the Segee package."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from segee.exceptions import (
    SegmentTreeError,
    SegmentTreeIndexError,
    SegmentTreeRangeError,
)
from segee.shared.backbone.sequence_protocol import SequenceProtocolMixin
from segee.shared.protocols import AdditiveProtocol
from segee.shared.queries.point_add_query import PointAddQueryMixin
from segee.shared.queries.range_sum_query import RangeSumQueryMixin

T = TypeVar("T", bound=AdditiveProtocol)

__all__ = ["BinaryIndexedTreeError", "GenericBinaryIndexedTree"]


class BinaryIndexedTreeError(SegmentTreeError):
    """Base exception for all binary indexed tree related errors."""


class GenericBinaryIndexedTree[T: AdditiveProtocol](
    SequenceProtocolMixin, PointAddQueryMixin, RangeSumQueryMixin[T]
):
    """Binary Indexed Tree (Fenwick Tree) for efficient prefix sum queries."""

    __slots__ = ("_size", "_tree")

    def __init__(self, data: int | Sequence[T] = 0) -> None:
        """Initialize the Binary Indexed Tree.

        Args:
            data: Either an integer specifying the size (initialized with zeros),
                    or a sequence of numbers to initialize the tree with.

        Raises:
            BinaryIndexedTreeError: If data is invalid.
        """
        if isinstance(data, int):
            if data < 0:
                msg = f"Size must be non-negative, got {data}"
                raise BinaryIndexedTreeError(msg)
            self._size = data
            self._tree: list[T] = [0] * (data + 1)
        else:
            if not isinstance(data, Sequence) or isinstance(data, str | bytes):
                msg = f"Expected int or Sequence, got {type(data)}"
                raise BinaryIndexedTreeError(msg)

            self._size = len(data)
            self._tree: list[T] = [0] * (len(data) + 1)

            # Initialize the tree with the provided data
            for i, value in enumerate(data):
                self.add(i, value)

    @property
    def identity(self) -> T:
        """Identity element for the additive operation."""
        return 0

    @property
    def size(self) -> int:
        """Get the size of the binary indexed tree."""
        return self._size

    def add(self, index: int, value: T) -> None:
        """Add a value to the element at the specified index."""
        if not 0 <= index < self._size:
            raise SegmentTreeIndexError(index, self._size)

        # Convert to 1-based indexing for internal operations
        index += 1
        while index <= self._size:
            self._tree[index] += value
            index += index & (-index)

    def set(self, index: int, value: T) -> None:
        """Set the element at the specified index to a specific value."""
        current = self.get(index)
        self.add(index, value - current)

    def get(self, index: int) -> T:
        """Get the element at the specified index."""
        if not 0 <= index < self._size:
            raise SegmentTreeIndexError(index, self._size)

        return self.sum(index, index + 1)

    def prefix_sum(self, right: int) -> T:
        """Compute the sum of elements from index 0 to right-1 (inclusive)."""
        if not 0 <= right <= self._size:
            raise SegmentTreeRangeError(0, right, self._size)
        return self._prefix_sum_internal(right)

    def _prefix_sum_internal(self, right: int) -> T:
        """Internal method to compute prefix sum for 0-based right index."""
        result = 0
        while right > 0:
            result += self._tree[right]
            right -= right & (-right)
        return result

    def sum(self, left: int = 0, right: int | None = None) -> T:
        """Get the sum of elements in the range [left, right)."""
        if right is None:
            right = self._size

        if not 0 <= left <= right <= self._size:
            raise SegmentTreeRangeError(left, right, self._size)

        if left == right:
            return 0

        return self._prefix_sum_internal(right) - self._prefix_sum_internal(left)

    def total(self) -> T:
        """Get the sum of all elements in the binary indexed tree."""
        return self.sum(0)

    def __len__(self) -> int:
        """Return the length of the binary indexed tree."""
        return self._size

    def __getitem__(self, index: int) -> T:
        """Get element at the specified index."""
        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        """Set element at the specified index."""
        self.set(index, value)

    def __iter__(self):
        """Iterate over all elements."""
        for i in range(self._size):
            yield self.get(i)

    def to_list(self) -> list[T]:
        """Convert to a regular Python list."""
        return list(self)
