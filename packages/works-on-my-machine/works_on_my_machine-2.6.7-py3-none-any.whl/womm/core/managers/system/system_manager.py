#!/usr/bin/env python3
"""
System Manager for Works On My Machine.
Handles system detection and prerequisites installation with integrated UI.
"""

# IMPORTS
########################################################
# Standard library imports
from typing import Dict, List

# Third-party imports
from rich.table import Table

from ...ui.common.console import (
    console,
    print_error,
    print_header,
    print_success,
    print_system,
)
from ...ui.common.progress import create_spinner_with_status
from ...utils.system.system_detector import SystemDetector

# Local imports - moved to methods to avoid slow startup
# from ..dependencies.runtime_manager import runtime_manager

# MAIN CLASS
########################################################


class SystemManager:
    """Manages system detection and prerequisites installation with integrated UI."""

    def __init__(self):
        """Initialize the SystemManager."""
        # Lazy initialization to avoid slow startup
        self._detector = None

    @property
    def detector(self):
        """Lazy load SystemDetector when needed."""
        if self._detector is None:
            self._detector = SystemDetector()
        return self._detector

    def detect_system(self) -> None:
        """Detect system information and available tools with UI."""
        print_header("WOMM System Detection")

        with create_spinner_with_status("Detecting system information...") as (
            progress,
            task,
        ):
            # Update description and status
            progress.update(
                task,
                description="🔍 Detecting system information...",
                status="Initializing...",
            )

            # Update status during detection
            progress.update(task, status="Scanning system...")
            data = self.detector.get_system_data()

            # Final status update
            progress.update(task, status="Detection complete!")

        if data:
            self._display_system_data(data)
        else:
            console.print("❌ Failed to detect system information")
            raise RuntimeError("System detection failed")

    def check_prerequisites(self, tools: List[str]) -> None:
        """Check system prerequisites with UI."""
        print_header("WOMM System Prerequisites :: Checking")

        from ...ui.common.console import print_system

        # Lazy import to avoid slow startup
        from ..dependencies.runtime_manager import runtime_manager

        print_system("Checking system prerequisites...")

        # Determine which tools to process
        tools_to_process = (
            ["python", "node", "git"] if not tools or "all" in tools else list(tools)
        )

        # Check prerequisites
        results = {}
        for _i, step in enumerate(tools_to_process):
            result = runtime_manager.check_runtime(step)
            results[step] = result

        # Display results in a table
        self._display_prerequisites_table(results, "Prerequisites Status")
        console.print("")

        # Check if any tools are missing
        missing_tools = [tool for tool, result in results.items() if not result.success]
        if missing_tools:
            print_error(f"Missing tools: {', '.join(missing_tools)}")
            print_system("💡 Run without --check flag to install them.")

    def install_prerequisites(
        self, tools: List[str], pm_args: List[str] | None = None, ask_path: bool = False
    ) -> None:
        """Install system prerequisites with interactive UI."""
        print_header("WOMM System Prerequisites :: Installing")

        # Step 1: Ensure a package manager is available (no auto-install)
        from ..dependencies.package_manager import package_manager

        # Lazy import to avoid slow startup
        from ..dependencies.runtime_manager import (
            RUNTIMES,
            RuntimeResult,
            runtime_manager,
        )

        print_system("Checking system prerequisites...")

        # Ensure package manager first to avoid repeated failures later
        preferred = (
            None  # Let runtime-specific handle preferences, but early feedback helps
        )
        pm_result = package_manager.ensure_manager(preferred)
        if not pm_result.success:
            if getattr(pm_result, "panel", None) is not None:
                console.print(pm_result.panel)
            print_error("Aucun gestionnaire de paquets disponible. Abandon.")
            return

        selected_pm_name = pm_result.package_manager_name
        selected_pm_platform = pm_result.platform

        all_runtimes = list(RUNTIMES.keys())
        current_status = runtime_manager.get_installation_status(all_runtimes)

        # Display current status
        current_results = {}
        for runtime in all_runtimes:
            status = current_status[runtime]
            current_results[runtime] = RuntimeResult(
                success=status["installed"],
                runtime_name=runtime,
                version=status["version"],
                path=status["path"],
                message=f"Runtime {runtime} {'available' if status['installed'] else 'not found'}",
                error=(
                    None if status["installed"] else f"Runtime {runtime} not installed"
                ),
            )

        self._display_prerequisites_table(current_results, "Current Status")

        # Step 2: Interactive selection if not "all" specified
        if not tools or "all" in tools:
            # Use interactive selection
            selected_runtimes = self._interactive_runtime_selection(current_status)
            # No need to show "no selection" message as it's handled in _interactive_runtime_selection
            if not selected_runtimes:
                return
        else:
            # Use specified tools
            selected_runtimes = tools

        # Step 3: Install selected runtimes
        if not selected_runtimes:
            console.print("✅ Tous les runtimes sont déjà installés !")
            return

        print_system("🚀 Installation des runtimes sélectionnés...")

        installation_results = {}
        for runtime in selected_runtimes:
            print_system(f"📦 Installation de {runtime}...")

            with create_spinner_with_status(f"Installing {runtime}...") as (
                progress,
                task,
            ):
                # Build extra args for PM if requested
                extra_pm_args = list(pm_args) if pm_args else None

                # Best-effort ask-path (Windows/winget,choco) via generic args
                if ask_path:
                    from ...ui.common.console import print_warn
                    from ...ui.common.prompts import prompt_path

                    install_dir = prompt_path(
                        f"Chemin d'installation pour {runtime} (laisser vide pour défaut):",
                        default=None,
                    )
                    if install_dir:
                        extra_pm_args = extra_pm_args or []
                        # Best-effort mapping by selected package manager
                        if (
                            selected_pm_platform == "windows"
                            and selected_pm_name == "winget"
                        ):
                            extra_pm_args.append(f"--location={install_dir}")
                        elif (
                            selected_pm_platform == "windows"
                            and selected_pm_name == "chocolatey"
                        ):
                            extra_pm_args.append(
                                f'--install-arguments=INSTALLDIR="{install_dir}"'
                            )
                        else:
                            print_warn(
                                "Le gestionnaire de paquets sélectionné ne supporte probablement pas un chemin d'installation personnalisé. L'argument sera ignoré."
                            )

                # Use runtime_manager for installation
                result = runtime_manager.install_runtime(
                    runtime, extra_pm_args=extra_pm_args
                )
                installation_results[runtime] = result

                if result.success:
                    progress.update(task, status=f"{runtime} installed successfully!")
                else:
                    progress.update(task, status=f"{runtime} installation failed!")

        # Step 4: Display final results
        print_system("Installation Summary:")
        self._display_installation_table(installation_results)
        console.print("")

        # Step 5: Final verification
        failed_installations = [
            runtime
            for runtime, result in installation_results.items()
            if not result.success
        ]

        if failed_installations:
            print_error(f"Failed to install: {', '.join(failed_installations)}")
            raise RuntimeError("Prerequisites installation failed")
        else:
            print_success("All prerequisites installed successfully!")

    def _interactive_runtime_selection(self, current_status: Dict) -> List[str]:
        """Interactive runtime selection using the new select_multiple_from_list method."""
        from ...ui.interactive import InteractiveMenu

        # Lazy import to avoid slow startup
        from ..dependencies.runtime_manager import RUNTIMES

        # Prepare items for selection
        items = []
        checked_items = []
        disabled_items = []

        # Sort runtimes by priority
        sorted_runtimes = sorted(RUNTIMES.items(), key=lambda x: x[1]["priority"])

        for runtime_name, runtime_config in sorted_runtimes:
            runtime_status = current_status.get(runtime_name, {})
            is_installed = runtime_status.get("installed", False)
            version = runtime_status.get("version", "Non installé")

            # Create item dict
            item = {
                "key": runtime_name,
                "name": runtime_name.title(),
                "version": version,
                "priority": runtime_config["priority"],
                "installed": is_installed,
            }
            items.append(item)

            # Mark as checked and disabled if installed
            if is_installed:
                checked_items.append(runtime_name)
                disabled_items.append(runtime_name)

        # Display function
        def format_runtime_item(item):
            status_icon = "✅" if item["installed"] else "❌"
            priority_text = f"[{item['priority']}] " if not item["installed"] else ""
            return f"{status_icon} {priority_text}{item['name']} ({item['version']})"

        # Create interactive menu
        menu = InteractiveMenu("Quels runtimes voulez-vous installer ?")

        # Check if all runtimes are already installed
        all_installed = all(item["installed"] for item in items)
        if all_installed:
            console.print("✅ Tous les runtimes sont déjà installés !")
            return []

        # Show selection
        selected = menu.select_multiple_from_list(
            items=items,
            display_func=format_runtime_item,
            checked_items=checked_items,
            disabled_items=disabled_items,
        )

        if selected:
            # Extract runtime names from selected items
            return [item["key"] for item in selected]

        return []

    def _display_system_data(self, data: Dict) -> None:
        """Display system data in a Rich panel."""
        from ...ui.common.panels import create_panel

        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")

        system_info = data.get("system_info", {})
        package_managers = data.get("package_managers", {})
        dev_environments = data.get("dev_environments", {})
        recommendations = data.get("recommendations", {})

        # Format the data nicely
        content = []
        content.append("[bold blue]System Information[/bold blue]")
        content.append(
            f"OS: {system_info.get('platform', 'unknown')} {system_info.get('platform_release', '')}"
        )
        content.append(f"Architecture: {system_info.get('architecture', 'unknown')}")
        content.append(f"Python: {system_info.get('python_version', 'unknown')}")
        content.append(f"Shell: {system_info.get('shell', 'unknown')}")

        content.append(
            f"\n[bold green]Package Managers[/bold green] ({len(package_managers)} available)"
        )
        for name, info in package_managers.items():
            if info.get("available"):
                content.append(
                    f"✓ {name}: {info.get('version', 'unknown')} - {info.get('description', '')}"
                )

        content.append(
            f"\n[bold yellow]Development Environments[/bold yellow] ({len(dev_environments)} detected)"
        )
        for _, info in dev_environments.items():
            if info.get("available"):
                content.append(
                    f"✓ {info.get('name', 'unknown')}: {info.get('version', 'unknown')}"
                )

        content.append("\n[bold magenta]Recommendations[/bold magenta]")
        for category, recommendation in recommendations.items():
            content.append(f"- {category}: {recommendation}")

        # Add a blank line before the panel for better spacing
        console.print()
        panel = create_panel(
            "\n".join(content),
            title="System Detection Results",
            style="white",
            border_style="dim white",
        )
        console.print(panel)

    def _display_prerequisites_table(self, results: Dict, title: str) -> None:
        """Display prerequisites results in a table."""
        table = Table(title=title)
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Version", style="dim")
        table.add_column("Path", style="dim")

        for tool, result in results.items():
            status = "✅ Installed" if result.success else "❌ Missing"
            version = result.version or "N/A"
            path = result.path or "N/A"
            table.add_row(tool.capitalize(), status, version, path)

        console.print("")
        console.print(table)

    def _display_installation_table(self, results: Dict) -> None:
        """Display installation results in a table."""
        table = Table(title="Installation Results")
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Version", style="dim")
        table.add_column("Message", style="dim")

        for tool, result in results.items():
            if result.success:
                status = "✅ Success"
                version = result.version or "N/A"
            else:
                status = "❌ Failed"
                version = "N/A"

            message = result.message or result.error or "N/A"
            table.add_row(tool.capitalize(), status, version, message)

        console.print(table)


# GLOBAL INSTANCE
########################################################

system_manager = SystemManager()
