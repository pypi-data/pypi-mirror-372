from enum import Enum


class Monoid(Enum):
    """Enumeration of common monoid types with identity elements."""

    ADD = 0
    MULTIPLY = 1
    MIN = float("inf")
    MAX = float("-inf")
