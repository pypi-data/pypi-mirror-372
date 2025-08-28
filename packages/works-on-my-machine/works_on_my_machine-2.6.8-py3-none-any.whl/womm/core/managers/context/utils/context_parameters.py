#!/usr/bin/env python3
"""
Context parameters management for intelligent context menu registration.

This module provides functionality to handle intelligent context parameters
like --root, --file, --files, --background and automatically generate
appropriate command parameters and registry paths.
"""

from enum import Enum
from typing import Dict, List, Optional, Set


class ContextType(Enum):
    """Types of context menu entries."""

    DIRECTORY = "directory"
    BACKGROUND = "background"
    FILE = "file"
    FILES = "files"
    ROOT = "root"


class ContextParameters:
    """Manages intelligent context parameters for context menu registration."""

    # Registry paths for different context types
    REGISTRY_PATHS = {
        ContextType.DIRECTORY: "Software\\Classes\\Directory\\shell",
        ContextType.BACKGROUND: "Software\\Classes\\Directory\\background\\shell",
        ContextType.FILE: "Software\\Classes\\*\\shell",
        ContextType.FILES: "Software\\Classes\\*\\shell",
        ContextType.ROOT: "Software\\Classes\\Drive\\shell",
    }

    # Command parameters for different context types
    COMMAND_PARAMETERS = {
        ContextType.DIRECTORY: "%V",  # Selected folder
        ContextType.BACKGROUND: "%V",  # Background context
        ContextType.FILE: "%1",  # Single selected file
        ContextType.FILES: "%V",  # Multiple selected files
        ContextType.ROOT: "%V",  # Root directory (drive)
    }

    # File type extensions for different contexts
    FILE_TYPE_EXTENSIONS = {
        "image": {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".svg",
            ".ico",
        },
        "text": {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".csv",
            ".log",
        },
        "archive": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".cab"},
        "document": {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".odt",
            ".ods",
            ".odp",
        },
        "media": {
            ".mp3",
            ".mp4",
            ".avi",
            ".mkv",
            ".wav",
            ".flac",
            ".mov",
            ".wmv",
            ".flv",
        },
        "code": {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
        },
    }

    def __init__(self):
        """Initialize the context parameters manager."""
        self.context_types: Set[ContextType] = set()
        self.file_types: Set[str] = set()
        self.custom_extensions: Set[str] = set()

    def add_context_type(self, context_type: ContextType) -> None:
        """
        Add a context type to the parameters.

        Args:
            context_type: The context type to add
        """
        self.context_types.add(context_type)

    def add_file_type(self, file_type: str) -> None:
        """
        Add a file type to the parameters.

        Args:
            file_type: The file type to add (e.g., 'image', 'text', 'archive')
        """
        if file_type in self.FILE_TYPE_EXTENSIONS:
            self.file_types.add(file_type)
        else:
            # Treat as custom extension
            if file_type.startswith("."):
                self.custom_extensions.add(file_type.lower())
            else:
                self.custom_extensions.add(f".{file_type.lower()}")

    def get_registry_paths(self) -> List[str]:
        """
        Get registry paths for all configured context types.

        Returns:
            List of registry paths
        """
        paths = []
        for context_type in self.context_types:
            if context_type in self.REGISTRY_PATHS:
                paths.append(self.REGISTRY_PATHS[context_type])
        return paths

    def get_command_parameter(self, context_type: ContextType) -> str:
        """
        Get the appropriate command parameter for a context type.

        Args:
            context_type: The context type

        Returns:
            Command parameter string
        """
        return self.COMMAND_PARAMETERS.get(context_type, "%V")

    def get_file_extensions(self) -> Set[str]:
        """
        Get all file extensions for configured file types.

        Returns:
            Set of file extensions
        """
        extensions = set()

        # Add extensions from file types
        for file_type in self.file_types:
            if file_type in self.FILE_TYPE_EXTENSIONS:
                extensions.update(self.FILE_TYPE_EXTENSIONS[file_type])

        # Add custom extensions
        extensions.update(self.custom_extensions)

        return extensions

    def build_command(self, base_command: str, context_type: ContextType) -> str:
        """
        Build the final command with appropriate parameters.

        Args:
            base_command: Base command without parameters
            context_type: Context type for parameter selection

        Returns:
            Complete command with parameters
        """
        parameter = self.get_command_parameter(context_type)

        # Check if command already has a parameter at the end (various formats)
        if base_command.endswith('"%V"'):
            # Replace "%V" with new parameter
            return base_command[:-4] + f'"{parameter}"'
        elif base_command.endswith('%V"'):
            # Replace %V" with new parameter
            return base_command[:-3] + f'{parameter}"'
        elif base_command.endswith("%V"):
            # Replace %V with new parameter
            return base_command[:-2] + parameter
        elif base_command.endswith('"'):
            # Command already has quotes, add parameter outside
            return f"{base_command} {parameter}"
        else:
            # Add quotes and parameter
            return f'"{base_command}" {parameter}'

    def validate_parameters(self) -> Dict:
        """
        Validate the current parameter configuration.

        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []

        # Check if context types are specified
        if not self.context_types:
            errors.append("No context types specified")

        # Check for conflicting context types
        if (
            ContextType.FILE in self.context_types
            and ContextType.FILES in self.context_types
        ):
            warnings.append(
                "Both --file and --files specified, --files will take precedence"
            )

        # Check file types
        if self.file_types:
            invalid_types = self.file_types - set(self.FILE_TYPE_EXTENSIONS.keys())
            if invalid_types:
                warnings.append(f"Unknown file types: {', '.join(invalid_types)}")

        # Check custom extensions
        for ext in self.custom_extensions:
            if not ext.startswith("."):
                errors.append(f"Custom extension must start with '.': {ext}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "context_types": [ct.value for ct in self.context_types],
            "file_types": list(self.file_types),
            "custom_extensions": list(self.custom_extensions),
        }

    def get_description(self) -> str:
        """
        Get a human-readable description of the current configuration.

        Returns:
            Description string
        """
        parts = []

        # Context types
        if self.context_types:
            context_names = [ct.value for ct in self.context_types]
            parts.append(f"Context: {', '.join(context_names)}")

        # File types
        if self.file_types:
            parts.append(f"File types: {', '.join(self.file_types)}")

        # Custom extensions
        if self.custom_extensions:
            parts.append(f"Extensions: {', '.join(sorted(self.custom_extensions))}")

        return (
            " | ".join(parts) if parts else "Default context (directory + background)"
        )

    @classmethod
    def from_flags(
        cls,
        root: bool = False,
        file: bool = False,
        files: bool = False,
        background: bool = False,
        file_types: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
    ) -> "ContextParameters":
        """
        Create ContextParameters from command line flags.

        Args:
            root: --root flag
            file: --file flag
            files: --files flag
            background: --background flag
            file_types: List of file types
            extensions: List of custom extensions

        Returns:
            Configured ContextParameters instance
        """
        params = cls()

        # Add context types based on flags
        if root:
            params.add_context_type(ContextType.ROOT)
        if file:
            params.add_context_type(ContextType.FILE)
        if files:
            params.add_context_type(ContextType.FILES)
        if background:
            params.add_context_type(ContextType.BACKGROUND)

        # If no specific context types specified, use defaults
        if not any([root, file, files, background]):
            params.add_context_type(ContextType.DIRECTORY)
            params.add_context_type(ContextType.BACKGROUND)

        # Add file types
        if file_types:
            for file_type in file_types:
                params.add_file_type(file_type)

        # Add custom extensions
        if extensions:
            for ext in extensions:
                params.add_file_type(ext)

        return params

    @classmethod
    def get_available_file_types(cls) -> Dict[str, Set[str]]:
        """
        Get all available file types and their extensions.

        Returns:
            Dictionary of file types and their extensions
        """
        return cls.FILE_TYPE_EXTENSIONS.copy()

    @classmethod
    def get_context_type_help(cls) -> str:
        """
        Get help text for context types.

        Returns:
            Help text string
        """
        help_text = "Available context types:\n"
        help_text += "• --root: Root directories (drives)\n"
        help_text += "• --file: Single file selection\n"
        help_text += "• --files: Multiple file selection\n"
        help_text += "• --background: Background context (empty space)\n"
        help_text += "• Default: Both directory and background contexts\n"
        return help_text

    @classmethod
    def get_file_type_help(cls) -> str:
        """
        Get help text for file types.

        Returns:
            Help text string
        """
        help_text = "Available file types:\n"
        for file_type, extensions in cls.FILE_TYPE_EXTENSIONS.items():
            ext_list = ", ".join(sorted(extensions))
            help_text += f"• {file_type}: {ext_list}\n"
        help_text += "• Custom extensions: Use --extensions .ext1 .ext2\n"
        return help_text
