#!/usr/bin/env python3
"""
Table utilities using Rich for beautiful table output.
"""

# IMPORTS
########################################################
# Standard library imports
from typing import Any, Dict, List

# Third-party imports
from rich.console import Console
from rich.table import Table

# Local imports
# (None for this file)


# CONFIGURATION
########################################################
# Global variables and settings

console = Console()


# MAIN FUNCTIONS
########################################################
# Core table creation functionality


def create_table(
    title: str,
    columns: List[str],
    rows: List[List[Any]],
    show_header: bool = True,
    **kwargs,
) -> Table:
    """Create a Rich table with the given data."""
    table = Table(title=title, show_header=show_header, **kwargs)

    # Add columns
    for column in columns:
        table.add_column(column, style="cyan", no_wrap=True)

    # Add rows
    for row in rows:
        table.add_row(*[str(cell) for cell in row])

    return table


# UTILITY FUNCTIONS
########################################################
# Helper functions for specific table types


def create_status_table(
    title: str, data: List[Dict[str, Any]], status_column: str = "Status", **kwargs
) -> Table:
    """Create a status table with colored status indicators."""
    if not data:
        return create_table(title, ["No data"], [[]])

    # Get columns from first row
    columns = list(data[0].keys())

    table = Table(title=title, show_header=True, **kwargs)

    # Add columns
    for column in columns:
        if column == status_column:
            table.add_column(column, style="bold", no_wrap=True)
        else:
            table.add_column(column, style="cyan", no_wrap=True)

    # Add rows with status styling
    for row_data in data:
        row = []
        for column in columns:
            value = str(row_data[column])
            if column == status_column:
                if "success" in value.lower() or "ok" in value.lower():
                    row.append(f"✅ {value}")
                elif "error" in value.lower() or "fail" in value.lower():
                    row.append(f"❌ {value}")
                elif "warning" in value.lower():
                    row.append(f"⚠️ {value}")
                else:
                    row.append(f"ℹ️ {value}")
            else:
                row.append(value)
        table.add_row(*row)

    return table


def create_dependency_table(dependencies: Dict[str, str]) -> Table:
    """Create a table for displaying dependencies."""
    table = Table(title="Dependencies", show_header=True)
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Version", style="green", no_wrap=True)
    table.add_column("Status", style="bold", no_wrap=True)

    for tool, version in dependencies.items():
        if version:
            table.add_row(tool, version, "✅ Available")
        else:
            table.add_row(tool, "N/A", "❌ Missing")

    return table


def create_command_table(commands: List[Dict[str, str]]) -> Table:
    """Create a table for displaying available commands."""
    table = Table(title="Available Commands", show_header=True)
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Category", style="yellow", no_wrap=True)

    for cmd in commands:
        table.add_row(
            cmd.get("command", ""), cmd.get("description", ""), cmd.get("category", "")
        )

    return table


def create_dictionary_table(dictionaries: List[Dict[str, Any]]) -> Table:
    """Create a table for displaying CSpell dictionaries."""
    table = Table(title="CSpell Dictionaries", show_header=True)
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Words", style="green", no_wrap=True)
    table.add_column("Size", style="yellow", no_wrap=True)
    table.add_column("Status", style="bold", no_wrap=True)

    for dict_info in dictionaries:
        file_name = dict_info.get("file", "")
        word_count = dict_info.get("words", 0)
        file_size = dict_info.get("size", "N/A")
        status = dict_info.get("status", "Available")

        # Format status with emoji
        if "available" in status.lower():
            status_display = "✅ Available"
        elif "error" in status.lower():
            status_display = "❌ Error"
        else:
            status_display = f"ℹ️ {status}"

        table.add_row(file_name, str(word_count), str(file_size), status_display)

    return table


def create_backup_table(backups: List[Dict[str, Any]]) -> Table:
    """Create a table for displaying PATH backup information."""
    table = Table(title="PATH Backups", show_header=True)
    table.add_column("Backup File", style="cyan", no_wrap=True)
    table.add_column("Size", style="green", no_wrap=True)
    table.add_column("Modified", style="yellow", no_wrap=True)
    table.add_column("Description", style="white")

    for backup in backups:
        # Format size
        size = backup.get("size", 0)
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size // 1024} KB"
        else:
            size_str = f"{size // (1024 * 1024)} MB"

        # Truncate description if too long
        description = backup.get("description", "No description")
        if len(description) > 50:
            description = description[:47] + "..."

        table.add_row(
            backup.get("name", ""), size_str, backup.get("modified", ""), description
        )

    return table
