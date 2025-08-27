#!/usr/bin/env python3
"""
Installation commands for WOMM CLI.
Handles installation, uninstallation, and PATH management.
"""

# IMPORTS
########################################################
# Standard library imports
import sys
from pathlib import Path

# Third-party imports
import click

from ..core.managers.installation.installation_manager import InstallationManager
from ..core.managers.installation.uninstallation_manager import UninstallationManager
from ..core.managers.system.user_path_manager import PathManager

# Local imports
from ..core.utils.security.security_validator import security_validator

# COMMAND FUNCTIONS
########################################################
# Main CLI command implementations


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force installation even if .womm directory exists",
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
@click.option(
    "--no-refresh-env",
    is_flag=True,
    help="Skip environment refresh after PATH configuration (Windows only)",
)
def install(force, target, no_refresh_env):
    """🚀 Install Works On My Machine in user directory."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            from ..core.ui.common.console import print_error

            print_error(f"Invalid target path: {error}")
            sys.exit(1)

    try:
        # Use InstallationManager for installation with integrated UI
        manager = InstallationManager()
        manager.install(force=force, target=target, refresh_env=not no_refresh_env)

    except Exception as e:
        from ..core.ui.common.console import print_error

        print_error(f"Installation failed: {e}")
        sys.exit(1)


@click.command()
@click.help_option("-h", "--help")
@click.option(
    "-f", "--force", is_flag=True, help="Force uninstallation without confirmation"
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def uninstall(force, target):
    """🗑️ Uninstall Works On My Machine from user directory."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            from ..core.ui.common.console import print_error

            print_error(f"Invalid target path: {error}")
            sys.exit(1)

    try:
        # Use UninstallationManager for uninstallation with integrated UI
        manager = UninstallationManager(target=target)
        manager.uninstall(force=force)

    except Exception as e:
        from ..core.ui.common.console import print_error

        print_error(f"Uninstallation failed: {e}")
        sys.exit(1)


@click.command("path")
@click.help_option("-h", "--help")
@click.option(
    "-b", "--backup", "backup_flag", is_flag=True, help="Create a PATH backup"
)
@click.option(
    "-r", "--restore", "restore_flag", is_flag=True, help="Restore PATH from backup"
)
@click.option(
    "-l", "--list", "list_flag", is_flag=True, help="List available PATH backups"
)
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def path_cmd(backup_flag, restore_flag, list_flag, target):
    """🧭 PATH utilities: backup, restore, and list backups."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            from ..core.ui.common.console import print_error

            print_error(f"Invalid target path: {error}")
            sys.exit(1)

    # Validate mutually exclusive operations
    selected = sum(bool(x) for x in (backup_flag, restore_flag, list_flag))
    if selected > 1:
        from ..core.ui.common.console import print_error

        print_error("Choose only one action among --backup, --restore, or --list")
        sys.exit(1)
    # Default to list if nothing selected
    if selected == 0:
        list_flag = True

    try:
        manager = PathManager(target=target)

        if list_flag:
            manager.list_backup()
        elif restore_flag:
            manager.restore_path()
        elif backup_flag:
            manager.backup_path()

    except Exception as e:
        from ..core.ui.common.console import print_error

        print_error(f"PATH command error: {e}")
        sys.exit(1)


@click.command("refresh-env")
@click.help_option("-h", "--help")
@click.option(
    "-t",
    "--target",
    type=click.Path(),
    help="Custom target directory (default: ~/.womm)",
)
def refresh_env(target):
    """🔄 Refresh environment variables (Windows only)."""
    # Security validation for target path
    if target:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            from ..core.ui.common.console import print_error

            print_error(f"Invalid target path: {error}")
            sys.exit(1)

    try:
        # Use InstallationManager for environment refresh
        manager = InstallationManager()
        if target:
            manager.target_path = Path(target).expanduser().resolve()

        if manager.platform != "Windows":
            click.echo(
                "[INFO] Environment refresh is only available on Windows", err=True
            )
            sys.exit(0)

        success = manager._refresh_environment()
        if success:
            click.echo("[SUCCESS] Environment variables refreshed successfully")
        else:
            click.echo("[WARNING] Environment refresh completed with warnings")

    except Exception as e:
        from ..core.ui.common.console import print_error

        print_error(f"Environment refresh failed: {e}")
        sys.exit(1)
