#!/usr/bin/env python3
"""
Cross-Platform VSCode Configuration.
Automatically generates VSCode configurations adapted to the OS.
"""

import json
import logging
import platform
from pathlib import Path
from typing import Any, Dict


def get_python_interpreter_paths() -> Dict[str, str]:
    """Returns Python interpreter paths according to the OS."""
    system = platform.system().lower()

    paths = {
        "windows": "./venv/Scripts/python.exe",
        "linux": "./venv/bin/python",
        "darwin": "./venv/bin/python",  # macOS
    }

    return paths.get(system, "./venv/bin/python")


def get_platform_specific_settings(language: str = "python") -> Dict[str, Any]:
    """Generate platform-specific VSCode settings."""
    system = platform.system().lower()

    if language == "python":
        base_settings = {
            # Base configuration (common)
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "editor.codeActionsOnSave": {"source.organizeImports": "explicit"},
            "editor.rulers": [88],
            "editor.tabSize": 4,
            "editor.insertSpaces": True,
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            # Configuration Python
            "python.terminal.activateEnvironment": True,
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.flake8Args": ["--config=.flake8"],
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": [
                "--line-length=88",
                "--target-version=py39",
            ],
            "python.sortImports.args": ["--profile=black", "--line-length=88"],
            "[python]": {
                "editor.defaultFormatter": "ms-python.black-formatter",
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": "explicit",
                },
            },
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": [
                "tests",
                "--tb=short",
                "--strict-markers",
            ],
            "python.testing.autoTestDiscoverOnSaveEnabled": True,
            "python.analysis.extraPaths": ["./src"],
            "python.analysis.autoSearchPaths": True,
            "python.analysis.typeCheckingMode": "basic",
            # Common exclusions
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True,
                "**/htmlcov": True,
                "**/.coverage": True,
                "**/build": True,
                "**/dist": True,
                "**/*.egg-info": True,
                "**/.mypy_cache": True,
                "**/.tox": True,
                "**/venv": True,
                "**/.venv": True,
                "**/.env*": True,
                "**/.secret*": True,
                "**/*password*": True,
                "**/*secret*": True,
                "**/*.key": True,
                "**/*.pem": True,
                "**/*.crt": True,
                "**/credentials": True,
            },
            "files.watcherExclude": {
                "**/.git/objects/**": True,
                "**/.git/subtree-cache/**": True,
                "**/venv/**": True,
                "**/.venv/**": True,
                "**/__pycache__/**": True,
                "**/.pytest_cache/**": True,
                "**/htmlcov/**": True,
                "**/.env*": True,
                "**/.secret*": True,
                "**/*password*": True,
                "**/*secret*": True,
                "**/*.key": True,
                "**/*.pem": True,
                "**/*.crt": True,
                "**/credentials/**": True,
            },
            "git.ignoreLimitWarning": True,
        }

        # Add OS-specific interpreter path
        python_path = get_python_interpreter_paths()
        base_settings["python.defaultInterpreterPath"] = python_path

        # OS-specific terminal environment configuration
        if system == "windows":
            base_settings["terminal.integrated.env.windows"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        elif system == "darwin":  # macOS
            base_settings["terminal.integrated.env.osx"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        else:  # Linux et autres Unix
            base_settings["terminal.integrated.env.linux"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }

        return base_settings

    elif language == "javascript":
        return {
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit",
                "source.fixAll.eslint": "explicit",
            },
            "editor.rulers": [80],
            "editor.tabSize": 2,
            "editor.insertSpaces": True,
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            # Configuration JavaScript/TypeScript
            "javascript.preferences.includePackageJsonAutoImports": "auto",
            "typescript.preferences.includePackageJsonAutoImports": "auto",
            "javascript.updateImportsOnFileMove.enabled": "always",
            "typescript.updateImportsOnFileMove.enabled": "always",
            # ESLint
            "eslint.enable": True,
            "eslint.format.enable": True,
            "eslint.lintTask.enable": True,
            # Prettier
            "[javascript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode",
                "editor.formatOnSave": True,
            },
            "[typescript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode",
                "editor.formatOnSave": True,
            },
            "[json]": {"editor.defaultFormatter": "esbenp.prettier-vscode"},
            # Exclusions
            "files.exclude": {
                "**/node_modules": True,
                "**/dist": True,
                "**/build": True,
                "**/.next": True,
                "**/coverage": True,
                "**/.nyc_output": True,
            },
            "files.watcherExclude": {
                "**/node_modules/**": True,
                "**/dist/**": True,
                "**/build/**": True,
                "**/.next/**": True,
            },
        }

    return {}


def generate_vscode_config(target_dir: Path, language: str = "python") -> None:
    """Generates VSCode configuration for a project."""
    vscode_dir = target_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Generate settings.json
    settings = get_platform_specific_settings(language)
    settings_file = vscode_dir / "settings.json"

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    logging.info(f"✅ VSCode configuration generated for {language} in {vscode_dir}")
    logging.info(f"🖥️  Detected platform: {platform.system()}")

    if language == "python":
        python_path = get_python_interpreter_paths()
        logging.info(f"🐍 Python path configured: {python_path}")


def main():
    """
    Main entry point.

    TODO: This function contains CLI logic and should be moved to appropriate CLI modules.
    For now, keeping structure but removing main execution code.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Generates a cross-platform VSCode configuration"
    )
    parser.add_argument(
        "--language",
        "-l",
        choices=["python", "javascript"],
        default="python",
        help="Target language (default: python)",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=Path,
        default=Path.cwd(),
        help="Target directory (default: current directory)",
    )
    parser.add_argument("--project-name", "-n", help="Project name")

    args = parser.parse_args()

    generate_vscode_config(
        target_dir=args.target,
        language=args.language,
    )


# NOTE: Main function removed - utility modules should not have main execution code.
# This function should be called from appropriate CLI modules instead.
