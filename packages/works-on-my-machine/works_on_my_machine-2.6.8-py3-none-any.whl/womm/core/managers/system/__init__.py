"""
System management modules for Works On My Machine.

This package contains system managers with integrated UI functionality.
"""

from .system_manager import SystemManager
from .user_path_manager import PathManager

__all__ = ["SystemManager", "PathManager"]
