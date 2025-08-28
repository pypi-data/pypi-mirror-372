# Range Minimum Query

## Problem Description

Given an array of integers, you need to handle two types of operations efficiently:

1. **Update**: Change the value at a specific index
2. **Query**: Find the minimum element in a given range [left, right)

## Input Format

- First line: `n` (size of array) and `q` (number of operations)
- Second line: `n` integers representing the initial array
- Next `q` lines: Each line contains either:
  - `1 i x`: Update index `i` to value `x`
  - `2 l r`: Query minimum of range [l, r)

## Output Format

For each query operation, output the minimum element in the specified range.

## Constraints

- 1 ≤ n, q ≤ 100,000
- 0 ≤ i < n
- 0 ≤ l < r ≤ n
- -10^9 ≤ x ≤ 10^9

## Sample Input

```
5 5
10 5 20 15 8
2 0 3
2 1 4
1 2 3
2 0 3
2 1 5
```

## Sample Output

```
5
5
3
3
```

## Explanation

- Initial array: [10, 5, 20, 15, 8]
- Query(0, 3): min of [10, 5, 20] = 5
- Query(1, 4): min of [5, 20, 15] = 5
- Update(2, 3): array becomes [10, 5, 3, 15, 8]
- Query(0, 3): min of [10, 5, 3] = 3
- Query(1, 5): min of [5, 3, 15, 8] = 3