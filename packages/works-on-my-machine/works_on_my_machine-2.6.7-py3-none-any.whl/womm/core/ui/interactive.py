#!/usr/bin/env python3
"""
Interactive UI components for Works On My Machine.
Provides interactive menus and dialogs using InquirerPy.
"""

# IMPORTS
########################################################
# Standard library imports
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

# Third-party imports
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from prompt_toolkit.styles import Style

# Local imports
# (None for this file)


# MAIN CLASS
########################################################
# Core interactive menu functionality


class InteractiveMenu:
    """Interactive menu with selection using InquirerPy."""

    def __init__(
        self,
        title: str = "Menu",
        border_style: str = "cyan",
        pointer: str = "→",
        instruction: Optional[str] = None,
        style: Optional[Style] = None,
    ):
        """Initialize the interactive menu.

        Args:
            title: Menu title
            border_style: Kept for compatibility (Rich panels)
            pointer: Pointer symbol for selections
            instruction: Optional instruction text displayed under the question
            style: Optional PromptToolkit Style for colors/formatting
        """
        self.title = title
        self.border_style = border_style
        self.pointer = pointer
        self.instruction = instruction
        self.style = style

    # PUBLIC METHODS
    ########################################################
    # Main interface methods for interactive menus

    def select_from_list(
        self,
        items: List[Dict[str, Any]],
        display_func: Optional[Callable[[Dict[str, Any]], str]] = None,
        default_index: int = 0,  # noqa: ARG002
        width: int = 80,  # noqa: ARG002
    ) -> Optional[Dict[str, Any]]:
        """Display an interactive menu and return the selected item.

        Args:
            items: List of items to display
            display_func: Function to format each item for display
            default_index: Default selected index (ignored with InquirerPy)
            width: Menu width (ignored with InquirerPy)

        Returns:
            Selected item or None if cancelled
        """
        if not items:
            return None

        # Format choices for display
        choices = []
        for item in items:
            display_text = display_func(item) if display_func else str(item)
            choices.append(display_text)

        try:
            # Use InquirerPy for selection
            choices_objects = [Choice(value=choice, name=choice) for choice in choices]
            selected_text = inquirer.select(
                message=self.title,
                choices=choices_objects,
                pointer=self.pointer,
                instruction=self.instruction,
                style=self.style,
            ).execute()

            if selected_text is None:
                return None

            # Find the corresponding item
            for i, choice in enumerate(choices):
                if choice == selected_text:
                    return items[i]

            return None

        except KeyboardInterrupt:
            return None

    def select_multiple_from_list(
        self,
        items: List[Dict[str, Any]],
        display_func: Optional[Callable[[Dict[str, Any]], str]] = None,
        checked_items: Optional[List[str]] = None,  # noqa: ARG002 (kept for API parity)
        disabled_items: Optional[List[str]] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        """Display an interactive multiple selection menu and return selected items.

        Args:
            items: List of items to display
            display_func: Function to format each item for display
            checked_items: (unused) kept for API parity
            disabled_items: List of item keys that should be considered installed
                            and therefore hidden from selection

        Returns:
            List of selected items or None if cancelled
        """
        if not items:
            return []

        # Format choices for InquirerPy with checkbox logic
        choices = []
        for item in items:
            display_text = display_func(item) if display_func else str(item)

            # Determine if item should be hidden (already installed)
            item_key = item.get("key", str(item))
            is_disabled = disabled_items and item_key in disabled_items

            # Skip already installed items (don't show them in the selection)
            if is_disabled:
                continue

            # Create InquirerPy Choice only for non-installed items
            choice = Choice(value=item, name=display_text)
            choices.append(choice)

        try:
            # Use InquirerPy for multiple selection
            selected_items = inquirer.checkbox(
                message=self.title,
                choices=choices,
                pointer=self.pointer,
                instruction=self.instruction,
                style=self.style,
            ).execute()

            if selected_items is None:
                return None

            return selected_items

        except KeyboardInterrupt:
            return None

    def confirm_action(
        self, message: str = "Confirm action", default_yes: bool = True
    ) -> bool:
        """Display a confirmation dialog.

        Args:
            message: Confirmation message
            default_yes: Whether "Yes" should be the default selection

        Returns:
            True if confirmed, False if cancelled or denied
        """
        try:
            # Use InquirerPy for confirmation
            result = inquirer.confirm(
                message=message,
                default=default_yes,
                style=self.style,
            ).execute()

            return result if result is not None else False

        except KeyboardInterrupt:
            return False

    # PRIVATE METHODS
    ########################################################


# UTILITY FUNCTIONS
########################################################
# Helper functions for formatting and display


def format_backup_item(backup_info: Dict[str, Any]) -> str:
    """Format a backup item for display in the menu.

    Args:
        backup_info: Backup information dictionary

    Returns:
        Formatted string for display
    """
    file_info = f"{backup_info['file'].name} ({backup_info['path_entries']} entries)"
    date_info = datetime.fromtimestamp(backup_info["file"].stat().st_mtime).strftime(
        "%Y-%m-%d %H:%M"
    )
    return f"{file_info} - {date_info}"
