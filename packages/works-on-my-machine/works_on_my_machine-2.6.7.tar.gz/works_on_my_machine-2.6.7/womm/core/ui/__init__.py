#!/usr/bin/env python3
"""
User Interface module using Rich for beautiful terminal output.
"""

# Import and expose common Rich utilities
from .common.console import (
    LogLevel,
    console,
    get_log_level,
    print_command,
    print_config,
    print_deps,
    print_detect,
    print_error,
    print_header,
    print_info,
    print_install,
    print_pattern,
    print_result,
    print_separator,
    print_success,
    print_system,
    print_tip,
    print_warn,
    set_critical_level,
    set_debug_level,
    set_error_level,
    set_info_level,
    set_log_level,
    set_warn_level,
)

# Import table utilities
from .common.tables import create_backup_table

# Import interactive components
from .interactive import InteractiveMenu, format_backup_item

__all__ = [
    "console",
    "LogLevel",
    "print_success",
    "print_error",
    "print_warn",
    "print_tip",
    "print_system",
    "print_install",
    "print_detect",
    "print_config",
    "print_deps",
    "print_pattern",
    "print_header",
    "print_info",
    "print_separator",
    "print_command",
    "print_result",
    # Fonctions de configuration du niveau de logging
    "set_log_level",
    "get_log_level",
    "set_debug_level",
    "set_info_level",
    "set_warn_level",
    "set_error_level",
    "set_critical_level",
    # Table utilities
    "create_backup_table",
    # Interactive components
    "InteractiveMenu",
    "format_backup_item",
]
