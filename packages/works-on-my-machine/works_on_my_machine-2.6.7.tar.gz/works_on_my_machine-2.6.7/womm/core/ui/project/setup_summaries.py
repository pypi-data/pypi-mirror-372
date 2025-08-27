#!/usr/bin/env python3
"""
Setup completion summaries for existing projects.

This module provides UI components for displaying completion summaries
after setting up existing projects, following the established patterns in the WOMM codebase.
"""

from pathlib import Path

from rich.panel import Panel

from ..common.console import console


def print_setup_completion_summary(
    project_path: Path,
    project_type: str,
    virtual_env: bool = False,
    install_deps: bool = False,
    setup_dev_tools: bool = False,
    setup_git_hooks: bool = False,
) -> None:
    """
    Print a completion summary for project setup.

    Args:
        project_path: Path to the project
        project_type: Type of project (python, javascript, react, vue)
        virtual_env: Whether virtual environment was set up
        install_deps: Whether dependencies were installed
        setup_dev_tools: Whether development tools were configured
        setup_git_hooks: Whether Git hooks were set up
    """
    if project_type == "python":
        _print_python_setup_summary(
            project_path, virtual_env, install_deps, setup_dev_tools, setup_git_hooks
        )
    elif project_type in ["javascript", "node", "react", "vue"]:
        _print_javascript_setup_summary(
            project_path, project_type, install_deps, setup_dev_tools, setup_git_hooks
        )
    else:
        _print_generic_setup_summary(
            project_path,
            project_type,
            virtual_env,
            install_deps,
            setup_dev_tools,
            setup_git_hooks,
        )


def _print_python_setup_summary(
    project_path: Path,
    virtual_env: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
) -> None:
    """Print Python project setup summary."""
    # Build content based on what was configured
    content = f"""📁 Project location: {project_path}

==================================================

🔧 Configuration completed:"""

    if virtual_env:
        content += """
  • Virtual environment setup"""

    if install_deps:
        content += """
  • Dependencies installed"""

    if setup_dev_tools:
        content += """
  • Development tools configured"""

    if setup_git_hooks:
        content += """
  • Git hooks configured"""

    content += """

🚀 Next steps:"""

    if virtual_env:
        content += f"""
1. Activate virtual environment:
   {project_path}\\venv\\Scripts\\activate"""

    if install_deps:
        content += """
2. Verify installation:
   pip list"""

    if setup_dev_tools:
        content += """
3. Format code:
   black .
   isort .

4. Lint code:
   flake8 .

5. Run tests:
   pytest"""

    content += f"""

6. Run the project:
   python src/{project_path.name.replace("-", "_")}/main.py"""

    if setup_dev_tools:
        content += """

💡 Available tools:
  • Code formatting (black, isort)
  • Linting (flake8, mypy)
  • Testing (pytest)
  • Pre-commit hooks"""

    # Create and display the panel
    completion_panel = Panel(
        content,
        title="🔧 Python Project Setup Completed!",
        border_style="bright_blue",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)


def _print_javascript_setup_summary(
    project_path: Path,
    project_type: str,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
) -> None:
    """Print JavaScript project setup summary."""
    # Build content based on what was configured
    content = f"""📁 Project location: {project_path}
🟨 Project type: {project_type}

==================================================

🔧 Configuration completed:"""

    if install_deps:
        content += """
  • Dependencies installed"""

    if setup_dev_tools:
        content += """
  • Development tools configured"""

    if setup_git_hooks:
        content += """
  • Git hooks configured"""

    content += """

🚀 Next steps:"""

    if install_deps:
        content += """
1. Verify installation:
   npm list"""

    if setup_dev_tools:
        content += """
2. Lint code:
   npm run lint

3. Format code:
   npm run format

4. Run tests:
   npm test"""

    content += """

5. Start development server:
   npm start

6. Build project:
   npm run build"""

    if setup_dev_tools:
        content += """

💡 Available tools:
  • Code formatting (Prettier)
  • Linting (ESLint)
  • Testing (Jest)
  • Git hooks (Husky)"""

    # Create and display the panel
    completion_panel = Panel(
        content,
        title="🔧 JavaScript Project Setup Completed!",
        border_style="bright_blue",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)


def _print_generic_setup_summary(
    project_path: Path,
    project_type: str,
    virtual_env: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
) -> None:
    """Print generic project setup summary."""
    # Build content based on what was configured
    content = f"""📁 Project location: {project_path}
📋 Project type: {project_type}

==================================================

🔧 Configuration completed:"""

    if virtual_env:
        content += """
  • Virtual environment setup"""

    if install_deps:
        content += """
  • Dependencies installed"""

    if setup_dev_tools:
        content += """
  • Development tools configured"""

    if setup_git_hooks:
        content += """
  • Git hooks configured"""

    content += """

🚀 Next steps:
1. Navigate to project directory:
   cd {project_path}

2. Explore the project structure

3. Read the README.md file

4. Start developing!"""

    # Create and display the panel
    completion_panel = Panel(
        content,
        title="🔧 Project Setup Completed!",
        border_style="bright_blue",
        width=80,
        padding=(1, 1),
    )

    console.print("")
    console.print(completion_panel)
