"""Segment Tree implementation module."""

from __future__ import annotations

from .backbone.generic_segment_tree import GenericSegmentTree
from .specialized import MaxSegmentTree, MinSegmentTree, SumSegmentTree

__all__ = [
    "GenericSegmentTree",
    "MaxSegmentTree",
    "MinSegmentTree",
    "SumSegmentTree",
]
