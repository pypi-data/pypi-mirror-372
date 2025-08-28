from __future__ import annotations

import os
import stat
from collections.abc import Generator
from pathlib import Path

import pytest
from wexample_helpers.helpers.file import (
    file_change_mode,
    file_change_mode_recursive,
    file_get_directories,
    file_list_subdirectories,
    file_mode_num_to_octal,
    file_mode_octal_to_num,
    file_path_get_mode_num,
    file_path_get_octal_mode,
    file_read,
    file_remove_if_exists,
    file_resolve_path,
    file_touch,
    file_validate_mode_octal,
    file_validate_mode_octal_or_fail,
    file_write,
)


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path]:
    """Fixture providing a temporary directory."""
    yield tmp_path


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path]:
    """Fixture providing a temporary file."""
    file_path = temp_dir / "test.txt"
    file_path.write_text("test content")
    yield file_path


def test_file_change_mode(temp_file: Path) -> None:
    mode = 0o644
    file_change_mode(str(temp_file), mode)
    assert stat.S_IMODE(temp_file.stat().st_mode) == mode

    # Test with non-existent file (should not raise)
    file_change_mode("/non/existent/file", mode)


def test_file_change_mode_recursive(temp_dir: Path) -> None:
    # Create test structure
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "file1.txt").write_text("test1")
    (temp_dir / "file2.txt").write_text("test2")

    mode = 0o755
    file_change_mode_recursive(str(temp_dir), mode)

    assert stat.S_IMODE(subdir.stat().st_mode) == mode
    assert stat.S_IMODE((subdir / "file1.txt").stat().st_mode) == mode
    assert stat.S_IMODE((temp_dir / "file2.txt").stat().st_mode) == mode


def test_file_list_subdirectories(temp_dir: Path) -> None:
    # Create test directories
    (temp_dir / "dir1").mkdir()
    (temp_dir / "dir2").mkdir()
    (temp_dir / ".hidden").mkdir()
    (temp_dir / "file.txt").write_text("test")

    subdirs = file_list_subdirectories(str(temp_dir))
    assert subdirs == ["dir1", "dir2"]


def test_file_mode_conversions() -> None:
    # Test num to octal
    assert file_mode_num_to_octal(0o644) == "644"

    # Test octal to num (string input)
    assert file_mode_octal_to_num("644") == 0o644
    # Test octal to num (int input should be treated as string)
    assert file_mode_octal_to_num(str(644)) == 0o644


def test_file_path_mode_operations(temp_file: Path) -> None:
    os.chmod(temp_file, 0o644)

    assert file_path_get_octal_mode(temp_file) == "644"
    assert file_path_get_mode_num(temp_file) == 0o644


def test_file_read_write(temp_dir: Path) -> None:
    file_path = temp_dir / "test.txt"
    content = "Hello, World!"

    # Test write
    file_write(str(file_path), content)
    assert file_path.read_text() == content

    # Test read
    assert file_read(str(file_path)) == content


def test_file_remove_if_exists(temp_file: Path) -> None:
    assert temp_file.exists()
    file_remove_if_exists(str(temp_file))
    assert not temp_file.exists()

    # Test with non-existent file (should not raise)
    file_remove_if_exists("/non/existent/file")


def test_file_resolve_path() -> None:
    path_str = "/test/path"
    path_obj = Path("/test/path")

    assert file_resolve_path(path_str) == Path(path_str)
    assert file_resolve_path(path_obj) == path_obj


def test_file_touch(temp_dir: Path) -> None:
    file_path = temp_dir / "touch_test.txt"
    file_touch(str(file_path))
    assert file_path.exists()
    assert file_path.stat().st_size == 0


def test_file_validate_mode_octal() -> None:
    assert file_validate_mode_octal("644")
    assert file_validate_mode_octal("755")
    assert not file_validate_mode_octal("999")  # Invalid octal
    assert not file_validate_mode_octal("1234")  # Too long
    assert not file_validate_mode_octal("12")  # Too short


def test_file_validate_mode_octal_or_fail() -> None:
    assert file_validate_mode_octal_or_fail("644")

    with pytest.raises(Exception):
        file_validate_mode_octal_or_fail("999")


def test_file_get_directories(temp_dir: Path) -> None:
    # Create test structure
    dir1 = temp_dir / "dir1"
    dir2 = temp_dir / "dir2"
    subdir = dir1 / "subdir"

    for d in [dir1, dir2, subdir]:
        d.mkdir()

    # Test non-recursive
    dirs = file_get_directories(str(temp_dir))
    assert len(dirs) == 2
    assert all(os.path.basename(d) in ["dir1", "dir2"] for d in dirs)

    # Test recursive
    dirs = file_get_directories(str(temp_dir), recursive=True)
    assert len(dirs) == 3
    assert any("subdir" in d for d in dirs)
