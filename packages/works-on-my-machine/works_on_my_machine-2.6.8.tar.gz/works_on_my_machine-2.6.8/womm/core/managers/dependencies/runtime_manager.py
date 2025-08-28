#!/usr/bin/env python3
"""
Runtime Manager for Works On My Machine.
Manages runtime dependencies (Python, Node.js, Git).
"""

import logging
import platform
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ....common.results import BaseResult
from ...utils.cli_utils import check_tool_available, run_silent


@dataclass
class RuntimeResult(BaseResult):
    """Result of a runtime operation."""

    runtime_name: str = ""
    version: Optional[str] = None
    path: Optional[str] = None


# RUNTIME DEFINITIONS
########################################################

RUNTIMES = {
    "python": {
        "version": "3.9+",
        "priority": 1,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "Python.Python.3.11",
            "chocolatey": "python",
            "homebrew": "python@3.11",
            "apt": "python3",
            "dnf": "python3",
            "pacman": "python",
        },
    },
    "node": {
        "version": "18+",
        "priority": 2,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "OpenJS.NodeJS",
            "chocolatey": "nodejs",
            "homebrew": "node",
            "apt": "nodejs",
            "dnf": "nodejs",
            "pacman": "nodejs",
        },
    },
    "git": {
        "version": "2.30+",
        "priority": 3,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "Git.Git",
            "chocolatey": "git",
            "homebrew": "git",
            "apt": "git",
            "dnf": "git",
            "pacman": "git",
        },
    },
}


# MAIN CLASS
########################################################


class RuntimeManager:
    """Manages runtime dependencies (Python, Node.js, Git)."""

    def __init__(self):
        self.system = platform.system()
        self.cache = {}

    def check_runtime(self, runtime: str) -> RuntimeResult:
        """Check if a runtime is installed."""

        from ...ui.common.progress import create_spinner

        with create_spinner(f"Checking [bold cyan]{runtime}[/bold cyan]...") as (
            progress,
            task,
        ):
            if runtime not in RUNTIMES:
                progress.update(task, description=f"Runtime {runtime} not supported")
                return RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"Runtime {runtime} not supported",
                    error=f"Runtime {runtime} not supported",
                )

            # Check cache first
            if runtime in self.cache:
                available, version = self.cache[runtime]
                progress.update(
                    task, description=f"Runtime {runtime} already installed"
                )
                return RuntimeResult(
                    success=available,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime) if available else None,
                    message=f"Runtime {runtime} {'available' if available else 'not found'}",
                    error=None if available else f"Runtime {runtime} not installed",
                )

            # Check runtime
            available, version = self._check_runtime_installation(runtime)
            self.cache[runtime] = (available, version)

            progress.update(
                task,
                description=f"Runtime {runtime} {'available' if available else 'not found'}",
            )
            return RuntimeResult(
                success=available,
                runtime_name=runtime,
                version=version,
                path=shutil.which(runtime) if available else None,
                message=f"Runtime {runtime} {'available' if available else 'not found'}",
                error=None if available else f"Runtime {runtime} not installed",
            )

    def install_runtime(
        self, runtime: str, extra_pm_args: Optional[List[str]] = None
    ) -> RuntimeResult:
        """Install a runtime."""
        from ...ui.common.progress import create_spinner

        with create_spinner(f"Installing [bold cyan]{runtime}[/bold cyan]...") as (
            progress,
            task,
        ):
            if runtime not in RUNTIMES:
                return RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"Runtime {runtime} not supported",
                    error=f"Runtime {runtime} not supported",
                )

            # Check if already installed
            available, version = self._check_runtime_installation(runtime)
            if available:
                progress.update(
                    task,
                    description=f"Runtime {runtime} already installed (version {version})",
                )
                return RuntimeResult(
                    success=True,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime),
                    message=f"Runtime {runtime} already installed (version {version})",
                )

            # Ensure a package manager is available
            from .package_manager import package_manager

            preferred = RUNTIMES[runtime].get("package_managers")
            pm_result = package_manager.ensure_manager(preferred)
            if not pm_result.success:
                progress.update(
                    task,
                    description=f"No package manager available for {runtime}",
                )
                # Optionally print the tips panel if present
                if getattr(pm_result, "panel", None) is not None:
                    from ...ui.common.console import console

                    console.print(pm_result.panel)

                return RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"No package manager available for {runtime}",
                    error=pm_result.error or "no_package_manager",
                )

            # Get package name
            package_name = RUNTIMES[runtime]["package_names"].get(
                pm_result.package_manager_name
            )
            if not package_name:
                progress.update(
                    task,
                    description=f"No package found for {runtime} in {pm_result.package_manager_name}",
                )
                return RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"No package found for {runtime} in {pm_result.package_manager_name}",
                    error=f"No package found for {runtime} in {pm_result.package_manager_name}",
                )

            # Install via package manager
            success = package_manager.install_package(
                package_name,
                pm_result.package_manager_name,
                extra_args=extra_pm_args,
            ).success

            if success:
                # Re-check after installation
                available, version = self._check_runtime_installation(runtime)
                self.cache[runtime] = (available, version)

                return RuntimeResult(
                    success=True,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime) if available else None,
                    message=f"Runtime {runtime} installed successfully",
                )
            else:
                return RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"Failed to install runtime {runtime}",
                    error="Installation failed",
                )

    def check_and_install_runtimes(
        self, runtimes: List[str]
    ) -> Dict[str, RuntimeResult]:
        """Check and install multiple runtimes."""
        results = {}

        for runtime in runtimes:
            if runtime not in RUNTIMES:
                results[runtime] = RuntimeResult(
                    success=False,
                    runtime_name=runtime,
                    message=f"Runtime {runtime} not supported",
                    error=f"Runtime {runtime} not supported",
                )
                continue

            # Check if already installed
            available, version = self._check_runtime_installation(runtime)
            if available:
                results[runtime] = RuntimeResult(
                    success=True,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime),
                    message=f"Runtime {runtime} already installed",
                )
            else:
                # Install runtime
                results[runtime] = self.install_runtime(runtime)

        return results

    def get_installation_status(self, runtimes: List[str] = None) -> Dict[str, Dict]:
        """Get comprehensive installation status for runtimes."""

        from ...ui.common.progress import create_spinner

        if runtimes is None:
            runtimes = list(RUNTIMES.keys())

        status = {}
        for runtime in runtimes:
            with create_spinner(f"Checking [bold cyan]{runtime}[/bold cyan]...") as (
                progress,
                task,
            ):
                available, version = self._check_runtime_installation(runtime)
                status[runtime] = {
                    "installed": available,
                    "version": version,
                    "path": shutil.which(runtime) if available else None,
                    "supported": runtime in RUNTIMES,
                }
                progress.update(
                    task,
                    description=f"Runtime {runtime} {'available' if available else 'not found'}",
                )

        return status

    def _check_runtime_installation(self, runtime: str) -> Tuple[bool, Optional[str]]:
        """Check if a runtime is installed and return version."""
        if runtime == "python":
            return self._check_python()
        elif runtime == "node":
            return self._check_node()
        elif runtime == "git":
            return self._check_git()
        else:
            return False, None

    def _check_python(self) -> Tuple[bool, Optional[str]]:
        """Check Python installation."""
        python_cmds = ["python3", "python", "py"]

        for cmd in python_cmds:
            if check_tool_available(cmd):
                try:
                    result = run_silent([cmd, "--version"])
                    if result.success and result.stdout.strip():
                        version = result.stdout.strip().split()[1]
                        version_parts = [int(x) for x in version.split(".")]
                        if version_parts >= [3, 8]:
                            # Optional: enforce minimum version from config
                            min_spec = RUNTIMES["python"].get("version")
                            if self._satisfies_min_version(version, min_spec):
                                return True, version
                except (IndexError, ValueError):
                    continue

        return False, None

    def _check_node(self) -> Tuple[bool, Optional[str]]:
        """Check Node.js installation."""
        if check_tool_available("node"):
            try:
                result = run_silent(["node", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().lstrip("v")
                    # Enforce minimum version if specified
                    min_spec = RUNTIMES["node"].get("version")
                    if self._satisfies_min_version(version, min_spec):
                        return True, version
            except (IndexError, ValueError) as e:
                logging.debug(f"Failed to get version for node: {e}")
                # Continue as version check failure is not critical

        return False, None

    def _check_git(self) -> Tuple[bool, Optional[str]]:
        """Check Git installation."""
        if check_tool_available("git"):
            try:
                result = run_silent(["git", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().split()[2]
                    min_spec = RUNTIMES["git"].get("version")
                    if self._satisfies_min_version(version, min_spec):
                        return True, version
            except (IndexError, ValueError) as e:
                logging.debug(f"Failed to get version for git: {e}")
                # Continue as version check failure is not critical

        return False, None

    def _satisfies_min_version(
        self, actual: Optional[str], min_spec: Optional[str]
    ) -> bool:
        """Return True if actual version satisfies min_spec like '18+' or '2.30+'.

        If min_spec is None or invalid, default to True.
        """
        if not actual or not min_spec or not min_spec.endswith("+"):
            return True
        try:
            min_version = min_spec[:-1]

            def parse(v: str) -> List[int]:
                return [int(x) for x in v.split(".") if x.isdigit()]

            a = parse(actual)
            m = parse(min_version)
            # pad shorter list with zeros
            length = max(len(a), len(m))
            a += [0] * (length - len(a))
            m += [0] * (length - len(m))
            return a >= m
        except Exception:
            return True


# GLOBAL INSTANCE
########################################################

runtime_manager = RuntimeManager()
