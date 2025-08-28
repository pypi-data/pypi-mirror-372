from __future__ import annotations

from datetime import datetime

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.testing.classes.pydantic_advanced import PydanticAdvanced, Status


def test_pydantic_advanced() -> None:
    # Create an instance with various data types
    instance = PydanticAdvanced(
        id="test123",
        status=Status.ACTIVE,
        _secret_key="super_secret",
        score=99.999,  # Will be rounded to 100.00
        metadata={"version": "1.0", "enabled": True, "priority": 1},
    )

    # Add some notes
    instance.notes = ["Note 1  ", "  Note 2  "]  # Will be stripped

    # Force creation time for consistent test
    instance._created_at = datetime(2025, 3, 5, 15, 30)

    # Dump the instance
    dump = DebugDump(instance)
    dump.execute()
