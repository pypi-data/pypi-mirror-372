#!/usr/bin/env python3
"""
Custom exceptions for uninstallation-related operations in Works On My Machine.

This module contains custom exceptions used specifically by uninstallation modules:
- UninstallationManager (womm/core/managers/installation/)
- Uninstallation utilities (womm/core/utils/installation/)
"""

from typing import Optional

# =============================================================================
# BASE EXCEPTIONS
# =============================================================================


class WOMMUninstallationError(Exception):
    """Base exception for all uninstallation-related errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# =============================================================================
# UNINSTALLATION MANAGER EXCEPTIONS
# =============================================================================


class UninstallationManagerError(WOMMUninstallationError):
    """Base exception for UninstallationManager errors."""


class UninstallationFailedError(UninstallationManagerError):
    """Raised when uninstallation process fails."""

    def __init__(self, stage: str, reason: str, details: Optional[str] = None):
        self.stage = stage
        self.reason = reason
        message = f"Uninstallation failed at stage '{stage}': {reason}"
        super().__init__(message, details)


class UninstallationVerificationError(UninstallationManagerError):
    """Raised when uninstallation verification fails."""

    def __init__(
        self, verification_step: str, reason: str, details: Optional[str] = None
    ):
        self.verification_step = verification_step
        self.reason = reason
        message = (
            f"Uninstallation verification failed at '{verification_step}': {reason}"
        )
        super().__init__(message, details)


class FileRemovalError(UninstallationManagerError):
    """Raised when file removal operations fail."""

    def __init__(self, file_path: str, reason: str, details: Optional[str] = None):
        self.file_path = file_path
        self.reason = reason
        message = f"Failed to remove '{file_path}': {reason}"
        super().__init__(message, details)


class DirectoryRemovalError(UninstallationManagerError):
    """Raised when directory removal operations fail."""

    def __init__(self, directory_path: str, reason: str, details: Optional[str] = None):
        self.directory_path = directory_path
        self.reason = reason
        message = f"Failed to remove directory '{directory_path}': {reason}"
        super().__init__(message, details)


class PathCleanupError(UninstallationManagerError):
    """Raised when PATH cleanup operations fail."""

    def __init__(self, reason: str, details: Optional[str] = None):
        self.reason = reason
        message = f"PATH cleanup failed: {reason}"
        super().__init__(message, details)


class InstallationNotFoundError(UninstallationManagerError):
    """Raised when WOMM installation is not found for uninstallation."""

    def __init__(self, target_path: str, details: Optional[str] = None):
        self.target_path = target_path
        message = f"WOMM installation not found at '{target_path}'"
        super().__init__(message, details)


class FileScanError(UninstallationManagerError):
    """Raised when scanning files for removal fails."""

    def __init__(self, target_path: str, reason: str, details: Optional[str] = None):
        self.target_path = target_path
        self.reason = reason
        message = f"Failed to scan files at '{target_path}': {reason}"
        super().__init__(message, details)


class DirectoryScanError(UninstallationManagerError):
    """Raised when scanning directories for removal fails."""

    def __init__(self, target_path: str, reason: str, details: Optional[str] = None):
        self.target_path = target_path
        self.reason = reason
        message = f"Failed to scan directories at '{target_path}': {reason}"
        super().__init__(message, details)


class FileListError(UninstallationManagerError):
    """Raised when generating file removal list fails."""

    def __init__(self, target_path: str, reason: str, details: Optional[str] = None):
        self.target_path = target_path
        self.reason = reason
        message = f"Failed to generate file list for '{target_path}': {reason}"
        super().__init__(message, details)


class PathRemovalError(UninstallationManagerError):
    """Raised when PATH removal operations fail."""

    def __init__(self, path_entry: str, reason: str, details: Optional[str] = None):
        self.path_entry = path_entry
        self.reason = reason
        message = f"Failed to remove PATH entry '{path_entry}': {reason}"
        super().__init__(message, details)


class UninstallationProgressError(UninstallationManagerError):
    """Raised when uninstallation progress tracking fails."""

    def __init__(self, stage: str, reason: str, details: Optional[str] = None):
        self.stage = stage
        self.reason = reason
        message = f"Progress tracking failed at stage '{stage}': {reason}"
        super().__init__(message, details)


# =============================================================================
# UNINSTALLATION UTILITIES EXCEPTIONS
# =============================================================================


class UninstallationUtilityError(WOMMUninstallationError):
    """Base exception for uninstallation utility errors."""


class FileRemovalVerificationError(UninstallationUtilityError):
    """Raised when file removal verification operations fail."""

    def __init__(
        self,
        verification_type: str,
        file_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        self.verification_type = verification_type
        self.file_path = file_path
        self.reason = reason
        message = f"File removal verification '{verification_type}' failed for '{file_path}': {reason}"
        super().__init__(message, details)


class CommandAccessibilityError(UninstallationUtilityError):
    """Raised when command accessibility verification fails."""

    def __init__(self, command_name: str, reason: str, details: Optional[str] = None):
        self.command_name = command_name
        self.reason = reason
        message = (
            f"Command accessibility verification failed for '{command_name}': {reason}"
        )
        super().__init__(message, details)


class UninstallationVerificationUtilityError(UninstallationUtilityError):
    """Raised when uninstallation verification operations fail."""

    def __init__(
        self, verification_step: str, reason: str, details: Optional[str] = None
    ):
        self.verification_step = verification_step
        self.reason = reason
        message = f"Uninstallation verification '{verification_step}' failed: {reason}"
        super().__init__(message, details)


class InstallationDirectoryError(UninstallationUtilityError):
    """Raised when installation directory operations fail."""

    def __init__(
        self,
        operation: str,
        directory_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        self.operation = operation
        self.directory_path = directory_path
        self.reason = reason
        message = f"Installation directory {operation} failed for '{directory_path}': {reason}"
        super().__init__(message, details)


class UninstallationBackupError(UninstallationUtilityError):
    """Raised when uninstallation backup operations fail."""

    def __init__(self, operation: str, reason: str, details: Optional[str] = None):
        self.operation = operation
        self.reason = reason
        message = f"Uninstallation backup {operation} failed: {reason}"
        super().__init__(message, details)


class UninstallationRestoreError(UninstallationUtilityError):
    """Raised when uninstallation restore operations fail."""

    def __init__(self, backup_file: str, reason: str, details: Optional[str] = None):
        self.backup_file = backup_file
        self.reason = reason
        message = f"Uninstallation restore from '{backup_file}' failed: {reason}"
        super().__init__(message, details)


class UninstallationFileListError(UninstallationUtilityError):
    """Raised when generating uninstallation file list fails."""

    def __init__(self, target_path: str, reason: str, details: Optional[str] = None):
        self.target_path = target_path
        self.reason = reason
        message = (
            f"Failed to generate uninstallation file list for '{target_path}': {reason}"
        )
        super().__init__(message, details)


class UninstallationDirectoryAccessError(UninstallationUtilityError):
    """Raised when accessing uninstallation directory fails."""

    def __init__(
        self,
        directory_path: str,
        operation: str,
        reason: str,
        details: Optional[str] = None,
    ):
        self.directory_path = directory_path
        self.operation = operation
        self.reason = reason
        message = f"Directory access failed for '{directory_path}' during {operation}: {reason}"
        super().__init__(message, details)


class UninstallationPermissionError(UninstallationUtilityError):
    """Raised when uninstallation permission issues occur."""

    def __init__(
        self,
        target_path: str,
        operation: str,
        reason: str,
        details: Optional[str] = None,
    ):
        self.target_path = target_path
        self.operation = operation
        self.reason = reason
        message = f"Permission error during {operation} at '{target_path}': {reason}"
        super().__init__(message, details)
