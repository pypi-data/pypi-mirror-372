"""
Installation utility modules for Works On My Machine.

This package contains utility functions for installation and path management operations.
"""

from .installation_utils import (
    create_womm_executable,
    get_current_womm_path,
    get_files_to_copy,
    get_files_to_remove,
    get_target_womm_path,
    should_exclude_file,
    verify_executable_works,
    verify_files_copied,
    verify_files_removed,
    verify_uninstallation_complete,
)
from .path_management_utils import (
    remove_from_path,
    remove_from_unix_path,
    remove_from_windows_path,
    setup_unix_path,
    setup_windows_path,
    verify_commands_accessible,
    verify_path_configuration,
)

__all__ = [
    # Installation utilities
    "create_womm_executable",
    "get_current_womm_path",
    "get_files_to_copy",
    "get_files_to_remove",
    "get_target_womm_path",
    "should_exclude_file",
    "verify_executable_works",
    "verify_files_copied",
    "verify_files_removed",
    "verify_uninstallation_complete",
    # Path management utilities
    "remove_from_path",
    "remove_from_unix_path",
    "remove_from_windows_path",
    "setup_unix_path",
    "setup_windows_path",
    "verify_commands_accessible",
    "verify_path_configuration",
]
