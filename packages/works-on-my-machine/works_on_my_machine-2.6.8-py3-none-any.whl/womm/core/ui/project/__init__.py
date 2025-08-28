#!/usr/bin/env python3
"""
Project UI components package.

This package provides UI components for project creation and management,
following the established patterns in the WOMM codebase.
"""

# Import UI components
from .completion_summaries import print_new_project_summary
from .project_wizard import ProjectWizard
from .setup_summaries import print_setup_completion_summary
from .template_ui import (
    interactive_template_create,
    interactive_template_delete,
    print_template_creation_summary,
    print_template_deletion_summary,
    print_template_deletion_summary_multiple,
    print_template_info,
    print_template_list,
)
from .templates.project_configurator import configure_project_options
from .templates.template_selector import display_template_selection

# Export all UI components
__all__ = [
    # Project wizard
    "ProjectWizard",
    # Template components
    "display_template_selection",
    "configure_project_options",
    # Template UI components
    "print_template_list",
    "print_template_info",
    "print_template_creation_summary",
    "print_template_deletion_summary",
    "print_template_deletion_summary_multiple",
    "interactive_template_create",
    "interactive_template_delete",
    # Summary components
    "print_new_project_summary",
    "print_setup_completion_summary",
]
