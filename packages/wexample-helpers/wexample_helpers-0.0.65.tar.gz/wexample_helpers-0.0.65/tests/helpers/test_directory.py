from __future__ import annotations

import os
import shutil
import tempfile

import pytest
from wexample_helpers.helpers.directory import (
    directory_aggregate_all_files,
    directory_aggregate_all_files_from_dir,
    directory_empty_dir,
    directory_execute_inside,
    directory_get_base_name,
    directory_get_parent_path,
    directory_list_files,
    directory_remove_tree_if_exists,
)


@pytest.fixture
def temp_dir() -> None:
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_directory_remove_tree_if_exists(temp_dir) -> None:
    # Create a test file in the temp directory
    test_file = os.path.join(temp_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")

    assert os.path.exists(temp_dir)
    directory_remove_tree_if_exists(temp_dir)
    assert not os.path.exists(temp_dir)

    # Test removing non-existent directory
    directory_remove_tree_if_exists("/non/existent/path")


def test_directory_execute_inside(temp_dir) -> None:
    original_dir = os.getcwd()

    with directory_execute_inside(temp_dir):
        assert os.getcwd() == temp_dir
    assert os.getcwd() == original_dir


def test_directory_get_base_name() -> None:
    assert directory_get_base_name("/path/to/dir/") == "dir"
    assert directory_get_base_name("/path/to/dir") == "dir"
    assert directory_get_base_name("dir") == "dir"


def test_directory_get_parent_path() -> None:
    assert directory_get_parent_path("/path/to/dir/") == "/path/to/"
    assert directory_get_parent_path("/path/to/dir") == "/path/to/"
    assert (
        directory_get_parent_path("/path/") == "//"
    )  # La fonction ajoute toujours os.sep à la fin


def test_directory_empty_dir(temp_dir) -> None:
    # Create test files and subdirectories
    test_file = os.path.join(temp_dir, "test.txt")
    test_subdir = os.path.join(temp_dir, "subdir")
    test_subfile = os.path.join(test_subdir, "subfile.txt")

    os.makedirs(test_subdir)
    with open(test_file, "w") as f:
        f.write("test")
    with open(test_subfile, "w") as f:
        f.write("subtest")

    directory_empty_dir(temp_dir)
    assert os.path.exists(temp_dir)
    assert len(os.listdir(temp_dir)) == 0


def test_directory_list_files(temp_dir) -> None:
    # Create test files in different subdirectories
    os.makedirs(os.path.join(temp_dir, "dir1"))
    os.makedirs(os.path.join(temp_dir, "dir2"))

    files = [
        os.path.join(temp_dir, "file1.txt"),
        os.path.join(temp_dir, "dir1", "file2.txt"),
        os.path.join(temp_dir, "dir2", "file3.txt"),
    ]

    for file_path in files:
        with open(file_path, "w") as f:
            f.write(f"content of {os.path.basename(file_path)}")

    listed_files = directory_list_files(temp_dir)
    assert len(listed_files) == 3
    assert all(os.path.isfile(f) for f in listed_files)
    assert sorted([os.path.basename(f) for f in listed_files]) == [
        "file1.txt",
        "file2.txt",
        "file3.txt",
    ]


def test_directory_aggregate_all_files(temp_dir) -> None:
    # Create test files with known content
    files = [
        (os.path.join(temp_dir, "file1.txt"), "content1\n"),
        (os.path.join(temp_dir, "file2.txt"), "content2\n"),
    ]

    for file_path, content in files:
        with open(file_path, "w") as f:
            f.write(content)

    file_paths = [f[0] for f in files]
    aggregated = directory_aggregate_all_files(file_paths)

    expected_content = "content1\n\ncontent2\n"
    assert aggregated == expected_content


def test_directory_aggregate_all_files_from_dir(temp_dir) -> None:
    # Create test files with known content
    files = [
        (os.path.join(temp_dir, "file1.txt"), "content1\n"),
        (os.path.join(temp_dir, "file2.txt"), "content2\n"),
    ]

    for file_path, content in files:
        with open(file_path, "w") as f:
            f.write(content)

    aggregated = directory_aggregate_all_files_from_dir(temp_dir)
    expected_content = "content1\n\ncontent2\n"
    assert aggregated == expected_content
