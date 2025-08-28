#!/usr/bin/env python3
"""
Development Tools Manager for Works On My Machine.
Manages language-specific development tools (black, isort, eslint, etc.).
"""

import shutil
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ....common.results import BaseResult
from ...ui.common.console import print_deps, print_error, print_success
from ...utils.cli_utils import check_tool_available, run_command, run_silent


@dataclass
class DevToolResult(BaseResult):
    """Result of a development tool operation."""

    tool_name: str = ""
    language: str = ""
    tool_type: str = ""
    path: Optional[str] = None


# DEVELOPMENT TOOLS DEFINITIONS
########################################################

DEV_TOOLS = {
    "python": {
        "formatting": ["black", "isort"],
        "linting": ["ruff", "flake8"],
        "security": ["bandit"],
        "testing": ["pytest"],
        "type_checking": ["mypy"],
    },
    "javascript": {
        "formatting": ["prettier"],
        "linting": ["eslint"],
        "testing": ["jest"],
        "bundling": ["webpack", "vite"],
    },
    "universal": {
        "spell_checking": ["cspell"],
        "git_hooks": ["pre-commit"],
    },
}

# Installation methods for each language
INSTALLATION_METHODS = {
    "python": "pip",
    "javascript": "npm",
    "universal": "auto",  # Auto-detect based on tool
}

# Special tool configurations
TOOL_CONFIGS = {
    "cspell": {
        "check_method": "npx",  # Can be checked via npx
        "install_method": "npm",
    },
    "pre-commit": {"check_method": "standard", "install_method": "pip"},
}


# MAIN CLASS
########################################################


class DevToolsManager:
    """Manages development tools for different languages."""

    def __init__(self):
        self.cache = {}

    def check_dev_tool(self, language: str, tool_type: str, tool: str) -> DevToolResult:
        """Check if a development tool is installed."""
        cache_key = f"{language}:{tool_type}:{tool}"

        if cache_key in self.cache:
            available = self.cache[cache_key]
            return DevToolResult(
                success=available,
                tool_name=tool,
                language=language,
                tool_type=tool_type,
                path=shutil.which(tool) if available else None,
                message=f"Dev tool {tool} {'available' if available else 'not found'}",
                error=None if available else f"Dev tool {tool} not installed",
            )

        # Check if tool is available
        available = self._check_tool_availability(tool)
        self.cache[cache_key] = available

        return DevToolResult(
            success=available,
            tool_name=tool,
            language=language,
            tool_type=tool_type,
            path=shutil.which(tool) if available else None,
            message=f"Dev tool {tool} {'available' if available else 'not found'}",
            error=None if available else f"Dev tool {tool} not installed",
        )

    def install_dev_tool(
        self, language: str, tool_type: str, tool: str
    ) -> DevToolResult:
        """Install a development tool with integrated UI feedback."""
        from ...ui.common.progress import create_spinner_with_status

        # Check if already installed
        if self.check_dev_tool(language, tool_type, tool).success:
            print_success(f"Dev tool {tool} already installed")
            return DevToolResult(
                success=True,
                tool_name=tool,
                language=language,
                tool_type=tool_type,
                path=shutil.which(tool),
                message=f"Dev tool {tool} already installed",
            )

        with create_spinner_with_status(
            f"Installing [bold cyan]{tool}[/bold cyan]..."
        ) as (
            progress,
            task,
        ):
            # Determine installation method
            progress.update(task, status="Determining installation method...")
            install_method = self._get_installation_method(language, tool)

            # Ensure required runtime is available (and attempt install if missing)
            progress.update(task, status="Checking runtime requirements...")
            runtime_ok, runtime_error = self._ensure_required_runtime(
                install_method, tool
            )
            if not runtime_ok:
                progress.update(task, status="Runtime requirements not met")
                print_error(
                    f"Runtime requirements not available for {tool}: {runtime_error}"
                )
                return DevToolResult(
                    success=False,
                    tool_name=tool,
                    language=language,
                    tool_type=tool_type,
                    message="Required runtime not available",
                    error=runtime_error or "Required runtime not available",
                )

            # Install the tool
            progress.update(task, status=f"Installing via {install_method}...")
            success = False
            if install_method == "pip":
                success = self._install_python_tool(tool)
            elif install_method == "npm":
                success = self._install_javascript_tool(tool)
            else:
                progress.update(task, status="No installation method found")
                print_error(f"No installation method found for {tool}")
                return DevToolResult(
                    success=False,
                    tool_name=tool,
                    language=language,
                    tool_type=tool_type,
                    message=f"No installation method found for {tool}",
                    error="No installation method found",
                )

            if success:
                # Clear cache for this tool
                self._clear_tool_cache(language, tool_type, tool)
                progress.update(task, status="Installation completed successfully!")
                print_success(f"Dev tool {tool} installed successfully")

                return DevToolResult(
                    success=True,
                    tool_name=tool,
                    language=language,
                    tool_type=tool_type,
                    path=shutil.which(tool),
                    message=f"Dev tool {tool} installed successfully",
                )
            else:
                progress.update(task, status="Installation failed")
                print_error(f"Failed to install dev tool {tool}")
                return DevToolResult(
                    success=False,
                    tool_name=tool,
                    language=language,
                    tool_type=tool_type,
                    message=f"Failed to install dev tool {tool}",
                    error="Installation failed",
                )

    def check_and_install_dev_tools(self, language: str) -> Dict[str, DevToolResult]:
        """Check and install all dev tools for a language with integrated UI."""
        from ...ui.common.progress import create_spinner_with_status

        if language not in DEV_TOOLS:
            print_error(f"Language {language} not supported")
            return {
                "error": DevToolResult(
                    success=False,
                    tool_name="",
                    language=language,
                    tool_type="",
                    message=f"Language {language} not supported",
                    error=f"Language {language} not supported",
                )
            }

        print_deps(f"Checking and installing {language} development tools...")

        results = {}
        total_tools = sum(len(tools) for tools in DEV_TOOLS[language].values())
        processed = 0

        with create_spinner_with_status(
            f"Processing [bold cyan]{language}[/bold cyan] dev tools..."
        ) as (
            progress,
            task,
        ):
            for tool_type, tools in DEV_TOOLS[language].items():
                for tool in tools:
                    processed += 1
                    progress.update(
                        task, status=f"Processing {tool} ({processed}/{total_tools})..."
                    )

                    result = self.check_dev_tool(language, tool_type, tool)
                    if not result.success:
                        # Try to install the tool
                        progress.update(task, status=f"Installing {tool}...")
                        result = self.install_dev_tool(language, tool_type, tool)
                    else:
                        print_success(f"Dev tool {tool} already available")

                    results[tool] = result

            progress.update(task, status="All tools processed!")

        # Summary
        successful = sum(1 for result in results.values() if result.success)
        print_deps(
            f"Development tools summary: {successful}/{len(results)} tools available"
        )

        return results

    def get_required_tools(self, language: str) -> List[str]:
        """Get list of required tools for a language."""
        if language not in DEV_TOOLS:
            return []

        tools = []
        for _, tool_list in DEV_TOOLS[language].items():
            tools.extend(tool_list)

        return tools

    def get_tool_status(self, language: str = None) -> Dict[str, Dict]:
        """Get comprehensive status of development tools with UI output."""
        from ...ui.common.progress import create_spinner

        status = {}
        languages_to_check = [language] if language else DEV_TOOLS.keys()

        with create_spinner("Checking dev tools status...") as (progress, task):
            for lang in languages_to_check:
                if lang not in DEV_TOOLS:
                    continue

                progress.update(
                    task, description=f"Checking [bold cyan]{lang}[/bold cyan] tools..."
                )

                status[lang] = {}
                for tool_type, tools in DEV_TOOLS[lang].items():
                    status[lang][tool_type] = {}
                    for tool in tools:
                        available = self._check_tool_availability(tool)
                        status[lang][tool_type][tool] = {
                            "installed": available,
                            "path": shutil.which(tool) if available else None,
                            "supported": True,
                        }

        # Display results in a table
        if status:
            self._display_status_table(status)

        return status

    def _display_status_table(self, status: Dict[str, Dict]) -> None:
        """Display development tools status in a formatted table."""
        from rich.table import Table

        from ...ui.common.console import console

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Language", style="cyan")
        table.add_column("Tool Type", style="blue")
        table.add_column("Tool", style="white")
        table.add_column("Status", justify="center")
        table.add_column("Path", style="dim")

        for language, lang_tools in status.items():
            for tool_type, tools in lang_tools.items():
                for tool, info in tools.items():
                    status_icon = "✅" if info["installed"] else "❌"
                    status_text = "Installed" if info["installed"] else "Missing"
                    path_text = info.get("path", "Not found") or "Not found"

                    table.add_row(
                        language,
                        tool_type,
                        tool,
                        f"{status_icon} {status_text}",
                        path_text,
                    )

        console.print("\n")
        console.print(table)
        console.print("\n")

    def _check_tool_availability(self, tool: str) -> bool:
        """Check if a tool is available."""
        # Standard check via PATH
        if check_tool_available(tool):
            return True

        # Special checks for certain tools
        if tool == "cspell":
            # Check if cspell is available via npx
            result = run_silent(["npx", "cspell", "--version"])
            return result.success

        return False

    def _get_installation_method(self, language: str, tool: str) -> str:
        """Get the installation method for a tool."""
        # Check if tool has specific configuration
        if tool in TOOL_CONFIGS:
            return TOOL_CONFIGS[tool]["install_method"]

        # Use language default
        return INSTALLATION_METHODS.get(language, "auto")

    def _install_python_tool(self, tool: str) -> bool:
        """Install a Python development tool."""
        cmd = [sys.executable, "-m", "pip", "install", tool]
        result = run_command(cmd)
        return result.success

    def _install_javascript_tool(self, tool: str) -> bool:
        """Install a JavaScript development tool."""
        cmd = ["npm", "install", "-g", tool]
        result = run_command(cmd)
        return result.success

    def _clear_tool_cache(self, language: str, tool_type: str, tool: str):
        """Clear cache for a specific tool."""
        cache_key = f"{language}:{tool_type}:{tool}"
        if cache_key in self.cache:
            del self.cache[cache_key]

    def _ensure_required_runtime(
        self, install_method: str, tool: str
    ) -> Tuple[bool, Optional[str]]:
        """Ensure the required runtime (python/node) is available before installing a tool.

        Returns:
            (True, None) if runtime is available or successfully installed; otherwise (False, error_message).
        """
        try:
            # Lazy import to avoid circular dependencies at module import time
            from .runtime_manager import runtime_manager
        except Exception as e:
            return False, f"Failed to import runtime manager: {e}"

        # Determine required runtime based on installation method or tool specifics
        required_runtime = None
        if install_method == "pip":
            required_runtime = "python"
        elif install_method == "npm" or tool in ("cspell",):
            required_runtime = "node"

        if not required_runtime:
            return False, "Unknown installation method for runtime requirement"

        # Check runtime availability
        runtime_check = runtime_manager.check_runtime(required_runtime)
        if runtime_check.success:
            return True, None

        # Attempt to install the missing runtime automatically
        runtime_install = runtime_manager.install_runtime(required_runtime)
        if runtime_install.success:
            return True, None

        return (
            False,
            runtime_install.error or f"Failed to ensure runtime {required_runtime}",
        )


# GLOBAL INSTANCE
########################################################

dev_tools_manager = DevToolsManager()
