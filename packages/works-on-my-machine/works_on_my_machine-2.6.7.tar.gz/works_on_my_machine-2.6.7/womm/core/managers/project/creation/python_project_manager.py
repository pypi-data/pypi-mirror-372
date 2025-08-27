#!/usr/bin/env python3
"""
Python project manager for WOMM CLI.
Handles Python-specific project creation and setup.
"""

import venv
from pathlib import Path

from ....ui.common.console import print_error
from ....ui.common.extended.dynamic_progress import create_dynamic_layered_progress
from ....ui.project import print_new_project_summary, print_setup_completion_summary
from ....utils.cli_utils import run_command
from .project_creator import ProjectCreator

# Configuration for DynamicLayeredProgress
PYTHON_PROJECT_CREATION_STAGES = [
    {
        "name": "main",
        "type": "main",
        "description": "Creating Python Project",
        "style": "bold blue",
        "steps": [
            "Validating project configuration",
            "Creating project structure",
            "Setting up virtual environment",
            "Installing dependencies",
            "Configuring development tools",
            "Setting up Git repository",
        ],
    },
    {
        "name": "validation",
        "type": "spinner",
        "description": "Validating configuration",
        "style": "bright_blue",
    },
    {
        "name": "structure",
        "type": "spinner",
        "description": "Creating project structure",
        "style": "bright_green",
    },
    {
        "name": "venv",
        "type": "spinner",
        "description": "Setting up virtual environment",
        "style": "bright_cyan",
    },
    {
        "name": "deps",
        "type": "spinner",
        "description": "Installing dependencies",
        "style": "bright_magenta",
    },
    {
        "name": "tools",
        "type": "spinner",
        "description": "Configuring development tools",
        "style": "bright_yellow",
    },
    {
        "name": "git",
        "type": "spinner",
        "description": "Setting up Git repository",
        "style": "bright_white",
    },
]

# Base configuration for DynamicLayeredProgress - Setup
PYTHON_PROJECT_SETUP_STAGES_BASE = [
    {
        "name": "main",
        "type": "main",
        "description": "Setting up Python Project",
        "style": "bold blue",
        "steps": [
            "Setting up virtual environment",
            "Installing dependencies",
            "Configuring development tools",
            "Setting up Git hooks",
        ],
    },
    {
        "name": "venv",
        "type": "spinner",
        "description": "Setting up virtual environment",
        "style": "bright_cyan",
    },
    {
        "name": "deps",
        "type": "spinner",
        "description": "Installing dependencies",
        "style": "bright_magenta",
    },
    {
        "name": "tools",
        "type": "spinner",
        "description": "Configuring development tools",
        "style": "bright_yellow",
    },
    {
        "name": "git",
        "type": "spinner",
        "description": "Setting up Git hooks",
        "style": "bright_white",
    },
]


def get_python_setup_stages(
    virtual_env: bool = False,
    install_deps: bool = False,
    setup_dev_tools: bool = False,
    setup_git_hooks: bool = False,
) -> list:
    """Generate setup stages based on selected options."""
    stages = [PYTHON_PROJECT_SETUP_STAGES_BASE[0]]  # Always include main

    # Filter steps in main stage
    main_steps = []
    if virtual_env:
        main_steps.append("Setting up virtual environment")
        stages.append(PYTHON_PROJECT_SETUP_STAGES_BASE[1])  # venv
    if install_deps:
        main_steps.append("Installing dependencies")
        stages.append(PYTHON_PROJECT_SETUP_STAGES_BASE[2])  # deps
    if setup_dev_tools:
        main_steps.append("Configuring development tools")
        stages.append(PYTHON_PROJECT_SETUP_STAGES_BASE[3])  # tools
    if setup_git_hooks:
        main_steps.append("Setting up Git hooks")
        stages.append(PYTHON_PROJECT_SETUP_STAGES_BASE[4])  # git

    # Update main stage steps
    stages[0]["steps"] = main_steps

    return stages


class PythonProjectManager(ProjectCreator):
    """Python-specific project manager."""

    def __init__(self):
        """Initialize the Python project manager."""
        super().__init__()
        self.template_dir = (
            Path(__file__).parent.parent.parent.parent.parent
            / "languages"
            / "python"
            / "templates"
        )

    def create_project(self, project_path: Path, project_name: str, **kwargs) -> bool:
        """
        Create a Python project with DynamicLayeredProgress.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            **kwargs: Additional configuration options

        Returns:
            True if project creation was successful, False otherwise
        """
        try:
            with create_dynamic_layered_progress(
                PYTHON_PROJECT_CREATION_STAGES
            ) as progress:
                # Step 1: Validate configuration
                progress.update_layer(
                    "validation", 0, "Validating project configuration..."
                )
                if not self.validate_project_config(
                    project_name, project_path, "python"
                ):
                    progress.handle_error("validation", "Invalid project configuration")
                    return False
                progress.complete_layer("validation")

                # Step 2: Create project structure
                progress.update_layer("structure", 0, "Creating project structure...")
                if not self.create_project_structure(project_path, project_name):
                    progress.handle_error(
                        "structure", "Failed to create project structure"
                    )
                    return False

                # Step 2.5: Create Python-specific files (part of structure)
                progress.update_layer("structure", 50, "Creating Python files...")
                if not self._create_python_files(project_path, project_name, **kwargs):
                    progress.handle_error("structure", "Failed to create Python files")
                    return False
                progress.complete_layer("structure")

                # Step 3: Set up virtual environment
                progress.update_layer("venv", 0, "Setting up virtual environment...")
                if not self._setup_virtual_environment(project_path):
                    progress.handle_error(
                        "venv", "Failed to set up virtual environment"
                    )
                    return False
                progress.complete_layer("venv")

                # Step 4: Install development dependencies
                progress.update_layer(
                    "deps", 0, "Installing development dependencies..."
                )
                if not self._install_dev_dependencies(project_path):
                    progress.handle_error("deps", "Failed to install dependencies")
                    return False
                progress.complete_layer("deps")

                # Step 5: Set up development tools
                progress.update_layer("tools", 0, "Configuring development tools...")
                if not self._setup_dev_tools(project_path):
                    progress.handle_error("tools", "Failed to set up development tools")
                    return False
                progress.complete_layer("tools")

                # Step 6: Initialize Git repository
                progress.update_layer("git", 0, "Setting up Git repository...")
                self.setup_git_repository(project_path)
                progress.complete_layer("git")

            print_new_project_summary(project_path, project_name, "python")
            return True

        except Exception as e:
            print_error(f"Error creating Python project: {e}")
            return False

    def _create_python_files(
        self, project_path: Path, project_name: str, **kwargs
    ) -> bool:
        """Create Python-specific project files."""
        try:
            # Create pyproject.toml
            if not self._create_pyproject_toml(project_path, project_name, **kwargs):
                return False

            # Create main Python file
            if not self._create_main_python_file(project_path, project_name):
                return False

            # Create test file
            if not self._create_test_file(project_path, project_name):
                return False

            # Create requirements files
            if not self._create_requirements_files(project_path):
                return False

            # Create development configuration files
            return self._create_dev_config_files(project_path)

        except Exception as e:
            print_error(f"Error creating Python files: {e}")
            return False

    def _create_pyproject_toml(
        self, project_path: Path, project_name: str, **kwargs
    ) -> bool:
        """Create pyproject.toml configuration file."""
        try:
            template_path = self.template_dir / "pyproject.toml.template"
            output_path = project_path / "pyproject.toml"

            template_vars = {
                "PROJECT_NAME": project_name,
                "PROJECT_DESCRIPTION": f"{project_name} - A Python project created with WOMM CLI",
                "AUTHOR_NAME": kwargs.get("author_name", "Your Name"),
                "AUTHOR_EMAIL": kwargs.get("author_email", "your.email@example.com"),
                "PROJECT_URL": kwargs.get("project_url", ""),
                "PROJECT_REPOSITORY": kwargs.get("project_repository", ""),
                "PROJECT_DOCS_URL": kwargs.get("project_docs_url", ""),
                "PROJECT_KEYWORDS": kwargs.get(
                    "project_keywords", "python,cli,utility"
                ),
            }

            return self.generate_template_file(
                template_path, output_path, template_vars
            )

        except Exception as e:
            print_error(f"Error creating pyproject.toml: {e}")
            return False

    def _create_main_python_file(self, project_path: Path, project_name: str) -> bool:
        """Create the main Python file."""
        try:
            # Create src directory structure
            src_dir = project_path / "src" / project_name.replace("-", "_")
            src_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py
            init_file = src_dir / "__init__.py"
            init_file.write_text(
                f'"""Main package for {project_name}."""\n\n__version__ = "0.1.0"\n',
                encoding="utf-8",
            )

            # Create main.py
            main_file = src_dir / "main.py"
            main_content = f'''#!/usr/bin/env python3
"""
Main entry point for {project_name}.

This module serves as the main entry point for the application.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from {project_name.replace("-", "_")} import __version__


def main():
    """Main function."""
    print(f"Hello from {{project_name}} v{{__version__}}!")
    print("This is a Python project created with WOMM CLI.")

    # Add your application logic here
    return 0



'''
            main_file.write_text(main_content, encoding="utf-8")
            main_file.chmod(0o755)  # Make executable

            return True

        except Exception as e:
            print_error(f"Error creating main Python file: {e}")
            return False

    def _create_test_file(self, project_path: Path, project_name: str) -> bool:
        """Create a basic test file."""
        try:
            test_dir = project_path / "tests"
            test_file = test_dir / f"test_{project_name.replace('-', '_')}.py"

            test_content = f'''"""
Tests for {project_name}.

This module contains tests for the main functionality.
"""

import pytest
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
import sys
sys.path.insert(0, str(src_path))

from {project_name.replace("-", "_")} import __version__


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_import():
    """Test that the package can be imported."""
    import {project_name.replace("-", "_")}
    assert {project_name.replace("-", "_")} is not None



'''
            test_file.write_text(test_content, encoding="utf-8")
            return True

        except Exception as e:
            print_error(f"Error creating test file: {e}")
            return False

    def _create_requirements_files(self, project_path: Path) -> bool:
        """Create requirements files."""
        try:
            # Create requirements.txt
            requirements_content = """# Core dependencies
# Add your project dependencies here
# Example:
# requests>=2.28.0
# pandas>=1.5.0
"""
            requirements_file = project_path / "requirements.txt"
            requirements_file.write_text(requirements_content, encoding="utf-8")

            # Create requirements-dev.txt
            dev_requirements_content = """# Development dependencies
-r requirements.txt

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0

# Code quality
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
mypy>=1.0.0

# Pre-commit
pre-commit>=3.0.0

# Documentation
sphinx>=6.0.0
sphinx-rtd-theme>=1.2.0
"""
            dev_requirements_file = project_path / "requirements-dev.txt"
            dev_requirements_file.write_text(dev_requirements_content, encoding="utf-8")

            return True

        except Exception as e:
            print_error(f"Error creating requirements files: {e}")
            return False

    def _create_dev_config_files(self, project_path: Path) -> bool:
        """Create development configuration files."""
        try:
            # Create .flake8
            flake8_config = """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude =
    .git,
    __pycache__,
    .venv,
    venv,
    .mypy_cache,
    .pytest_cache,
    build,
    dist,
    *.egg-info
"""
            flake8_file = project_path / ".flake8"
            flake8_file.write_text(flake8_config, encoding="utf-8")

            # Create .isort.cfg
            isort_config = """[settings]
profile = black
line_length = 88
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
"""
            isort_file = project_path / ".isort.cfg"
            isort_file.write_text(isort_config, encoding="utf-8")

            # Create mypy.ini
            mypy_config = """[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy.plugins.numpy.*]
ignore_missing_imports = True
"""
            mypy_file = project_path / "mypy.ini"
            mypy_file.write_text(mypy_config, encoding="utf-8")

            return True

        except Exception as e:
            print_error(f"Error creating dev config files: {e}")
            return False

    def _setup_virtual_environment(self, project_path: Path) -> bool:
        """Set up Python virtual environment."""
        try:
            venv_path = project_path / "venv"

            if venv_path.exists():
                return True

            # Create virtual environment
            venv.create(venv_path, with_pip=True)

            # Upgrade pip
            python_exe = (
                venv_path / "Scripts" / "python.exe"
                if project_path.drive
                else venv_path / "bin" / "python"
            )
            pip_exe = (
                venv_path / "Scripts" / "pip.exe"
                if project_path.drive
                else venv_path / "bin" / "pip"
            )

            if python_exe.exists() and pip_exe.exists():
                result = run_command(
                    [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
                    "Upgrading pip",
                    cwd=project_path,
                )
                if not result.success:
                    pass

            return True

        except Exception as e:
            print_error(f"Error setting up virtual environment: {e}")
            return False

    def _install_dev_dependencies(self, project_path: Path) -> bool:
        """Install development dependencies."""
        try:
            venv_path = project_path / "venv"

            # Check if virtual environment exists
            if not venv_path.exists():
                print_error("Virtual environment not found")
                return False

            # Find pip executable
            pip_exe = None
            possible_pip_paths = [
                venv_path / "Scripts" / "pip.exe",  # Windows
                venv_path / "bin" / "pip",  # Unix
                venv_path / "Scripts" / "pip3.exe",  # Windows with version
                venv_path / "bin" / "pip3",  # Unix with version
            ]

            for pip_path in possible_pip_paths:
                if pip_path.exists():
                    pip_exe = pip_path
                    break

            if not pip_exe:
                print_error("pip not found in virtual environment")
                return False

            # Install development requirements
            dev_requirements = project_path / "requirements-dev.txt"
            if dev_requirements.exists():
                # Use run_command but bypass security validation
                from ....utils.cli_utils import run_silent

                result = run_silent(
                    [str(pip_exe), "install", "-r", "requirements-dev.txt"],
                    cwd=project_path,
                    timeout=600,
                )

                if not result.success:
                    print_error(
                        f"Failed to install development dependencies: {result.stderr}"
                    )
                    return False
            else:
                # No requirements-dev.txt found, skipping dependency installation
                pass

            return True

        except Exception as e:
            print_error(f"Error installing development dependencies: {e}")
            return False

    def _setup_pre_commit(self, project_path: Path) -> bool:
        """Set up pre-commit hooks."""
        try:
            venv_path = project_path / "venv"
            python_exe = (
                venv_path / "Scripts" / "python.exe"
                if project_path.drive
                else venv_path / "bin" / "python"
            )

            if not python_exe.exists():
                # print_info(
                #     "Python not found in virtual environment, skipping pre-commit setup"
                # )  # Supprimé pour éviter duplication
                return True

            # Create .pre-commit-config.yaml
            pre_commit_config = """repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
"""
            pre_commit_file = project_path / ".pre-commit-config.yaml"
            pre_commit_file.write_text(pre_commit_config, encoding="utf-8")

            # Install pre-commit hooks
            result = run_command(
                [str(python_exe), "-m", "pre_commit", "install"],
                "Installing pre-commit hooks",
                cwd=project_path,
            )

            if result.success:
                return True
            else:
                # print_info("Warning: Failed to install pre-commit hooks")  # Supprimé pour éviter duplication
                return True

        except Exception as e:
            print_error(f"Error setting up pre-commit: {e}")
            return False

    def setup_environment(self, project_path: Path) -> bool:
        """
        Set up development environment for an existing Python project.

        Args:
            project_path: Path to the project

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            # Set up virtual environment
            if not self._setup_virtual_environment(project_path):
                return False

            # Install development dependencies
            if not self._install_dev_dependencies(project_path):
                return False

            # Set up pre-commit hooks
            return self._setup_pre_commit(project_path)

        except Exception as e:
            print_error(f"Error setting up Python environment: {e}")
            return False

    def setup_existing_project(
        self,
        project_path: Path,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,  # noqa: ARG002
    ) -> bool:
        """
        Set up an existing Python project with development tools.

        Args:
            project_path: Path to the existing project
            virtual_env: Whether to create virtual environment
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks
            **kwargs: Additional options

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            # Generate stages based on selected options
            setup_stages = get_python_setup_stages(
                virtual_env=virtual_env,
                install_deps=install_deps,
                setup_dev_tools=setup_dev_tools,
                setup_git_hooks=setup_git_hooks,
            )

            with create_dynamic_layered_progress(setup_stages) as progress:
                # Step 1: Set up virtual environment if requested
                if virtual_env:
                    progress.update_layer(
                        "venv", 0, "Setting up virtual environment..."
                    )
                    if not self._setup_virtual_environment(project_path):
                        progress.handle_error(
                            "venv", "Failed to set up virtual environment"
                        )
                        return False
                    progress.complete_layer("venv")

                # Step 2: Install dependencies if requested
                if install_deps:
                    progress.update_layer("deps", 0, "Installing dependencies...")
                    if not self._install_dev_dependencies(project_path):
                        progress.handle_error("deps", "Failed to install dependencies")
                        return False
                    progress.complete_layer("deps")

                # Step 3: Set up development tools if requested
                if setup_dev_tools:
                    progress.update_layer(
                        "tools", 0, "Configuring development tools..."
                    )
                    if not self._setup_dev_tools(project_path):
                        progress.handle_error(
                            "tools", "Failed to set up development tools"
                        )
                        return False
                    progress.complete_layer("tools")

                # Step 4: Set up Git hooks if requested
                if setup_git_hooks:
                    progress.update_layer("git", 0, "Setting up Git hooks...")
                    if not self._setup_pre_commit(project_path):
                        progress.handle_error("git", "Failed to set up Git hooks")
                        return False
                    progress.complete_layer("git")

            # Generate setup completion summary
            print_setup_completion_summary(
                project_path,
                "python",
                virtual_env=virtual_env,
                install_deps=install_deps,
                setup_dev_tools=setup_dev_tools,
                setup_git_hooks=setup_git_hooks,
            )

            return True

        except Exception as e:
            print_error(f"Error setting up Python project: {e}")
            return False

    def _setup_dev_tools(self, project_path: Path) -> bool:
        """Set up development tools for existing project."""
        try:
            # Create development configuration files if they don't exist
            if not self._create_dev_config_files(project_path):
                return False

            # Install development dependencies
            return self._install_dev_dependencies(project_path)

        except Exception as e:
            print_error(f"Error setting up development tools: {e}")
            return False
