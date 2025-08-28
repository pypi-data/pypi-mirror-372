#!/usr/bin/env python3
"""
Interactive wizard for context menu configuration.

This module provides an interactive step-by-step wizard for configuring
context menu entries, making it easy for users to set up their scripts
without needing to know all the technical details.
"""

from pathlib import Path
from typing import Optional, Tuple

try:
    from InquirerPy import inquirer
    from InquirerPy.validator import PathValidator

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

from ...managers.context.utils.context_parameters import ContextParameters, ContextType
from ..common.console import Console, print_error, print_info
from ..interactive import InteractiveMenu


class ContextMenuWizard:
    """Interactive wizard for context menu configuration."""

    # Console instance for styling
    _console = Console()

    @staticmethod
    def run_setup() -> Tuple[
        Optional[str], Optional[str], Optional[str], Optional[ContextParameters]
    ]:
        """
        Run the complete interactive setup wizard.

        Returns:
            Tuple of (script_path, label, icon, context_params) or (None, None, None, None) if cancelled
        """
        print_info("🎯 Interactive Context Menu Setup")
        print_info("=" * 50)

        # Step 1: Select script file
        ContextMenuWizard._console.print("", style="dim")
        ContextMenuWizard._console.print(
            "📁 Step 1: Select script file", style="bold blue"
        )
        script_path = ContextMenuWizard._select_script()
        if not script_path:
            return None, None, None, None

        # Step 2: Enter label
        ContextMenuWizard._console.print("\n" + (":" * 80) + "\n", style="dim")
        ContextMenuWizard._console.print(
            "🏷️  Step 2: Enter display label", style="bold blue"
        )
        label = ContextMenuWizard._get_label()
        if not label:
            return None, None, None, None

        # Step 3: Select icon
        ContextMenuWizard._console.print("\n" + (":" * 80) + "\n", style="dim")
        ContextMenuWizard._console.print("🎨 Step 3: Select icon", style="bold blue")
        icon = ContextMenuWizard._select_icon(script_path)

        # Step 4: Select context type
        ContextMenuWizard._console.print("\n" + (":" * 80) + "\n", style="dim")
        ContextMenuWizard._console.print(
            "🎯 Step 4: Select context type", style="bold blue"
        )
        context_params = ContextMenuWizard._select_context()

        return script_path, label, icon, context_params

    @staticmethod
    def _select_script() -> Optional[str]:
        """Interactive script file selection."""
        if INQUIRERPY_AVAILABLE:
            # Use InquirerPy for better file selection
            return ContextMenuWizard._select_script_with_inquirer()
        else:
            # Fallback to custom menu
            return ContextMenuWizard._select_script_fallback()

    @staticmethod
    def _select_script_with_inquirer() -> Optional[str]:
        """Select script using InquirerPy file browser."""
        try:
            # Create a custom validator for script files
            class ScriptFileValidator(PathValidator):
                def __init__(self):
                    super().__init__()
                    self.script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

                def validate(self, document):
                    result = super().validate(document)
                    if result:
                        path = Path(document.text)
                        if (
                            path.is_file()
                            and path.suffix.lower() in self.script_extensions
                        ):
                            return True
                        else:
                            raise ValueError(
                                f"File must be a script ({', '.join(self.script_extensions)})"
                            )
                    return result

            # Use InquirerPy file browser
            script_path = inquirer.filepath(
                message="Select script file:",
                default=str(Path.cwd()),
                validate=ScriptFileValidator(),
                only_files=True,
                only_directories=False,
                transformer=lambda result: str(Path(result).resolve()),
                filter=lambda result: str(Path(result).resolve()),
            ).execute()

            if script_path:
                return script_path
            else:
                print_info("File selection cancelled")
                return None

        except Exception as e:
            print_error(f"Error with file browser: {e}")
            print_info("Falling back to manual input...")
            return ContextMenuWizard._select_script_fallback()

    @staticmethod
    def _select_script_fallback() -> Optional[str]:
        """Fallback script selection using custom menu."""
        menu = InteractiveMenu(
            title="Select Script File",
            instruction="Choose how to specify the script file",
        )

        options = ["Browse current directory", "Enter path manually", "Cancel"]

        choice = menu.select_from_list(options)

        if choice == 0:  # Browse
            return ContextMenuWizard._browse_for_script()
        elif choice == 1:  # Manual
            print_info("Enter the full path to your script:")
            path = input("> ").strip()
            if path and Path(path).exists():
                return path
            else:
                print_error("Invalid path or file not found")
                return None
        else:  # Cancel
            return None

    @staticmethod
    def _browse_for_script() -> Optional[str]:
        """Browse for script files in current directory."""
        current_dir = Path.cwd()

        # Supported script extensions
        script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

        # Find script files in current directory
        script_files = []
        for file in current_dir.iterdir():
            if file.is_file() and file.suffix.lower() in script_extensions:
                script_files.append(file)

        if not script_files:
            print_error("No script files found in current directory")
            print_info(f"Current directory: {current_dir}")
            print_info(f"Supported extensions: {', '.join(script_extensions)}")
            return None

        # Sort files by name
        script_files.sort(key=lambda x: x.name.lower())

        # Create selection menu
        menu = InteractiveMenu(
            title="Select Script File",
            instruction=f"Found {len(script_files)} script files in {current_dir.name}",
        )

        # Add file options
        file_options = []
        for file in script_files:
            file_info = f"{file.name} ({file.suffix.upper()})"
            file_options.append(file_info)

        # Add navigation options
        file_options.extend(["📁 Browse parent directory", "❌ Cancel"])

        choice = menu.select_from_list(file_options)

        if choice < len(script_files):
            # File selected
            selected_file = script_files[choice]
            return str(selected_file.resolve())
        elif choice == len(script_files):
            # Browse parent directory
            parent_dir = current_dir.parent
            if parent_dir != current_dir:  # Not at root
                return ContextMenuWizard._browse_directory(parent_dir)
            else:
                print_error("Already at root directory")
                return None
        else:
            # Cancel
            return None

    @staticmethod
    def _browse_directory(directory: Path) -> Optional[str]:
        """Browse a specific directory for script files."""
        if not directory.exists() or not directory.is_dir():
            print_error(f"Invalid directory: {directory}")
            return None

        # Supported script extensions
        script_extensions = {".py", ".bat", ".ps1", ".exe", ".cmd"}

        # Get subdirectories and script files
        subdirs = []
        script_files = []

        try:
            for item in directory.iterdir():
                if item.is_dir():
                    subdirs.append(item)
                elif item.is_file() and item.suffix.lower() in script_extensions:
                    script_files.append(item)
        except PermissionError:
            print_error(f"Permission denied accessing directory: {directory}")
            return None

        # Sort items
        subdirs.sort(key=lambda x: x.name.lower())
        script_files.sort(key=lambda x: x.name.lower())

        # Create options list
        options = []
        all_items = []

        # Add parent directory option (if not at root)
        if directory.parent != directory:
            options.append("📁 .. (Parent directory)")
            all_items.append(("parent", directory.parent))

        # Add subdirectories
        for subdir in subdirs:
            options.append(f"📁 {subdir.name}/")
            all_items.append(("dir", subdir))

        # Add script files
        for file in script_files:
            options.append(f"📄 {file.name} ({file.suffix.upper()})")
            all_items.append(("file", file))

        # Add cancel option
        options.append("❌ Cancel")
        all_items.append(("cancel", None))

        if not script_files and not subdirs:
            print_error(f"No script files or subdirectories found in {directory}")
            return None

        # Show selection menu
        menu = InteractiveMenu(
            title="Browse Directory",
            instruction=f"Current: {directory} | Files: {len(script_files)} | Dirs: {len(subdirs)}",
        )

        choice = menu.select_from_list(options)

        if choice >= len(all_items):
            return None

        item_type, item_path = all_items[choice]

        if item_type == "file":
            return str(item_path.resolve())
        elif item_type == "dir" or item_type == "parent":
            return ContextMenuWizard._browse_directory(item_path)
        else:  # cancel
            return None

    @staticmethod
    def _get_label() -> Optional[str]:
        """Interactive label input."""
        if INQUIRERPY_AVAILABLE:
            return ContextMenuWizard._get_label_with_inquirer()
        else:
            return ContextMenuWizard._get_label_fallback()

    @staticmethod
    def _get_label_with_inquirer() -> Optional[str]:
        """Get label using InquirerPy."""
        try:
            label = inquirer.text(
                message="Enter the label to display in the context menu:",
                validate=lambda result: len(result.strip()) > 0 if result else False,
                invalid_message="Label cannot be empty",
                filter=lambda result: result.strip(),
            ).execute()

            return label if label else None

        except Exception as e:
            print_error(f"Error with label input: {e}")
            print_info("Falling back to manual input...")
            return ContextMenuWizard._get_label_fallback()

    @staticmethod
    def _get_label_fallback() -> Optional[str]:
        """Fallback label input."""
        print_info("Enter the label to display in the context menu:")
        label = input("> ").strip()
        if not label:
            print_error("Label cannot be empty")
            return None
        return label

    @staticmethod
    def _select_icon(script_path: str) -> Optional[str]:  # noqa: ARG004
        """Interactive icon selection."""
        # Note: script_path is kept for future use when auto-detecting script icons
        if INQUIRERPY_AVAILABLE:
            return ContextMenuWizard._select_icon_with_inquirer()
        else:
            return ContextMenuWizard._select_icon_fallback()

    @staticmethod
    def _select_icon_with_inquirer() -> Optional[str]:
        """Select icon using InquirerPy."""
        try:
            # First, ask for icon type
            icon_type = inquirer.select(
                message="Choose icon type:",
                choices=[
                    {"name": "Auto-detect (recommended)", "value": "auto"},
                    {"name": "Use script's own icon", "value": "script"},
                    {"name": "Browse for icon file", "value": "browse"},
                    {"name": "Enter custom path", "value": "manual"},
                    {"name": "No icon", "value": "none"},
                ],
                default="auto",
            ).execute()

            if icon_type == "auto":
                return "auto"
            elif icon_type == "script":
                return "script"
            elif icon_type == "none":
                return None
            elif icon_type == "browse":
                # Use InquirerPy file browser for icon files
                class IconFileValidator(PathValidator):
                    def __init__(self):
                        super().__init__()
                        self.icon_extensions = {
                            ".ico",
                            ".exe",
                            ".dll",
                            ".png",
                            ".jpg",
                            ".jpeg",
                        }

                    def validate(self, document):
                        result = super().validate(document)
                        if result:
                            path = Path(document.text)
                            if (
                                path.is_file()
                                and path.suffix.lower() in self.icon_extensions
                            ):
                                return True
                            else:
                                raise ValueError(
                                    f"File must be an icon ({', '.join(self.icon_extensions)})"
                                )
                        return result

                icon_path = inquirer.filepath(
                    message="Select icon file:",
                    default=str(Path.cwd()),
                    validate=IconFileValidator(),
                    only_files=True,
                    only_directories=False,
                    transformer=lambda result: str(Path(result).resolve()),
                    filter=lambda result: str(Path(result).resolve()),
                ).execute()

                return icon_path if icon_path else "auto"
            else:  # manual
                icon_path = inquirer.text(
                    message="Enter icon file path:",
                    validate=lambda result: Path(result).exists() if result else True,
                ).execute()

                return icon_path if icon_path else "auto"

        except Exception as e:
            print_error(f"Error with icon selection: {e}")
            print_info("Falling back to manual input...")
            return ContextMenuWizard._select_icon_fallback()

    @staticmethod
    def _select_icon_fallback() -> Optional[str]:
        """Fallback icon selection using custom menu."""
        menu = InteractiveMenu(
            title="Select Icon", instruction="Choose icon for the context menu entry"
        )

        options = [
            "Auto-detect (recommended)",
            "Use script's own icon",
            "Enter custom icon path",
            "No icon",
        ]

        choice = menu.select_from_list(options)

        if choice == 0:
            return "auto"
        elif choice == 1:
            return "script"
        elif choice == 2:
            print_info("Enter the path to your icon file (.ico, .exe, etc.):")
            icon_path = input("> ").strip()
            return icon_path if icon_path else "auto"
        else:
            return None

    @staticmethod
    def _select_context() -> ContextParameters:
        """Interactive context type selection."""
        menu = InteractiveMenu(
            title="Select Context Type",
            instruction="Choose where this script should appear",
        )

        context_options = [
            "Directory + Background (default)",
            "Files only",
            "Directories only",
            "Background only",
            "Root directories (drives)",
            "Custom file types",
        ]

        choice = menu.select_from_list(context_options)

        context_params = ContextParameters()

        if choice == 0:  # Default
            context_params.add_context_type(ContextType.DIRECTORY)
            context_params.add_context_type(ContextType.BACKGROUND)
        elif choice == 1:  # Files
            context_params.add_context_type(ContextType.FILE)
        elif choice == 2:  # Directories
            context_params.add_context_type(ContextType.DIRECTORY)
        elif choice == 3:  # Background
            context_params.add_context_type(ContextType.BACKGROUND)
        elif choice == 4:  # Root
            context_params.add_context_type(ContextType.ROOT)
        elif choice == 5:  # Custom file types
            context_params.add_context_type(ContextType.FILE)
            ContextMenuWizard._select_file_types(context_params)

        return context_params

    @staticmethod
    def _select_file_types(context_params: ContextParameters) -> None:
        """Interactive file type selection."""
        menu = InteractiveMenu(
            title="Select File Types", instruction="Choose which file types to support"
        )

        file_type_options = [
            "Images (.jpg, .png, .gif, etc.)",
            "Text files (.txt, .md, .py, etc.)",
            "Archives (.zip, .rar, .7z, etc.)",
            "Documents (.pdf, .doc, .xls, etc.)",
            "Media files (.mp3, .mp4, .avi, etc.)",
            "Code files (.py, .js, .java, etc.)",
            "Custom extensions",
        ]

        choice = menu.select_from_list(file_type_options)

        if choice == 0:
            context_params.add_file_type("image")
        elif choice == 1:
            context_params.add_file_type("text")
        elif choice == 2:
            context_params.add_file_type("archive")
        elif choice == 3:
            context_params.add_file_type("document")
        elif choice == 4:
            context_params.add_file_type("media")
        elif choice == 5:
            context_params.add_file_type("code")
        elif choice == 6:
            print_info("Enter custom extensions (e.g., .py .js .txt):")
            extensions = input("> ").strip().split()
            for ext in extensions:
                context_params.add_file_type(ext)
