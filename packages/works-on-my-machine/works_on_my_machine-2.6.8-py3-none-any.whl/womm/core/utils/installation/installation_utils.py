#!/usr/bin/env python3
"""
Installation utilities for Works On My Machine.

This module provides pure utility functions for WOMM installation operations.
All functions here are stateless and can be used independently.
"""

# IMPORTS
########################################################
# Standard library imports
import platform
import stat
from pathlib import Path
from time import sleep
from typing import Dict, List

# Local imports
from ...exceptions.installation import (
    ExecutableVerificationError,
    FileVerificationError,
    InstallationUtilityError,
    PathUtilityError,
)
from ..cli_utils import run_silent
from ..system.user_path_utils import extract_path_from_reg_output

# =============================================================================
# FILE MANAGEMENT UTILITIES
# =============================================================================


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)

    Returns:
        True if file should be excluded, False otherwise
    """
    # Check if we're in dev mode (pyproject.toml exists in parent)
    project_root = source_path.parent
    pyproject_file = project_root / "pyproject.toml"

    if pyproject_file.exists():
        # DEV MODE: Read pyproject.toml for patterns
        return check_pyproject_patterns(file_path, source_path, pyproject_file)
    else:
        # PACKAGE MODE: No filtering needed (already done during build)
        return False  # Include everything


def check_pyproject_patterns(
    file_path: Path, source_path: Path, pyproject_file: Path
) -> bool:
    """Check exclusion patterns from pyproject.toml.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)
        pyproject_file: Path to pyproject.toml

    Returns:
        True if file should be excluded, False otherwise
    """
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    try:
        with open(pyproject_file, "rb") as f:
            config = tomllib.load(f)

        # Get exclude patterns from setuptools
        setuptools_config = config.get("tool", {}).get("setuptools", {})
        packages_find = setuptools_config.get("packages", {}).get("find", {})
        exclude_patterns = packages_find.get("exclude", [])

        # Add womm-specific exclusions
        womm_config = config.get("tool", {}).get("womm", {}).get("installation", {})
        additional_exclude = womm_config.get("additional-exclude", [])
        exclude_patterns.extend(additional_exclude)

        # Apply patterns
        relative_path = file_path.relative_to(source_path)

        for pattern in exclude_patterns:
            if pattern.endswith("*"):
                # Handle wildcard patterns
                base_pattern = pattern[:-1]
                if str(relative_path).startswith(base_pattern):
                    return True
            elif pattern in str(relative_path):
                return True

        return False

    except Exception as e:
        # Fallback to default patterns if pyproject.toml can't be read
        print(f"Warning: Could not read pyproject.toml: {e}")
        return check_default_patterns(file_path, source_path)


def check_default_patterns(file_path: Path, source_path: Path) -> bool:
    """Fallback to default exclusion patterns.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path (womm package directory)

    Returns:
        True if file should be excluded, False otherwise
    """
    default_patterns = [
        ".git",
        ".gitignore",
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".coverage",
        "htmlcov",
        "coverage.xml",
        ".venv",
        "venv",
        "node_modules",
        "build",
        "dist",
        "*.egg-info",
        "tests",
        "test_*",
        "*_test.py",
        "docs",
        "pyproject.toml",
        "setup.py",
        "*.log",
        ".DS_Store",
        "Thumbs.db",
        ".vscode",
        ".idea",
        ".cursor",
        "ignore-install.txt",
        "womm.bat",
    ]

    file_name = file_path.name
    relative_path = file_path.relative_to(source_path)

    for pattern in default_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in str(relative_path):
            return True

    return False


def get_files_to_copy(source_path: Path) -> List[str]:
    """Get list of files to copy during installation.

    Args:
        source_path: Source directory path

    Returns:
        List of file paths relative to source
    """
    files_to_copy = []

    for file_path in source_path.rglob("*"):
        if file_path.is_file() and not should_exclude_file(file_path, source_path):
            relative_path = file_path.relative_to(source_path)
            files_to_copy.append(str(relative_path))

    return files_to_copy


# =============================================================================
# EXECUTABLE CREATION UTILITIES
# =============================================================================


def create_womm_executable(target_path: Path) -> Dict:
    """Create the womm executable script.

    Args:
        target_path: Path where WOMM is installed

    Returns:
        Dictionary with success status and details

    Raises:
        InstallationUtilityError: If executable creation fails
    """
    try:
        # Create womm.py wrapper
        womm_py_path = target_path / "womm.py"
        womm_py_content = '''#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Wrapper Entry Point.
This is a wrapper that calls the womm package __main__ module.
"""

import sys
from pathlib import Path


def main():
    """Main entry point for the womm wrapper."""
    try:
        # Add the current directory to path to import womm package
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        # Import and run the __main__ module
        from womm.__main__ import main as womm_main
        womm_main()
    except ImportError as e:
        print("❌ Error: Could not import womm package")
        print("💡 Make sure you're in the works-on-my-machine directory")
        print(f"🔧 Error details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running WOMM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

        # Write womm.py
        with open(womm_py_path, "w", encoding="utf-8") as f:
            f.write(womm_py_content)

        # Create executable script content
        if platform.system() == "Windows":
            # Windows batch file
            executable_path = target_path / "womm.bat"
            script_content = f'@echo off\npython "{womm_py_path}" %*\n'
        else:
            # Unix shell script
            executable_path = target_path / "womm"
            script_content = f'#!/bin/bash\npython3 "{womm_py_path}" "$@"\n'

        # Write the executable
        with open(executable_path, "w", encoding="utf-8") as f:
            f.write(script_content)
            sleep(0.5)

        # Make executable on Unix systems
        if platform.system() != "Windows":
            executable_path.chmod(executable_path.stat().st_mode | stat.S_IEXEC)

        return {
            "success": True,
            "executable_path": str(executable_path),
            "womm_py_path": str(womm_py_path),
            "platform": platform.system(),
        }

    except OSError as e:
        # File system errors
        raise InstallationUtilityError(
            message=f"Failed to create WOMM executable: {e}",
            details=f"Target path: {target_path}, Platform: {platform.system()}",
        ) from e
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise InstallationUtilityError(
            message=f"Unexpected error during executable creation: {e}",
            details=f"Target path: {target_path}, Platform: {platform.system()}",
        ) from e


# =============================================================================
# VERIFICATION UTILITIES
# =============================================================================


def verify_files_copied(source_path: Path, target_path: Path) -> Dict:
    """Verify that all required files were copied correctly.

    Args:
        source_path: Original source directory (womm package directory)
        target_path: Target installation directory (will contain womm/ subdirectory)

    Returns:
        Dictionary with verification results

    Raises:
        FileVerificationError: If files are missing or corrupted
    """
    try:
        files_to_check = get_files_to_copy(source_path)
        missing_files = []
        size_mismatches = []

        # Files are copied to target_path/womm/
        womm_target_path = target_path / "womm"

        for relative_file in files_to_check:
            source_file = source_path / relative_file
            target_file = womm_target_path / relative_file

            if not target_file.exists():
                missing_files.append(str(relative_file))
            elif source_file.stat().st_size != target_file.stat().st_size:
                size_mismatches.append(str(relative_file))

        # If there are issues, raise appropriate exceptions
        if missing_files:
            raise FileVerificationError(
                verification_type="copy_verification",
                file_path=str(missing_files[0]),  # First missing file
                reason=f"Missing {len(missing_files)} files",
                details=f"Missing files: {missing_files[:5]}{'...' if len(missing_files) > 5 else ''}",
            )

        if size_mismatches:
            raise FileVerificationError(
                verification_type="copy_verification",
                file_path=str(size_mismatches[0]),  # First mismatched file
                reason=f"Size mismatch in {len(size_mismatches)} files",
                details=f"Size mismatches: {size_mismatches[:5]}{'...' if len(size_mismatches) > 5 else ''}",
            )

        # All files verified successfully
        return {
            "success": True,
            "total_files": len(files_to_check),
            "missing_files": [],
            "size_mismatches": [],
        }

    except FileVerificationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise FileVerificationError(
            verification_type="copy_verification",
            file_path=str(target_path),
            reason=f"Unexpected error during file verification: {e}",
            details="This is an unexpected error that should be reported",
        ) from e


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


def verify_executable_works(target_path: Path) -> Dict:
    """Verify that the WOMM executable works correctly.

    Args:
        target_path: Target installation directory

    Returns:
        Dictionary with verification results

    Raises:
        ExecutableVerificationError: If executable is missing or fails to work
    """
    try:
        if platform.system() == "Windows":
            executable_path = target_path / "womm.bat"
            test_command = [str(executable_path), "--version"]
        else:
            executable_path = target_path / "womm"
            test_command = [str(executable_path), "--version"]

        if not executable_path.exists():
            raise ExecutableVerificationError(
                executable_name="womm",
                reason=f"Executable not found at {executable_path}",
                details=f"Platform: {platform.system()}",
            )

        # Test the executable
        result = run_silent(test_command, capture_output=True)

        if result.returncode == 0:
            # Handle stdout properly
            stdout_str = result.stdout
            if isinstance(stdout_str, bytes):
                stdout_str = stdout_str.decode()

            return {
                "success": True,
                "executable_path": str(executable_path),
                "output": stdout_str,
            }
        else:
            # Handle stderr properly
            stderr_str = result.stderr
            if isinstance(stderr_str, bytes):
                stderr_str = stderr_str.decode()

            raise ExecutableVerificationError(
                executable_name="womm",
                reason=f"Executable test failed with code {result.returncode}",
                details=f"stderr: {stderr_str}",
            )

    except ExecutableVerificationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Convert unexpected errors to our exception type
        raise ExecutableVerificationError(
            executable_name="womm",
            reason=f"Unexpected error during executable verification: {e}",
            details="This is an unexpected error that should be reported",
        ) from e
