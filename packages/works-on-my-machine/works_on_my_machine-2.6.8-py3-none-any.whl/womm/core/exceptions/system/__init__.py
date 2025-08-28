#!/usr/bin/env python3
"""
System exceptions for Works On My Machine.

This package contains custom exceptions used specifically by system management modules:
- PathManager (womm/core/managers/system/user_path_manager.py)
- User path utilities (womm/core/utils/system/user_path_utils.py)

Following a pragmatic approach with simplified exception hierarchy:
- UserPathError: Base exception for all user path operations
- RegistryError: Registry-specific errors (Windows only)
- FileSystemError: File system errors (Unix RC files)
"""

from .user_path_exceptions import FileSystemError, RegistryError, UserPathError

__all__ = [
    # Base exception
    "UserPathError",
    # Registry exceptions (Windows only)
    "RegistryError",
    # File system exceptions (Unix only)
    "FileSystemError",
]
