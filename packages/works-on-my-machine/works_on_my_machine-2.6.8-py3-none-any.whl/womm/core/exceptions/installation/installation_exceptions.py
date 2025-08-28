#!/usr/bin/env python3
"""
Installation exceptions for Works On My Machine.

This module contains custom exceptions used specifically by installation modules:
- InstallationManager (womm/core/managers/installation/installation_manager.py)
- Installation utilities (womm/core/utils/installation/installation_utils.py)

Following a pragmatic approach with 8 main exception types:
1. InstallationUtilityError - Base exception for installation utilities
2. FileVerificationError - File verification errors
3. PathUtilityError - PATH verification errors
4. ExecutableVerificationError - Executable verification errors
5. InstallationManagerError - Base exception for installation manager
6. InstallationFileError - File operation errors during installation
7. InstallationPathError - PATH operation errors during installation
8. InstallationVerificationError - Verification errors during installation
9. InstallationSystemError - System operation errors during installation
"""

# IMPORTS
########################################################
# Standard library imports
from typing import Optional

# =============================================================================
# UTILITY EXCEPTIONS
# =============================================================================


class InstallationUtilityError(Exception):
    """Base exception for all installation utility errors.

    This is the main exception class for all installation utility operations.
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


class FileVerificationError(InstallationUtilityError):
    """File verification errors for installation operations.

    This exception is raised when file verification operations fail,
    such as checking if files were copied correctly or verifying file integrity.
    """

    def __init__(
        self,
        verification_type: str,
        file_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize file verification error with specific context.

        Args:
            verification_type: Type of verification being performed (e.g., "copy_verification")
            file_path: The file being verified
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.verification_type = verification_type
        self.file_path = file_path
        self.reason = reason
        message = f"File verification '{verification_type}' failed for '{file_path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# UTILITY EXCEPTIONS - PATH OPERATIONS
# =============================================================================


class PathUtilityError(InstallationUtilityError):
    """PATH verification errors for installation operations.

    This exception is raised when PATH verification operations fail,
    such as checking if WOMM is correctly configured in system PATH.
    """

    def __init__(
        self,
        operation: str,
        path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize path utility error with specific context.

        Args:
            operation: The operation being performed (e.g., "path_verification")
            path: The path being verified
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Path utility {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# UTILITY EXCEPTIONS - EXECUTABLE OPERATIONS
# =============================================================================


class ExecutableVerificationError(InstallationUtilityError):
    """Executable verification errors for installation operations.

    This exception is raised when executable verification operations fail,
    such as checking if WOMM commands are accessible or testing executables.
    """

    def __init__(
        self,
        executable_name: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize executable verification error with specific context.

        Args:
            executable_name: Name of the executable being verified (e.g., "womm")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.executable_name = executable_name
        self.reason = reason
        message = f"Executable verification failed for '{executable_name}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - BASE
# =============================================================================


class InstallationManagerError(Exception):
    """Base exception for InstallationManager errors.

    This exception is raised when InstallationManager operations fail,
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


class InstallationFileError(InstallationManagerError):
    """File operation errors during installation process.

    This exception is raised when file operations fail during
    the installation process, such as copying files or creating directories.
    """

    def __init__(
        self,
        operation: str,
        file_path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize installation file error with specific context.

        Args:
            operation: The file operation being performed (e.g., "copy", "create")
            file_path: The file path being operated on
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"Installation file {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - PATH OPERATIONS
# =============================================================================


class InstallationPathError(InstallationManagerError):
    """PATH operation errors during installation process.

    This exception is raised when PATH operations fail during
    the installation process, such as setting up or backing up PATH.
    """

    def __init__(
        self,
        operation: str,
        path: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize installation path error with specific context.

        Args:
            operation: The PATH operation being performed (e.g., "setup", "backup")
            path: The path being operated on
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Installation PATH {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - VERIFICATION OPERATIONS
# =============================================================================


class InstallationVerificationError(InstallationManagerError):
    """Verification errors during installation process.

    This exception is raised when verification operations fail during
    the installation process, such as checking installation integrity.
    """

    def __init__(
        self,
        verification_type: str,
        target: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize installation verification error with specific context.

        Args:
            verification_type: Type of verification being performed (e.g., "integrity_check")
            target: The target being verified
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.verification_type = verification_type
        self.target = target
        self.reason = reason
        message = f"Installation verification '{verification_type}' failed for '{target}': {reason}"
        super().__init__(message, details)


# =============================================================================
# MANAGER EXCEPTIONS - SYSTEM OPERATIONS
# =============================================================================


class InstallationSystemError(InstallationManagerError):
    """System operation errors during installation process.

    This exception is raised when system operations fail during
    the installation process, such as environment refresh or system calls.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: Optional[str] = None,
    ):
        """Initialize installation system error with specific context.

        Args:
            operation: The system operation being performed (e.g., "environment_refresh")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"Installation system {operation} failed: {reason}"
        super().__init__(message, details)
