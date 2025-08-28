#!/usr/bin/env python3
"""
Completion summaries for new project creation.

This module provides UI components for displaying completion summaries
after creating new projects, following the established patterns in the WOMM codebase.
"""

from pathlib import Path

from ..common.console import console
from ..common.panels import create_success_panel


def print_new_project_summary(
    project_path: Path, project_name: str, project_type: str
) -> None:
    """
    Print a completion summary for a newly created project.

    Args:
        project_path: Path to the created project
        project_name: Name of the project
        project_type: Type of project (python, javascript, react, vue)
    """
    if project_type == "python":
        _print_python_new_summary(project_path, project_name)
    elif project_type in ["javascript", "node", "react", "vue"]:
        _print_javascript_new_summary(project_path, project_name, project_type)
    else:
        _print_generic_new_summary(project_path, project_name, project_type)


def _print_python_new_summary(project_path: Path, project_name: str) -> None:
    """Print Python project creation summary."""
    content = f"""
📁 Project location: {project_path}
🐍 Python package: {project_name.replace("-", "_")}

{"=" * 50}

🚀 Next steps:
1. Activate virtual environment:
   {project_path}\\venv\\Scripts\\activate

2. Install dependencies:
   pip install -r requirements-dev.txt

3. Run tests:
   pytest

4. Format code:
   black .
   isort .

5. Lint code:
   flake8 .

6. Run the project:
   python src/{project_name.replace("-", "_")}/main.py

💡 The project includes:
  • Virtual environment (venv)
  • Development tools (black, flake8, isort, mypy)
  • Testing framework (pytest)
  • Pre-commit hooks
  • VSCode configuration"""

    # Create and display the panel
    completion_panel = create_success_panel(
        "Python Project Created Successfully!",
        content,
        border_style="bright_green",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)


def _print_javascript_new_summary(
    project_path: Path,
    project_name: str,
    project_type: str,  # noqa: ARG001
) -> None:
    """Print JavaScript project creation summary."""
    content = f"""
📁 Project location: {project_path}
🟨 Project type: {project_type}

{"=" * 50}

🚀 Next steps:
1. Install dependencies:
   npm install

2. Start development server:
   npm start

3. Run tests:
   npm test

4. Lint code:
   npm run lint

5. Format code:
   npm run format

6. Build project:
   npm run build"""

    # Add framework-specific information
    if project_type == "react":
        content += """

💡 The project includes:
  • React development setup"""
    elif project_type == "vue":
        content += """

💡 The project includes:
  • Vue development setup"""
    else:
        content += """

💡 The project includes:
  • Node.js development setup"""

    content += """
  • Package management (npm)
  • Development tools (ESLint, Prettier, Jest)
  • Git hooks (Husky)
  • VSCode configuration
  • Node.js development setup"""

    # Create and display the panel
    completion_panel = create_success_panel(
        "JavaScript Project Created Successfully!",
        content,
        border_style="bright_green",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)


def _print_generic_new_summary(
    project_path: Path,
    project_name: str,
    project_type: str,  # noqa: ARG001
) -> None:
    """Print generic project creation summary."""
    content = f"""
📁 Project location: {project_path}
📋 Project type: {project_type}

{"=" * 50}

🚀 Next steps:
1. Navigate to project directory:
   cd {project_path}

2. Explore the project structure

3. Read the README.md file

4. Start developing!"""

    # Create and display the panel
    completion_panel = create_success_panel(
        "Project Created Successfully!",
        content,
        border_style="bright_green",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)
