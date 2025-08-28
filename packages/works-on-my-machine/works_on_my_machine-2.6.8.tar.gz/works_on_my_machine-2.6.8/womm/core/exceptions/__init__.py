#!/usr/bin/env python3
"""
Custom exceptions for Works On My Machine.

This package contains all custom exceptions used throughout the WOMM project.
"""

from .installation import (  # Installation exceptions
    DirectoryAccessError,
    ExecutableVerificationError,
    FileScanError,
    FileVerificationError,
    InstallationFileError,
    InstallationManagerError,
    InstallationPathError,
    InstallationSystemError,
    InstallationUtilityError,
    InstallationVerificationError,
    PathUtilityError,
    UninstallationFileError,
    UninstallationManagerError,
    UninstallationManagerVerificationError,
    UninstallationPathError,
    UninstallationUtilityError,
    UninstallationVerificationError,
)
from .system import FileSystemError, RegistryError, UserPathError  # System exceptions

__all__ = [
    # Installation Utility exceptions
    "InstallationUtilityError",
    "FileVerificationError",
    "PathUtilityError",
    "ExecutableVerificationError",
    # Installation Manager exceptions
    "InstallationManagerError",
    "InstallationFileError",
    "InstallationPathError",
    "InstallationVerificationError",
    "InstallationSystemError",
    # Uninstallation Utility exceptions
    "UninstallationUtilityError",
    "FileScanError",
    "DirectoryAccessError",
    "UninstallationVerificationError",
    # Uninstallation Manager exceptions
    "UninstallationManagerError",
    "UninstallationFileError",
    "UninstallationPathError",
    "UninstallationManagerVerificationError",
    # System exceptions
    "UserPathError",
    "RegistryError",
    "FileSystemError",
]
