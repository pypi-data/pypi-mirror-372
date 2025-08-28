#!/usr/bin/env python3
"""
Installation utility modules for Works On My Machine.

This package contains utility functions for installation and uninstallation operations.
"""

from .common_utils import get_current_womm_path, get_target_womm_path
from .installation_utils import (
    create_womm_executable,
    get_files_to_copy,
    should_exclude_file,
    verify_commands_accessible,
    verify_executable_works,
    verify_files_copied,
    verify_path_configuration,
)
from .uninstallation_utils import (
    get_files_to_remove,
    verify_files_removed,
    verify_uninstallation_complete,
)

__all__ = [
    # Common utilities
    "get_current_womm_path",
    "get_target_womm_path",
    # Installation utilities
    "create_womm_executable",
    "get_files_to_copy",
    "should_exclude_file",
    "verify_executable_works",
    "verify_files_copied",
    # Uninstallation utilities
    "get_files_to_remove",
    "verify_files_removed",
    "verify_uninstallation_complete",
    # Path verification utilities
    "verify_commands_accessible",
    "verify_path_configuration",
]
