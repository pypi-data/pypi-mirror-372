#!/usr/bin/env python3
"""
System commands for WOMM CLI.
Handles system detection and prerequisites installation.
"""

# IMPORTS
########################################################
# Standard library imports

# Third-party imports
import click

# Local imports
# (None for this file)


# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def system_group(ctx):
    """🔧 System detection and prerequisites."""
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# COMMAND FUNCTIONS
########################################################
# Command implementations


@system_group.command("detect")
@click.help_option("-h", "--help")
def system_detect():
    """🔍 Detect system information and available tools."""
    # Lazy import to avoid slow startup
    from ..core.managers.system import SystemManager

    # Use SystemManager for system detection with integrated UI
    system_manager = SystemManager()
    system_manager.detect_system()


@system_group.command("install")
@click.help_option("-h", "--help")
@click.option(
    "-c",
    "--check",
    is_flag=True,
    help="Only check prerequisites",
)
@click.option(
    "-p",
    "--pm-args",
    help="Extra arguments passed to the package manager (quoted string)",
    multiple=True,
)
@click.option(
    "-a",
    "--ask-path",
    is_flag=True,
    help="Interactively ask for an installation path (best-effort, Windows only)",
)
@click.argument("tools", nargs=-1, type=click.Choice(["python", "node", "git", "all"]))
def system_install(check, pm_args, ask_path, tools):
    """📦 Install system prerequisites."""
    # Lazy import to avoid slow startup
    from ..core.managers.system import SystemManager

    # Use SystemManager for prerequisites management with integrated UI
    system_manager = SystemManager()
    if check:
        system_manager.check_prerequisites(list(tools))
    else:
        # Flatten pm_args (Click multiple=True yields a tuple of strings)
        extra_args = [a for a in pm_args if a]
        system_manager.install_prerequisites(
            list(tools), pm_args=extra_args, ask_path=ask_path
        )
