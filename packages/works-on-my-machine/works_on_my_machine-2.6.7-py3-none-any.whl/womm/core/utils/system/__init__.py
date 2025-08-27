#!/usr/bin/env python3
"""
System utility modules for Works On My Machine.

This package contains pure utility functions for system management operations.
"""

# Import utility functions for external use
from .system_detector import SystemDetector
from .user_path_utils import deduplicate_path_entries, extract_path_from_reg_output

__all__ = [
    "SystemDetector",
    "deduplicate_path_entries",
    "extract_path_from_reg_output",
]
