#!/usr/bin/env python3
"""
Project validation utilities for WOMM CLI.
Validates project names, paths, and configurations.
"""

import re
from pathlib import Path
from typing import Tuple


class ProjectValidator:
    """Project validation utilities."""

    # Invalid characters for project names
    INVALID_CHARS = r'[<>:"/\\|?*]'

    # Reserved names on Windows
    RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    @classmethod
    def validate_project_name(cls, project_name: str) -> Tuple[bool, str]:
        """
        Validate a project name.

        Args:
            project_name: Name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not project_name:
            return False, "Project name cannot be empty"

        if len(project_name) > 50:
            return False, "Project name is too long (max 50 characters)"

        if project_name.startswith(".") or project_name.endswith("."):
            return False, "Project name cannot start or end with a dot"

        if re.search(cls.INVALID_CHARS, project_name):
            return (
                False,
                f"Project name contains invalid characters: {cls.INVALID_CHARS}",
            )

        if project_name.upper() in cls.RESERVED_NAMES:
            return False, f"Project name '{project_name}' is reserved on Windows"

        if not re.match(r"^[a-zA-Z0-9._-]+$", project_name):
            return (
                False,
                "Project name can only contain letters, numbers, dots, underscores, and hyphens",
            )

        return True, ""

    @classmethod
    def validate_project_path(cls, project_path: Path) -> Tuple[bool, str]:
        """
        Validate a project path.

        Args:
            project_path: Path to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if path is absolute
            if not project_path.is_absolute():
                project_path = project_path.resolve()

            # Check if parent directory exists and is writable
            parent_dir = project_path.parent
            if not parent_dir.exists():
                return False, f"Parent directory does not exist: {parent_dir}"

            if not parent_dir.is_dir():
                return False, f"Parent path is not a directory: {parent_dir}"

            # Check if we can write to parent directory
            try:
                test_file = parent_dir / ".womm_test_write"
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError):
                return False, f"Cannot write to directory: {parent_dir}"

            # Check if project directory already exists
            if project_path.exists():
                if not project_path.is_dir():
                    return False, f"Path exists but is not a directory: {project_path}"

                # Check if directory is empty
                try:
                    if any(project_path.iterdir()):
                        return False, f"Directory is not empty: {project_path}"
                except PermissionError:
                    return False, f"Cannot access directory: {project_path}"

            return True, ""

        except Exception as e:
            return False, f"Error validating path: {e}"

    @classmethod
    def validate_project_type(cls, project_type: str) -> Tuple[bool, str]:
        """
        Validate a project type.

        Args:
            project_type: Type to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        supported_types = ["python", "javascript", "react", "vue"]

        if not project_type:
            return False, "Project type cannot be empty"

        if project_type not in supported_types:
            return (
                False,
                f"Unsupported project type: {project_type}. Supported: {', '.join(supported_types)}",
            )

        return True, ""

    @classmethod
    def validate_project_config(cls, config: dict) -> Tuple[bool, str]:
        """
        Validate a project configuration.

        Args:
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["project_name", "project_type"]

        for field in required_fields:
            if field not in config:
                return False, f"Missing required field: {field}"

        # Validate individual fields
        is_valid, error = cls.validate_project_name(config["project_name"])
        if not is_valid:
            return False, f"Invalid project name: {error}"

        is_valid, error = cls.validate_project_type(config["project_type"])
        if not is_valid:
            return False, f"Invalid project type: {error}"

        return True, ""

    @classmethod
    def suggest_project_name(cls, base_name: str) -> str:
        """
        Suggest a valid project name based on input.

        Args:
            base_name: Base name to suggest from

        Returns:
            Valid project name suggestion
        """
        if not base_name:
            return "my-project"

        # Remove invalid characters
        suggested = re.sub(cls.INVALID_CHARS, "-", base_name)

        # Remove leading/trailing dots
        suggested = suggested.strip(".")

        # Convert to lowercase
        suggested = suggested.lower()

        # Replace spaces with hyphens
        suggested = re.sub(r"\s+", "-", suggested)

        # Remove multiple consecutive hyphens
        suggested = re.sub(r"-+", "-", suggested)

        # Ensure it's not empty
        if not suggested:
            suggested = "my-project"

        # Ensure it's not too long
        if len(suggested) > 50:
            suggested = suggested[:50].rstrip("-")

        # Ensure it doesn't start with a number
        if suggested and suggested[0].isdigit():
            suggested = f"project-{suggested}"

        return suggested
