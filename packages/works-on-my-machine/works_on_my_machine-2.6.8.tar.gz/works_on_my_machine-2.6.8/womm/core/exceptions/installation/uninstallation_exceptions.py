#!/usr/bin/env python3
"""
Uninstallation exceptions for Works On My Machine.

This module contains custom exceptions used specifically by uninstallation modules:
- UninstallationManager (womm/core/managers/installation/uninstallation_manager.py)
- Uninstallation utilities (womm/core/utils/installation/uninstallation_utils.py)

Following a pragmatic approach with 8 main exception types:
1. UninstallationUtilityError - Base exception for uninstallation utilities
2. FileScanError - File scanning and list generation errors
3. DirectoryAccessError - Directory access and permission errors
4. UninstallationVerificationError - Uninstallation verification errors
5. UninstallationManagerError - Base exception for uninstallation manager
6. UninstallationFileError - File operation errors during uninstallation
7. UninstallationPathError - PATH operation errors during uninstallation
8. UninstallationVerificationError - Verification errors during uninstallation
"""

# IMPORTS
########################################################
# Standard library imports
from typing import Optional

# =============================================================================
# UTILITY EXCEPTIONS
# =============================================================================


class UninstallationUtilityError(Exception):
    """Base exception for all uninstallation utility errors.

    This is the main exception class for all uninstallation utility operations.
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
# UTILITY EXCEPTIONS - FILE OPERATIONS
# =============================================================================


class FileScanError(UninstallationUtilityError):
    """File scanning errors for uninstallation operations.

    This exception is raised when file scanning operations fail,
    such as generating lists of files to remove or scanning directories.
    """

    def __init__(
        self,
        operation: str,
        target_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize file scan error with specific context.

        Args:
            operation: The operation being performed (e.g., "list_generation")
            target_path: The target path being scanned
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.target_path = target_path
        self.reason = reason
        message = f"File scan {operation} failed for '{target_path}': {reason}"
        super().__init__(message, details)


class DirectoryAccessError(UninstallationUtilityError):
    """Directory access errors for uninstallation operations.

    This exception is raised when directory access operations fail,
    such as accessing directories for scanning or verification.
    """

    def __init__(
        self,
        operation: str,
        directory_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize directory access error with specific context.

        Args:
            operation: The operation being performed (e.g., "verification")
            directory_path: The directory being accessed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.directory_path = directory_path
        self.reason = reason
        message = (
            f"Directory access {operation} failed for '{directory_path}': {reason}"
        )
        super().__init__(message, details)


# =============================================================================
# UTILITY EXCEPTIONS - VERIFICATION OPERATIONS
# =============================================================================


class UninstallationVerificationError(UninstallationUtilityError):
    """Uninstallation verification errors.

    This exception is raised when uninstallation verification operations fail,
    such as checking if files were removed or verifying uninstallation completion.
    """

    def __init__(
        self,
        verification_type: str,
        target_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize uninstallation verification error with specific context.

        Args:
            verification_type: Type of verification being performed (e.g., "removal_verification")
            target_path: The target path being verified
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.verification_type = verification_type
        self.target_path = target_path
        self.reason = reason
        message = f"Uninstallation verification '{verification_type}' failed for '{target_path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - BASE
# =============================================================================


class UninstallationManagerError(Exception):
    """Base exception for UninstallationManager errors.

    This exception is raised when UninstallationManager operations fail,
    such as process orchestration, progress tracking, or state management.
    """

    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize the manager error with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# =============================================================================
# MANAGER EXCEPTIONS - FILE OPERATIONS
# =============================================================================


class UninstallationFileError(UninstallationManagerError):
    """File operation errors during uninstallation process.

    This exception is raised when file operations fail during
    the uninstallation process, such as removing files or directories.
    """

    def __init__(
        self,
        operation: str,
        file_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize uninstallation file error with specific context.

        Args:
            operation: The file operation being performed (e.g., "remove", "delete")
            file_path: The file path being operated on
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"Uninstallation file {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - PATH OPERATIONS
# =============================================================================


class UninstallationPathError(UninstallationManagerError):
    """PATH operation errors during uninstallation process.

    This exception is raised when PATH operations fail during
    the uninstallation process, such as cleaning up PATH entries.
    """

    def __init__(
        self,
        operation: str,
        path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize uninstallation path error with specific context.

        Args:
            operation: The PATH operation being performed (e.g., "cleanup", "remove")
            path: The path being operated on
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Uninstallation PATH {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - VERIFICATION OPERATIONS
# =============================================================================


class UninstallationManagerVerificationError(UninstallationManagerError):
    """Verification errors during uninstallation process.

    This exception is raised when verification operations fail during
    the uninstallation process, such as checking if uninstallation completed.
    """

    def __init__(
        self,
        verification_type: str,
        target: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize uninstallation verification error with specific context.

        Args:
            verification_type: Type of verification being performed (e.g., "completion_check")
            target: The target being verified
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.verification_type = verification_type
        self.target = target
        self.reason = reason
        message = f"Uninstallation verification '{verification_type}' failed for '{target}': {reason}"
        super().__init__(message, details)
