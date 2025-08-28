from __future__ import annotations

import os
import re
import sys

# Ensure local helpers are importable
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
HELPERS_PATH = os.path.join(PROJECT_ROOT, "pip", "helpers")
sys.path.insert(0, HELPERS_PATH)

from wexample_helpers.enums.debug_path_style import (  # type: ignore  # noqa: E402
    DebugPathStyle,
)
from wexample_helpers.helpers.error import error_format  # type: ignore  # noqa: E402


def _raise_nested() -> None:
    def inner() -> None:
        raise ValueError("boom")

    def middle() -> None:
        inner()

    middle()


def test_error_format_contains_exception_and_frames() -> None:
    try:
        _raise_nested()
    except Exception as e:  # noqa: PIE786
        out = error_format(e, path_style=DebugPathStyle.FULL)
    # Strip ANSI CSI and OSC 8 hyperlinks that may wrap the file path
    ansi_csi = re.compile(r"\x1B\[[0-9;]*[A-Za-z]")
    osc8 = re.compile(r"\x1B\]8;;.*?\x1B\\")
    out_clean = ansi_csi.sub("", osc8.sub("", out))

    # Should end with the exception message
    assert out.strip().endswith("ValueError: boom")

    # Should contain at least one formatted frame header
    assert "File     :" in out_clean
    assert "Function :" in out_clean

    # Contains this test function name
    assert "test_error_format_contains_exception_and_frames" in out_clean

    # Contains path with a colon and line number pattern
    assert re.search(r":\d+\nLine\s+:\s+\d+", out_clean) is not None
