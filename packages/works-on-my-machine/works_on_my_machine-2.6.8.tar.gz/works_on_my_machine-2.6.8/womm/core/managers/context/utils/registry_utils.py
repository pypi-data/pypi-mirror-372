#!/usr/bin/env python3
"""
Registry utilities for Windows context menu management.

This module provides low-level registry operations for managing
Windows context menu entries.
"""

import winreg
from pathlib import Path
from typing import Dict, List, Optional


class RegistryUtils:
    """Windows Registry utilities for context menu management."""

    # Registry paths for context menus
    CONTEXT_PATHS = {
        "directory": "Software\\Classes\\Directory\\shell",
        "background": "Software\\Classes\\Directory\\background\\shell",
        "file": "Software\\Classes\\*\\shell",
        "image": "Software\\Classes\\SystemFileAssociations\\image\\shell",
        "text": "Software\\Classes\\SystemFileAssociations\\text\\shell",
        "archive": "Software\\Classes\\SystemFileAssociations\\compressed\\shell",
    }

    @classmethod
    def generate_registry_key_name(cls, file_path: str) -> str:
        """Generate registry key name from file path."""
        # Extract filename and extension
        path_obj = Path(file_path)
        filename = path_obj.stem
        extension = path_obj.suffix.lower()

        # Normalize filename: replace spaces and special chars with underscores
        normalized_name = "".join(c if c.isalnum() else "_" for c in filename)
        # Remove consecutive underscores and leading/trailing underscores
        normalized_name = "_".join(part for part in normalized_name.split("_") if part)
        # Convert to lowercase for consistency
        normalized_name = normalized_name.lower()

        # Get extension without dot and normalize
        ext_clean = extension.replace(".", "").lower()

        # Format: womm_{extension}_{filename}
        return f"womm_{ext_clean}_{normalized_name}"

    @classmethod
    def add_context_menu_entry(
        cls,
        registry_path: str,
        command: str,
        mui_verb: str,
        icon_path: Optional[str] = None,
    ) -> bool:
        """Add context menu entry to registry."""
        try:
            # Create the registry key
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                # Set the display name
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, mui_verb)

                # Set the command
                with winreg.CreateKey(key, "command") as cmd_key:
                    winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

                # Set icon if provided
                if icon_path:
                    winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)

            return True

        except Exception as e:
            print(f"Error adding registry entry: {e}")
            return False

    @classmethod
    def remove_context_menu_entry(cls, registry_path: str) -> bool:
        """Remove context menu entry from registry."""
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
            return True
        except Exception as e:
            print(f"Error removing registry entry: {e}")
            return False

    @classmethod
    def list_context_menu_entries(cls, context_type: str = "directory") -> List[Dict]:
        """List context menu entries for given type."""
        entries = []
        registry_path = cls.CONTEXT_PATHS.get(context_type)

        if not registry_path:
            return entries

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        entry_info = cls._get_entry_info(registry_path, subkey_name)
                        if entry_info:
                            entries.append(entry_info)
                        i += 1
                    except OSError:
                        break

        except Exception as e:
            print(f"Error listing registry entries: {e}")

        return entries

    @classmethod
    def _get_entry_info(cls, base_path: str, key_name: str) -> Optional[Dict]:
        """Get information about a specific registry entry."""
        try:
            full_path = f"{base_path}\\{key_name}"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, full_path) as key:
                info = {"key_name": key_name, "registry_path": full_path}

                # Get MUIVerb (display name)
                try:
                    mui_verb, _ = winreg.QueryValueEx(key, "MUIVerb")
                    info["display_name"] = mui_verb
                except OSError:
                    info["display_name"] = key_name

                # Get icon
                try:
                    icon, _ = winreg.QueryValueEx(key, "Icon")
                    info["icon"] = icon
                except OSError:
                    info["icon"] = None

                # Get command
                try:
                    with winreg.OpenKey(key, "command") as cmd_key:
                        command, _ = winreg.QueryValueEx(cmd_key, "")
                        info["command"] = command
                except OSError:
                    info["command"] = None

                return info

        except Exception:
            return None

    @classmethod
    def backup_registry_entries(cls, context_types: List[str] = None) -> Dict:
        """Backup context menu entries to dictionary."""
        if context_types is None:
            context_types = ["directory", "background"]

        backup_data = {
            "timestamp": None,
            "context_types": {},
        }

        for context_type in context_types:
            entries = cls.list_context_menu_entries(context_type)
            backup_data["context_types"][context_type] = entries

        return backup_data

    @classmethod
    def restore_registry_entries(cls, backup_data: Dict) -> bool:
        """Restore context menu entries from backup data."""
        try:
            for _context_type, entries in backup_data.get("context_types", {}).items():
                for entry in entries:
                    registry_path = entry.get("registry_path")
                    command = entry.get("command")
                    display_name = entry.get("display_name")
                    icon = entry.get("icon")

                    if registry_path and command and display_name:
                        cls.add_context_menu_entry(
                            registry_path, command, display_name, icon
                        )

            return True

        except Exception as e:
            print(f"Error restoring registry entries: {e}")
            return False

    @classmethod
    def get_context_path(cls, context_type: str) -> Optional[str]:
        """Get registry path for context type."""
        return cls.CONTEXT_PATHS.get(context_type)

    @classmethod
    def get_supported_context_types(cls) -> List[str]:
        """Get list of supported context types."""
        return list(cls.CONTEXT_PATHS.keys())
