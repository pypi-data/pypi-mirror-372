#!/usr/bin/env python3
"""
Validation utilities for context menu operations.

This module provides comprehensive validation functionality
for Windows context menu operations, including input validation,
data validation, and system compatibility checks.
"""

import os
import re
import winreg
from pathlib import Path
from typing import Dict, Optional


class ValidationUtils:
    """Validation utilities for context menu operations."""

    # Valid registry key name pattern
    REGISTRY_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")

    # Valid file extensions for scripts
    VALID_SCRIPT_EXTENSIONS = {".py", ".ps1", ".bat", ".cmd", ".exe", ".msi"}

    # Maximum lengths
    MAX_LABEL_LENGTH = 256
    MAX_REGISTRY_KEY_LENGTH = 255
    MAX_PATH_LENGTH = 260

    @staticmethod
    def validate_script_path(script_path: str) -> Dict:
        """
        Validate a script path for context menu registration.

        Args:
            script_path: Path to the script to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check if path is provided
            if not script_path or not script_path.strip():
                return {"valid": False, "error": "Script path is required"}

            # Convert to Path object and resolve relative paths
            path = Path(script_path.strip()).resolve()

            # Check if file exists
            if not path.exists():
                return {
                    "valid": False,
                    "error": f"Script file not found: {script_path}",
                }

            # Check if it's a file (not directory)
            if not path.is_file():
                return {"valid": False, "error": f"Path is not a file: {script_path}"}

            # Check file extension
            extension = path.suffix.lower()
            if extension not in ValidationUtils.VALID_SCRIPT_EXTENSIONS:
                return {
                    "valid": False,
                    "error": f"Unsupported file extension: {extension}. Supported: {', '.join(ValidationUtils.VALID_SCRIPT_EXTENSIONS)}",
                }

            # Check file size (prevent empty files)
            try:
                if path.stat().st_size == 0:
                    return {"valid": False, "error": "Script file is empty"}
            except OSError:
                return {"valid": False, "error": "Cannot access script file"}

            # Check if file is readable
            try:
                with open(path, encoding="utf-8", errors="ignore") as f:
                    f.read(1)  # Try to read at least one character
            except (UnicodeDecodeError, PermissionError):
                # For binary files like .exe, this is expected
                if extension not in {".exe", ".msi"}:
                    return {
                        "valid": False,
                        "error": "Script file is not readable or contains invalid characters",
                    }

            # Check path length
            if len(str(path)) > ValidationUtils.MAX_PATH_LENGTH:
                return {
                    "valid": False,
                    "error": f"Script path is too long (max {ValidationUtils.MAX_PATH_LENGTH} characters)",
                }

            return {
                "valid": True,
                "script_path": str(path.absolute()),
                "extension": extension,
                "file_size": path.stat().st_size,
            }

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    @staticmethod
    def validate_label(label: str) -> Dict:
        """
        Validate a context menu label.

        Args:
            label: Label to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check if label is provided
            if not label or not label.strip():
                return {"valid": False, "error": "Label is required"}

            label = label.strip()

            # Check length
            if len(label) > ValidationUtils.MAX_LABEL_LENGTH:
                return {
                    "valid": False,
                    "error": f"Label is too long (max {ValidationUtils.MAX_LABEL_LENGTH} characters)",
                }

            # Check for invalid characters
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
            found_invalid = [char for char in invalid_chars if char in label]
            if found_invalid:
                return {
                    "valid": False,
                    "error": f"Label contains invalid characters: {', '.join(found_invalid)}",
                }

            # Check for control characters
            if any(ord(char) < 32 for char in label):
                return {"valid": False, "error": "Label contains control characters"}

            return {"valid": True, "label": label, "length": len(label)}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    @staticmethod
    def validate_registry_key(key_name: str) -> Dict:
        """
        Validate a registry key name.

        Args:
            key_name: Registry key name to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check if key name is provided
            if not key_name or not key_name.strip():
                return {"valid": False, "error": "Registry key name is required"}

            key_name = key_name.strip()

            # Check length
            if len(key_name) > ValidationUtils.MAX_REGISTRY_KEY_LENGTH:
                return {
                    "valid": False,
                    "error": f"Registry key name is too long (max {ValidationUtils.MAX_REGISTRY_KEY_LENGTH} characters)",
                }

            # Check pattern
            if not ValidationUtils.REGISTRY_KEY_PATTERN.match(key_name):
                return {
                    "valid": False,
                    "error": "Registry key name contains invalid characters. Use only letters, numbers, hyphens, underscores, and dots",
                }

            # Check for reserved names
            reserved_names = {
                "con",
                "prn",
                "aux",
                "nul",
                "com1",
                "com2",
                "com3",
                "com4",
                "com5",
                "com6",
                "com7",
                "com8",
                "com9",
                "lpt1",
                "lpt2",
                "lpt3",
                "lpt4",
                "lpt5",
                "lpt6",
                "lpt7",
                "lpt8",
                "lpt9",
            }
            if key_name.lower() in reserved_names:
                return {
                    "valid": False,
                    "error": f"Registry key name '{key_name}' is reserved by Windows",
                }

            return {"valid": True, "key_name": key_name, "length": len(key_name)}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    @staticmethod
    def validate_icon_path(icon_path: str) -> Dict:
        """
        Validate an icon path.

        Args:
            icon_path: Icon path to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check if icon path is provided
            if not icon_path or not icon_path.strip():
                return {"valid": False, "error": "Icon path is required"}

            icon_path = icon_path.strip()

            # Handle special values
            if icon_path.lower() in {"auto", "default", "none"}:
                return {
                    "valid": True,
                    "icon_path": icon_path.lower(),
                    "type": "special",
                }

            # Convert to Path object
            path = Path(icon_path)

            # Check if file exists
            if not path.exists():
                return {"valid": False, "error": f"Icon file not found: {icon_path}"}

            # Check if it's a file
            if not path.is_file():
                return {"valid": False, "error": f"Path is not a file: {icon_path}"}

            # Check file extension
            extension = path.suffix.lower()
            valid_icon_extensions = {
                ".ico",
                ".exe",
                ".dll",
                ".png",
                ".jpg",
                ".jpeg",
                ".bmp",
            }
            if extension not in valid_icon_extensions:
                return {
                    "valid": False,
                    "error": f"Unsupported icon format: {extension}. Supported: {', '.join(valid_icon_extensions)}",
                }

            # Check file size
            try:
                file_size = path.stat().st_size
                if file_size == 0:
                    return {"valid": False, "error": "Icon file is empty"}
                if file_size > 10 * 1024 * 1024:  # 10MB limit
                    return {
                        "valid": False,
                        "error": "Icon file is too large (max 10MB)",
                    }
            except OSError:
                return {"valid": False, "error": "Cannot access icon file"}

            return {
                "valid": True,
                "icon_path": str(path.absolute()),
                "extension": extension,
                "file_size": file_size,
            }

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    @staticmethod
    def validate_backup_data(data: Dict) -> Dict:
        """
        Validate backup data structure.

        Args:
            data: Backup data to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check if data is provided
            if not data or not isinstance(data, dict):
                return {"valid": False, "error": "Backup data must be a dictionary"}

            # Check required top-level keys
            required_keys = ["metadata", "entries"]
            for key in required_keys:
                if key not in data:
                    return {"valid": False, "error": f"Missing required key: {key}"}

            # Validate metadata
            metadata = data["metadata"]
            if not isinstance(metadata, dict):
                return {"valid": False, "error": "Metadata must be a dictionary"}

            required_metadata = ["version", "timestamp", "total_entries"]
            for key in required_metadata:
                if key not in metadata:
                    return {"valid": False, "error": f"Missing metadata key: {key}"}

            # Validate entries structure
            entries = data["entries"]
            if not isinstance(entries, dict):
                return {"valid": False, "error": "Entries must be a dictionary"}

            # Check for expected context types
            expected_types = ["directory", "background"]
            for context_type in expected_types:
                if context_type not in entries:
                    return {
                        "valid": False,
                        "error": f"Missing context type: {context_type}",
                    }

            # Validate individual entries
            for context_type, context_entries in entries.items():
                if not isinstance(context_entries, list):
                    return {
                        "valid": False,
                        "error": f"Context entries must be a list: {context_type}",
                    }

                for entry in context_entries:
                    if not isinstance(entry, dict):
                        return {
                            "valid": False,
                            "error": f"Entry must be a dictionary in {context_type}",
                        }

                    # Check required entry fields
                    required_entry_fields = ["key_name", "display_name"]
                    for field in required_entry_fields:
                        if field not in entry:
                            return {
                                "valid": False,
                                "error": f"Missing entry field: {field}",
                            }

            return {
                "valid": True,
                "entry_count": metadata.get("total_entries", 0),
                "context_types": list(entries.keys()),
            }

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    @staticmethod
    def check_permissions() -> Dict:
        """
        Check if the current user has sufficient permissions for registry operations.

        Returns:
            Permission check result dictionary
        """
        try:
            # Check if running on Windows
            if os.name != "nt":
                return {
                    "has_permissions": False,
                    "error": "Registry operations are only supported on Windows",
                }

            # Try to access registry for writing
            test_key = "Software\\Classes\\Directory\\shell\\WOMM_TEST_PERMISSIONS"

            try:
                # Try to create a test key
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, test_key)
                winreg.CloseKey(key)

                return {
                    "has_permissions": True,
                    "level": "user",
                    "message": "User has sufficient permissions for registry operations",
                }

            except PermissionError:
                return {
                    "has_permissions": False,
                    "error": "Insufficient permissions. Try running as administrator",
                    "level": "admin_required",
                }

            except Exception as e:
                return {
                    "has_permissions": False,
                    "error": f"Permission check failed: {str(e)}",
                }

        except Exception as e:
            return {
                "has_permissions": False,
                "error": f"Permission check error: {str(e)}",
            }

    @staticmethod
    def validate_windows_compatibility() -> Dict:
        """
        Check Windows compatibility for context menu operations.

        Returns:
            Compatibility check result dictionary
        """
        try:
            # Check OS
            if os.name != "nt":
                return {
                    "compatible": False,
                    "error": "Context menu operations are only supported on Windows",
                }

            # Check Windows version
            import platform

            windows_version = platform.version()

            # Windows 7 and later are supported
            if int(windows_version.split(".")[0]) < 6:
                return {"compatible": False, "error": "Windows 7 or later is required"}

            # Check if registry is accessible
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, "Software\\Classes", 0, winreg.KEY_READ
                )
                winreg.CloseKey(key)
            except Exception as e:
                return {
                    "compatible": False,
                    "error": f"Cannot access Windows Registry: {str(e)}",
                }

            return {
                "compatible": True,
                "windows_version": windows_version,
                "message": "System is compatible with context menu operations",
            }

        except Exception as e:
            return {
                "compatible": False,
                "error": f"Compatibility check error: {str(e)}",
            }

    @staticmethod
    def validate_command_parameters(
        script_path: str, label: str, icon: Optional[str] = None
    ) -> Dict:
        """
        Validate all parameters for context menu registration.

        Args:
            script_path: Path to the script
            label: Display label
            icon: Icon path (optional)

        Returns:
            Comprehensive validation result
        """
        try:
            results = {"valid": True, "errors": [], "warnings": [], "details": {}}

            # Validate script path
            script_validation = ValidationUtils.validate_script_path(script_path)
            results["details"]["script"] = script_validation
            if not script_validation["valid"]:
                results["valid"] = False
                results["errors"].append(script_validation["error"])

            # Validate label
            label_validation = ValidationUtils.validate_label(label)
            results["details"]["label"] = label_validation
            if not label_validation["valid"]:
                results["valid"] = False
                results["errors"].append(label_validation["error"])

            # Validate icon if provided
            if icon:
                icon_validation = ValidationUtils.validate_icon_path(icon)
                results["details"]["icon"] = icon_validation
                if not icon_validation["valid"]:
                    results["warnings"].append(
                        f"Icon validation: {icon_validation['error']}"
                    )

            # Check permissions
            permission_check = ValidationUtils.check_permissions()
            results["details"]["permissions"] = permission_check
            if not permission_check["has_permissions"]:
                results["valid"] = False
                results["errors"].append(permission_check["error"])

            # Check compatibility
            compatibility_check = ValidationUtils.validate_windows_compatibility()
            results["details"]["compatibility"] = compatibility_check
            if not compatibility_check["compatible"]:
                results["valid"] = False
                results["errors"].append(compatibility_check["error"])

            return results

        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "details": {},
            }

    @staticmethod
    def sanitize_registry_key(key_name: str) -> str:
        """
        Sanitize a registry key name to make it valid.

        Args:
            key_name: Original key name

        Returns:
            Sanitized key name
        """
        try:
            # Remove invalid characters
            sanitized = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", key_name)

            # Remove leading/trailing invalid characters
            sanitized = sanitized.strip("_")

            # Ensure it's not empty
            if not sanitized:
                sanitized = "womm_entry"

            # Limit length
            if len(sanitized) > ValidationUtils.MAX_REGISTRY_KEY_LENGTH:
                sanitized = sanitized[: ValidationUtils.MAX_REGISTRY_KEY_LENGTH]

            return sanitized

        except Exception:
            return "womm_entry"

    @staticmethod
    def sanitize_label(label: str) -> str:
        """
        Sanitize a context menu label to make it valid.

        Args:
            label: Original label

        Returns:
            Sanitized label
        """
        try:
            # Remove invalid characters
            invalid_chars = ["<", ">", ":", '"', "|", "?", "*", "\\", "/"]
            sanitized = label
            for char in invalid_chars:
                sanitized = sanitized.replace(char, " ")

            # Remove control characters
            sanitized = "".join(char for char in sanitized if ord(char) >= 32)

            # Remove extra whitespace
            sanitized = " ".join(sanitized.split())

            # Limit length
            if len(sanitized) > ValidationUtils.MAX_LABEL_LENGTH:
                sanitized = sanitized[: ValidationUtils.MAX_LABEL_LENGTH]

            return sanitized

        except Exception:
            return "WOMM Entry"
