"""
Installation modules for Works On My Machine.

This package contains all installation related functionality.
"""

from .installation_manager import InstallationManager

# PrerequisiteInstaller has been moved to shared.core.prerequisite_manager
from .uninstallation_manager import UninstallationManager

# Note: deploy-devtools.py is a script, not a module
# Functions can be imported directly if needed

__all__ = [
    "InstallationManager",
    "UninstallationManager",
]
