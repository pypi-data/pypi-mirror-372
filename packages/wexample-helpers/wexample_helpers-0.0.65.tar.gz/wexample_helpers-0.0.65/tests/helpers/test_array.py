from __future__ import annotations

from wexample_helpers.helpers.array import array_replace_value, array_swap, array_unique


def test_array_replace_value() -> None:
    # Test with numbers
    assert array_replace_value([1, 2, 1, 3], 1, 4) == [4, 2, 4, 3]

    # Test with strings
    assert array_replace_value(["a", "b", "a"], "a", "c") == ["c", "b", "c"]


def test_array_swap() -> None:
    # Test with numbers
    array = [1, 2]
    assert array_swap(array, False) == [1, 2]
    assert array_swap(array, True) == [2, 1]

    # Test with strings
    array = ["a", "b"]
    assert array_swap(array, True) == ["b", "a"]


def test_array_unique() -> None:
    # Test with numbers
    assert sorted(array_unique([1, 2, 2, 3, 1])) == [1, 2, 3]

    # Test with strings
    assert sorted(array_unique(["a", "b", "a", "c"])) == ["a", "b", "c"]
