#!/usr/bin/env python3
"""
PATH Manager for Works On My Machine.

Handles PATH backup, restoration, and management operations.
Provides a unified interface for cross-platform PATH management.
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard library imports
import json
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
from rich.console import Console
from rich.table import Table

# Local imports
from ...exceptions.system import FileSystemError, RegistryError, UserPathError
from ...ui import (
    InteractiveMenu,
    create_backup_table,
    format_backup_item,
    print_error,
    print_header,
    print_info,
    print_success,
    print_system,
)
from ...utils.cli_utils import run_silent
from ...utils.system.user_path_utils import (
    extract_path_from_reg_output,
    remove_from_unix_path,
    remove_from_windows_path,
    setup_unix_path,
    setup_windows_path,
)

# =============================================================================
# MAIN CLASS
# =============================================================================


class PathManager:
    """Manages PATH operations for Works On My Machine.

    Provides cross-platform PATH management including backup, restoration,
    and modification operations with integrated UI feedback.
    """

    def __init__(self, target: Optional[str] = None):
        """Initialize the path manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()
        else:
            self.target_path = Path.home() / ".womm"

        self.backup_dir = self.target_path / ".backup"
        self.latest_backup = self.backup_dir / ".path.json"
        self.platform = platform.system()

    # =============================================================================
    # PUBLIC METHODS - UI INTEGRATED
    # =============================================================================

    def list_backup(self) -> None:
        """List available PATH backups with integrated UI.

        This method handles the complete UI flow for listing backup information.
        """
        print_header("W.O.M.M PATH Backup List")

        # Get backup information
        result = self._list_backups()

        # Display results using console functions
        if result["success"]:
            print_system(f"Backup location: {result['backup_location']}")
            print_success("PATH backup information retrieved successfully!")

            if result["backups"]:
                print("")
                # Create and display backup table
                backup_table = create_backup_table(result["backups"])
                console = Console()
                console.print(backup_table)
            else:
                print("")
                print_system("No backup files found")
        else:
            print_error("Failed to retrieve backup information")
            for error in result["errors"]:
                print_error(error)

    def backup_path(self) -> None:
        """Create a new PATH backup with integrated UI.

        This method handles the complete UI flow for creating a new backup.
        """
        print_header("W.O.M.M PATH Backup Creation")

        # Create backup directory if it doesn't exist
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Get current PATH
        if self.platform == "Windows":
            # Read PATH from user registry (HKCU), not from current session
            query = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
            if not query.success:
                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="query",
                    reason="Failed to query Windows user PATH from registry",
                    details=f"Return code: {query.returncode}",
                )
            current_path = extract_path_from_reg_output(query.stdout)
            if not current_path:
                raise UserPathError(
                    message="No PATH value found in Windows user registry",
                    details=f"Registry query succeeded but no PATH value was extracted. Output: {str(query.stdout)}",
                )
        else:
            current_path = os.environ.get("PATH", "")

        # Create JSON backup file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_json = self.backup_dir / f".path_{timestamp}.json"
        sep = os.pathsep or ";"
        entries = [p for p in current_path.split(sep) if p]
        payload = {
            "type": "womm_path_backup",
            "version": 1,
            "timestamp": timestamp,
            "platform": self.platform,
            "target": str(self.target_path),
            "separator": sep,
            "path_string": current_path,
            "entries": entries,
            "length": len(current_path),
        }
        with open(backup_json, "w", encoding="utf-8") as jf:
            json.dump(payload, jf, indent=2, ensure_ascii=False)

        # Update latest backup reference (copy instead of symlink for Windows compatibility)
        if self.latest_backup.exists():
            self.latest_backup.unlink()
        shutil.copy2(backup_json, self.latest_backup)

        # Display success results
        print_success("PATH backup (JSON) created successfully!")
        print_system(f"Backup location: {self.backup_dir}")
        print_system(f"Backup file: {backup_json.name}")
        print_info(f"PATH length: {len(current_path)} characters")

    def restore_path(self) -> None:
        """Restore user PATH from backup with integrated UI.

        This method handles the complete UI flow for PATH restoration.
        """
        console = Console()
        print_header("W.O.M.M PATH Restoration")

        # Check if any backup files exist (JSON only)
        backup_files = list(self.backup_dir.glob(".path_*.json"))
        if not backup_files:
            raise UserPathError(
                message="No PATH backup found",
                details=f"Target path: {self.target_path}, Backup location: {self.backup_dir}, No backup files matching pattern '.path_*.json' found",
            )

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Create selection table
        table = Table(title="Available PATH Backups")
        table.add_column("Index", style="cyan", no_wrap=True)
        table.add_column("Backup File", style="green")
        table.add_column("Date", style="yellow")
        table.add_column("Size", style="blue")
        table.add_column("PATH Entries", style="magenta")

        backup_info_list = []

        for i, backup_file in enumerate(backup_files, 1):
            try:
                stat = backup_file.stat()
                modified_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Read backup JSON content
                data = json.loads(backup_file.read_text(encoding="utf-8"))
                path_value = data.get("path_string", "")
                entries = data.get("entries", [])
                path_entries = len(entries)

                table.add_row(
                    str(i),
                    backup_file.name,
                    modified_date,
                    f"{stat.st_size} bytes",
                    str(path_entries),
                )

                backup_info_list.append(
                    {
                        "file": backup_file,
                        "path_value": path_value,
                        "path_entries": path_entries,
                    }
                )

            except Exception as e:
                print_error(f"Error reading backup {backup_file.name}: {e}")
                continue

        if not backup_info_list:
            raise UserPathError(
                message="No valid backup files found",
                details="All backup files failed to load or parse",
            )

        # Display backup selection table
        console.print(table)
        print("")

        # Interactive selection with checkbox menu
        menu = InteractiveMenu(title="Select Backup to Restore", border_style="cyan")
        selected_backup = menu.select_from_list(
            backup_info_list, display_func=format_backup_item
        )

        if selected_backup is None:
            print_system("Restoration cancelled")
            return

        # Confirm selection
        selected_file = selected_backup["file"]
        path_value = selected_backup["path_value"]
        path_entries = selected_backup["path_entries"]

        print_info(f"Selected: {selected_file.name}")
        print_info(
            f"Date: {datetime.fromtimestamp(selected_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print_info(f"PATH entries: {path_entries}")
        print_info(f"PATH length: {len(path_value)} characters")

        # Ask for confirmation with interactive menu
        confirm_menu = InteractiveMenu(
            title="Confirm Restoration", border_style="yellow"
        )
        if not confirm_menu.confirm_action(
            "Proceed with restoration?", default_yes=True
        ):
            print_system("Restoration cancelled")
            return

        # Restore PATH
        if self.platform == "Windows":
            restore_result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_EXPAND_SZ",
                    "/d",
                    path_value,
                    "/f",
                ]
            )
            if not restore_result.success:
                raise RegistryError(
                    registry_key="HKCU\\Environment",
                    operation="update",
                    reason="Failed to restore Windows user PATH",
                    details=f"Return code: {restore_result.returncode}",
                )
        else:
            # For Unix, we can only update current session
            os.environ["PATH"] = path_value

        # Display success results
        print_success("PATH restored successfully!")
        print_info(f"Restored from backup: {selected_file.name}")
        print_info(f"Restored {path_entries} PATH entries")
        print_info("You may need to restart your terminal for changes to take effect")

    # =============================================================================
    # PUBLIC METHODS - UTILITY OPERATIONS
    # =============================================================================

    def add_to_path(self) -> Dict:
        """Add WOMM to PATH environment variable.

        Returns:
            Dictionary with operation results
        """
        try:
            womm_path = str(self.target_path)

            if self.platform == "Windows":
                return setup_windows_path(womm_path, "")
            else:
                return setup_unix_path(womm_path, "")

        except RegistryError as e:
            return {
                "success": False,
                "error": f"Error adding to PATH: Registry {e.operation} failed for {e.registry_key}: {e.reason}",
            }
        except FileSystemError as e:
            return {
                "success": False,
                "error": f"Error adding to PATH: File {e.operation} failed for {e.file_path}: {e.reason}",
            }
        except UserPathError as e:
            return {"success": False, "error": f"Error adding to PATH: {e.message}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error adding to PATH: {e}"}

    def remove_from_path(self) -> Dict:
        """Remove WOMM from PATH environment variable.

        Returns:
            Dictionary with operation results
        """
        try:
            womm_path = str(self.target_path)

            if self.platform == "Windows":
                return remove_from_windows_path(womm_path)
            else:
                return remove_from_unix_path(womm_path)

        except RegistryError as e:
            return {
                "success": False,
                "error": f"Error removing from PATH: Registry {e.operation} failed for {e.registry_key}: {e.reason}",
            }
        except FileSystemError as e:
            return {
                "success": False,
                "error": f"Error removing from PATH: File {e.operation} failed for {e.file_path}: {e.reason}",
            }
        except UserPathError as e:
            return {"success": False, "error": f"Error removing from PATH: {e.message}"}
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error removing from PATH: {e}",
            }

    # =============================================================================
    # PRIVATE METHODS - INTERNAL OPERATIONS
    # =============================================================================

    def _backup_path(self) -> Dict:
        """Backup the current user PATH.

        Returns:
            Dictionary containing backup results
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backup_files": [],
            "errors": [],
        }

        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Get current PATH
            if self.platform == "Windows":
                # Read PATH from user registry (HKCU), not from current session
                query = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
                if not query.success:
                    result["errors"].append(
                        "Failed to query Windows user PATH from registry"
                    )
                    return result
                current_path = extract_path_from_reg_output(query.stdout)
                if not current_path:
                    result["errors"].append(
                        "No PATH value found in Windows user registry"
                    )
                    return result
            else:
                current_path = os.environ.get("PATH", "")

            # Create JSON backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_json = self.backup_dir / f".path_{timestamp}.json"
            sep = os.pathsep or ";"
            entries = [p for p in current_path.split(sep) if p]
            payload = {
                "type": "womm_path_backup",
                "version": 1,
                "timestamp": timestamp,
                "platform": self.platform,
                "target": str(self.target_path),
                "separator": sep,
                "path_string": current_path,
                "entries": entries,
                "length": len(current_path),
            }
            with open(backup_json, "w", encoding="utf-8") as jf:
                json.dump(payload, jf, indent=2, ensure_ascii=False)

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            if self.latest_backup.exists():
                self.latest_backup.unlink()
            shutil.copy2(backup_json, self.latest_backup)

            # Get list of all backup files (JSON only)
            backup_files = sorted(self.backup_dir.glob(".path_*.json"), reverse=True)
            result["backup_files"] = [str(f.name) for f in backup_files]
            result["success"] = True

            return result

        except Exception as e:
            result["errors"].append(f"Error creating PATH backup: {e}")
            return result

    def _list_backups(self) -> Dict:
        """List available PATH backups.

        Returns:
            Dictionary containing backup information
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backups": [],
            "latest_backup": "",
            "errors": [],
        }

        try:
            if not self.backup_dir.exists():
                result["errors"].append("No backup directory found")
                return result

            # Get all backup files (JSON only)
            backup_files = list(self.backup_dir.glob(".path_*.json"))
            if not backup_files:
                result["errors"].append("No PATH backups found")
                return result

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                try:
                    stat = backup_file.stat()
                    data = json.loads(backup_file.read_text(encoding="utf-8"))
                    backup_info = {
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "description": f"JSON backup ({data.get('timestamp', '')})",
                    }
                    result["backups"].append(backup_info)

                    # Mark as latest if it's the most recent
                    if not result["latest_backup"]:
                        result["latest_backup"] = backup_file.name

                except Exception as e:
                    result["errors"].append(f"Error listing backups: {e}")
                    continue

            result["success"] = True
            return result

        except Exception as e:
            result["errors"].append(f"Error listing backups: {e}")
            return result
