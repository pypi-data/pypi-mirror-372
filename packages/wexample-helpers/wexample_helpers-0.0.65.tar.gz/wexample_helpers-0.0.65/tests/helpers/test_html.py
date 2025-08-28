from __future__ import annotations

from wexample_helpers.helpers.html import html_remove_tags, html_split_prompt_parts


def test_html_remove_tags() -> None:
    # Test basic HTML tag removal
    assert html_remove_tags("<p>Hello</p>") == "Hello"

    # Test nested tags
    assert html_remove_tags("<div><p>Hello</p></div>") == "Hello"

    # Test with attributes
    assert html_remove_tags('<div class="test">Hello</div>') == "Hello"

    # Test with multiple tags and text
    assert html_remove_tags("<p>Hello</p><div>World</div>") == "HelloWorld"

    # Test with self-closing tags
    assert html_remove_tags("<p>Hello<br/>World</p>") == "HelloWorld"

    # Test with empty string
    assert html_remove_tags("") == ""

    # Test with no tags
    assert html_remove_tags("Hello World") == "Hello World"


def test_html_split_prompt_parts() -> None:
    # Test basic split - should keep HTML with adjacent text
    assert html_split_prompt_parts("Hello <b>World</b>") == ["Hello <b>World</b>"]

    # Test multiple tags - should keep each tag with its adjacent text
    assert html_split_prompt_parts("Hello <b>World</b> and <i>Universe</i>") == [
        "Hello <b>World</b>",
        " and <i>Universe</i>",
    ]

    # Test nested tags (should keep them together with surrounding text)
    assert html_split_prompt_parts("Start <div><p>Nested</p></div> End") == [
        "Start <div><p>Nested</p></div> End"
    ]

    # Test empty string
    assert html_split_prompt_parts("") == []

    # Test string with no tags
    assert html_split_prompt_parts("Hello World") == ["Hello World"]

    # Test with attributes
    assert html_split_prompt_parts('Hello <div class="test">World</div>') == [
        'Hello <div class="test">World</div>'
    ]
