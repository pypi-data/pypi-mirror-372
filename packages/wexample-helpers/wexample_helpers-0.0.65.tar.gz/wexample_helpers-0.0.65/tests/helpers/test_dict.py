from __future__ import annotations

from wexample_helpers.helpers.dict import (
    dict_get_first_missing_key,
    dict_get_item_by_path,
    dict_has_item_by_path,
    dict_merge,
    dict_remove_item_by_path,
    dict_set_item_by_path,
    dict_sort_values,
)


def test_dict_get_item_by_path() -> None:
    data = {"a": {"b": {"c": 1}}}
    assert dict_get_item_by_path(data, "a.b.c") == 1
    assert dict_get_item_by_path(data, "a.b.d") is None
    assert dict_get_item_by_path(data, "x.y", default=42) == 42


def test_dict_has_item_by_path() -> None:
    data = {"a": {"b": {"c": 1}}}
    assert dict_has_item_by_path(data, "a.b.c") is True
    assert dict_has_item_by_path(data, "a.b.d") is False
    assert dict_has_item_by_path(data, "x.y") is False


def test_dict_merge() -> None:
    dict1 = {"a": 1, "b": {"c": 2}}
    dict2 = {"b": {"d": 3}, "e": 4}
    merged = dict_merge(dict1, dict2)
    assert merged == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}


def test_dict_remove_item_by_path() -> None:
    data = {"a": {"b": {"c": 1, "d": 2}}}
    dict_remove_item_by_path(data, "a.b.c")
    assert data == {"a": {"b": {"d": 2}}}

    # Test removing non-existent path
    dict_remove_item_by_path(data, "x.y.z")
    assert data == {"a": {"b": {"d": 2}}}


def test_dict_set_item_by_path() -> None:
    data = {}
    dict_set_item_by_path(data, "a.b.c", 1)
    assert data == {"a": {"b": {"c": 1}}}

    # Test merge behavior
    dict_set_item_by_path(data, "a.b", {"d": 2}, when_exist="merge")
    assert data == {"a": {"b": {"c": 1, "d": 2}}}


def test_dict_sort_values() -> None:
    data = {"c": 3, "a": 1, "b": 2}
    sorted_dict = dict_sort_values(data)
    assert list(sorted_dict.items()) == [("a", 1), ("b", 2), ("c", 3)]


def test_dict_get_first_missing_key() -> None:
    data = {"a": 1, "b": 2}
    assert dict_get_first_missing_key(data, ["a", "b", "c"]) == "c"
    assert dict_get_first_missing_key(data, ["a", "b"]) is None
