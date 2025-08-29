"""
Style and theme functionality for PathBrowser widget.

This module provides theme loading, color processing, and appearance
customization for the PathBrowser widget.
"""

import configparser
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PathBrowserTheme:
    """Theme configuration for PathBrowser widget."""

    background: str = "#ffffff"
    foreground: str = "#000000"
    tree_background: str = "#f0f0f0"
    tree_foreground: str = "#000000"
    selected_background: str = "#0078d4"
    selected_foreground: str = "#ffffff"
    hover_background: str = "#e5f3ff"
    hover_foreground: str = "#000000"
    button_background: str = "#f0f0f0"
    button_foreground: str = "#000000"
    entry_background: str = "#ffffff"
    entry_foreground: str = "#000000"
    status_background: str = "#f0f0f0"
    status_foreground: str = "#000000"


def _load_theme_file(theme_name: str) -> Dict[str, Any]:
    """
    Load theme from .ini file.

    Args:
        theme_name: Name of the theme file (without .ini extension)

    Returns:
        dict: Theme definition dictionary

    Raises:
        FileNotFoundError: If theme file doesn't exist
        configparser.Error: If .ini file is malformed
    """
    # Get the directory where this module is located
    current_dir = Path(__file__).parent.parent.parent / "themes"
    theme_file = current_dir / f"{theme_name}.ini"
    if not theme_file.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_file}")
    config = configparser.ConfigParser()
    config.read(theme_file)
    if theme_name not in config:
        raise configparser.Error(
            f"Theme section '{theme_name}' not found in {theme_file}"
        )
    theme_section = config[theme_name]
    theme_dict = {}
    for key, value in theme_section.items():
        theme_dict[key] = value
    return theme_dict


def get_pathbrowser_theme(theme_name: str = "light") -> PathBrowserTheme:
    """
    Get theme configuration for PathBrowser.

    Args:
        theme_name: Name of the theme to load

    Returns:
        PathBrowserTheme: Theme configuration object
    """
    try:
        theme_dict = _load_theme_file(theme_name)
        # Filter only the fields that PathBrowserTheme supports
        supported_fields = {
            "background",
            "foreground",
            "tree_background",
            "tree_foreground",
            "selected_background",
            "selected_foreground",
            "hover_background",
            "hover_foreground",
            "button_background",
            "button_foreground",
            "entry_background",
            "entry_foreground",
            "status_background",
            "status_foreground",
        }
        filtered_dict = {k: v for k, v in theme_dict.items() if k in supported_fields}
        return PathBrowserTheme(**filtered_dict)
    except (FileNotFoundError, configparser.Error) as e:
        logger.warning("Failed to load theme %s: %s", theme_name, e)
        # Return default theme
        return PathBrowserTheme()


def get_pathbrowser_themes() -> list:
    """
    Get list of available themes.

    Returns:
        list: List of available theme names
    """
    themes_dir = Path(__file__).parent.parent.parent / "themes"
    if not themes_dir.exists():
        return ["light"]

    themes = []
    for theme_file in themes_dir.glob("*.ini"):
        theme_name = theme_file.stem
        if theme_name in ["light", "dark"]:
            themes.append(theme_name)

    return themes if themes else ["light"]


def apply_theme_to_widget(widget, theme: PathBrowserTheme):
    """
    Apply theme to a widget and its children.

    Args:
        widget: The widget to apply theme to
        theme: Theme configuration object
    """
    try:
        # Apply to the widget itself
        widget.configure(bg=theme.background, fg=theme.foreground)

        # Apply to common child widgets
        for child in widget.winfo_children():
            widget_type = child.winfo_class()

            if widget_type == "Treeview":
                child.configure(
                    background=theme.tree_background,
                    foreground=theme.tree_foreground,
                    selectbackground=theme.selected_background,
                    selectforeground=theme.selected_foreground,
                )
            elif widget_type == "TButton":
                child.configure(
                    background=theme.button_background,
                    foreground=theme.button_foreground,
                )
            elif widget_type == "TEntry":
                child.configure(
                    fieldbackground=theme.entry_background,
                    foreground=theme.entry_foreground,
                )
            elif widget_type == "TLabel":
                child.configure(
                    background=theme.background, foreground=theme.foreground
                )
            elif widget_type == "TFrame":
                child.configure(background=theme.background)

            # Recursively apply to children
            apply_theme_to_widget(child, theme)

    except (OSError, ValueError) as e:
        logger.debug("Failed to apply theme to widget: %s", e)


def get_default_theme() -> PathBrowserTheme:
    """
    Get the default theme for PathBrowser.

    Returns:
        PathBrowserTheme: Default theme configuration
    """
    return PathBrowserTheme()
