"""
Path browser widget module for tkface.

This module provides a path browser widget with directory tree and file list panes.
Features:
- Directory tree (left pane) with icons and refresh
- File list (right pane) with details view, filtering, sorting, and multiple selection
- Path navigation bar
- OK/Cancel buttons at the bottom
- File information caching and management
- Theme support
- Performance optimization
"""

from .core import PathBrowser, PathBrowserConfig, PathBrowserState
from .manager import FileInfo, FileInfoManager
from .style import PathBrowserTheme, get_pathbrowser_theme, get_pathbrowser_themes
from .utils import format_size

__all__ = [
    "PathBrowser",
    "PathBrowserConfig",
    "PathBrowserState",
    "FileInfoManager",
    "FileInfo",
    "format_size",
    "get_pathbrowser_theme",
    "get_pathbrowser_themes",
    "PathBrowserTheme",
]
