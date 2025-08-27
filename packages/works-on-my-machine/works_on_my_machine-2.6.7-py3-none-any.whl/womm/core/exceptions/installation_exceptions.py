#!/usr/bin/env python3
"""
Custom exceptions for installation-related operations in Works On My Machine.

This module contains custom exceptions used specifically by installation modules:
- InstallationManager (womm/core/managers/installation/)
- UninstallationManager (womm/core/managers/installation/)
- Installation utilities (womm/core/utils/installation/)
"""

from typing import Optional

# =============================================================================
# BASE EXCEPTIONS
# =============================================================================


class WOMMInstallationError(Exception):
    """Base exception for all installation-related errors."""

    def __init__(self, message: str, details: Optional[str] = None):
        self.message = message
        self.details = details
        super().__init__(self.message)


# =============================================================================
# INSTALLATION MANAGER EXCEPTIONS
# =============================================================================


class InstallationManagerError(WOMMInstallationError):
    """Base exception for InstallationManager errors."""


class InstallationFailedError(InstallationManagerError):
    """Raised when installation process fails."""

    def __init__(self, stage: str, reason: str, details: Optional[str] = None):
        self.stage = stage
        self.reason = reason
        message = f"Installation failed at stage '{stage}': {reason}"
        super().__init__(message, details)


class InstallationVerificationError(InstallationManagerError):
    """Raised when installation verification fails."""

    def __init__(
        self, verification_step: str, reason: str, details: Optional[str] = None
    ):
        self.verification_step = verification_step
        self.reason = reason
        message = f"Installation verification failed at '{verification_step}': {reason}"
        super().__init__(message, details)


class FileCopyError(InstallationManagerError):
    """Raised when file copying operations fail."""

    def __init__(
        self, source: str, target: str, reason: str, details: Optional[str] = None
    ):
        self.source = source
        self.target = target
        self.reason = reason
        message = f"Failed to copy '{source}' to '{target}': {reason}"
        super().__init__(message, details)


class ExecutableCreationError(InstallationManagerError):
    """Raised when executable creation fails."""

    def __init__(
        self, executable_name: str, reason: str, details: Optional[str] = None
    ):
        self.executable_name = executable_name
        self.reason = reason
        message = f"Failed to create executable '{executable_name}': {reason}"
        super().__init__(message, details)


class EnvironmentRefreshError(InstallationManagerError):
    """Raised when environment refresh fails (Windows only)."""

    def __init__(self, reason: str, details: Optional[str] = None):
        self.reason = reason
        message = f"Environment refresh failed: {reason}"
        super().__init__(message, details)


class InstallationRollbackError(InstallationManagerError):
    """Raised when installation rollback fails."""

    def __init__(self, stage: str, reason: str, details: Optional[str] = None):
        self.stage = stage
        self.reason = reason
        message = f"Installation rollback failed at stage '{stage}': {reason}"
        super().__init__(message, details)


# =============================================================================
# UNINSTALLATION MANAGER EXCEPTIONS
# =============================================================================


class UninstallationManagerError(WOMMInstallationError):
    """Base exception for UninstallationManager errors."""


class UninstallationFailedError(UninstallationManagerError):
    """Raised when uninstallation process fails."""

    def __init__(self, stage: str, reason: str, details: Optional[str] = None):
        self.stage = stage
        self.reason = reason
        message = f"Uninstallation failed at stage '{stage}': {reason}"
        super().__init__(message, details)


class FileRemovalError(UninstallationManagerError):
    """Raised when file removal operations fail."""

    def __init__(self, file_path: str, reason: str, details: Optional[str] = None):
        self.file_path = file_path
        self.reason = reason
        message = f"Failed to remove '{file_path}': {reason}"
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


# =============================================================================
# INSTALLATION UTILITIES EXCEPTIONS
# =============================================================================


class InstallationUtilityError(WOMMInstallationError):
    """Base exception for installation utility errors."""


class FileUtilityError(InstallationUtilityError):
    """Raised when file utility operations fail."""

    def __init__(
        self, operation: str, file_path: str, reason: str, details: Optional[str] = None
    ):
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"File utility {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)


class PathUtilityError(InstallationUtilityError):
    """Raised when path utility operations fail."""

    def __init__(
        self, operation: str, path: str, reason: str, details: Optional[str] = None
    ):
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Path utility {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


class InstallationPathError(InstallationUtilityError):
    """Raised when installation path operations fail."""

    def __init__(
        self, operation: str, path: str, reason: str, details: Optional[str] = None
    ):
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Installation path {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


class FileVerificationError(InstallationUtilityError):
    """Raised when file verification operations fail."""

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
        message = f"File verification '{verification_type}' failed for '{file_path}': {reason}"
        super().__init__(message, details)


class ExecutableVerificationError(InstallationUtilityError):
    """Raised when executable verification operations fail."""

    def __init__(
        self, executable_name: str, reason: str, details: Optional[str] = None
    ):
        self.executable_name = executable_name
        self.reason = reason
        message = f"Executable verification failed for '{executable_name}': {reason}"
        super().__init__(message, details)


class InstallationBackupError(InstallationUtilityError):
    """Raised when installation backup operations fail."""

    def __init__(self, operation: str, reason: str, details: Optional[str] = None):
        self.operation = operation
        self.reason = reason
        message = f"Installation backup {operation} failed: {reason}"
        super().__init__(message, details)


class InstallationRestoreError(InstallationUtilityError):
    """Raised when installation restore operations fail."""

    def __init__(self, backup_file: str, reason: str, details: Optional[str] = None):
        self.backup_file = backup_file
        self.reason = reason
        message = f"Installation restore from '{backup_file}' failed: {reason}"
        super().__init__(message, details)
