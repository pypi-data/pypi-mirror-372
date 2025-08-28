from __future__ import annotations

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.testing.classes.pydantic_inheritance_main import (
    PydanticInheritanceMain,
)


def test_pydantic_inheritance() -> None:
    # Create instance with various properties
    instance = PydanticInheritanceMain(
        environment="production",
        name="test_instance",
        tags=["test", "debug"],
        description="A test instance",
        enabled=True,
        priority=50,
    )

    # Test public fields
    assert instance.name == "test_instance"
    assert instance.tags == ["test", "debug"]
    assert instance.description == "A test instance"
    assert instance.version == "1.0.0"  # Overridden from BaseMixin
    assert instance.enabled is True
    assert instance.priority == 50

    # Test environment from config
    assert instance.environment == "production"

    # Test private fields
    assert instance.created_at is not None
    metadata = instance.get_metadata()
    assert isinstance(metadata, dict)

    # Add some metadata and verify
    instance.set_metadata("custom_key", "custom_value")
    updated_metadata = instance.get_metadata()
    assert updated_metadata["custom_key"] == "custom_value"

    # Debug dump the instance
    print("\nInstance Debug:")
    dump = DebugDump(instance)
    dump.execute()
