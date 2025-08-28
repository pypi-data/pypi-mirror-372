"""Tests for RangeAddBinaryIndexedTree functionality."""

from __future__ import annotations

import pytest

from segee.binary_indexed_tree import (
    BinaryIndexedTreeError,
    RangeAddBinaryIndexedTree,
)
from segee.exceptions import SegmentTreeIndexError, SegmentTreeRangeError


class TestRangeAddBinaryIndexedTreeInitialization:
    """Test RangeAddBinaryIndexedTree initialization."""

    def test_initialization_with_size(self) -> None:
        """Test initialization with integer size."""
        bit = RangeAddBinaryIndexedTree(5)
        assert len(bit) == 5
        assert list(bit) == [0, 0, 0, 0, 0]

    def test_initialization_with_sequence(self) -> None:
        """Test initialization with sequence."""
        data = [1, 2, 3, 4, 5]
        bit = RangeAddBinaryIndexedTree(data)
        assert len(bit) == 5
        assert list(bit) == data

    def test_initialization_with_mixed_types(self) -> None:
        """Test initialization with mixed int/float sequence."""
        data = [1, 2.5, 3, 4.0, 5]
        bit = RangeAddBinaryIndexedTree(data)
        assert len(bit) == 5
        assert list(bit) == data

    def test_initialization_empty_sequence(self) -> None:
        """Test initialization with empty sequence."""
        bit = RangeAddBinaryIndexedTree([])
        assert len(bit) == 0
        assert list(bit) == []

    def test_initialization_zero_size(self) -> None:
        """Test initialization with zero size."""
        bit = RangeAddBinaryIndexedTree(0)
        assert len(bit) == 0
        assert list(bit) == []

    def test_invalid_size_negative(self) -> None:
        """Test initialization with negative size raises error."""
        with pytest.raises(BinaryIndexedTreeError, match="Size must be non-negative"):
            RangeAddBinaryIndexedTree(-1)

    def test_invalid_data_type(self) -> None:
        """Test initialization with invalid data type raises error."""
        with pytest.raises(BinaryIndexedTreeError, match="Expected int or Sequence"):
            RangeAddBinaryIndexedTree("invalid")  # type: ignore[arg-type]


class TestRangeAddBinaryIndexedTreeSequenceProtocol:
    """Test sequence protocol implementation."""

    def test_len(self) -> None:
        """Test __len__ method."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert len(bit) == 5

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit[0] == 1
        assert bit[2] == 3
        assert bit[4] == 5

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit[2] = 10
        assert bit[2] == 10
        assert list(bit) == [1, 2, 10, 4, 5]

    def test_contains(self) -> None:
        """Test __contains__ method."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert 3 in bit
        assert 6 not in bit
        assert 0 not in bit

    def test_iter(self) -> None:
        """Test __iter__ method."""
        data = [1, 2, 3, 4, 5]
        bit = RangeAddBinaryIndexedTree(data)
        result = list(bit)
        assert result == data

    def test_repr(self) -> None:
        """Test __repr__ method."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        assert repr(bit) == "RangeAddBinaryIndexedTree([1, 2, 3])"

    def test_getitem_invalid_index(self) -> None:
        """Test __getitem__ with invalid index."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeIndexError):
            _ = bit[3]
        with pytest.raises(SegmentTreeIndexError):
            _ = bit[-4]

    def test_setitem_invalid_index(self) -> None:
        """Test __setitem__ with invalid index."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeIndexError):
            bit[3] = 10
        with pytest.raises(SegmentTreeIndexError):
            bit[-4] = 10


class TestRangeAddBinaryIndexedTreePointOperations:
    """Test point update operations."""

    def test_add_single_element(self) -> None:
        """Test adding to a single element."""
        bit = RangeAddBinaryIndexedTree(5)
        bit.add(2, None, value=3)
        assert bit[2] == 3
        assert bit[0] == 0
        assert bit[1] == 0

    def test_add_multiple_elements(self) -> None:
        """Test adding to multiple elements."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(0, None, value=10)
        bit.add(2, None, value=20)
        assert bit[0] == 11
        assert bit[2] == 23
        assert bit[1] == 2
        assert bit[3] == 4

    def test_add_negative_values(self) -> None:
        """Test adding negative values."""
        bit = RangeAddBinaryIndexedTree([10, 20, 30])
        bit.add(1, None, value=-5)
        assert bit[1] == 15

    def test_add_invalid_index(self) -> None:
        """Test adding with invalid index."""
        bit = RangeAddBinaryIndexedTree(3)
        with pytest.raises(SegmentTreeIndexError):
            bit.add(3, None, value=10)
        with pytest.raises(SegmentTreeIndexError):
            bit.add(-4, None, value=10)


class TestRangeAddBinaryIndexedTreeRangeOperations:
    """Test range update operations."""

    def test_range_add_basic(self) -> None:
        """Test basic range add functionality."""
        bit = RangeAddBinaryIndexedTree(5)
        bit.add(1, 4, value=3)  # Add 3 to indices [1, 2, 3]
        expected = [0, 3, 3, 3, 0]
        assert list(bit) == expected

    def test_range_add_full_array(self) -> None:
        """Test range add on full array."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(0, 5, value=10)  # Add 10 to all elements
        expected = [11, 12, 13, 14, 15]
        assert list(bit) == expected

    def test_range_add_single_element(self) -> None:
        """Test range add on single element."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        bit.add(1, 2, value=5)  # Add 5 to index 1 only
        expected = [1, 7, 3]
        assert list(bit) == expected

    def test_range_add_empty_range(self) -> None:
        """Test range add on empty range."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        original = list(bit)
        bit.add(1, 1, value=10)  # Empty range
        assert list(bit) == original

    def test_range_add_overlapping_ranges(self) -> None:
        """Test overlapping range additions."""
        bit = RangeAddBinaryIndexedTree(5)
        bit.add(0, 3, value=5)  # [5, 5, 5, 0, 0]
        bit.add(2, 5, value=3)  # [5, 5, 8, 3, 3]
        expected = [5, 5, 8, 3, 3]
        assert list(bit) == expected

    def test_range_add_negative_values(self) -> None:
        """Test range add with negative values."""
        bit = RangeAddBinaryIndexedTree([10, 20, 30])
        bit.add(0, 3, value=-5)
        expected = [5, 15, 25]
        assert list(bit) == expected

    def test_range_add_invalid_range(self) -> None:
        """Test range add with invalid range."""
        bit = RangeAddBinaryIndexedTree(3)
        with pytest.raises(SegmentTreeRangeError):
            bit.add(0, 4, value=10)  # right > size
        with pytest.raises(SegmentTreeRangeError):
            bit.add(-1, 2, value=10)  # left < 0
        with pytest.raises(SegmentTreeRangeError):
            bit.add(2, 1, value=10)  # left > right


class TestRangeAddBinaryIndexedTreePrefixSum:
    """Test prefix sum queries."""

    def test_prefix_sum_basic(self) -> None:
        """Test basic prefix sum functionality."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.prefix_sum(0) == 0
        assert bit.prefix_sum(1) == 1
        assert bit.prefix_sum(3) == 6  # 1 + 2 + 3
        assert bit.prefix_sum(5) == 15  # 1 + 2 + 3 + 4 + 5

    def test_prefix_sum_after_point_updates(self) -> None:
        """Test prefix sum after point updates."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, None, value=10)  # [1, 12, 3, 4, 5]
        assert bit.prefix_sum(2) == 13  # 1 + 12
        assert bit.prefix_sum(3) == 16  # 1 + 12 + 3

    def test_prefix_sum_after_range_updates(self) -> None:
        """Test prefix sum after range updates."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, 4, value=10)  # [1, 12, 13, 14, 5]
        assert bit.prefix_sum(1) == 1
        assert bit.prefix_sum(3) == 26  # 1 + 12 + 13
        assert bit.prefix_sum(5) == 45  # 1 + 12 + 13 + 14 + 5

    def test_prefix_sum_empty_range(self) -> None:
        """Test prefix sum with empty range."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        assert bit.prefix_sum(0) == 0

    def test_prefix_sum_invalid_range(self) -> None:
        """Test prefix sum with invalid range."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeRangeError):
            bit.prefix_sum(4)
        with pytest.raises(SegmentTreeRangeError):
            bit.prefix_sum(-1)


class TestRangeAddBinaryIndexedTreeRangeSum:
    """Test range sum queries."""

    def test_range_sum_basic(self) -> None:
        """Test basic range sum functionality."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(0, 3) == 6  # 1 + 2 + 3
        assert bit.sum(1, 4) == 9  # 2 + 3 + 4
        assert bit.sum(2, 5) == 12  # 3 + 4 + 5

    def test_range_sum_after_point_updates(self) -> None:
        """Test range sum after point updates."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, None, value=10)  # [1, 12, 3, 4, 5]
        assert bit.sum(0, 3) == 16  # 1 + 12 + 3
        assert bit.sum(1, 4) == 19  # 12 + 3 + 4

    def test_range_sum_after_range_updates(self) -> None:
        """Test range sum after range updates."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, 4, value=10)  # [1, 12, 13, 14, 5]
        assert bit.sum(0, 3) == 26  # 1 + 12 + 13
        assert bit.sum(1, 4) == 39  # 12 + 13 + 14

    def test_range_sum_single_element(self) -> None:
        """Test range sum with single element."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(2, 3, value=10)  # Add 10 to index 2
        assert bit.sum(2, 3) == 13  # 3 + 10

    def test_range_sum_empty_range(self) -> None:
        """Test range sum with empty range."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(2, 2) == 0

    def test_range_sum_full_array(self) -> None:
        """Test range sum for full array."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(0, 5, value=1)  # Add 1 to all elements
        assert bit.sum(0, 5) == 20  # (1+2+3+4+5) + 5*1

    def test_range_sum_with_none_end(self) -> None:
        """Test range sum with None as right boundary."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(2, 5, value=10)  # [1, 2, 13, 14, 15]
        assert bit.sum(2) == 42  # 13 + 14 + 15
        assert bit.sum(0) == 45  # 1 + 2 + 13 + 14 + 15

    def test_range_sum_invalid_range(self) -> None:
        """Test range sum with invalid range."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(0, 4)
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(-1, 2)
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(2, 1)  # left > right


class TestRangeAddBinaryIndexedTreeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_element_tree(self) -> None:
        """Test tree with single element."""
        bit = RangeAddBinaryIndexedTree([42])
        assert len(bit) == 1
        assert bit[0] == 42

        bit.add(0, 1, value=10)
        assert bit[0] == 52
        assert bit.prefix_sum(1) == 52
        assert bit.sum(0, 1) == 52

    def test_mixed_point_and_range_updates(self) -> None:
        """Test mixing point and range updates."""
        bit = RangeAddBinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(0, None, value=10)  # [11, 2, 3, 4, 5]
        bit.add(1, 4, value=5)  # [11, 7, 8, 9, 5]
        bit.add(2, None, value=-3)  # [11, 7, 5, 9, 5]

        expected = [11, 7, 5, 9, 5]
        assert list(bit) == expected
        assert bit.sum(0, 5) == 37

    def test_large_numbers(self) -> None:
        """Test with large numbers."""
        bit = RangeAddBinaryIndexedTree([1_000_000, 2_000_000, 3_000_000])
        bit.add(0, 3, value=1_000_000)
        assert bit.sum(0, 3) == 9_000_000

    def test_floating_point_numbers(self) -> None:
        """Test with floating point numbers."""
        bit = RangeAddBinaryIndexedTree([1.5, 2.5, 3.5])
        bit.add(0, 3, value=0.5)
        assert bit.sum(0, 3) == pytest.approx(9.0)
        assert bit[1] == pytest.approx(3.0)

    def test_zero_values(self) -> None:
        """Test with zero values."""
        bit = RangeAddBinaryIndexedTree([0, 0, 0, 0])
        assert bit.sum(0, 4) == 0
        bit.add(1, 3, value=5)
        assert bit.sum(0, 4) == 10  # 0 + 5 + 5 + 0

    def test_to_list_method(self) -> None:
        """Test to_list method."""
        data = [1, 2, 3, 4, 5]
        bit = RangeAddBinaryIndexedTree(data)
        assert bit.to_list() == data

        bit.add(1, 4, value=10)
        expected = [1, 12, 13, 14, 5]
        assert bit.to_list() == expected
