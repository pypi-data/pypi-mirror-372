from typing import List, Optional, Sequence

from .CompressedList import CompressedList
from .partition import Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedStringList(CompressedList):
    """CompressedList implementation for lists of strings."""

    def __init__(
        self,
        unlist_data: List[str],
        partitioning: Partitioning,
        element_metadata: dict = None,
        metadata: dict = None,
        **kwargs,
    ):
        """Initialize a CompressedStringList.

        Args:
            unlist_data:
                List of strings.

            partitioning:
                Partitioning object defining element boundaries.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            kwargs:
                Additional arguments.
        """
        super().__init__(
            unlist_data, partitioning, element_type="string", element_metadata=element_metadata, metadata=metadata
        )

    def _extract_range(self, start: int, end: int) -> List[str]:
        """Extract a range from unlist_data.

        Args:
            start:
                Start index (inclusive).

            end:
                End index (exclusive).

        Returns:
            List of strings.
        """
        return self._unlist_data[start:end]

    @classmethod
    def from_list(
        cls, lst: List[List[str]], names: Optional[Sequence[str]] = None, metadata: dict = None
    ) -> "CompressedStringList":
        """Create a `CompressedStringList` from a list of string lists.

        Args:
            lst:
                List of string lists.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedStringList`.
        """
        # Flatten the list
        flat_data = []
        for sublist in lst:
            flat_data.extend(sublist)

        # Create partitioning
        partitioning = Partitioning.from_list(lst, names)

        return cls(flat_data, partitioning, metadata=metadata)
