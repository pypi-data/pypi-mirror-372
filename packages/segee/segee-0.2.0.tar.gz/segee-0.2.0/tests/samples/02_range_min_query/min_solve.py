"""Solution for Range Minimum Query problem using MinSegmentTree."""

from __future__ import annotations

import sys
from pathlib import Path

# Add the project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from segee import MinSegmentTree


def solve(input_data: str) -> str:
    """Solve the Range Minimum Query problem.

    Args:
        input_data: Input string containing the problem data

    Returns:
        Output string with query results
    """
    lines = input_data.strip().split("\n")
    n, q = map(int, lines[0].split())
    initial_values = list(map(int, lines[1].split()))

    # Initialize the segment tree with the initial values
    tree = MinSegmentTree(n)
    for i, value in enumerate(initial_values):
        tree.set(i, value)

    results = []

    for i in range(q):
        operation = list(map(int, lines[2 + i].split()))

        if operation[0] == 1:  # Update operation
            _, index, value = operation
            tree.set(index, value)
        elif operation[0] == 2:  # Query operation
            _, left, right = operation
            result = tree.minimum(left, right)
            results.append(str(int(result)))

    return "\n".join(results)


def main() -> None:
    """Main function for interactive testing."""
    sample_input = """5 5
10 5 20 15 8
2 0 3
2 1 4
1 2 3
2 0 3
2 1 5"""

    result = solve(sample_input)
    print(result)


if __name__ == "__main__":
    main()
