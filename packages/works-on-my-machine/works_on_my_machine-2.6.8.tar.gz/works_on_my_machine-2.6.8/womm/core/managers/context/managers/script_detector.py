#!/usr/bin/env python3
"""
Script type detection and configuration for context menu entries.

This module provides automatic detection of script types and appropriate
configuration including icons and command building.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ....utils.cli_utils import check_tool_available, run_silent


class ScriptType:
    """Script type enumeration and configuration."""

    PYTHON = "python"
    POWERSHELL = "powershell"
    BATCH = "batch"
    EXECUTABLE = "executable"
    UNKNOWN = "unknown"


class ScriptDetector:
    """Detect script types and provide appropriate configuration."""

    # Extension to script type mapping
    EXTENSIONS = {
        ".py": ScriptType.PYTHON,
        ".ps1": ScriptType.POWERSHELL,
        ".bat": ScriptType.BATCH,
        ".cmd": ScriptType.BATCH,
        ".exe": ScriptType.EXECUTABLE,
        ".msi": ScriptType.EXECUTABLE,
    }

    # Default icons for each script type
    DEFAULT_ICONS = {
        ScriptType.PYTHON: "python.exe,0",
        ScriptType.POWERSHELL: "powershell.exe,0",
        ScriptType.BATCH: "cmd.exe,0",
        ScriptType.EXECUTABLE: None,  # Use file's own icon
        ScriptType.UNKNOWN: None,
    }

    # Context parameters for each script type
    CONTEXT_PARAMS = {
        ScriptType.PYTHON: "%V",  # Directory context
        ScriptType.POWERSHELL: "%V",  # Directory context
        ScriptType.BATCH: "%V",  # Directory context
        ScriptType.EXECUTABLE: "%V",  # Directory context
        ScriptType.UNKNOWN: "%V",  # Default to directory
    }

    @classmethod
    def detect_type(cls, file_path: str) -> str:
        """Detect script type from file extension."""
        ext = Path(file_path).suffix.lower()
        return cls.EXTENSIONS.get(ext, ScriptType.UNKNOWN)

    @classmethod
    def get_default_icon(cls, script_type: str) -> Optional[str]:
        """Get default icon for script type."""
        return cls.DEFAULT_ICONS.get(script_type)

    @classmethod
    def get_context_params(cls, script_type: str) -> str:
        """Get context parameters for script type."""
        return cls.CONTEXT_PARAMS.get(script_type, "%V")

    @classmethod
    def build_command(
        cls, script_type: str, script_path: str, context_params: str = None
    ) -> str:
        """Build appropriate command for script type."""
        if context_params is None:
            context_params = cls.get_context_params(script_type)

        # Convert relative path to absolute path
        import os

        script_abs_path = os.path.abspath(script_path)

        if script_type == ScriptType.PYTHON:
            # Use the same logic as RuntimeManager to find Python
            python_cmds = ["python3", "python", "py"]

            for cmd in python_cmds:
                if check_tool_available(cmd):
                    try:
                        result = run_silent([cmd, "--version"])
                        if result.success and result.stdout.strip():
                            version = result.stdout.strip().split()[1]
                            version_parts = [int(x) for x in version.split(".")]
                            if version_parts >= [3, 8]:  # Minimum Python 3.8
                                python_exe = shutil.which(cmd)
                                if python_exe:
                                    return f'"{python_exe}" "{script_abs_path}" "{context_params}"'
                    except (IndexError, ValueError):
                        continue

            # Fallback: try py launcher directly
            return f'cmd.exe /k py "{script_abs_path}" "{context_params}"'

        elif script_type == ScriptType.POWERSHELL:
            return f'powershell.exe -ExecutionPolicy Bypass -File "{script_abs_path}" "{context_params}"'

        elif script_type == ScriptType.BATCH or script_type == ScriptType.EXECUTABLE:
            return f'"{script_abs_path}" "{context_params}"'

        else:
            # Unknown type, try to execute directly
            return f'"{script_abs_path}" "{context_params}"'

    @classmethod
    def get_script_info(cls, file_path: str) -> Dict[str, Any]:
        """Get comprehensive script information."""
        script_type = cls.detect_type(file_path)

        return {
            "type": script_type,
            "extension": Path(file_path).suffix.lower(),
            "default_icon": cls.get_default_icon(script_type),
            "context_params": cls.get_context_params(script_type),
            "command": cls.build_command(script_type, file_path),
        }
