from __future__ import annotations

from datetime import datetime

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.testing.classes.pydantic_class import PydanticClass


def test_pydantic_class() -> None:
    # Create instance with some data
    instance = PydanticClass(
        name="test_item",
        count=42,
        description="A test item",
        tags=["test", "debug"],
        created_at=datetime(2025, 3, 5, 15, 46),
    )

    # Dump the instance
    dump = DebugDump(instance)
    dump.execute()
