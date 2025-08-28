"""
Project creation modules for Works On My Machine.

This package contains project creation functionality for different languages.
"""

from .javascript_project_manager import JavaScriptProjectManager
from .project_creator import ProjectCreator
from .python_project_manager import PythonProjectManager

__all__ = [
    "ProjectCreator",
    "PythonProjectManager",
    "JavaScriptProjectManager",
]
