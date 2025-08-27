#!/usr/bin/env python3
"""
Template selector UI components.

This module provides UI components for template selection and management,
following the established patterns in the WOMM codebase.
"""

from typing import List, Optional

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

from ...common.console import print_info
from ...interactive import InteractiveMenu


def display_template_selection(
    templates: List[str], project_type: str
) -> Optional[str]:
    """
    Display interactive template selection menu.

    Args:
        templates: List of available template names
        project_type: Type of project (python, javascript, etc.)

    Returns:
        Selected template name or None if cancelled
    """
    if not templates:
        print_info(f"No templates available for {project_type} projects")
        return None

    print_info(f"📋 Available templates for {project_type} projects:")
    print_info("=" * 50)

    if INQUIRERPY_AVAILABLE:
        choices = [Choice(value=template, name=template) for template in templates]
        selected = inquirer.select(
            message="Select a template:",
            choices=choices,
            pointer="→",
        ).execute()
        return selected
    else:
        # Fallback to simple menu
        menu = InteractiveMenu("Select a template:")
        items = [{"name": template, "description": template} for template in templates]
        selected = menu.select_from_list(items, display_func=lambda x: x["description"])
        return selected["name"] if selected else None
