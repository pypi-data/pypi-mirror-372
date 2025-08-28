"""Tests for custom exceptions."""

import pytest

from segee.exceptions import (
    SegmentTreeError,
    SegmentTreeIndexError,
    SegmentTreeInitializationError,
    SegmentTreeRangeError,
)


class TestSegmentTreeError:
    """Test base SegmentTreeError class."""

    def test_is_exception(self) -> None:
        """Test that SegmentTreeError is an Exception."""
        error = SegmentTreeError("Test error")
        assert isinstance(error, Exception)

    def test_inheritance_hierarchy(self) -> None:
        """Test exception inheritance hierarchy."""
        index_error = SegmentTreeIndexError(5, 3)
        range_error = SegmentTreeRangeError(2, 1, 5)
        init_error = SegmentTreeInitializationError("Invalid parameters")

        # All should inherit from SegmentTreeError
        assert isinstance(index_error, SegmentTreeError)
        assert isinstance(range_error, SegmentTreeError)
        assert isinstance(init_error, SegmentTreeError)

        # Check built-in exception inheritance
        assert isinstance(index_error, IndexError)
        assert isinstance(range_error, ValueError)
        assert isinstance(init_error, ValueError)


class TestSegmentTreeIndexError:
    """Test SegmentTreeIndexError class."""

    def test_creation_with_positive_index(self) -> None:
        """Test creating error with positive index."""
        error = SegmentTreeIndexError(5, 3)
        assert error.index == 5
        assert error.size == 3
        assert "Index 5 is out of bounds for segment tree of size 3" in str(error)

    def test_creation_with_negative_index(self) -> None:
        """Test creating error with negative index."""
        error = SegmentTreeIndexError(-1, 5)
        assert error.index == -1
        assert error.size == 5
        assert "Index -1 is out of bounds for segment tree of size 5" in str(error)

    def test_error_message_format(self) -> None:
        """Test error message formatting."""
        error = SegmentTreeIndexError(10, 8)
        expected_message = "Index 10 is out of bounds for segment tree of size 8"
        assert str(error) == expected_message

    def test_attributes_accessible(self) -> None:
        """Test that attributes are accessible after creation."""
        index, size = 7, 5
        error = SegmentTreeIndexError(index, size)

        assert hasattr(error, "index")
        assert hasattr(error, "size")
        assert error.index == index
        assert error.size == size


class TestSegmentTreeRangeError:
    """Test SegmentTreeRangeError class."""

    def test_creation_with_invalid_bounds(self) -> None:
        """Test creating error with invalid bounds."""
        error = SegmentTreeRangeError(5, 2, 10)
        assert error.left == 5
        assert error.right == 2
        assert error.size == 10
        assert "Invalid range [5, 2) for segment tree of size 10" in str(error)

    def test_creation_with_out_of_bounds_range(self) -> None:
        """Test creating error with out of bounds range."""
        error = SegmentTreeRangeError(0, 15, 10)
        assert error.left == 0
        assert error.right == 15
        assert error.size == 10
        assert "Invalid range [0, 15) for segment tree of size 10" in str(error)

    def test_error_message_format(self) -> None:
        """Test error message formatting."""
        error = SegmentTreeRangeError(3, 1, 5)
        expected_message = "Invalid range [3, 1) for segment tree of size 5"
        assert str(error) == expected_message

    def test_attributes_accessible(self) -> None:
        """Test that attributes are accessible after creation."""
        left, right, size = 2, 8, 5
        error = SegmentTreeRangeError(left, right, size)

        assert hasattr(error, "left")
        assert hasattr(error, "right")
        assert hasattr(error, "size")
        assert error.left == left
        assert error.right == right
        assert error.size == size

    def test_negative_bounds(self) -> None:
        """Test error with negative bounds."""
        error = SegmentTreeRangeError(-1, 5, 10)
        assert error.left == -1
        assert error.right == 5
        assert error.size == 10
        assert "Invalid range [-1, 5) for segment tree of size 10" in str(error)


class TestSegmentTreeInitializationError:
    """Test SegmentTreeInitializationError class."""

    def test_creation_with_message(self) -> None:
        """Test creating error with custom message."""
        message = "Size must be positive"
        error = SegmentTreeInitializationError(message)
        assert str(error) == message

    def test_creation_with_empty_message(self) -> None:
        """Test creating error with empty message."""
        error = SegmentTreeInitializationError("")
        assert str(error) == ""

    def test_inheritance_from_value_error(self) -> None:
        """Test that it inherits from ValueError."""
        error = SegmentTreeInitializationError("Test")
        assert isinstance(error, ValueError)
        assert isinstance(error, SegmentTreeError)

    def test_multiple_initialization_errors(self) -> None:
        """Test different initialization error scenarios."""
        size_error = SegmentTreeInitializationError("Size must be positive, got -5")
        operation_error = SegmentTreeInitializationError("Operation must be callable")

        assert "Size must be positive" in str(size_error)
        assert "Operation must be callable" in str(operation_error)


class TestExceptionUsageInRealScenarios:
    """Test exceptions in realistic usage scenarios."""

    def test_catching_specific_exception_types(self) -> None:
        """Test that specific exception types can be caught."""
        # Test SegmentTreeIndexError
        try:
            raise SegmentTreeIndexError(10, 5)
        except SegmentTreeIndexError as e:
            assert e.index == 10
            assert e.size == 5
        except Exception:
            pytest.fail("Should have caught SegmentTreeIndexError specifically")

        # Test SegmentTreeRangeError
        try:
            raise SegmentTreeRangeError(5, 2, 10)
        except SegmentTreeRangeError as e:
            assert e.left == 5
            assert e.right == 2
            assert e.size == 10
        except Exception:
            pytest.fail("Should have caught SegmentTreeRangeError specifically")

    def test_catching_base_exception(self) -> None:
        """Test that base SegmentTreeError can catch all custom exceptions."""
        exceptions_to_test = [
            SegmentTreeIndexError(5, 3),
            SegmentTreeRangeError(2, 1, 5),
            SegmentTreeInitializationError("Invalid"),
        ]

        for exception in exceptions_to_test:
            try:
                raise exception
            except SegmentTreeError:
                pass  # This is expected
            except Exception:
                pytest.fail(f"Should have caught {type(exception).__name__} as SegmentTreeError")

    def test_exception_chaining(self) -> None:
        """Test exception chaining works correctly."""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise SegmentTreeInitializationError("Wrapper error") from e
        except SegmentTreeInitializationError as e:
            assert str(e) == "Wrapper error"
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Original error"

    def test_reraise_as_different_type(self) -> None:
        """Test re-raising built-in exceptions as custom exceptions."""
        try:
            # Simulate catching a built-in IndexError and re-raising as custom
            try:
                lst = [1, 2, 3]
                _ = lst[10]  # This will raise IndexError
            except IndexError:
                raise SegmentTreeIndexError(10, 3)
        except SegmentTreeIndexError as e:
            assert e.index == 10
            assert e.size == 3
