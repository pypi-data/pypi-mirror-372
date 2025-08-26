from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator, List, Optional, Sequence, Union
from warnings import warn

import biocutils as ut
import numpy as np

from .partition import Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def _validate_data_and_partitions(unlist_data, partition):
    if len(unlist_data) != partition.nobj():
        raise ValueError(
            f"Length of 'unlist_data' ({len(unlist_data)}) "
            f"doesn't match 'partitioning' total length ({partition.nobj()})."
        )


class CompressedList(ABC):
    """Base class for compressed list objects.

    `CompressedList` stores list elements concatenated in a single vector-like object
    with partitioning information that defines where each list element starts and ends.
    """

    def __init__(
        self,
        unlist_data: Any,
        partitioning: Partitioning,
        element_type: str = None,
        element_metadata: dict = None,
        metadata: Optional[dict] = None,
        validate: bool = True,
    ):
        """Initialize a CompressedList.

        Args:
            unlist_data:
                Vector-like object containing concatenated elements.

            partitioning:
                Partitioning object defining element boundaries.

            element_type:
                String identifier for the type of elements.

            element_metadata:
                Optional metadata for elements.

            metadata:
                Optional general metadata.

            validate:
                Internal use only.
        """
        self._unlist_data = unlist_data
        self._partitioning = partitioning
        self._element_type = element_type
        self._element_metadata = element_metadata or {}
        self._metadata = metadata or {}

        if validate:
            _validate_data_and_partitions(self._unlist_data, self._partitioning)

    def _define_output(self, in_place: bool = False) -> "Partitioning":
        if in_place is True:
            return self
        else:
            return self.__copy__()

    #########################
    ######>> Copying <<######
    #########################

    def __deepcopy__(self, memo=None, _nil=[]):
        """
        Returns:
            A deep copy of the current ``Partitioning``.
        """
        from copy import deepcopy

        _unlistdata_copy = deepcopy(self._unlist_data)
        _part_copy = deepcopy(self._partitioning)
        _elem_type_copy = deepcopy(self._element_type)
        _elem_metadata_copy = deepcopy(self._element_metadata)
        _metadata_copy = deepcopy(self._metadata)

        current_class_const = type(self)
        return current_class_const(
            unlist_data=_unlistdata_copy,
            partitioning=_part_copy,
            element_type=_elem_type_copy,
            element_metadata=_elem_metadata_copy,
            metadata=_metadata_copy,
        )

    def __copy__(self):
        """
        Returns:
            A shallow copy of the current ``Partitioning``.
        """
        current_class_const = type(self)
        return current_class_const(
            unlist_data=self._unlist_data,
            partitioning=self._partitioning,
            element_type=self._element_type,
            element_metadata=self._element_metadata,
            metadata=self._metadata,
        )

    def copy(self):
        """Alias for :py:meth:`~__copy__`."""
        return self.__copy__()

    ######################################
    ######>> length and iterators <<######
    ######################################

    def __len__(self) -> int:
        """Return the number of list elements."""
        return len(self._partitioning)

    def get_element_lengths(self) -> np.ndarray:
        """Get the lengths of each list element."""
        return self._partitioning.get_element_lengths()

    def __iter__(self) -> Iterator[Any]:
        """Iterate over list elements."""
        for i in range(len(self)):
            yield self[i]

    ##########################
    ######>> Printing <<######
    ##########################

    def __repr__(self) -> str:
        """
        Returns:
            A string representation.
        """
        output = f"{type(self).__name__}(number_of_elements={len(self)}"
        output += ", unlist_data=" + ut.print_truncated_list(self._unlist_data)
        output += ", partitioning=" + self._partitioning.__repr__()
        output += ", element_type=" + self._element_type

        if len(self._element_metadata) > 0:
            output += ", element_metadata=" + ut.print_truncated_dict(self._element_metadata)

        if len(self._metadata) > 0:
            output += ", metadata=" + ut.print_truncated_dict(self._metadata)

        output += ")"
        return output

    def __str__(self) -> str:
        """
        Returns:
            A pretty-printed string containing the contents of this object.
        """
        output = f"class: {type(self).__name__}\n"

        output += f"number of elements: ({len(self)}) of type: {self._element_type}\n"

        output += f"unlist_data: {ut.print_truncated_list(self._unlist_data)}\n"

        output += f"partitioning: {ut.print_truncated_list(self._partitioning)}\n"

        output += f"element_metadata({str(len(self._element_metadata))}): {ut.print_truncated_list(list(self._element_metadata.keys()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"
        output += f"metadata({str(len(self._metadata))}): {ut.print_truncated_list(list(self._metadata.keys()), sep=' ', include_brackets=False, transform=lambda y: y)}\n"

        return output

    #############################
    ######>> element_type <<#####
    #############################

    def get_element_type(self) -> str:
        """Return the element_type."""
        return self._element_type

    @property
    def element_type(self) -> str:
        """Alias for :py:attr:`~get_element_type`, provided for back-compatibility."""
        return self.get_element_type()

    ###########################
    ######>> partitions <<#####
    ###########################

    def get_partitioning(self) -> Partitioning:
        """Return the paritioning info."""
        return self._partitioning

    @property
    def paritioning(self) -> Partitioning:
        """Alias for :py:attr:`~get_paritioning`, provided for back-compatibility."""
        return self.get_partitioning()

    #######################
    ######>> names <<######
    #######################

    def get_names(self) -> Optional[ut.NamedList]:
        """Get the names of list elements."""
        return self._partitioning.get_names()

    def set_names(self, names: Sequence[str], in_place: bool = False) -> "CompressedList":
        """Set the names of list elements.

        names:
            New names, same as the number of rows.

            May be `None` to remove names.

        in_place:
            Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        output._partitioning = self._partitioning.set_names(names, in_place=False)
        return output

    @property
    def names(self) -> Optional[ut.NamedList]:
        """Alias for :py:attr:`~get_names`."""
        return self._partitioning.get_names()

    @names.setter
    def names(self, names: Sequence[str]):
        """Alias for :py:attr:`~set_names` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'names' is an in-place operation, use 'set_names' instead",
            UserWarning,
        )
        self.set_names(names=names, in_place=True)

    #############################
    ######>> unlist_data <<######
    #############################

    def get_unlist_data(self) -> Any:
        """Get all elements."""
        return self._unlist_data

    def set_unlist_data(self, unlist_data: Any, in_place: bool = False) -> "CompressedList":
        """Set new list elements.

        Args:
            unlist_data:
                New vector-like object containing concatenated elements.

            in_place:
                Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)

        _validate_data_and_partitions(unlist_data=unlist_data, partition=self._partitioning)

        output._unlist_data = unlist_data
        return output

    @property
    def unlist_data(self) -> Any:
        """Alias for :py:attr:`~get_unlist_data`."""
        return self.get_unlist_data()

    @unlist_data.setter
    def unlist_data(self, unlist_data: Any):
        """Alias for :py:attr:`~set_unlist_data` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'unlist_data' is an in-place operation, use 'set_unlist_data' instead",
            UserWarning,
        )
        self.set_unlist_data(unlist_data, in_place=True)

    ###################################
    ######>> element metadata <<#######
    ###################################

    def get_element_metadata(self) -> dict:
        """
        Returns:
            Dictionary of metadata for each element in this object.
        """
        return self._element_metadata

    def set_element_metadata(self, element_metadata: dict, in_place: bool = False) -> "CompressedList":
        """Set new element metadata.

        Args:
            element_metadata:
                New element metadata for this object.

            in_place:
                Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if not isinstance(element_metadata, dict):
            raise TypeError(f"`element_metadata` must be a dictionary, provided {type(element_metadata)}.")
        output = self._define_output(in_place)
        output._element_metadata = element_metadata
        return output

    @property
    def element_metadata(self) -> dict:
        """Alias for :py:attr:`~get_element_metadata`."""
        return self.get_element_metadata()

    @element_metadata.setter
    def element_metadata(self, element_metadata: dict):
        """Alias for :py:attr:`~set_element_metadata` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'element_metadata' is an in-place operation, use 'set_element_metadata' instead",
            UserWarning,
        )
        self.set_element_metadata(element_metadata, in_place=True)

    ###########################
    ######>> metadata <<#######
    ###########################

    def get_metadata(self) -> dict:
        """
        Returns:
            Dictionary of metadata for this object.
        """
        return self._metadata

    def set_metadata(self, metadata: dict, in_place: bool = False) -> "CompressedList":
        """Set additional metadata.

        Args:
            metadata:
                New metadata for this object.

            in_place:
                Whether to modify the ``CompressedList`` in place.

        Returns:
            A modified ``CompressedList`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if not isinstance(metadata, dict):
            raise TypeError(f"`metadata` must be a dictionary, provided {type(metadata)}.")
        output = self._define_output(in_place)
        output._metadata = metadata
        return output

    @property
    def metadata(self) -> dict:
        """Alias for :py:attr:`~get_metadata`."""
        return self.get_metadata()

    @metadata.setter
    def metadata(self, metadata: dict):
        """Alias for :py:attr:`~set_metadata` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'metadata' is an in-place operation, use 'set_metadata' instead",
            UserWarning,
        )
        self.set_metadata(metadata, in_place=True)

    ##########################
    ######>> accessors <<#####
    ##########################

    def __getitem__(self, key: Union[int, str, slice]) -> Any:
        """Get an element or slice of elements from the list.

        Args:
            key:
                Integer index, string name, or slice.

        Returns:
            List element(s).
        """
        # string keys (names)
        if isinstance(key, str):
            if key not in self.names:
                raise KeyError(f"No element named '{key}'.")
            key = list(self.names).index(key)

        # integer indices
        if isinstance(key, int):
            if key < 0:
                key += len(self)
            if key < 0 or key >= len(self):
                raise IndexError(f"List index '{key}' out of range.")

            start, end = self._partitioning.get_partition_range(key)
            return self._extract_range(start, end)

        # slices
        elif isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            result = []
            for i in indices:
                start, end = self._partitioning.get_partition_range(i)
                result.append(self._extract_range(start, end))

            # Create a new CompressedList from the result
            return self.__class__.from_list(
                result, names=[self.names[i] for i in indices] if self.names[0] is not None else None
            )

        else:
            raise TypeError("Index must be int, str, or slice.")

    ##################################
    ######>> abstract methods <<######
    ##################################

    @abstractmethod
    def _extract_range(self, start: int, end: int) -> Any:
        """Extract a range from `unlist_data`.

        This method must be implemented by subclasses to handle
        type-specific extraction from `unlist_data`.

        Args:
            start:
                Start index (inclusive).

            end:
                End index (exclusive).

        Returns:
            Extracted element.
        """
        pass

    @classmethod
    @abstractmethod
    def from_list(
        cls, lst: List[Any], names: Optional[Sequence[str]] = None, metadata: dict = None
    ) -> "CompressedList[Any]":
        """Create a CompressedList from a regular list.

        This method must be implemented by subclasses to handle
        type-specific conversion from list to unlist_data.

        Args:
            lst:
                List to convert.

            names:
                Optional names for list elements.

            metadata:
                Optional metadata.

        Returns:
            A new `CompressedList`.
        """
        pass

    ###########################
    ######>> coercions <<######
    ###########################

    def to_list(self) -> List[Any]:
        """Convert to a regular Python list.

        Returns:
            A regular Python list with all elements.
        """
        return list(self)

    def unlist(self, use_names: bool = True) -> Any:
        """Get the underlying unlisted data.

        Args:
            use_names:
                Whether to include names in the result if applicable.

                Currently not used.

        Returns:
            The unlisted data.
        """
        return self._unlist_data

    def relist(self, unlist_data: Any) -> "CompressedList[Any]":
        """Create a new `CompressedList` with the same partitioning but different data.

        Args:
            unlist_data:
                New unlisted data.

        Returns:
            A new CompressedList.
        """
        _validate_data_and_partitions(unlist_data, self._partitioning)

        return self.__class__(
            unlist_data,
            self._partitioning.copy(),
            element_type=self._element_type,
            element_metadata=self._element_metadata.copy(),
            metadata=self._metadata.copy(),
        )

    def extract_subset(self, indices: Sequence[int]) -> "CompressedList[Any]":
        """Extract a subset of elements by indices.

        Args:
            indices:
                Sequence of indices to extract.

        Returns:
            A new CompressedList with only the selected elements.
        """
        # Validate indices
        for i in indices:
            if i < 0 or i >= len(self):
                raise IndexError(f"Index {i} out of range")

        # Extract element lengths and names
        new_lengths = [self.get_element_lengths()[i] for i in indices]
        new_names = [self.names[i] for i in indices] if self.names[0] is not None else None

        # Create new partitioning
        new_partitioning = Partitioning.from_lengths(new_lengths, new_names)

        # Extract data
        new_data = []
        for i in indices:
            start, end = self._partitioning.get_partition_range(i)
            if isinstance(self._unlist_data, np.ndarray):
                new_data.append(self._unlist_data[start:end])
            else:
                new_data.extend(self._unlist_data[start:end])

        if isinstance(self._unlist_data, np.ndarray):
            new_data = np.concatenate(new_data)

        # Create new compressed list
        return self.__class__(
            new_data,
            new_partitioning,
            element_type=self._element_type,
            element_metadata={k: v for k, v in self._element_metadata.items() if k in indices},
            metadata=self._metadata.copy(),
        )

    def lapply(self, func: Callable) -> "CompressedList[Any]":
        """Apply a function to each element.

        Args:
            func:
                Function to apply to each element.

        Returns:
            A new CompressedList with the results.
        """
        result = [func(elem) for elem in self]
        return self.__class__.from_list(result, self.names, self._metadata)
