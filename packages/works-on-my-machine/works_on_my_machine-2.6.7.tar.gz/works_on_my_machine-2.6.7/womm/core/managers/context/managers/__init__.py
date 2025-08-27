#!/usr/bin/env python3
"""
Context menu managers.

This module contains the core managers for context menu operations.
"""

from .backup_manager import BackupManager
from .context_menu import ContextMenuManager
from .icon_manager import IconManager
from .script_detector import ScriptDetector

__all__ = [
    "ContextMenuManager",
    "BackupManager",
    "IconManager",
    "ScriptDetector",
]
