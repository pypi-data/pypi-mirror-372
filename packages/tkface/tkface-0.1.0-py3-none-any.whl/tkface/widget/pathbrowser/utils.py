"""
Utility functions for PathBrowser widget.

This module provides common utility functions used across the PathBrowser
widget components.
"""

import fnmatch
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# OS detection constants
IS_MACOS = sys.platform == "darwin"
IS_WINDOWS = sys.platform.startswith("win")
IS_LINUX = sys.platform.startswith("linux")


def format_size(size_bytes: int) -> str:
    """
    Format file size using standard library.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted size string (e.g., "1.5 MB", "2.3 GB")
    """
    if size_bytes == 0:
        return "0 B"

    # Use standard library for size formatting
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            if unit != "B":
                return f"{size_bytes:.1f} {unit}"
            return f"{int(size_bytes)} {unit}"
        size_bytes /= 1024

    return f"{size_bytes:.1f} TB"


def open_file_with_default_app(file_path: str) -> bool:
    """
    Open a file with the default application for the current platform.

    Args:
        file_path: Path to the file to open

    Returns:
        True if successful, False otherwise
    """
    try:
        if IS_WINDOWS:
            os.startfile(file_path)  # pylint: disable=no-member
        elif IS_MACOS:
            subprocess.run(["open", file_path], check=False)
        else:
            subprocess.run(["xdg-open", file_path], check=False)
        return True
    except Exception:
        return False


def add_extension_if_needed(
    filename: str, filetypes: List[Tuple[str, str]], current_filter: str = None
) -> str:
    """
    Add file extension if not present and filetypes are available.

    Args:
        filename: The filename to process
        filetypes: List of file type filters [(description, pattern), ...]
        current_filter: Current filter selection

    Returns:
        Filename with extension added if needed
    """
    if not filetypes or os.path.splitext(filename)[1]:
        return filename

    if not current_filter:
        return filename

    for desc, pattern in filetypes:
        expected_filter = f"{desc} ({pattern})"
        if current_filter == expected_filter and pattern != "*.*":
            ext = pattern.rsplit("*", maxsplit=1)[-1] if "*" in pattern else ""
            if ext and not filename.endswith(ext):
                filename += ext
            break

    return filename


def matches_filter(
    filename: str,
    filetypes: List[Tuple[str, str]],
    current_filter: str,
    select_mode: str,
    all_files_text: str,
) -> bool:
    """
    Check if filename matches the current filter.

    Args:
        filename: The filename to check
        filetypes: List of file type filters [(description, pattern), ...]
        current_filter: Current filter selection
        select_mode: Selection mode ("file", "dir", or "both")
        all_files_text: Text for "All files" filter

    Returns:
        True if filename matches the filter
    """
    if select_mode == "dir":
        return False

    if current_filter == all_files_text:
        return True

    # Find the pattern for the selected filter
    for desc, pattern in filetypes:
        if current_filter == f"{desc} ({pattern})":
            if pattern == "*.*":
                return True

            # Handle multiple patterns separated by spaces
            patterns = pattern.split()
            for single_pattern in patterns:
                if single_pattern.startswith("*."):
                    ext = single_pattern[1:]
                    if filename.lower().endswith(ext.lower()):
                        return True
                else:
                    # Simple pattern matching for non-extension patterns
                    if fnmatch.fnmatch(filename.lower(), single_pattern.lower()):
                        return True

            # If we get here, no pattern matched
            return False

    # If no filter was found, return True (show all files)
    return True


def would_create_loop(path: str, real_path: str, tree_widget) -> bool:
    """
    Check if adding this path would create a loop in the directory tree.

    Args:
        path: The path to check
        real_path: The real path (resolved symlink)
        tree_widget: The tree widget to check against

    Returns:
        True if adding this path would create a loop
    """
    # Check if the real path is already in the tree
    if tree_widget.exists(real_path):
        return True

    # Check if this would create a circular reference (macOS specific)
    # For example: /Volumes/Macintosh HD/Volumes -> /
    if IS_MACOS and real_path == "/" and Path(path).is_relative_to("/Volumes"):
        return True

    # Check if the path contains the real path (would create a loop)
    if real_path != "/" and real_path in path:
        return True

    return False


def get_performance_stats(
    cache_size: int,
    memory_usage_bytes: int,
    current_directory: str,
    selected_items_count: int,
) -> dict:
    """
    Get performance statistics for debugging.

    Args:
        cache_size: Number of cached items
        memory_usage_bytes: Memory usage in bytes
        current_directory: Current directory path
        selected_items_count: Number of selected items

    Returns:
        Dictionary containing performance statistics
    """
    return {
        "cache_size": cache_size,
        "memory_usage_bytes": memory_usage_bytes,
        "current_directory": current_directory,
        "selected_items_count": selected_items_count,
    }
