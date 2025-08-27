#!/usr/bin/env python3
"""
File Scanner - Utilities for finding and filtering Python files.
Handles file discovery, security pattern filtering, and directory scanning.
"""

import logging
from pathlib import Path
from typing import List

from .security.security_validator import SecurityValidator


class FileScanner:
    """Handles file discovery and filtering for linting operations."""

    PYTHON_EXTENSIONS = {".py", ".pyi"}
    EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".env",
        "build",
        "dist",
        "*.egg-info",
    }

    def __init__(self):
        """Initialize file scanner."""
        self.security_validator = SecurityValidator()

    def find_python_files(
        self, target_path: Path, recursive: bool = True
    ) -> List[Path]:
        """
        Find Python files in the given path.

        Args:
            target_path: Path to search (file or directory)
            recursive: Whether to search recursively in subdirectories

        Returns:
            List[Path]: List of Python file paths
        """
        if not target_path.exists():
            logging.warning(f"Path does not exist: {target_path}")
            return []

        python_files = []

        if target_path.is_file():
            if self._is_python_file(target_path):
                python_files.append(target_path)
        elif target_path.is_dir():
            python_files.extend(self._scan_directory(target_path, recursive))

        # Filter out files that match security patterns
        filtered_files = self._filter_secure_files(python_files)

        logging.debug(f"Found {len(filtered_files)} Python files in {target_path}")
        return filtered_files

    def get_project_python_files(self, project_root: Path) -> List[Path]:
        """
        Get all Python files in a project, excluding common non-source directories.

        Args:
            project_root: Root directory of the project

        Returns:
            List[Path]: List of Python source files
        """
        if not project_root.exists() or not project_root.is_dir():
            logging.warning(f"Invalid project root: {project_root}")
            return []

        python_files = []

        # Walk through all subdirectories
        try:
            for item in project_root.rglob("*"):
                if self._should_exclude_path(item):
                    continue

                if item.is_file() and self._is_python_file(item):
                    python_files.append(item)

        except (PermissionError, OSError) as e:
            logging.warning(f"Error scanning {project_root}: {e}")

        # Filter security patterns
        filtered_files = self._filter_secure_files(python_files)

        logging.debug(
            f"Found {len(filtered_files)} Python files in project {project_root.name}"
        )
        return filtered_files

    def _scan_directory(self, directory: Path, recursive: bool) -> List[Path]:
        """
        Scan a directory for Python files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List[Path]: List of Python files found
        """
        python_files = []

        try:
            pattern = "**/*" if recursive else "*"

            for item in directory.glob(pattern):
                if self._should_exclude_path(item):
                    continue

                if item.is_file() and self._is_python_file(item):
                    python_files.append(item)

        except (PermissionError, OSError) as e:
            logging.warning(f"Error scanning directory {directory}: {e}")

        return python_files

    def _is_python_file(self, file_path: Path) -> bool:
        """
        Check if a file is a Python file.

        Args:
            file_path: Path to check

        Returns:
            bool: True if it's a Python file
        """
        return file_path.suffix.lower() in self.PYTHON_EXTENSIONS

    def _should_exclude_path(self, path: Path) -> bool:
        """
        Check if a path should be excluded from scanning.

        Args:
            path: Path to check

        Returns:
            bool: True if path should be excluded
        """
        # Check if any part of the path matches excluded directories
        for part in path.parts:
            if part in self.EXCLUDED_DIRS:
                return True

        # Check for pattern matches (like *.egg-info)
        for pattern in self.EXCLUDED_DIRS:
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(path.name, pattern):
                    return True

        return False

    def _filter_secure_files(self, files: List[Path]) -> List[Path]:
        """
        Filter out files that contain security patterns.

        Args:
            files: List of files to filter

        Returns:
            List[Path]: Filtered list of files
        """
        filtered_files = []

        for file_path in files:
            try:
                # Use validate_path method which exists in SecurityValidator
                is_valid, error_msg = self.security_validator.validate_path(
                    file_path, must_exist=True
                )
                if is_valid:
                    filtered_files.append(file_path)
                else:
                    logging.debug(
                        f"Excluded file due to security validation: {file_path} - {error_msg}"
                    )
            except Exception as e:
                logging.warning(f"Error checking security for {file_path}: {e}")
                # Include the file if we can't check it
                filtered_files.append(file_path)

        return filtered_files

    def get_scan_summary(self, files: List[Path]) -> dict:
        """
        Get summary information about scanned files.

        Args:
            files: List of files that were found

        Returns:
            dict: Summary information
        """
        if not files:
            return {
                "total_files": 0,
                "total_size": 0,
                "directories": set(),
                "extensions": {},
            }

        total_size = 0
        directories = set()
        extensions = {}

        for file_path in files:
            try:
                # Get file size
                total_size += file_path.stat().st_size

                # Track directories
                directories.add(file_path.parent)

                # Count extensions
                ext = file_path.suffix.lower()
                extensions[ext] = extensions.get(ext, 0) + 1

            except (OSError, PermissionError):
                # Skip files we can't access
                continue

        return {
            "total_files": len(files),
            "total_size": total_size,
            "directories": directories,
            "extensions": extensions,
        }
