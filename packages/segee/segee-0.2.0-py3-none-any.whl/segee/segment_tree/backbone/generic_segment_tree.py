"""High-performance Segment Tree implementation with enterprise-grade design."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from typing import Generic, TypeVar, overload

from segee.exceptions import (
    SegmentTreeIndexError,
    SegmentTreeInitializationError,
    SegmentTreeRangeError,
)
from segee.shared.backbone.sequence_protocol import SequenceProtocolMixin

# Type definitions
T = TypeVar("T")
BinaryOperation = Callable[[T, T], T]
Predicate = Callable[[T], bool]

__all__ = ["GenericSegmentTree"]


class GenericSegmentTree[T](SequenceProtocolMixin[T]):
    """A high-performance Segment Tree data structure for range queries and updates.

    The Segment Tree supports efficient range aggregation queries and point updates
    in O(log n) time complexity. It's designed for scenarios where you need to
    frequently query ranges of data and occasionally update individual elements.

    Examples:
        Basic usage with sum operation:

        >>> def add(a: int, b: int) -> int:
        ...     return a + b
        >>> tree = GenericSegmentTree(5, 0, add)
        >>> tree.set(0, 10)
        >>> tree.set(1, 20)
        >>> tree.prod(0, 2)  # Sum of elements from index 0 to 1
        30

        Usage with custom objects and operations:

        >>> def max_op(a: int, b: int) -> int:
        ...     return max(a, b)
        >>> tree = GenericSegmentTree(3, float('-inf'), max_op)
        >>> tree.set(0, 5)
        >>> tree.set(1, 10)
        >>> tree.set(2, 3)
        >>> tree.prod(0, 3)  # Maximum value in range [0, 3)
        10

    Attributes:
        size: The number of elements the segment tree can hold.
    """

    __slots__ = ("_bit_len", "_data", "_identity", "_offset", "_operation", "_size", "_total_size")

    def __init__(
        self,
        size: int,
        identity: T,
        operation: BinaryOperation[T],
    ) -> None:
        """Initialize a new Segment Tree.

        Args:
            size: The number of elements the segment tree will hold.
                Must be a positive integer.
            identity: The identity element for the operation (e.g., 0 for sum,
                1 for product, float('-inf') for max).
            operation: A binary operation that combines two elements.
                Must be associative (i.e., op(a, op(b, c)) == op(op(a, b), c)).

        Raises:
            SegmentTreeInitializationError: If size is not positive or if the
                operation is not callable.

        Note:
            The operation must be associative for the segment tree to work correctly.
            Common examples include addition, multiplication, min, max, GCD, etc.
        """
        if size <= 0:
            msg = f"Size must be positive, got {size}"
            raise SegmentTreeInitializationError(msg)

        if not callable(operation):
            msg = "Operation must be callable"
            raise SegmentTreeInitializationError(msg)

        self._size = size
        self._identity = identity
        self._operation = operation

        # Calculate the height and total size of the internal tree structure
        self._bit_len = (size - 1).bit_length()
        self._offset = (1 << self._bit_len) - 1
        self._total_size = self._offset + size

        # Initialize the internal array with identity elements
        self._data: list[T] = [self._identity] * self._total_size

    def __hash__(self) -> int:
        """Segment trees are mutable and should not be hashed."""
        msg = "unhashable type: 'GenericSegmentTree'"
        raise TypeError(msg)

    @property
    def size(self) -> int:
        """Get the number of elements in the segment tree."""
        return self._size

    def set(self, index: int, value: T) -> None:
        """Update the element at the specified index.

        Args:
            index: The index to update (0-based).
            value: The new value to set.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.

        Time Complexity:
            O(log n) where n is the size of the segment tree.
        """
        # Handle negative indexing
        if index < 0:
            index += self._size

        self._validate_index(index)

        # Convert to internal index and update the leaf
        internal_index = index + self._offset
        self._data[internal_index] = value

        # Update all parent nodes up to the root
        while internal_index > 0:
            internal_index = self._get_parent_index(internal_index)
            left_child = self._get_left_child_index(internal_index)
            right_child = self._get_right_child_index(internal_index)

            if right_child < self._total_size:
                self._data[internal_index] = self._operation(
                    self._data[left_child],
                    self._data[right_child],
                )
            else:
                self._data[internal_index] = self._data[left_child]

    def get(self, index: int) -> T:
        """Get the element at the specified index.

        Args:
            index: The index to retrieve (0-based).

        Returns:
            The value at the specified index.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.

        Time Complexity:
            O(1)
        """
        # Handle negative indexing
        if index < 0:
            index += self._size

        self._validate_index(index)
        return self._data[index + self._offset]

    def prod(self, left: int = 0, right: int | None = None) -> T:
        """Query the aggregated result over the range [left, right).

        Args:
            left: The left bound of the range (inclusive). Defaults to 0.
            right: The right bound of the range (exclusive). Defaults to size.

        Returns:
            The result of applying the operation to all elements in the range.

        Raises:
            SegmentTreeRangeError: If the range is invalid.

        Time Complexity:
            O(log n) where n is the size of the segment tree.

        Examples:
            >>> tree = GenericSegmentTree(5, 0, lambda a, b: a + b)
            >>> for i in range(5):
            ...     tree.set(i, i + 1)
            >>> tree.prod(1, 4)  # Sum of elements from index 1 to 3
            9
        """
        if right is None:
            right = self._size

        self._validate_range(left, right)

        if left == right:
            return self._identity

        node_indices = self._get_range_nodes(left, right)
        result = self._identity

        for node_index in node_indices:
            result = self._operation(result, self._data[node_index])

        return result

    def all_prod(self) -> T:
        """Query the aggregated result over the entire range.

        Returns:
            The result of applying the operation to all elements.

        Time Complexity:
            O(1)
        """
        return self._data[0] if self._size > 0 else self._identity

    def max_right(self, left: int, predicate: Predicate[T]) -> int:
        """Find the maximum right boundary where the predicate holds.

        Finds the largest index r such that predicate(prod(left, r)) is True.

        Args:
            left: The left bound of the search range.
            predicate: A function that returns True if the condition is satisfied.

        Returns:
            The maximum right boundary (exclusive) where the predicate holds.

        Raises:
            SegmentTreeIndexError: If left is out of bounds.

        Time Complexity:
            O(log n)

        Note:
            The predicate must be monotonic: if predicate(x) is True,
            then predicate(y) should also be True for all y where y can be
            obtained by removing some elements from x.
        """
        if left < 0 or left > self._size:
            raise SegmentTreeIndexError(left, self._size)

        if left == self._size:
            return self._size

        # Convert to internal indexing
        left_internal = left + self._offset
        right_internal = self._get_right_child_index(self._offset - 1)
        current_value = self._identity

        while True:
            # Check if we can include the left node
            if left_internal % 2 == 0:  # Left node is a right child
                test_value = self._operation(current_value, self._data[left_internal])
                if not predicate(test_value):
                    # Binary search within this subtree
                    while left_internal < self._offset:
                        left_internal = self._get_left_child_index(left_internal)
                        test_value = self._operation(current_value, self._data[left_internal])
                        if predicate(test_value):
                            current_value = test_value
                            left_internal += 1
                    break

                current_value = test_value
                if left_internal == right_internal:
                    left_internal = self._total_size
                    break
                left_internal += 1

            if left_internal == right_internal:
                left_internal = self._total_size
                break

            # Move up the tree
            left_internal = self._get_parent_index(left_internal)
            right_internal = self._get_parent_index(right_internal)

        return left_internal - self._offset

    def min_left(self, right: int, predicate: Predicate[T]) -> int:
        """Find the minimum left boundary where the predicate holds.

        Finds the smallest index l such that predicate(prod(l, right)) is True.

        Args:
            right: The right bound of the search range.
            predicate: A function that returns True if the condition is satisfied.

        Returns:
            The minimum left boundary (inclusive) where the predicate holds.

        Raises:
            SegmentTreeIndexError: If right is out of bounds.

        Time Complexity:
            O(log n)

        Note:
            The predicate must be monotonic: if predicate(x) is True,
            then predicate(y) should also be True for all y where y can be
            obtained by removing some elements from x.
        """
        if right < 0 or right > self._size:
            raise SegmentTreeIndexError(right, self._size)

        if right == 0:
            return 0

        # Binary search for the minimum left
        left = 0
        result = right

        while left < result:
            mid = (left + result) // 2
            if predicate(self.prod(mid, right)):
                result = mid
            else:
                left = mid + 1

        return result

    def _validate_index(self, index: int) -> None:
        """Validate that an index is within bounds."""
        if index < 0 or index >= self._size:
            raise SegmentTreeIndexError(index, self._size)

    def _validate_range(self, left: int, right: int) -> None:
        """Validate that a range is valid."""
        if left < 0 or right > self._size or left > right:
            raise SegmentTreeRangeError(left, right, self._size)

    def _get_range_nodes(self, left: int, right: int) -> Iterator[int]:
        """Get the internal node indices that cover the given range."""
        left_internal = left + self._offset
        right_internal = right + self._offset
        left_nodes: list[int] = []
        right_nodes: list[int] = []

        while right_internal - left_internal > 0:
            if left_internal % 2 == 0:  # Left index is a right child
                left_nodes.append(left_internal)
                left_internal += 1

            if right_internal % 2 == 0:  # Right index is a right child
                right_nodes.append(right_internal - 1)
                right_internal -= 1

            left_internal = (left_internal - 1) >> 1
            right_internal = (right_internal - 1) >> 1

        # Yield left nodes first, then right nodes in reverse order
        yield from left_nodes
        yield from reversed(right_nodes)

    def _get_parent_index(self, index: int) -> int:
        """Get the parent index of a node."""
        return (index - 1) >> 1

    def _get_left_child_index(self, index: int) -> int:
        """Get the left child index of a node."""
        return (index << 1) + 1

    def _get_right_child_index(self, index: int) -> int:
        """Get the right child index of a node."""
        return (index << 1) + 2

    # Sequence protocol implementation

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: int | slice) -> T | list[T]:
        """Get element(s) at the specified index or slice."""
        if isinstance(index, slice):
            start, stop, step = index.indices(self._size)
            return [self.get(i) for i in range(start, stop, step)]

        if index < 0:
            index += self._size

        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        """Set the element at the specified index."""
        if index < 0:
            index += self._size
        self.set(index, value)

    def __len__(self) -> int:
        """Get the length of the segment tree."""
        return self._size

    def __iter__(self) -> Iterator[T]:
        """Iterate over all elements in the segment tree."""
        for i in range(self._size):
            yield self.get(i)

    def __contains__(self, value: object) -> bool:
        """Check if a value exists in the segment tree."""
        return any(element == value for element in self)

    def __repr__(self) -> str:
        """Return a string representation of the segment tree."""
        elements = list(self)
        return f"GenericSegmentTree({elements!r})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        elements = list(self)
        return f"GenericSegmentTree({elements!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another sequence."""
        if not isinstance(other, Sequence):
            return NotImplemented

        if len(self) != len(other):
            return False

        return all(a == b for a, b in zip(self, other, strict=True))


# Register GenericSegmentTree as a Sequence
Sequence.register(GenericSegmentTree)
