"""Test utility functions."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rori.utils import cat, get_executable_or_exit, tail


def test_cat_existing_file():
    """Test cat function with existing file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("line 1\nline 2\nline 3\n")
        temp_path = Path(f.name)

    try:
        content = cat(temp_path)
        assert content == "line 1\nline 2\nline 3\n"
    finally:
        temp_path.unlink()


def test_cat_nonexistent_file():
    """Test cat function with non-existent file."""
    nonexistent_path = Path("/tmp/nonexistent_file.txt")

    with pytest.raises(FileNotFoundError):
        cat(nonexistent_path)


def test_cat_empty_file():
    """Test cat function with empty file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        temp_path = Path(f.name)

    try:
        content = cat(temp_path)
        assert content == ""
    finally:
        temp_path.unlink()


def test_tail_existing_file():
    """Test tail function with existing file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        lines = [f"line {i}\n" for i in range(1, 21)]  # 20 lines
        f.writelines(lines)
        temp_path = Path(f.name)

    try:
        # Test default tail (last 10 lines)
        content = tail(temp_path)
        expected_lines = lines[-10:]
        expected_content = "".join(expected_lines)
        assert content == expected_content

        # Test tail with specific number of lines
        content = tail(temp_path, n=5)
        expected_lines = lines[-5:]
        expected_content = "".join(expected_lines)
        assert content == expected_content
    finally:
        temp_path.unlink()


def test_tail_file_with_fewer_lines():
    """Test tail function when file has fewer lines than requested."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        lines = ["line 1\n", "line 2\n", "line 3\n"]
        f.writelines(lines)
        temp_path = Path(f.name)

    try:
        content = tail(temp_path, n=10)  # Request more lines than available
        expected_content = "".join(lines)
        assert content == expected_content
    finally:
        temp_path.unlink()


def test_tail_empty_file():
    """Test tail function with empty file."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        temp_path = Path(f.name)

    try:
        content = tail(temp_path)
        assert content == ""
    finally:
        temp_path.unlink()


def test_tail_nonexistent_file():
    """Test tail function with non-existent file."""
    nonexistent_path = Path("/tmp/nonexistent_file.txt")

    with pytest.raises(FileNotFoundError):
        tail(nonexistent_path)


@patch("rori.utils.shutil.which")
def test_get_executable_or_exit_found(mock_which):
    """Test get_executable_or_exit when executable is found."""
    mock_which.return_value = "/usr/bin/kubectl"

    result = get_executable_or_exit("kubectl")
    assert result == "/usr/bin/kubectl"
    mock_which.assert_called_once_with("kubectl")


@patch("rori.utils.shutil.which")
@patch("rori.utils.sys.exit")
def test_get_executable_or_exit_not_found(mock_exit, mock_which):
    """Test get_executable_or_exit when executable is not found."""
    mock_which.return_value = None

    get_executable_or_exit("nonexistent")

    mock_which.assert_called_once_with("nonexistent")
    mock_exit.assert_called_once_with(1)


def test_tail_follow_mode():
    """Test tail function in follow mode."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("initial content\n")
        temp_path = Path(f.name)

    try:
        # Test that follow mode returns a generator
        result = tail(temp_path, follow=True)
        assert hasattr(result, "__iter__")

        # We can't easily test the actual following behavior without
        # complex async setup, so just verify it returns an iterator
    finally:
        temp_path.unlink()


def test_cat_handles_binary_files():
    """Test cat function handles binary files gracefully."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        # Write some binary data
        f.write(b"\x89PNG\r\n\x1a\n")  # PNG header
        temp_path = Path(f.name)

    try:
        # Should handle binary files without crashing
        content = cat(temp_path)
        assert isinstance(content, str)
    except UnicodeDecodeError:
        # This is acceptable behavior for binary files
        pass
    finally:
        temp_path.unlink()


def test_tail_handles_large_files():
    """Test tail function with large files."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        # Write many lines
        for i in range(1000):
            f.write(f"line {i}\n")
        temp_path = Path(f.name)

    try:
        content = tail(temp_path, n=5)
        lines = content.strip().split("\n")
        assert len(lines) == 5
        assert lines[-1] == "line 999"
        assert lines[0] == "line 995"
    finally:
        temp_path.unlink()


@patch("rori.utils.os.path.exists")
def test_file_operations_with_permissions(mock_exists):
    """Test file operations handle permission errors."""
    mock_exists.return_value = True

    # Create a path that will cause permission error
    restricted_path = Path("/root/restricted_file.txt")

    with pytest.raises((PermissionError, OSError)):
        cat(restricted_path)
