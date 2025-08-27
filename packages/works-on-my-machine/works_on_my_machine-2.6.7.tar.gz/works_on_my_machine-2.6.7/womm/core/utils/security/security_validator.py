#!/usr/bin/env python3
"""
Security validation module for Works On My Machine CLI.

This module provides comprehensive validation for all user inputs and system
operations. It follows the Utils pattern by providing ONLY validation functions
without any execution logic.

Key features:
- Project name validation
- Path and file validation
- Command and argument validation
- Registry operation validation (Windows)
- File operation validation

Architecture compliance:
- Pure validation functions (no execution)
- No UI imports (tools layer)
- No manager dependencies
- Stateless operations where possible
"""

import os
import platform
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Union


class SecurityValidator:
    """Security validation for CLI operations."""

    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        r"[;&|`$(){}\[\]]",  # Shell command characters
        r"\.\./",  # Path traversal
        r"\.\.\\",  # Path traversal Windows
        r"[<>]",  # Redirection
        r"\\x[0-9a-fA-F]{2}",  # Encoded characters
        r"%[0-9a-fA-F]{2}",  # URL encoding
    ]

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        ".py",
        ".pyw",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".bat",
        ".cmd",
        ".ps1",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
    }

    # Allowed commands
    ALLOWED_COMMANDS = {
        "python",
        "python3",
        "py",
        "python.exe",
        "python3.exe",
        "py.exe",
        "node",
        "npm",
        "npx",
        "git",
        "pip",
        "pip3",
        "black",
        "isort",
        "flake8",
        "ruff",
        "pytest",
        "pre-commit",
        "cspell",
        "eslint",
        "prettier",
        "jest",
        "husky",
        "lint-staged",
        # Development tools
        "code",
        # Windows system commands for installation
        "reg",
        "setx",
        "powershell",
        "cmd",
        "msiexec",
        # Package managers
        "choco",
        "winget",
        "scoop",
        "brew",
        "apt",
        "yum",
        "dnf",
        "pacman",
        "snap",
    }

    def __init__(self):
        """Initialize security validator."""
        self.system = platform.system()
        self.max_path_length = 260 if self.system == "Windows" else 4096

    def validate_project_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate project name for security.

        Args:
            name: Project name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name:
            return False, "Project name cannot be empty"

        if len(name) > 50:
            return False, "Project name too long (max 50 characters)"

        # Check for dangerous characters
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, name):
                return False, f"Project name contains dangerous characters: {pattern}"

        # Check allowed characters
        if not re.match(r"^[a-zA-Z0-9_-]+$", name):
            return (
                False,
                "Project name can only contain letters, numbers, underscores, and hyphens",
            )

        # Check reserved names
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
        if name.lower() in reserved_names:
            return False, f"Project name '{name}' is reserved by the system"

        return True, ""

    def validate_path(
        self, path: Union[str, Path], must_exist: bool = False
    ) -> Tuple[bool, str]:
        """
        Validate file or directory path.

        Args:
            path: Path to validate
            must_exist: Whether the path must exist

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path_obj = Path(path).resolve()
        except (OSError, RuntimeError) as e:
            return False, f"Invalid path: {e}"

        # Check length
        if len(str(path_obj)) > self.max_path_length:
            return False, f"Path too long (max {self.max_path_length} characters)"

        # Check for dangerous characters
        path_str = str(path_obj)
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, path_str):
                return False, f"Path contains dangerous characters: {pattern}"

        # Check existence if required
        if must_exist and not path_obj.exists():
            return False, f"Path does not exist: {path_obj}"

        return True, ""

    def validate_command(self, command: Union[str, List[str]]) -> Tuple[bool, str]:
        """
        Validate command for security.

        Args:
            command: Command to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        cmd_parts = command.split() if isinstance(command, str) else list(command)

        if not cmd_parts:
            return False, "Empty command"

        # Check main command
        main_cmd = cmd_parts[0].lower()
        # Extract command name without path
        cmd_name = Path(main_cmd).name.lower()
        if cmd_name not in self.ALLOWED_COMMANDS:
            return False, f"Command '{cmd_name}' is not allowed"

        # Check arguments with context-aware validation
        for _i, arg in enumerate(cmd_parts[1:], 1):
            if not self._validate_argument_with_context(arg, cmd_name, cmd_parts):
                return False, f"Invalid argument: {arg}"

        return True, ""

    def _validate_argument(self, arg: str) -> bool:
        """Validate command argument."""
        # Check for dangerous characters
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, arg):
                return False

        # Check length
        return not len(arg) > 1000

    def _validate_argument_with_context(
        self, arg: str, command: str, full_command: List[str]
    ) -> bool:
        """Validate command argument with command context."""
        # Special handling for PATH-related commands
        if command.lower() in ["reg", "setx"]:
            # Check if this is a PATH operation
            is_path_operation = False
            if (
                command.lower() == "reg"
                and len(full_command) > 3
                and "HKCU\\Environment" in full_command
                and "/v" in full_command
                and "PATH" in full_command
            ):
                # reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d <value> /f
                is_path_operation = True
            elif command.lower() == "setx" and len(full_command) > 2:
                # setx PATH <value>
                is_path_operation = "PATH" in full_command

            if is_path_operation:
                # Allow semicolons in PATH values for Windows
                # Remove semicolons from dangerous patterns check for this case
                dangerous_patterns = [
                    p for p in self.DANGEROUS_PATTERNS if ";" not in p
                ]
                for pattern in dangerous_patterns:
                    if re.search(pattern, arg):
                        return False
                return not len(arg) > 1000

        # Default validation
        return self._validate_argument(arg)

    def validate_file_operation(
        self, source: Path, destination: Path, operation: str
    ) -> Tuple[bool, str]:
        """
        Validate file operation (copy, move, etc.).

        Args:
            source: Source path
            destination: Destination path
            operation: Operation type ('copy', 'move', 'delete')

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Valider les chemins
        for path, name in [(source, "source"), (destination, "destination")]:
            is_valid, error = self.validate_path(path, must_exist=(name == "source"))
            if not is_valid:
                return False, f"Invalid {name} path: {error}"

        # Check permissions
        if operation in ["copy", "move"]:
            if not os.access(source, os.R_OK):
                return False, f"Cannot read source: {source}"

            dest_parent = destination.parent
            if not os.access(dest_parent, os.W_OK):
                return False, f"Cannot write to destination directory: {dest_parent}"

        # Check disk space for copies
        if operation == "copy" and source.is_file():
            try:
                free_space = shutil.disk_usage(destination.parent).free
                file_size = source.stat().st_size
                if file_size > free_space:
                    return False, "Insufficient disk space for copy operation"
            except OSError:
                pass  # Ignore stat errors

        return True, ""

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe use.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remove leading/trailing spaces
        sanitized = sanitized.strip()

        # Limiter la longueur
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[: 255 - len(ext)] + ext

        return sanitized

    def validate_script_execution(self, script_path: Path) -> Tuple[bool, str]:
        """
        Validate script for execution.

        Args:
            script_path: Path to script

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check that file exists
        if not script_path.exists():
            return False, f"Script does not exist: {script_path}"

        # Check that it's a file
        if not script_path.is_file():
            return False, f"Path is not a file: {script_path}"

        # Check extension
        if script_path.suffix not in self.ALLOWED_EXTENSIONS:
            return False, f"File extension not allowed: {script_path.suffix}"

        # Check read permissions
        if not os.access(script_path, os.R_OK):
            return False, f"Cannot read script: {script_path}"

        # Check that script is in an allowed directory
        # Allow both development directory and installed directory (~/.womm)
        project_root = Path(__file__).parent.parent
        installed_root = Path.home() / ".womm"

        # Also allow current working directory for development
        current_dir = Path.cwd()

        allowed_dirs = [
            project_root / "languages",
            project_root / "shared",
            project_root,
            installed_root / "languages",
            installed_root / "shared",
            installed_root,
            current_dir / "languages",
            current_dir / "shared",
            current_dir,
        ]

        # Convert script_path to absolute path for comparison
        script_abs_path = script_path.resolve()

        script_in_allowed_dir = any(
            script_abs_path.is_relative_to(allowed_dir) for allowed_dir in allowed_dirs
        )

        if not script_in_allowed_dir:
            return False, f"Script not in allowed directory: {script_path}"

        return True, ""

    def validate_registry_operation(self, key_path: str) -> Tuple[bool, str]:
        """
        Validate registry operation (Windows only).

        Args:
            key_path: Registry key path
            operation: Operation type ('read', 'write', 'delete')

        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.system != "Windows":
            return False, "Registry operations only supported on Windows"

        # Check key format
        if not re.match(r"^[A-Za-z0-9_\\]+$", key_path):
            return False, f"Invalid registry key format: {key_path}"

        # Check allowed keys
        allowed_prefixes = [
            r"Software\\WorksOnMyMachine",
            r"Software\\Classes\\Directory\\Background\\shell",
            r"Software\\Classes\\Directory\\shell",
        ]

        key_allowed = any(
            re.match(prefix, key_path, re.IGNORECASE) for prefix in allowed_prefixes
        )

        if not key_allowed:
            return False, f"Registry key not allowed: {key_path}"

        return True, ""


# Global instance for simple usage
security_validator = SecurityValidator()


def validate_user_input(input_value: str, input_type: str) -> Tuple[bool, str]:
    """
    Validate user input based on type.

    Args:
        input_value: User input to validate
        input_type: Type of input ('project_name', 'path', 'command')

    Returns:
        Tuple of (is_valid, error_message)
    """
    if input_type == "project_name":
        return security_validator.validate_project_name(input_value)
    elif input_type == "path":
        return security_validator.validate_path(input_value)
    elif input_type == "command":
        return security_validator.validate_command(input_value)
    elif input_type == "template_name":
        return security_validator.validate_project_name(
            input_value
        )  # Use same validation as project_name
    else:
        return False, f"Unknown input type: {input_type}"
