"""Tests for MinSegmentTree specialized class."""

from __future__ import annotations

import pytest

from segee.exceptions import SegmentTreeInitializationError
from segee.segment_tree import MinSegmentTree


class TestMinSegmentTree:
    """Test MinSegmentTree functionality."""

    def test_initialization(self) -> None:
        """Test MinSegmentTree initialization."""
        tree = MinSegmentTree(5)
        assert tree.size == 5
        assert tree.all_prod() == float("inf")
        assert tree.global_min() == float("inf")

    def test_basic_operations(self) -> None:
        """Test basic set and get operations."""
        tree = MinSegmentTree(3)
        tree.set(0, 10)
        tree.set(1, 5)
        tree.set(2, 15)

        assert tree.get(0) == 10
        assert tree.get(1) == 5
        assert tree.get(2) == 15

    def test_min_queries(self) -> None:
        """Test minimum method alias for range queries."""
        tree = MinSegmentTree(5)
        values = [10, 5, 20, 15, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.minimum(0, 2) == 5  # min(10, 5)
        assert tree.minimum(1, 4) == 5  # min(5, 20, 15)
        assert tree.minimum() == 5  # All elements

    def test_prod_compatibility(self) -> None:
        """Test that prod method still works alongside minimum."""
        tree = MinSegmentTree(3)
        tree.set(0, 15)
        tree.set(1, 10)
        tree.set(2, 25)

        assert tree.prod(0, 2) == 10
        assert tree.minimum(0, 2) == 10  # Should be the same

    def test_negative_values(self) -> None:
        """Test MinSegmentTree with negative values."""
        tree = MinSegmentTree(3)
        tree.set(0, -5)
        tree.set(1, -10)
        tree.set(2, -3)

        assert tree.minimum(0, 3) == -10
        assert tree.global_min() == -10

    def test_float_values(self) -> None:
        """Test MinSegmentTree with float values."""
        tree = MinSegmentTree(3)
        tree.set(0, 1.5)
        tree.set(1, 2.3)
        tree.set(2, 0.8)

        assert tree.minimum(0, 3) == 0.8
        assert tree.global_min() == 0.8

    def test_single_element(self) -> None:
        """Test MinSegmentTree with single element."""
        tree = MinSegmentTree(1)
        tree.set(0, 42)

        assert tree.minimum() == 42
        assert tree.global_min() == 42

    def test_invalid_initialization(self) -> None:
        """Test MinSegmentTree with invalid size."""
        with pytest.raises(SegmentTreeInitializationError):
            MinSegmentTree(0)

        with pytest.raises(SegmentTreeInitializationError):
            MinSegmentTree(-3)

    def test_sequence_protocol(self) -> None:
        """Test sequence protocol implementation."""
        tree = MinSegmentTree(3)
        tree[0] = 30
        tree[1] = 10
        tree[2] = 20

        assert len(tree) == 3
        assert list(tree) == [30, 10, 20]
        assert tree[1] == 10
        assert 10 in tree

    def test_max_right_functionality(self) -> None:
        """Test max_right with MinSegmentTree."""
        tree = MinSegmentTree(5)
        values = [10, 5, 20, 3, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find max right where min >= 5
        result = tree.max_right(0, lambda x: x >= 5)
        assert result == 3  # min([10, 5, 20]) = 5 >= 5

    def test_min_left_functionality(self) -> None:
        """Test min_left with MinSegmentTree."""
        tree = MinSegmentTree(5)
        values = [10, 5, 20, 3, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left where min <= 5
        result = tree.min_left(5, lambda x: x <= 5)
        assert result == 0  # min([10, 5, 20, 3, 8]) = 3 <= 5

    def test_empty_range_handling(self) -> None:
        """Test handling of empty ranges."""
        tree = MinSegmentTree(5)
        # Empty range should return identity (inf)
        assert tree.minimum(2, 2) == float("inf")
        assert tree.prod(3, 3) == float("inf")

    def test_mixed_positive_negative_zero(self) -> None:
        """Test with mix of positive, negative, and zero values."""
        tree = MinSegmentTree(5)
        values = [5, -3, 0, 10, -7]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.minimum(0, 3) == -3
        assert tree.minimum(2, 5) == -7
        assert tree.global_min() == -7
