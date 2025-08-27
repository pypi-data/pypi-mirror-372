#!/usr/bin/env python3
"""
Path management utilities for Works On My Machine.

This module provides utilities for managing system PATH variables
during installation and uninstallation operations.
"""

# IMPORTS
########################################################
# Standard library imports
import platform
from pathlib import Path
from typing import Dict

from ...exceptions.installation_exceptions import (
    ExecutableVerificationError,
    PathUtilityError,
)

# Local imports
from ..cli_utils import run_silent
from ..system.user_path_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)

# FUNCTIONS
########################################################
# Windows PATH management


def setup_windows_path(entry_path: str, original_path: str) -> Dict:
    """Setup WOMM in Windows PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory
        original_path: Original PATH value for backup

    Returns:
        Dictionary with operation results
    """
    try:
        # Query current user PATH from registry
        result = run_silent(
            [
                "reg",
                "query",
                "HKCU\\Environment",
                "/v",
                "PATH",
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            # Handle stderr properly - check if it's bytes or str
            stderr_str = result.stderr
            if isinstance(stderr_str, bytes):
                stderr_str = stderr_str.decode()

            return {
                "success": False,
                "error": "Failed to query current PATH from registry",
                "stderr": stderr_str,
            }

        # Extract current PATH value - handle stdout properly
        stdout_str = result.stdout
        if isinstance(stdout_str, bytes):
            stdout_str = stdout_str.decode()

        current_path = extract_path_from_reg_output(stdout_str)

        # Normalize path separators and deduplicate
        def _normalize_list(path_str: str) -> list[str]:
            """Split PATH string and normalize separators."""
            entries = [p.strip() for p in path_str.split(";") if p.strip()]
            return [str(Path(p)) for p in entries]

        # Parse current PATH entries
        current_entries = _normalize_list(current_path)
        normalized_womm = str(Path(entry_path))

        # Check if WOMM path is already in PATH
        if normalized_womm not in current_entries:
            # Add WOMM path to the beginning for priority
            updated_entries = current_entries + [normalized_womm]
            updated_path = ";".join(updated_entries)

            # Deduplicate entries to clean up PATH
            updated_path = deduplicate_path_entries(updated_path)

            # Update PATH in registry
            reg_result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_EXPAND_SZ",
                    "/d",
                    updated_path,
                    "/f",
                ],
                capture_output=True,
            )

            if reg_result.returncode != 0:
                # Handle stderr properly
                stderr_str = reg_result.stderr
                if isinstance(stderr_str, bytes):
                    stderr_str = stderr_str.decode()

                return {
                    "success": False,
                    "error": "Failed to update PATH in registry",
                    "stderr": stderr_str,
                }

            return {
                "success": True,
                "action": "added",
                "entry_path": normalized_womm,
                "original_path": original_path,
                "updated_path": updated_path,
            }
        else:
            return {
                "success": True,
                "action": "already_present",
                "entry_path": normalized_womm,
                "current_path": current_path,
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception during Windows PATH setup: {e}",
        }


def remove_from_path(entry_path: str) -> Dict:
    """Remove WOMM from PATH environment variable (cross-platform).

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dict with operation result and details
    """
    import platform

    if platform.system() == "Windows":
        return remove_from_windows_path(entry_path)
    else:
        return remove_from_unix_path(entry_path)


def remove_from_windows_path(entry_path: str) -> Dict:
    """Remove WOMM from Windows PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dictionary with operation results
    """
    try:
        # Query current user PATH from registry
        result = run_silent(
            [
                "reg",
                "query",
                "HKCU\\Environment",
                "/v",
                "PATH",
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": "Failed to query current PATH from registry",
            }

        # Extract and normalize current PATH - handle stdout properly
        stdout_str = result.stdout
        if isinstance(stdout_str, bytes):
            stdout_str = stdout_str.decode()

        current_path = extract_path_from_reg_output(stdout_str)

        def _norm(p: str) -> str:
            """Normalize path for comparison."""
            return str(Path(p).resolve()) if p else ""

        path_entries = [p.strip() for p in current_path.split(";") if p.strip()]
        normalized_womm = _norm(entry_path)

        # Filter out WOMM paths
        updated_entries = []
        removed_paths = []

        for entry in path_entries:
            normalized_entry = _norm(entry)
            if normalized_entry and normalized_entry != normalized_womm:
                updated_entries.append(entry)
            elif normalized_entry == normalized_womm:
                removed_paths.append(entry)

        if removed_paths:
            # Update PATH in registry
            updated_path = ";".join(updated_entries)

            reg_result = run_silent(
                [
                    "reg",
                    "add",
                    "HKCU\\Environment",
                    "/v",
                    "PATH",
                    "/t",
                    "REG_EXPAND_SZ",
                    "/d",
                    updated_path,
                    "/f",
                ],
                capture_output=True,
            )

            if reg_result.returncode != 0:
                return {
                    "success": False,
                    "error": "Failed to update PATH in registry",
                }

            return {
                "success": True,
                "action": "removed",
                "removed_paths": removed_paths,
                "updated_path": updated_path,
            }
        else:
            return {
                "success": True,
                "action": "not_found",
                "current_path": current_path,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def setup_unix_path(entry_path: str, original_path: str) -> Dict:
    """Setup WOMM in Unix PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory
        original_path: Original PATH value for backup

    Returns:
        Dictionary with operation results
    """
    try:
        shell_rc_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        # Find existing shell configuration file
        target_rc = None
        for rc_file in shell_rc_files:
            if rc_file.exists():
                target_rc = rc_file
                break

        # Default to .bashrc if none exist
        if target_rc is None:
            target_rc = Path.home() / ".bashrc"

        # Check if WOMM path is already in the RC file
        womm_export_line = f'export PATH="{entry_path}:$PATH"'
        womm_path_comment = "# Added by Works On My Machine installer"

        if target_rc.exists():
            with open(target_rc, encoding="utf-8") as f:
                content = f.read()
                if entry_path in content:
                    return {
                        "success": True,
                        "action": "already_present",
                        "rc_file": str(target_rc),
                        "entry_path": entry_path,
                    }

        # Add WOMM to PATH
        with open(target_rc, "a", encoding="utf-8") as f:
            f.write(f"\n{womm_path_comment}\n{womm_export_line}\n")

        return {
            "success": True,
            "action": "added",
            "rc_file": str(target_rc),
            "entry_path": entry_path,
            "original_path": original_path,
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def remove_from_unix_path(entry_path: str) -> Dict:
    """Remove WOMM from Unix PATH environment variable.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dictionary with operation results
    """
    try:
        shell_rc_files = [
            Path.home() / ".bashrc",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        removed_from_files = []

        for rc_file in shell_rc_files:
            if not rc_file.exists():
                continue

            with open(rc_file, encoding="utf-8") as f:
                lines = f.readlines()

            # Filter out WOMM-related lines
            updated_lines = []
            removed_lines = []
            skip_next = False

            for _i, line in enumerate(lines):
                line_stripped = line.strip()

                # Skip WOMM comment lines
                if "Added by Works On My Machine installer" in line:
                    removed_lines.append(line_stripped)
                    skip_next = True
                    continue

                # Skip WOMM export lines
                elif skip_next and "export PATH=" in line and entry_path in line:
                    removed_lines.append(line_stripped)
                    skip_next = False
                    continue

                # Skip direct WOMM export lines without comment
                elif "export PATH=" in line and entry_path in line:
                    removed_lines.append(line_stripped)
                    continue

                else:
                    updated_lines.append(line)
                    skip_next = False

            # Write back if changes were made
            if removed_lines:
                with open(rc_file, "w", encoding="utf-8") as f:
                    f.writelines(updated_lines)

                removed_from_files.append(
                    {
                        "file": str(rc_file),
                        "removed_lines": removed_lines,
                    }
                )

        if removed_from_files:
            return {
                "success": True,
                "action": "removed",
                "removed_from_files": removed_from_files,
            }
        else:
            return {
                "success": True,
                "action": "not_found",
                "checked_files": [str(f) for f in shell_rc_files if f.exists()],
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def verify_path_configuration(entry_path: str) -> Dict:
    """Verify that WOMM is correctly configured in PATH.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dictionary with verification results

    Raises:
        PathUtilityError: If PATH configuration verification fails
    """
    try:
        if platform.system() == "Windows":
            # Query Windows registry for PATH
            result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
                capture_output=True,
            )

            if result.returncode != 0:
                raise PathUtilityError(
                    operation="path_verification",
                    path=entry_path,
                    reason="Failed to query PATH from registry",
                    details=f"Return code: {result.returncode}",
                )

            # Handle stdout properly
            stdout_str = result.stdout
            if isinstance(stdout_str, bytes):
                stdout_str = stdout_str.decode()

            current_path = extract_path_from_reg_output(stdout_str)
            path_entries = [p.strip() for p in current_path.split(";") if p.strip()]

        else:
            # Check Unix shell configuration files
            shell_rc_files = [
                Path.home() / ".bashrc",
                Path.home() / ".zshrc",
                Path.home() / ".profile",
            ]

            path_entries = []
            for rc_file in shell_rc_files:
                if rc_file.exists():
                    with open(rc_file, encoding="utf-8") as f:
                        content = f.read()
                        if entry_path in content:
                            path_entries.append(str(rc_file))

        # Normalize paths for comparison
        normalized_womm = str(Path(entry_path).resolve())
        found_in_path = False

        if platform.system() == "Windows":
            normalized_entries = [str(Path(p).resolve()) for p in path_entries if p]
            found_in_path = normalized_womm in normalized_entries
        else:
            found_in_path = len(path_entries) > 0

        if not found_in_path:
            raise PathUtilityError(
                operation="path_verification",
                path=entry_path,
                reason="WOMM path not found in system PATH",
                details=f"Platform: {platform.system()}, Checked locations: {path_entries if platform.system() != 'Windows' else 'Registry'}",
            )

        return {
            "success": True,
            "entry_path": entry_path,
            "found_in_path": True,
            "platform": platform.system(),
            "checked_locations": (
                path_entries if platform.system() != "Windows" else "Registry"
            ),
        }

    except PathUtilityError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise PathUtilityError(
            operation="path_verification",
            path=entry_path,
            reason=f"Unexpected error during PATH verification: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


def verify_commands_accessible(entry_path: str) -> Dict:
    """Verify that WOMM commands are accessible from PATH.

    Args:
        entry_path: Path to WOMM installation directory

    Returns:
        Dictionary with verification results

    Raises:
        ExecutableVerificationError: If executable is not accessible
    """
    try:
        # First test: Check if executable exists at the specified path
        if platform.system() == "Windows":
            local_executable = Path(entry_path) / "womm.bat"
            global_command = ["womm.bat", "--version"]
        else:
            local_executable = Path(entry_path) / "womm"
            global_command = ["womm", "--version"]

        # Test 1: Local executable exists and works
        if not local_executable.exists():
            raise ExecutableVerificationError(
                executable_name="womm",
                reason=f"WOMM executable not found at {local_executable}",
                details=f"Platform: {platform.system()}",
            )

        # Test local executable
        local_result = run_silent(
            [str(local_executable), "--version"], capture_output=True
        )
        local_works = local_result.returncode == 0

        # Debug info for local test failure
        if not local_works:
            import tempfile

            # Clean stdout/stderr of problematic Unicode characters
            stdout_clean = (
                str(local_result.stdout).encode("ascii", "replace").decode("ascii")
                if local_result.stdout
                else "None"
            )
            stderr_clean = (
                str(local_result.stderr).encode("ascii", "replace").decode("ascii")
                if local_result.stderr
                else "None"
            )

            debug_file = Path(tempfile.gettempdir()) / "womm_local_test_debug.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("Local executable test failed:\n")
                f.write(f"Executable: {local_executable}\n")
                f.write(f"Exists: {local_executable.exists()}\n")
                f.write(f"Command: {[str(local_executable), '--version']}\n")
                f.write(f"Return code: {local_result.returncode}\n")
                f.write(f"Stdout: {stdout_clean}\n")
                f.write(f"Stderr: {stderr_clean}\n")
                if local_executable.exists():
                    f.write(f"File size: {local_executable.stat().st_size}\n")
                    try:
                        with open(local_executable, encoding="utf-8") as exe_file:
                            f.write(f"Content:\n{exe_file.read()}\n")
                    except Exception as e:
                        f.write(f"Could not read executable content: {e}\n")

        # Test 2: Global accessibility via PATH
        global_result = run_silent(global_command, capture_output=True)
        global_works = global_result.returncode == 0

        # Logic for handling local vs global test results is handled below in unified way
        if local_works and global_works:
            # Handle stdout properly
            stdout_str = global_result.stdout
            if isinstance(stdout_str, bytes):
                stdout_str = stdout_str.decode()

            return {
                "success": True,
                "womm_accessible": True,
                "local_test": True,
                "global_test": True,
                "version_output": stdout_str,
                "executable_path": str(local_executable),
            }
        elif local_works and not global_works:
            # Local works but global doesn't - this is common on Windows after fresh install
            return {
                "success": True,  # Consider this a success since local works
                "womm_accessible": True,
                "local_test": True,
                "global_test": False,
                "warning": "Global command not yet accessible in current session (normal after fresh installation)",
                "executable_path": str(local_executable),
                "path_status": "timing_issue",
            }
        else:
            # Both local and global failed - this is a real problem
            stderr_str = (
                global_result.stderr if not global_works else local_result.stderr
            )
            if isinstance(stderr_str, bytes):
                stderr_str = stderr_str.decode()

            # Clean stderr of problematic Unicode characters
            stderr_clean = (
                stderr_str.encode("ascii", "replace").decode("ascii")
                if stderr_str
                else "None"
            )

            raise ExecutableVerificationError(
                executable_name="womm",
                reason="WOMM command not accessible - both local and global tests failed",
                details=f"Local: {local_works}, Global: {global_works}, stderr: {stderr_clean}",
            )

    except ExecutableVerificationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        # Clean the error message of Unicode characters that can't be encoded
        error_msg = str(e).encode("ascii", "replace").decode("ascii")
        raise ExecutableVerificationError(
            executable_name="womm",
            reason=f"Unexpected error during command verification: {error_msg}",
            details="This is an unexpected error that should be reported",
        ) from e
