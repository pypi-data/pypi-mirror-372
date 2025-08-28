from __future__ import annotations

from wexample_helpers.helpers.polyfill import polyfill_register_global


def test_polyfill_register_global() -> None:
    # Test that the function accepts any type of argument without raising exceptions
    class DummyClass:
        pass

    # Test with various types of arguments
    polyfill_register_global(DummyClass)
    polyfill_register_global([DummyClass, DummyClass])

    # Test with multiple classes
    class Class1:
        pass

    class Class2:
        pass

    polyfill_register_global([Class1, Class2])

    # The function should always return None
    assert polyfill_register_global(DummyClass) is None
