#!/usr/bin/env python3
"""
Python Linting Tools - Python-specific linting functionality.
Handles ruff, black, isort, bandit with their specific configurations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from ....common.results import ToolResult
from .lint_utils import check_tool_availability, run_tool_check, run_tool_fix


class PythonLintingTools:
    """Manages Python-specific linting tools (ruff, black, isort, bandit)."""

    TOOLS_CONFIG = {
        "ruff": {
            "check_args": ["check", "--no-fix"],
            "fix_args": ["check", "--fix"],
            "json_support": True,
        },
        "black": {
            "check_args": ["--check", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "isort": {
            "check_args": ["--check-only", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "bandit": {
            "check_args": ["-r", "-f", "json"],
            "fix_args": [],  # bandit doesn't have fix mode
            "json_support": True,
        },
    }

    def __init__(self):
        """Initialize Python linting tools manager."""
        self._available_tools: Optional[Dict[str, bool]] = None

    def get_available_tools(self) -> Dict[str, bool]:
        """
        Get dictionary of available Python linting tools.

        Returns:
            Dict[str, bool]: Tool name -> availability status
        """
        if self._available_tools is None:
            self._available_tools = {}
            for tool_name in self.TOOLS_CONFIG:
                self._available_tools[tool_name] = check_tool_availability(tool_name)
                if self._available_tools[tool_name]:
                    logging.debug(f"✓ {tool_name} is available")
                else:
                    logging.debug(f"✗ {tool_name} is not available")

        return self._available_tools

    def check_python_code(
        self, target_dirs: List[str], cwd: Path, tools: Optional[List[str]] = None
    ) -> Dict[str, ToolResult]:
        """
        Run Python linting tools in check mode.

        Args:
            target_dirs: List of directories/files to lint
            cwd: Working directory
            tools: Specific tools to run (if None, run all available)

        Returns:
            Dict[str, ToolResult]: Tool name -> result mapping
        """
        available_tools = self.get_available_tools()
        tools_to_run = tools or [
            t for t, available in available_tools.items() if available
        ]

        results = {}
        for tool_name in tools_to_run:
            if not available_tools.get(tool_name, False):
                logging.warning(f"Tool {tool_name} is not available, skipping")
                continue

            config = self.TOOLS_CONFIG[tool_name]
            try:
                result = run_tool_check(
                    tool_name=tool_name,
                    args=config["check_args"],
                    target_dirs=target_dirs,
                    cwd=cwd,
                    json_output=config["json_support"],
                )
                results[tool_name] = result
                logging.debug(f"✓ {tool_name} check completed")
            except Exception as exc:
                logging.error(f"Failed to run {tool_name}: {exc}")
                results[tool_name] = ToolResult(
                    success=False,
                    tool_name=tool_name,
                    message=f"Failed to execute {tool_name}: {str(exc)}",
                )

        return results

    def fix_python_code(
        self, target_dirs: List[str], cwd: Path, tools: Optional[List[str]] = None
    ) -> Dict[str, ToolResult]:
        """
        Run Python linting tools in fix mode.

        Args:
            target_dirs: List of directories/files to fix
            cwd: Working directory
            tools: Specific tools to run (if None, run all available fixable tools)

        Returns:
            Dict[str, ToolResult]: Tool name -> result mapping
        """
        available_tools = self.get_available_tools()
        fixable_tools = [
            t
            for t, config in self.TOOLS_CONFIG.items()
            if config["fix_args"]
            or t in ["black", "isort"]  # these tools fix by default
        ]
        tools_to_run = tools or [
            t for t in fixable_tools if available_tools.get(t, False)
        ]

        results = {}
        for tool_name in tools_to_run:
            if not available_tools.get(tool_name, False):
                logging.warning(f"Tool {tool_name} is not available, skipping")
                continue

            config = self.TOOLS_CONFIG[tool_name]
            fix_args = config["fix_args"]

            # For tools that fix by default (black, isort), use empty args
            if not fix_args and tool_name in ["black", "isort"]:
                fix_args = []

            if tool_name == "bandit":
                # Bandit doesn't have fix mode, skip
                logging.info(f"Skipping {tool_name} - no fix mode available")
                continue

            try:
                result = run_tool_fix(
                    tool_name=tool_name, args=fix_args, target_dirs=target_dirs, cwd=cwd
                )
                results[tool_name] = result
                logging.debug(f"✓ {tool_name} fix completed")
            except Exception as exc:
                logging.error(f"Failed to run {tool_name}: {exc}")
                results[tool_name] = ToolResult(
                    success=False,
                    tool_name=tool_name,
                    message=f"Failed to execute {tool_name}: {str(exc)}",
                )

        return results

    def get_tool_summary(self) -> Dict[str, str]:
        """
        Get summary of tool availability and versions.

        Returns:
            Dict[str, str]: Tool name -> status/version string
        """
        from ..cli_utils import get_tool_version

        available_tools = self.get_available_tools()
        summary = {}

        for tool_name, is_available in available_tools.items():
            if is_available:
                version = get_tool_version(tool_name)
                summary[tool_name] = version or "Available (version unknown)"
            else:
                summary[tool_name] = "Not available"

        return summary
