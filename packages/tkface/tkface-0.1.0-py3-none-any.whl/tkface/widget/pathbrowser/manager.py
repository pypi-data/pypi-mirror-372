"""
File information management for PathBrowser widget.

This module provides file information caching, management, and utilities
for the PathBrowser widget.
"""

import logging
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path

from tkface import lang

from . import utils

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """File information cache."""

    path: str
    name: str
    is_dir: bool
    size_bytes: int
    size_str: str
    modified: str
    file_type: str


class FileInfoManager:
    """Manages file information with caching using standard library."""

    def __init__(self, root=None, max_cache_size=1000):
        # Use weakref to avoid circular references
        self._root = weakref.ref(root) if root else None
        self._max_cache_size = max_cache_size
        # Use OrderedDict for LRU behavior
        self._cache = OrderedDict()

    def get_file_info(self, file_path: str) -> FileInfo:
        """Get file information with caching."""
        # Check cache first
        if file_path in self._cache:
            # Move to end (most recently used)
            self._cache.move_to_end(file_path)
            return self._cache[file_path]

        # Get file information using pathlib
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()
            name = path_obj.name
            is_dir = path_obj.is_dir()

            # Size information
            size_bytes = stat.st_size if not is_dir else 0
            size_str = utils.format_size(size_bytes) if not is_dir else ""

            # Modified date
            modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))

            # File type
            if self._root is not None:
                root = self._root()  # pylint: disable=not-callable
            else:
                root = None
            if is_dir:
                file_type = lang.get("Folder", root)
            else:
                suffix = path_obj.suffix
                if suffix:
                    file_type = suffix[1:].upper()
                else:
                    file_type = lang.get("File", root)

            file_info = FileInfo(
                path=file_path,
                name=name,
                is_dir=is_dir,
                size_bytes=size_bytes,
                size_str=size_str,
                modified=modified,
                file_type=file_type,
            )

            # Cache the result with LRU management
            self._cache[file_path] = file_info
            self._manage_cache_size()
            return file_info

        except (OSError, PermissionError) as e:
            logger.warning("Failed to get file info for %s: %s", file_path, e)
            path_obj = Path(file_path)
            if self._root is not None:
                root = self._root()  # pylint: disable=not-callable
            else:
                root = None
            file_info = FileInfo(
                path=file_path,
                name=path_obj.name,
                is_dir=False,
                size_bytes=0,
                size_str="",
                modified="",
                file_type=lang.get("Unknown", root),
            )

            # Cache even error results to avoid repeated failed attempts
            self._cache[file_path] = file_info
            self._manage_cache_size()
            return file_info

    def _manage_cache_size(self):
        """Manage cache size using OrderedDict's LRU behavior."""
        while len(self._cache) > self._max_cache_size:
            # Remove oldest item (first in OrderedDict)
            self._cache.popitem(last=False)

    def clear_directory_cache(self, directory_path: str):
        """Clear cache entries for a specific directory and its subdirectories."""
        keys_to_remove = [
            key for key in self._cache.keys() if key.startswith(directory_path)
        ]
        for key in keys_to_remove:
            del self._cache[key]

    def get_memory_usage_estimate(self) -> int:
        """Get estimated memory usage in bytes."""
        # Simple estimate: sum of string lengths + object overhead
        total_size = 0
        for file_info in self._cache.values():
            total_size += (
                len(file_info.path)
                + len(file_info.name)
                + len(file_info.size_str)
                + len(file_info.modified)
                + len(file_info.file_type)
                + 100
            )
        return total_size

    def _resolve_symlink(self, path: str) -> str:
        """Resolve symlinks to prevent loops on macOS."""
        if utils.IS_MACOS:
            try:
                path_obj = Path(path)
                real_path = str(path_obj.resolve())
                return real_path if real_path != str(path_obj) else path
            except (OSError, PermissionError):
                logger.debug("Failed to resolve symlink for %s", path)
        return path

    def clear_cache(self):
        """Clear the cache."""
        self._cache.clear()

    def remove_from_cache(self, file_path: str):
        """Remove a specific file from cache."""
        if file_path in self._cache:
            del self._cache[file_path]

    def get_cache_size(self) -> int:
        """Get the number of cached items."""
        return len(self._cache)

    def get_cached_file_info(self, file_path: str) -> FileInfo:
        """Get file info from cache if available, otherwise fetch and cache it."""
        return self.get_file_info(file_path)
