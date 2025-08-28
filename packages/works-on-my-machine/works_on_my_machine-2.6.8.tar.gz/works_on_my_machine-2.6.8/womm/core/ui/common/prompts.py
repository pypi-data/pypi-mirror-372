#!/usr/bin/env python3
"""
Prompt utilities using Rich for beautiful user prompts.
"""

# IMPORTS
########################################################
# Standard library imports
from typing import List, Optional

# Third-party imports
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.text import Text

# Local imports
# (None for this file)


# CONFIGURATION
########################################################
# Global variables and settings

console = Console()


# MAIN FUNCTIONS
########################################################
# Core prompt functionality


def confirm(message: str, default: bool = False, show_default: bool = True) -> bool:
    """Show a confirmation prompt."""
    return Confirm.ask(message, default=default, show_default=show_default)


def prompt_choice(
    message: str, choices: List[str], default: Optional[str] = None
) -> str:
    """Show a choice prompt with options."""
    console.print(f"\n{message}")

    for i, choice in enumerate(choices, 1):
        console.print(f"  {i}. {choice}")

    while True:
        try:
            choice_num = IntPrompt.ask(
                "Enter your choice",
                default=choices.index(default) + 1 if default else None,
            )

            if 1 <= choice_num <= len(choices):
                return choices[choice_num - 1]
            else:
                console.print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            console.print("Please enter a valid number")


def prompt_text(
    message: str, default: Optional[str] = None, password: bool = False
) -> str:
    """Show a text input prompt."""
    return Prompt.ask(message, default=default, password=password)


def prompt_path(message: str, default: Optional[str] = None) -> str:
    """Show a path input prompt."""
    return Prompt.ask(message, default=default)


# UTILITY FUNCTIONS
########################################################
# Helper functions for panel-based prompts


def show_info_panel(title: str, content: str, style: str = "cyan") -> None:
    """Show an info panel."""
    panel = Panel(Text(content, style=style), title=f"ℹ️ {title}", border_style=style)
    console.print(panel)


def show_warning_panel(title: str, content: str, width: int = 80) -> None:
    """Show a warning panel."""
    panel = Panel(
        Text(content, style="yellow"),
        title=f"⚠️ {title}",
        border_style="yellow",
        width=width,
        padding=(1, 1),
    )
    console.print(panel)


def show_error_panel(title: str, content: str, width: int = 80) -> None:
    """Show an error panel."""
    panel = Panel(
        Text(content, style="red"),
        title=f"❌ {title}",
        border_style="red",
        width=width,
        padding=(1, 1),
    )
    console.print(panel)


def print_prompt(
    message: str, required: bool = False, default: Optional[str] = None
) -> str:
    """Show a prompt and return user input."""
    while True:
        result = prompt_text(message, default=default)
        if result or not required:
            return result
        console.print("❌ Cette valeur est requise. Veuillez réessayer.", style="red")
