#!/usr/bin/env python3
"""
Dictionary Manager for CSpell - Pure utility functions for dictionary operations.
Used by SpellManager for UI-integrated dictionary management.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .cspell_utils import add_words_from_file


def add_all_dictionaries_from_dir(project_path: Path) -> bool:
    """
    Add all dictionary files from .cspell-dict/ to CSpell configuration.
    Pure utility function without UI - used by SpellManager.

    Args:
        project_path: Project root path

    Returns:
        bool: True if successful, False otherwise
    """
    cspell_dict_dir = project_path / ".cspell-dict"

    # Check if .cspell-dict directory exists
    if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
        return False

    # Find all .txt files
    dict_files = list(cspell_dict_dir.glob("*.txt"))

    if not dict_files:
        return False

    # Process each dictionary file
    success_count = 0

    for dict_file in dict_files:
        try:
            success = add_words_from_file(project_path, dict_file)
            if success:
                success_count += 1
        except Exception as e:
            logging.debug(f"Error with {dict_file.name}: {e}")

    # Return True if at least some dictionaries were added
    return success_count > 0


def list_available_dictionaries(project_path: Optional[Path] = None) -> List[Path]:
    """
    List all available dictionary files in .cspell-dict/.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        List[Path]: List of dictionary file paths
    """
    if project_path is None:
        project_path = Path.cwd()

    cspell_dict_dir = project_path / ".cspell-dict"

    if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
        return []

    return list(cspell_dict_dir.glob("*.txt"))


def get_dictionary_info(project_path: Optional[Path] = None) -> dict:
    """
    Get information about available dictionaries.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        dict: Dictionary information
    """
    if project_path is None:
        project_path = Path.cwd()

    cspell_dict_dir = project_path / ".cspell-dict"

    info = {
        "directory_exists": cspell_dict_dir.exists(),
        "directory_path": str(cspell_dict_dir),
        "files": [],
        "total_files": 0,
        "total_words": 0,
    }

    if not info["directory_exists"]:
        return info

    dict_files = list_available_dictionaries(project_path)
    info["files"] = [str(f) for f in dict_files]
    info["total_files"] = len(dict_files)

    # Count words in each file
    for dict_file in dict_files:
        try:
            with open(dict_file, encoding="utf-8") as f:
                words = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                info["total_words"] += len(words)
        except Exception as e:
            logging.debug(f"Failed to read dictionary file {dict_file}: {e}")

    return info


# Backward compatibility wrapper for CLI usage
def add_all_dictionaries(project_path: Optional[Path] = None) -> bool:
    """Legacy function name for backward compatibility."""
    if project_path is None:
        project_path = Path.cwd()
    return add_all_dictionaries_from_dir(project_path)
