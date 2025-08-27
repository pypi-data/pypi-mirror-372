#!/usr/bin/env python3
"""
Linting manager for WOMM projects.
Centralizes linting logic and provides structured results.
Refactored to use modular utilities and follow architectural patterns.
"""

from pathlib import Path
from typing import List, Optional

from ....common.results import LintSummary
from ...ui.common.console import print_header
from ...ui.common.extended import ProgressAnimations, create_dynamic_layered_progress
from ...utils.file_scanner import FileScanner
from ...utils.lint.python_linting import PythonLintingTools


class LintManager:
    """
    Manages linting operations for different languages and tools.
    Refactored to use modular utilities and follow architectural patterns.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize lint manager.

        Args:
            project_root: Root directory of the project (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.file_scanner = FileScanner()
        self.python_tools = PythonLintingTools()

    def check_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in check mode.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)

        Returns:
            LintSummary: Summary of linting results
        """
        print_header("🔍 Checking Python Code")

        # Define stages for dynamic progress
        stages = [
            {
                "name": "main_linting",
                "type": "main",
                "steps": ["File Scan", "Tool Execution", "Analysis"],
                "description": "Python Linting Progress",
                "style": "bold bright_white",
            },
            {
                "name": "file_scan",
                "type": "spinner",
                "description": "Scanning Python files...",
                "style": "bright_cyan",
            },
            {
                "name": "tool_execution",
                "type": "spinner",
                "description": "Running linting tools...",
                "style": "bright_yellow",
            },
            {
                "name": "analysis",
                "type": "spinner",
                "description": "Analyzing results...",
                "style": "bright_green",
            },
        ]

        with create_dynamic_layered_progress(stages) as progress:
            animations = ProgressAnimations(progress.progress)

            # Stage 1: File Scan
            progress.update_layer(
                "file_scan", 0, "Scanning project for Python files..."
            )
            python_files = self._get_target_files(target_paths)
            if not python_files:
                # Apply error pulse animation before emergency stop
                file_scan_task_id = progress._get_task_id_by_name("file_scan")
                if file_scan_task_id:
                    animations.error_pulse(file_scan_task_id)
                progress.emergency_stop("No Python files found to check")
                return LintSummary(
                    success=False, message="No Python files found to check"
                )

            scan_summary = self.file_scanner.get_scan_summary(python_files)
            progress.update_layer(
                "file_scan", 50, f"Found {len(python_files)} Python files"
            )
            progress.update_layer("file_scan", 100, "File scan completed")
            progress.complete_layer("file_scan")
            # Apply success flash animation when file scan completes
            file_scan_task_id = progress._get_task_id_by_name("file_scan")
            if file_scan_task_id:
                animations.success_flash(file_scan_task_id)
            progress.update_layer("main_linting", 0, "File scan completed")

            # Stage 2: Tool Execution
            progress.update_layer("tool_execution", 0, "Preparing tools...")
            target_dirs = [str(f) for f in python_files]

            available_tools = self.python_tools.get_available_tools()
            tools_to_run = tools or [
                t for t, available in available_tools.items() if available
            ]

            progress.update_layer(
                "tool_execution", 25, f"Running {len(tools_to_run)} tools..."
            )

            # Apply smooth progress animation during tool execution
            tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
            if tool_exec_task_id:
                animations.smooth_progress(tool_exec_task_id, 75, duration=2.0)

            tool_results = self.python_tools.check_python_code(
                target_dirs=target_dirs, cwd=self.project_root, tools=tools
            )

            progress.update_layer("tool_execution", 100, "Tool execution completed")
            progress.complete_layer("tool_execution")
            # Apply success flash animation when tool execution completes
            tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
            if tool_exec_task_id:
                animations.success_flash(tool_exec_task_id)
            progress.update_layer("main_linting", 1, "Tool execution completed")

            # Stage 3: Analysis
            progress.update_layer("analysis", 0, "Calculating results...")
            total_issues = sum(result.issues_found for result in tool_results.values())
            progress.update_layer("analysis", 100, f"Found {total_issues} issues")
            progress.complete_layer("analysis")
            # Apply success flash animation when analysis completes
            analysis_task_id = progress._get_task_id_by_name("analysis")
            if analysis_task_id:
                animations.success_flash(analysis_task_id)
            progress.update_layer("main_linting", 2, "Analysis completed")

        # Calculate totals
        total_issues = sum(result.issues_found for result in tool_results.values())

        summary = LintSummary(
            success=all(result.success for result in tool_results.values()),
            message=f"Checked {len(python_files)} files with {len(tool_results)} tools",
            total_files=len(python_files),
            total_issues=total_issues,
            tool_results=tool_results,
            scan_summary=scan_summary,
        )

        return summary

    def fix_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in fix mode.

        Args:
            target_paths: Specific paths to fix (if None, scan entire project)
            tools: Specific tools to run (if None, run all available fixable tools)

        Returns:
            LintSummary: Summary of fixing results
        """
        print_header("🔍 Fixing Python Code")

        # Define stages for dynamic progress
        stages = [
            {
                "name": "main_fixing",
                "type": "main",
                "steps": ["File Scan", "Tool Execution", "Analysis"],
                "description": "Python Code Fixing Progress",
                "style": "bold bright_white",
            },
            {
                "name": "file_scan",
                "type": "spinner",
                "description": "Scanning Python files...",
                "style": "bright_cyan",
            },
            {
                "name": "tool_execution",
                "type": "spinner",
                "description": "Running fixing tools...",
                "style": "bright_yellow",
            },
            {
                "name": "analysis",
                "type": "spinner",
                "description": "Analyzing results...",
                "style": "bright_green",
            },
        ]

        with create_dynamic_layered_progress(stages) as progress:
            animations = ProgressAnimations(progress.progress)

            # Stage 1: File Scan
            progress.update_layer(
                "file_scan", 0, "Scanning project for Python files..."
            )
            python_files = self._get_target_files(target_paths)
            if not python_files:
                # Apply error pulse animation before emergency stop
                file_scan_task_id = progress._get_task_id_by_name("file_scan")
                if file_scan_task_id:
                    animations.error_pulse(file_scan_task_id)
                progress.emergency_stop("No Python files found to fix")
                return LintSummary(
                    success=False, message="No Python files found to fix"
                )

            scan_summary = self.file_scanner.get_scan_summary(python_files)
            progress.update_layer(
                "file_scan", 50, f"Found {len(python_files)} Python files"
            )
            progress.update_layer("file_scan", 100, "File scan completed")
            progress.complete_layer("file_scan")
            # Apply success flash animation when file scan completes
            file_scan_task_id = progress._get_task_id_by_name("file_scan")
            if file_scan_task_id:
                animations.success_flash(file_scan_task_id)
            progress.update_layer("main_fixing", 0, "File scan completed")

            # Stage 2: Tool Execution
            progress.update_layer("tool_execution", 0, "Preparing fixing tools...")
            target_dirs = [str(f) for f in python_files]

            available_tools = self.python_tools.get_available_tools()
            tools_to_run = tools or [
                t for t, available in available_tools.items() if available
            ]

            progress.update_layer(
                "tool_execution", 25, f"Running {len(tools_to_run)} fixing tools..."
            )

            # Apply smooth progress animation during tool execution
            tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
            if tool_exec_task_id:
                animations.smooth_progress(tool_exec_task_id, 75, duration=2.0)

            tool_results = self.python_tools.fix_python_code(
                target_dirs=target_dirs, cwd=self.project_root, tools=tools
            )

            progress.update_layer("tool_execution", 100, "Tool execution completed")
            progress.complete_layer("tool_execution")
            # Apply success flash animation when tool execution completes
            tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
            if tool_exec_task_id:
                animations.success_flash(tool_exec_task_id)
            progress.update_layer("main_fixing", 1, "Tool execution completed")

            # Stage 3: Analysis
            progress.update_layer("analysis", 0, "Calculating results...")
            total_fixed = sum(result.fixed_issues for result in tool_results.values())
            progress.update_layer("analysis", 100, f"Fixed {total_fixed} issues")
            progress.complete_layer("analysis")
            # Apply success flash animation when analysis completes
            analysis_task_id = progress._get_task_id_by_name("analysis")
            if analysis_task_id:
                animations.success_flash(analysis_task_id)
            progress.update_layer("main_fixing", 2, "Analysis completed")

        # Calculate totals
        total_fixed = sum(result.fixed_issues for result in tool_results.values())

        summary = LintSummary(
            success=all(result.success for result in tool_results.values()),
            message=f"Processed {len(python_files)} files with {len(tool_results)} tools",
            total_files=len(python_files),
            total_fixed=total_fixed,
            tool_results=tool_results,
            scan_summary=scan_summary,
        )

        return summary

    def get_tool_status(self) -> dict:
        """
        Get status of all available linting tools.

        Returns:
            dict: Tool availability and version information
        """
        print_header("🔍 Linting Tools Status")
        return self.python_tools.get_tool_summary()

    def _get_target_files(self, target_paths: Optional[List[str]]) -> List[Path]:
        """
        Get list of Python files to process.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)

        Returns:
            List[Path]: List of Python files to process
        """
        if not target_paths:
            # Scan entire project
            return self.file_scanner.get_project_python_files(self.project_root)

        # Process specific paths
        python_files = []
        for path_str in target_paths:
            path = Path(path_str)
            # Don't modify the path if it's already absolute
            # If it's relative, resolve it from current working directory, not project_root
            if not path.is_absolute():
                path = Path.cwd() / path

            python_files.extend(
                self.file_scanner.find_python_files(path, recursive=True)
            )

        return python_files
