#!/usr/bin/env python3
"""
Project configuration UI components.

This module provides UI components for project configuration and setup,
following the established patterns in the WOMM codebase.
"""

from typing import Dict

try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

from ...common.console import print_info


def configure_project_options(project_type: str) -> Dict:
    """
    Configure project-specific options through interactive UI.

    Args:
        project_type: Type of project (python, javascript, react, vue)

    Returns:
        Dictionary containing project configuration options
    """
    print_info(f"⚙️  Configuring {project_type} project options")
    print_info("=" * 50)

    options = {}

    # Common options for all project types
    options.update(_configure_common_options())

    # Project-specific options
    if project_type == "python":
        options.update(_configure_python_options())
    elif project_type in ["javascript", "react", "vue"]:
        options.update(_configure_javascript_options(project_type))

    return options


def _configure_common_options() -> Dict:
    """Configure common options for all project types."""
    options = {}

    if INQUIRERPY_AVAILABLE:
        options["author_name"] = (
            inquirer.text(
                message="Author name:",
                default="Your Name",
            ).execute()
            or "Your Name"
        )

        options["author_email"] = (
            inquirer.text(
                message="Author email:",
                default="your.email@example.com",
            ).execute()
            or "your.email@example.com"
        )

        options["project_description"] = (
            inquirer.text(
                message="Project description:",
                default="A new project created with WOMM CLI",
            ).execute()
            or "A new project created with WOMM CLI"
        )

        options["project_url"] = (
            inquirer.text(
                message="Project URL (optional):",
            ).execute()
            or ""
        )

        options["project_repository"] = (
            inquirer.text(
                message="Repository URL (optional):",
            ).execute()
            or ""
        )

        options["project_docs_url"] = (
            inquirer.text(
                message="Documentation URL (optional):",
            ).execute()
            or ""
        )

        # Keywords
        keywords_input = (
            inquirer.text(
                message="Keywords (comma-separated):",
                default="cli,utility",
            ).execute()
            or "cli,utility"
        )
        options["project_keywords"] = [
            kw.strip() for kw in keywords_input.split(",") if kw.strip()
        ]

        # License
        license_choices = [
            Choice(value="MIT", name="MIT License"),
            Choice(value="Apache-2.0", name="Apache License 2.0"),
            Choice(value="GPL-3.0", name="GNU General Public License v3.0"),
            Choice(value="BSD-3-Clause", name="BSD 3-Clause License"),
            Choice(value="custom", name="Custom license"),
        ]
        selected_license = inquirer.select(
            message="License:",
            choices=license_choices,
            pointer="→",
        ).execute()

        if selected_license == "custom":
            options["license"] = (
                inquirer.text(
                    message="Custom license name:",
                ).execute()
                or "MIT"
            )
        else:
            options["license"] = selected_license

    else:
        # Fallback to simple input
        options["author_name"] = (
            input("Author name [Your Name]: ").strip() or "Your Name"
        )
        options["author_email"] = (
            input("Author email [your.email@example.com]: ").strip()
            or "your.email@example.com"
        )
        options["project_description"] = (
            input("Project description: ").strip()
            or "A new project created with WOMM CLI"
        )
        options["project_url"] = input("Project URL (optional): ").strip()
        options["project_repository"] = input("Repository URL (optional): ").strip()
        options["project_docs_url"] = input("Documentation URL (optional): ").strip()

        keywords_input = (
            input("Keywords (comma-separated) [cli,utility]: ").strip() or "cli,utility"
        )
        options["project_keywords"] = [
            kw.strip() for kw in keywords_input.split(",") if kw.strip()
        ]

        print_info("License options:")
        print_info("1. MIT License")
        print_info("2. Apache License 2.0")
        print_info("3. GNU General Public License v3.0")
        print_info("4. BSD 3-Clause License")
        print_info("5. Custom license")
        license_choice = input("Select license (1-5) [1]: ").strip() or "1"
        licenses = ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "custom"]
        selected_license = (
            licenses[int(license_choice) - 1]
            if license_choice.isdigit() and 1 <= int(license_choice) <= 5
            else "MIT"
        )

        if selected_license == "custom":
            options["license"] = input("Custom license name: ").strip() or "MIT"
        else:
            options["license"] = selected_license

    return options


def _configure_python_options() -> Dict:
    """Configure Python-specific options."""
    options = {}

    if INQUIRERPY_AVAILABLE:
        # Python version
        python_versions = [
            Choice(value="3.8", name="Python 3.8"),
            Choice(value="3.9", name="Python 3.9"),
            Choice(value="3.10", name="Python 3.10"),
            Choice(value="3.11", name="Python 3.11"),
            Choice(value="3.12", name="Python 3.12"),
        ]
        options["python_version"] = inquirer.select(
            message="Python version:",
            choices=python_versions,
            pointer="→",
        ).execute()

        # Development tools
        options["include_dev_tools"] = inquirer.confirm(
            message="Include development tools (black, flake8, pytest, etc.)?",
            default=True,
        ).execute()

        if options["include_dev_tools"]:
            dev_tools = [
                Choice(value="black", name="Black (code formatting)"),
                Choice(value="flake8", name="Flake8 (linting)"),
                Choice(value="isort", name="isort (import sorting)"),
                Choice(value="mypy", name="MyPy (type checking)"),
                Choice(value="pytest", name="pytest (testing)"),
                Choice(value="pre-commit", name="pre-commit (git hooks)"),
            ]
            selected_tools = inquirer.checkbox(
                message="Select development tools:",
                choices=dev_tools,
                pointer="→",
            ).execute()
            options["dev_tools"] = selected_tools

        # Project structure
        options["create_src_layout"] = inquirer.confirm(
            message="Use src/ layout (recommended for packages)?",
            default=True,
        ).execute()

        options["include_docs"] = inquirer.confirm(
            message="Include documentation setup (Sphinx)?",
            default=False,
        ).execute()

    else:
        # Fallback to simple input
        print_info("Python version options:")
        versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
        for i, version in enumerate(versions, 1):
            print_info(f"{i}. Python {version}")
        version_choice = input("Select Python version (1-5) [5]: ").strip() or "5"
        options["python_version"] = (
            versions[int(version_choice) - 1]
            if version_choice.isdigit() and 1 <= int(version_choice) <= 5
            else "3.12"
        )

        include_dev = input("Include development tools? (Y/n): ").strip().lower()
        options["include_dev_tools"] = include_dev in ["", "y", "yes"]

        if options["include_dev_tools"]:
            print_info("Development tools:")
            tools = ["black", "flake8", "isort", "mypy", "pytest", "pre-commit"]
            for i, tool in enumerate(tools, 1):
                print_info(f"{i}. {tool}")
            tools_input = input(
                "Select tools (comma-separated numbers, or 'all'): "
            ).strip()
            if tools_input.lower() == "all":
                options["dev_tools"] = tools
            else:
                selected_indices = [
                    int(x.strip()) - 1
                    for x in tools_input.split(",")
                    if x.strip().isdigit()
                ]
                options["dev_tools"] = [
                    tools[i] for i in selected_indices if 0 <= i < len(tools)
                ]

        src_layout = input("Use src/ layout? (Y/n): ").strip().lower()
        options["create_src_layout"] = src_layout in ["", "y", "yes"]

        include_docs = input("Include documentation setup? (y/N): ").strip().lower()
        options["include_docs"] = include_docs in ["y", "yes"]

    return options


def _configure_javascript_options(project_type: str) -> Dict:
    """Configure JavaScript-specific options."""
    options = {}

    if INQUIRERPY_AVAILABLE:
        # JavaScript project type
        if project_type == "javascript":
            js_types = [
                Choice(value="node", name="Node.js application"),
                Choice(value="library", name="JavaScript library"),
                Choice(value="cli", name="CLI application"),
            ]
            options["js_project_type"] = inquirer.select(
                message="JavaScript project type:",
                choices=js_types,
                pointer="→",
            ).execute()

        # Package manager
        package_managers = [
            Choice(value="npm", name="npm (default)"),
            Choice(value="yarn", name="Yarn"),
            Choice(value="pnpm", name="pnpm"),
        ]
        options["package_manager"] = inquirer.select(
            message="Package manager:",
            choices=package_managers,
            pointer="→",
        ).execute()

        # TypeScript
        if project_type in ["react", "vue"]:
            options["use_typescript"] = inquirer.confirm(
                message="Use TypeScript?",
                default=True,
            ).execute()
        else:
            options["use_typescript"] = inquirer.confirm(
                message="Use TypeScript?",
                default=False,
            ).execute()

        # Development tools
        options["include_dev_tools"] = inquirer.confirm(
            message="Include development tools (ESLint, Prettier, Jest, etc.)?",
            default=True,
        ).execute()

        if options["include_dev_tools"]:
            dev_tools = [
                Choice(value="eslint", name="ESLint (linting)"),
                Choice(value="prettier", name="Prettier (formatting)"),
                Choice(value="jest", name="Jest (testing)"),
                Choice(value="husky", name="Husky (git hooks)"),
                Choice(value="lint-staged", name="lint-staged (pre-commit linting)"),
            ]
            selected_tools = inquirer.checkbox(
                message="Select development tools:",
                choices=dev_tools,
                pointer="→",
            ).execute()
            options["dev_tools"] = selected_tools

        # Framework-specific options
        if project_type == "react":
            options["use_jsx"] = inquirer.confirm(
                message="Use JSX syntax?",
                default=True,
            ).execute()

        elif project_type == "vue":
            options["vue_version"] = inquirer.select(
                message="Vue.js version:",
                choices=[
                    Choice(value="3", name="Vue 3 (Composition API)"),
                    Choice(value="2", name="Vue 2 (Options API)"),
                ],
                pointer="→",
            ).execute()

    else:
        # Fallback to simple input
        if project_type == "javascript":
            print_info("JavaScript project types:")
            js_types = ["node", "library", "cli"]
            for i, js_type in enumerate(js_types, 1):
                print_info(f"{i}. {js_type}")
            type_choice = input("Select type (1-3) [1]: ").strip() or "1"
            options["js_project_type"] = (
                js_types[int(type_choice) - 1]
                if type_choice.isdigit() and 1 <= int(type_choice) <= 3
                else "node"
            )

        print_info("Package managers:")
        managers = ["npm", "yarn", "pnpm"]
        for i, manager in enumerate(managers, 1):
            print_info(f"{i}. {manager}")
        manager_choice = input("Select package manager (1-3) [1]: ").strip() or "1"
        options["package_manager"] = (
            managers[int(manager_choice) - 1]
            if manager_choice.isdigit() and 1 <= int(manager_choice) <= 3
            else "npm"
        )

        if project_type in ["react", "vue"]:
            use_ts = input("Use TypeScript? (Y/n): ").strip().lower()
            options["use_typescript"] = use_ts in ["", "y", "yes"]
        else:
            use_ts = input("Use TypeScript? (y/N): ").strip().lower()
            options["use_typescript"] = use_ts in ["y", "yes"]

        include_dev = input("Include development tools? (Y/n): ").strip().lower()
        options["include_dev_tools"] = include_dev in ["", "y", "yes"]

        if options["include_dev_tools"]:
            print_info("Development tools:")
            tools = ["eslint", "prettier", "jest", "husky", "lint-staged"]
            for i, tool in enumerate(tools, 1):
                print_info(f"{i}. {tool}")
            tools_input = input(
                "Select tools (comma-separated numbers, or 'all'): "
            ).strip()
            if tools_input.lower() == "all":
                options["dev_tools"] = tools
            else:
                selected_indices = [
                    int(x.strip()) - 1
                    for x in tools_input.split(",")
                    if x.strip().isdigit()
                ]
                options["dev_tools"] = [
                    tools[i] for i in selected_indices if 0 <= i < len(tools)
                ]

        if project_type == "react":
            use_jsx = input("Use JSX syntax? (Y/n): ").strip().lower()
            options["use_jsx"] = use_jsx in ["", "y", "yes"]

        elif project_type == "vue":
            print_info("Vue.js versions:")
            print_info("1. Vue 3 (Composition API)")
            print_info("2. Vue 2 (Options API)")
            version_choice = input("Select version (1-2) [1]: ").strip() or "1"
            options["vue_version"] = "3" if version_choice == "1" else "2"

    return options
