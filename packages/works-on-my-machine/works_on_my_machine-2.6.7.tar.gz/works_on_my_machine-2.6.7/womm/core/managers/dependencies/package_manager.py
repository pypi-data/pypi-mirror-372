#!/usr/bin/env python3
"""
Package Manager for Works On My Machine.
Manages system package managers (winget, chocolatey, homebrew, apt, etc.).
"""

import logging
import os
import platform
import shlex
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ....common.results import BaseResult
from ...ui.common.panels import create_info_panel
from ...utils.cli_utils import check_tool_available, run_command, run_silent


@dataclass
class PackageManagerResult(BaseResult):
    """Result of a package manager operation."""

    package_manager_name: str = ""
    version: Optional[str] = None
    platform: Optional[str] = None
    priority: Optional[int] = None
    panel: Optional[Any] = None


# PACKAGE MANAGER DEFINITIONS
########################################################

SYSTEM_PACKAGE_MANAGERS = {
    "winget": {
        "platform": "windows",
        "priority": 1,
        "description": "Microsoft Windows Package Manager",
        "install_command": "winget install",
        "search_command": "winget search",
        "list_command": "winget list",
    },
    "chocolatey": {
        "platform": "windows",
        "priority": 2,
        "description": "Chocolatey Package Manager",
        "install_command": "choco install",
        "search_command": "choco search",
        "list_command": "choco list",
    },
    "scoop": {
        "platform": "windows",
        "priority": 3,
        "description": "Scoop Package Manager",
        "install_command": "scoop install",
        "search_command": "scoop search",
        "list_command": "scoop list",
    },
    "homebrew": {
        "platform": "darwin",
        "priority": 1,
        "description": "Homebrew Package Manager",
        "install_command": "brew install",
        "search_command": "brew search",
        "list_command": "brew list",
    },
    "apt": {
        "platform": "linux",
        "priority": 1,
        "description": "Advanced Package Tool (Debian/Ubuntu)",
        "install_command": "apt install",
        "search_command": "apt search",
        "list_command": "apt list --installed",
    },
    "dnf": {
        "platform": "linux",
        "priority": 2,
        "description": "Dandified YUM (Fedora/RHEL)",
        "install_command": "dnf install",
        "search_command": "dnf search",
        "list_command": "dnf list installed",
    },
    "pacman": {
        "platform": "linux",
        "priority": 3,
        "description": "Pacman Package Manager (Arch Linux)",
        "install_command": "pacman -S",
        "search_command": "pacman -Ss",
        "list_command": "pacman -Q",
    },
    "zypper": {
        "platform": "linux",
        "priority": 4,
        "description": "Zypper Package Manager (openSUSE)",
        "install_command": "zypper install",
        "search_command": "zypper search",
        "list_command": "zypper packages --installed",
    },
}


# MAIN CLASS
########################################################


class PackageManager:
    """Manages system package managers."""

    def __init__(self):
        self.system = platform.system()
        self.cache = {}

    def detect_available_managers(self) -> Dict[str, PackageManagerResult]:
        """Detect all available package managers for the current system."""
        results = {}

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
            if self._is_manager_for_current_platform(config):
                result = self.check_package_manager(manager_name)
                results[manager_name] = result

        return results

    def check_package_manager(self, manager_name: str) -> PackageManagerResult:
        """Check if a package manager is available."""
        from ...ui.common.console import print_system
        from ...ui.common.progress import create_spinner

        print_system(f"Checking [bold cyan]{manager_name}[/bold cyan]...")

        with create_spinner(f"Checking [bold cyan]{manager_name}[/bold cyan]...") as (
            progress,
            task,
        ):
            if manager_name not in SYSTEM_PACKAGE_MANAGERS:
                progress.update(
                    task,
                    description=f"Package manager {manager_name} not supported",
                )
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    message=f"Package manager {manager_name} not supported",
                    error=f"Package manager {manager_name} not supported",
                )

            # Check cache first
            if manager_name in self.cache:
                available, version = self.cache[manager_name]
                config = SYSTEM_PACKAGE_MANAGERS[manager_name]
                progress.update(
                    task,
                    description=f"Package manager {manager_name} {'available' if available else 'not found'}",
                )
                return PackageManagerResult(
                    success=available,
                    package_manager_name=manager_name,
                    version=version,
                    platform=config["platform"],
                    priority=config["priority"],
                    message=f"Package manager {manager_name} {'available' if available else 'not found'}",
                    error=(
                        None
                        if available
                        else f"Package manager {manager_name} not installed"
                    ),
                )

            # Check if manager is available
            available, version = self._check_manager_availability(manager_name)
            self.cache[manager_name] = (available, version)

            config = SYSTEM_PACKAGE_MANAGERS[manager_name]
            progress.update(
                task,
                description=f"Package manager {manager_name} {'available' if available else 'not found'}",
            )
            return PackageManagerResult(
                success=available,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Package manager {manager_name} {'available' if available else 'not found'}",
                error=(
                    None
                    if available
                    else f"Package manager {manager_name} not installed"
                ),
            )

    def get_best_available_manager(self) -> Optional[str]:
        """Get the best available package manager for the current system."""
        available_managers = []

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
            if self._is_manager_for_current_platform(config):
                available, _ = self._check_manager_availability(manager_name)
                if available:
                    available_managers.append((manager_name, config["priority"]))

        if available_managers:
            # Sort by priority (lower number = higher priority)
            available_managers.sort(key=lambda x: x[1])
            return available_managers[0][0]

        return None

    def ensure_manager(
        self, preferred: Optional[List[str]] = None
    ) -> PackageManagerResult:
        """Ensure that at least one package manager is available.

        - If one of the preferred (or platform-supported) managers is available, return it.
        - Otherwise, return a failure result with a Rich Panel containing tips to install one.
        """

        # Build candidate list
        def is_supported(m: str) -> bool:
            cfg = SYSTEM_PACKAGE_MANAGERS.get(m)
            return bool(cfg and self._is_manager_for_current_platform(cfg))

        candidates: List[str]
        if preferred:
            candidates = [m for m in preferred if is_supported(m)]
        else:
            candidates = [
                m
                for m, cfg in SYSTEM_PACKAGE_MANAGERS.items()
                if self._is_manager_for_current_platform(cfg)
            ]

        # Gather available with priorities
        available: List[tuple[str, int]] = []
        for m in candidates:
            ok, _ = self._check_manager_availability(m)
            if ok:
                available.append((m, SYSTEM_PACKAGE_MANAGERS[m]["priority"]))

        if available:
            available.sort(key=lambda x: x[1])
            best = available[0][0]
            ver = self._check_manager_availability(best)[1]
            return PackageManagerResult(
                success=True,
                package_manager_name=best,
                version=ver,
                platform=SYSTEM_PACKAGE_MANAGERS[best]["platform"],
                priority=SYSTEM_PACKAGE_MANAGERS[best]["priority"],
                message=f"Using package manager: {best}",
            )

        # No manager available → provide tips panel
        panel = self._build_no_pm_panel(candidates)
        return PackageManagerResult(
            success=False,
            package_manager_name="none",
            message="No package manager available on this system",
            error="no_package_manager",
            panel=panel,
        )

    def _build_no_pm_panel(self, candidates: List[str]) -> Any:
        """Create a tips panel to guide user to install a package manager safely.

        The candidates list is used to indicate which managers are acceptable for the current operation.
        """
        sys_name = self.system.lower()

        supported_on_platform = [
            m
            for m, cfg in SYSTEM_PACKAGE_MANAGERS.items()
            if self._is_manager_for_current_platform(cfg)
        ]

        header: List[str] = []
        if sys_name == "windows":
            header.append(
                "Aucun gestionnaire de paquets détecté (winget/chocolatey/scoop)."
            )
        elif sys_name == "darwin":
            header.append("Aucun gestionnaire de paquets détecté (Homebrew).")
        else:
            header.append(
                "Aucun gestionnaire de paquets détecté (apt/dnf/pacman/zypper)."
            )

        if candidates:
            header.append(
                "Candidats compatibles pour cette opération: " + ", ".join(candidates)
            )
        else:
            header.append(
                "Gestionnaires supportés sur cette plateforme: "
                + ", ".join(supported_on_platform)
            )

        header.append("")

        if sys_name == "windows":
            body = [
                "Recommandé:",
                "- winget (Microsoft Store): ouvrez le Microsoft Store et installez 'App Installer'.",
                "- Chocolatey: PowerShell (Run as Administrator):",
                "  Set-ExecutionPolicy Bypass -Scope Process -Force;",
                "  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12;",
                "  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
                "- Scoop: PowerShell (Run as Administrator):",
                "  iwr -useb get.scoop.sh | iex",
            ]
        elif sys_name == "darwin":
            body = [
                "Installez Homebrew:",
                "- Ouvrez le Terminal puis exécutez:",
                '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            ]
        else:
            body = [
                "Vérifiez votre distribution Linux et assurez-vous que l'outil par défaut est installé et accessible dans le PATH.",
            ]

        content = "\n".join(header + body)
        return create_info_panel(
            "Gestionnaire de paquets requis",
            content,
            style="yellow",
            border_style="yellow",
        )

    def install_package(
        self,
        package_name: str,
        manager_name: str = None,
        extra_args: Optional[list[str]] = None,
    ) -> PackageManagerResult:
        """Install a package using the specified or best available package manager."""
        # DRY-RUN: skip real installation when WOMM_DRY_RUN is enabled
        if os.environ.get("WOMM_DRY_RUN", "").lower() in ("1", "true", "yes"):
            selected_manager = manager_name or self.get_best_available_manager()
            if not selected_manager:
                return PackageManagerResult(
                    success=False,
                    package_manager_name="none",
                    message="No package manager available (dry-run)",
                    error="No package manager available",
                )
            cfg = SYSTEM_PACKAGE_MANAGERS.get(selected_manager, {})
            args_desc = f" args={extra_args}" if extra_args else ""
            return PackageManagerResult(
                success=True,
                package_manager_name=selected_manager,
                version=None,
                platform=cfg.get("platform"),
                priority=cfg.get("priority"),
                message=f"[dry-run] Would install {package_name} via {selected_manager}{args_desc}",
            )
        if manager_name is None:
            manager_name = self.get_best_available_manager()
            if not manager_name:
                return PackageManagerResult(
                    success=False,
                    package_manager_name="none",
                    message="No package manager available",
                    error="No package manager available",
                )

        if manager_name not in SYSTEM_PACKAGE_MANAGERS:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not supported",
                error=f"Package manager {manager_name} not supported",
            )

        # Check if manager is available
        available, version = self._check_manager_availability(manager_name)
        if not available:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not available",
                error=f"Package manager {manager_name} not installed",
            )

        # Install package
        success = self._install_package_via_manager(
            manager_name, package_name, extra_args=extra_args
        )

        config = SYSTEM_PACKAGE_MANAGERS[manager_name]
        if success:
            return PackageManagerResult(
                success=True,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Package {package_name} installed successfully via {manager_name}",
            )
        else:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Failed to install package {package_name} via {manager_name}",
                error="Installation failed",
            )

    def search_package(
        self, package_name: str, manager_name: str = None
    ) -> PackageManagerResult:
        """Search for a package using the specified or best available package manager."""
        if manager_name is None:
            manager_name = self.get_best_available_manager()
            if not manager_name:
                return PackageManagerResult(
                    success=False,
                    package_manager_name="none",
                    message="No package manager available",
                    error="No package manager available",
                )

        if manager_name not in SYSTEM_PACKAGE_MANAGERS:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not supported",
                error=f"Package manager {manager_name} not supported",
            )

        # Check if manager is available
        available, version = self._check_manager_availability(manager_name)
        if not available:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not available",
                error=f"Package manager {manager_name} not installed",
            )

        # Search package
        result = self._search_package_via_manager(manager_name, package_name)

        config = SYSTEM_PACKAGE_MANAGERS[manager_name]
        if result.success:
            return PackageManagerResult(
                success=True,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Search results for {package_name} via {manager_name}",
                error=None,
            )
        else:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Failed to search for {package_name} via {manager_name}",
                error=result.stderr,
            )

    def get_installation_status(self) -> Dict[str, Dict]:
        """Get comprehensive status of all package managers."""
        status = {}

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
            available, version = self._check_manager_availability(manager_name)
            status[manager_name] = {
                "available": available,
                "version": version,
                "platform": config["platform"],
                "priority": config["priority"],
                "description": config["description"],
                "supported_on_current_platform": self._is_manager_for_current_platform(
                    config
                ),
            }

        return status

    def _is_manager_for_current_platform(self, config: Dict) -> bool:
        """Check if a package manager is supported on the current platform."""
        return (
            config["platform"] == self.system.lower() or config["platform"] == "linux"
        )

    def _check_manager_availability(
        self, manager_name: str
    ) -> tuple[bool, Optional[str]]:
        """Check if a package manager is available and return version."""
        if not check_tool_available(manager_name):
            return False, None

        # Try to get version
        try:
            result = run_silent([manager_name, "--version"])
            if result.success and result.stdout.strip():
                version = (
                    result.stdout.strip().split()[0]
                    if result.stdout.strip()
                    else "unknown"
                )
                return True, version
        except Exception as e:
            logging.debug(f"Failed to get version for {manager_name}: {e}")
            # Continue execution as version check failure is not critical

        return False, None

    def _install_package_via_manager(
        self,
        manager_name: str,
        package_name: str,
        extra_args: Optional[list[str]] = None,
    ) -> bool:
        """Install a package via a specific package manager."""
        SYSTEM_PACKAGE_MANAGERS[manager_name]

        if manager_name == "winget":
            cmd = ["winget", "install", package_name, "--accept-source-agreements"]
        elif manager_name == "chocolatey":
            cmd = ["choco", "install", package_name, "-y"]
        elif manager_name == "scoop":
            cmd = ["scoop", "install", package_name]
        elif manager_name == "homebrew":
            cmd = ["brew", "install", package_name]
        elif manager_name == "apt":
            cmd = [
                "sudo",
                "apt",
                "update",
                "&&",
                "sudo",
                "apt",
                "install",
                "-y",
                package_name,
            ]
        elif manager_name == "dnf":
            cmd = ["sudo", "dnf", "install", "-y", package_name]
        elif manager_name == "pacman":
            cmd = ["sudo", "pacman", "-S", "--noconfirm", package_name]
        elif manager_name == "zypper":
            cmd = ["sudo", "zypper", "install", "-y", package_name]
        else:
            return False

        # Append any extra args provided by the user
        if extra_args:
            # If user provided a raw string somewhere else, ensure we have tokens
            flattened: list[str] = []
            for a in extra_args:
                if isinstance(a, str):
                    # Split only if it contains spaces and not already a token
                    tokens = shlex.split(a) if " " in a else [a]
                    flattened.extend(tokens)
                else:
                    flattened.append(str(a))
            cmd.extend(flattened)

        result = run_command(cmd)
        return result.success

    def _search_package_via_manager(self, manager_name: str, package_name: str):
        """Search for a package via a specific package manager."""
        search_commands = {
            "winget": ["winget", "search", package_name],
            "chocolatey": ["choco", "search", package_name],
            "scoop": ["scoop", "search", package_name],
            "homebrew": ["brew", "search", package_name],
            "apt": ["apt", "search", package_name],
            "dnf": ["dnf", "search", package_name],
            "pacman": ["pacman", "-Ss", package_name],
            "zypper": ["zypper", "search", package_name],
        }

        if manager_name not in search_commands:
            return BaseResult(success=False, stderr="Unsupported package manager")

        return run_command(search_commands[manager_name])


# GLOBAL INSTANCE
########################################################

package_manager = PackageManager()
