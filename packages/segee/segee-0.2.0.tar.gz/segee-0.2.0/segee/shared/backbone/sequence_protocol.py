from __future__ import annotations

from abc import abstractmethod
from typing import TypeVar

T = TypeVar("T")


class SequenceProtocolMixin[T]:
    """Mixin providing sequence protocol methods for data structures."""

    @abstractmethod
    def __len__(self) -> int:
        """Return the size of the data structure."""
        ...

    @abstractmethod
    def __getitem__(self, index: int) -> T:
        """Get the value at the specified index."""
        ...

    @abstractmethod
    def __setitem__(self, index: int, value: T) -> None:
        """Set the value at the specified index."""
        ...

    def __contains__(self, value: T) -> bool:
        """Check if a value exists in the data structure."""
        return any(self[i] == value for i in range(len(self)))

    def __iter__(self):
        """Iterate over all values in the data structure."""
        for i in range(len(self)):
            yield self[i]

    def to_list(self) -> list[T]:
        """Convert the data structure to a list representation.

        Returns:
            List containing all values in the data structure.
        """
        return [self[i] for i in range(len(self))]
