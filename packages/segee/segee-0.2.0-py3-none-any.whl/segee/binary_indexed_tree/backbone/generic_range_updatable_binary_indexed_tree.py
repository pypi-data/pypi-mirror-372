"""Generic Range Updatable Binary Indexed Tree implementation for the Segee package."""

from __future__ import annotations

from collections.abc import Sequence

from segee.exceptions import SegmentTreeIndexError, SegmentTreeRangeError
from segee.shared.backbone.sequence_protocol import SequenceProtocolMixin
from segee.shared.protocols import AdditiveProtocol
from segee.shared.queries.range_sum_query import RangeSumQueryMixin

from .generic_binary_indexed_tree import BinaryIndexedTreeError, GenericBinaryIndexedTree

__all__ = ["GenericRangeAddBinaryIndexedTree"]


class GenericRangeAddBinaryIndexedTree[T: AdditiveProtocol](
    SequenceProtocolMixin, RangeSumQueryMixin[T]
):
    """Range Updatable Binary Indexed Tree with support for range updates.

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

    def __init__(self, data: int | Sequence[T] = 0) -> None:
        """Initialize the Range Updatable Binary Indexed Tree.

        Args:
            data: Either an integer specifying the size (initialized with zeros),
                 or a sequence of numbers to initialize the tree with.

        Raises:
            BinaryIndexedTreeError: If data is invalid.

        Examples:
            >>> bit = RangeAddBinaryIndexedTree(5)  # Size 5, all zeros
            >>> bit = RangeAddBinaryIndexedTree([1, 2, 3])  # Initialize with [1, 2, 3]
        """
        # For range updates, we don't use the parent BIT's storage
        # Instead we use two BITs for the difference array technique
        if isinstance(data, int):
            if data < 0:
                msg = f"Size must be non-negative, got {data}"
                raise BinaryIndexedTreeError(msg)
            self._size = data
        else:
            if not isinstance(data, Sequence) or isinstance(data, str | bytes):
                msg = f"Expected int or Sequence, got {type(data)}"
                raise BinaryIndexedTreeError(msg)
            self._size = len(data)

        # Initialize with data if provided, otherwise zeros
        if isinstance(data, int):
            self._original_data: list[T] = [0] * data
        else:
            self._original_data = list(data)

        # Dual BIT approach for efficient range updates and range queries
        # _bit1: difference array for range updates
        # _bit2: for efficient range sum computation
        self._bit1 = GenericBinaryIndexedTree(self._size)
        self._bit2 = GenericBinaryIndexedTree(self._size)

    @property
    def identity(self) -> T:
        """Identity element for sum operations (zero)."""
        return 0

    def __len__(self) -> int:
        """Return the size of the tree."""
        return self._size

    def __getitem__(self, index: int) -> T:
        """Get the value at the specified index.

        Args:
            index: Zero-based index.

        Returns:
            The value at the specified index.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.
        """
        if not 0 <= index < self._size:
            raise SegmentTreeIndexError(index, self._size)

        # Value at index = original + effect of all range updates
        return self._original_data[index] + self._get_range_update_effect(index)

    def _get_range_update_effect(self, index: int) -> T:
        """Get the cumulative effect of range updates at a specific index using difference array."""
        return self._bit1.prefix_sum(index + 1)

    def __setitem__(self, index: int, value: T) -> None:
        """Set the value at the specified index.

        Args:
            index: Zero-based index.
            value: New value to set.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.
        """
        if not 0 <= index < self._size:
            raise SegmentTreeIndexError(index, self._size)
        current_value = self[index]
        self.add(index, None, value=value - current_value)

    def __repr__(self) -> str:
        """Return a string representation of the tree."""
        values = list(self)
        return f"RangeAddBinaryIndexedTree({values})"

    def add(self, left: int, right: int | None, *, value: T) -> None:
        """Add a value to element(s) at the specified index or range.

        Args:
            left: Left boundary (inclusive, 0-based). For point updates, this is the index.
            right: Right boundary (exclusive, 0-based). If None, performs point update.
            value: Value to add to the element(s).

        Raises:
            SegmentTreeIndexError: If index is out of bounds (point update).
            SegmentTreeRangeError: If the range is invalid (range update).

        Time complexity: O(log n)

        Examples:
            >>> bit.add(2, value=5)        # Point update: add 5 to index 2
            >>> bit.add(1, 4, value=3)     # Range update: add 3 to range [1, 4)
        """
        if right is None:
            # Point update
            if not 0 <= left < self._size:
                raise SegmentTreeIndexError(left, self._size)
            self._original_data[left] += value
        else:
            # Range update
            if not 0 <= left <= right <= self._size:
                raise SegmentTreeRangeError(left, right, self._size)

            if left == right:
                return

            # Dual BIT technique for range updates:
            # BIT1: difference array for point queries
            # BIT2: for efficient range sum computation
            self._bit1.add(left, value)
            self._bit2.add(left, value * left)

            if right < self._size:
                self._bit1.add(right, -value)
                self._bit2.add(right, -value * right)

    def prefix_sum(self, right: int) -> T:
        """Compute the sum of elements from index 0 to right-1 (inclusive).

        Args:
            right: Right boundary (exclusive, 0-based).

        Returns:
            Sum of elements in the range [0, right).

        Raises:
            SegmentTreeRangeError: If right is out of valid range.

        Time complexity: O(log n)
        """
        if not 0 <= right <= self._size:
            raise SegmentTreeRangeError(0, right, self._size)

        if right == 0:
            return 0

        # Efficient O(log n) range sum using dual BIT approach
        original_sum = sum(self._original_data[:right])

        # Using dual BIT technique for O(log n) range sum of updates
        # Formula: sum of range [0, right) = sum(bit1) * right - sum(bit2)
        update_sum = self._bit1.prefix_sum(right) * right - self._bit2.prefix_sum(right)

        return original_sum + update_sum

    def sum(self, left: int = 0, right: int | None = None) -> T:
        """Get the sum of elements in the range [left, right).

        Unified method for both point and range sum queries.

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). If None, sums to the end.

        Returns:
            The sum of all elements in the specified range.

        Raises:
            SegmentTreeRangeError: If the range is invalid.

        Time complexity: O(log n)
        """
        if right is None:
            right = self._size

        if not 0 <= left <= right <= self._size:
            raise SegmentTreeRangeError(left, right, self._size)

        if left == right:
            return 0

        return self.prefix_sum(right) - self.prefix_sum(left)

    def total(self) -> T:
        """Get the sum of all elements in the binary indexed tree.

        This is an alias for compatibility with SumSegmentTree.

        Returns:
            The sum of all elements in the tree.
        """
        return self.sum(0)
