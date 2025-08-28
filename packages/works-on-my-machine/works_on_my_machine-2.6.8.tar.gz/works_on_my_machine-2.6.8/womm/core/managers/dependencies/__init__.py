#!/usr/bin/env python3
"""
Dependencies management for WOMM.

Contains all dependency management modules for runtimes, package managers,
and development tools.
"""

from .dev_tools_manager import dev_tools_manager
from .package_manager import package_manager
from .runtime_manager import runtime_manager

__all__ = [
    "runtime_manager",
    "package_manager",
    "dev_tools_manager",
]
