import numpy as np
import pytest

from compressed_lists import CompressedIntegerList, Partitioning

__author__ = "Jayaram Kancherla"
__copyright__ = "Jayaram Kancherla"
__license__ = "MIT"


@pytest.fixture
def int_data():
    return [[1, 2, 3], [4, 5], [6, 7, 8, 9]]


@pytest.fixture
def int_list(int_data):
    names = ["A", "B", "C"]
    return CompressedIntegerList.from_list(int_data, names)


def test_creation(int_data):
    int_list = CompressedIntegerList.from_list(int_data)

    assert len(int_list) == 3
    assert isinstance(int_list.unlist_data, np.ndarray)
    assert list(int_list.get_unlist_data()) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(int_list.get_element_lengths()) == [3, 2, 4]


def test_creation_from_parts():
    int_list = CompressedIntegerList(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9]), Partitioning(ends=[3, 5, 9]))

    assert len(int_list) == 3
    assert isinstance(int_list.unlist_data, np.ndarray)
    assert list(int_list.get_unlist_data()) == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert list(int_list.get_element_lengths()) == [3, 2, 4]


def test_creation_with_names(int_data):
    names = ["A", "B", "C"]
    int_list = CompressedIntegerList.from_list(int_data, names)

    assert list(int_list.names) == names


def test_validation():
    data = np.array([1, 2, 3, 4, 5])
    partitioning = Partitioning([2, 4, 7])

    with pytest.raises(ValueError):
        CompressedIntegerList(data, partitioning)


def test_getitem_by_index(int_list):
    assert np.allclose(int_list[0], [1, 2, 3])
    assert np.allclose(int_list[1], [4, 5])
    assert np.allclose(int_list[2], [6, 7, 8, 9])

    assert np.allclose(int_list[-1], [6, 7, 8, 9])

    with pytest.raises(IndexError):
        int_list[3]


def test_getitem_by_name(int_list):
    assert np.allclose(int_list["A"], [1, 2, 3])
    assert np.allclose(int_list["B"], [4, 5])
    assert np.allclose(int_list["C"], [6, 7, 8, 9])

    with pytest.raises(KeyError):
        int_list["D"]


def test_getitem_by_slice(int_list):
    sliced = int_list[1:3]

    assert len(sliced) == 2
    assert np.allclose(sliced[0], [4, 5])
    assert np.allclose(sliced[1], [6, 7, 8, 9])
    assert list(sliced.names) == ["B", "C"]

    # Empty slice
    empty = int_list[3:4]
    assert len(empty) == 0


def test_iteration(int_list, int_data):
    items = list(int_list)
    print(items, int_data)
    for i, lst in enumerate(items):
        assert np.allclose(lst, int_data[i])


def test_to_list(int_list, int_data):
    regular_list = int_list.to_list()
    for i, lst in enumerate(regular_list):
        assert np.allclose(lst, int_data[i])


def test_unlist(int_list):
    unlisted = int_list.unlist()
    assert isinstance(unlisted, np.ndarray)
    assert np.allclose(list(unlisted), [1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_relist(int_list):
    new_data = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90], dtype=np.int64)
    relisted = int_list.relist(new_data)

    assert len(relisted) == len(int_list)
    assert list(relisted.get_names()) == list(int_list.names)
    assert np.allclose(relisted[0], [10, 20, 30])
    assert np.allclose(relisted[1], [40, 50])
    assert np.allclose(relisted[2], [60, 70, 80, 90])

    with pytest.raises(ValueError):
        int_list.relist(np.array([1, 2, 3]))


def test_extract_subset(int_list):
    subset = int_list.extract_subset([0, 2])

    assert len(subset) == 2
    assert np.allclose(subset[0], [1, 2, 3])
    assert np.allclose(subset[1], [6, 7, 8, 9])
    assert list(subset.names) == ["A", "C"]

    with pytest.raises(IndexError):
        int_list.extract_subset([0, 3])


def test_lapply(int_list):
    squared = int_list.lapply(lambda x: [i**2 for i in x])

    assert len(squared) == len(int_list)
    assert np.allclose(squared[0], [1, 4, 9])
    assert np.allclose(squared[1], [16, 25])
    assert np.allclose(squared[2], [36, 49, 64, 81])
