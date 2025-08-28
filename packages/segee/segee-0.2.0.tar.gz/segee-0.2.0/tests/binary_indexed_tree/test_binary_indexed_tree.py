"""Tests for BinaryIndexedTree basic functionality."""

from __future__ import annotations

import pytest

from segee.binary_indexed_tree import BinaryIndexedTree, BinaryIndexedTreeError
from segee.exceptions import SegmentTreeIndexError, SegmentTreeRangeError


class TestBinaryIndexedTreeInitialization:
    """Test BinaryIndexedTree initialization and validation."""

    def test_initialization_with_size(self) -> None:
        """Test initialization with integer size."""
        bit = BinaryIndexedTree(5)
        assert len(bit) == 5
        assert list(bit) == [0, 0, 0, 0, 0]

    def test_initialization_with_sequence(self) -> None:
        """Test initialization with sequence."""
        data = [1, 2, 3, 4, 5]
        bit = BinaryIndexedTree(data)
        assert len(bit) == 5
        assert list(bit) == data

    def test_initialization_with_mixed_types(self) -> None:
        """Test initialization with mixed int/float sequence."""
        data = [1, 2.5, 3, 4.0, 5]
        bit = BinaryIndexedTree(data)
        assert len(bit) == 5
        assert list(bit) == data

    def test_initialization_empty_sequence(self) -> None:
        """Test initialization with empty sequence."""
        bit = BinaryIndexedTree([])
        assert len(bit) == 0
        assert list(bit) == []

    def test_initialization_zero_size(self) -> None:
        """Test initialization with zero size."""
        bit = BinaryIndexedTree(0)
        assert len(bit) == 0
        assert list(bit) == []

    def test_invalid_size_negative(self) -> None:
        """Test initialization with negative size raises error."""
        with pytest.raises(BinaryIndexedTreeError, match="Size must be non-negative"):
            BinaryIndexedTree(-1)

    def test_invalid_data_type(self) -> None:
        """Test initialization with invalid data type raises error."""
        with pytest.raises(BinaryIndexedTreeError, match="Expected int or Sequence"):
            BinaryIndexedTree("invalid")  # type: ignore[arg-type]


class TestBinaryIndexedTreeSequenceProtocol:
    """Test sequence protocol implementation."""

    def test_len(self) -> None:
        """Test __len__ method."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert len(bit) == 5

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit[0] == 1
        assert bit[2] == 3
        assert bit[4] == 5

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        bit[2] = 10
        assert bit[2] == 10
        assert list(bit) == [1, 2, 10, 4, 5]

    def test_contains(self) -> None:
        """Test __contains__ method."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert 3 in bit
        assert 6 not in bit
        assert 0 not in bit

    def test_iter(self) -> None:
        """Test __iter__ method."""
        data = [1, 2, 3, 4, 5]
        bit = BinaryIndexedTree(data)
        result = list(bit)
        assert result == data

    def test_repr(self) -> None:
        """Test __repr__ method."""
        bit = BinaryIndexedTree([1, 2, 3])
        assert repr(bit) == "BinaryIndexedTree([1, 2, 3])"

    def test_getitem_invalid_index(self) -> None:
        """Test __getitem__ with invalid index."""
        bit = BinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeIndexError):
            _ = bit[3]
        with pytest.raises(SegmentTreeIndexError):
            _ = bit[-4]

    def test_setitem_invalid_index(self) -> None:
        """Test __setitem__ with invalid index."""
        bit = BinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeIndexError):
            bit[3] = 10
        with pytest.raises(SegmentTreeIndexError):
            bit[-4] = 10


class TestBinaryIndexedTreeOperations:
    """Test BIT operations."""

    def test_add_single_element(self) -> None:
        """Test adding to a single element."""
        bit = BinaryIndexedTree(5)
        bit.add(2, 3)
        assert bit[2] == 3
        assert bit[0] == 0
        assert bit[1] == 0

    def test_add_multiple_elements(self) -> None:
        """Test adding to multiple elements."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(0, 10)
        bit.add(2, 20)
        assert bit[0] == 11
        assert bit[2] == 23
        assert bit[1] == 2
        assert bit[3] == 4

    def test_add_negative_values(self) -> None:
        """Test adding negative values."""
        bit = BinaryIndexedTree([10, 20, 30])
        bit.add(1, -5)
        assert bit[1] == 15

    def test_add_invalid_index(self) -> None:
        """Test adding with invalid index."""
        bit = BinaryIndexedTree(3)
        with pytest.raises(SegmentTreeIndexError):
            bit.add(3, 10)
        with pytest.raises(SegmentTreeIndexError):
            bit.add(-4, 10)


class TestBinaryIndexedTreePrefixSum:
    """Test prefix sum queries."""

    def test_prefix_sum_basic(self) -> None:
        """Test basic prefix sum functionality."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.prefix_sum(0) == 0
        assert bit.prefix_sum(1) == 1
        assert bit.prefix_sum(3) == 6  # 1 + 2 + 3
        assert bit.prefix_sum(5) == 15  # 1 + 2 + 3 + 4 + 5

    def test_prefix_sum_after_updates(self) -> None:
        """Test prefix sum after adding elements."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, 10)  # [1, 12, 3, 4, 5]
        assert bit.prefix_sum(2) == 13  # 1 + 12
        assert bit.prefix_sum(3) == 16  # 1 + 12 + 3

    def test_prefix_sum_empty_range(self) -> None:
        """Test prefix sum with empty range."""
        bit = BinaryIndexedTree([1, 2, 3])
        assert bit.prefix_sum(0) == 0

    def test_prefix_sum_invalid_range(self) -> None:
        """Test prefix sum with invalid range."""
        bit = BinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeRangeError):
            bit.prefix_sum(4)
        with pytest.raises(SegmentTreeRangeError):
            bit.prefix_sum(-1)


class TestBinaryIndexedTreeRangeSum:
    """Test range sum queries."""

    def test_range_sum_basic(self) -> None:
        """Test basic range sum functionality."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(0, 3) == 6  # 1 + 2 + 3
        assert bit.sum(1, 4) == 9  # 2 + 3 + 4
        assert bit.sum(2, 5) == 12  # 3 + 4 + 5

    def test_range_sum_single_element(self) -> None:
        """Test range sum with single element."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(2, 3) == 3

    def test_range_sum_empty_range(self) -> None:
        """Test range sum with empty range."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(2, 2) == 0

    def test_range_sum_full_array(self) -> None:
        """Test range sum for full array."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(0, 5) == 15

    def test_range_sum_with_none_end(self) -> None:
        """Test range sum with None as right boundary."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        assert bit.sum(2) == 12  # 3 + 4 + 5
        assert bit.sum(0) == 15  # 1 + 2 + 3 + 4 + 5

    def test_range_sum_after_updates(self) -> None:
        """Test range sum after adding elements."""
        bit = BinaryIndexedTree([1, 2, 3, 4, 5])
        bit.add(1, 10)  # [1, 12, 3, 4, 5]
        assert bit.sum(0, 3) == 16  # 1 + 12 + 3
        assert bit.sum(1, 4) == 19  # 12 + 3 + 4

    def test_range_sum_invalid_range(self) -> None:
        """Test range sum with invalid range."""
        bit = BinaryIndexedTree([1, 2, 3])
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(0, 4)
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(-1, 2)
        with pytest.raises(SegmentTreeRangeError):
            bit.sum(2, 1)  # left > right


class TestBinaryIndexedTreeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_single_element_tree(self) -> None:
        """Test tree with single element."""
        bit = BinaryIndexedTree([42])
        assert len(bit) == 1
        assert bit[0] == 42
        assert bit.prefix_sum(1) == 42
        assert bit.sum(0, 1) == 42

    def test_large_numbers(self) -> None:
        """Test with large numbers."""
        bit = BinaryIndexedTree([1_000_000, 2_000_000, 3_000_000])
        assert bit.sum(0, 3) == 6_000_000
        bit.add(1, 1_000_000)
        assert bit.sum(0, 3) == 7_000_000

    def test_floating_point_numbers(self) -> None:
        """Test with floating point numbers."""
        bit = BinaryIndexedTree([1.5, 2.5, 3.5])
        assert bit.sum(0, 3) == pytest.approx(7.5)
        bit.add(1, 0.5)
        assert bit[1] == pytest.approx(3.0)

    def test_zero_values(self) -> None:
        """Test with zero values."""
        bit = BinaryIndexedTree([0, 0, 0, 0])
        assert bit.sum(0, 4) == 0
        bit.add(2, 5)
        assert bit.sum(0, 4) == 5

    def test_to_list_method(self) -> None:
        """Test to_list method."""
        data = [1, 2, 3, 4, 5]
        bit = BinaryIndexedTree(data)
        assert bit.to_list() == data

        bit.add(2, 10)
        expected = [1, 2, 13, 4, 5]
        assert bit.to_list() == expected
