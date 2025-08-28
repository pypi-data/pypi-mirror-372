#!/usr/bin/env python3
"""
New project commands for WOMM CLI.
Handles creation of new Python and JavaScript projects using the modular architecture.
"""

import sys
from typing import Optional

import click

from ..core.managers.project import ProjectManager
from ..core.ui.common.console import print_error, print_header
from ..core.ui.project import ProjectWizard
from ..core.utils.security.security_validator import validate_user_input


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def new_group(ctx):
    """🆕 Create new projects with modern development setup."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@new_group.command("python")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "-t",
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--author-name",
    help="Author name for the project",
)
@click.option(
    "--author-email",
    help="Author email for the project",
)
@click.option(
    "--project-url",
    help="Project URL",
)
@click.option(
    "--project-repository",
    help="Project repository URL",
)
def new_python(
    project_name: Optional[str],
    current_dir: bool,
    target: Optional[str],
    interactive: bool,
    author_name: Optional[str],
    author_email: Optional[str],
    project_url: Optional[str],
    project_repository: Optional[str],
):
    """🐍 Create a new Python project with full development environment."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            return _run_interactive_python_setup(project_manager)

        # Non-interactive mode
        return _run_direct_python_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            author_name,
            author_email,
            project_url,
            project_repository,
        )

    except Exception as e:
        print_error(f"Error creating Python project: {e}")
        sys.exit(1)


@new_group.command("javascript")
@click.help_option("-h", "--help")
@click.argument("project_name", required=False)
@click.option(
    "-c",
    "--current-dir",
    is_flag=True,
    help="Use current directory instead of creating a new one",
)
@click.option(
    "-t",
    "--target",
    help="Target directory where to create the project (default: current directory)",
)
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["node", "react", "vue"]),
    default="node",
    help="JavaScript project type",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Run in interactive mode with guided setup",
)
@click.option(
    "--author-name",
    help="Author name for the project",
)
@click.option(
    "--author-email",
    help="Author email for the project",
)
@click.option(
    "--project-url",
    help="Project URL",
)
@click.option(
    "--project-repository",
    help="Project repository URL",
)
def new_javascript(
    project_name: Optional[str],
    current_dir: bool,
    target: Optional[str],
    project_type: str,
    interactive: bool,
    author_name: Optional[str],
    author_email: Optional[str],
    project_url: Optional[str],
    project_repository: Optional[str],
):
    """🟨 Create a new JavaScript/Node.js project with development tools."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Interactive mode
        if interactive:
            return _run_interactive_javascript_setup(project_manager)

        # Non-interactive mode
        return _run_direct_javascript_setup(
            project_manager,
            project_name,
            current_dir,
            target,
            project_type,
            author_name,
            author_email,
            project_url,
            project_repository,
        )

    except Exception as e:
        print_error(f"Error creating JavaScript project: {e}")
        sys.exit(1)


# Helper functions for interactive modes
def _run_interactive_python_setup(project_manager: ProjectManager) -> int:
    """Run interactive Python project setup."""
    print_header("🐍 Interactive Python Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Create project
    success = project_manager.create_project(
        project_type="python",
        project_name=config.get("project_name"),
        target=str(config.get("project_path").parent),
        **config.get("options", {}),
    )

    if success:
        return 0
    else:
        return 1


def _run_interactive_javascript_setup(project_manager: ProjectManager) -> int:
    """Run interactive JavaScript project setup."""
    print_header("🟨 Interactive JavaScript Project Setup")

    # Get project configuration
    config = ProjectWizard.run_interactive_setup()
    if not config:
        print_error("Project setup cancelled")
        return 1

    # Determine the project type based on configuration
    js_project_type = config.get("project_type", "node")

    # Map the project type to the correct ProjectManager type
    if js_project_type in ["react", "vue"]:
        pm_project_type = js_project_type  # Use directly: "react" or "vue"
    else:
        pm_project_type = "javascript"  # Use "javascript" for node, library, cli

    # Prepare options
    options = config.get("options", {})

    # Add project_type to options only when using "javascript" as main type
    # and it's not already in options
    if pm_project_type == "javascript" and "project_type" not in options:
        options["project_type"] = js_project_type

    # Remove project_type from options to avoid conflict with create_project parameter
    options.pop("project_type", None)

    # Create project
    success = project_manager.create_project(
        project_type=pm_project_type,
        project_name=config.get("project_name"),
        target=str(config.get("project_path").parent),
        **options,
    )

    if success:
        return 0
    else:
        return 1


# Helper functions for direct modes
def _run_direct_python_setup(
    project_manager: ProjectManager,
    project_name: Optional[str],
    current_dir: bool,
    target: Optional[str],
    author_name: Optional[str],
    author_email: Optional[str],
    project_url: Optional[str],
    project_repository: Optional[str],
) -> int:
    """Run direct Python project setup."""

    # Validate project name if provided
    if project_name and not current_dir:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            print_error(f"Invalid project name: {error}")
            return 1

    # Prepare options
    options = {}
    if author_name:
        options["author_name"] = author_name
    if author_email:
        options["author_email"] = author_email
    if project_url:
        options["project_url"] = project_url
    if project_repository:
        options["project_repository"] = project_repository
    if target:
        options["target"] = target

    # Create project
    success = project_manager.create_project(
        project_type="python",
        project_name=project_name,
        current_dir=current_dir,
        **options,
    )

    if success:
        return 0
    else:
        return 1


def _run_direct_javascript_setup(
    project_manager: ProjectManager,
    project_name: Optional[str],
    current_dir: bool,
    target: Optional[str],
    project_type: str,
    author_name: Optional[str],
    author_email: Optional[str],
    project_url: Optional[str],
    project_repository: Optional[str],
) -> int:
    """Run direct JavaScript project setup."""

    # Validate project name if provided
    if project_name and not current_dir:
        is_valid, error = validate_user_input(project_name, "project_name")
        if not is_valid:
            print_error(f"Invalid project name: {error}")
            return 1

    # Prepare options
    options = {}
    if author_name:
        options["author_name"] = author_name
    if author_email:
        options["author_email"] = author_email
    if project_url:
        options["project_url"] = project_url
    if project_repository:
        options["project_repository"] = project_repository
    if target:
        options["target"] = target

    # Create project
    # Map CLI types to ProjectManager types
    pm_project_type = "javascript" if project_type == "node" else project_type

    success = project_manager.create_project(
        project_type=pm_project_type,
        project_name=project_name,
        current_dir=current_dir,
        **options,
    )

    if success:
        return 0
    else:
        return 1
