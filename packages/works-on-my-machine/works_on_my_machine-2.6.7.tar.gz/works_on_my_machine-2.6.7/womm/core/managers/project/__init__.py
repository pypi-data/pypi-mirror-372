"""
Project management modules for Works On My Machine.

This package contains project creation and management functionality.
"""

from .creation.javascript_project_manager import JavaScriptProjectManager
from .creation.project_creator import ProjectCreator
from .creation.python_project_manager import PythonProjectManager
from .project_manager import ProjectManager
from .templates.template_manager import TemplateManager

__all__ = [
    "ProjectManager",
    "ProjectCreator",
    "PythonProjectManager",
    "JavaScriptProjectManager",
    "TemplateManager",
]
