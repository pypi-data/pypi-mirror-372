"""Core tests for basic SegmentTree functionality."""

from __future__ import annotations

import math
import operator

import pytest

from segee.exceptions import (
    SegmentTreeIndexError,
    SegmentTreeInitializationError,
    SegmentTreeRangeError,
)
from segee.segment_tree import GenericSegmentTree


class TestSegmentTreeInitialization:
    """Test SegmentTree initialization and validation."""

    def test_valid_initialization(self) -> None:
        """Test valid initialization parameters."""
        tree = GenericSegmentTree(5, 0, operator.add)
        assert tree.size == 5

    def test_initialization_with_custom_identity_and_operation(self) -> None:
        """Test initialization with custom identity and operation."""
        tree = GenericSegmentTree(10, float("inf"), min)
        assert tree.size == 10
        assert tree.all_prod() == float("inf")

    def test_invalid_size_zero(self) -> None:
        """Test initialization with zero size raises error."""
        with pytest.raises(SegmentTreeInitializationError, match="Size must be positive"):
            GenericSegmentTree(0, 0, operator.add)

    def test_invalid_size_negative(self) -> None:
        """Test initialization with negative size raises error."""
        with pytest.raises(SegmentTreeInitializationError, match="Size must be positive"):
            GenericSegmentTree(-5, 0, operator.add)

    def test_invalid_operation_not_callable(self) -> None:
        """Test initialization with non-callable operation raises error."""
        with pytest.raises(SegmentTreeInitializationError, match="Operation must be callable"):
            GenericSegmentTree(5, 0, "not_callable")  # type: ignore[arg-type]


class TestSegmentTreeBasicOperations:
    """Test basic SegmentTree operations."""

    def test_set_and_get_single_element(self) -> None:
        """Test setting and getting a single element."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(0, 42)
        assert tree.get(0) == 42

    def test_set_and_get_multiple_elements(self) -> None:
        """Test setting and getting multiple elements."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [10, 20, 30, 40, 50]

        for i, value in enumerate(values):
            tree.set(i, value)

        for i, expected in enumerate(values):
            assert tree.get(i) == expected

    def test_get_invalid_index_positive(self) -> None:
        """Test getting element at invalid positive index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeIndexError):
            tree.get(5)

    def test_get_invalid_index_negative(self) -> None:
        """Test getting element at invalid negative index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeIndexError):
            tree.get(-6)

    def test_set_invalid_index(self) -> None:
        """Test setting element at invalid index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeIndexError):
            tree.set(5, 42)

    def test_negative_indexing(self) -> None:
        """Test negative indexing works correctly."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(-1, 99)  # Last element
        assert tree.get(-1) == 99
        assert tree.get(4) == 99


class TestSegmentTreeRangeQueries:
    """Test range query operations."""

    def test_prod_sum_operation(self) -> None:
        """Test range product with sum operation."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        # Test various ranges
        assert tree.prod(0, 2) == 3  # 1 + 2
        assert tree.prod(1, 4) == 9  # 2 + 3 + 4
        assert tree.prod(0, 5) == 15  # 1 + 2 + 3 + 4 + 5

    def test_prod_max_operation(self) -> None:
        """Test range product with max operation."""
        tree = GenericSegmentTree(5, float("-inf"), max)
        values = [10, 5, 20, 15, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.prod(0, 2) == 10
        assert tree.prod(1, 4) == 20
        assert tree.prod(0, 5) == 20

    def test_prod_empty_range(self) -> None:
        """Test range product with empty range returns identity."""
        tree = GenericSegmentTree(5, 0, operator.add)
        assert tree.prod(2, 2) == 0

    def test_prod_single_element_range(self) -> None:
        """Test range product with single element."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(2, 42)
        assert tree.prod(2, 3) == 42

    def test_prod_default_parameters(self) -> None:
        """Test range product with default parameters covers entire range."""
        tree = GenericSegmentTree(3, 0, operator.add)
        tree.set(0, 1)
        tree.set(1, 2)
        tree.set(2, 3)
        assert tree.prod() == 6

    def test_prod_invalid_range_left_negative(self) -> None:
        """Test range product with invalid negative left bound."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeRangeError):
            tree.prod(-1, 3)

    def test_prod_invalid_range_right_too_large(self) -> None:
        """Test range product with invalid right bound."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeRangeError):
            tree.prod(0, 6)

    def test_prod_invalid_range_left_greater_than_right(self) -> None:
        """Test range product with left > right."""
        tree = GenericSegmentTree(5, 0, operator.add)
        with pytest.raises(SegmentTreeRangeError):
            tree.prod(3, 1)

    def test_all_prod_empty_tree(self) -> None:
        """Test all_prod on tree with no elements set returns identity."""
        tree = GenericSegmentTree(5, 42, operator.add)
        assert tree.all_prod() == 42

    def test_all_prod_with_elements(self) -> None:
        """Test all_prod with elements set."""
        tree = GenericSegmentTree(3, 1, operator.mul)
        tree.set(0, 2)
        tree.set(1, 3)
        tree.set(2, 4)
        assert tree.all_prod() == 24


class TestSequenceProtocol:
    """Test Sequence protocol implementation."""

    def test_len(self) -> None:
        """Test __len__ method."""
        tree = GenericSegmentTree(10, 0, operator.add)
        assert len(tree) == 10

    def test_getitem_positive_index(self) -> None:
        """Test __getitem__ with positive index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(2, 42)
        assert tree[2] == 42

    def test_getitem_negative_index(self) -> None:
        """Test __getitem__ with negative index."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(-1, 42)
        assert tree[-1] == 42

    def test_getitem_slice(self) -> None:
        """Test __getitem__ with slice."""
        tree = GenericSegmentTree(5, 0, operator.add)
        values = [1, 2, 3, 4, 5]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree[1:4] == [2, 3, 4]
        assert tree[:3] == [1, 2, 3]
        assert tree[2:] == [3, 4, 5]

    def test_setitem(self) -> None:
        """Test __setitem__ method."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree[2] = 42
        assert tree[2] == 42

    def test_contains_true(self) -> None:
        """Test __contains__ returns True for existing element."""
        tree = GenericSegmentTree(5, 0, operator.add)
        tree.set(2, 42)
        assert 42 in tree

    def test_contains_false(self) -> None:
        """Test __contains__ returns False for non-existing element."""
        tree = GenericSegmentTree(5, 0, operator.add)
        assert 42 not in tree

    def test_iter(self) -> None:
        """Test iteration over segment tree."""
        tree = GenericSegmentTree(3, 0, operator.add)
        values = [10, 20, 30]

        for i, value in enumerate(values):
            tree.set(i, value)

        result = list(tree)
        assert result == values

    def test_equality_true(self) -> None:
        """Test equality comparison returns True for equal sequences."""
        tree1 = GenericSegmentTree(3, 0, operator.add)
        tree2 = GenericSegmentTree(3, 0, operator.add)

        values = [1, 2, 3]
        for i, value in enumerate(values):
            tree1.set(i, value)
            tree2.set(i, value)

        assert tree1 == tree2
        assert tree1 == values

    def test_equality_false_different_length(self) -> None:
        """Test equality comparison returns False for different lengths."""
        tree1 = GenericSegmentTree(3, 0, operator.add)
        tree2 = GenericSegmentTree(4, 0, operator.add)
        assert tree1 != tree2

    def test_equality_false_different_values(self) -> None:
        """Test equality comparison returns False for different values."""
        tree1 = GenericSegmentTree(2, 0, operator.add)
        tree2 = GenericSegmentTree(2, 0, operator.add)

        tree1.set(0, 1)
        tree2.set(0, 2)

        assert tree1 != tree2


class TestStringRepresentation:
    """Test string representation methods."""

    def test_repr(self) -> None:
        """Test __repr__ method."""
        tree = GenericSegmentTree(3, 0, operator.add)
        tree.set(0, 1)
        tree.set(1, 2)
        tree.set(2, 3)

        result = repr(tree)
        assert "GenericSegmentTree([1, 2, 3])" in result

    def test_str(self) -> None:
        """Test __str__ method."""
        tree = GenericSegmentTree(3, 0, operator.add)
        tree.set(0, 1)
        tree.set(1, 2)
        tree.set(2, 3)

        result = str(tree)
        assert "GenericSegmentTree([1, 2, 3])" in result


class TestComplexOperations:
    """Test complex operations and edge cases."""

    def test_min_operation(self) -> None:
        """Test segment tree with min operation."""
        tree = GenericSegmentTree(5, float("inf"), min)
        values = [10, 5, 20, 15, 8]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.prod(0, 2) == 5
        assert tree.prod(1, 4) == 5
        assert tree.prod(2, 5) == 8

    def test_gcd_operation(self) -> None:
        """Test segment tree with GCD operation."""
        tree = GenericSegmentTree(4, 0, math.gcd)
        values = [12, 18, 24, 30]

        for i, value in enumerate(values):
            tree.set(i, value)

        assert tree.prod(0, 2) == 6  # gcd(12, 18)
        assert tree.prod(0, 4) == 6  # gcd(12, 18, 24, 30)

    def test_string_concatenation(self) -> None:
        """Test segment tree with string concatenation."""
        tree = GenericSegmentTree(3, "", operator.add)
        tree.set(0, "Hello")
        tree.set(1, " ")
        tree.set(2, "World")

        assert tree.prod(0, 3) == "Hello World"

    def test_large_tree_performance(self) -> None:
        """Test operations on larger tree for basic performance validation."""
        size = 1000
        tree = GenericSegmentTree(size, 0, operator.add)

        # Set all elements to 1
        for i in range(size):
            tree.set(i, 1)

        # Query should return the range size
        assert tree.prod(100, 200) == 100
        assert tree.all_prod() == size


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_element_tree(self) -> None:
        """Test tree with single element."""
        tree = GenericSegmentTree(1, 0, operator.add)
        tree.set(0, 42)

        assert tree.get(0) == 42
        assert tree.prod(0, 1) == 42
        assert tree.all_prod() == 42
        assert len(tree) == 1

    def test_power_of_two_size(self) -> None:
        """Test tree with power of two size."""
        tree = GenericSegmentTree(8, 0, operator.add)

        for i in range(8):
            tree.set(i, i + 1)

        assert tree.all_prod() == 36  # Sum of 1+2+...+8

    def test_non_power_of_two_size(self) -> None:
        """Test tree with non-power of two size."""
        tree = GenericSegmentTree(7, 0, operator.add)

        for i in range(7):
            tree.set(i, i + 1)

        assert tree.all_prod() == 28  # Sum of 1+2+...+7

    def test_zero_as_identity_with_multiplication(self) -> None:
        """Test using zero as identity with multiplication (edge case)."""
        # Note: This is mathematically incorrect (should use 1 for multiplication)
        # but tests the implementation behavior
        tree = GenericSegmentTree(3, 0, operator.mul)
        tree.set(0, 5)
        tree.set(1, 3)

        # With 0 as identity, any multiplication will result in 0
        assert tree.prod(0, 2) == 0

    def test_update_same_element_multiple_times(self) -> None:
        """Test updating the same element multiple times."""
        tree = GenericSegmentTree(5, 0, operator.add)

        # Set initial values
        for i in range(5):
            tree.set(i, 1)

        initial_sum = tree.all_prod()
        assert initial_sum == 5

        # Update middle element multiple times
        tree.set(2, 10)
        assert tree.all_prod() == 14

        tree.set(2, 20)
        assert tree.all_prod() == 24

        tree.set(2, 0)
        assert tree.all_prod() == 4
