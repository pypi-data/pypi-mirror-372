# Range Sum Query

## Problem Description

Given an array of integers, you need to handle two types of operations efficiently:

1. **Update**: Change the value at a specific index
2. **Query**: Calculate the sum of elements in a given range [left, right)

## Input Format

- First line: `n` (size of array) and `q` (number of operations)
- Second line: `n` integers representing the initial array
- Next `q` lines: Each line contains either:
  - `1 i x`: Update index `i` to value `x`
  - `2 l r`: Query sum of range [l, r)

## Output Format

For each query operation, output the sum of the specified range.

## Constraints

- 1 ≤ n, q ≤ 100,000
- 0 ≤ i < n
- 0 ≤ l < r ≤ n
- -10^9 ≤ x ≤ 10^9

## Sample Input

```
5 4
1 2 3 4 5
2 0 3
1 1 10
2 0 3
2 1 4
```

## Sample Output

```
6
14
17
```

## Explanation

- Initial array: [1, 2, 3, 4, 5]
- Query(0, 3): sum of [1, 2, 3] = 6
- Update(1, 10): array becomes [1, 10, 3, 4, 5]
- Query(0, 3): sum of [1, 10, 3] = 14
- Query(1, 4): sum of [10, 3, 4] = 17