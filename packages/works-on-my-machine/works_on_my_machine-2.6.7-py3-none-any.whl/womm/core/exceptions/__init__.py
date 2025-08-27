#!/usr/bin/env python3
"""
Custom exceptions for Works On My Machine.

This module contains all custom exceptions used throughout the WOMM codebase.
"""

from .installation_exceptions import (  # Installation Manager exceptions; Installation Utility exceptions; Base exceptions
    EnvironmentRefreshError,
    ExecutableCreationError,
    ExecutableVerificationError,
    FileCopyError,
    FileUtilityError,
    FileVerificationError,
    InstallationBackupError,
    InstallationFailedError,
    InstallationManagerError,
    InstallationPathError,
    InstallationRestoreError,
    InstallationRollbackError,
    InstallationUtilityError,
    InstallationVerificationError,
    PathUtilityError,
    WOMMInstallationError,
)
from .uninstallation_exceptions import (  # Uninstallation Manager exceptions; Base exceptions
    CommandAccessibilityError,
    DirectoryRemovalError,
    DirectoryScanError,
    FileListError,
    FileRemovalError,
    FileRemovalVerificationError,
    FileScanError,
    InstallationDirectoryError,
    InstallationNotFoundError,
    PathCleanupError,
    PathRemovalError,
    UninstallationBackupError,
    UninstallationDirectoryAccessError,
    UninstallationFailedError,
    UninstallationFileListError,
    UninstallationManagerError,
    UninstallationPermissionError,
    UninstallationProgressError,
    UninstallationRestoreError,
    UninstallationUtilityError,
    UninstallationVerificationError,
    UninstallationVerificationUtilityError,
    WOMMUninstallationError,
)

__all__ = [
    # Base exceptions
    "WOMMInstallationError",
    "WOMMUninstallationError",
    # Installation Manager exceptions
    "InstallationManagerError",
    "InstallationFailedError",
    "InstallationVerificationError",
    "FileCopyError",
    "ExecutableCreationError",
    "EnvironmentRefreshError",
    "InstallationRollbackError",
    # Uninstallation Manager exceptions
    "UninstallationManagerError",
    "UninstallationFailedError",
    "UninstallationVerificationError",
    "FileRemovalError",
    "DirectoryRemovalError",
    "FileScanError",
    "DirectoryScanError",
    "FileListError",
    "PathCleanupError",
    "PathRemovalError",
    "InstallationNotFoundError",
    "UninstallationProgressError",
    # Installation Utility exceptions
    "InstallationUtilityError",
    "FileUtilityError",
    "PathUtilityError",
    "InstallationPathError",
    "FileVerificationError",
    "ExecutableVerificationError",
    "InstallationBackupError",
    "InstallationRestoreError",
    # Uninstallation Utility exceptions
    "UninstallationUtilityError",
    "FileRemovalVerificationError",
    "CommandAccessibilityError",
    "UninstallationVerificationUtilityError",
    "InstallationDirectoryError",
    "UninstallationBackupError",
    "UninstallationRestoreError",
    "UninstallationFileListError",
    "UninstallationDirectoryAccessError",
    "UninstallationPermissionError",
]
