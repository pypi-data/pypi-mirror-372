"""
File dialog module for tkface.

This module provides file and directory selection dialogs.
"""

import tkinter as tk
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .. import lang, win
from ..widget.pathbrowser import PathBrowser
from . import _position_window


@dataclass
class FileDialogConfig:
    """Configuration for file dialog."""

    select: str = "file"
    multiple: bool = False
    initialdir: Optional[str] = None
    filetypes: Optional[List[Tuple[str, str]]] = None
    title: Optional[str] = None
    save_mode: bool = False
    initialfile: Optional[str] = None


@dataclass
class WindowPosition:
    """Window positioning configuration."""

    x: Optional[int] = None
    y: Optional[int] = None
    x_offset: int = 0
    y_offset: int = 0


def _create_dialog_window(parent: Optional[tk.Tk]) -> tk.Toplevel:
    """Create and configure the dialog window."""
    if parent is None:
        dialog = tk.Toplevel()
        dialog.withdraw()  # Hide until ready
    else:
        dialog = tk.Toplevel(parent)
        dialog.withdraw()  # Hide until ready
    return dialog


def _setup_dialog_properties(dialog: tk.Toplevel, title: str, scaled_sizes: dict):
    """Setup dialog window properties."""
    dialog.title(title)
    dialog.resizable(True, True)
    dialog.minsize(scaled_sizes["min_width"], scaled_sizes["min_height"])
    dialog.geometry(f"{scaled_sizes['default_width']}x{scaled_sizes['default_height']}")


def _position_dialog(
    dialog: tk.Toplevel,
    parent: Optional[tk.Tk],
    x: Optional[int],
    y: Optional[int],
    x_offset: int,
    y_offset: int,
):  # pylint: disable=too-many-arguments,too-many-positional-arguments
    """Position the dialog window."""
    if parent:
        _position_window(dialog, parent, x, y, x_offset, y_offset)
    else:
        # Position on screen if no parent
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        if x is None:
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        if y is None:
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
        x += x_offset
        y += y_offset
        dialog.geometry(f"{width}x{height}+{x}+{y}")


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-statements
def askpath(
    select: str = "file",
    multiple: bool = False,
    initialdir: Optional[str] = None,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
    config: Optional[FileDialogConfig] = None,
    position: Optional[WindowPosition] = None,
) -> List[str]:
    """
    Show a file/directory selection dialog.

    Args:
        select: Selection mode ("file", "dir", or "both")
        multiple: Allow multiple selection
        initialdir: Initial directory to display
        filetypes: List of file type filters [(description, pattern), ...]
        title: Dialog title
        parent: Parent window (if None, creates a new Toplevel)
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
        config: FileDialogConfig object (overrides individual parameters)
        position: WindowPosition object (overrides individual position parameters)

    Returns:
        List of selected file/directory paths (empty list if cancelled)
    """
    # Use dataclass config if provided, otherwise use individual parameters
    if config is not None:
        select = config.select
        multiple = config.multiple
        initialdir = config.initialdir
        filetypes = config.filetypes
        title = config.title

    if position is not None:
        x = position.x
        y = position.y
        x_offset = position.x_offset
        y_offset = position.y_offset

    # Create dialog window
    dialog = _create_dialog_window(parent)

    # Cache DPI scaling calculations for performance (similar to messagebox.py)
    scaled_sizes = win.calculate_dpi_sizes(
        {
            "min_width": 900,
            "min_height": 650,
            "default_width": 1000,
            "default_height": 700,
            "padding": 10,
        },
        dialog,
        max_scale=1.5,
    )

    # Set dialog properties
    if title is None:
        if select == "file":
            title = "Select File"
        elif select == "dir":
            title = "Select Directory"
        else:
            title = "Select File or Directory"
        if multiple:
            title += "s"

    _setup_dialog_properties(dialog, title, scaled_sizes)

    # Make dialog modal
    if parent:
        dialog.transient(parent)
    dialog.grab_set()

    # Create path browser widget
    # Set language for the dialog before creating PathBrowser
    lang.set("auto", dialog)

    browser = PathBrowser(
        dialog,
        select=select,
        multiple=multiple,
        initialdir=initialdir,
        filetypes=filetypes,
        save_mode=getattr(config, "save_mode", False) if config else False,
        initialfile=getattr(config, "initialfile", None) if config else None,
    )
    browser.pack(
        fill=tk.BOTH,
        expand=True,
        padx=scaled_sizes["padding"],
        pady=scaled_sizes["padding"],
    )

    # Position the dialog (after content is created)
    _position_dialog(dialog, parent, x, y, x_offset, y_offset)

    # Result storage
    result = []

    def on_ok(event=None):  # pylint: disable=unused-argument
        nonlocal result
        result = browser.get_selection()
        dialog.destroy()

    def on_cancel(event=None):  # pylint: disable=unused-argument
        nonlocal result
        result = []
        dialog.destroy()

    # Bind events
    browser.bind("<<PathBrowserOK>>", on_ok)
    browser.bind("<<PathBrowserCancel>>", on_cancel)

    # Focus on the browser
    browser.focus_set()

    # Show dialog and wait (after position is set)
    dialog.deiconify()  # Show the dialog
    dialog.lift()
    dialog.focus_set()
    dialog.wait_window()

    return result


def askopenfile(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    initialdir: Optional[str] = None,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
    config: Optional[FileDialogConfig] = None,
    position: Optional[WindowPosition] = None,
) -> List[str]:
    """
    Show a single file selection dialog.

    Args:
        initialdir: Initial directory to display
        filetypes: List of file type filters [(description, pattern), ...]
        title: Dialog title
        parent: Parent window
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
        config: FileDialogConfig object (overrides individual parameters)
        position: WindowPosition object (overrides individual position parameters)

    Returns:
        List with single selected file path (empty list if cancelled)
    """
    if config is None:
        config = FileDialogConfig(
            select="file",
            multiple=False,
            initialdir=initialdir,
            filetypes=filetypes,
            title=title,
        )

    if position is None:
        position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)

    return askpath(parent=parent, config=config, position=position)


def askopenfiles(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    initialdir: Optional[str] = None,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
    config: Optional[FileDialogConfig] = None,
    position: Optional[WindowPosition] = None,
) -> List[str]:
    """
    Show a multiple file selection dialog.

    Args:
        initialdir: Initial directory to display
        filetypes: List of file type filters [(description, pattern), ...]
        title: Dialog title
        parent: Parent window
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
        config: FileDialogConfig object (overrides individual parameters)
        position: WindowPosition object (overrides individual position parameters)

    Returns:
        List of selected file paths (empty list if cancelled)
    """
    if config is None:
        config = FileDialogConfig(
            select="file",
            multiple=True,
            initialdir=initialdir,
            filetypes=filetypes,
            title=title,
        )

    if position is None:
        position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)

    return askpath(parent=parent, config=config, position=position)


def askdirectory(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    initialdir: Optional[str] = None,
    title: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
    config: Optional[FileDialogConfig] = None,
    position: Optional[WindowPosition] = None,
) -> List[str]:
    """
    Show a directory selection dialog.

    Args:
        initialdir: Initial directory to display
        title: Dialog title
        parent: Parent window
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
        config: FileDialogConfig object (overrides individual parameters)
        position: WindowPosition object (overrides individual position parameters)

    Returns:
        List with single selected directory path (empty list if cancelled)
    """
    if config is None:
        config = FileDialogConfig(
            select="dir",
            multiple=False,
            initialdir=initialdir,
            filetypes=None,
            title=title,
        )

    if position is None:
        position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)

    return askpath(parent=parent, config=config, position=position)


def asksavefile(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    initialdir: Optional[str] = None,
    initialfile: Optional[str] = None,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
    config: Optional[FileDialogConfig] = None,
    position: Optional[WindowPosition] = None,
) -> List[str]:
    """
    Show a file save dialog.

    Args:
        initialdir: Initial directory to display
        initialfile: Initial filename to suggest
        filetypes: List of file type filters [(description, pattern), ...]
        title: Dialog title
        parent: Parent window
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
        config: FileDialogConfig object (overrides individual parameters)
        position: WindowPosition object (overrides individual position parameters)

    Returns:
        List with single selected file path (empty list if cancelled)
    """
    if config is None:
        config = FileDialogConfig(
            select="file",
            multiple=False,
            initialdir=initialdir,
            filetypes=filetypes,
            title=title or "Save File",
            save_mode=True,
            initialfile=initialfile,
        )

    if position is None:
        position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)

    # For save dialog, we need to modify the PathBrowser to handle save mode
    # This will be implemented by adding a save_mode parameter to PathBrowser
    result = askpath(parent=parent, config=config, position=position)

    return result
