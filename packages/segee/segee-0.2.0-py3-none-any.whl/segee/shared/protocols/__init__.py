"""Protocol definitions for the Segee package.

This module provides simple, essential protocols for types used in
data structures. These protocols enable static type checking and
provide clear contracts for operations.

The protocols are designed to be minimal and focused:
- AdditiveProtocol: Types supporting addition and subtraction
- ComparableProtocol: Types supporting comparison operations
- MultiplicativeProtocol: Types supporting multiplication

Examples:
    >>> from segee.shared.protocols import AdditiveProtocol, ComparableProtocol
    >>>
    >>> def sum_range(data: list[AdditiveProtocol]) -> AdditiveProtocol:
    ...     return sum(data[1:]) - sum(data[:-1])  # Range sum using protocols
    >>>
    >>> def find_min(data: list[ComparableProtocol]) -> ComparableProtocol:
    ...     return min(data)  # Min operation using comparison protocol
"""

from __future__ import annotations

from .additive import AdditiveProtocol
from .comparable import ComparableProtocol
from .multiplicative import MultiplicativeProtocol

__all__ = [
    "AdditiveProtocol",
    "ComparableProtocol",
    "MultiplicativeProtocol",
]
