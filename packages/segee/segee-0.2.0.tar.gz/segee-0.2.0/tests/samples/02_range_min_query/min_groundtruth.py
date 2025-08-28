"""Ground truth implementation for Range Minimum Query using naive approach."""

from __future__ import annotations


def solve_min_naive(input_data: str) -> str:
    """Solve Range Minimum Query using naive O(n) approach per query.

    This implementation serves as ground truth for correctness verification.
    Time complexity: O(q * n) where q is queries and n is array size.

    Args:
        input_data: Input string containing the problem data

    Returns:
        Output string with query results
    """
    lines = input_data.strip().split("\n")
    n, q = map(int, lines[0].split())
    array = list(map(int, lines[1].split()))

    results = []

    for i in range(q):
        operation = list(map(int, lines[2 + i].split()))

        if operation[0] == 1:  # Update operation
            _, index, value = operation
            array[index] = value
        elif operation[0] == 2:  # Query operation
            _, left, right = operation
            # Naive min calculation: O(n)
            result = min(array[left:right])
            results.append(str(result))

    return "\n".join(results)


def main() -> None:
    """Main function for testing."""
    sample_input = """5 5
10 5 20 15 8
2 0 3
2 1 4
1 2 3
2 0 3
2 1 5"""

    result = solve_min_naive(sample_input)
    print("Naive implementation result:")
    print(result)


if __name__ == "__main__":
    main()
