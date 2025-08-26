---
file_format: mystnb
kernelspec:
  name: python
---

# Basic Usage

```{code-cell}
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

## Partitioning

The `Partitioning` class handles the information about where each element begins and ends in the concatenated data. It allows for efficient extraction of elements without storing each element separately.

```{code-cell}
from compressed_lists import Partitioning

# Create partitioning from end positions
ends = [3, 5, 10]
names = ["A", "B", "C"]
part = Partitioning(ends, names)

# Get partition range for an element
start, end = part[1]
print(start, end)
```

# Creating Custom CompressedList Subclasses

`CompressedList` can be easily it can be extended to support custom data types. Here's a step-by-step guide to creating your own `CompressedList` subclass:

## 1. Subclass CompressedList

Create a new class that inherits from `CompressedList` with appropriate type annotations:

```python
from typing import List, TypeVar, Generic
from compressed_lists import CompressedList, Partitioning
import numpy as np

class CustomCompressedList(CompressedList):
    """A custom CompressedList for your data type."""
    pass
```

## 2. Implement the Constructor

The constructor should initialize the superclass with the appropriate data:

```python
def __init__(self,
             unlist_data: Any,  # Replace with your data type
             partitioning: Partitioning,
             element_metadata: dict = None,
             metadata: dict = None):
    super().__init__(unlist_data, partitioning,
                    element_type="custom_type",  # Set your element type
                    element_metadata=element_metadata,
                    metadata=metadata)
```

## 3. Implement _extract_range Method

This method defines how to extract a range of elements from your unlisted data:

```python
def _extract_range(self, start: int, end: int) -> List[T]:
    """Extract a range from unlisted data."""
    # For example, with numpy arrays:
    return self.unlist_data[start:end].tolist()

    # Or for other data types:
    # return self.unlist_data[start:end]
```

## 4. Implement from_list Class Method

This factory method creates a new instance from a list:

```python
@classmethod
def from_list(cls, lst: List[List[T]], names: list = None,
             metadata: dict = None) -> 'CustomCompressedList':
    """Create a new CustomCompressedList from a list."""
    # Flatten the list
    flat_data = []
    for sublist in lst:
        flat_data.extend(sublist)

    # Create partitioning
    partitioning = Partitioning.from_list(lst, names)

    # Create unlisted data in your preferred format
    # For example, with numpy:
    unlist_data = np.array(flat_data, dtype=np.float64)

    return cls(unlist_data, partitioning, metadata=metadata)
```

## Complete Example: CompressedFloatList

Here's a complete example of a custom CompressedList for floating-point numbers:

```{code-cell}
import numpy as np
from compressed_lists import CompressedList, Partitioning
from typing import List

class CompressedFloatList(CompressedList):
    def __init__(self,
                unlist_data: np.ndarray,
                partitioning: Partitioning,
                element_metadata: dict = None,
                metadata: dict = None):
        super().__init__(unlist_data, partitioning,
                        element_type="float",
                        element_metadata=element_metadata,
                        metadata=metadata)

    def _extract_range(self, start: int, end: int) -> List[float]:
        return self.unlist_data[start:end].tolist()

    @classmethod
    def from_list(cls, lst: List[List[float]], names: list = None,
                 metadata: dict = None) -> 'CompressedFloatList':
        # Flatten the list
        flat_data = []
        for sublist in lst:
            flat_data.extend(sublist)

        # Create partitioning
        partitioning = Partitioning.from_list(lst, names)

        # Create unlist_data
        unlist_data = np.array(flat_data, dtype=np.float64)

        return cls(unlist_data, partitioning, metadata=metadata)

# Usage
float_data = [[1.1, 2.2, 3.3], [4.4, 5.5], [6.6, 7.7, 8.8, 9.9]]
float_list = CompressedFloatList.from_list(float_data, names=["X", "Y", "Z"])
print(float_list["Y"])
```

## For More Complex Data Types

For more complex data types, you would follow the same pattern but customize the storage and extraction methods to suit your data.

For example, with a custom object:

```python
class MyObject:
    def __init__(self, value):
        self.value = value

class CompressedMyObjectList(CompressedList[List[MyObject]]):
    # Implementation details...

    def _extract_range(self, start: int, end: int) -> List[MyObject]:
        return self.unlist_data[start:end]

    @classmethod
    def from_list(cls, lst: List[List[MyObject]], ...):
        # Custom flattening and storage logic
        # ...
```
