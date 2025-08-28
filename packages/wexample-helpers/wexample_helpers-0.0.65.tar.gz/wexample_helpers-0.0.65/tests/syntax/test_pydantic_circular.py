from __future__ import annotations

from wexample_helpers.common.debug.debug_dump import DebugDump
from wexample_helpers.testing.classes.pydantic_circular_advanced_kernel import (
    AdvancedKernel,
)
from wexample_helpers.testing.classes.pydantic_circular_base_kernel import BaseKernel


def _test_kernel_service(kernel_class: type, kernel_name: str):
    """Test kernel and service circular reference."""
    # Create a kernel which will automatically create its service
    kernel = kernel_class(name=kernel_name, debug=True)

    # Verify circular reference
    assert kernel.service.kernel == kernel
    assert kernel.service.name == f"{kernel_name}_service"

    # Debug dump both objects
    print(f"\n{kernel.__class__.__name__} Debug:")
    kernel_dump = DebugDump(kernel)
    kernel_dump.execute()

    print(f"\n{kernel.service.__class__.__name__} Debug:")
    service_dump = DebugDump(kernel.service)
    service_dump.execute()

    return kernel


def test_pydantic_circular() -> None:
    """Test basic kernel circular reference."""
    _test_kernel_service(BaseKernel, "test_kernel")


def test_pydantic_circular_advanced() -> None:
    """Test advanced kernel with inheritance."""
    kernel = _test_kernel_service(AdvancedKernel, "advanced_kernel")

    # Additional advanced checks
    assert isinstance(kernel, AdvancedKernel)
    assert kernel.version == "1.0.0"
    assert kernel.service.mode == "advanced"
    assert kernel.service.base_kernel == kernel  # Test base type access
    assert kernel.service.advanced_kernel == kernel  # Test advanced type access
