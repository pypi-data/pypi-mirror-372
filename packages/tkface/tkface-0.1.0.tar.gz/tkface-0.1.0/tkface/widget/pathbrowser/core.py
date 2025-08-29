"""
Core functionality for the PathBrowser widget.

This module provides the main PathBrowser class, data processing, event handling,
and configuration management for the PathBrowser widget.
"""

# pylint: disable=no-member
# The following attributes are dynamically created by view.create_pathbrowser_widgets:
# file_tree, tree, path_var, status_var, up_button, down_button, filter_combo,
# selected_files_entry, selected_var

import logging
import os
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from tkface import lang
from tkface.dialog import messagebox
from tkface.widget.pathbrowser import view

from . import utils
from .manager import FileInfoManager
from .style import get_pathbrowser_theme

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PathBrowserConfig:
    """Configuration for PathBrowser widget."""

    select: str = "file"
    multiple: bool = False
    initialdir: Optional[str] = None
    filetypes: List[Tuple[str, str]] = field(
        default_factory=lambda: [("All files", "*.*")]
    )
    ok_label: str = "ok"
    cancel_label: str = "cancel"
    save_mode: bool = False
    initialfile: Optional[str] = None
    # Performance settings
    max_cache_size: int = 1000
    batch_size: int = 100
    enable_memory_monitoring: bool = True
    show_hidden_files: bool = False
    lazy_loading: bool = True


@dataclass
class PathBrowserState:
    """State management for PathBrowser widget."""

    current_dir: str = field(default_factory=lambda: str(Path.cwd()))
    selected_items: List[str] = field(default_factory=list)
    sort_column: str = "#0"
    sort_reverse: bool = False
    navigation_history: List[str] = field(default_factory=list)
    forward_history: List[str] = field(default_factory=list)
    selection_anchor: Optional[str] = None


class PathBrowser(tk.Frame):
    """
    A path browser widget with directory tree and file list.

    Features:
    - Directory tree (left pane) with icons and refresh
    - File list (right pane) with details view, filtering, sorting, and multiple \
        selection
    - Path navigation bar
    - OK/Cancel buttons at the bottom
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        parent,
        select: str = "file",
        multiple: bool = False,
        initialdir: Optional[str] = None,
        filetypes: Optional[List[Tuple[str, str]]] = None,
        ok_label: str = "ok",
        cancel_label: str = "cancel",
        save_mode: bool = False,
        initialfile: Optional[str] = None,
        config: Optional[PathBrowserConfig] = None,
        **kwargs,
    ):
        """
        Initialize the path browser widget.

        Args:
            parent: Parent widget
            select: Selection mode ("file", "dir", or "both")
            multiple: Allow multiple selection
            initialdir: Initial directory to display
            filetypes: List of file type filters [(description, pattern), ...]
            ok_label: Text for the OK button (e.g., "Open", "Save")
            cancel_label: Text for the Cancel button
            save_mode: Whether this is a save dialog
            initialfile: Initial filename for save mode
            config: Configuration object (overrides individual parameters)
            **kwargs: Additional arguments for Frame
        """
        super().__init__(parent)  # pylint: disable=too-many-positional-arguments
        self.configure(**kwargs)

        # Use config if provided, otherwise use individual parameters
        if config is not None:
            self.config = config
        else:
            self.config = PathBrowserConfig(
                select=select,
                multiple=multiple,
                initialdir=initialdir,
                filetypes=filetypes or [("All files", "*.*")],
                ok_label=ok_label,
                cancel_label=cancel_label,
                save_mode=save_mode,
                initialfile=initialfile,
            )

        # Initialize state
        self.state = PathBrowserState(
            current_dir=self.config.initialdir or str(Path.cwd())
        )

        # Initialize file info manager with config settings
        self.file_info_manager = FileInfoManager(
            self, max_cache_size=self.config.max_cache_size
        )

        # Initialize theme
        self.theme = get_pathbrowser_theme()

        # Create widgets and setup bindings
        # These will create the following members: file_tree, tree,
        # path_var, status_var, up_button, down_button, filter_combo,
        # selected_files_entry, selected_var
        view.create_pathbrowser_widgets(self)
        view.setup_pathbrowser_bindings(self)

        # Load initial directory
        self._load_directory(self.state.current_dir)

        # Initialize navigation buttons state
        self._update_navigation_buttons()
        # Set initial focus to file_tree for keyboard navigation
        self.file_tree.focus_set()
        # Schedule focus setting after a short delay to ensure it takes effect
        self.after(100, self.file_tree.focus_set)

        # Language system is initialized by parent window

        # Start memory monitoring if enabled
        if self.config.enable_memory_monitoring:
            self._schedule_memory_monitoring()

        # pylint: disable=attribute-defined-outside-init
        # The following attributes are created by view.create_pathbrowser_widgets:
        # file_tree, tree, path_var, status_var, up_button, down_button,
        # filter_combo, selected_files_entry, selected_var

    def _init_language(self):
        """Initialize the language system."""
        # This method is deprecated - language is now set by parent window

    def _load_directory(self, path: str):  # pylint: disable=no-member
        """Load and display the specified directory."""
        try:
            # Resolve symlinks to prevent loops on macOS
            # pylint: disable=protected-access
            resolved_path = self.file_info_manager._resolve_symlink(path)
            self.state.current_dir = str(Path(resolved_path).absolute())
            self.path_var.set(self.state.current_dir)

            # Clear cache entries for old directory to free memory
            if hasattr(self, "state") and hasattr(self.state, "current_dir"):
                old_dir = getattr(self.state, "current_dir", None)
                if old_dir and old_dir != self.state.current_dir:
                    # Use improved cache clearing method
                    self.file_info_manager.clear_directory_cache(old_dir)

            view.load_directory_tree(self)
            view.load_files(self)
            self._update_status()
            # Clear selection when changing directory
            self.state.selected_items = []
            view.update_selected_display(self)
            # Update navigation buttons state
            self._update_navigation_buttons()

        except PermissionError as e:
            logger.error("Permission denied for directory %s: %s", path, e)
            error_msg = (
                f"{lang.get('Access denied:', self)} {Path(path).name}\n"
                f"{lang.get('You do not have permission to access this folder.', self)}"
            )
            self.status_var.set(error_msg)
            messagebox.showerror(
                master=self.winfo_toplevel(),
                message=error_msg,
                title=lang.get("Access Denied", self),
            )

        except FileNotFoundError:
            logger.error("Directory not found: %s", path)
            error_msg = (
                f"{lang.get('Directory not found:', self)} {Path(path).name}\n"
                f"{lang.get('The folder may have been moved or deleted.', self)}"
            )
            self.status_var.set(error_msg)
            # Try to navigate to parent directory
            parent_dir = str(Path(path).parent)
            if parent_dir and parent_dir != path:
                self._load_directory(parent_dir)
            else:
                # Fallback to home directory
                home_dir = str(Path.home())
                self._load_directory(home_dir)

        except OSError as e:
            logger.error("Failed to load directory %s: %s", path, e)
            error_msg = (
                f"{lang.get('Error loading directory:', self)} {Path(path).name}\n"
                f"{str(e)}"
            )
            self.status_var.set(error_msg)
            # Try to navigate to parent directory
            parent_dir = str(Path(path).parent)
            if parent_dir and parent_dir != path:
                self._load_directory(parent_dir)
            else:
                # Fallback to home directory
                home_dir = str(Path.home())
                self._load_directory(home_dir)

    def _go_up(self):  # pylint: disable=no-member
        """Navigate to the parent directory."""
        parent_dir = str(Path(self.state.current_dir).parent)
        if parent_dir and parent_dir != self.state.current_dir:
            # Save current directory to forward history before moving up
            self.state.forward_history.append(self.state.current_dir)
            # Clear navigation history when moving to a new branch
            self.state.navigation_history.clear()
            self._load_directory(parent_dir)
            self._update_navigation_buttons()

    def _go_down(self):  # pylint: disable=no-member
        """Navigate to the most recently visited subdirectory."""
        if self.state.forward_history:
            # Save current directory to navigation history before moving forward
            self.state.navigation_history.append(self.state.current_dir)
            # Get the most recent directory from forward history
            next_dir = self.state.forward_history.pop()
            self._load_directory(next_dir)
            self._update_navigation_buttons()
        else:
            self.status_var.set(lang.get("No forward history available", self))

    def _go_to_path(self):  # pylint: disable=no-member
        """Navigate to the path entered in the path bar."""
        path = self.path_var.get()
        # pylint: disable=protected-access
        path = self.file_info_manager._resolve_symlink(path)
        file_info = self.file_info_manager.get_cached_file_info(path)
        if file_info.is_dir:
            self._load_directory(path)

    def _update_navigation_buttons(self):  # pylint: disable=no-member
        """Update the enabled/disabled state of navigation buttons."""
        # Enable/disable up button based on whether we can go up
        parent_dir = str(Path(self.state.current_dir).parent)
        can_go_up = parent_dir and parent_dir != self.state.current_dir
        self.up_button.config(state="normal" if can_go_up else "disabled")

        # Enable/disable down button based on forward history
        can_go_down = len(self.state.forward_history) > 0
        self.down_button.config(state="normal" if can_go_down else "disabled")

    def _update_filter_options(self):  # pylint: disable=no-member
        """Update the filter combobox options."""
        options = []
        all_files_added = False

        # Add "All files" option first if not already in filetypes
        for desc, pattern in self.config.filetypes:
            if desc.lower() == "all files" or pattern == "*.*":
                all_files_added = True
                break

        if not all_files_added:
            options.append(lang.get("All files", self))

        # Add all filetypes
        for desc, pattern in self.config.filetypes:
            options.append(f"{desc} ({pattern})")

        self.filter_combo["values"] = options
        # Set default to first filetype (not "All files" if possible)
        if options:
            if len(options) > 1 and options[0] == lang.get("All files", self):
                # If "All files" is first, use the second option (first filetype)
                self.filter_combo.set(options[1])
            else:
                # Otherwise use the first option
                self.filter_combo.set(options[0])

    def _on_tree_select(self, event):  # pylint: disable=unused-argument,no-member
        """Handle tree selection."""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]

            # pylint: disable=protected-access
            resolved_selected_path = self.file_info_manager._resolve_symlink(
                selected_path
            )
            file_info = self.file_info_manager.get_cached_file_info(
                resolved_selected_path
            )
            if file_info.is_dir:
                # Only load directory if it's different from current
                if resolved_selected_path != self.state.current_dir:
                    # Clear forward history when navigating to a new directory
                    self.state.forward_history.clear()
                    self._load_directory(resolved_selected_path)

                # Update selection display for directory selection
                if self.config.select in ["dir", "both"]:
                    self.state.selected_items = [resolved_selected_path]
                    view.update_selected_display(self)
                    # Update status bar for directory selection
                    self._update_status()

    def _on_tree_open(self, event):  # pylint: disable=unused-argument,no-member
        """Handle tree node expansion."""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]
            file_info = self.file_info_manager.get_file_info(selected_path)
            if file_info.is_dir:
                # Remove placeholder and populate children
                children = self.tree.get_children(selected_path)
                for child in children:
                    if child.endswith("_placeholder"):
                        self.tree.delete(child)

                # Populate children if not already done
                if not self.tree.get_children(selected_path):
                    view.populate_tree_node(self, selected_path)

    def _on_tree_right_click(self, event):  # pylint: disable=unused-argument,no-member
        """Handle tree right click."""
        # Get clicked item
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            view.show_context_menu(self, event, "tree")

    def _on_file_right_click(self, event):  # pylint: disable=unused-argument,no-member
        """Handle file list right click."""
        # Get clicked item
        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            view.show_context_menu(self, event, "file")

    def _copy_path(self):  # pylint: disable=no-member
        """Copy selected path to clipboard."""
        selection = self.tree.selection() or self.file_tree.selection()
        if selection:
            path = selection[0]
            self.clipboard_clear()
            self.clipboard_append(path)

    def _open_selected(self):  # pylint: disable=no-member
        """Open selected file/directory."""
        selection = self.file_tree.selection()
        if selection:
            item_id = selection[0]
            # pylint: disable=protected-access
            item_id = self.file_info_manager._resolve_symlink(item_id)
            file_info = self.file_info_manager.get_cached_file_info(item_id)
            if file_info.is_dir:
                # Clear forward history when navigating to a new directory
                self.state.forward_history.clear()
                self._load_directory(item_id)
            else:
                # Try to open file with default application
                if not utils.open_file_with_default_app(item_id):
                    logger.warning("Failed to open file %s", item_id)

    # pylint: disable=unused-argument,no-member
    def _expand_node(self, event):
        """Expand the currently selected tree node."""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]
            file_info = self.file_info_manager.get_cached_file_info(selected_path)
            if file_info.is_dir:
                self.tree.item(selected_path, open=True)
                # Remove placeholder and populate if needed
                children = self.tree.get_children(selected_path)
                for child in children:
                    if child.endswith("_placeholder"):
                        self.tree.delete(child)
                if not self.tree.get_children(selected_path):
                    view.populate_tree_node(self, selected_path)
        return "break"  # Prevent default behavior

    # pylint: disable=unused-argument,no-member
    def _collapse_node(self, event):
        """Collapse the currently selected tree node."""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]
            file_info = self.file_info_manager.get_cached_file_info(selected_path)
            if file_info.is_dir:
                self.tree.item(selected_path, open=False)
        return "break"  # Prevent default behavior

    # pylint: disable=unused-argument,no-member
    def _toggle_selected_node(self, event):
        """Toggle the expansion state of the currently selected tree node."""
        selection = self.tree.selection()
        if selection:
            selected_path = selection[0]
            file_info = self.file_info_manager.get_cached_file_info(selected_path)
            if file_info.is_dir:
                is_open = self.tree.item(selected_path, "open")
                if is_open:
                    self._collapse_node(event)
                else:
                    self._expand_node(event)
        return "break"  # Prevent default behavior

    def _on_file_tree_click(self, event):  # pylint: disable=unused-argument,no-member
        """Handle file tree click to ensure focus."""
        # Ensure file_tree has focus for keyboard events
        self.file_tree.focus_set()

    def _on_file_frame_click(self, event):  # pylint: disable=unused-argument,no-member
        """Handle file frame click to ensure focus."""
        # Ensure file_tree has focus for keyboard events
        self.file_tree.focus_set()

    def _handle_up_key(self, event):  # pylint: disable=unused-argument,no-member
        """Handle Up key globally."""
        # Check if file_tree has focus or if we should handle it anyway
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._move_selection_up(event)
        return None

    def _handle_down_key(self, event):  # pylint: disable=unused-argument,no-member
        """Handle Down key globally."""
        # Check if file_tree has focus or if we should handle it anyway
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._move_selection_down(event)
        return None

    def _handle_home_key(self, event):  # pylint: disable=unused-argument,no-member
        """Handle Home key globally."""
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._move_to_first(event)
        return None

    def _handle_end_key(self, event):  # pylint: disable=unused-argument,no-member
        """Handle End key globally."""
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._move_to_last(event)
        return None

    def _handle_shift_up_key(self, event):  # pylint: disable=unused-argument,no-member
        """Handle Shift+Up key globally."""
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._extend_selection_up(event)
        return None

    # pylint: disable=unused-argument,no-member
    def _handle_shift_down_key(self, event):
        """Handle Shift+Down key globally."""
        focused_widget = self.focus_get()
        if focused_widget in (self.file_tree, self):
            return self._extend_selection_down(event)
        return None

    # pylint: disable=unused-argument,no-member
    def _move_selection_up(self, event):
        """Move selection up in the file list."""
        return self._move_selection(event, direction=-1)

    # pylint: disable=unused-argument,no-member
    def _move_selection_down(self, event):
        """Move selection down in the file list."""
        return self._move_selection(event, direction=1)

    # pylint: disable=unused-argument,no-member
    def _move_selection(self, event, direction):
        """Move selection in the specified direction.

        Args:
            event: The key event
            direction: Direction to move (-1 for up, 1 for down)
        """
        current_selection = self.file_tree.selection()
        if not current_selection:
            # If nothing is selected, select the first item
            children = self.file_tree.get_children()
            if children:
                self.file_tree.selection_set(children[0])
                self.file_tree.see(children[0])
            return "break"

        # Get current selection index
        children = self.file_tree.get_children()
        if not children:
            return "break"

        current_index = children.index(current_selection[0])
        new_index = current_index + direction

        # Check bounds
        if direction == -1 and new_index >= 0:
            # Moving up: check lower bound
            valid_move = True
        elif direction == 1 and new_index < len(children):
            # Moving down: check upper bound
            valid_move = True
        else:
            valid_move = False

        if valid_move:
            # Move to new item
            new_selection = children[new_index]
            self.file_tree.selection_set(new_selection)
            self.file_tree.see(new_selection)
            # Reset anchor for single selection
            self.state.selection_anchor = None
            # Update selection state
            self._on_file_select(None)

        return "break"

    def _move_to_first(self, event):  # pylint: disable=unused-argument,no-member
        """Move selection to the first item in the file list."""
        return self._move_to_edge(event, edge="first")

    def _move_to_last(self, event):  # pylint: disable=unused-argument,no-member
        """Move selection to the last item in the file list."""
        return self._move_to_edge(event, edge="last")

    def _move_to_edge(self, event, edge):  # pylint: disable=unused-argument,no-member
        """Move selection to the specified edge of the file list.

        Args:
            event: The key event
            edge: Edge to move to ("first" or "last")
        """
        children = self.file_tree.get_children()
        if children:
            if edge == "first":
                target_item = children[0]
            else:  # edge == "last"
                target_item = children[-1]

            self.file_tree.selection_set(target_item)
            self.file_tree.see(target_item)
            # Update selection state
            self._on_file_select(None)
        return "break"

    def _extend_selection_up(self, event):  # pylint: disable=unused-argument,no-member
        """Extend selection upward with Shift+Up."""
        return self._extend_selection_range(event, direction=-1)

    # pylint: disable=unused-argument,no-member
    def _extend_selection_down(self, event):
        """Extend selection downward with Shift+Down."""
        return self._extend_selection_range(event, direction=1)

    # pylint: disable=no-member
    def _extend_selection_range(self, event, direction):
        """Extend selection range in the specified direction.

        Args:
            event: The key event
            direction: Direction to extend (-1 for up, 1 for down)
        """
        if not self.config.multiple:
            if direction == -1:
                return self._move_selection_up(event)
            return self._move_selection_down(event)

        current_selection = self.file_tree.selection()
        children = self.file_tree.get_children()

        if not children:
            return "break"

        if not current_selection:
            # If nothing is selected, select the first item
            self.file_tree.selection_set(children[0])
            self.file_tree.see(children[0])
            self._on_file_select(None)
            return "break"

        # Use stored anchor or set it if not available
        if self.state.selection_anchor is None:
            self.state.selection_anchor = current_selection[0]

        anchor_item = self.state.selection_anchor
        anchor_index = children.index(anchor_item)

        # For range selection, track the current end of selection
        # We'll use the last selected item as the current end
        if len(current_selection) == 1:
            # Single selection - use it as both anchor and current end
            current_end = current_selection[0]
        else:
            # Multiple selection - find the end that's furthest from anchor
            anchor_index = children.index(anchor_item)
            current_end = None
            max_distance = 0

            for item in current_selection:
                item_index = children.index(item)
                distance = abs(item_index - anchor_index)
                if distance > max_distance:
                    max_distance = distance
                    current_end = item

        current_end_index = children.index(current_end)

        # Calculate new end index
        new_end_index = current_end_index + direction

        # Check bounds
        if direction == -1 and new_end_index >= 0:
            # Moving up: check lower bound
            valid_range = True
        elif direction == 1 and new_end_index < len(children):
            # Moving down: check upper bound
            valid_range = True
        else:
            valid_range = False

        if valid_range:
            # Create range selection from anchor to new end
            start_index = min(anchor_index, new_end_index)
            end_index = max(anchor_index, new_end_index)
            range_items = children[start_index : end_index + 1]

            # Set the new selection range
            self.file_tree.selection_set(range_items)
            self.file_tree.see(children[new_end_index])

            # Update selection state without calling _on_file_select to avoid recursion
            # Just update the internal state
            self.state.selected_items = list(range_items)
            view.update_selected_display(self)
            self._update_status()

        return "break"

    def _expand_all(self, path):  # pylint: disable=no-member
        """Recursively expand all subdirectories."""
        file_info = self.file_info_manager.get_cached_file_info(path)
        if file_info.is_dir:
            # Expand current node
            self.tree.item(path, open=True)
            # Remove placeholders and populate
            children = self.tree.get_children(path)
            for child in children:
                if child.endswith("_placeholder"):
                    self.tree.delete(child)
            if not self.tree.get_children(path):
                view.populate_tree_node(self, path)

            # Recursively expand children
            children = self.tree.get_children(path)
            for child in children:
                child_info = self.file_info_manager.get_cached_file_info(child)
                if child_info.is_dir:
                    self._expand_all(child)

    def _on_file_select(self, event):  # pylint: disable=unused-argument,no-member
        """Handle file list selection."""
        selection = self.file_tree.selection()
        self.state.selected_items = []

        for item_id in selection:
            file_info = self.file_info_manager.get_cached_file_info(item_id)

            if file_info.is_dir:
                if self.config.select in ["dir", "both"]:
                    self.state.selected_items.append(item_id)
                # Also add directories in file mode for validation in _on_ok
                elif self.config.select == "file":
                    self.state.selected_items.append(item_id)
            else:
                if self.config.select in ["file", "both"]:
                    self.state.selected_items.append(item_id)

        # Set anchor for range selection if not already set
        # Only set anchor for single selection, not for range selection
        if selection and self.state.selection_anchor is None and len(selection) == 1:
            self.state.selection_anchor = selection[0]

        view.update_selected_display(self)
        self._update_status()  # Update status bar when selection changes
        # Clear focus from entry when file is selected
        self.focus_set()

    def _sort_files(self, column):  # pylint: disable=no-member
        """Sort files by the specified column."""
        if self.state.sort_column == column:
            self.state.sort_reverse = not self.state.sort_reverse
        else:
            self.state.sort_column = column
            self.state.sort_reverse = False

        # Update heading to show sort direction
        for col in ["#0", "size", "modified", "type"]:
            if col == column:
                direction = " ▼" if self.state.sort_reverse else " ▲"
                self.file_tree.heading(
                    col,
                    text=self.file_tree.heading(col)["text"]
                    .replace(" ▲", "")
                    .replace(" ▼", "")
                    + direction,
                )
            else:
                # Remove sort indicators from other columns
                text = self.file_tree.heading(col)["text"]
                text = text.replace(" ▲", "").replace(" ▼", "")
                self.file_tree.heading(col, text=text)

        # Reload files with new sort order
        view.load_files(self)

    def _on_filename_focus(self, event):  # pylint: disable=unused-argument,no-member
        """Handle filename entry focus - select all text."""
        self.selected_files_entry.select_range(0, tk.END)

    def _on_file_double_click(self, event):  # pylint: disable=unused-argument,no-member
        """Handle file double-click."""
        selection = self.file_tree.selection()
        if selection:
            item_id = selection[0]
            # pylint: disable=protected-access
            item_id = self.file_info_manager._resolve_symlink(item_id)
            file_info = self.file_info_manager.get_cached_file_info(item_id)

            if file_info.is_dir:
                # Clear forward history when navigating to a new directory
                self.state.forward_history.clear()
                self._load_directory(item_id)
            elif self.config.select == "file" and not self.config.multiple:
                self._on_ok()

    def _on_filter_change(self, event):  # pylint: disable=unused-argument,no-member
        """Handle filter change."""
        view.load_files(self)

    def _on_ok(self, event=None):  # pylint: disable=unused-argument,no-member
        """Handle OK button click."""
        if self.config.save_mode:
            # In save mode, validate filename
            filename = self.selected_var.get().strip()
            if not filename:
                # Show error if no filename is entered
                error_msg = lang.get("Please enter a filename.", self)
                messagebox.showerror(
                    master=self.winfo_toplevel(),
                    message=error_msg,
                    title=lang.get("Error", self),
                )
                return

            # Check if file already exists
            full_path = os.path.join(self.state.current_dir, filename)
            if os.path.exists(full_path):
                # Ask for confirmation to overwrite
                overwrite_msg = lang.get(
                    "File already exists. Do you want to overwrite it?", self
                )
                if not messagebox.askyesno(
                    master=self.winfo_toplevel(),
                    message=overwrite_msg,
                    title=lang.get("Confirm Overwrite", self),
                ):
                    return

            self.event_generate("<<PathBrowserOK>>")
        else:
            # Get the filename from the text box
            filename = self.selected_var.get().strip()

            # Set selected items if needed
            if not self.state.selected_items and self.config.select in ["dir", "both"]:
                # If nothing selected and we're in dir mode, select current directory
                self.state.selected_items = [self.state.current_dir]

            # Validate selection if we have items
            if self.state.selected_items and self.config.select == "file":
                if self._has_directory_selection():
                    self._show_directory_error()
                    return

            self.event_generate("<<PathBrowserOK>>")

    def _has_directory_selection(self) -> bool:  # pylint: disable=no-member
        """Check if any selected items are directories."""
        return any(
            self.file_info_manager.get_cached_file_info(item_path).is_dir
            for item_path in self.state.selected_items
        )

    def _show_directory_error(self):  # pylint: disable=no-member
        """Show error message for directory selection in file mode."""
        error_msg = (
            lang.get("Directory selected.", self)
            + "\n"
            + lang.get("Please select a file.", self)
        )
        messagebox.showerror(
            master=self.winfo_toplevel(),
            message=error_msg,
            title=lang.get("Error", self),
        )

    def _on_cancel(self, event=None):  # pylint: disable=unused-argument,no-member
        """Handle Cancel button click."""
        self.state.selected_items = []
        view.update_selected_display(self)
        self._update_status()  # Update status bar when selection is cleared
        self.event_generate("<<PathBrowserCancel>>")

    def _update_status(self):  # pylint: disable=no-member
        """Update the status bar."""
        view.update_status(self)

    def _add_extension_if_needed(self, filename: str) -> str:
        """Add file extension if not present and filetypes are available."""
        current_filter = None
        if hasattr(self, "filter_var"):
            current_filter = self.filter_var.get()
        return utils.add_extension_if_needed(
            filename, self.config.filetypes, current_filter
        )

    def get_selection(self) -> List[str]:
        """
        Get the currently selected items.

        Returns:
            List of selected file/directory paths
        """
        if self.config.save_mode:
            # In save mode, get the filename from the entry field
            filename = self.selected_var.get().strip()
            if filename:
                filename = self._add_extension_if_needed(filename)
                full_path = os.path.join(self.state.current_dir, filename)
                return [full_path]
            return []
        return self.state.selected_items.copy()

    def set_initial_directory(self, path: str):
        """
        Set the initial directory to display.

        Args:
            path: Directory path to display
        """
        file_info = self.file_info_manager.get_file_info(path)
        if file_info.is_dir:
            self._load_directory(path)

    # pylint: disable=no-member
    def set_file_types(self, filetypes: List[Tuple[str, str]]):
        """
        Set the file type filters.

        Args:
            filetypes: List of file type filters [(description, pattern), ...]
        """
        self.config.filetypes = filetypes
        self._update_filter_options()
        view.load_files(self)

    def _schedule_memory_monitoring(self):  # pylint: disable=no-member
        """Schedule periodic memory monitoring."""
        if self.config.enable_memory_monitoring:
            self._check_memory_usage()
            # Check every 30 seconds
            self.after(30000, self._schedule_memory_monitoring)

    def _check_memory_usage(self):  # pylint: disable=no-member
        """Check memory usage and log if high."""
        memory_usage = self.file_info_manager.get_memory_usage_estimate()
        cache_size = self.file_info_manager.get_cache_size()

        # Log memory usage for debugging
        if memory_usage > 10 * 1024 * 1024:  # 10MB
            logger.info(
                "PathBrowser memory usage: %d bytes, cache size: %d items",
                memory_usage,
                cache_size,
            )

        # Auto-cleanup if memory usage is very high
        if memory_usage > 50 * 1024 * 1024:  # 50MB
            logger.warning("High memory usage detected, clearing old cache entries")
            self.file_info_manager.clear_cache()

    def get_performance_stats(self) -> dict:
        """Get performance statistics for debugging."""
        return utils.get_performance_stats(
            self.file_info_manager.get_cache_size(),
            self.file_info_manager.get_memory_usage_estimate(),
            self.state.current_dir,
            len(self.state.selected_items),
        )

    def optimize_performance(self):  # pylint: disable=no-member
        """Manually trigger performance optimization."""
        # Clear old cache entries
        old_memory = self.file_info_manager.get_memory_usage_estimate()
        self.file_info_manager.clear_cache()
        new_memory = self.file_info_manager.get_memory_usage_estimate()

        logger.info(
            "Performance optimization: freed %d bytes of memory",
            old_memory - new_memory,
        )

        # Reload current directory with fresh cache
        self._load_directory(self.state.current_dir)
