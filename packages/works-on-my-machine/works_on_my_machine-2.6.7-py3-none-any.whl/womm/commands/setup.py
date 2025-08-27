#!/usr/bin/env python3
"""
Setup commands for WOMM CLI.
Handles configuration of existing projects using the modular architecture.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from ..core.managers.project import ProjectManager
from ..core.ui.common.console import print_error, print_info, print_success
from ..core.ui.project import ProjectWizard
from ..core.utils.project.project_detector import ProjectDetector


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def setup_group(ctx):
    """🔧 Configure existing projects with development tools."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@setup_group.command("detect")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the project directory",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
def setup_detect(
    project_path: Path,
    interactive: bool,
):
    """🔍 Auto-detect project type and configure development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Detect project type
        detector = ProjectDetector(project_path)
        detected_type, confidence = detector.detect_project_type()

        if detected_type == "unknown" or confidence < 20:
            print_error("No suitable project type detected in the specified directory")
            print_info("Supported project types: python, javascript, react, vue")
            sys.exit(1)

        print_success(
            f"Detected project type: {detected_type} (confidence: {confidence}%)"
        )

        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, detected_type, project_path)

        # Non-interactive mode
        return _run_direct_setup(project_manager, detected_type, project_path)

    except Exception as e:
        print_error(f"Error detecting project type: {e}")
        sys.exit(1)


@setup_group.command("python")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the Python project directory",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--virtual-env",
    is_flag=True,
    help="Create virtual environment",
)
@click.option(
    "--install-deps",
    is_flag=True,
    help="Install dependencies",
)
@click.option(
    "--setup-dev-tools",
    is_flag=True,
    help="Setup development tools (linting, formatting, etc.)",
)
@click.option(
    "--setup-git-hooks",
    is_flag=True,
    help="Setup Git hooks",
)
def setup_python(
    project_path: Path,
    interactive: bool,
    virtual_env: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
):
    """🐍 Configure existing Python project with development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, "python", project_path)

        # Non-interactive mode
        options = {
            "virtual_env": virtual_env,
            "install_deps": install_deps,
            "setup_dev_tools": setup_dev_tools,
            "setup_git_hooks": setup_git_hooks,
        }
        return _run_direct_setup(project_manager, "python", project_path, options)

    except Exception as e:
        print_error(f"Error configuring Python project: {e}")
        sys.exit(1)


@setup_group.command("javascript")
@click.help_option("-h", "--help")
@click.option(
    "-p",
    "--path",
    "project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Path to the JavaScript project directory",
)
@click.option(
    "-t",
    "--type",
    "project_type",
    type=click.Choice(["node", "react", "vue"]),
    help="JavaScript project type (auto-detected if not specified)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--install-deps",
    is_flag=True,
    help="Install dependencies",
)
@click.option(
    "--setup-dev-tools",
    is_flag=True,
    help="Setup development tools (linting, formatting, etc.)",
)
@click.option(
    "--setup-git-hooks",
    is_flag=True,
    help="Setup Git hooks",
)
def setup_javascript(
    project_path: Path,
    project_type: Optional[str],
    interactive: bool,
    install_deps: bool,
    setup_dev_tools: bool,
    setup_git_hooks: bool,
):
    """🟨 Configure existing JavaScript project with development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Auto-detect type if not specified
        if not project_type:
            detector = ProjectDetector(project_path)
            detected_type, confidence = detector.detect_project_type()
            if detected_type in ["javascript", "react", "vue"]:
                project_type = detected_type
            else:
                print_error("Could not auto-detect JavaScript project type")
                print_info("Please specify --type (node, react, vue)")
                sys.exit(1)

        # Interactive mode
        if interactive:
            return _run_interactive_setup(project_manager, project_type, project_path)

        # Non-interactive mode
        options = {
            "install_deps": install_deps,
            "setup_dev_tools": setup_dev_tools,
            "setup_git_hooks": setup_git_hooks,
        }
        return _run_direct_setup(project_manager, project_type, project_path, options)

    except Exception as e:
        print_error(f"Error configuring JavaScript project: {e}")
        sys.exit(1)


# Helper functions for interactive modes
def _run_interactive_setup(
    project_manager: ProjectManager, project_type: str, project_path: Path
) -> int:
    """Run interactive project setup."""
    # Get setup configuration
    config = ProjectWizard.run_interactive_setup_for_existing_project(
        project_type, project_path
    )
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Configure project
    success = project_manager.setup_project(
        project_type=project_type,
        project_path=project_path,
        **config.get("options", {}),
    )

    if success:
        return 0
    else:
        print_error(f"Failed to configure {project_type} project")
        return 1


# Helper functions for direct modes
def _run_direct_setup(
    project_manager: ProjectManager,
    project_type: str,
    project_path: Path,
    options: Optional[dict] = None,
) -> int:
    """Run direct project setup."""

    if options is None:
        options = {}

    # Configure project
    success = project_manager.setup_project(
        project_type=project_type,
        project_path=project_path,
        **options,
    )

    if success:
        return 0
    else:
        print_error(f"Failed to configure {project_type} project")
        return 1
