"""Query mixins for data structures."""

from __future__ import annotations

from .point_add_query import PointAddQueryMixin
from .range_add_query import RangeAddQueryMixin
from .range_max_query import RangeMaxQueryMixin
from .range_min_query import RangeMinQueryMixin
from .range_sum_query import RangeSumQueryMixin

__all__ = [
    "PointAddQueryMixin",
    "RangeAddQueryMixin",
    "RangeMaxQueryMixin",
    "RangeMinQueryMixin",
    "RangeSumQueryMixin",
]
