"""Tests for Range Minimum Query problem solution."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the sample directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from min_groundtruth import solve_min_naive
from min_solve import solve


class TestRangeMinQuerySolution:
    """Test the Range Minimum Query solution."""

    def test_sample_case(self) -> None:
        """Test the provided sample case."""
        input_data = """5 5
10 5 20 15 8
2 0 3
2 1 4
1 2 3
2 0 3
2 1 5"""

        expected_output = """5
5
3
3"""

        result = solve(input_data)
        assert result == expected_output

    def test_single_element(self) -> None:
        """Test with single element array."""
        input_data = """1 3
42
2 0 1
1 0 10
2 0 1"""

        expected_output = """42
10"""

        result = solve(input_data)
        assert result == expected_output

    def test_no_updates_only_queries(self) -> None:
        """Test with only query operations."""
        input_data = """4 3
10 5 30 2
2 0 2
2 1 3
2 0 4"""

        expected_output = """5
5
2"""

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

        expected_output = """-5
-20
-20"""

        result = solve(input_data)
        assert result == expected_output

    def test_all_same_values(self) -> None:
        """Test with all identical values."""
        input_data = """4 3
7 7 7 7
2 0 2
2 1 4
2 0 4"""

        expected_output = """7
7
7"""

        result = solve(input_data)
        assert result == expected_output

    def test_ascending_sequence(self) -> None:
        """Test with ascending sequence."""
        input_data = """5 3
1 2 3 4 5
2 0 3
2 2 5
2 0 5"""

        expected_output = """1
3
1"""

        result = solve(input_data)
        assert result == expected_output

    def test_descending_sequence(self) -> None:
        """Test with descending sequence."""
        input_data = """5 3
50 40 30 20 10
2 0 3
2 2 5
2 0 5"""

        expected_output = """30
10
10"""

        result = solve(input_data)
        assert result == expected_output

    def test_single_element_ranges(self) -> None:
        """Test queries with single element ranges."""
        input_data = """5 5
10 20 30 40 50
2 0 1
2 2 3
1 3 5
2 3 4
2 4 5"""

        expected_output = """10
30
5
50"""

        result = solve(input_data)
        assert result == expected_output

    def test_large_values(self) -> None:
        """Test with large values."""
        input_data = """3 3
1000000000 -1000000000 500000000
2 0 3
1 0 2000000000
2 0 2"""

        expected_output = """-1000000000
-1000000000"""

        result = solve(input_data)
        assert result == expected_output


class TestGroundTruthComparison:
    """Test segment tree implementation against naive ground truth."""

    def test_against_naive_sample_case(self) -> None:
        """Test sample case against naive implementation."""
        input_data = """5 5
10 5 20 15 8
2 0 3
2 1 4
1 2 3
2 0 3
2 1 5"""

        segment_result = solve(input_data)
        naive_result = solve_min_naive(input_data)
        assert segment_result == naive_result

    def test_against_naive_complex_case(self) -> None:
        """Test complex case against naive implementation."""
        input_data = """8 12
100 50 75 25 80 60 40 90
2 0 4
2 2 6
1 3 10
2 0 8
2 3 7
1 0 200
1 7 5
2 0 3
2 5 8
2 0 8
2 4 6
2 1 5"""

        segment_result = solve(input_data)
        naive_result = solve_min_naive(input_data)
        assert segment_result == naive_result

    def test_against_naive_edge_cases(self) -> None:
        """Test edge cases against naive implementation."""
        # Single element
        input_data = """1 3
-50
2 0 1
1 0 100
2 0 1"""

        segment_result = solve(input_data)
        naive_result = solve_min_naive(input_data)
        assert segment_result == naive_result

        # All negative values
        input_data = """6 8
-100 -50 -200 -10 -150 -75
2 0 3
2 2 5
1 1 -300
2 0 6
2 1 4
1 4 -5
2 3 6
2 0 6"""

        segment_result = solve(input_data)
        naive_result = solve_min_naive(input_data)
        assert segment_result == naive_result
