#!/usr/bin/env python3
"""
User PATH exceptions for Works On My Machine.

This module contains custom exceptions used specifically by PATH management modules:
- PathManager (womm/core/managers/system/user_path_manager.py)
- User path utilities (womm/core/utils/system/user_path_utils.py)

Following a pragmatic approach with only 3 main exception types:
1. UserPathError - Base exception for all user path operations
2. RegistryError - Registry-specific errors (Windows only)
3. FileSystemError - File system errors (Unix RC files)
"""

from typing import Optional

# =============================================================================
# BASE EXCEPTION
# =============================================================================


class UserPathError(Exception):
    """Base exception for all user PATH-related errors.

    This is the main exception class for all user path operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
    """

    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize the exception with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# =============================================================================
# REGISTRY EXCEPTIONS (Windows only)
# =============================================================================


class RegistryError(UserPathError):
    """Registry-specific errors for Windows PATH operations.

    This exception is raised when Windows registry operations fail,
    such as querying or updating the PATH environment variable.
    """

    def __init__(
        self,
        registry_key: str,
        operation: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize registry error with specific context.

        Args:
            registry_key: The registry key being accessed (e.g., "HKCU\\Environment")
            operation: The operation being performed (e.g., "query", "update")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.registry_key = registry_key
        self.operation = operation
        self.reason = reason
        message = f"Registry {operation} failed for {registry_key}: {reason}"
        super().__init__(message, details)


# =============================================================================
# FILE SYSTEM EXCEPTIONS (Unix only)
# =============================================================================


class FileSystemError(UserPathError):
    """File system errors for Unix PATH operations.

    This exception is raised when Unix shell configuration file operations fail,
    such as reading or writing .bashrc, .zshrc, or .profile files.
    """

    def __init__(
        self,
        file_path: str,
        operation: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize file system error with specific context.

        Args:
            file_path: The file being accessed (e.g., "~/.bashrc")
            operation: The operation being performed (e.g., "read", "write")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.file_path = file_path
        self.operation = operation
        self.reason = reason
        message = f"File {operation} failed for {file_path}: {reason}"
        super().__init__(message, details)
