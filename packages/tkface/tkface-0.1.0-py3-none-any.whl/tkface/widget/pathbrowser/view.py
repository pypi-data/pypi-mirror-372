"""
View and UI functionality for PathBrowser widget.

This module provides UI creation, display updates, and user interaction
handling for the PathBrowser widget.
"""

import logging
import string
import tkinter as tk
from contextlib import suppress
from itertools import islice
from operator import itemgetter
from pathlib import Path
from tkinter import ttk

from tkface import lang
from tkface.dialog import messagebox

from . import utils

# Configure logging
logger = logging.getLogger(__name__)


def _create_path_navigation(pathbrowser_instance):
    """Create path navigation widgets."""
    # Top toolbar with path and navigation
    pathbrowser_instance.top_toolbar = ttk.Frame(pathbrowser_instance)
    pathbrowser_instance.top_toolbar.pack(fill=tk.X, padx=5, pady=5)

    # Path display and navigation
    pathbrowser_instance.path_frame = ttk.Frame(pathbrowser_instance.top_toolbar)
    pathbrowser_instance.path_frame.pack(fill=tk.X)

    # Up button
    pathbrowser_instance.up_button = ttk.Button(
        pathbrowser_instance.path_frame,
        text="<",
        command=pathbrowser_instance._go_up,  # pylint: disable=protected-access
        width=3,
    )
    pathbrowser_instance.up_button.pack(side=tk.LEFT, padx=(0, 5))

    # Down button
    pathbrowser_instance.down_button = ttk.Button(
        pathbrowser_instance.path_frame,
        text=">",
        command=pathbrowser_instance._go_down,  # pylint: disable=protected-access
        width=3,
    )
    pathbrowser_instance.down_button.pack(side=tk.LEFT, padx=(0, 5))

    # Path entry
    pathbrowser_instance.path_var = tk.StringVar()
    pathbrowser_instance.path_entry = ttk.Entry(
        pathbrowser_instance.path_frame,
        textvariable=pathbrowser_instance.path_var,
        state="normal",
    )
    pathbrowser_instance.path_entry.pack(
        side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5)
    )

    # Go button
    pathbrowser_instance.go_button = ttk.Button(
        pathbrowser_instance.path_frame,
        text=lang.get("Go", pathbrowser_instance),
        command=pathbrowser_instance._go_to_path,  # pylint: disable=protected-access
    )
    pathbrowser_instance.go_button.pack(side=tk.LEFT)

    # Bind Enter key to path entry for navigation
    pathbrowser_instance.path_entry.bind(
        "<Return>",
        lambda e: pathbrowser_instance._go_to_path(),  # pylint: disable=protected-access
    )


def _create_main_paned_window(pathbrowser_instance):
    """Create main paned window with tree and file list."""
    # Main paned window
    pathbrowser_instance.paned = ttk.PanedWindow(
        pathbrowser_instance, orient=tk.HORIZONTAL
    )
    pathbrowser_instance.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Left pane - Directory tree
    pathbrowser_instance.tree_frame = ttk.Frame(pathbrowser_instance.paned)
    pathbrowser_instance.paned.add(pathbrowser_instance.tree_frame, weight=1)

    # Directory tree with icons and better styling
    pathbrowser_instance.tree = ttk.Treeview(
        pathbrowser_instance.tree_frame,
        show="tree",
        selectmode="browse",
        height=15,  # Set reasonable height
    )
    pathbrowser_instance.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Configure tree style for better appearance
    style = ttk.Style()
    # Increase row height for better visibility
    style.configure("Treeview", rowheight=25)


def _create_file_list(pathbrowser_instance):
    """Create file list widget."""
    # Right pane - File list
    pathbrowser_instance.file_frame = ttk.Frame(pathbrowser_instance.paned)
    pathbrowser_instance.paned.add(pathbrowser_instance.file_frame, weight=2)

    # File list as Treeview for better appearance
    select_mode = "extended" if pathbrowser_instance.config.multiple else "browse"
    pathbrowser_instance.file_tree = ttk.Treeview(
        pathbrowser_instance.file_frame,
        columns=("size", "modified", "type"),
        show="tree headings",
        selectmode=select_mode,
        height=15,  # Set reasonable height
    )

    # Configure columns with sorting
    pathbrowser_instance.file_tree.heading(
        "#0",
        text=lang.get("Name", pathbrowser_instance),
        # pylint: disable=protected-access
        command=lambda: pathbrowser_instance._sort_files("#0"),
    )
    pathbrowser_instance.file_tree.heading(
        "size",
        text=lang.get("Size", pathbrowser_instance),
        # pylint: disable=protected-access
        command=lambda: pathbrowser_instance._sort_files("size"),
    )
    pathbrowser_instance.file_tree.heading(
        "modified",
        text=lang.get("Modified", pathbrowser_instance),
        # pylint: disable=protected-access
        command=lambda: pathbrowser_instance._sort_files("modified"),
    )
    pathbrowser_instance.file_tree.heading(
        "type",
        text=lang.get("Type", pathbrowser_instance),
        # pylint: disable=protected-access
        command=lambda: pathbrowser_instance._sort_files("type"),
    )

    pathbrowser_instance.file_tree.column("#0", width=200, minwidth=150)
    pathbrowser_instance.file_tree.column("size", width=80, minwidth=60)
    pathbrowser_instance.file_tree.column("modified", width=120, minwidth=100)
    pathbrowser_instance.file_tree.column("type", width=100, minwidth=80)

    pathbrowser_instance.file_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


def _create_status_and_buttons(pathbrowser_instance):
    """Create status bar and bottom buttons."""
    # Status bar (bottom)
    pathbrowser_instance.status_var = tk.StringVar()
    pathbrowser_instance.status_bar = ttk.Label(
        pathbrowser_instance,
        textvariable=pathbrowser_instance.status_var,
        relief=tk.SUNKEN,
    )
    pathbrowser_instance.status_bar.pack(fill=tk.X, padx=5, pady=(0, 5), side=tk.BOTTOM)

    # Bottom buttons (above status bar)
    pathbrowser_instance.button_frame = ttk.Frame(pathbrowser_instance)
    pathbrowser_instance.button_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)

    # Set button labels based on save mode
    if getattr(pathbrowser_instance.config, "save_mode", False):
        ok_text = lang.get("Save", pathbrowser_instance)
    else:
        ok_text = lang.get(pathbrowser_instance.config.ok_label, pathbrowser_instance)

    pathbrowser_instance.ok_button = ttk.Button(
        pathbrowser_instance.button_frame,
        text=ok_text,
        command=pathbrowser_instance._on_ok,  # pylint: disable=protected-access
    )
    pathbrowser_instance.ok_button.pack(side=tk.RIGHT, padx=(5, 0))

    pathbrowser_instance.cancel_button = ttk.Button(
        pathbrowser_instance.button_frame,
        text=lang.get(pathbrowser_instance.config.cancel_label, pathbrowser_instance),
        command=pathbrowser_instance._on_cancel,  # pylint: disable=protected-access
    )
    pathbrowser_instance.cancel_button.pack(side=tk.RIGHT)


def _create_toolbar(pathbrowser_instance):
    """Create bottom toolbar with file name and filter."""
    # Bottom toolbar with file name and filter (Windows style)
    pathbrowser_instance.toolbar_frame = ttk.Frame(pathbrowser_instance)
    pathbrowser_instance.toolbar_frame.pack(fill=tk.X, padx=5, pady=2, side=tk.BOTTOM)
    # Configure minimum width to prevent hiding
    pathbrowser_instance.toolbar_frame.configure(width=800)

    # File name display (left side)
    # Set label text based on save mode
    if getattr(pathbrowser_instance.config, "save_mode", False):
        label_text = lang.get("File name:", pathbrowser_instance)
    else:
        label_text = lang.get("File name:", pathbrowser_instance)

    pathbrowser_instance.selected_label = ttk.Label(
        pathbrowser_instance.toolbar_frame, text=label_text
    )
    pathbrowser_instance.selected_label.pack(side=tk.LEFT, padx=(0, 5))

    pathbrowser_instance.selected_var = tk.StringVar()
    # Set initial filename for save mode
    save_mode = getattr(pathbrowser_instance.config, "save_mode", False)
    initialfile = getattr(pathbrowser_instance.config, "initialfile", None)
    if save_mode and initialfile:
        pathbrowser_instance.selected_var.set(initialfile)
    else:
        pathbrowser_instance.selected_var.set("")
    pathbrowser_instance.selected_files_entry = ttk.Entry(
        pathbrowser_instance.toolbar_frame,
        textvariable=pathbrowser_instance.selected_var,
        state="normal",
        width=30,  # Set minimum width
    )
    pathbrowser_instance.selected_files_entry.pack(
        side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10)
    )

    # Bind focus event to select all text when focused
    pathbrowser_instance.selected_files_entry.bind(
        "<FocusIn>",
        pathbrowser_instance._on_filename_focus,  # pylint: disable=protected-access
    )

    # Filter (right side)
    pathbrowser_instance.filter_label = ttk.Label(
        pathbrowser_instance.toolbar_frame,
        text=lang.get("Files of type:", pathbrowser_instance),
    )
    pathbrowser_instance.filter_label.pack(side=tk.LEFT, padx=(0, 5))

    # Filter combobox
    pathbrowser_instance.filter_var = tk.StringVar()
    pathbrowser_instance.filter_combo = ttk.Combobox(
        pathbrowser_instance.toolbar_frame,
        textvariable=pathbrowser_instance.filter_var,
        state="readonly",
        width=20,  # Reduce width to fit better
    )
    pathbrowser_instance.filter_combo.pack(side=tk.LEFT, padx=(0, 5))
    pathbrowser_instance._update_filter_options()  # pylint: disable=protected-access


def create_pathbrowser_widgets(pathbrowser_instance):
    """Create the widget layout for PathBrowser."""
    _create_path_navigation(pathbrowser_instance)
    _create_main_paned_window(pathbrowser_instance)
    _create_file_list(pathbrowser_instance)
    _create_status_and_buttons(pathbrowser_instance)
    _create_toolbar(pathbrowser_instance)

    # Initialize view mode
    pathbrowser_instance.view_mode = "details"


def setup_pathbrowser_bindings(pathbrowser_instance):
    """Setup event bindings for PathBrowser."""
    pathbrowser_instance.tree.bind(
        "<<TreeviewSelect>>",
        pathbrowser_instance._on_tree_select,  # pylint: disable=protected-access
    )
    pathbrowser_instance.tree.bind(
        "<<TreeviewOpen>>",
        pathbrowser_instance._on_tree_open,  # pylint: disable=protected-access
    )
    pathbrowser_instance.tree.bind(
        "<Button-3>",
        pathbrowser_instance._on_tree_right_click,  # pylint: disable=protected-access
    )  # Right click
    pathbrowser_instance.file_tree.bind(
        "<<TreeviewSelect>>",
        pathbrowser_instance._on_file_select,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<Double-Button-1>",
        pathbrowser_instance._on_file_double_click,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<Button-3>",
        pathbrowser_instance._on_file_right_click,  # pylint: disable=protected-access
    )  # Right click
    pathbrowser_instance.filter_combo.bind(
        "<<ComboboxSelected>>",
        pathbrowser_instance._on_filter_change,  # pylint: disable=protected-access
    )

    # Keyboard shortcuts
    pathbrowser_instance.bind(
        "<Return>", pathbrowser_instance._on_ok  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<Escape>", pathbrowser_instance._on_cancel  # pylint: disable=protected-access
    )

    # Global keyboard shortcuts for file navigation
    pathbrowser_instance.bind(
        "<Up>", pathbrowser_instance._handle_up_key  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<Down>",
        pathbrowser_instance._handle_down_key,  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<Home>",
        pathbrowser_instance._handle_home_key,  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<End>",
        pathbrowser_instance._handle_end_key,  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<Shift-Up>",
        pathbrowser_instance._handle_shift_up_key,  # pylint: disable=protected-access
    )
    pathbrowser_instance.bind(
        "<Shift-Down>",
        pathbrowser_instance._handle_shift_down_key,  # pylint: disable=protected-access
    )

    # Tree-specific keyboard shortcuts
    pathbrowser_instance.tree.bind(
        "<Right>", pathbrowser_instance._expand_node  # pylint: disable=protected-access
    )
    pathbrowser_instance.tree.bind(
        "<Left>",
        pathbrowser_instance._collapse_node,  # pylint: disable=protected-access
    )
    pathbrowser_instance.tree.bind(
        "<space>",
        pathbrowser_instance._toggle_selected_node,  # pylint: disable=protected-access
    )

    # File list keyboard shortcuts
    pathbrowser_instance.file_tree.bind(
        "<Up>",
        pathbrowser_instance._move_selection_up,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<Down>",
        pathbrowser_instance._move_selection_down,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<Home>",
        pathbrowser_instance._move_to_first,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<End>", pathbrowser_instance._move_to_last  # pylint: disable=protected-access
    )

    # Multi-selection with Shift key
    pathbrowser_instance.file_tree.bind(
        "<Shift-Up>",
        pathbrowser_instance._extend_selection_up,  # pylint: disable=protected-access
    )
    pathbrowser_instance.file_tree.bind(
        "<Shift-Down>",
        pathbrowser_instance._extend_selection_down,  # pylint: disable=protected-access
    )

    # Ensure file_tree gets focus when clicked
    pathbrowser_instance.file_tree.bind(
        "<Button-1>",
        pathbrowser_instance._on_file_tree_click,  # pylint: disable=protected-access
    )

    # Ensure file_tree gets focus when frame is clicked
    pathbrowser_instance.file_frame.bind(
        "<Button-1>",
        pathbrowser_instance._on_file_frame_click,  # pylint: disable=protected-access
    )


def load_directory_tree(pathbrowser_instance):
    """Load the directory tree."""
    pathbrowser_instance.tree.delete(*pathbrowser_instance.tree.get_children())

    # Add root directories with better icons and labels
    if utils.IS_WINDOWS:  # Windows
        for drive in string.ascii_uppercase:
            drive_path = f"{drive}:\\"
            if Path(drive_path).exists():
                # Get drive label if possible
                pathbrowser_instance.tree.insert(
                    "", "end", drive_path, text=drive_path, open=False
                )
                # Pre-populate root level directories for better UX
                populate_tree_node(pathbrowser_instance, drive_path)
    else:  # Unix-like
        pathbrowser_instance.tree.insert("", "end", "/", text="/", open=False)
        # Pre-populate root level directories for better UX
        populate_tree_node(pathbrowser_instance, "/")

    # Expand current directory path
    expand_path(pathbrowser_instance, pathbrowser_instance.state.current_dir)


def populate_tree_node(pathbrowser_instance, parent):
    """Populate a tree node with its children using improved lazy loading."""
    try:
        # Check if already populated (avoid duplicate work)
        existing_children = pathbrowser_instance.tree.get_children(parent)
        has_placeholders = any(
            child.endswith("_placeholder") for child in existing_children
        )
        if existing_children and not has_placeholders:
            return  # Already populated

        # Get directories only, more efficiently
        dirs = []
        path_obj = Path(parent)

        # Use contextlib.suppress for cleaner error handling
        for item in path_obj.iterdir():
            if item.is_dir():
                # Check for symlink loops on macOS
                if utils.IS_MACOS:
                    with suppress(OSError, PermissionError):
                        real_path = item.resolve()
                        if real_path == Path("/") and "/Volumes/" in str(item):
                            continue
                        if real_path != item and utils.would_create_loop(
                            str(item), str(real_path), pathbrowser_instance.tree
                        ):
                            continue

                dirs.append((item.name, str(item)))

        # Sort and add directories efficiently
        dirs.sort(key=lambda x: x[0].lower())

        # Remove any existing placeholders
        for child in existing_children:
            if child.endswith("_placeholder"):
                pathbrowser_instance.tree.delete(child)

        # Add directories with improved performance
        for child_name, child_path in dirs:
            if not pathbrowser_instance.tree.exists(child_path):
                pathbrowser_instance.tree.insert(
                    parent, "end", child_path, text=child_name, open=False
                )

                # Check if directory has subdirectories (lazy loading)
                with suppress(OSError, PermissionError):
                    # Quick check for subdirectories without full enumeration
                    has_subdirs = False
                    for subitem in path_obj.joinpath(child_name).iterdir():
                        if subitem.is_dir():
                            has_subdirs = True
                            break

                    if has_subdirs:
                        # Add placeholder for lazy loading
                        placeholder_id = f"{child_path}_placeholder"
                        pathbrowser_instance.tree.insert(
                            child_path,
                            "end",
                            placeholder_id,
                            text=lang.get("Loading...", pathbrowser_instance),
                            open=False,
                        )

    except (OSError, PermissionError) as e:
        logger.warning("Failed to populate tree node for %s: %s", parent, e)
        # Show user-friendly error in status bar
        pathbrowser_instance.status_var.set(
            f"{lang.get('Cannot access:', pathbrowser_instance)} "
            f"{Path(parent).name}"
        )


def expand_path(pathbrowser_instance, path: str):
    """Expand the tree to show the specified path."""
    # Resolve symlinks to prevent loops on macOS
    # pylint: disable=protected-access
    path = pathbrowser_instance.file_info_manager._resolve_symlink(path)
    path_obj = Path(path)
    if utils.IS_WINDOWS:
        parts = path_obj.parts
        current = parts[0] + "\\"
    else:
        parts = path_obj.parts
        current = "/"

    # Expand path and populate nodes
    for part in parts[1:]:
        if part:
            current = str(Path(current) / part)
            try:
                # Open the node
                pathbrowser_instance.tree.item(current, open=True)
                # Remove any placeholders
                children = pathbrowser_instance.tree.get_children(current)
                for child in children:
                    if child.endswith("_placeholder"):
                        pathbrowser_instance.tree.delete(child)
                # Populate children if not already done
                if not pathbrowser_instance.tree.get_children(current):
                    populate_tree_node(pathbrowser_instance, current)
            except tk.TclError as e:
                logger.debug("Failed to expand path node %s: %s", current, e)

    # Select and highlight current directory
    try:
        pathbrowser_instance.tree.selection_set(path)
        pathbrowser_instance.tree.see(path)
    except tk.TclError as e:
        logger.debug("Failed to select path %s: %s", path, e)


def load_files(pathbrowser_instance):
    """Load files in the current directory with improved performance using itertools."""
    pathbrowser_instance.file_tree.delete(
        *pathbrowser_instance.file_tree.get_children()
    )

    try:
        # Use pathlib for more efficient directory scanning
        path_obj = Path(pathbrowser_instance.state.current_dir)

        # Use itertools for efficient processing
        batch_size = pathbrowser_instance.config.batch_size

        # Create iterator for directory items
        def filtered_items():
            for item in path_obj.iterdir():
                if item.is_dir():
                    # Always include directories
                    yield item
                elif utils.matches_filter(
                    item.name,
                    pathbrowser_instance.config.filetypes,
                    pathbrowser_instance.filter_var.get(),
                    pathbrowser_instance.config.select,
                    lang.get("All files", pathbrowser_instance),
                ):
                    # Only include files that match filter
                    yield item

        # Process items in batches using itertools
        all_items = []
        processed_count = 0

        # Use islice for efficient batching
        item_iterator = filtered_items()
        while True:
            batch = list(islice(item_iterator, batch_size))
            if not batch:
                break

            # Process batch
            for item in batch:
                file_info = pathbrowser_instance.file_info_manager.get_cached_file_info(
                    str(item)
                )
                icon = "📁" if file_info.is_dir else "📄"
                all_items.append(
                    (
                        file_info.name,
                        file_info.path,
                        icon,
                        file_info.size_str,
                        file_info.modified,
                        file_info.file_type,
                        file_info.size_bytes,
                    )
                )
                processed_count += 1

            # Update status for large directories
            if processed_count % (batch_size * 2) == 0:
                pathbrowser_instance.status_var.set(
                    f"{lang.get('Loading files...', pathbrowser_instance)} "
                    f"({processed_count})"
                )
                pathbrowser_instance.update()  # Allow GUI to update

        # Sort and add items efficiently
        all_items = sort_items(pathbrowser_instance, all_items)

        # Batch insert items for better performance
        for i, (name, path, icon, size, modified, file_type, _) in enumerate(all_items):
            pathbrowser_instance.file_tree.insert(
                "",
                "end",
                path,
                text=f"{icon} {name}",
                values=(size, modified, file_type),
            )

            # Update progress for very large directories
            if i % batch_size == 0 and len(all_items) > batch_size * 2:
                pathbrowser_instance.status_var.set(
                    f"{lang.get('Displaying files...', pathbrowser_instance)} "
                    f"({i + 1}/{len(all_items)})"
                )
                pathbrowser_instance.update()

    except (OSError, PermissionError) as e:
        logger.error(
            "Failed to load files for directory %s: %s",
            pathbrowser_instance.state.current_dir,
            e,
        )
        error_msg = (
            f"{lang.get('Error loading files:', pathbrowser_instance)} " f"{str(e)}"
        )
        pathbrowser_instance.status_var.set(error_msg)

        # Show error dialog for permission issues
        if isinstance(e, PermissionError):
            messagebox.showerror(
                master=pathbrowser_instance.winfo_toplevel(),
                message=error_msg,
                title=lang.get("Access Denied", pathbrowser_instance),
            )


def sort_items(pathbrowser_instance, items):
    """Sort items based on current sort column and direction using operator module."""
    if not items:
        return items

    # Define sort keys using operator module for efficiency
    sort_keys = {
        "#0": itemgetter(0),  # name
        "size": lambda x: (
            (0, 0) if x[5] == lang.get("Folder", pathbrowser_instance) else (1, x[6])
        ),
        "modified": lambda x: (
            (0, "") if x[5] == lang.get("Folder", pathbrowser_instance) else (1, x[4])
        ),
        "type": itemgetter(5),  # file_type
    }

    sort_key = sort_keys.get(pathbrowser_instance.state.sort_column, itemgetter(0))

    # Use sorted with key function for efficient sorting
    return sorted(items, key=sort_key, reverse=pathbrowser_instance.state.sort_reverse)


def update_selected_display(pathbrowser_instance):
    """Update the selected files display."""
    if not pathbrowser_instance.state.selected_items:
        pathbrowser_instance.selected_var.set("")
        pathbrowser_instance._update_status()  # pylint: disable=protected-access
        return

    # Get file names from selected items
    files = []
    for item_path in pathbrowser_instance.state.selected_items:
        file_info = pathbrowser_instance.file_info_manager.get_cached_file_info(
            item_path
        )
        if not file_info.is_dir:
            files.append(file_info.name)

            # Set display text based on selection
        if not files:
            # Only directories selected, keep filename entry empty
            pathbrowser_instance.selected_var.set("")
        elif len(files) == 1:
            # Single file
            pathbrowser_instance.selected_var.set(files[0])
        elif len(files) <= 3:
            # Show all file names if 3 or fewer
            pathbrowser_instance.selected_var.set(", ".join(files))
        else:
            # Show first file name with count indication
            pathbrowser_instance.selected_var.set(
                f"{files[0]} (+{len(files) - 1} more)"
            )

    # Update status bar to reflect selection changes
    pathbrowser_instance._update_status()  # pylint: disable=protected-access


def update_status(pathbrowser_instance):
    """Update the status bar."""
    try:
        if pathbrowser_instance.state.selected_items:
            update_selection_status(pathbrowser_instance)
        else:
            update_directory_status(pathbrowser_instance)

    except (OSError, PermissionError) as e:
        logger.error(
            "Access denied for directory %s: %s",
            pathbrowser_instance.state.current_dir,
            e,
        )
        pathbrowser_instance.status_var.set(
            f"Access denied: {Path(pathbrowser_instance.state.current_dir).name}"
        )


def update_selection_status(pathbrowser_instance):
    """Update status bar for selected items."""
    selected_files = 0
    selected_folders = 0
    selected_size = 0
    selected_items_info = []

    # Get file information efficiently using cache
    for item_path in pathbrowser_instance.state.selected_items:
        file_info = pathbrowser_instance.file_info_manager.get_cached_file_info(
            item_path
        )
        selected_items_info.append(file_info)

        if file_info.is_dir:
            selected_folders += 1
        else:
            selected_files += 1
            selected_size += file_info.size_bytes

    # Build selection text
    selection_parts = []
    if selected_folders > 0:
        if selected_folders == 1:
            dir_info = next(info for info in selected_items_info if info.is_dir)
            selection_parts.append(f"📁 {dir_info.name}")
        else:
            selection_parts.append(
                f"📁 {selected_folders} " f"{lang.get('folders', pathbrowser_instance)}"
            )

    if selected_files > 0:
        if selected_files == 1:
            file_info = next(info for info in selected_items_info if not info.is_dir)
            selection_parts.append(file_info.name)
        else:
            selection_parts.append(
                f"{selected_files} {lang.get('files', pathbrowser_instance)}"
            )

    if selection_parts:
        selection_text = ", ".join(selection_parts)
        if selected_files > 0:
            selection_text += f" ({utils.format_size(selected_size)})"
        status_text = f"{lang.get('Selected:', pathbrowser_instance)} {selection_text}"
    else:
        status_text = "No valid selections"

    pathbrowser_instance.status_var.set(status_text)


def update_directory_status(pathbrowser_instance):
    """Update status bar for current directory."""
    try:
        path_obj = Path(pathbrowser_instance.state.current_dir)
        file_count = 0
        folder_count = 0
        total_size = 0

        for item in path_obj.iterdir():
            if item.is_dir():
                folder_count += 1
            else:
                file_count += 1
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    pass

        # Build status text
        status_parts = []
        if folder_count > 0:
            folder_label = lang.get(
                "folder" if folder_count == 1 else "folders", pathbrowser_instance
            )
            folder_text = f"{folder_count} {folder_label}"
            status_parts.append(folder_text)

        if file_count > 0:
            file_label = lang.get(
                "file" if file_count == 1 else "files", pathbrowser_instance
            )
            file_text = f"{file_count} {file_label}"
            status_parts.append(file_text)

        if status_parts:
            status_text = ", ".join(status_parts)
            if file_count > 0:
                status_text += f" ({utils.format_size(total_size)})"
        else:
            status_text = lang.get("Empty folder", pathbrowser_instance)

        pathbrowser_instance.status_var.set(status_text)
    except (OSError, PermissionError) as e:
        logger.error(
            "Access denied for directory %s: %s",
            pathbrowser_instance.state.current_dir,
            e,
        )
        pathbrowser_instance.status_var.set(
            f"Access denied: {Path(pathbrowser_instance.state.current_dir).name}"
        )


def show_context_menu(pathbrowser_instance, event, menu_type="file"):
    """Show context menu for tree or file items."""
    menu = tk.Menu(pathbrowser_instance, tearoff=0)

    if menu_type == "tree":
        selection = pathbrowser_instance.tree.selection()
        if selection:
            selected_path = selection[0]
            file_info = pathbrowser_instance.file_info_manager.get_file_info(
                selected_path
            )
            if file_info.is_dir:
                # Check if node is open
                is_open = pathbrowser_instance.tree.item(selected_path, "open")

                if is_open:
                    menu.add_command(
                        label=lang.get("Collapse", pathbrowser_instance),
                        # pylint: disable=protected-access
                        command=lambda: pathbrowser_instance._collapse_node(None),
                    )
                else:
                    menu.add_command(
                        label=lang.get("Expand", pathbrowser_instance),
                        # pylint: disable=protected-access
                        command=lambda: pathbrowser_instance._expand_node(None),
                    )

                menu.add_command(
                    label=lang.get("Expand All", pathbrowser_instance),
                    # pylint: disable=protected-access
                    command=lambda: pathbrowser_instance._expand_all(selected_path),
                )
                menu.add_separator()
    else:  # file menu
        selection = pathbrowser_instance.file_tree.selection()
        if selection:
            menu.add_command(
                label=lang.get("Open", pathbrowser_instance),
                # pylint: disable=protected-access
                command=pathbrowser_instance._open_selected,
            )
            menu.add_separator()

    menu.add_command(
        label=lang.get("Copy Path", pathbrowser_instance),
        # pylint: disable=protected-access
        command=pathbrowser_instance._copy_path,
    )
    menu.post(event.x_root, event.y_root)
