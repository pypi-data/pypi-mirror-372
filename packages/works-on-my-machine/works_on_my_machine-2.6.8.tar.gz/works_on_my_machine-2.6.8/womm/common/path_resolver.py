#!/usr/bin/env python3
"""
Path management utilities for WOMM CLI.
Provides path resolution and validation functions.
"""

from pathlib import Path

from .imports import get_languages_module_path, get_shared_module_path


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def get_shared_path() -> Path:
    """Get the shared modules path."""
    return get_shared_module_path()


def resolve_script_path(relative_path: str) -> Path:
    """Resolve a script path relative to the project root."""
    # Handle both development and PyPI installation
    if relative_path.startswith("languages/"):
        languages_path = get_languages_module_path()
        return languages_path / relative_path[10:]  # Remove "languages/" prefix
    else:
        return get_project_root() / relative_path


def validate_script_exists(script_path: Path) -> bool:
    """Validate that a script file exists and is executable."""
    return script_path.exists() and script_path.is_file()


# Export path functions
__all__ = [
    "get_project_root",
    "get_shared_path",
    "resolve_script_path",
    "validate_script_exists",
]
