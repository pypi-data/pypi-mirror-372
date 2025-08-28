#!/usr/bin/env python3
"""
Uninstaller for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

# IMPORTS
########################################################
# Standard library imports
import platform
from pathlib import Path
from time import sleep
from typing import Optional

# Local imports
from ...exceptions.installation import (  # Utility exceptions
    DirectoryAccessError,
    FileScanError,
    InstallationManagerError,
    UninstallationFileError,
    UninstallationManagerError,
    UninstallationManagerVerificationError,
    UninstallationPathError,
    UninstallationUtilityError,
    UninstallationVerificationError,
)
from ...utils.installation import (
    get_files_to_remove,
    get_target_womm_path,
    verify_uninstallation_complete,
)
from ...utils.system.user_path_utils import (
    FileSystemError,
    RegistryError,
    UserPathError,
    remove_from_path,
)

# =============================================================================
# MAIN CLASS
# =============================================================================


class UninstallationManager:
    """Manages the uninstallation process for Works On My Machine."""

    def __init__(self, target: Optional[str] = None):
        """Initialize the uninstallation manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        try:
            if target:
                self.target_path = Path(target).expanduser().resolve()
            else:
                self.target_path = get_target_womm_path()
        except Exception as e:
            raise InstallationManagerError(
                message=f"Failed to initialize uninstallation manager: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

        self.platform = platform.system()

    # =============================================================================
    # PUBLIC METHODS - MAIN OPERATIONS
    # =============================================================================

    def uninstall(
        self,
        force: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Uninstall Works On My Machine from the user's system.

        Args:
            force: Force uninstallation without confirmation
            dry_run: Show what would be done without making changes
            verbose: Show detailed progress information

        Returns:
            True if uninstallation successful, False otherwise
        """
        # Import UI modules
        from ...ui.common.console import (
            console,
            print_error,
            print_header,
            print_install,
            print_success,
            print_system,
        )
        from ...ui.common.extended.dynamic_progress import (
            create_dynamic_layered_progress,
        )
        from ...ui.common.panels import create_panel
        from ...ui.common.progress import create_spinner_with_status
        from ...ui.common.prompts import confirm, show_warning_panel

        print_header("W.O.M.M Uninstallation")

        # Check target directory existence
        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            progress.update(task, status="Analyzing uninstallation requirements...")

            # Check if WOMM is installed
            if not self.target_path.exists():
                progress.stop()
                show_warning_panel(
                    "WOMM not found",
                    f"No installation found at: {self.target_path}\n"
                    "WOMM may not be installed or may be in a different location",
                )
                return False
            else:
                progress.update(
                    task, status=f"Found installation at: {self.target_path}"
                )

        # Check if force is required
        if not force and not dry_run:
            # Show warning panel for uninstallation
            console.print("")
            show_warning_panel(
                "Uninstallation Confirmation",
                f"This will completely remove WOMM from {self.target_path}.\n\n"
                "This action cannot be undone.",
            )

            # Ask for confirmation
            if not confirm(
                "Do you want to continue and remove WOMM completely?",
                default=False,
            ):
                console.print("❌ Uninstallation cancelled", style="red")
                return False

            console.print("")
            print_system("Proceeding with uninstallation...")

        if dry_run:
            print_system("DRY RUN MODE - No changes will be made")

        # Get list of files to remove
        print("")
        with create_spinner_with_status("Analyzing installed files...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning installation directory...")
            files_to_remove = get_files_to_remove(self.target_path)
            progress.update(
                task, status=f"Found {len(files_to_remove)} files to remove"
            )

        if dry_run:
            print_install("Would remove from PATH configuration")
            print_install(f"Would remove {len(files_to_remove)} files")
            print_install(f"Would remove directory: {self.target_path}")
            if verbose:
                print_system("🔍 Dry run mode - detailed logging enabled")
                for file_path in files_to_remove[:5]:  # Show first 5 files as sample
                    print_system(f"  📄 Would remove: {file_path}")
                if len(files_to_remove) > 5:
                    print_system(f"  ... and {len(files_to_remove) - 5} more files")
            return True

        # Define uninstallation stages with DynamicLayeredProgress
        # Color palette: unified cyan for all steps, semantic colors for states
        stages = [
            {
                "name": "main_uninstallation",
                "type": "main",
                "steps": [
                    "Preparation",
                    "PATH Cleanup",
                    "File Removal",
                    "Verification",
                ],
                "description": "WOMM Uninstallation Progress",
                "style": "bold bright_white",
            },
            {
                "name": "preparation",
                "type": "spinner",
                "description": "Preparing uninstallation environment...",
                "style": "bright_blue",
            },
            {
                "name": "path_cleanup",
                "type": "spinner",
                "description": "Removing from PATH...",
                "style": "bright_blue",
            },
            {
                "name": "file_removal",
                "type": "progress",
                "total": len(files_to_remove),
                "description": "Removing installation files...",
                "style": "bright_blue",
            },
            {
                "name": "verification",
                "type": "steps",
                "steps": [
                    "File removal check",
                    "Command accessibility test",
                ],
                "description": "Verifying uninstallation...",
                "style": "bright_blue",
            },
        ]

        print("")
        with create_dynamic_layered_progress(stages) as progress:
            try:
                # Stage 1: Preparation
                prep_messages = [
                    "Analyzing uninstallation requirements...",
                    "Checking installation integrity...",
                    "Validating removal permissions...",
                    "Preparing cleanup operations...",
                ]

                for msg in prep_messages:
                    progress.update_layer("preparation", 0, msg)
                    sleep(0.2)

                # Complete preparation
                progress.complete_layer("preparation")

                # Update main uninstallation progress
                progress.update_layer("main_uninstallation", 0, "Preparation completed")
                sleep(0.3)

                # Stage 2: PATH Cleanup
                progress.update_layer("path_cleanup", 0, "Removing WOMM from PATH...")
                if not self._cleanup_path():
                    progress.emergency_stop("Failed to remove from PATH")
                    raise UninstallationPathError(
                        operation="cleanup",
                        path=str(self.target_path),
                        reason="Failed to remove from PATH",
                        details="remove_from_path utility returned False",
                    )

                progress.update_layer("path_cleanup", 0, "PATH cleanup completed")
                sleep(0.2)

                # Complete PATH cleanup
                progress.complete_layer("path_cleanup")

                # Update main uninstallation progress
                progress.update_layer(
                    "main_uninstallation", 1, "PATH cleanup completed"
                )
                sleep(0.3)

                # Stage 3: File Removal
                self._remove_files_with_progress(files_to_remove, progress, verbose)

                # Complete file removal
                progress.complete_layer("file_removal")

                # Update main uninstallation progress
                progress.update_layer("main_uninstallation", 2, "Files removed")
                sleep(0.3)

                # Stage 4: Verification
                self._verify_uninstallation_with_progress(progress)

                # Complete verification
                progress.complete_layer("verification")

                # Complete main uninstallation progress
                progress.update_layer(
                    "main_uninstallation", 3, "Uninstallation completed!"
                )
                sleep(0.3)

                # Complete and remove main uninstallation layer
                progress.complete_layer("main_uninstallation")

            except (
                InstallationManagerError,
                UninstallationFileError,
                UninstallationPathError,
                UninstallationManagerVerificationError,
                UninstallationManagerError,
                # Utility exceptions that might be raised by utility functions
                UninstallationUtilityError,
                FileScanError,
                DirectoryAccessError,
                UninstallationVerificationError,
                # System exceptions that might be raised by user_path_manager
                UserPathError,
                RegistryError,
                FileSystemError,
            ) as e:
                # Stop progress first, then print error details
                progress.emergency_stop(f"Uninstallation failed: {type(e).__name__}")

                # Now safe to print error details
                from ...ui.common.console import print_error

                print_error(
                    f"Uninstallation failed at stage '{getattr(e, 'stage', 'unknown')}': {e}"
                )
                if hasattr(e, "details") and e.details:
                    print_error(f"Details: {e.details}")

                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Handle any other unexpected errors
                progress.emergency_stop("Unexpected error during uninstallation")

                # Print unexpected error details
                from ...ui.common.console import print_error

                print_error(f"Unexpected error during uninstallation: {e}")

                raise UninstallationManagerError(
                    message=f"Unexpected error during uninstallation: {e}",
                    details="This is an unexpected error that should be reported",
                ) from e

        print("")
        print_success("✅ W.O.M.M uninstallation completed successfully!")
        print_system(f"📁 Removed from: {self.target_path}")

        # Show completion panel
        completion_content = (
            "WOMM has been successfully removed from your system.\n\n"
            "To complete the cleanup:\n"
            "• Restart your terminal for PATH changes to take effect\n"
            "• Remove any remaining WOMM references from your shell config files\n\n"
            "Thank you for using Works On My Machine!"
        )

        completion_panel = create_panel(
            completion_content,
            title="✅ Uninstallation Complete",
            style="bright_green",
            border_style="bright_green",
            padding=(1, 1),
        )
        print("")
        console.print(completion_panel)

        return True

    # =============================================================================
    # PRIVATE METHODS - PATH OPERATIONS
    # =============================================================================

    def _cleanup_path(self) -> bool:
        """Cleanup PATH environment variable using path management utils.

        Returns:
            True if successful, False otherwise

        Raises:
            PathCleanupError: If PATH cleanup fails
        """
        try:
            result = remove_from_path(self.target_path)
            sleep(0.5)

            if not result:
                from ...ui.common.console import print_error

                print_error("PATH cleanup failed: remove_from_path returned False")

                raise UninstallationPathError(
                    operation="cleanup",
                    path=str(self.target_path),
                    reason="PATH cleanup failed",
                    details="remove_from_path utility returned False",
                )

            return True

        except (UserPathError, RegistryError) as e:
            # Convert user_path_utils exceptions to manager exceptions
            raise UninstallationPathError(
                operation="cleanup",
                path=str(self.target_path),
                reason=f"PATH cleanup failed: {e.message}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Unexpected error during PATH cleanup: {e}")

            raise UninstallationPathError(
                operation="cleanup",
                path=str(self.target_path),
                reason=f"Unexpected error during PATH cleanup: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - FILE OPERATIONS
    # =============================================================================

    def _remove_files_with_progress(
        self, files_to_remove: list[str], progress, verbose: bool = False
    ) -> bool:
        """Remove WOMM installation files with progress tracking.

        Args:
            files_to_remove: List of files and directories to remove for progress tracking
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful

        Raises:
            FileRemovalError: If file removal operations fail
            DirectoryRemovalError: If directory removal operations fail
            UninstallationProgressError: If progress tracking fails
        """
        try:
            import shutil
            from time import sleep

            # Remove each file and directory in order (files first, then directories)
            for i, item_path in enumerate(files_to_remove):
                target_item = self.target_path / item_path.rstrip("/")

                if not target_item.exists():
                    continue

                # Update progress
                item_name = Path(item_path).name
                if item_path.endswith("/"):
                    progress.update_layer(
                        "file_removal", i + 1, f"Removing directory: {item_name}"
                    )
                else:
                    progress.update_layer(
                        "file_removal", i + 1, f"Removing file: {item_name}"
                    )

                try:
                    if target_item.is_file():
                        target_item.unlink()
                        sleep(0.01)
                        if verbose:
                            from ...ui.common.console import print_system

                            print_system(f"🗑️ Removed file: {item_path}")
                    elif target_item.is_dir():
                        shutil.rmtree(target_item)
                        sleep(0.02)
                        if verbose:
                            from ...ui.common.console import print_system

                            print_system(f"🗑️ Removed directory: {item_path}")
                except PermissionError as e:
                    if target_item.is_file():
                        raise UninstallationFileError(
                            operation="remove_file",
                            file_path=str(target_item),
                            reason=f"Permission denied: {e}",
                            details=f"Cannot remove file due to permissions: {item_path}",
                        ) from e
                    else:
                        raise UninstallationFileError(
                            operation="remove_directory",
                            file_path=str(target_item),
                            reason=f"Permission denied: {e}",
                            details=f"Cannot remove directory due to permissions: {item_path}",
                        ) from e
                except OSError as e:
                    if target_item.is_file():
                        raise UninstallationFileError(
                            operation="remove_file",
                            file_path=str(target_item),
                            reason=f"OS error: {e}",
                            details=f"Failed to remove file: {item_path}",
                        ) from e
                    else:
                        raise UninstallationFileError(
                            operation="remove_directory",
                            file_path=str(target_item),
                            reason=f"OS error: {e}",
                            details=f"Failed to remove directory: {item_path}",
                        ) from e

            # Finally remove the root directory itself
            if self.target_path.exists():
                progress.update_layer(
                    "file_removal",
                    len(files_to_remove) + 1,
                    "Removing installation directory",
                )
                try:
                    shutil.rmtree(self.target_path)
                    sleep(0.1)

                    if verbose:
                        from ...ui.common.console import print_system

                        print_system(
                            f"🗑️ Removed installation directory: {self.target_path}"
                        )
                except PermissionError as e:
                    raise UninstallationFileError(
                        operation="remove_directory",
                        file_path=str(self.target_path),
                        reason=f"Permission denied: {e}",
                        details="Cannot remove installation directory due to permissions",
                    ) from e
                except OSError as e:
                    raise UninstallationFileError(
                        operation="remove_directory",
                        file_path=str(self.target_path),
                        reason=f"OS error: {e}",
                        details="Failed to remove installation directory",
                    ) from e

            return True

        except (UninstallationFileError, UninstallationManagerError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected errors to our exception type
            raise UninstallationFileError(
                operation="file_removal",
                file_path=str(self.target_path),
                reason=f"Unexpected error during file removal: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # =============================================================================

    def _verify_uninstallation_with_progress(self, progress) -> bool:
        """Verify uninstallation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed

        Raises:
            UninstallationVerificationError: If verification operations fail
            UninstallationProgressError: If progress tracking fails
        """
        try:
            # Step 1: File removal check
            progress.update_layer("verification", 0, "Checking file removal...")
            if self.target_path.exists():
                raise UninstallationManagerVerificationError(
                    verification_type="file_removal_check",
                    target=str(self.target_path),
                    reason=f"Installation directory still exists: {self.target_path}",
                    details="The target directory was not removed during uninstallation",
                )
            sleep(0.2)

            # Step 2: Command accessibility test
            progress.update_layer("verification", 1, "Testing command accessibility...")
            try:
                verification_result = verify_uninstallation_complete(self.target_path)
            except Exception as e:
                raise UninstallationManagerVerificationError(
                    verification_type="command_accessibility_test",
                    target=str(self.target_path),
                    reason=f"Verification utility failed: {e}",
                    details="The verification utility function raised an exception",
                ) from e

            if not verification_result["success"]:
                raise UninstallationManagerVerificationError(
                    verification_type="command_accessibility_test",
                    target=str(self.target_path),
                    reason=f"Verification failed: {verification_result.get('message', 'Unknown error')}",
                    details="The verification utility returned a failure status",
                )
            sleep(0.2)

            return True

        except (UninstallationManagerVerificationError, UninstallationManagerError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected errors to our exception type
            raise UninstallationManagerVerificationError(
                verification_type="unexpected_error",
                target=str(self.target_path),
                reason=f"Unexpected error during verification: {e}",
                details="This is an unexpected error that should be reported",
            ) from e
