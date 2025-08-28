#!/usr/bin/env python3
"""
Installation Manager for Works On My Machine.

This module handles the complete installation process of WOMM to the user's
home directory, using utility functions for core operations.

Author: WOMM Team
Version: 2.2.0
"""

# IMPORTS
########################################################
# Standard library imports
import platform
import shutil
from pathlib import Path
from time import sleep
from typing import Optional

# Local imports
from ...exceptions.installation import (
    ExecutableVerificationError,
    FileVerificationError,
    InstallationFileError,
    InstallationManagerError,
    InstallationPathError,
    InstallationSystemError,
    InstallationUtilityError,
    InstallationVerificationError,
    PathUtilityError,
)
from ...exceptions.system import FileSystemError, RegistryError, UserPathError
from ...utils.installation import (
    create_womm_executable,
    get_current_womm_path,
    get_files_to_copy,
    get_target_womm_path,
    verify_commands_accessible,
    verify_files_copied,
    verify_path_configuration,
)

# =============================================================================
# MAIN CLASS
# =============================================================================


class InstallationManager:
    """Manages the installation process for Works On My Machine.

    This class handles all aspects of installing Works On My Machine to the user's
    system, including:
        - File copying and directory structure setup
        - PATH environment variable configuration
        - Registry modifications (Windows)
        - Backup creation for safe rollback
        - Interactive UI with progress tracking
        - Security validation throughout the process

    The installer supports both development (git clone) and PyPI installations,
    with automatic detection and appropriate handling for each scenario.
    """

    def __init__(self):
        """Initialize the installation manager."""
        self.source_path = get_current_womm_path()
        self.target_path = get_target_womm_path()
        self.actions = []
        self.platform = platform.system()
        # Track backup file for potential rollback after failures
        self._path_backup_file: Optional[str] = None

    # =============================================================================
    # PUBLIC METHODS
    # =============================================================================

    def install(
        self,
        target: Optional[str] = None,
        force: bool = False,
        backup: bool = True,
        dry_run: bool = False,
        verbose: bool = False,
        refresh_env: bool = True,
    ) -> bool:
        """Install Works On My Machine to the user's system.

        Args:
            target: Custom target directory (default: ~/.womm)
            force: Force installation even if already installed
            backup: Create backup before installation
            dry_run: Show what would be done without making changes
            verbose: Show detailed progress information
            refresh_env: Refresh environment variables after PATH setup (Windows only)

        Returns:
            True if installation successful, False otherwise
        """
        # Override target path if specified
        if target:
            self.target_path = Path(target).expanduser().resolve()

        # Store refresh_env setting for use in _setup_path
        self._refresh_env = refresh_env

        # Import UI modules
        from ...ui.common.console import (
            console,
            print_header,
            print_install,
            print_success,
            print_system,
        )
        from ...ui.common.extended.dynamic_progress import (
            create_dynamic_layered_progress,
        )
        from ...ui.common.panels import create_panel

        print_header("W.O.M.M Installation")

        # Check target directory existence
        from ...ui.common.progress import create_spinner_with_status

        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            progress.update(task, status="Analyzing installation requirements...")

            # Check if WOMM is already installed
            if (
                self.target_path.exists()
                and any(self.target_path.iterdir())
                and not force
            ):
                from ...ui.common.prompts import show_warning_panel

                show_warning_panel(
                    "Installation directory already exists",
                    f"Target directory: {self.target_path}\n"
                    "Use --force to overwrite existing installation",
                )
                return False

        if dry_run:
            print_system("DRY RUN MODE - No changes will be made")

        # Get list of files to copy
        console.print("")
        with create_spinner_with_status("Analyzing source files...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning source directory...")
            files_to_copy = get_files_to_copy(self.source_path)
            progress.update(task, status=f"Found {len(files_to_copy)} files to copy")

        if dry_run:
            if backup:
                print_install("Would backup current PATH configuration")
            print_install(
                f"Would copy {len(files_to_copy)} files to {self.target_path}"
            )
            print_install("Would setup PATH configuration")
            print_install("Would create executable script")
            print_install("Would verify installation")
            if verbose:
                print_system("🔍 Dry run mode - detailed logging enabled")
                for file_path in files_to_copy[:5]:  # Show first 5 files as sample
                    print_system(f"  📄 Would copy: {file_path}")
                if len(files_to_copy) > 5:
                    print_system(f"  ... and {len(files_to_copy) - 5} more files")
            return True

        # Define installation stages with DynamicLayeredProgress
        # Color palette: unified cyan for all steps, semantic colors for states
        stages = [
            {
                "name": "main_installation",
                "type": "main",
                "steps": [
                    "Preparation",
                    "File Copy",
                    "Executable",
                    "Backup",
                    "PATH Setup",
                    "Environment",
                    "Verification",
                ],
                "description": "WOMM Installation Progress",
                "style": "bold bright_white",
            },
            {
                "name": "preparation",
                "type": "spinner",
                "description": "Preparing installation environment...",
                "style": "bright_blue",
            },
            {
                "name": "file_copy",
                "type": "progress",
                "total": len(files_to_copy),
                "description": "Copying project files...",
                "style": "bright_blue",
            },
            {
                "name": "executable",
                "type": "spinner",
                "description": "Creating executable script...",
                "style": "bright_blue",
            },
            {
                "name": "backup",
                "type": "spinner",
                "description": "Creating PATH backup...",
                "style": "bright_blue",
            },
            {
                "name": "path_setup",
                "type": "spinner",
                "description": "Configuring PATH environment...",
                "style": "bright_blue",
            },
            {
                "name": "refresh_env",
                "type": "spinner",
                "description": "Refreshing environment variables...",
                "style": "bright_blue",
            },
            {
                "name": "verification",
                "type": "steps",
                "steps": [
                    "File integrity check",
                    "Essential files verification",
                    "Command accessibility test",
                    "PATH configuration test",
                ],
                "description": "Verifying installation...",
                "style": "bright_blue",
            },
        ]

        console.print("")
        with create_dynamic_layered_progress(stages) as progress:
            try:
                # Stage 1: Preparation
                prep_messages = [
                    "Analyzing system requirements...",
                    "Checking target directory permissions...",
                    "Validating installation path...",
                    "Preparing file operations...",
                ]

                for msg in prep_messages:
                    progress.update_layer("preparation", 0, msg)
                    sleep(0.2)

                # Complete preparation
                progress.complete_layer("preparation")

                # Update main installation progress
                progress.update_layer("main_installation", 0, "Preparation completed")
                sleep(0.3)

                # Stage 2: Copy files
                self._copy_files_with_progress(files_to_copy, progress, verbose)

                # Complete file copy
                progress.complete_layer("file_copy")

                # Update main installation progress
                progress.update_layer("main_installation", 1, "Files copied")
                sleep(0.3)

                # Stage 3: Create executable
                progress.update_layer("executable", 0, "Creating womm.py executable...")
                executable_result = create_womm_executable(self.target_path)
                if not executable_result["success"]:
                    progress.emergency_stop(
                        f"Failed to create executable: {executable_result.get('error')}"
                    )
                    raise ExecutableVerificationError(
                        executable_name="womm",
                        reason=executable_result.get("error", "Unknown error"),
                        details="Failed to create WOMM executable",
                    )

                progress.update_layer("executable", 0, "Creating womm.bat wrapper...")
                sleep(0.2)

                # Complete executable creation
                progress.complete_layer("executable")

                # Update main installation progress
                progress.update_layer("main_installation", 2, "Executable created")
                sleep(0.3)

                # Stage 4: Backup PATH
                progress.update_layer(
                    "backup", 0, "Backing up current PATH configuration..."
                )
                if not self._backup_path():
                    progress.emergency_stop("Failed to backup PATH")
                    raise InstallationPathError(
                        operation="backup",
                        path=str(self.target_path),
                        reason="Could not create PATH backup before installation",
                        details="PATH backup operation failed",
                    )

                progress.update_layer("backup", 0, "PATH backup completed")
                sleep(0.2)

                # Complete backup
                progress.complete_layer("backup")

                # Update main installation progress
                progress.update_layer("main_installation", 3, "PATH backup completed")
                sleep(0.3)

                # Stage 5: Setup PATH
                progress.update_layer(
                    "path_setup", 0, "Configuring PATH environment variable..."
                )
                if not self._setup_path():
                    progress.emergency_stop("Failed to setup PATH")
                    self._rollback_path()  # Rollback on failure
                    raise InstallationPathError(
                        operation="setup",
                        path=str(self.target_path),
                        reason="PATH environment variable configuration failed",
                        details="PATH setup operation failed",
                    )

                progress.update_layer("path_setup", 0, "PATH configuration completed")
                sleep(0.2)

                # Complete PATH setup
                progress.complete_layer("path_setup")

                # Update main installation progress
                progress.update_layer("main_installation", 4, "PATH configured")
                sleep(0.3)

                # Stage 5: Environment Refresh (Windows only)
                if self.platform == "Windows" and self._refresh_env:
                    progress.update_layer(
                        "refresh_env", 0, "Refreshing environment variables..."
                    )
                    try:
                        self._refresh_environment()
                        progress.update_layer(
                            "refresh_env", 0, "Environment refresh completed"
                        )
                    except Exception as e:
                        progress.emergency_stop("Environment refresh failed")
                        raise InstallationSystemError(
                            operation="environment_refresh",
                            reason="Environment refresh failed",
                            details=str(e),
                        ) from e

                        # Complete refresh_env step
                    progress.complete_layer("refresh_env")

                    # Update main installation progress
                    progress.update_layer(
                        "main_installation", 5, "Environment refreshed"
                    )
                    sleep(0.3)
                else:
                    # Skip refresh_env step for non-Windows or when disabled
                    progress.complete_layer("refresh_env")
                    progress.update_layer(
                        "main_installation", 5, "Environment refresh skipped"
                    )
                    sleep(0.1)

                # Stage 6: Verification
                self._verify_installation_with_progress(progress)

                # Complete verification
                progress.complete_layer("verification")

                # Complete main installation progress
                progress.update_layer("main_installation", 6, "Installation completed!")
                sleep(0.3)

                # Final completion for main installation
                sleep(0.5)

                # Complete and remove main installation layer
                progress.complete_layer("main_installation")

            except (
                InstallationUtilityError,
                InstallationFileError,
                InstallationPathError,
                InstallationSystemError,
                InstallationVerificationError,
                # Utility exceptions that might be raised by utility functions
                FileVerificationError,
                PathUtilityError,
                ExecutableVerificationError,
                # System exceptions that might be raised by user_path_manager
                UserPathError,
                RegistryError,
                FileSystemError,
            ) as e:
                # Stop progress first, then print error details
                progress.emergency_stop(f"Installation failed: {type(e).__name__}")

                # Now safe to print error details
                from ...ui.common.console import print_error

                print_error(f"Installation failed: {e.message}")
                if e.details:
                    print_error(f"Details: {e.details}")

                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Handle any other unexpected errors
                progress.emergency_stop("Unexpected error during installation")

                # Print unexpected error details
                from ...ui.common.console import print_error

                print_error(f"Unexpected error during installation: {e}")

                raise InstallationManagerError(
                    message=f"Unexpected error during installation: {e}",
                    details="This is an unexpected error that should be reported",
                ) from e

        console.print("")
        print_success("✅ W.O.M.M installation completed successfully!")
        print_system(f"📁 Installed to: {self.target_path}")

        # Show Windows-specific PATH info if needed
        if self.platform == "Windows":
            from ...ui.common.console import print_tip

            print_tip(
                "On Windows, the 'womm' command will be available in new terminal sessions."
            )
            print_tip("To use it immediately in this terminal, run: womm refresh-env")

        # Show completion panel
        completion_content = (
            "WOMM has been successfully installed on your system.\n\n"
            "Getting started:\n"
            "• Run 'womm --help' to see all available commands\n"
            "• Try 'womm init' to set up a new project\n"
            "• Use 'womm deploy' to manage your development tools\n\n"
            "• Restart your terminal for PATH changes to take effect\n\n"
            "Welcome to Works On My Machine!"
        )

        completion_panel = create_panel(
            completion_content,
            title="✅ Installation Complete",
            style="bright_green",
            border_style="bright_green",
            padding=(1, 1),
        )
        console.print("")
        console.print(completion_panel)

        return True

    # =============================================================================
    # PRIVATE METHODS - FILE OPERATIONS
    # =============================================================================

    def _copy_files_with_progress(
        self,
        files_to_copy: list[str],
        progress,
        verbose: bool = False,
    ) -> bool:
        """Copy files from source to target directory with progress tracking.

        Args:
            files_to_copy: List of relative file paths to copy
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise

        Raises:
            FileVerificationError: If file copying fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Create target directory (womm subdirectory)
            womm_target_path = self.target_path / "womm"
            womm_target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with progress tracking
            for i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file
                target_file = womm_target_path / relative_file

                # Update file copy progress
                file_name = Path(relative_file).name
                progress.update_layer("file_copy", i + 1, f"Copying: {file_name}")

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(source_file, target_file)
                sleep(0.01)

                if verbose:
                    # Silent mode during progress - details shown in progress bar
                    pass

            return True

        except OSError as e:
            # Stop progress and raise specific exception
            progress.emergency_stop("File copy failed")

            raise FileVerificationError(
                verification_type="file_copy",
                file_path=str(source_file),
                reason=str(e),
                details=f"Failed at file {i + 1}/{len(files_to_copy)}: {relative_file}",
            ) from e
        except Exception as e:
            # Stop progress and raise manager exception
            progress.emergency_stop("Unexpected error during file copy")

            raise InstallationFileError(
                operation="copy",
                file_path=str(source_file),
                reason=f"Unexpected error during file copy: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    def _copy_files(
        self,
        files_to_copy: list[str],
        verbose: bool = False,
        progress=None,
        file_task_id=None,
    ) -> bool:
        """Copy files from source to target directory.

        Args:
            files_to_copy: List of relative file paths to copy
            verbose: Show detailed progress information
            progress: Progress instance (optional)
            file_task_id: Progress task ID (optional)

        Returns:
            True if successful, False otherwise

        Raises:
            FileVerificationError: If file copying fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Create target directory (womm subdirectory)
            womm_target_path = self.target_path / "womm"
            womm_target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with layered progress bar
            for _i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file
                target_file = womm_target_path / relative_file

                # Update file copy progress bar
                if progress and file_task_id is not None:
                    file_name = Path(relative_file).name
                    progress.update(file_task_id, details=f"Copying: {file_name}")

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(source_file, target_file)
                sleep(0.01)

                # Advance file copy progress
                if progress and file_task_id is not None:
                    progress.advance(file_task_id)

                if verbose and progress and file_task_id is not None:
                    # Update progress details instead of printing directly
                    progress.update(
                        file_task_id, description=f"Copying files... ({relative_file})"
                    )

            return True

        except OSError as e:
            # Stop progress and raise specific exception
            if progress:
                progress.emergency_stop("File copy failed")

            raise FileVerificationError(
                verification_type="file_copy",
                file_path=str(source_file),
                reason=str(e),
                details=f"Failed at file {_i + 1}/{len(files_to_copy)}: {relative_file}",
            ) from e
        except Exception as e:
            # Stop progress and raise manager exception
            if progress:
                progress.emergency_stop("Unexpected error during file copy")

            raise InstallationFileError(
                operation="copy",
                file_path=str(source_file),
                reason=f"Unexpected error during file copy: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - PATH OPERATIONS
    # =============================================================================

    def _setup_path(self) -> bool:
        """Setup PATH environment variable using PathManager.

        Returns:
            True if successful, False otherwise

        Raises:
            PathUtilityError: If PATH setup fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))
            result = path_manager.add_to_path()
            sleep(0.5)

            if not result["success"]:
                from ...ui.common.console import print_error

                print_error(
                    f"PATH setup failed: {result.get('error', 'Unknown error')}"
                )
                if "stderr" in result:
                    print_error(f"stderr: {result['stderr']}")

                raise PathUtilityError(
                    operation="path_setup",
                    path=str(self.target_path),
                    reason="PATH setup failed",
                    details=f"PathManager error: {result.get('error', 'Unknown error')}",
                )

            # Note: Environment refresh is now handled as a separate step
            return True

        except PathUtilityError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Note: PATH setup is not called within progress context, safe to print immediately
            from ...ui.common.console import print_error

            print_error(f"Unexpected error setting up PATH: {e}")

            raise InstallationPathError(
                operation="setup",
                path=str(self.target_path),
                reason=f"Unexpected error setting up PATH: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    def _refresh_environment(self) -> bool:
        """Refresh environment variables using RefreshEnv.cmd (Windows only).

        Returns:
            True if successful, False otherwise

        Raises:
            InstallationUtilityError: If environment refresh fails
        """
        try:
            from ...utils.cli_utils import run_silent

            # Try multiple possible locations for RefreshEnv.cmd
            possible_paths = [
                self.target_path
                / "womm"
                / "bin"
                / "RefreshEnv.cmd",  # Full installation
                self.target_path / "bin" / "RefreshEnv.cmd",  # Direct structure
                self.source_path
                / "womm"
                / "bin"
                / "RefreshEnv.cmd",  # Development context
                self.source_path
                / "bin"
                / "RefreshEnv.cmd",  # Alternative dev structure
            ]

            refresh_env_path = None
            for path in possible_paths:
                if path.exists():
                    refresh_env_path = path
                    break

            if refresh_env_path is None:
                # Create temporary debug info for user
                import tempfile

                debug_file = Path(tempfile.gettempdir()) / "womm_refreshenv_debug.txt"
                with open(debug_file, "w") as f:
                    f.write("RefreshEnv.cmd search results:\n")
                    f.write(f"Target path: {self.target_path}\n")
                    f.write(f"Source path: {self.source_path}\n")
                    for i, path in enumerate(possible_paths):
                        f.write(
                            f"Path {i + 1}: {path} - {'EXISTS' if path.exists() else 'NOT FOUND'}\n"
                        )
                    f.write("\nActual directory contents:\n")
                    if self.target_path.exists():
                        f.write(
                            f"Target contents: {list(self.target_path.rglob('*'))}\n"
                        )

                # Silently skip if RefreshEnv.cmd not found (normal in some setups)
                return True

            # Execute RefreshEnv.cmd silently (don't interrupt progress display)
            result = run_silent([str(refresh_env_path)])

            if result.success:
                # Environment refreshed successfully (silent)
                return True
            else:
                # Don't fail installation if refresh fails, continue silently
                # Note: Warning logged but not displayed during progress
                return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error refreshing environment: {e}")
            # Don't fail installation if refresh fails, but raise exception for logging
            raise InstallationSystemError(
                operation="environment_refresh",
                reason=f"Environment refresh failed: {e}",
                details="RefreshEnv.cmd execution failed",
            ) from e

    def _backup_path(self) -> bool:
        """Backup current PATH configuration using PathManager.

        Returns:
            True if backup successful, False otherwise

        Raises:
            InstallationUtilityError: If PATH backup fails
        """
        try:
            from ...exceptions.system import (
                FileSystemError,
                RegistryError,
                UserPathError,
            )
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))
            backup_result = path_manager._backup_path()

            if backup_result["success"]:
                # Keep backup reference for potential rollback
                backup_files = backup_result.get("backup_files", [])
                if backup_files:
                    latest_name = backup_files[0]
                    self._path_backup_file = str(
                        (path_manager.backup_dir / latest_name).resolve()
                    )
                return True
            else:
                from ...ui.common.console import print_error

                print_error(f"PATH backup failed: {backup_result.get('error')}")

                raise InstallationPathError(
                    operation="backup",
                    path=str(self.target_path),
                    reason="PATH backup failed",
                    details=f"PathManager backup error: {backup_result.get('error')}",
                )

        except UserPathError as e:
            # Convert UserPathError to installation exception
            raise InstallationPathError(
                operation="backup",
                path=str(self.target_path),
                reason=f"PATH backup failed: {e.message}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except RegistryError as e:
            # Convert RegistryError to installation exception
            raise InstallationPathError(
                operation="backup",
                path=str(self.target_path),
                reason=f"PATH backup failed: Registry {e.operation} failed for {e.registry_key}: {e.reason}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except FileSystemError as e:
            # Convert FileSystemError to installation exception
            raise InstallationPathError(
                operation="backup",
                path=str(self.target_path),
                reason=f"PATH backup failed: File {e.operation} failed for {e.file_path}: {e.reason}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Unexpected error during PATH backup: {e}")

            raise InstallationPathError(
                operation="backup",
                path=str(self.target_path),
                reason=f"Unexpected error during PATH backup: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    def _rollback_path(self) -> bool:
        """Rollback PATH to previous state using PathManager backup.

        Returns:
            True if rollback successful, False otherwise

        Raises:
            InstallationUtilityError: If PATH rollback fails
        """
        try:
            if not self._path_backup_file:
                from ...ui.common.console import print_error

                print_error("No backup file available for rollback")

                raise InstallationPathError(
                    operation="rollback",
                    path=str(self.target_path),
                    reason="No backup file available for rollback",
                    details="PATH backup file not found for rollback",
                )

            # Use PathManager to restore from specific backup file
            import json
            from pathlib import Path

            from ...exceptions.system import (
                FileSystemError,
                RegistryError,
                UserPathError,
            )

            backup_file = Path(self._path_backup_file)
            if not backup_file.exists():
                from ...ui.common.console import print_error

                print_error(f"Backup file not found: {backup_file}")

                raise InstallationPathError(
                    operation="rollback",
                    path=str(backup_file),
                    reason="Backup file not found for rollback",
                    details=f"Backup file not found at: {backup_file}",
                )

            # Read backup data to get the PATH string
            with open(backup_file, encoding="utf-8") as f:
                backup_data = json.load(f)

            restored_path = backup_data.get("path_string", "")
            if not restored_path:
                from ...ui.common.console import print_error

                print_error("Invalid backup file: no PATH string found")

                raise InstallationPathError(
                    operation="rollback",
                    path=str(backup_file),
                    reason="Invalid backup file for rollback",
                    details="Backup file contains no PATH string",
                )

            # Use PathManager's platform-specific restore logic
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))

            if path_manager.platform == "Windows":
                from ...utils.cli_utils import run_silent

                result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        restored_path,
                        "/f",
                    ]
                )

                if result.success:
                    from ...ui.common.console import print_success

                    print_success("PATH successfully rolled back to previous state")
                    return True
                else:
                    from ...ui.common.console import print_error

                    print_error(f"PATH rollback failed: {result.stderr}")

                    raise InstallationPathError(
                        operation="rollback",
                        path=str(self.target_path),
                        reason="PATH rollback failed: Registry update failed",
                        details=f"Windows registry update failed: {result.stderr}",
                    )
            else:
                # Unix rollback - update environment
                import os

                os.environ["PATH"] = restored_path
                from ...ui.common.console import print_success

                print_success("PATH successfully rolled back to previous state")
                return True

        except UserPathError as e:
            # Convert UserPathError to installation exception
            raise InstallationPathError(
                operation="rollback",
                path=str(self.target_path),
                reason=f"PATH rollback failed: {e.message}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except RegistryError as e:
            # Convert RegistryError to installation exception
            raise InstallationPathError(
                operation="rollback",
                path=str(self.target_path),
                reason=f"PATH rollback failed: Registry {e.operation} failed for {e.registry_key}: {e.reason}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except FileSystemError as e:
            # Convert FileSystemError to installation exception
            raise InstallationPathError(
                operation="rollback",
                path=str(self.target_path),
                reason=f"PATH rollback failed: File {e.operation} failed for {e.file_path}: {e.reason}",
                details=f"Original error: {type(e).__name__} - {e.details}",
            ) from e
        except (
            InstallationUtilityError,
            InstallationFileError,
            InstallationPathError,
            InstallationSystemError,
            InstallationVerificationError,
            # Utility exceptions that might be raised by utility functions
            FileVerificationError,
            PathUtilityError,
            ExecutableVerificationError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Unexpected error during PATH rollback: {e}")

            raise InstallationPathError(
                operation="rollback",
                path=str(self.target_path),
                reason=f"Unexpected error during PATH rollback: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # =============================================================================

    def _verify_installation_with_progress(self, progress) -> bool:
        """Verify installation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed, False otherwise

        Raises:
            FileVerificationError: If file verification fails
            ExecutableVerificationError: If executable verification fails
            PathUtilityError: If PATH verification fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Step 1: File integrity check
            progress.update_layer("verification", 0, "Checking file integrity...")

            try:
                verify_files_copied(self.source_path, self.target_path)
                # If we get here, verification passed (no exception raised)
            except Exception as e:
                # Stop progress and handle the exception
                progress.emergency_stop("File verification failed")

                # Re-raise as file verification error
                raise FileVerificationError(
                    verification_type="file_integrity",
                    file_path=str(self.target_path),
                    reason=str(e),
                    details="Files are missing or corrupted",
                ) from e

            sleep(0.2)

            # Step 2: Essential files verification
            progress.update_layer("verification", 1, "Verifying essential files...")
            essential_files = ["womm.py", "womm.bat"]
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    progress.emergency_stop("Essential file missing")

                    raise FileVerificationError(
                        verification_type="essential_files",
                        file_path=str(file_path),
                        reason=f"Essential file missing: {essential_file}",
                        details=f"Required file not found at {file_path}",
                    )
            sleep(0.2)

            # Step 3: Command accessibility test
            progress.update_layer("verification", 2, "Testing command accessibility...")

            # Environment refresh is now handled in a separate step before verification

            try:
                result = verify_commands_accessible(str(self.target_path))
                # Check result details
                if isinstance(result, dict):
                    if result.get("warning"):
                        # Windows case: local works but global doesn't - this is expected
                        pass
                    elif result.get("path_status") == "enhanced_success":
                        # Great! Global test succeeded with PATH enhancement
                        pass
                    # If we get here, verification passed
            except Exception as e:
                # On Windows, check if it's the expected PATH timing issue
                if (
                    self.platform == "Windows"
                    and "Local executable works but global command failed" in str(e)
                ):
                    # Continue with installation since local executable works (don't print during progress)
                    # Note: Windows PATH timing issue - command will be available in new terminals
                    sleep(0.2)
                else:
                    # Stop progress and handle the exception
                    progress.emergency_stop("Command verification failed")

                    raise ExecutableVerificationError(
                        executable_name="womm",
                        reason=str(e),
                        details="WOMM commands are not accessible",
                    ) from e
            sleep(0.2)

            # Step 4: PATH configuration test
            progress.update_layer("verification", 3, "Verifying PATH configuration...")

            try:
                verify_path_configuration(str(self.target_path))
                # If we get here, verification passed (no exception raised)
            except Exception as e:
                # Stop progress and handle the exception
                progress.emergency_stop("PATH verification failed")

                raise PathUtilityError(
                    operation="path_configuration",
                    path=str(self.target_path),
                    reason=str(e),
                    details="PATH environment variable is not configured correctly",
                ) from e
            sleep(0.2)

            return True

        except (FileVerificationError, ExecutableVerificationError, PathUtilityError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Stop progress and handle unexpected errors
            progress.emergency_stop("Unexpected error during verification")

            raise InstallationVerificationError(
                verification_type="unexpected_error",
                target=str(self.target_path),
                reason=f"Unexpected error during verification: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    def _verify_installation(self) -> bool:
        """Verify that the installation completed successfully.

        Returns:
            True if verification passed, False otherwise

        Raises:
            FileVerificationError: If file verification fails
            ExecutableVerificationError: If executable verification fails
            PathUtilityError: If PATH verification fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Use utils for verification

            # 0. Verify all files were copied correctly
            try:
                verify_files_copied(self.source_path, self.target_path)
                # If we get here, verification passed (no exception raised)
            except Exception as e:
                from ...ui.common.console import print_error

                print_error(f"File verification failed: {e}")

                raise FileVerificationError(
                    verification_type="file_integrity",
                    file_path=str(self.target_path),
                    reason=str(e),
                    details="Files are missing or corrupted",
                ) from e

            # 1. Verify essential files exist (basic check during installation)
            essential_files = ["womm.py", "womm.bat"]
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    from ...ui.common.console import print_error

                    print_error(f"Essential file missing: {essential_file}")

                    raise FileVerificationError(
                        verification_type="essential_files",
                        file_path=str(file_path),
                        reason=f"Essential file missing: {essential_file}",
                        details=f"Required file not found at {file_path}",
                    )

            # 2. Verify commands are accessible in PATH
            try:
                verify_commands_accessible(str(self.target_path))
                # If we get here, verification passed (no exception raised)
            except Exception as e:
                from ...ui.common.console import print_error

                print_error(f"Commands not accessible: {e}")

                raise ExecutableVerificationError(
                    executable_name="womm",
                    reason=str(e),
                    details="WOMM commands are not accessible",
                ) from e

            # 3. Verify PATH configuration
            try:
                verify_path_configuration(str(self.target_path))
                # If we get here, verification passed (no exception raised)
            except Exception as e:
                from ...ui.common.console import print_error

                print_error(f"PATH configuration failed: {e}")

                raise PathUtilityError(
                    operation="path_configuration",
                    path=str(self.target_path),
                    reason=str(e),
                    details="PATH environment variable is not configured correctly",
                ) from e

            return True

        except (FileVerificationError, ExecutableVerificationError, PathUtilityError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Unexpected error during verification: {e}")

            raise InstallationVerificationError(
                verification_type="unexpected_error",
                target=str(self.target_path),
                reason=f"Unexpected error during verification: {e}",
                details="This is an unexpected error that should be reported",
            ) from e
