#!/usr/bin/env python3
"""
Backup manager for context menu operations.

This module provides comprehensive backup management functionality
for Windows context menu entries, including creation, validation,
listing, and cleanup of backup files.
"""

import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ...installation.installation_manager import get_target_womm_path


class BackupManager:
    """Manages context menu backup operations."""

    # Backup file format version
    BACKUP_VERSION = "1.0"

    # Maximum number of backup files to keep
    MAX_BACKUP_FILES = 10

    # Backup file retention period (days)
    BACKUP_RETENTION_DAYS = 30

    def __init__(self):
        """Initialize the backup manager."""
        self.backup_dir = self._get_backup_directory()

    def _get_backup_directory(self) -> Path:
        """Get the backup directory path."""
        try:
            womm_path = get_target_womm_path()
            if womm_path.exists():
                backup_dir = womm_path / ".backup" / "context_menu"
                backup_dir.mkdir(parents=True, exist_ok=True)
                return backup_dir
        except Exception as e:
            # Log the exception for debugging
            import logging

            logging.debug(f"Could not access WOMM backup directory: {e}")

        # Fallback to current directory
        return Path(".")

    def create_backup_file(
        self,
        entries: Dict,
        custom_filename: Optional[str] = None,
        add_timestamp: bool = True,
    ) -> Tuple[bool, str, Dict]:
        """
        Create a backup file with context menu entries.

        Args:
            entries: Dictionary containing context menu entries
            custom_filename: Optional custom filename (without extension)
            add_timestamp: Whether to add timestamp to filename

        Returns:
            Tuple of (success, filepath, metadata)
        """
        try:
            # Generate filename
            base_name = custom_filename or "context_menu_backup"

            if add_timestamp:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{base_name}_{timestamp}.json"
            else:
                filename = f"{base_name}.json"

            filepath = self.backup_dir / filename

            # Create backup data with metadata
            backup_data = self._create_backup_data(entries)

            # Write backup file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            return True, str(filepath), backup_data["metadata"]

        except Exception as e:
            return False, str(e), {}

    def _create_backup_data(self, entries: Dict) -> Dict:
        """
        Create backup data structure with metadata.

        Args:
            entries: Context menu entries

        Returns:
            Backup data dictionary with metadata
        """
        # Count total entries
        total_entries = sum(
            len(entries.get(context_type, []))
            for context_type in ["directory", "background"]
        )

        # Create metadata
        metadata = {
            "version": self.BACKUP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "platform": "Windows",
            "total_entries": total_entries,
            "context_types": list(entries.keys()),
            "entry_counts": {
                context_type: len(entries.get(context_type, []))
                for context_type in ["directory", "background"]
            },
        }

        return {"metadata": metadata, "entries": entries}

    def list_backup_files(self, include_metadata: bool = True) -> List[Dict]:
        """
        List all available backup files with optional metadata.

        Args:
            include_metadata: Whether to include backup metadata

        Returns:
            List of backup file information dictionaries
        """
        backup_files = []

        try:
            # Find all backup files
            pattern = "context_menu_backup_*.json"
            files = sorted(
                self.backup_dir.glob(pattern),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            for file in files:
                file_info = {
                    "filename": file.name,
                    "filepath": str(file),
                    "size_bytes": file.stat().st_size,
                    "modified_time": datetime.fromtimestamp(file.stat().st_mtime),
                    "size_kb": file.stat().st_size / 1024,
                }

                if include_metadata:
                    try:
                        with open(file, encoding="utf-8") as f:
                            data = json.load(f)

                        metadata = data.get("metadata", {})
                        file_info.update(
                            {
                                "entry_count": metadata.get("total_entries", 0),
                                "backup_version": metadata.get("version", "unknown"),
                                "backup_timestamp": metadata.get(
                                    "timestamp", "unknown"
                                ),
                                "context_types": metadata.get("context_types", []),
                            }
                        )
                    except Exception:
                        file_info.update(
                            {
                                "entry_count": 0,
                                "backup_version": "unknown",
                                "backup_timestamp": "unknown",
                                "context_types": [],
                            }
                        )

                backup_files.append(file_info)

        except Exception as e:
            # Log the exception for debugging
            import logging

            logging.debug(f"Error listing backup files: {e}")

        return backup_files

    def load_backup_file(self, filepath: str) -> Tuple[bool, Dict, str]:
        """
        Load and validate a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            Tuple of (success, data, error_message)
        """
        try:
            backup_path = Path(filepath)
            if not backup_path.exists():
                return False, {}, f"Backup file not found: {filepath}"

            with open(backup_path, encoding="utf-8") as f:
                data = json.load(f)

            # Validate backup format
            validation_result = self.validate_backup_format(data)
            if not validation_result["valid"]:
                return False, {}, f"Invalid backup format: {validation_result['error']}"

            return True, data, ""

        except json.JSONDecodeError as e:
            return False, {}, f"Invalid JSON format: {e}"
        except Exception as e:
            return False, {}, f"Error loading backup: {e}"

    def validate_backup_format(self, data: Dict) -> Dict:
        """
        Validate backup data format.

        Args:
            data: Backup data to validate

        Returns:
            Validation result dictionary
        """
        try:
            # Check required top-level keys
            required_keys = ["metadata", "entries"]
            for key in required_keys:
                if key not in data:
                    return {"valid": False, "error": f"Missing required key: {key}"}

            # Validate metadata
            metadata = data["metadata"]
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

            return {"valid": True, "error": ""}

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {e}"}

    def cleanup_old_backups(
        self, max_files: Optional[int] = None, retention_days: Optional[int] = None
    ) -> Dict:
        """
        Clean up old backup files.

        Args:
            max_files: Maximum number of backup files to keep
            retention_days: Number of days to keep backups

        Returns:
            Cleanup result dictionary
        """
        if max_files is None:
            max_files = self.MAX_BACKUP_FILES
        if retention_days is None:
            retention_days = self.BACKUP_RETENTION_DAYS

        try:
            backup_files = self.list_backup_files(include_metadata=False)
            deleted_files = []
            kept_files = []

            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x["modified_time"])

            cutoff_date = datetime.now() - timedelta(days=retention_days)

            for file_info in backup_files:
                file_path = Path(file_info["filepath"])
                should_delete = False

                # Check retention period
                if file_info["modified_time"] < cutoff_date:
                    should_delete = True

                # Check max files limit
                if len(kept_files) >= max_files:
                    should_delete = True

                if should_delete:
                    try:
                        file_path.unlink()
                        deleted_files.append(file_info["filename"])
                    except Exception as e:
                        # Log the exception for debugging
                        import logging

                        logging.debug(
                            f"Could not delete backup file {file_info['filename']}: {e}"
                        )
                else:
                    kept_files.append(file_info["filename"])

            return {
                "success": True,
                "deleted_files": deleted_files,
                "kept_files": kept_files,
                "deleted_count": len(deleted_files),
                "kept_count": len(kept_files),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "deleted_files": [],
                "kept_files": [],
                "deleted_count": 0,
                "kept_count": 0,
            }

    def get_backup_info(self, filepath: str) -> Dict:
        """
        Get detailed information about a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            Backup information dictionary
        """
        try:
            success, data, error = self.load_backup_file(filepath)
            if not success:
                return {"error": error}

            metadata = data.get("metadata", {})
            entries = data.get("entries", {})

            # Calculate additional statistics
            entry_stats = {}
            for context_type, context_entries in entries.items():
                entry_stats[context_type] = {
                    "count": len(context_entries),
                    "sample_keys": [
                        entry.get("key_name", "unknown")
                        for entry in context_entries[:5]
                    ],
                }

            return {
                "success": True,
                "filepath": filepath,
                "metadata": metadata,
                "entry_stats": entry_stats,
                "total_entries": metadata.get("total_entries", 0),
                "backup_version": metadata.get("version", "unknown"),
                "created": metadata.get("timestamp", "unknown"),
                "platform": metadata.get("platform", "unknown"),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_backup_copy(
        self, source_filepath: str, destination_filepath: str
    ) -> Tuple[bool, str]:
        """
        Create a copy of a backup file.

        Args:
            source_filepath: Source backup file path
            destination_filepath: Destination backup file path

        Returns:
            Tuple of (success, error_message)
        """
        try:
            source_path = Path(source_filepath)
            destination_path = Path(destination_filepath)

            if not source_path.exists():
                return False, f"Source file not found: {source_filepath}"

            # Create destination directory if needed
            destination_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy the file
            shutil.copy2(source_path, destination_path)

            return True, ""

        except Exception as e:
            return False, str(e)

    def merge_backups(
        self, backup_filepaths: List[str], output_filepath: str
    ) -> Tuple[bool, str, Dict]:
        """
        Merge multiple backup files into a single backup.

        Args:
            backup_filepaths: List of backup file paths to merge
            output_filepath: Output backup file path

        Returns:
            Tuple of (success, error_message, merged_data)
        """
        try:
            merged_entries = {"directory": [], "background": []}
            merged_metadata = {
                "version": self.BACKUP_VERSION,
                "timestamp": datetime.now().isoformat(),
                "platform": "Windows",
                "merged_from": [],
                "total_entries": 0,
            }

            # Load and merge each backup
            for filepath in backup_filepaths:
                success, data, error = self.load_backup_file(filepath)
                if not success:
                    return False, f"Error loading {filepath}: {error}", {}

                # Add to merged entries (avoid duplicates by key_name)
                existing_keys = set()
                for context_type in ["directory", "background"]:
                    existing_keys.update(
                        entry.get("key_name") for entry in merged_entries[context_type]
                    )

                for context_type in ["directory", "background"]:
                    for entry in data.get("entries", {}).get(context_type, []):
                        key_name = entry.get("key_name")
                        if key_name and key_name not in existing_keys:
                            merged_entries[context_type].append(entry)
                            existing_keys.add(key_name)

                # Update metadata
                merged_metadata["merged_from"].append(filepath)

            # Calculate total entries
            total_entries = sum(
                len(merged_entries[context_type])
                for context_type in ["directory", "background"]
            )
            merged_metadata["total_entries"] = total_entries

            # Create merged backup data
            merged_data = {"metadata": merged_metadata, "entries": merged_entries}

            # Save merged backup
            success, filepath, _ = self.create_backup_file(
                merged_entries, output_filepath, add_timestamp=False
            )
            if not success:
                return False, f"Error saving merged backup: {filepath}", {}

            return True, "", merged_data

        except Exception as e:
            return False, str(e), {}
