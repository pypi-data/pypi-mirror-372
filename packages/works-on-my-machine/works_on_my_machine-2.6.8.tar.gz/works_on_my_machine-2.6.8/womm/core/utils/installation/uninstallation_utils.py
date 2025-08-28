#!/usr/bin/env python3
"""
Uninstallation utilities for Works On My Machine.

This module provides pure utility functions for WOMM uninstallation operations.
All functions here are stateless and can be used independently.
"""

# IMPORTS
########################################################
# Standard library imports
from pathlib import Path
from typing import Dict, List

# Local imports
from ...exceptions.installation import (
    DirectoryAccessError,
    FileScanError,
    UninstallationVerificationError,
)

# =============================================================================
# FILE SCANNING UTILITIES
# =============================================================================


def get_files_to_remove(target_path: Path) -> List[str]:
    """Get list of files and directories to remove for progress tracking.

    Args:
        target_path: Target installation directory

    Returns:
        List of relative file and directory paths to remove

    Raises:
        FileScanError: If file list generation fails
        DirectoryAccessError: If directory access fails
    """
    files_to_remove = []

    if not target_path.exists():
        return files_to_remove

    try:
        # Check if we have permission to access the directory
        if not target_path.is_dir():
            raise DirectoryAccessError(
                operation="list_generation",
                directory_path=str(target_path),
                reason="Target path is not a directory",
                details=f"Path exists but is not a directory: {target_path}",
            )

        # Get all files and directories recursively
        for item_path in target_path.rglob("*"):
            try:
                if item_path.is_file():
                    # Add file with relative path
                    relative_path = item_path.relative_to(target_path)
                    files_to_remove.append(str(relative_path))
                elif item_path.is_dir():
                    # Add directory with relative path (keep trailing slash for directories)
                    relative_path = item_path.relative_to(target_path)
                    files_to_remove.append(f"{relative_path}/")
            except PermissionError as e:
                raise DirectoryAccessError(
                    operation="file_scanning",
                    directory_path=str(item_path),
                    reason=f"Permission denied: {e}",
                    details=f"Cannot access file/directory: {item_path}",
                ) from e

        # Sort to ensure files are removed before their parent directories
        # Files first, then directories (reverse alphabetical for nested dirs)
        files_to_remove.sort(key=lambda x: (x.endswith("/"), x))

        return files_to_remove

    except DirectoryAccessError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise FileScanError(
            operation="list_generation",
            target_path=str(target_path),
            reason=f"Unexpected error during file list generation: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


# =============================================================================
# VERIFICATION UTILITIES
# =============================================================================


def verify_files_removed(target_path: Path) -> Dict:
    """Verify that WOMM files were removed successfully.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with success status and details

    Raises:
        UninstallationVerificationError: If files were not removed successfully
        DirectoryAccessError: If directory access fails during verification
    """
    try:
        # Check if we can access the directory for verification
        if target_path.exists():
            try:
                # Try to access the directory to see if it's accessible
                target_path.stat()
            except PermissionError as e:
                raise DirectoryAccessError(
                    operation="verification",
                    directory_path=str(target_path),
                    reason=f"Permission denied during verification: {e}",
                    details=f"Cannot access directory for verification: {target_path}",
                ) from e

            # Directory exists and is accessible
            raise UninstallationVerificationError(
                verification_type="removal_verification",
                target_path=str(target_path),
                reason="WOMM directory still exists after removal",
                details=f"Directory path: {target_path}",
            )
        else:
            return {"success": True, "message": "All WOMM files removed successfully"}

    except (UninstallationVerificationError, DirectoryAccessError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise UninstallationVerificationError(
            verification_type="removal_verification",
            target_path=str(target_path),
            reason=f"File removal verification error: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


def verify_uninstallation_complete(target_path: Path) -> Dict:
    """Verify that uninstallation completed successfully.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with success status and details

    Raises:
        UninstallationVerificationError: If uninstallation verification fails
        DirectoryAccessError: If directory access fails during verification
    """
    try:
        # Check that target directory is gone
        if target_path.exists():
            try:
                # Try to access the directory to see if it's accessible
                target_path.stat()
            except PermissionError as e:
                raise DirectoryAccessError(
                    operation="verification",
                    directory_path=str(target_path),
                    reason=f"Permission denied during verification: {e}",
                    details=f"Cannot access directory for verification: {target_path}",
                ) from e

            # Directory exists and is accessible
            raise UninstallationVerificationError(
                verification_type="directory_removal",
                target_path=str(target_path),
                reason=f"Installation directory still exists: {target_path}",
                details="The target directory was not removed during uninstallation",
            )

        # Simple check that womm command is no longer accessible
        from ....common.security import run_silent

        try:
            cmd_result = run_silent("womm --version", timeout=10)
        except Exception:
            # If command execution fails, that's actually success (command not found)
            return {
                "success": True,
                "message": "WOMM command no longer accessible (execution failed)",
            }

        # If command is not found (exit code 9009 on Windows), that's success
        if cmd_result.returncode == 9009:  # Command not found on Windows
            return {"success": True, "message": "WOMM command no longer accessible"}
        else:
            # Command still found, but this might be from another installation
            return {
                "success": True,  # Don't fail uninstallation for this
                "message": "WOMM command still accessible (may be from another installation)",
            }

    except (UninstallationVerificationError, DirectoryAccessError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise UninstallationVerificationError(
            verification_type="unexpected_error",
            target_path=str(target_path),
            reason=f"Uninstallation verification error: {e}",
            details="This is an unexpected error that should be reported",
        ) from e
