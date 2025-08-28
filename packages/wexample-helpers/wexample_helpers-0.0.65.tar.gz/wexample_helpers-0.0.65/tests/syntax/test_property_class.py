from __future__ import annotations

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.testing.classes.property_class import PropertyClass


def test_property_class() -> None:
    # Create instance
    instance = PropertyClass()

    # Set value through property
    instance.value = "test"

    # Dump the instance
    dump = DebugDump(instance)
    dump.execute()
