#!/usr/bin/env python3
"""
Common utilities for Works On My Machine installation operations.

This module provides shared utility functions used by both installation
and uninstallation operations.
"""

# IMPORTS
########################################################
# Standard library imports
import sys
from pathlib import Path

# Local imports
from ...exceptions.installation import InstallationUtilityError

# =============================================================================
# COMMON PATH UTILITIES
# =============================================================================


def get_target_womm_path() -> Path:
    """Get the standard target path for Works On My Machine.

    Returns:
        Path object pointing to the .womm directory in user's home.
    """
    return Path.home() / ".womm"


def get_current_womm_path() -> Path:
    """Get the womm package directory by finding __main__.py.

    Returns:
        Path object pointing to the womm package directory (parent of __main__.py).

    Raises:
        InstallationUtilityError: If the womm package directory cannot be found.
    """
    # Try to find __main__.py in the womm package
    try:
        import womm.__main__

        __main__path = Path(womm.__main__.__file__)
        womm_dir = __main__path.parent
        return womm_dir
    except ImportError as e:
        # Fallback: search in sys.path for __main__.py
        for path in sys.path:
            if path:
                potential_main = Path(path) / "womm" / "__main__.py"
                if potential_main.exists():
                    return potential_main.parent

        # Last resort: try to find from current file location
        current_file = Path(__file__)
        # Navigate up to find womm directory
        for parent in current_file.parents:
            if (parent / "__main__.py").exists():
                return parent

        raise InstallationUtilityError(
            message="Could not find womm package directory (__main__.py not found)",
            details=f"Import error: {e}",
        ) from e
