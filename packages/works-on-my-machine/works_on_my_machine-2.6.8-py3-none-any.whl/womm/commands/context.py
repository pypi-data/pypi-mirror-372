#!/usr/bin/env python3
"""
Context menu commands for WOMM CLI.
Handles Windows context menu management.
"""

# IMPORTS
########################################################
# External modules and dependencies

import platform
from pathlib import Path

import click

# IMPORTS
########################################################
# Internal modules and dependencies
from rich import print

from ..core.managers.installation.installation_manager import get_target_womm_path
from ..core.ui.common.console import (
    LogLevel,
    print_error,
    print_header,
    print_info,
    print_pattern,
    print_success,
)
from ..core.ui.common.panels import create_panel
from ..core.ui.common.progress import create_spinner_with_status
from ..core.ui.interactive import InteractiveMenu

# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def _check_windows_only() -> bool:
    """Check if running on Windows and display appropriate message."""
    if platform.system().lower() != "windows":
        print_info("Context menu management is Windows-specific")
        print_info("Consider using symbolic links or aliases on Unix systems")
        return False
    return True


# Legacy functions removed - now using ContextMenuManager directly


def _get_backup_directory() -> str:
    """Get the appropriate directory for backups."""
    try:
        womm_path = get_target_womm_path()
        if womm_path.exists():
            backup_dir = womm_path / ".backup" / "context_menu"
            backup_dir.mkdir(parents=True, exist_ok=True)
            return str(backup_dir)
    except Exception as e:
        print_pattern(
            LogLevel.DEBUG, "SYSTEM", f"Could not access WOMM backup directory: {e}"
        )

    # Fallback to current directory
    return "."


# Legacy functions removed - now using ContextMenuManager directly


def _show_tip_panel(content: str, title: str = "Tip"):
    """Show a tip panel with consistent formatting."""
    tip_panel = create_panel(
        content,
        title=title,
        border_style="yellow",
        style="bright_yellow",
        padding=(1, 1),
        width=80,
    )
    print("")
    print(tip_panel)
    print("")


# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.pass_context
def context_group(ctx):
    """Windows context menu management."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# COMMAND FUNCTIONS
########################################################
# Command implementations


@context_group.command("register")
@click.help_option("-h", "--help")
@click.option(
    "-t",
    "--target",
    "target_path",
    type=click.Path(),
    help="Script or executable to register in context menu",
)
@click.option(
    "-l",
    "--label",
    help="Label to display in context menu",
)
@click.option(
    "--icon",
    default="auto",
    help="Icon path or 'auto' for auto-detection (default: auto)",
)
@click.option(
    "--root",
    is_flag=True,
    help="Register for root directories (drives) only",
)
@click.option(
    "--file",
    is_flag=True,
    help="Register for single file selection",
)
@click.option(
    "--files",
    is_flag=True,
    help="Register for multiple file selection",
)
@click.option(
    "--background",
    is_flag=True,
    help="Register for background context only",
)
@click.option(
    "--file-types",
    multiple=True,
    help="File types to register for (e.g., image, text, archive)",
)
@click.option(
    "--extension",
    "extensions",
    multiple=True,
    help="Custom file extensions (e.g., .py, .js)",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode - guided setup",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_register(
    target_path,
    label,
    icon,
    root,
    file,
    files,
    background,
    file_types,
    extensions,
    dry_run,
    interactive,
    verbose,
):
    """📝 Register scripts in Windows context menu."""
    if not _check_windows_only():
        return

    print_header("📝 Context Menu Registration")

    # Handle interactive mode
    if interactive:
        from ..core.ui.context.interactive_wizard import ContextMenuWizard

        target_path, label, icon, context_params = ContextMenuWizard.run_setup()
        if not target_path:  # User cancelled
            return
    else:
        # Validate required parameters in non-interactive mode
        if not target_path:
            print_error("Missing required option: --target")
            print_info("Use --interactive for guided setup")
            return
        if not label:
            print_error("Missing required option: --label")
            print_info("Use --interactive for guided setup")
            return

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    # Create context parameters from flags
    from ..core.managers.context.utils.context_parameters import ContextParameters

    context_params = ContextParameters.from_flags(
        root=root,
        file=file,
        files=files,
        background=background,
        file_types=list(file_types) if file_types else None,
        extensions=list(extensions) if extensions else None,
    )

    if verbose:
        print_info(f"Target: {target_path}")
        print_info(f"Label: {label}")
        print_info(f"Icon: {icon}")
        print_info(f"Context: {context_params.get_description()}")

    # Validation will be done in register_script()
    if verbose:
        print_info("Validating script and parameters...")

    # Create backup before registration
    if not dry_run:
        backup_dir = _get_backup_directory()
        backup_file = f"{backup_dir}/context_menu_backup_before_register.json"

        with create_spinner_with_status("Creating backup before registration...") as (
            progress,
            task,
        ):
            progress.update(task, status="Creating backup...")
            backup_result = manager.backup_entries(backup_file)

        if not backup_result["success"]:
            print_error(f"Backup failed: {backup_result['error']}")
            return

        if verbose:
            print_info(f"Backup created: {backup_file}")

    # Register script
    with create_spinner_with_status("Registering script in context menu...") as (
        progress,
        task,
    ):
        progress.update(task, status="Adding registry entries...")
        result = manager.register_script(
            target_path, label, icon, dry_run, context_params
        )

    if result["success"]:
        info = result["info"]

        if dry_run:
            print_info("🔧 Would add to Windows Context Menu")
            print_info(f"📜 Script: {info['script_path']}")
            print_info(f"🎯 Type: {info['script_type']}")
            print_info(f"🏷️  Title: {info['label']}")
            print_info(f"🎨 Icon: {info['icon_path'] or 'Default file icon'}")
            print_info(f"🔑 Registry Key: {info['registry_key']}")
            print_info(f"⚡ Command: {info['command']}")
            print_info(f"🎯 Context: {context_params.get_description()}")
            print_info("\n🔍 Dry run mode - no changes made")
            print_success("✅ Configuration validated successfully")
        else:
            # Import UI and show success message
            from ..core.ui.context.context import ContextMenuUI

            ui = ContextMenuUI()
            ui.show_register_success(label, info["registry_key"])

    else:
        print_error(f"Registration failed: {result['error']}")
        if verbose and "info" in result:
            info = result["info"]
            print_info(f"Script path: {info.get('script_path')}")
            print_info(f"Script type: {info.get('script_type')}")
            print_info(f"Registry key: {info.get('registry_key')}")


@context_group.command("unregister")
@click.help_option("-h", "--help")
@click.option(
    "--remove",
    "remove_key",
    required=True,
    help="Key name to remove (as stored in registry)",
)
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_unregister(remove_key, dry_run, verbose):
    """🗑️ Unregister scripts from Windows context menu."""
    if not _check_windows_only():
        return

    print_header("🗑️ Context Menu Unregistration")

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    if verbose:
        print_info(f"Removing key: {remove_key}")

    # Unregister script
    with create_spinner_with_status("Unregistering script from context menu...") as (
        progress,
        task,
    ):
        progress.update(task, status="Removing registry entries...")
        result = manager.unregister_script(remove_key, dry_run)

    if result["success"]:
        if dry_run:
            print_info(f"🔍 Would remove context menu entry: {remove_key}")
            print_success("✅ Dry run completed successfully")
        else:
            # Import UI and show success message
            from ..core.ui.context.context import ContextMenuUI

            ui = ContextMenuUI()
            ui.show_unregister_success(remove_key)

    else:
        print_error(f"Unregistration failed: {result['error']}")


@context_group.command("list")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_list(verbose):  # noqa: ARG001
    """📋 List registered context menu entries."""
    if not _check_windows_only():
        return

    print_header("📋 Context Menu List")

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    # List entries
    with create_spinner_with_status("Retrieving context menu entries...") as (
        progress,
        task,
    ):
        progress.update(task, status="Reading registry entries...")
        result = manager.list_entries()

    if result["success"]:
        entries = result["entries"]

        print("📋 Context Menu Entries:")
        print("=" * 50)

        for context_type in ["directory", "background"]:
            print(f"\n{context_type.upper()} CONTEXT:")
            context_entries = entries.get(context_type, [])

            if not context_entries:
                print("  No entries found")
            else:
                for entry in context_entries:
                    print(f"  Key: {entry['key_name']}")
                    print(f"    Display: {entry['display_name']}")
                    if entry["command"]:
                        print(f"    Command: {entry['command']}")
                    if entry["icon"]:
                        print(f"    Icon: {entry['icon']}")
                    print()

        # Import UI and show commands panel
        from ..core.ui.context.context import ContextMenuUI

        ui = ContextMenuUI()
        ui.show_list_commands()

    else:
        print_error(f"Failed to retrieve context menu entries: {result['error']}")


@context_group.command("quick-setup")
@click.help_option("-h", "--help")
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Show commands without executing",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_quick_setup(dry_run, verbose):
    """⚡ Quick setup common WOMM tools in context menu."""
    if not _check_windows_only():
        return

    print_header("⚡ Quick Setup Common WOMM Tools")

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    # Common WOMM tools to register
    tools = [
        {
            "target": "womm.py",
            "label": "WOMM CLI",
            "description": "Main WOMM command-line interface",
        },
        # Add more tools as needed
    ]

    success_count = 0
    total_tools = len(tools)

    with create_spinner_with_status("Setting up common WOMM tools...") as (
        progress,
        task,
    ):
        for i, tool in enumerate(tools, 1):
            progress.update(
                task, status=f"Registering {tool['description']} ({i}/{total_tools})..."
            )
            if verbose:
                print_info(f"Registering: {tool['description']}")

            # Register using ContextMenuManager
            result = manager.register_script(
                tool["target"], tool["label"], "auto", dry_run
            )

            if result["success"]:
                success_count += 1
                if verbose:
                    print_success(f"Registered: {tool['label']}")
            else:
                if verbose:
                    print_error(
                        f"Failed to register: {tool['label']} - {result['error']}"
                    )

    if not dry_run:
        if success_count == total_tools:
            print_success(f"All {total_tools} WOMM tools registered successfully!")
            print_info("Right-click in any folder to access WOMM tools")
        else:
            print_info(f"Registered {success_count}/{total_tools} tools successfully")
    else:
        print_info(f"Would register {total_tools} WOMM tools")


@context_group.command("status")
@click.help_option("-h", "--help")
def context_status():
    """📊 Show context menu registration status (Windows only)."""
    if not _check_windows_only():
        return

    print_header("📊 Context Menu Status")

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    # Get context menu entries
    with create_spinner_with_status("Checking context menu registration status...") as (
        progress,
        task,
    ):
        progress.update(task, status="Retrieving context menu entries...")
        result = manager.list_entries()

    if result["success"]:
        entries = result["entries"]
        total_entries = sum(
            len(entries.get(context_type, []))
            for context_type in ["directory", "background"]
        )

        print_success(f"Found {total_entries} context menu entries")

        # Show helpful information panel
        info_content = """Context menu status information:

• Entries with descriptions are managed by external tools
• Entries without descriptions are system defaults or unmanaged
• All entries are shown for both folder and background context menus
• Backup files are stored in your WOMM installation directory"""

        _show_tip_panel(info_content, "Status Information")

    else:
        print_error("Failed to retrieve context menu status")

        # Show troubleshooting panel
        troubleshoot_content = """Troubleshooting context menu issues:

• Ensure you have administrator privileges
• Check if Windows Registry access is blocked
• Try running from an elevated command prompt
• Verify WOMM installation is complete"""

        _show_tip_panel(troubleshoot_content, "Troubleshooting")


@context_group.command("backup")
@click.option(
    "--output", "-o", help="Custom backup file path (default: auto-generated)"
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_backup(output, verbose):  # noqa: ARG001
    """💾 Create backup of current context menu entries."""

    if not _check_windows_only():
        return

    print_header("💾 Context Menu Backup")

    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    # Determine backup file path
    if output:
        # Custom output path
        backup_file = output
        print_info(f"Backup location: {backup_file}")
    else:
        # Auto-generated path with timestamp
        from datetime import datetime

        backup_dir = _get_backup_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/context_menu_backup_{timestamp}.json"
        print_info(f"Backup location: {backup_file}")

    # Create backup
    with create_spinner_with_status("Creating context menu backup...") as (
        progress,
        task,
    ):
        progress.update(task, status="Reading registry entries...")
        result = manager.backup_entries(backup_file)

    if result["success"]:
        # Import UI and show success message
        from ..core.ui.context.context import ContextMenuUI

        ui = ContextMenuUI()
        ui.show_backup_success(backup_file, result["entry_count"])
    else:
        print_error(f"Backup failed: {result['error']}")


@context_group.command("restore")
@click.help_option("-h", "--help")
@click.option(
    "--backup-file",
    "-f",
    help="Specific backup file to restore (default: interactive selection)",
)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_restore(backup_file, dry_run, verbose):
    """🔄 Restore context menu entries from backup."""
    if not _check_windows_only():
        return

    print_header("🔄 Context Menu Restore")

    # Import ContextMenuManager and UI
    from ..core.managers.context.managers.context_menu import ContextMenuManager
    from ..core.ui.context.context import ContextMenuUI

    # Initialize manager and UI
    manager = ContextMenuManager()
    ui = ContextMenuUI()

    backup_dir = Path(_get_backup_directory())

    # If specific backup file provided, use it
    if backup_file:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print_error(f"Backup file not found: {backup_file}")
            return
        selected_file = backup_path
    else:
        # Interactive selection from available backups
        selected_file = ui.show_backup_selection_menu(backup_dir, verbose)
        if selected_file is None:
            return

    # Confirm restore operation
    if not ui.confirm_restore_operation(selected_file):
        print_info("Restore cancelled")
        return

    # Execute restore
    with create_spinner_with_status("Restoring context menu from backup...") as (
        progress,
        task,
    ):
        progress.update(task, status="Restoring from backup...")
        result = manager.restore_entries(str(selected_file))

    if result["success"]:
        if dry_run:
            print_info(f"🔍 Would restore from: {selected_file.name}")
            print_success("✅ Dry run completed successfully")
        else:
            ui.show_restore_success(selected_file, result["entry_count"])
    else:
        print_error(f"Restore failed: {result['error']}")


@context_group.command("cherry-pick")
@click.help_option("-h", "--help")
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    help="Show changes without executing",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_cherry_pick(dry_run, verbose):
    """🍒 Cherry-pick specific context menu entries from backups."""
    if not _check_windows_only():
        return

    print_header("🍒 Context Menu Cherry-Pick")

    try:
        # Get backup directory and scan for backups
        backup_dir = Path(_get_backup_directory())
        if not backup_dir.exists():
            print_error("No backup directory found")
            print_info("Create a backup first using 'womm context register'")
            return

        # Collect all entries from all backups
        with create_spinner_with_status("Scanning backup files...") as (progress, task):
            progress.update(task, status="Collecting context menu entries...")
            all_entries = _collect_all_entries_from_backups(backup_dir, verbose)
        if not all_entries:
            print_error("No context menu entries found in backups")
            return

        # Get currently installed entries for comparison
        current_entries = _get_current_context_entries(verbose)

        # Filter out already installed entries
        available_entries = _filter_available_entries(all_entries, current_entries)
        if not available_entries:
            print_info("All context menu entries from backups are already installed")
            return

        # Show selection menu
        selected_entries = _show_cherry_pick_menu(available_entries)
        if not selected_entries:
            print_info("Cherry-pick cancelled")
            return

        # Apply selected entries
        _apply_cherry_picked_entries(selected_entries, dry_run, verbose)

    except Exception as e:
        print_error(f"Cherry-pick failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()


def _collect_all_entries_from_backups(backup_dir: Path, verbose: bool) -> list:
    """Collect and deduplicate all context menu entries from backup files."""
    import json

    all_entries = {}  # Using dict to automatically deduplicate by key_name
    backup_files = sorted(backup_dir.glob("context_menu_backup_*.json"))

    if verbose:
        print_info(f"Scanning {len(backup_files)} backup files...")

    for backup_file in backup_files:
        try:
            with open(backup_file, encoding="utf-8") as f:
                data = json.load(f)

            entries = data.get("entries", [])
            for entry in entries:
                key_name = entry.get("key_name")
                if key_name and key_name not in all_entries:
                    # Add metadata about source backup
                    entry["_source_backup"] = backup_file.name
                    entry["_display_name"] = _format_entry_display_name(entry)
                    all_entries[key_name] = entry

        except Exception as e:
            if verbose:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading {backup_file.name}: {e}"
                )

    if verbose:
        print_info(f"Found {len(all_entries)} unique context menu entries")

    return list(all_entries.values())


def _format_entry_display_name(entry: dict) -> str:
    """Format entry for display in selection menu."""
    key_name = entry.get("key_name", "Unknown")
    properties = entry.get("properties", {})

    # Try to get a user-friendly name
    display_text = properties.get("MUIVerb") or properties.get("@", key_name)

    # Get command info for context
    command = properties.get("Command", "")
    if command:
        # Extract executable name from command
        import re

        exe_match = re.search(r'"([^"]*\.exe)"', command)
        if exe_match:
            exe_name = Path(exe_match.group(1)).name
            display_text = f"{display_text} ({exe_name})"

    return f"{display_text} [key: {key_name}]"


def _get_current_context_entries(verbose: bool) -> set:
    """Get currently installed context menu entries."""
    if verbose:
        print_info("Checking currently installed context menu entries...")

    try:
        # Import ContextMenuManager
        from ..core.managers.context.managers.context_menu import ContextMenuManager

        # Initialize manager
        manager = ContextMenuManager()

        # Get current entries
        result = manager.list_entries()

        if result["success"]:
            entries = result["entries"]
            current_keys = set()

            # Extract key names from all context types
            for context_type in ["directory", "background"]:
                context_entries = entries.get(context_type, [])
                for entry in context_entries:
                    key_name = entry.get("key_name")
                    if key_name:
                        current_keys.add(key_name)

            if verbose:
                print_info(f"Found {len(current_keys)} currently installed entries")

            return current_keys
        else:
            if verbose:
                print_pattern(
                    LogLevel.DEBUG,
                    "SYSTEM",
                    f"Error listing entries: {result['error']}",
                )
            return set()

    except Exception as e:
        if verbose:
            print_pattern(
                LogLevel.DEBUG, "SYSTEM", f"Error checking current entries: {e}"
            )
        return set()


def _filter_available_entries(all_entries: list, current_entries: set) -> list:
    """Filter out entries that are already installed."""
    available = []
    for entry in all_entries:
        key_name = entry.get("key_name")
        if key_name and key_name not in current_entries:
            available.append(entry)
    return available


def _show_cherry_pick_menu(available_entries: list) -> list:
    """Show interactive menu for selecting entries to install."""
    print_info("Select context menu entries to install:")

    # Create interactive menu
    menu = InteractiveMenu(
        title="Cherry-pick Context Menu Entries",
        instruction="Use space to select/deselect, enter to confirm, q to quit",
    )

    # Format entries for display
    def format_entry(entry):
        return entry["_display_name"]

    # Show multi-selection menu
    selected = menu.select_multiple_from_list(
        available_entries, display_func=format_entry
    )

    return selected if selected else []


def _apply_cherry_picked_entries(selected_entries: list, dry_run: bool, verbose: bool):
    """Apply the selected context menu entries."""
    # Import ContextMenuManager
    from ..core.managers.context.managers.context_menu import ContextMenuManager

    # Initialize manager
    manager = ContextMenuManager()

    with create_spinner_with_status(
        f"Applying {len(selected_entries)} selected entries..."
    ) as (progress, task):
        for i, entry in enumerate(selected_entries, 1):
            key_name = entry.get("key_name")
            properties = entry.get("properties", {})
            source_backup = entry.get("_source_backup", "unknown")

            # Extract command and other properties
            command = properties.get("Command", "")
            muiverb = properties.get("MUIVerb")
            icon = properties.get("Icon")

            if not command:
                print_pattern(
                    LogLevel.WARNING, "SYSTEM", f"Skipping {key_name}: no command found"
                )
                continue

            progress.update(
                task, status=f"Installing {key_name} ({i}/{len(selected_entries)})..."
            )
            if verbose:
                print_info(f"[{i}/{len(selected_entries)}] Installing: {key_name}")
                print_info(f"   Source: {source_backup}")
                print_info(f"   Command: {command}")

            # Extract script path from command (simplified approach)
            script_path = None
            if '"' in command:
                script_match = command.split('"')[1]
                if script_match and Path(script_match).exists():
                    script_path = script_match

            if not script_path:
                print_pattern(
                    LogLevel.WARNING,
                    "SYSTEM",
                    f"Skipping {key_name}: could not extract script path",
                )
                continue

            # Execute registration
            if dry_run:
                print_info(
                    f"Dry run: Would register {script_path} as '{muiverb or key_name}'"
                )
            else:
                result = manager.register_script(
                    script_path, muiverb or key_name, icon or "auto", dry_run=False
                )

                if result["success"]:
                    print_success(f"Installed: {key_name}")
                else:
                    print_error(f"Failed to install: {key_name} - {result['error']}")

    if not dry_run:
        print_success(
            f"Cherry-pick completed! {len(selected_entries)} entries installed"
        )

        # Show tip panel
        tip_content = f"""Cherry-pick installation completed successfully.

• {len(selected_entries)} context menu entries installed
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the new entries
• If an entry doesn't work, check the original script path"""

        _show_tip_panel(tip_content, "Cherry-pick Complete")
