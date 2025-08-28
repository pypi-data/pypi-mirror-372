from __future__ import annotations

import json

from wexample_helpers.helpers.json import (
    json_load,
    json_load_if_valid,
    json_parse_if_valid,
)


def test_json_parse_if_valid() -> None:
    # Test valid JSON string
    assert json_parse_if_valid('{"key": "value"}') == {"key": "value"}
    assert json_parse_if_valid("[1, 2, 3]") == [1, 2, 3]

    # Test invalid JSON string
    assert json_parse_if_valid("{invalid}") is False
    assert json_parse_if_valid("[1, 2,]") is False

    # Test empty string
    assert json_parse_if_valid("") is False

    # Test complex nested structure
    complex_json = '{"array": [1, 2, {"nested": "value"}], "number": 42}'
    expected = {"array": [1, 2, {"nested": "value"}], "number": 42}
    assert json_parse_if_valid(complex_json) == expected


def test_json_load_if_valid(tmp_path) -> None:
    # Create test files
    valid_json_file = tmp_path / "valid.json"
    invalid_json_file = tmp_path / "invalid.json"
    nonexistent_file = tmp_path / "nonexistent.json"

    # Write valid JSON
    valid_json_file.write_text('{"test": "data"}')
    # Write invalid JSON
    invalid_json_file.write_text("{invalid}")

    # Test valid JSON file
    assert json_load_if_valid(str(valid_json_file)) == {"test": "data"}

    # Test invalid JSON file
    assert json_load_if_valid(str(invalid_json_file)) is False

    # Test nonexistent file
    assert json_load_if_valid(str(nonexistent_file)) is False


def test_json_load(tmp_path) -> None:
    # Create test file
    test_file = tmp_path / "test.json"
    test_data = {
        "string": "value",
        "number": 42,
        "array": [1, 2, 3],
        "nested": {"key": "value"},
    }

    # Write test data
    test_file.write_text(json.dumps(test_data))

    # Test loading
    loaded_data = json_load(str(test_file))
    assert loaded_data == test_data

    # Test loading array
    array_file = tmp_path / "array.json"
    array_data = [1, 2, {"key": "value"}]
    array_file.write_text(json.dumps(array_data))

    loaded_array = json_load(str(array_file))
    assert loaded_array == array_data
