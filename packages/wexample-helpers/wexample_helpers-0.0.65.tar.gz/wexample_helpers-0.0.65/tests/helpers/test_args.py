from __future__ import annotations

from wexample_helpers.helpers.args import (
    args_convert_dict_to_snake_dict,
    args_in_function,
    args_is_basic_value,
    args_parse_dict,
    args_parse_list,
    args_parse_list_or_strings_list,
    args_parse_one,
    args_push_one,
    args_replace_one,
    args_shift_one,
    args_split_arg_array,
)


def test_args_replace_one() -> None:
    args = ["--test", "value", "--other", "data"]
    result = args_replace_one(args, "test", "new_value")
    assert result == "value"
    assert args == ["--other", "data", "--test", "new_value"]


def test_args_push_one() -> None:
    args = []
    args_push_one(args, "test", "value")
    assert args == ["--test", "value"]

    args_push_one(args, "flag")
    assert args == ["--test", "value", "--flag"]


def test_args_shift_one() -> None:
    args = ["--test", "value", "--flag"]

    # Test value argument
    result = args_shift_one(args, "test")
    assert result == "value"
    assert args == ["--flag"]

    # Test flag argument
    result = args_shift_one(args, "flag", is_flag=True)
    assert result is True
    assert args == []


def test_args_split_arg_array() -> None:
    # Test string input
    assert args_split_arg_array("a,b,c") == ["a", "b", "c"]
    assert args_split_arg_array("[a, b, c]") == ["a", "b", "c"]
    assert args_split_arg_array("") == []

    # Test iterable input
    assert args_split_arg_array(["a", "b", "c"]) == ["a", "b", "c"]


def test_args_convert_dict_to_snake_dict() -> None:
    input_dict = {"camelCase": 1, "PascalCase": 2}
    result = args_convert_dict_to_snake_dict(input_dict)
    assert result == {"camel_case": 1, "pascal_case": 2}


def test_args_parse_dict() -> None:
    assert args_parse_dict('{"key": "value"}') == {"key": "value"}
    assert args_parse_dict("invalid") == {}


def test_args_parse_list_or_strings_list() -> None:
    assert args_parse_list_or_strings_list("[1, 2, 3]") == [1, 2, 3]
    assert args_parse_list_or_strings_list("a b c") == ["a", "b", "c"]


def test_args_parse_list() -> None:
    assert args_parse_list("[1, 2, 3]") == [1, 2, 3]
    assert args_parse_list("[a, b, c]") == []  # Invalid list returns empty


def test_args_parse_one() -> None:
    assert args_parse_one("123") == 123
    assert args_parse_one("true") == "true"  # String, not boolean
    assert args_parse_one('{"key": "value"}') == {"key": "value"}
    assert args_parse_one("") is None


def test_args_is_basic_value() -> None:
    # Test simple types
    assert args_is_basic_value("string") is True
    assert args_is_basic_value(123) is True
    assert args_is_basic_value(True) is True
    assert args_is_basic_value(None) is True

    # Test collections
    assert args_is_basic_value([1, "2", True]) is True
    assert args_is_basic_value({"key": "value"}) is True
    assert args_is_basic_value([{"key": [1, 2]}]) is True

    # Test non-basic values
    class TestClass:
        pass

    assert args_is_basic_value(TestClass()) is False


def test_args_in_function() -> None:
    def test_func(arg1, arg2=None) -> None:
        pass

    assert args_in_function(test_func, "arg1") is True
    assert args_in_function(test_func, "arg2") is True
    assert args_in_function(test_func, "arg3") is False
