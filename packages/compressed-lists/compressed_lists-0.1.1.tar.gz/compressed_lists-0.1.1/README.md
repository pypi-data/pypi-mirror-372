[![PyPI-Server](https://img.shields.io/pypi/v/compressed-lists.svg)](https://pypi.org/project/compressed-lists/)
![Unit tests](https://github.com/BiocPy/compressed-lists/actions/workflows/run-tests.yml/badge.svg)

# CompressedList Implementation in Python

A Python implementation of the `CompressedList` class from R/Bioconductor for memory-efficient list-like objects.

`CompressedList` is a memory-efficient container for list-like objects. Instead of storing each list element separately, it concatenates all elements into a single vector-like object and maintains information about where each original element begins and ends. This approach is significantly more memory-efficient than standard lists, especially when dealing with many list elements.

## Install

To get started, install the package from [PyPI](https://pypi.org/project/compressed-lists/)

```bash
pip install compressed-lists
```

## Usage


```py
from compressed_lists import CompressedIntegerList, CompressedStringList

# Create a CompressedIntegerList
int_data = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
names = ["A", "B", "C"]
int_list = CompressedIntegerList.from_list(int_data, names)

# Access elements
print(int_list[0])      # [1, 2, 3]
print(int_list["B"])    # [4, 5]
print(int_list[1:3])    # Slice of elements

# Apply a function to each element
squared = int_list.lapply(lambda x: [i**2 for i in x])
print(squared[0])       # [1, 4, 9]

# Convert to a regular Python list
regular_list = int_list.to_list()

# Create a CompressedStringList
char_data = [["apple", "banana"], ["cherry", "date", "elderberry"], ["fig"]]
char_list = CompressedStringList.from_list(char_data)
```

### Partitioning

The `Partitioning` class handles the information about where each element begins and ends in the concatenated data. It allows for efficient extraction of elements without storing each element separately.

```python
from compressed_lists import Partitioning

# Create partitioning from end positions
ends = [3, 5, 10]
names = ["A", "B", "C"]
part = Partitioning(ends, names)

# Get partition range for an element
start, end = part[1]  # Returns (3, 5)
```

> [!NOTE]
>
> Check out the [documentation](https://biocpy.github.io/compressed-lists) for extending CompressedLists to custom data types.

<!-- biocsetup-notes -->

## Note

This project has been set up using [BiocSetup](https://github.com/biocpy/biocsetup)
and [PyScaffold](https://pyscaffold.org/).
