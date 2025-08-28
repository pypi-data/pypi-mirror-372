#!/usr/bin/env python3
"""
Main project manager for WOMM CLI.
Orchestrates project creation and management operations.
"""

from pathlib import Path
from typing import Optional

from ...ui.common.console import print_error, print_info
from ...ui.common.progress import create_spinner_with_status
from ...utils.project.project_detector import ProjectDetector
from ...utils.project.vscode_config import generate_vscode_config
from ..dependencies.runtime_manager import runtime_manager
from .creation.javascript_project_manager import JavaScriptProjectManager
from .creation.project_creator import ProjectCreator
from .creation.python_project_manager import PythonProjectManager
from .templates.template_manager import TemplateManager


class ProjectManager:
    """Main project manager for WOMM CLI."""

    def __init__(self):
        """Initialize the project manager."""
        self.project_creator = ProjectCreator()
        self.python_manager = PythonProjectManager()
        self.javascript_manager = JavaScriptProjectManager()
        self.template_manager = TemplateManager()
        self.detector = ProjectDetector()

    def create_project(
        self,
        project_type: str,
        project_name: Optional[str] = None,
        current_dir: bool = False,
        **kwargs,
    ) -> bool:
        """
        Create a new project of the specified type.

        Args:
            project_type: Type of project to create (python, javascript, etc.)
            project_name: Name of the project
            current_dir: Whether to use current directory
            **kwargs: Additional project-specific options including 'target'

        Returns:
            True if project creation was successful, False otherwise
        """
        try:
            # Determine project path
            target = kwargs.get("target")

            if current_dir:
                project_path = Path.cwd()
                project_name = project_path.name
            elif target:
                # Use specified target directory
                target_path = Path(target)
                if project_name:
                    project_path = target_path / project_name
                else:
                    print_error("Project name is required when using target directory")
                    return False
            elif project_name:
                project_path = Path.cwd() / project_name
            else:
                print_error("Project name is required when not using current directory")
                return False

            # Validate project type
            if not self._validate_project_type(project_type):
                return False

            # Check dependencies
            if not self._check_dependencies(project_type):
                return False

            # Create project based on type
            if project_type == "python":
                return self.python_manager.create_project(
                    project_path, project_name, **kwargs
                )
            elif project_type in ["javascript", "react", "vue"]:
                js_type = (
                    kwargs.get("project_type", "node")
                    if project_type == "javascript"
                    else project_type
                )
                return self.javascript_manager.create_project(
                    project_path, project_name, js_type, **kwargs
                )
            else:
                print_error(f"Unsupported project type: {project_type}")
                return False

        except Exception as e:
            print_error(f"Error creating project: {e}")
            return False

    def detect_project_type(
        self, project_path: Optional[Path] = None
    ) -> tuple[str, int]:
        """
        Detect the type of project in the given path.

        Args:
            project_path: Path to analyze (defaults to current directory)

        Returns:
            Tuple of (project_type, confidence_score)
        """
        detector = ProjectDetector(project_path)
        return detector.detect_project_type()

    def setup_development_environment(
        self, project_path: Path, project_type: str
    ) -> bool:
        """
        Set up development environment for an existing project.

        Args:
            project_path: Path to the project
            project_type: Type of project

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            with create_spinner_with_status("Setting up development environment..."):
                # Generate VSCode configuration
                generate_vscode_config(project_path, project_type)

                # Set up project-specific environment
                if project_type == "python":
                    return self.python_manager.setup_environment(project_path)
                elif project_type in ["javascript", "react", "vue"]:
                    return self.javascript_manager.setup_environment(project_path)
                else:
                    print_error(
                        f"Unsupported project type for environment setup: {project_type}"
                    )
                    return False

        except Exception as e:
            print_error(f"Error setting up development environment: {e}")
            return False

    def _validate_project_type(self, project_type: str) -> bool:
        """Validate that the project type is supported."""
        supported_types = ["python", "javascript", "react", "vue"]
        if project_type not in supported_types:
            print_error(f"Unsupported project type: {project_type}")
            print_info(f"Supported types: {', '.join(supported_types)}")
            return False
        return True

    def _check_dependencies(self, project_type: str) -> bool:
        """Check if required dependencies are available."""
        try:
            if project_type == "python":
                result = runtime_manager.check_runtime("python")
                if not result.success:
                    print_info("Python runtime not found, attempting to install...")
                    install_result = runtime_manager.install_runtime("python")
                    if not install_result.success:
                        print_error("Failed to install Python runtime")
                        return False

            elif project_type in ["javascript", "react", "vue"]:
                result = runtime_manager.check_runtime("node")
                if not result.success:
                    print_info("Node.js runtime not found, attempting to install...")
                    install_result = runtime_manager.install_runtime("node")
                    if not install_result.success:
                        print_error("Failed to install Node.js runtime")
                        return False

            return True

        except Exception as e:
            print_error(f"Error checking dependencies: {e}")
            return False

    def get_available_project_types(self) -> list[tuple[str, str]]:
        """Get list of available project types with descriptions."""
        return [
            ("python", "Python project with virtual environment and development tools"),
            ("javascript", "JavaScript/Node.js project with npm and development tools"),
            ("react", "React.js project with modern development setup"),
            ("vue", "Vue.js project with modern development setup"),
        ]

    def get_project_templates(self, project_type: str) -> list[str]:
        """Get available templates for a project type."""
        return self.template_manager.get_templates(project_type)

    def setup_project(
        self,
        project_type: str,
        project_path: Path,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,
    ) -> bool:
        """
        Set up an existing project with development tools and configuration.

        Args:
            project_type: Type of project (python, javascript, react, vue)
            project_path: Path to the existing project
            virtual_env: Whether to create virtual environment (Python only)
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks
            **kwargs: Additional project-specific options

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            # Validate project type
            if not self._validate_project_type(project_type):
                return False

            # Check dependencies
            if not self._check_dependencies(project_type):
                return False

            # Set up project based on type
            if project_type == "python":
                return self.python_manager.setup_existing_project(
                    project_path,
                    virtual_env=virtual_env,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                    **kwargs,
                )
            elif project_type in ["javascript", "react", "vue"]:
                return self.javascript_manager.setup_existing_project(
                    project_path,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                    **kwargs,
                )
            else:
                print_error(f"Unsupported project type for setup: {project_type}")
                return False

        except Exception as e:
            print_error(f"Error setting up project: {e}")
            return False
