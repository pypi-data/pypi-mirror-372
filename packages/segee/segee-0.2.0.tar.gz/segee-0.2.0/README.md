# 🌳 Segee

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Python data structures library for efficient range queries and updates.


## ✨ Features

- **Segment Trees**: Range queries with any associative operation (sum, min, max, GCD, etc.)
- **Binary Indexed Trees**: Efficient sum queries and updates for additive operations
- **Type Safety**: Generic type hints with protocol-based constraints
- **Pure Python**: Zero dependencies, works with Python 3.12+
- **Comprehensive Testing**: 232 tests including real-world problem validation
- **Pythonic API**: Full sequence protocol support (`tree[i]`, `len(tree)`, etc.)

## 🚀 Quick Start

```python
from segee import SumSegmentTree, MinSegmentTree, BinaryIndexedTree

# Segment Trees - for any associative operation
sum_tree = SumSegmentTree(5)
sum_tree[0:5] = [1, 2, 3, 4, 5]
print(sum_tree.sum(1, 4))     # 9 (sum of indices 1-3)

min_tree = MinSegmentTree(5)
min_tree[0:5] = [10, 5, 20, 15, 8]
print(min_tree.minimum(1, 4))  # 5 (min of indices 1-3)

# Binary Indexed Trees - optimized for additive operations
bit = BinaryIndexedTree([1, 2, 3, 4, 5])
bit.add(2, 10)  # Add 10 to index 2
print(bit.sum(0, 5))  # 25 (sum of all elements)

# Custom operations with generic segment tree
import math
from segee import GenericSegmentTree
gcd_tree = GenericSegmentTree(5, 0, math.gcd)
```

## 📦 Installation

```bash
pip install segee
```

## 🏗️ Available Data Structures

### Segment Trees
- `GenericSegmentTree[T]` - Generic implementation for any associative operation
- `SumSegmentTree` - Optimized for sum operations
- `MinSegmentTree` - Optimized for minimum operations
- `MaxSegmentTree` - Optimized for maximum operations

### Binary Indexed Trees
- `GenericBinaryIndexedTree[T]` - Generic implementation for additive operations
- `BinaryIndexedTree` - Optimized for int/float types
- `RangeAddBinaryIndexedTree` - Supports efficient range updates

### 🎯 Interactive CLI
```bash
# Launch interactive segment tree CLI
segee
```

## 🏛️ Architecture

```
segee/
├── segment_tree/           # Segment tree module
│   ├── backbone/          # Generic implementations
│   └── specialized/       # Sum/Min/Max classes
├── binary_indexed_tree/   # Binary indexed tree module
│   ├── backbone/          # Generic implementations
│   └── specialized/       # Optimized classes
├── shared/               # Shared protocols and mixins
└── segee_cli/           # Interactive CLI application
```


## 📚 Documentation

- [Usage Guide](docs/usage.md) - Examples and usage patterns
- [API Reference](docs/api.md) - Complete method documentation
- [Performance Guide](docs/performance.md) - Complexity analysis and benchmarks
- [Contributing](docs/contributing.md) - Development guidelines


## 🤔 When to Use

- **Segment Trees**: When you need range queries with custom operations (min, max, GCD, XOR, etc.)
- **Binary Indexed Trees**: When you need fast sum queries and updates, or range sum with range updates

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
