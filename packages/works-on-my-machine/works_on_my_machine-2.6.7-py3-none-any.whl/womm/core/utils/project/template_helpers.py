#!/usr/bin/env python3
"""
Template Helpers - Utilities for cross-platform template generation.
Generates cross-platform templates.
Validates placeholders in a template.
"""

import logging
import os
import platform
import re
from pathlib import Path
from typing import Any, Dict, Optional


def get_platform_info() -> Dict[str, str]:
    """Returns platform information."""
    system = platform.system()
    return {
        "system": system,
        "system_lower": system.lower(),
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_macos": system == "Darwin",
        "path_separator": os.sep,
        "line_ending": "\r\n" if system == "Windows" else "\n",
    }


def get_python_paths() -> Dict[str, str]:
    """Returns Python paths according to OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "venv_python": "./venv/Scripts/python.exe",
            "venv_activate": "./venv/Scripts/activate.bat",
            "venv_pip": "./venv/Scripts/pip.exe",
            "python_executable": "python.exe",
        }
    else:  # Linux/macOS
        return {
            "venv_python": "./venv/bin/python",
            "venv_activate": "source ./venv/bin/activate",
            "venv_pip": "./venv/bin/pip",
            "python_executable": "python3",
        }


def get_node_paths() -> Dict[str, str]:
    """Returns Node.js paths according to OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "npm_executable": "npm.cmd",
            "node_executable": "node.exe",
            "npx_executable": "npx.cmd",
        }
    else:  # Linux/macOS
        return {
            "npm_executable": "npm",
            "node_executable": "node",
            "npx_executable": "npx",
        }


def get_shell_commands() -> Dict[str, str]:
    """Returns shell commands according to OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "shell": "cmd",
            "shell_extension": ".bat",
            "remove_dir": "rmdir /s /q",
            "copy_file": "copy",
            "move_file": "move",
            "make_executable": "rem",  # Not needed on Windows
            "which": "where",
        }
    else:  # Linux/macOS
        return {
            "shell": "bash",
            "shell_extension": ".sh",
            "remove_dir": "rm -rf",
            "copy_file": "cp",
            "move_file": "mv",
            "make_executable": "chmod +x",
            "which": "which",
        }


def replace_platform_placeholders(text: str, **extra_vars) -> str:
    r"""
    Replace platform-specific placeholders in a text.

    Supported placeholders:
    - {{PYTHON_PATH}} - Path to Python executable
    - {{VENV_ACTIVATE}} - Virtual environment activation command
    - {{SHELL_EXT}} - Shell script extension (.bat or .sh)
    - {{PATH_SEP}} - Path separator (/ or \\)
    - {{LINE_ENDING}} - Line ending (\\r\\n or \\n)
    """
    platform_info = get_platform_info()
    python_paths = get_python_paths()
    node_paths = get_node_paths()
    shell_commands = get_shell_commands()

    # Replacement dictionary
    replacements = {
        # Platform information
        "PLATFORM_SYSTEM": platform_info["system"],
        "PLATFORM_SYSTEM_LOWER": platform_info["system_lower"],
        "IS_WINDOWS": str(platform_info["is_windows"]).lower(),
        "IS_LINUX": str(platform_info["is_linux"]).lower(),
        "IS_MACOS": str(platform_info["is_macos"]).lower(),
        "PATH_SEP": platform_info["path_separator"],
        "LINE_ENDING": platform_info["line_ending"],
        # Python paths
        "PYTHON_PATH": python_paths["venv_python"],
        "VENV_ACTIVATE": python_paths["venv_activate"],
        "VENV_PIP": python_paths["venv_pip"],
        "PYTHON_EXECUTABLE": python_paths["python_executable"],
        # Node.js paths
        "NPM_EXECUTABLE": node_paths["npm_executable"],
        "NODE_EXECUTABLE": node_paths["node_executable"],
        "NPX_EXECUTABLE": node_paths["npx_executable"],
        # Shell commands
        "SHELL": shell_commands["shell"],
        "SHELL_EXT": shell_commands["shell_extension"],
        "REMOVE_DIR": shell_commands["remove_dir"],
        "COPY_FILE": shell_commands["copy_file"],
        "MOVE_FILE": shell_commands["move_file"],
        "MAKE_EXECUTABLE": shell_commands["make_executable"],
        "WHICH": shell_commands["which"],
        # Additional variables
        **extra_vars,
    }

    # Replace placeholders
    result = text
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    return result


def generate_cross_platform_template(
    template_path: Path,
    output_path: Path,
    template_vars: Optional[Dict[str, str]] = None,
) -> None:
    """
    Generates a file from a template by replacing placeholders.

    Args:
        template_path: Path to the template to use.
        output_path: Path to the output file.
        template_vars: Variables to replace in the template.

    Returns:
        None
    """
    if template_vars is None:
        template_vars = {}

    # Read template
    with open(template_path, encoding="utf-8") as f:
        template_content = f.read()

    # Replace placeholders
    result_content = replace_platform_placeholders(template_content, **template_vars)

    # Create output directory if necessary
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_content)

    logging.info(f"✅ Template generated: {output_path}")


def validate_template_placeholders(template_path: Path) -> Dict[str, Any]:
    """
    Validate placeholders in a template and return statistics.

    Args:
        template_path: Path to the template to validate.

    Returns:
        A dictionary containing validation statistics.
    """
    with open(template_path, encoding="utf-8") as f:
        content = f.read()

    # Search for placeholders
    placeholder_pattern = r"\{\{([A-Z_]+)\}\}"
    placeholders = re.findall(placeholder_pattern, content)

    # Supported placeholders
    supported_placeholders = {
        "PLATFORM_SYSTEM",
        "PLATFORM_SYSTEM_LOWER",
        "IS_WINDOWS",
        "IS_LINUX",
        "IS_MACOS",
        "PATH_SEP",
        "LINE_ENDING",
        "PYTHON_PATH",
        "VENV_ACTIVATE",
        "VENV_PIP",
        "PYTHON_EXECUTABLE",
        "NPM_EXECUTABLE",
        "NODE_EXECUTABLE",
        "NPX_EXECUTABLE",
        "SHELL",
        "SHELL_EXT",
        "REMOVE_DIR",
        "COPY_FILE",
        "MOVE_FILE",
        "MAKE_EXECUTABLE",
        "WHICH",
        # Standard project placeholders
        "PROJECT_NAME",
        "PROJECT_DESCRIPTION",
        "AUTHOR_NAME",
        "AUTHOR_EMAIL",
        "PROJECT_URL",
        "PROJECT_REPOSITORY",
        "PROJECT_DOCS_URL",
        "PROJECT_KEYWORDS",
    }

    # Classify placeholders
    found_placeholders = set(placeholders)
    supported_found = found_placeholders & supported_placeholders
    unsupported_found = found_placeholders - supported_placeholders

    return {
        "total_placeholders": len(found_placeholders),
        "supported_placeholders": list(supported_found),
        "unsupported_placeholders": list(unsupported_found),
        "is_valid": len(unsupported_found) == 0,
        "template_path": str(template_path),
    }


def main():
    """
    Main entry point for tests.

    TODO: This function contains debug/test logic and should be moved to tests/ package.
    For now, logging statements replace print() to maintain functionality.
    """
    platform_info = get_platform_info()
    python_paths = get_python_paths()
    node_paths = get_node_paths()
    shell_commands = get_shell_commands()

    logging.info("🌍 Platform information:")
    for key, value in platform_info.items():
        logging.info(f"  {key}: {value}")

    logging.info("🐍 Python paths:")
    for key, value in python_paths.items():
        logging.info(f"  {key}: {value}")

    logging.info("🟨 Node.js paths:")
    for key, value in node_paths.items():
        logging.info(f"  {key}: {value}")

    logging.info("💻 Shell commands:")
    for key, value in shell_commands.items():
        logging.info(f"  {key}: {value}")


# NOTE: Main function removed - utility modules should not have main execution code.
# This function should be called from appropriate test modules instead.
