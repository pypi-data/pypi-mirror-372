from __future__ import annotations

from wexample_helpers.helpers.string import string_to_kebab_case, string_to_snake_case


def test_string_to_kebab_case() -> None:
    # Test camelCase to kebab-case
    assert string_to_kebab_case("camelCase") == "camel-case"

    # Test PascalCase to kebab-case
    assert string_to_kebab_case("PascalCase") == "pascal-case"

    # Test with spaces
    assert string_to_kebab_case("hello world") == "hello-world"

    # Test with underscores
    assert string_to_kebab_case("hello_world") == "hello-world"

    # Test with multiple spaces/underscores
    assert string_to_kebab_case("hello__world  test") == "hello-world-test"

    # Test with mixed cases and separators
    assert (
        string_to_kebab_case("HelloWorld_testCase spaces")
        == "hello-world-test-case-spaces"
    )

    # Test with empty string
    assert string_to_kebab_case("") == ""

    # Test single word
    assert string_to_kebab_case("test") == "test"


def test_string_to_snake_case() -> None:
    # Test camelCase to snake_case
    assert string_to_snake_case("camelCase") == "camel_case"

    # Test PascalCase to snake_case
    assert string_to_snake_case("PascalCase") == "pascal_case"

    # Test with spaces
    assert string_to_snake_case("hello world") == "hello_world"

    # Test with existing underscores
    assert string_to_snake_case("hello_world") == "hello_world"

    # Test with multiple spaces
    assert string_to_snake_case("hello  world") == "hello_world"

    # Test with mixed cases and separators
    assert (
        string_to_snake_case("HelloWorld testCase-mixed")
        == "hello_world_test_case_mixed"
    )

    # Test with numbers
    assert string_to_snake_case("hello123World") == "hello123_world"
    assert string_to_snake_case("123World") == "123_world"

    # Test with empty string
    assert string_to_snake_case("") == ""

    # Test single word
    assert string_to_snake_case("test") == "test"

    # Test with special characters
    assert string_to_snake_case("hello!world") == "hello_world"
    assert string_to_snake_case("hello-world") == "hello_world"
