"""Tests for MaxSegmentTree specialized class."""

from __future__ import annotations

import pytest

from segee.exceptions import SegmentTreeInitializationError
from segee.segment_tree import MaxSegmentTree


class TestMaxSegmentTree:
    """Test MaxSegmentTree functionality."""

    def test_initialization(self) -> None:
        """Test MaxSegmentTree initialization."""
        tree = MaxSegmentTree(5)
        assert tree.size == 5
        assert tree.all_prod() == float("-inf")
        assert tree.global_max() == float("-inf")

    def test_basic_operations(self) -> None:
        """Test basic set and get operations."""
        tree = MaxSegmentTree(3)
        tree.set(0, 10)
        tree.set(1, 25)
        tree.set(2, 15)

        assert tree.get(0) == 10
        assert tree.get(1) == 25
        assert tree.get(2) == 15

    def test_max_queries(self) -> None:
        """Test maximum method alias for range queries."""
        tree = MaxSegmentTree(5)
        values = [10, 5, 20, 15, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.maximum(0, 2) == 10  # max(10, 5)
        assert tree.maximum(1, 4) == 20  # max(5, 20, 15)
        assert tree.maximum() == 20  # All elements

    def test_prod_compatibility(self) -> None:
        """Test that prod method still works alongside maximum."""
        tree = MaxSegmentTree(3)
        tree.set(0, 5)
        tree.set(1, 15)
        tree.set(2, 10)

        assert tree.prod(0, 2) == 15
        assert tree.maximum(0, 2) == 15  # Should be the same

    def test_negative_values(self) -> None:
        """Test MaxSegmentTree with negative values."""
        tree = MaxSegmentTree(3)
        tree.set(0, -5)
        tree.set(1, -10)
        tree.set(2, -3)

        assert tree.maximum(0, 3) == -3
        assert tree.global_max() == -3

    def test_float_values(self) -> None:
        """Test MaxSegmentTree with float values."""
        tree = MaxSegmentTree(3)
        tree.set(0, 1.5)
        tree.set(1, 2.8)
        tree.set(2, 0.9)

        assert tree.maximum(0, 3) == 2.8
        assert tree.global_max() == 2.8

    def test_single_element(self) -> None:
        """Test MaxSegmentTree with single element."""
        tree = MaxSegmentTree(1)
        tree.set(0, 42)

        assert tree.maximum() == 42
        assert tree.global_max() == 42

    def test_invalid_initialization(self) -> None:
        """Test MaxSegmentTree with invalid size."""
        with pytest.raises(SegmentTreeInitializationError):
            MaxSegmentTree(0)

        with pytest.raises(SegmentTreeInitializationError):
            MaxSegmentTree(-3)

    def test_sequence_protocol(self) -> None:
        """Test sequence protocol implementation."""
        tree = MaxSegmentTree(3)
        tree[0] = 30
        tree[1] = 50
        tree[2] = 20

        assert len(tree) == 3
        assert list(tree) == [30, 50, 20]
        assert tree[1] == 50
        assert 50 in tree

    def test_max_right_functionality(self) -> None:
        """Test max_right with MaxSegmentTree."""
        tree = MaxSegmentTree(5)
        values = [1, 5, 3, 10, 2]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find max right where max <= 5
        result = tree.max_right(0, lambda x: x <= 5)
        assert result == 3  # max([1, 5, 3]) = 5 <= 5

    def test_min_left_functionality(self) -> None:
        """Test min_left with MaxSegmentTree."""
        tree = MaxSegmentTree(5)
        values = [1, 5, 3, 10, 2]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left where max >= 5
        result = tree.min_left(5, lambda x: x >= 5)
        assert result == 0  # max([1, 5, 3, 10, 2]) = 10 >= 5

    def test_empty_range_handling(self) -> None:
        """Test handling of empty ranges."""
        tree = MaxSegmentTree(5)
        # Empty range should return identity (-inf)
        assert tree.maximum(2, 2) == float("-inf")
        assert tree.prod(3, 3) == float("-inf")

    def test_mixed_positive_negative_zero(self) -> None:
        """Test with mix of positive, negative, and zero values."""
        tree = MaxSegmentTree(5)
        values = [-5, 3, 0, -10, 7]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.maximum(0, 3) == 3
        assert tree.maximum(2, 5) == 7
        assert tree.global_max() == 7

    def test_identical_values(self) -> None:
        """Test with all identical values."""
        tree = MaxSegmentTree(4)
        for i in range(4):
            tree.set(i, 42)

        assert tree.maximum(0, 2) == 42
        assert tree.maximum(1, 4) == 42
        assert tree.global_max() == 42

    def test_ascending_sequence(self) -> None:
        """Test with ascending sequence of values."""
        tree = MaxSegmentTree(5)
        for i in range(5):
            tree.set(i, i + 1)  # [1, 2, 3, 4, 5]

        assert tree.maximum(0, 3) == 3
        assert tree.maximum(2, 5) == 5
        assert tree.global_max() == 5

    def test_descending_sequence(self) -> None:
        """Test with descending sequence of values."""
        tree = MaxSegmentTree(5)
        for i in range(5):
            tree.set(i, 5 - i)  # [5, 4, 3, 2, 1]

        assert tree.maximum(0, 3) == 5
        assert tree.maximum(2, 5) == 3
        assert tree.global_max() == 5
