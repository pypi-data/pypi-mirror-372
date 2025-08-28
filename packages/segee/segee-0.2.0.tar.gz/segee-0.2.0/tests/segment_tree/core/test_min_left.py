"""Tests for SegmentTree min_left functionality."""

from __future__ import annotations

import operator

import pytest

from segee.exceptions import SegmentTreeIndexError
from segee.segment_tree import GenericSegmentTree


class TestSegmentTreeMinLeft:
    """Test min_left functionality."""

    def test_min_left_sum_predicate(self) -> None:
        """Test min_left with sum predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left where sum <= 9 (from right=5)
        result = tree.min_left(5, lambda x: x <= 9)
        assert result == 3  # Sum of [4, 5] = 9 <= 9

    def test_min_left_at_boundary(self) -> None:
        """Test min_left at tree boundary."""
        tree = GenericSegmentTree(5, 0, operator.add)
        result = tree.min_left(0, lambda _: True)
        assert result == 0

    def test_min_left_invalid_index(self) -> None:
        """Test min_left with invalid ending index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeIndexError):
            tree.min_left(-1, lambda _: True)

    def test_min_left_max_predicate(self) -> None:
        """Test min_left with max predicate."""
        tree = GenericSegmentTree(5, float("-inf"), max)
        values = [10, 5, 20, 15, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left where max >= 15 (from right=5)
        result = tree.min_left(5, lambda x: x >= 15)
        assert result == 0  # max([10, 5, 20, 15, 8]) = 20 >= 15

        # Find min left where max >= 21 (from right=5) - no such range
        result2 = tree.min_left(5, lambda x: x >= 21)
        assert result2 == 5  # No range satisfies the condition

    def test_min_left_no_valid_range(self) -> None:
        """Test min_left when no range satisfies predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        # No range ending at 3 has sum >= 50
        result = tree.min_left(3, lambda x: x >= 50)
        assert result == 3

    def test_min_left_all_satisfy_predicate(self) -> None:
        """Test min_left when all ranges satisfy predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 1, 1, 1, 1]

        for i, value in enumerate(values):
            tree.set(i, value)

        # All ranges ending at 4 have sum >= 1
        result = tree.min_left(4, lambda x: x >= 1)
        assert result == 0

    def test_min_left_min_operation(self) -> None:
        """Test min_left with min operation."""
        tree = GenericSegmentTree(5, float("inf"), min)
        values = [10, 5, 15, 3, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left where min <= 5 (from right=5)
        result = tree.min_left(5, lambda x: x <= 5)
        assert result == 0  # min([10, 5, 15, 3, 8]) = 3 <= 5

    def test_min_left_from_middle(self) -> None:
        """Test min_left ending at middle of array."""
        tree = GenericSegmentTree(6, 0, operator.add)
        values = [10, 5, 3, 2, 1, 4]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find min left ending at index 3 where sum <= 10
        result = tree.min_left(3, lambda x: x <= 10)
        assert result == 1  # Sum of [5, 3, 2] = 10 <= 10

    def test_min_left_single_element(self) -> None:
        """Test min_left on single element tree."""
        tree = GenericSegmentTree(1, 0, operator.add)
        tree.set(0, 42)

        result = tree.min_left(1, lambda x: x <= 50)
        assert result == 0

        result = tree.min_left(1, lambda x: x <= 30)
        assert result == 1

    def test_min_left_empty_range(self) -> None:
        """Test min_left with empty range (right=0)."""
        tree = GenericSegmentTree(5, 0, operator.add)
        result = tree.min_left(0, lambda _: True)
        assert result == 0
