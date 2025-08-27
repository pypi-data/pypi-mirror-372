#!/usr/bin/env python3
"""
Context menu UI components.

This module provides UI components for context menu operations,
including backup selection and restoration interfaces.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich import print

from ..common.console import (
    LogLevel,
    print_error,
    print_info,
    print_pattern,
    print_success,
)
from ..common.panels import create_panel
from ..common.prompts import confirm, prompt_choice


class ContextMenuUI:
    """UI components for context menu operations."""

    @staticmethod
    def show_backup_selection_menu(
        backup_dir: Path,
        verbose: bool = False,  # noqa: ARG004
    ) -> Optional[Path]:
        """
        Show interactive menu for selecting a backup file to restore.

        Args:
            backup_dir: Directory containing backup files
            verbose: Enable verbose output

        Returns:
            Selected backup file path or None if cancelled
        """
        # Find all backup files
        backup_files = list(backup_dir.glob("context_menu_backup_*.json"))
        if not backup_files:
            print_error("No context menu backups found")
            print_info(f"Checked directory: {backup_dir}")
            return None

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        print_info("Available context menu backups:")
        print("")

        # Display backup options
        for i, file in enumerate(backup_files, 1):
            try:
                stat = file.stat()
                modified_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                size_kb = stat.st_size / 1024

                # Try to read backup info
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                print_info(f"  {i}. {file.name}")
                print_info(f"     📅 {modified_date} | 📦 {size_kb:.1f} KB{info}")

            except Exception as e:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading backup {file.name}: {e}"
                )
                continue

        print("")

        # Create backup file choices
        backup_choices = []
        for file in backup_files:
            try:
                size_kb = file.stat().st_size / 1024
                modified_date = datetime.fromtimestamp(file.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Try to read entry count from backup
                info = ""
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                choice_text = (
                    f"{file.name} - 📅 {modified_date} | 📦 {size_kb:.1f} KB{info}"
                )
                backup_choices.append(choice_text)

            except Exception as e:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading backup {file.name}: {e}"
                )
                continue

        # Show selection menu
        try:
            selected_choice = prompt_choice(
                "Choose a backup to restore:", backup_choices
            )

            # Find the corresponding file
            selected_index = backup_choices.index(selected_choice)
            selected_file = backup_files[selected_index]

            return selected_file

        except (KeyboardInterrupt, ValueError):
            print_info("📤 Restore cancelled")
            return None

    @staticmethod
    def confirm_restore_operation(backup_file: Path) -> bool:
        """
        Ask user to confirm the restore operation.

        Args:
            backup_file: Path to the backup file to restore

        Returns:
            True if user confirms, False otherwise
        """
        print_info(f"Selected backup: {backup_file.name}")

        # Show backup details
        try:
            with open(backup_file, encoding="utf-8") as f:
                data = json.load(f)

            entry_count = len(data.get("entries", []))
            timestamp = data.get("timestamp", "Unknown")

            # Format timestamp for display
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:  # noqa: E722
                formatted_time = timestamp

            details_panel = create_panel(
                f"""Backup Details:
• File: {backup_file.name}
• Entries: {entry_count}
• Created: {formatted_time}
• Size: {backup_file.stat().st_size / 1024:.1f} KB""",
                title="Backup Information",
                border_style="blue",
                style="bright_blue",
                padding=(1, 1),
                width=60,
            )
            print("")
            print(details_panel)
            print("")

        except Exception as e:
            print_pattern(
                LogLevel.DEBUG, "SYSTEM", f"Could not read backup details: {e}"
            )

        # Ask for confirmation
        return confirm(
            "This will overwrite current context menu entries. Proceed?", default=False
        )

    @staticmethod
    def show_restore_success(backup_file: Path, entry_count: int) -> None:
        """
        Show success message after restore operation.

        Args:
            backup_file: Path to the restored backup file
            entry_count: Number of entries restored
        """
        print_success("Context menu restored successfully!")
        print_info(f"Restored from: {backup_file.name}")

        # Show helpful tip panel
        tip_content = f"""Context menu restore completed successfully.

• Restored from: {backup_file.name}
• {entry_count} entries restored
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the restored entries"""

        tip_panel = create_panel(
            tip_content,
            title="Restore Complete",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        print("")
        print(tip_panel)
        print("")

    @staticmethod
    def show_backup_success(backup_file: str, entry_count: int) -> None:
        """
        Show success message after backup operation.

        Args:
            backup_file: Path to the created backup file
            entry_count: Number of entries backed up
        """
        print_success("Backup completed successfully!")
        print_info(f"📄 Backup saved to: {backup_file}")
        print_info(f"📦 {entry_count} entries backed up")

        # Show helpful tip panel
        tip_content = f"""Context menu backup completed successfully.

• Backup file: {backup_file}
• {entry_count} entries backed up
• Use this backup to restore context menu entries if needed
• You can specify a custom backup location with --output"""

        tip_panel = create_panel(
            tip_content,
            title="Backup Information",
            border_style="yellow",
            style="bright_yellow",
            padding=(1, 1),
            width=80,
        )
        print("")
        print(tip_panel)
        print("")

    @staticmethod
    def show_register_success(label: str, registry_key: str) -> None:
        """
        Show success message after registration operation.

        Args:
            label: Display label of the registered entry
            registry_key: Registry key name
        """
        print_success(f"Tool '{label}' registered successfully in context menu")
        print_info(f"Registry key: {registry_key}")

        # Show helpful tip panel
        tip_content = """Right-click in any folder to see your new context menu entry.

• The entry will appear in both folder and background context menus
• Use 'womm context list' to see all registered entries
• Use 'womm context unregister --remove <key>' to remove entries later"""

        tip_panel = create_panel(
            tip_content,
            title="Context Menu Usage",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        print("")
        print(tip_panel)
        print("")

    @staticmethod
    def show_unregister_success(registry_key: str) -> None:
        """
        Show success message after unregistration operation.

        Args:
            registry_key: Registry key name that was removed
        """
        print_success(f"Entry '{registry_key}' removed successfully from context menu")

        # Show helpful tip panel
        tip_content = """Context menu entry has been removed successfully.

• Changes will be visible after refreshing File Explorer
• Use 'womm context list' to verify the removal
• Use 'womm context register' to add new entries"""

        tip_panel = create_panel(
            tip_content,
            title="Unregistration Complete",
            border_style="green",
            style="bright_green",
            padding=(1, 1),
            width=80,
        )
        print("")
        print(tip_panel)
        print("")

    @staticmethod
    def show_list_commands() -> None:
        """Show helpful commands panel after listing entries."""
        tip_content = """Context menu management commands:

• womm context register --target <file> --label "<name>" - Add new entry
• womm context unregister --remove <key> - Remove existing entry
• womm context backup - Create backup of current entries
• womm context restore - Restore entries from backup"""

        tip_panel = create_panel(
            tip_content,
            title="Context Menu Commands",
            border_style="blue",
            style="bright_blue",
            padding=(1, 1),
            width=80,
        )
        print("")
        print(tip_panel)
        print("")
