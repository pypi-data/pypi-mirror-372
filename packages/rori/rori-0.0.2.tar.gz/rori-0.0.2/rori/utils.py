import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterator, Optional


def is_executable_available(executable: str) -> bool:
    """
    Check if an executable is available in the system PATH.

    Args:
        executable: Name of the executable to check

    Returns:
        True if executable is found, False otherwise
    """
    return shutil.which(executable) is not None


def check_file_access(file_path: Path, operation: str = "read") -> None:
    """
    Comprehensive file access check using os.access().

    Args:
        file_path: Path to the file to check
        operation: Type of operation ("read", "write", "execute")

    Raises:
        FileNotFoundError: If the file doesn't exist
        IsADirectoryError: If the path is a directory when a file is expected
        PermissionError: If the file can't be accessed for the operation
    """
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} no such file")

    if not file_path.is_file():
        raise IsADirectoryError(f"{file_path} is a directory")

    # Use os.access for more accurate permission checking
    access_map = {
        "read": os.R_OK,
        "write": os.W_OK,
        "execute": os.X_OK,
    }

    if operation not in access_map:
        raise ValueError(f"invalid operation {operation}")

    if not os.access(file_path, access_map[operation]):
        raise PermissionError(f"{file_path} permission denied")


def cat(file_path: str | Path, encoding: str = "utf-8") -> list[str]:
    """
    Read and return the entire contents of a file (like Unix cat command).

    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)

    Returns:
        String containing the file contents

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
        UnicodeDecodeError: If the file can't be decoded with the specified encoding
    """
    file_path = Path(file_path)
    check_file_access(file_path, "read")
    # return file_path.read_text(encoding=encoding)
    with file_path.open("r", encoding=encoding) as f:
        # Read all lines and return the last N
        all_lines = f.readlines()
        return [line.rstrip("\n\r") for line in all_lines]


def tail(
    file_path: str | Path,
    lines: int = 10,
    encoding: str = "utf-8",
    follow: bool = False,
    sleep_interval: float = 1.0,
) -> list[str] | Iterator[str]:
    """
    Read the last N lines from a file (like Unix tail command).

    Args:
        file_path: Path to the file to read
        lines: Number of lines to return from the end (default: 10)
        encoding: File encoding (default: utf-8)
        follow: If True, continuously monitor file for new lines (like tail -f)
        sleep_interval: Time to sleep between checks when following (default: 1.0s)

    Returns:
        List of strings (last N lines) or Iterator if follow=True

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read
    """
    file_path = Path(file_path)
    check_file_access(file_path, "read")

    if follow:
        return _tail_follow(file_path, lines, encoding, sleep_interval)
    else:
        return _tail_static(file_path, lines, encoding)


def _tail_static(file_path: Path, lines: int, encoding: str) -> list[str]:
    """Get the last N lines from a file (static version)."""
    with file_path.open("r", encoding=encoding) as f:
        # Read all lines and return the last N
        all_lines = f.readlines()
        return [line.rstrip("\n\r") for line in all_lines[-lines:]]


def _tail_follow(
    file_path: Path, lines: int, encoding: str, sleep_interval: float
) -> Iterator[str]:
    """
    Follow a file and yield new lines as they're added (like tail -f).

    This is a generator that yields the last N lines initially,
    then continuously monitors for new lines.
    """
    initial_lines = _tail_static(file_path, lines, encoding)
    for line in initial_lines:
        yield line

    # Remember file position and size
    with file_path.open("r", encoding=encoding) as f:
        f.seek(0, 2)  # Seek to end
        last_position = f.tell()
        last_size = file_path.stat().st_size

    # Now follow the file
    while True:
        try:
            current_size = file_path.stat().st_size

            # Check if file was truncated or recreated
            if current_size < last_size:
                last_position = 0

            # Check if file has new content
            if current_size > last_size or last_position < current_size:
                with file_path.open("r", encoding=encoding) as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    last_position = f.tell()

                    for line in new_lines:
                        yield line.rstrip("\n\r")

            last_size = current_size
        except (FileNotFoundError, PermissionError):
            # File might have been deleted or moved, wait and retry
            pass
        except KeyboardInterrupt:
            break
        time.sleep(sleep_interval)
