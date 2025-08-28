#!/usr/bin/env python3
"""
Context menu manager.

This module orchestrates context menu operations using the modular architecture.
It coordinates ScriptDetector, IconManager, and RegistryUtils to provide
a unified interface for context menu management.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from ..utils.context_parameters import ContextParameters, ContextType
from ..utils.registry_utils import RegistryUtils
from ..utils.validation import ValidationUtils
from .backup_manager import BackupManager
from .icon_manager import IconManager
from .script_detector import ScriptDetector, ScriptType


class ContextMenuManager:
    """Context menu manager - orchestrates all context menu operations."""

    def __init__(self):
        """Initialize the context menu manager with all required components."""
        self.script_detector = ScriptDetector()
        self.icon_manager = IconManager()
        self.registry_utils = RegistryUtils()
        self.backup_manager = BackupManager()
        self.validation_utils = ValidationUtils()

    def register_script(
        self,
        script_path: str,
        label: str,
        icon: Optional[str] = None,
        dry_run: bool = False,
        context_params: Optional[ContextParameters] = None,
    ) -> Dict[str, Any]:
        """
        Register a script in the Windows context menu.

        Args:
            script_path: Path to the script or executable
            label: Display name in context menu
            icon: Icon path or 'auto' for auto-detection
            dry_run: If True, show what would be done without making changes

        Returns:
            Dict containing operation result and details
        """
        try:
            # Comprehensive validation using ValidationUtils
            validation_result = ValidationUtils.validate_command_parameters(
                script_path, label, icon
            )
            if not validation_result["valid"]:
                error_message = "; ".join(validation_result["errors"])
                return {
                    "success": False,
                    "error": f"Validation failed: {error_message}",
                    "validation_details": validation_result,
                }

            # Detect script type and get info
            script_info = ScriptDetector.get_script_info(script_path)
            script_type = script_info["type"]

            # Resolve icon
            icon_path = self.icon_manager.resolve_icon(icon or "auto", script_path)
            if icon_path is None and icon and icon.lower() != "auto":
                # Fallback to default icon for script type
                icon_path = script_info["default_icon"]

            # Generate registry key name
            registry_key_name = self.registry_utils.generate_registry_key_name(
                script_path
            )

            # Build command
            command = script_info["command"]

            # Use context parameters if provided, otherwise use defaults
            if context_params is None:
                context_params = ContextParameters.from_flags()

            # Validate context parameters
            validation = context_params.validate_parameters()
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": f"Context parameter validation failed: {'; '.join(validation['errors'])}",
                    "validation_details": validation,
                }

            # Show warnings if any
            if validation["warnings"]:
                print(f"⚠️  Warnings: {'; '.join(validation['warnings'])}")

            # Build final command for display (use first context type for dry-run)
            context_types = list(context_params.context_types)
            if context_types:
                final_command = context_params.build_command(command, context_types[0])
            else:
                final_command = command

            # Prepare result info
            result_info = {
                "script_path": script_path,
                "script_type": script_type,
                "label": label,
                "icon_path": icon_path,
                "registry_key": registry_key_name,
                "command": final_command,
                "context_info": context_params.get_description(),
            }

            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "info": result_info,
                }

            # Get registry paths and add entries
            registry_paths = context_params.get_registry_paths()
            success_count = 0
            total_paths = len(registry_paths)

            for registry_path in registry_paths:
                full_path = f"{registry_path}\\{registry_key_name}"

                # Build command with appropriate parameters for this context type
                context_type = self._get_context_type_from_path(registry_path)
                final_command = context_params.build_command(command, context_type)

                success = self.registry_utils.add_context_menu_entry(
                    full_path,
                    final_command,
                    label,
                    icon_path,
                )

                if success:
                    success_count += 1

            if success_count == total_paths:
                return {
                    "success": True,
                    "info": result_info,
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to add registry entries ({success_count}/{total_paths} succeeded)",
                    "info": result_info,
                    "context_info": context_params.get_description(),
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Registration failed: {str(e)}",
            }

    def _get_context_type_from_path(self, registry_path: str) -> ContextType:
        """
        Determine context type from registry path.

        Args:
            registry_path: Registry path

        Returns:
            ContextType enum value
        """
        if "Directory\\shell" in registry_path and "background" not in registry_path:
            return ContextType.DIRECTORY
        elif "Directory\\background" in registry_path:
            return ContextType.BACKGROUND
        elif "Drive\\shell" in registry_path:
            return ContextType.ROOT
        elif "*\\shell" in registry_path:
            return ContextType.FILE
        else:
            return ContextType.DIRECTORY  # Default fallback

    def unregister_script(self, key_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Unregister a script from the Windows context menu.

        Args:
            key_name: Registry key name to remove
            dry_run: If True, show what would be done without making changes

        Returns:
            Dict containing operation result
        """
        try:
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "key_name": key_name,
                }

            # Try to remove from both context types
            success = False
            for context_type in ["directory", "background"]:
                registry_path = self.registry_utils.get_context_path(context_type)
                if registry_path:
                    full_path = f"{registry_path}\\{key_name}"
                    if self.registry_utils.remove_context_menu_entry(full_path):
                        success = True

            if success:
                return {
                    "success": True,
                    "key_name": key_name,
                }
            else:
                return {
                    "success": False,
                    "error": f"Entry not found: {key_name}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Unregistration failed: {str(e)}",
            }

    def list_entries(self) -> Dict[str, Any]:
        """
        List all registered context menu entries.

        Returns:
            Dict containing all entries organized by context type
        """
        try:
            all_entries = {}

            for context_type in ["directory", "background"]:
                entries = self.registry_utils.list_context_menu_entries(context_type)
                all_entries[context_type] = entries

            return {
                "success": True,
                "entries": all_entries,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list entries: {str(e)}",
            }

    def backup_entries(self, backup_file: str) -> Dict[str, Any]:
        """
        Backup current context menu entries.

        Args:
            backup_file: Path to save the backup file

        Returns:
            Dict containing operation result
        """
        try:
            # Get current entries
            entries_result = self.list_entries()
            if not entries_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to get current entries: {entries_result['error']}",
                }

            entries = entries_result["entries"]

            # Use BackupManager to create backup
            success, filepath, metadata = self.backup_manager.create_backup_file(
                entries, custom_filename=Path(backup_file).stem, add_timestamp=False
            )

            if success:
                return {
                    "success": True,
                    "backup_file": filepath,
                    "entry_count": metadata.get("total_entries", 0),
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create backup: {filepath}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Backup failed: {str(e)}",
            }

    def restore_entries(self, backup_file: str) -> Dict[str, Any]:
        """
        Restore context menu entries from backup.

        Args:
            backup_file: Path to the backup file

        Returns:
            Dict containing operation result
        """
        try:
            # Use BackupManager to load and validate backup
            success, data, error = self.backup_manager.load_backup_file(backup_file)
            if not success:
                return {
                    "success": False,
                    "error": f"Failed to load backup: {error}",
                }

            # Restore entries using RegistryUtils
            success = self.registry_utils.restore_registry_entries(data)

            if success:
                return {
                    "success": True,
                    "backup_file": backup_file,
                    "entry_count": data.get("metadata", {}).get("total_entries", 0),
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to restore registry entries",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Restore failed: {str(e)}",
            }

    def get_script_info(self, script_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a script.

        Args:
            script_path: Path to the script

        Returns:
            Dict containing script information
        """
        try:
            script_info = ScriptDetector.get_script_info(script_path)

            # Add icon information
            icon_path = self.icon_manager.resolve_icon("auto", script_path)
            script_info["resolved_icon"] = icon_path

            # Add registry key name
            registry_key = self.registry_utils.generate_registry_key_name(script_path)
            script_info["registry_key"] = registry_key

            return {
                "success": True,
                "info": script_info,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get script info: {str(e)}",
            }

    def validate_script(self, script_path: str) -> Dict[str, Any]:
        """
        Validate if a script can be registered in context menu.

        Args:
            script_path: Path to the script

        Returns:
            Dict containing validation result
        """
        try:
            # Use ValidationUtils for comprehensive validation
            validation_result = ValidationUtils.validate_script_path(script_path)
            if not validation_result["valid"]:
                return {
                    "valid": False,
                    "error": validation_result["error"],
                    "validation_details": validation_result,
                }

            # Get script info
            script_info = ScriptDetector.get_script_info(script_path)
            script_type = script_info["type"]

            # Check if script type is supported
            if script_type == ScriptType.UNKNOWN:
                return {
                    "valid": False,
                    "error": f"Unsupported script type: {Path(script_path).suffix}",
                    "validation_details": validation_result,
                }

            # Check if command can be built
            command = script_info["command"]
            if not command:
                return {
                    "valid": False,
                    "error": "Could not build execution command",
                    "validation_details": validation_result,
                }

            # Check permissions and compatibility
            permission_check = ValidationUtils.check_permissions()
            compatibility_check = ValidationUtils.validate_windows_compatibility()

            return {
                "valid": True,
                "script_type": script_type,
                "command": command,
                "validation_details": validation_result,
                "permissions": permission_check,
                "compatibility": compatibility_check,
            }

        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation failed: {str(e)}",
            }
