"""Tests for SumSegmentTree specialized class."""

from __future__ import annotations

import pytest

from segee.exceptions import SegmentTreeInitializationError
from segee.segment_tree import SumSegmentTree


class TestSumSegmentTree:
    """Test SumSegmentTree functionality."""

    def test_initialization(self) -> None:
        """Test SumSegmentTree initialization."""
        tree = SumSegmentTree(5)
        assert tree.size == 5
        assert tree.all_prod() == 0
        assert tree.total() == 0

    def test_basic_operations(self) -> None:
        """Test basic set and get operations."""
        tree = SumSegmentTree(3)
        tree.set(0, 10)
        tree.set(1, 20)
        tree.set(2, 30)

        assert tree.get(0) == 10
        assert tree.get(1) == 20
        assert tree.get(2) == 30

    def test_sum_queries(self) -> None:
        """Test sum method alias for range queries."""
        tree = SumSegmentTree(5)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.sum(0, 2) == 3  # 1 + 2
        assert tree.sum(1, 4) == 9  # 2 + 3 + 4
        assert tree.sum() == 15  # All elements

    def test_prod_compatibility(self) -> None:
        """Test that prod method still works alongside sum."""
        tree = SumSegmentTree(3)
        tree.set(0, 5)
        tree.set(1, 10)
        tree.set(2, 15)

        assert tree.prod(0, 2) == 15
        assert tree.sum(0, 2) == 15  # Should be the same

    def test_float_values(self) -> None:
        """Test SumSegmentTree with float values."""
        tree = SumSegmentTree(3)
        tree.set(0, 1.5)
        tree.set(1, 2.5)
        tree.set(2, 3.5)

        assert tree.sum(0, 3) == 7.5
        assert tree.total() == 7.5

    def test_invalid_initialization(self) -> None:
        """Test SumSegmentTree with invalid size."""
        with pytest.raises(SegmentTreeInitializationError):
            SumSegmentTree(0)

        with pytest.raises(SegmentTreeInitializationError):
            SumSegmentTree(-5)

    def test_sequence_protocol(self) -> None:
        """Test sequence protocol implementation."""
        tree = SumSegmentTree(3)
        tree[0] = 10
        tree[1] = 20
        tree[2] = 30

        assert len(tree) == 3
        assert list(tree) == [10, 20, 30]
        assert tree[1] == 20
        assert 20 in tree

    def test_negative_indexing(self) -> None:
        """Test negative indexing support."""
        tree = SumSegmentTree(3)
        tree.set(-1, 100)  # Last element
        assert tree.get(-1) == 100
        assert tree.get(2) == 100

    def test_large_numbers(self) -> None:
        """Test SumSegmentTree with large numbers."""
        tree = SumSegmentTree(5)
        large_values = [1000000, 2000000, 3000000, 4000000, 5000000]

        for i, value in enumerate(large_values):
            tree.set(i, value)

        assert tree.sum(0, 3) == 6000000
        assert tree.total() == 15000000

    def test_zero_values(self) -> None:
        """Test SumSegmentTree with zero values."""
        tree = SumSegmentTree(5)
        # All elements start as 0 (identity)
        assert tree.total() == 0

        tree.set(2, 10)
        assert tree.total() == 10

        tree.set(2, 0)  # Reset to zero
        assert tree.total() == 0
