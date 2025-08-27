#!/usr/bin/env python3
"""
Icon management for context menu entries.

This module provides icon detection, validation, and management for
context menu entries with automatic icon selection based on file extensions.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class IconManager:
    """Manage icons for context menu entries."""

    # Extension to icon mapping
    EXTENSION_ICONS = {
        # Scripts
        ".py": "python.exe,0",
        ".ps1": "powershell.exe,0",
        ".bat": "cmd.exe,0",
        ".cmd": "cmd.exe,0",
        ".js": "node.exe,0",
        ".ts": "node.exe,0",
        # Documents
        ".txt": "notepad.exe,0",
        ".md": "notepad.exe,0",
        ".doc": "wordpad.exe,0",
        ".docx": "wordpad.exe,0",
        ".pdf": "AcroRd32.exe,0",
        # Images
        ".jpg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".jpeg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".png": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".gif": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".bmp": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".ico": "rundll32.exe,shell32.dll,ShellImagePreview",
        # Archives
        ".zip": "zipfldr.dll,0",
        ".rar": "WinRAR.exe,0",
        ".7z": "7zFM.exe,0",
        ".tar": "zipfldr.dll,0",
        ".gz": "zipfldr.dll,0",
        # Code
        ".html": "mshtml.dll,0",
        ".htm": "mshtml.dll,0",
        ".css": "mshtml.dll,0",
        ".xml": "mshtml.dll,0",
        ".json": "notepad.exe,0",
        # Executables
        ".exe": None,  # Use file's own icon
        ".msi": None,  # Use file's own icon
    }

    # System icon shortcuts
    SYSTEM_ICONS = {
        "auto": None,  # Auto-detect
        "python": "python.exe,0",
        "powershell": "powershell.exe,0",
        "cmd": "cmd.exe,0",
        "node": "node.exe,0",
        "notepad": "notepad.exe,0",
        "explorer": "explorer.exe,0",
        "folder": "shell32.dll,4",
        "file": "shell32.dll,1",
        "gear": "shell32.dll,14",
        "settings": "shell32.dll,21",
    }

    # Common system paths for icons
    SYSTEM_PATHS = [
        "C:\\Windows\\System32",
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
    ]

    @classmethod
    def get_icon_for_extension(cls, extension: str) -> Optional[str]:
        """Get default icon for file extension."""
        return cls.EXTENSION_ICONS.get(extension.lower())

    @classmethod
    def get_system_icon(cls, icon_name: str) -> Optional[str]:
        """Get system icon by name."""
        return cls.SYSTEM_ICONS.get(icon_name.lower())

    @classmethod
    def validate_icon_path(cls, icon_path: str) -> bool:
        """Validate if icon path exists and is accessible."""
        if not icon_path:
            return False

        # Handle icon with index (e.g., "file.exe,0")
        file_path = icon_path.split(",")[0] if "," in icon_path else icon_path

        # Check if it's a system icon
        if file_path in cls.SYSTEM_ICONS:
            return True

        # Check if file exists
        if os.path.exists(file_path):
            return True

        # Try to find in system paths
        for system_path in cls.SYSTEM_PATHS:
            full_path = os.path.join(system_path, file_path)
            if os.path.exists(full_path):
                return True

        return False

    @classmethod
    def resolve_icon(cls, icon_input: str, file_path: str = None) -> Optional[str]:
        """Resolve icon from various input formats."""
        if not icon_input or icon_input.lower() == "auto":
            # Auto-detect based on file extension
            if file_path:
                extension = Path(file_path).suffix.lower()
                return cls.get_icon_for_extension(extension)
            return None

        # Check if it's a system icon name
        system_icon = cls.get_system_icon(icon_input)
        if system_icon:
            return system_icon

        # Check if it's a valid path
        if cls.validate_icon_path(icon_input):
            return icon_input

        # Try to find in system paths
        for system_path in cls.SYSTEM_PATHS:
            full_path = os.path.join(system_path, icon_input)
            if os.path.exists(full_path):
                return full_path

        return None

    @classmethod
    def find_icon_in_path(cls, icon_name: str) -> Optional[str]:
        """Find icon file in system PATH."""
        return shutil.which(icon_name)

    @classmethod
    def get_available_icons(cls) -> Dict[str, str]:
        """Get list of available system icons."""
        return cls.SYSTEM_ICONS.copy()

    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions."""
        return list(cls.EXTENSION_ICONS.keys())
