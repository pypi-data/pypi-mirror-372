#!/usr/bin/env python3
"""
Panel utilities using Rich for beautiful panel output.
"""

# IMPORTS
########################################################
# Standard library imports
from typing import Any, Optional

# Third-party imports
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Local imports
# (None for this file)


# CONFIGURATION
########################################################
# Global variables and settings

console = Console()


# MAIN FUNCTIONS
########################################################
# Core panel creation functionality


def create_panel(
    content: Any,
    title: Optional[str] = None,
    border_style: str = "blue",
    width=80,
    **kwargs,
) -> Panel:
    """Create a Rich panel with the given content."""
    return Panel(content, title=title, border_style=border_style, width=width, **kwargs)


# UTILITY FUNCTIONS
########################################################
# Helper functions for specific panel types


def create_info_panel(
    title: str,
    content: str,
    style: str = "cyan",
    border_style: str = "cyan",
    width=80,
    **kwargs,
) -> Panel:
    """Create an info panel with title and content."""
    text = Text(content, style=style)
    return Panel(
        Align(text, align="left"),
        title=f"ℹ️ {title}",
        border_style=border_style,
        width=width,
        **kwargs,
    )


def create_success_panel(
    title: str, content: str, border_style: str = "green", width=80, **kwargs
) -> Panel:
    """Create a success panel with green styling."""
    text = Text(content, style="green")
    return Panel(
        Align(text, align="left"),
        title=f"✅ {title}",
        border_style=border_style,
        width=width,
        **kwargs,
    )


def create_error_panel(
    title: str, content: str, border_style: str = "red", width=80, **kwargs
) -> Panel:
    """Create an error panel with red styling."""
    text = Text(content, style="red")
    return Panel(
        Align(text, align="left"),
        title=f"❌ {title}",
        border_style=border_style,
        width=width,
        **kwargs,
    )


def create_warning_panel(
    title: str, content: str, border_style: str = "yellow", width=80, **kwargs
) -> Panel:
    """Create a warning panel with yellow styling."""
    text = Text(content, style="yellow")
    return Panel(
        Align(text, align="left"),
        title=f"⚠️ {title}",
        border_style=border_style,
        width=width,
        **kwargs,
    )


def create_installation_panel(
    step: str,
    description: str,
    status: str = "pending",
    border_style: str = "blue",
    width=80,
    **kwargs,
) -> Panel:
    """Create an installation step panel."""
    if status == "success":
        icon = "✅"
        style = "green"
    elif status == "error":
        icon = "❌"
        style = "red"
    elif status == "warning":
        icon = "⚠️"
        style = "yellow"
    else:
        icon = "⏳"
        style = "blue"

    content = f"{description}"
    text = Text(content, style=style)

    return Panel(
        Align(text, align="left"),
        title=f"{icon} {step}",
        border_style=border_style,
        width=width,
        **kwargs,
    )
