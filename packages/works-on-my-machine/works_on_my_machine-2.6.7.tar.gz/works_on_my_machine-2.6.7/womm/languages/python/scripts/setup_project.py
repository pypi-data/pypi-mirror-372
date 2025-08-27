#!/usr/bin/env python3
"""
Python development environment initialization script.

Usage:
    python setup_project.py [project_name]
        try:
            from ....core.tools.cspell_utils import setup_project_cspell

            success = setup_project_cspell(
                project_path, "python", project_name
            )
            if success:
                print("   [OK] CSpell configuration created")
            else:
                print("   [WARN] CSpell configuration failed")
        except ImportError:
            print("   [WARN] cspell_utils module not found")up_project.py --current-dir

Features:
    - Copy development configurations
    - Initialize Git with adapted .gitignore
    - Configure pre-commit hooks
    - Create basic project structure
    - Configure VSCode
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Import security validator
try:
    from ....core.utils.security.security_validator import SecurityValidator

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class PythonProjectSetup:
    """Class to configure a Python development environment."""

    def __init__(self, project_path: Path, project_name: str) -> None:
        """Initialize the Python project configuration script."""
        self.project_path = project_path
        self.project_name = project_name
        self.python_tools_path = Path(__file__).parent.parent
        self.devtools_path = self.python_tools_path.parent.parent

    def setup_all(self) -> None:
        """Configure the complete development environment."""
        print(f"[PYTHON] Setting up Python environment for '{self.project_name}'")
        print(f"[DIR] Directory: {self.project_path}")

        self.create_directory_structure()
        self.copy_configs()
        self.setup_git()
        self.setup_cspell()
        self.create_project_files()
        self.setup_vscode()
        self.setup_development_environment()
        self.install_hooks()

        print("\n[SUCCESS] Python configuration completed!")
        self.print_next_steps()

    def create_directory_structure(self) -> None:
        """Create the basic directory structure."""
        print("\n[DIRS] Creating directory structure...")

        directories = [
            self.project_path / self.project_name,
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / ".vscode",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   [OK] {directory}")

    def copy_configs(self) -> None:
        """Copy configuration files."""
        print("\n[CONFIG] Copying Python configurations...")

        configs = [
            ("configs/.pre-commit-config.yaml", ".pre-commit-config.yaml"),
            ("templates/gitignore-python.txt", ".gitignore"),
            ("templates/Makefile.template", "Makefile"),
            ("templates/DEVELOPMENT.md.template", "docs/DEVELOPMENT.md"),
        ]

        for source, dest in configs:
            source_path = self.python_tools_path / source
            dest_path = self.project_path / dest

            if source_path.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Process templates
                if source_path.suffix == ".template":
                    content = source_path.read_text(encoding="utf-8")
                    content = content.replace("{{PROJECT_NAME}}", self.project_name)
                    dest_path.write_text(content, encoding="utf-8")
                else:
                    shutil.copy2(source_path, dest_path)

                print(f"   [OK] {dest}")
            else:
                print(f"   [WARN] Missing file: {source}")

    def setup_git(self):
        """Initialise Git et configure .gitignore."""
        print("\n[GIT] Configuration Git...")

        if not (self.project_path / ".git").exists():
            try:
                git_path = shutil.which("git")
                if git_path is None:
                    print("   [WARN] Git not found")
                    return

                # Security validation
                if SECURITY_AVAILABLE:
                    validator = SecurityValidator()
                    is_valid, error_msg = validator.validate_command([git_path, "init"])
                    if not is_valid:
                        print(f"   [WARN] Security validation failed: {error_msg}")
                        return

                subprocess.run(  # noqa: S603
                    [git_path, "init"],
                    cwd=self.project_path,
                    check=True,
                    capture_output=True,
                )
                print("   [OK] Git repository initialized")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("   [WARN] Git not found or initialization error")

    def setup_cspell(self):
        """Configure CSpell for the project."""
        print("[CSPELL] Configuring CSpell...")

        # Importer le gestionnaire CSpell
        devtools_path = Path.home() / ".womm"
        sys.path.insert(0, str(devtools_path))

        try:
            from ....core.utils.spell.cspell_utils import setup_project_cspell

            success = setup_project_cspell(
                self.project_path, "python", self.project_name
            )
            if success:
                print("   [OK] CSpell configuration created")
            else:
                print("   [WARN] Error configuring CSpell")
        except ImportError:
            print("   [WARN] cspell_utils module not found")

    def setup_development_environment(self):
        """Configure the Python development environment."""
        print("[ENV] Setting up development environment...")

        # Importer le gestionnaire d'environnement
        devtools_path = Path.home() / ".womm"
        sys.path.insert(0, str(devtools_path))

        print("   [INFO] Development environment setup skipped (legacy)")
        return True

    def create_project_files(self):
        """Create the basic project files."""
        print("\n[FILES] Creating basic files...")

        # pyproject.toml
        pyproject_content = f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{self.project_name}"
version = "0.1.0"
description = "Description de votre projet Python"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [{{name = "Votre Nom", email = "votre.email@example.com"}}]

dependencies = [
    # Add your dependencies here
]

[project.optional-dependencies]
dev = [
    "pytest>=6.2.5",
    "pytest-cov>=3.0.0",
    "coverage>=7.10.0",
    "flake8>=6.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "pre-commit>=3.0.0",
    "bandit>=1.7.0",
]

[tool.black]
line-length = 88
target-version = ['py39', 'py310', 'py311', 'py312']

[tool.isort]
profile = "black"
line_length = 88
known_first_party = ["{self.project_name}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov={self.project_name}",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
]
"""

        (self.project_path / "pyproject.toml").write_text(
            pyproject_content, encoding="utf-8"
        )
        print("   [OK] pyproject.toml")

        # __init__.py
        init_content = f'''# -*- coding: utf-8 -*-
"""
{self.project_name} package.
"""
__version__ = "0.1.0"
'''
        (self.project_path / self.project_name / "__init__.py").write_text(
            init_content, encoding="utf-8"
        )
        print("   [OK] __init__.py")

        # README.md
        readme_content = f"""# {self.project_name}

Description de votre projet Python.

## 🚀 Installation

```bash
# Development mode installation
pip install -e ".[dev]"
```

## 🛠️ Development

```bash
# Code formatting
black .
isort .

# Quality check
flake8

# Tests
pytest
pytest --cov  # With coverage
```

## 📋 Make Commands

```bash
make help           # Help
make format         # Automatic formatting
make lint           # Quality check
make test           # Unit tests
make test-cov       # Tests with coverage
make clean          # Cleanup
```

## 📖 Documentation

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete development guide.
"""
        (self.project_path / "README.md").write_text(readme_content, encoding="utf-8")
        print("   [OK] README.md")

        # Test example
        test_content = f'''# -*- coding: utf-8 -*-
"""
Tests pour {self.project_name}.
"""
import pytest
from {self.project_name} import __version__


def test_version():
    """Test de la version du package."""
    assert __version__ == "0.1.0"


def test_import():
    """Test d'import du package."""
    import {self.project_name}
    assert {self.project_name} is not None
'''
        (self.project_path / "tests" / f"test_{self.project_name}.py").write_text(
            test_content, encoding="utf-8"
        )
        print("   [OK] test example")

    def setup_vscode(self):
        """Configure VSCode."""
        print("\n[VSCODE] Configuration VSCode...")

        vscode_files = ["settings.json", "extensions.json"]

        for file in vscode_files:
            source = self.python_tools_path / "vscode" / file
            dest = self.project_path / ".vscode" / file

            if source.exists():
                shutil.copy2(source, dest)
                print(f"   [OK] .vscode/{file}")
            else:
                print(f"   [WARN] Missing VSCode file: {file}")

    def install_hooks(self):
        """Installe les hooks pre-commit."""
        print("\n[HOOKS] Installing pre-commit hooks...")

        try:
            # Check if pre-commit is installed
            precommit_path = shutil.which("pre-commit")
            if precommit_path is None:
                print(
                    "   [WARN] pre-commit not found. Install with: pip install pre-commit"
                )
                return

            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command(
                    [precommit_path, "--version"]
                )
                if not is_valid:
                    print(f"   [WARN] Security validation failed: {error_msg}")
                    return

            subprocess.run(  # noqa: S603
                [precommit_path, "--version"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )

            # Installer les hooks
            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command(
                    [precommit_path, "install"]
                )
                if not is_valid:
                    print(f"   [WARN] Security validation failed: {error_msg}")
                    return

            subprocess.run(  # noqa: S603
                [precommit_path, "install"],
                cwd=self.project_path,
                check=True,
                capture_output=True,
            )
            print("   [OK] Pre-commit hooks installed")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print(
                "   [WARN] pre-commit not found. Install with: pip install pre-commit"
            )

    def print_next_steps(self):
        """Display next steps."""
        print(
            f"""
[SUCCESS] Python project '{self.project_name}' configured successfully!

[NEXT] Next steps:
1. cd {self.project_path}
2. pip install -e ".[dev]"
3. pre-commit install  # If not already done
4. git add .
5. git commit -m "Initial commit with Python dev environment"

[TOOLS] Useful commands:
- make lint                    # Quality check
- make format                  # Automatic formatting
- make test                    # Tests
- black . && isort .           # Manual formatting
- pytest --cov                 # Tests with coverage

[DOCS] Documentation:
- docs/DEVELOPMENT.md          # Development guide
- {self.python_tools_path}/PYTHON.md  # Complete Python documentation

[END] Happy Python coding!
"""
        )
