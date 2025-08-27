"""
Core modules for Works On My Machine.

This package contains core utilities and base functionality.
"""

from ..utils.cli_utils import (
    CLIUtils,
    CommandResult,
    check_tool_available,
    get_tool_version,
    run_command,
    run_interactive,
    run_silent,
)

# Note: system_detector functions are not exported at module level
# Note: template_helpers functions are not exported at module level

__all__ = [
    "run_command",
    "run_silent",
    "run_interactive",
    "check_tool_available",
    "get_tool_version",
    "CLIUtils",
    "CommandResult",
]
