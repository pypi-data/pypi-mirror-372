"""Performance comparison tests for segment tree vs naive implementations."""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import pytest

# Add sample directories to path
sys.path.insert(0, str(Path(__file__).parent / "01_range_sum_query"))
sys.path.insert(0, str(Path(__file__).parent / "02_range_min_query"))

# Import with module reloading to avoid conflicts
import importlib.util

# Load sum query modules
sum_spec = importlib.util.spec_from_file_location(
    "sum_solve", Path(__file__).parent / "01_range_sum_query" / "sum_solve.py"
)
sum_module = importlib.util.module_from_spec(sum_spec)
sum_spec.loader.exec_module(sum_module)

sum_naive_spec = importlib.util.spec_from_file_location(
    "sum_groundtruth", Path(__file__).parent / "01_range_sum_query" / "sum_groundtruth.py"
)
sum_naive_module = importlib.util.module_from_spec(sum_naive_spec)
sum_naive_spec.loader.exec_module(sum_naive_module)

# Load min query modules
min_spec = importlib.util.spec_from_file_location(
    "min_solve", Path(__file__).parent / "02_range_min_query" / "min_solve.py"
)
min_module = importlib.util.module_from_spec(min_spec)
min_spec.loader.exec_module(min_module)

min_naive_spec = importlib.util.spec_from_file_location(
    "min_groundtruth", Path(__file__).parent / "02_range_min_query" / "min_groundtruth.py"
)
min_naive_module = importlib.util.module_from_spec(min_naive_spec)
min_naive_spec.loader.exec_module(min_naive_module)

sum_solve = sum_module.solve
sum_naive = sum_naive_module.solve_sum_naive
min_solve = min_module.solve
min_naive = min_naive_module.solve_min_naive


def generate_test_data(n: int, q: int, operation_ratio: float = 0.3) -> str:
    """Generate test data for performance testing.

    Args:
        n: Array size
        q: Number of queries
        operation_ratio: Ratio of update operations (vs query operations)

    Returns:
        Generated test input string
    """
    # Generate initial array
    initial_array = [random.randint(-1000, 1000) for _ in range(n)]

    lines = [f"{n} {q}"]
    lines.append(" ".join(map(str, initial_array)))

    # Generate operations
    for _ in range(q):
        if random.random() < operation_ratio:
            # Update operation
            index = random.randint(0, n - 1)
            value = random.randint(-1000, 1000)
            lines.append(f"1 {index} {value}")
        else:
            # Query operation
            left = random.randint(0, n - 1)
            right = random.randint(left + 1, n)
            lines.append(f"2 {left} {right}")

    return "\n".join(lines)


class TestPerformanceComparison:
    """Performance comparison between segment tree and naive implementations."""

    @pytest.mark.parametrize("n,q", [(100, 100), (500, 500), (1000, 1000)])
    def test_sum_query_performance(self, n: int, q: int) -> None:
        """Test sum query performance comparison."""
        # Set seed for reproducible results
        random.seed(42)
        test_data = generate_test_data(n, q)

        # Measure segment tree performance
        start_time = time.perf_counter()
        segment_result = sum_solve(test_data)
        segment_time = time.perf_counter() - start_time

        # Measure naive performance
        start_time = time.perf_counter()
        naive_result = sum_naive(test_data)
        naive_time = time.perf_counter() - start_time

        # Verify results match
        assert segment_result == naive_result

        # Performance analysis
        speedup = naive_time / segment_time if segment_time > 0 else float("inf")

        print(f"\nSum Query Performance (n={n}, q={q}):")
        print(f"  Segment Tree: {segment_time:.4f}s")
        print(f"  Naive:        {naive_time:.4f}s")
        print(f"  Speedup:      {speedup:.2f}x")

        # Performance comparison is informational only
        # Focus on correctness verification rather than strict performance requirements
        assert segment_time > 0, "Segment tree should complete in measurable time"
        assert naive_time > 0, "Naive method should complete in measurable time"

    @pytest.mark.parametrize("n,q", [(100, 100), (500, 500), (1000, 1000)])
    def test_min_query_performance(self, n: int, q: int) -> None:
        """Test min query performance comparison."""
        # Set seed for reproducible results
        random.seed(123)
        test_data = generate_test_data(n, q)

        # Measure segment tree performance
        start_time = time.perf_counter()
        segment_result = min_solve(test_data)
        segment_time = time.perf_counter() - start_time

        # Measure naive performance
        start_time = time.perf_counter()
        naive_result = min_naive(test_data)
        naive_time = time.perf_counter() - start_time

        # Verify results match
        assert segment_result == naive_result

        # Performance analysis
        speedup = naive_time / segment_time if segment_time > 0 else float("inf")

        print(f"\nMin Query Performance (n={n}, q={q}):")
        print(f"  Segment Tree: {segment_time:.4f}s")
        print(f"  Naive:        {naive_time:.4f}s")
        print(f"  Speedup:      {speedup:.2f}x")

        # Performance comparison is informational only
        # Focus on correctness verification rather than strict performance requirements
        assert segment_time > 0, "Segment tree should complete in measurable time"
        assert naive_time > 0, "Naive method should complete in measurable time"

    def test_scalability_demonstration(self) -> None:
        """Demonstrate scalability advantage of segment tree for larger inputs."""
        # Test with larger inputs where segment tree should show advantage
        sizes = [(1000, 2000), (2000, 3000)]

        for n, q in sizes:
            random.seed(456)
            test_data = generate_test_data(n, q, operation_ratio=0.2)

            # Measure segment tree performance
            start_time = time.perf_counter()
            segment_result = sum_solve(test_data)
            segment_time = time.perf_counter() - start_time

            # Measure naive performance
            start_time = time.perf_counter()
            naive_result = sum_naive(test_data)
            naive_time = time.perf_counter() - start_time

            # Verify correctness
            assert segment_result == naive_result

            speedup = naive_time / segment_time if segment_time > 0 else float("inf")

            print(f"\nScalability Test (n={n}, q={q}):")
            print(f"  Segment Tree: {segment_time:.4f}s")
            print(f"  Naive:        {naive_time:.4f}s")
            print(f"  Speedup:      {speedup:.2f}x")

            # Performance comparison is informational only
            # Focus on correctness verification rather than strict performance requirements
            assert segment_time > 0, "Segment tree should complete in measurable time"
            assert naive_time > 0, "Naive method should complete in measurable time"


if __name__ == "__main__":
    # Run a quick performance test
    test = TestPerformanceComparison()
    test.test_sum_query_performance(500, 500)
    test.test_min_query_performance(500, 500)
