"""Tests for Range Sum Query problem solution."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the sample directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sum_groundtruth import solve_sum_naive
from sum_solve import solve


class TestRangeSumQuerySolution:
    """Test the Range Sum Query solution."""

    def test_sample_case(self) -> None:
        """Test the provided sample case."""
        input_data = """5 4
1 2 3 4 5
2 0 3
1 1 10
2 0 3
2 1 4"""

        expected_output = """6
14
17"""

        result = solve(input_data)
        assert result == expected_output

    def test_single_element(self) -> None:
        """Test with single element array."""
        input_data = """1 3
42
2 0 1
1 0 100
2 0 1"""

        expected_output = """42
100"""

        result = solve(input_data)
        assert result == expected_output

    def test_no_updates_only_queries(self) -> None:
        """Test with only query operations."""
        input_data = """4 3
10 20 30 40
2 0 2
2 1 3
2 0 4"""

        expected_output = """30
50
100"""

        result = solve(input_data)
        assert result == expected_output

    def test_only_updates_no_queries(self) -> None:
        """Test with only update operations."""
        input_data = """3 2
1 2 3
1 0 10
1 2 30"""

        expected_output = """"""

        result = solve(input_data)
        assert result == expected_output

    def test_negative_values(self) -> None:
        """Test with negative values."""
        input_data = """4 4
-5 10 -3 8
2 0 2
1 1 -20
2 0 2
2 1 4"""

        expected_output = """5
-25
-15"""

        result = solve(input_data)
        assert result == expected_output

    def test_zero_values(self) -> None:
        """Test with zero values."""
        input_data = """3 3
0 0 0
2 0 3
1 1 5
2 0 3"""

        expected_output = """0
5"""

        result = solve(input_data)
        assert result == expected_output

    def test_large_values(self) -> None:
        """Test with large values."""
        input_data = """3 3
1000000000 -1000000000 500000000
2 0 3
1 0 2000000000
2 0 2"""

        expected_output = """500000000
1000000000"""

        result = solve(input_data)
        assert result == expected_output

    def test_full_range_queries(self) -> None:
        """Test queries that span the entire array."""
        input_data = """5 3
1 2 3 4 5
2 0 5
1 2 100
2 0 5"""

        expected_output = """15
112"""

        result = solve(input_data)
        assert result == expected_output

    def test_single_element_ranges(self) -> None:
        """Test queries with single element ranges."""
        input_data = """5 5
10 20 30 40 50
2 0 1
2 2 3
1 3 100
2 3 4
2 4 5"""

        expected_output = """10
30
100
50"""

        result = solve(input_data)
        assert result == expected_output

    def test_consecutive_updates_same_index(self) -> None:
        """Test multiple updates to the same index."""
        input_data = """3 5
1 2 3
2 0 3
1 1 10
1 1 20
1 1 5
2 0 3"""

        expected_output = """6
9"""

        result = solve(input_data)
        assert result == expected_output


class TestGroundTruthComparison:
    """Test segment tree implementation against naive ground truth."""

    def test_against_naive_sample_case(self) -> None:
        """Test sample case against naive implementation."""
        input_data = """5 4
1 2 3 4 5
2 0 3
1 1 10
2 0 3
2 1 4"""

        segment_result = solve(input_data)
        naive_result = solve_sum_naive(input_data)
        assert segment_result == naive_result

    def test_against_naive_complex_case(self) -> None:
        """Test complex case against naive implementation."""
        input_data = """10 15
1 5 2 8 3 9 4 7 6 0
2 0 5
2 3 8
1 4 100
2 0 10
2 4 6
1 0 50
1 9 25
2 0 3
2 7 10
2 0 10
1 5 0
2 5 8
2 0 5
2 8 10
2 0 10"""

        segment_result = solve(input_data)
        naive_result = solve_sum_naive(input_data)
        assert segment_result == naive_result

    def test_against_naive_edge_cases(self) -> None:
        """Test edge cases against naive implementation."""
        # Single element
        input_data = """1 3
42
2 0 1
1 0 -10
2 0 1"""

        segment_result = solve(input_data)
        naive_result = solve_sum_naive(input_data)
        assert segment_result == naive_result

        # All negative values
        input_data = """5 5
-10 -5 -20 -1 -15
2 0 3
2 1 4
1 2 -100
2 0 5
2 2 5"""

        segment_result = solve(input_data)
        naive_result = solve_sum_naive(input_data)
        assert segment_result == naive_result
