"""
Project utility modules for Works On My Machine.

This package contains pure utility functions for project management operations.
"""

# Import utility functions for external use
from .project_detector import ProjectDetector
from .template_helpers import (
    get_node_paths,
    get_platform_info,
    get_python_paths,
    get_shell_commands,
    replace_platform_placeholders,
    validate_template_placeholders,
)
from .vscode_config import (
    generate_vscode_config,
    get_platform_specific_settings,
    get_python_interpreter_paths,
)

__all__ = [
    "ProjectDetector",
    "get_node_paths",
    "get_platform_info",
    "get_python_paths",
    "get_shell_commands",
    "replace_platform_placeholders",
    "validate_template_placeholders",
    "generate_vscode_config",
    "get_platform_specific_settings",
    "get_python_interpreter_paths",
]
