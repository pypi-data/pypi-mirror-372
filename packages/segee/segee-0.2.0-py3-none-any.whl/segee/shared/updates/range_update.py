# DEPRECATED: This file is deprecated. Use UnifiedUpdateMixin from point_update.py instead.
from abc import ABC, abstractmethod


# Legacy mixins for backward compatibility - DO NOT USE IN NEW CODE
class RangeUpdateMixin(ABC):
    """DEPRECATED: Use UnifiedUpdateMixin instead."""

    @abstractmethod
    def update(self, left: int, right: int, value: float) -> None:
        """DEPRECATED: Update a value to all elements in the specified range."""
        ...


class RangeAddMixin(ABC):
    """DEPRECATED: Use UnifiedUpdateMixin instead."""

    @abstractmethod
    def add(self, left: int, right: int, value: float) -> None:
        """DEPRECATED: Add a value to all elements in the specified range."""
        ...
