#!/usr/bin/env python3
"""
Template commands for WOMM CLI.
Handles template generation from existing projects and template management.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from ..core.managers.project import ProjectManager
from ..core.ui.common.console import print_error, print_header, print_info
from ..core.ui.project import (
    interactive_template_create,
    interactive_template_delete,
    print_template_deletion_summary_multiple,
    print_template_info,
    print_template_list,
)
from ..core.utils.security.security_validator import validate_user_input


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def template_group(ctx):
    """📋 Generate and manage project templates from existing projects."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@template_group.command("list")
@click.help_option("-h", "--help")
def template_list():
    """📋 List available project templates."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        print_header("📋 Template List")
        return _list_templates(project_manager)

    except Exception as e:
        print_error(f"Error listing templates: {e}")
        sys.exit(1)


@template_group.command("create")
@click.help_option("-h", "--help")
@click.argument("template_name", required=False)
@click.option(
    "--from-project",
    "source_project_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Path to the existing project to create template from",
)
@click.option(
    "--description",
    help="Description for the template",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Use interactive mode to create template",
)
def template_create(
    template_name: Optional[str],
    source_project_path: Optional[Path],
    description: Optional[str],
    interactive: bool,
):
    """🚀 Create a new template from an existing project.

    If TEMPLATE_NAME is not provided, it will be automatically generated
    based on the project type and name.

    Use --interactive for guided template creation.
    """

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        if interactive:
            print_header("🚀 Interactive Template Creation")
            return _create_template_interactive(project_manager)
        else:
            print_header("🚀 Template Creation")
            return _create_template_direct(
                project_manager, template_name, source_project_path, description
            )

    except Exception as e:
        print_error(f"Error creating template: {e}")
        sys.exit(1)


@template_group.command("use")
@click.help_option("-h", "--help")
@click.argument("template_name")
@click.option(
    "-p",
    "--path",
    "target_path",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=".",
    help="Target directory for the generated project",
)
@click.option(
    "--project-name",
    help="Project name for the generated project",
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
def template_use(
    template_name: str,
    target_path: Path,
    project_name: Optional[str],
    author_name: Optional[str],
    author_email: Optional[str],
    project_url: Optional[str],
    project_repository: Optional[str],
):
    """🎯 Use a template to create a new project."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        # Prepare template variables
        template_vars = {}
        if project_name:
            template_vars["PROJECT_NAME"] = project_name
        if author_name:
            template_vars["AUTHOR_NAME"] = author_name
        if author_email:
            template_vars["AUTHOR_EMAIL"] = author_email
        if project_url:
            template_vars["PROJECT_URL"] = project_url
        if project_repository:
            template_vars["PROJECT_REPOSITORY"] = project_repository

        # Generate project from template
        success = project_manager.template_manager.generate_from_template(
            template_name=template_name,
            target_path=target_path,
            template_vars=template_vars,
        )

        if success:
            return 0
        else:
            return 1

    except Exception as e:
        print_error(f"Error using template: {e}")
        sys.exit(1)


@template_group.command("delete")
@click.help_option("-h", "--help")
@click.argument("template_name", required=False)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Use interactive mode to delete templates",
)
def template_delete(template_name: Optional[str], interactive: bool):
    """🗑️ Delete a template.

    Use --interactive for guided template deletion with multiple selection.
    """
    # Initialize project manager
    project_manager = ProjectManager()

    try:
        if interactive:
            print_header("🗑️ Interactive Template Deletion")
            return _delete_template_interactive(project_manager)
        else:
            print_header("🗑️ Template Deletion")
            if not template_name:
                print_error("Template name is required when not using interactive mode")
                return 1
            return _delete_template(project_manager, template_name)

    except Exception as e:
        print_error(f"Error deleting template: {e}")
        sys.exit(1)


@template_group.command("info")
@click.help_option("-h", "--help")
@click.argument("template_name")
def template_info(template_name: str):
    """ℹ️ Show information about a template."""

    # Initialize project manager
    project_manager = ProjectManager()

    try:
        print_header(f"ℹ️ Template Info: {template_name}")
        return _show_template_info(project_manager, template_name)

    except Exception as e:
        print_error(f"Error getting template info: {e}")
        sys.exit(1)


# Helper functions
def _generate_template_name(
    source_project_path: Path, project_manager: ProjectManager
) -> str:
    """
    Generate a template name based on the source project.

    Args:
        source_project_path: Path to the source project
        project_manager: Project manager instance

    Returns:
        Generated template name
    """
    # Get project name from path
    project_name = source_project_path.name.lower()

    # Clean project name (remove special characters, replace spaces with hyphens)
    import re

    clean_name = re.sub(r"[^a-zA-Z0-9_-]", "-", project_name)
    clean_name = re.sub(r"-+", "-", clean_name)  # Replace multiple hyphens with single
    clean_name = clean_name.strip("-")  # Remove leading/trailing hyphens

    # Detect project type
    project_type = project_manager.template_manager._detect_project_type(
        source_project_path
    )

    # Generate template name
    if project_type != "unknown":
        template_name = f"{project_type}-{clean_name}"
    else:
        template_name = clean_name

    # Ensure uniqueness
    existing_templates = project_manager.template_manager.list_templates()
    all_template_names = []
    for templates in existing_templates.values():
        all_template_names.extend(templates)

    base_name = template_name
    counter = 1
    while template_name in all_template_names:
        template_name = f"{base_name}-{counter}"
        counter += 1

    return template_name


def _list_templates(project_manager: ProjectManager) -> int:
    """List available templates."""
    all_templates = project_manager.template_manager.list_templates()
    print_template_list(all_templates)
    return 0


def _show_template_info(project_manager: ProjectManager, template_name: str) -> int:
    """Show detailed information about a template."""
    template_info = project_manager.template_manager.get_template_info(template_name)

    if not template_info:
        print_error(f"Template '{template_name}' not found")
        return 1

    print_template_info(template_name, template_info)
    return 0


def _create_template_interactive(project_manager: ProjectManager) -> int:
    """Create template using interactive form."""

    # Get user input through interactive form
    answers = interactive_template_create()

    if not answers:
        print_info("Template creation cancelled.")
        return 0

    # Validate template name
    is_valid, error = validate_user_input(answers["template_name"], "template_name")
    if not is_valid:
        print_error(f"Invalid template name: {error}")
        return 1

    # Create template from project
    success = project_manager.template_manager.create_template_from_project(
        source_project_path=Path(answers["source_project"]),
        template_name=answers["template_name"],
        description=answers["description"],
    )

    if success:
        return 0
    else:
        return 1


def _create_template_direct(
    project_manager: ProjectManager,
    template_name: Optional[str],
    source_project_path: Optional[Path],
    description: Optional[str],
) -> int:
    """Create template using direct parameters."""
    if not source_project_path:
        print_error("Source project path is required when not using interactive mode")
        return 1

    # Generate template name if not provided
    if not template_name:
        template_name = _generate_template_name(source_project_path, project_manager)
        print_info(f"Generated template name: {template_name}")

    # Validate template name
    is_valid, error = validate_user_input(template_name, "template_name")
    if not is_valid:
        print_error(f"Invalid template name: {error}")
        return 1

    # Create template from project
    success = project_manager.template_manager.create_template_from_project(
        source_project_path=source_project_path,
        template_name=template_name,
        description=description,
    )

    if success:
        return 0
    else:
        return 1


def _delete_template_interactive(project_manager: ProjectManager) -> int:
    """Delete templates using interactive form."""

    # Get available templates
    all_templates = project_manager.template_manager.list_templates()

    # Get user input through interactive form
    selected_templates = interactive_template_delete(all_templates)

    if not selected_templates:
        print_info("Template deletion cancelled.")
        return 0

    # Delete selected templates
    success_count = 0
    failed_templates = []

    for template_name in selected_templates:
        success = project_manager.template_manager.delete_template(
            template_name, show_summary=False
        )
        if success:
            success_count += 1
        else:
            failed_templates.append(template_name)

    # Display summary using Rich panel
    print_template_deletion_summary_multiple(selected_templates, failed_templates)

    if success_count == len(selected_templates):
        return 0
    else:
        return 1


def _delete_template(project_manager: ProjectManager, template_name: str) -> int:
    """Delete a single template."""
    success = project_manager.template_manager.delete_template(template_name)

    if success:
        return 0
    else:
        return 1
