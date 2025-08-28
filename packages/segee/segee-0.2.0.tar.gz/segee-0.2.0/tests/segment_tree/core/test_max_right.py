"""Tests for SegmentTree max_right functionality."""

from __future__ import annotations

import operator

import pytest

from segee.exceptions import SegmentTreeIndexError
from segee.segment_tree import GenericSegmentTree


class TestSegmentTreeMaxRight:
    """Test max_right functionality."""

    def test_max_right_sum_predicate(self) -> None:
        """Test max_right with sum predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find max right where sum <= 6
        result = tree.max_right(0, lambda x: x <= 6)
        assert result == 3  # Sum of [1, 2, 3] = 6

    def test_max_right_at_boundary(self) -> None:
        """Test max_right at tree boundary."""
        tree = GenericSegmentTree(5, 0, operator.add)
        result = tree.max_right(5, lambda _: True)
        assert result == 5

    def test_max_right_invalid_index(self) -> None:
        """Test max_right with invalid starting index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeIndexError):
            tree.max_right(6, lambda _: True)

    def test_max_right_no_valid_range(self) -> None:
        """Test max_right when no range satisfies predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [10, 20, 30, 40, 50]

        for i, value in enumerate(values):
            tree.set(i, value)

        # No range starting from 0 has sum <= 5
        result = tree.max_right(0, lambda x: x <= 5)
        assert result == 0

    def test_max_right_all_satisfy_predicate(self) -> None:
        """Test max_right when all ranges satisfy predicate."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 1, 1, 1, 1]

        for i, value in enumerate(values):
            tree.set(i, value)

        # All ranges starting from 0 have sum <= 10
        result = tree.max_right(0, lambda x: x <= 10)
        assert result == 5

    def test_max_right_max_operation(self) -> None:
        """Test max_right with max operation."""
        tree = GenericSegmentTree(5, float("-inf"), max)
        values = [5, 10, 3, 8, 15]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find max right where max <= 10
        result = tree.max_right(0, lambda x: x <= 10)
        assert result == 4  # max([5, 10, 3, 8]) = 10 <= 10

    def test_max_right_from_middle(self) -> None:
        """Test max_right starting from middle of array."""
        tree = GenericSegmentTree(6, 0, operator.add)
        values = [1, 2, 3, 4, 5, 6]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Find max right starting from index 2 where sum <= 12
        result = tree.max_right(2, lambda x: x <= 12)
        assert result == 5  # Sum of [3, 4, 5] = 12

    def test_max_right_single_element(self) -> None:
        """Test max_right on single element tree."""
        tree = GenericSegmentTree(1, 0, operator.add)
        tree.set(0, 42)

        result = tree.max_right(0, lambda x: x <= 50)
        assert result == 1

        result = tree.max_right(0, lambda x: x <= 30)
        assert result == 0
