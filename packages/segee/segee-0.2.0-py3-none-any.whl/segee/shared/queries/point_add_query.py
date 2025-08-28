"""Point add query mixin for data structures."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from segee.shared.protocols import AdditiveProtocol

T = TypeVar("T", bound=AdditiveProtocol)


class PointAddQueryMixin(ABC):
    """Mixin providing point add query operations.

    This mixin defines the interface for data structures that support
    adding values to specific indices.
    """

    @abstractmethod
    def add(self, index: int, value: T) -> None:
        """Add a value to the element at the specified index.

        Args:
            index: The index to update.
            value: The value to add.

        Raises:
            SegmentTreeIndexError: If index is out of bounds.
        """
        ...
