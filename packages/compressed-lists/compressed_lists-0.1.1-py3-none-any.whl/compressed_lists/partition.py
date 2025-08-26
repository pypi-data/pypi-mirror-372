from typing import List, Optional, Sequence, Union
from warnings import warn

import biocutils as ut
import numpy as np

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


def _validate_names(names, expected_len):
    if names is None:
        return

    if len(names) != expected_len:
        raise ValueError("Length of names must match length of ends.")


class Partitioning:
    """Represents partitioning information for a `CompressedList`.

    This is similar to the ``PartitioningByEnd`` class in Bioconductor.
    It keeps track of where each element begins and ends in the unlisted data.
    """

    def __init__(self, ends: Sequence[int], names: Optional[Sequence[str]] = None, validate: bool = True):
        """Initialize a Partitioning object.

        Args:
            ends:
                Sequence of ending positions for each partition (exclusive).

            names:
                Optional names for each partition.

            validate:
                Internal use only.
        """
        self._ends = np.array(ends, dtype=np.int64)

        # Calculate starts from ends
        self._starts = np.zeros_like(self._ends)
        if len(self._ends) > 0:
            self._starts[1:] = self._ends[:-1]

        self._names = None
        if names is not None:
            self._names = ut.NamedList(names)

        if validate:
            _validate_names(names, len(ends))

    @classmethod
    def from_lengths(cls, lengths: Sequence[int], names: Optional[Sequence[str]] = None) -> "Partitioning":
        """Create a Partitioning from a sequence of lengths.

        Args:
            lengths:
                Sequence of partition lengths.

            names:
                Optional names for each partition.

        Returns:
            A new Partitioning object.
        """
        ends = np.cumsum(lengths)
        return cls(ends, names)

    @classmethod
    def from_list(cls, lst: List, names: Optional[Sequence[str]] = None) -> "Partitioning":
        """Create a Partitioning from a list by using the lengths of each element.

        Args:
            lst:
                A list to create partitioning from.

            names:
                Optional names for each partition.

        Returns:
            A new Partitioning object.
        """
        lengths = [len(item) if hasattr(item, "__len__") else 1 for item in lst]
        return cls.from_lengths(lengths, names)

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

        _ends_copy = deepcopy(self._ends)
        _names_copy = deepcopy(self._names)

        current_class_const = type(self)
        return current_class_const(
            ends=_ends_copy,
            names=_names_copy,
        )

    def __copy__(self):
        """
        Returns:
            A shallow copy of the current ``Partitioning``.
        """
        current_class_const = type(self)
        return current_class_const(
            ends=self._ends,
            names=self._names,
        )

    def copy(self):
        """Alias for :py:meth:`~__copy__`."""
        return self.__copy__()

    ######################################
    ######>> length and iterators <<######
    ######################################

    def __len__(self) -> int:
        """Return the number of partitions."""
        return len(self._ends)

    def get_nobj(self) -> int:
        """Return the total number of objects across all partitions."""
        return self._ends[-1] if len(self._ends) > 0 else 0

    def nobj(self) -> int:
        """Alias for :py:attr:`~get_nobj`."""
        return self.get_nobj()

    def get_element_lengths(self) -> np.ndarray:
        """Return the lengths of each partition."""
        return self._ends - self._starts

    def element_lengths(self) -> int:
        """Alias for :py:attr:`~get_element_lengths`."""
        return self.get_element_lengths()

    ##########################
    ######>> Printing <<######
    ##########################

    def __repr__(self) -> str:
        """
        Returns:
            A string representation.
        """
        output = f"{type(self).__name__}(number_of_elements={len(self)}"

        if self._names is not None:
            output += ", names=" + ut.print_truncated_list(self._names)

        output += ")"
        return output

    def __str__(self) -> str:
        """
        Returns:
            A pretty-printed string containing the contents of this object.
        """
        output = f"class: {type(self).__name__}\n"

        output += f"num of elements: ({len(self)})\n"

        output += f"names({0 if self._names is None else len(self._names)}): {' ' if self._names is None else ut.print_truncated_list(self._names)}\n"

        return output

    ##########################
    ######>> accessors <<#####
    ##########################

    def get_partition_range(self, i: int) -> tuple:
        """Get the start and end indices for partition ``i``."""
        if i < 0 or i >= len(self):
            raise IndexError(f"Partition index {i} out of range.")
        return (self._starts[i], self._ends[i])

    def __getitem__(self, key: Union[int, slice]) -> Union[tuple, List[tuple]]:
        """Get partition range(s) by index or slice.

        Args:
            key:
                Integer index or slice.

        Returns:
            Tuple of (start, end) or list of such tuples.
        """
        if isinstance(key, int):
            return self.get_partition_range(key)
        elif isinstance(key, slice):
            indices = range(*key.indices(len(self)))
            return [self.get_partition_range(i) for i in indices]
        else:
            raise TypeError("Index must be 'int' or 'slice'.")

    ######################
    ######>> names <<#####
    ######################

    def get_names(self) -> Optional[ut.NamedList]:
        """Return the names of each partition."""
        return self._names

    def set_names(self, names: Optional[List[str]], in_place: bool = False) -> "Partitioning":
        """Set the names of list elements.

        Args:
            names:
                New names, same as the number of elements.

                May be `None` to remove row names.

            in_place:
                Whether to modify the ``Partitioning`` in place.

        Returns:
            A modified ``Partitioning`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if names is not None and not isinstance(names, ut.Names):
            names = ut.Names(names)

        _validate_names(names, len(self._ends))

        output = self._define_output(in_place)
        output._names = names
        return output

    @property
    def names(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_names`, provided for back-compatibility."""
        return self.get_names()

    @names.setter
    def names(self, names: Optional[List[str]]):
        """Alias for :py:meth:`~set_names` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'row_names' is an in-place operation, use 'set_names' instead",
            UserWarning,
        )
        self.set_names(names, in_place=True)

    #####################
    ######>> ends <<#####
    #####################

    def get_ends(self) -> Optional[ut.NamedList]:
        """Return the names of each partition."""
        return self._ends

    @property
    def ends(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_ends`, provided for back-compatibility."""
        return self.get_ends()

    #######################
    ######>> starts <<#####
    #######################

    def get_starts(self) -> Optional[ut.NamedList]:
        """Return the starts of each partition."""
        return self._starts

    @property
    def starts(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_starts`, provided for back-compatibility."""
        return self.get_starts()
