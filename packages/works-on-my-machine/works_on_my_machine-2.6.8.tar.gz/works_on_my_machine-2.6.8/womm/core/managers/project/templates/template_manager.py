#!/usr/bin/env python3
"""
Template manager for WOMM CLI.
Handles template generation from existing projects and template management.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from ....ui.common.console import print_error, print_success


class TemplateManager:
    """Template management for project creation from existing projects."""

    def __init__(self):
        """Initialize the template manager."""
        # Templates stored in user's home directory
        self.templates_dir = Path.home() / ".womm" / ".templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.template_cache: Dict[str, Dict] = {}

    def create_template_from_project(
        self, source_project_path: Path, template_name: str, **kwargs
    ) -> bool:
        """
        Create a template from an existing project.

        Args:
            source_project_path: Path to the existing project
            template_name: Name for the new template
            **kwargs: Additional template metadata

        Returns:
            True if template creation was successful, False otherwise
        """
        try:
            if not source_project_path.exists():
                print_error(f"Source project not found: {source_project_path}")
                return False

            # Create template directory
            template_dir = self.templates_dir / template_name
            if template_dir.exists():
                print_error(f"Template '{template_name}' already exists")
                return False

            template_dir.mkdir(parents=True, exist_ok=True)

            # Detect project type
            project_type = self._detect_project_type(source_project_path)

            # Scan and generalize the project
            template_files = self._scan_and_generalize_project(
                source_project_path, template_dir
            )

            # Create template.json
            template_data = {
                "name": template_name,
                "description": kwargs.get(
                    "description", f"Template generated from {source_project_path.name}"
                ),
                "version": "1.0.0",
                "author": "WOMM CLI",
                "project_type": project_type,
                "source_project": str(source_project_path),
                "created": kwargs.get("created", ""),
                "variables": self._extract_template_variables(template_dir),
                "files": template_files,
            }

            template_json = template_dir / "template.json"
            with open(template_json, "w", encoding="utf-8") as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            # Get file count for summary
            file_count = len(template_files)

            # Use new UI function for creation summary
            from ....ui.project.template_ui import print_template_creation_summary

            print_template_creation_summary(
                template_name, str(source_project_path), file_count
            )
            return True

        except Exception as e:
            print_error(f"Error creating template: {e}")
            return False

    def generate_from_template(
        self,
        template_name: str,
        target_path: Path,
        template_vars: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Generate a project from a template.

        Args:
            template_name: Name of the template to use
            target_path: Path where to generate the project
            template_vars: Variables to substitute in templates

        Returns:
            True if generation was successful, False otherwise
        """
        try:
            template_dir = self.templates_dir / template_name

            if not template_dir.exists():
                print_error(f"Template '{template_name}' not found")
                return False

            # Validate template
            if not self._validate_template(template_name):
                return False

            # Create target directory
            target_path.mkdir(parents=True, exist_ok=True)

            # Get template files
            template_files = self._get_template_files(template_dir)

            # Process each file
            for template_file in template_files:
                if not self._process_template_file(
                    template_file, template_dir, target_path, template_vars
                ):
                    return False

            print_success(f"Project generated from template '{template_name}'")
            return True

        except Exception as e:
            print_error(f"Error generating from template: {e}")
            return False

    def list_templates(self) -> Dict[str, List[str]]:
        """
        List all available templates.

        Returns:
            Dictionary mapping project types to template lists
        """
        try:
            templates = {}

            for template_dir in self.templates_dir.iterdir():
                if template_dir.is_dir() and not template_dir.name.startswith("."):
                    template_info = self._get_template_info(template_dir.name)
                    if template_info:
                        project_type = template_info.get("project_type", "unknown")
                        if project_type not in templates:
                            templates[project_type] = []
                        templates[project_type].append(template_dir.name)

            return templates

        except Exception as e:
            print_error(f"Error listing templates: {e}")
            return {}

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        Get information about a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Template information dictionary or None if not found
        """
        return self._get_template_info(template_name)

    def delete_template(self, template_name: str, show_summary: bool = True) -> bool:
        """
        Delete a template.

        Args:
            template_name: Name of the template
            show_summary: Whether to show deletion summary (default: True)

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            template_dir = self.templates_dir / template_name

            if not template_dir.exists():
                print_error(f"Template '{template_name}' not found")
                return False

            # Remove template directory
            shutil.rmtree(template_dir)

            # Show deletion summary only if requested
            if show_summary:
                from ....ui.project.template_ui import print_template_deletion_summary

                print_template_deletion_summary(template_name)

            return True

        except Exception as e:
            print_error(f"Error deleting template: {e}")
            return False

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect the type of project."""
        try:
            # Check for Python project
            if (project_path / "pyproject.toml").exists() or (
                project_path / "requirements.txt"
            ).exists():
                return "python"

            # Check for JavaScript project
            if (project_path / "package.json").exists():
                return "javascript"

            # Check for React project
            if (project_path / "package.json").exists():
                with open(project_path / "package.json", encoding="utf-8") as f:
                    package_data = json.load(f)
                    dependencies = package_data.get("dependencies", {})
                    if "react" in dependencies:
                        return "react"
                    elif "vue" in dependencies:
                        return "vue"
                return "javascript"

            return "unknown"

        except Exception:
            return "unknown"

    def _scan_and_generalize_project(
        self, source_path: Path, template_dir: Path
    ) -> List[str]:
        """Scan project and create generalized template files."""
        template_files = []

        # Files to ignore
        ignore_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "Thumbs.db",
            ".vscode",
            ".idea",
        ]

        for item in source_path.rglob("*"):
            # Skip ignored patterns
            if any(pattern in str(item) for pattern in ignore_patterns):
                continue

            if item.is_file():
                # Get relative path
                rel_path = item.relative_to(source_path)

                # Generalize the path (replace project name in folder names)
                rel_path_str = str(rel_path)
                generalized_path = rel_path_str.replace(
                    source_path.name, "{{PROJECT_NAME}}"
                )
                generalized_path = generalized_path.replace(
                    source_path.name.replace("-", "_"), "{{PROJECT_NAME}}"
                )
                generalized_path = generalized_path.replace(
                    source_path.name.replace("_", "-"), "{{PROJECT_NAME}}"
                )

                template_file = template_dir / f"{generalized_path}.template"

                # Create parent directories
                template_file.parent.mkdir(parents=True, exist_ok=True)

                # Read and generalize content
                content = item.read_text(encoding="utf-8", errors="ignore")
                generalized_content = self._generalize_content(
                    content, source_path.name
                )

                # Write template file
                template_file.write_text(generalized_content, encoding="utf-8")
                template_files.append(generalized_path)

        return template_files

    def _generalize_content(self, content: str, source_project_name: str) -> str:
        """Generalize content by replacing specific values with template variables."""
        # Common patterns to generalize
        generalizations = [
            # Project names (common patterns)
            (r"my-project", "{{PROJECT_NAME}}"),
            (r"my_project", "{{PROJECT_NAME}}"),
            (r"MyProject", "{{PROJECT_NAME}}"),
            # Source project name (most important)
            (re.escape(source_project_name), "{{PROJECT_NAME}}"),
            (re.escape(source_project_name.replace("-", "_")), "{{PROJECT_NAME}}"),
            (re.escape(source_project_name.replace("_", "-")), "{{PROJECT_NAME}}"),
            # Author information
            (r"John Doe", "{{AUTHOR_NAME}}"),
            (r"john\.doe@example\.com", "{{AUTHOR_EMAIL}}"),
            # Common email patterns
            (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "{{AUTHOR_EMAIL}}"),
            # URLs and repositories
            (
                r"https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
                "{{PROJECT_REPOSITORY}}",
            ),
            (r"https://example\.com", "{{PROJECT_URL}}"),
            # Version numbers
            (
                r'"version":\s*"[0-9]+\.[0-9]+\.[0-9]+"',
                '"version": "{{PROJECT_VERSION}}"',
            ),
        ]

        generalized = content
        for pattern, replacement in generalizations:
            generalized = re.sub(pattern, replacement, generalized, flags=re.IGNORECASE)

        return generalized

    def _extract_template_variables(self, template_dir: Path) -> Dict[str, str]:
        """Extract template variables from template files."""
        variables = {}

        # Default variables
        default_vars = {
            "PROJECT_NAME": "Project name",
            "AUTHOR_NAME": "Author name",
            "AUTHOR_EMAIL": "Author email",
            "PROJECT_VERSION": "0.1.0",
            "PROJECT_DESCRIPTION": "Project description",
            "PROJECT_URL": "Project URL",
            "PROJECT_REPOSITORY": "Project repository",
        }

        # Scan template files for variables
        for template_file in template_dir.rglob("*.template"):
            content = template_file.read_text(encoding="utf-8")
            matches = re.findall(r"\{\{([^}]+)\}\}", content)
            for match in matches:
                if match not in variables:
                    variables[match] = default_vars.get(match, f"{match} value")

        return variables

    def _get_template_files(self, template_dir: Path) -> List[str]:
        """Get list of template files."""
        try:
            files = []
            for item in template_dir.rglob("*.template"):
                if item.is_file():
                    # Get relative path from template directory
                    rel_path = item.relative_to(template_dir)
                    # Remove .template extension for output
                    output_path = str(rel_path).replace(".template", "")
                    files.append(output_path)
            return sorted(files)
        except Exception:
            return []

    def _process_template_file(
        self,
        template_file: str,
        template_dir: Path,
        target_path: Path,
        template_vars: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Process a single template file."""
        try:
            source_file = template_dir / f"{template_file}.template"

            # Substitute variables in the file path as well
            target_file_path = template_file
            if template_vars:
                for var_name, var_value in template_vars.items():
                    target_file_path = target_file_path.replace(
                        f"{{{{{var_name}}}}}", str(var_value)
                    )

            target_file = target_path / target_file_path

            if not source_file.exists():
                return True  # Skip if template file doesn't exist

            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Read template content
            content = source_file.read_text(encoding="utf-8")

            # Substitute variables
            if template_vars:
                for var_name, var_value in template_vars.items():
                    content = content.replace(f"{{{{{var_name}}}}}", str(var_value))

            # Write output file
            target_file.write_text(content, encoding="utf-8")

            return True

        except Exception as e:
            print_error(f"Error processing template file {template_file}: {e}")
            return False

    def _get_template_info(self, template_name: str) -> Optional[Dict]:
        """Get template information."""
        try:
            template_dir = self.templates_dir / template_name
            template_json = template_dir / "template.json"

            if template_json.exists():
                with open(template_json, encoding="utf-8") as f:
                    return json.load(f)

            return None

        except Exception:
            return None

    def _validate_template(self, template_name: str) -> bool:
        """Validate a template."""
        try:
            template_dir = self.templates_dir / template_name
            template_json = template_dir / "template.json"

            if not template_json.exists():
                print_error(f"Template metadata not found: {template_json}")
                return False

            # Validate template.json
            with open(template_json, encoding="utf-8") as f:
                template_data = json.load(f)

            required_fields = ["name", "project_type"]
            for field in required_fields:
                if field not in template_data:
                    print_error(f"Required field missing in template.json: {field}")
                    return False

            return True

        except Exception as e:
            print_error(f"Error validating template: {e}")
            return False
