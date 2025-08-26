from typing import List, Optional, Sequence

import numpy as np

from .CompressedList import CompressedList
from .partition import Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


class CompressedIntegerList(CompressedList):
    """CompressedList implementation for lists of integers."""

    def __init__(
        self,
        unlist_data: np.ndarray,
        partitioning: Partitioning,
        element_metadata: dict = None,
        metadata: dict = None,
        **kwargs,
    ):
        """Initialize a CompressedIntegerList.

        Args:
            unlist_data:
                NumPy array of integers.

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
            unlist_data, partitioning, element_type="integer", element_metadata=element_metadata, metadata=metadata
        )

    def _extract_range(self, start: int, end: int) -> np.ndarray:
        """Extract a range from unlist_data.

        Args:
            start:
                Start index (inclusive).

            end:
                End index (exclusive).

        Returns:
            Same type as unlist_data.
        """
        return self._unlist_data[start:end]

    @classmethod
    def from_list(
        cls, lst: List[List[int]], names: Optional[Sequence[str]] = None, metadata: dict = None
    ) -> "CompressedIntegerList":
        """
        Create a CompressedIntegerList from a list of integer lists.

        Args:
            lst:
                List of integer lists.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new CompressedIntegerList.
        """
        # Flatten the list
        flat_data = []
        for sublist in lst:
            flat_data.extend(sublist)

        # Create partitioning
        partitioning = Partitioning.from_list(lst, names)

        # Create unlist_data
        unlist_data = np.array(flat_data, dtype=np.int64)

        return cls(unlist_data, partitioning, metadata=metadata)
