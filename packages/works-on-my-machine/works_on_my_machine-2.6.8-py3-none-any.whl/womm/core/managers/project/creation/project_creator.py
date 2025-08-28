#!/usr/bin/env python3
"""
Base project creator for WOMM CLI.
Provides common functionality for all project types.
"""

import shutil
from pathlib import Path
from typing import Dict, Optional

from ....ui.common.console import print_error, print_info
from ....utils.cli_utils import run_command
from ....utils.project.project_validator import ProjectValidator
from ....utils.project.template_helpers import generate_cross_platform_template


class ProjectCreator:
    """Base project creator with common functionality."""

    def __init__(self):
        """Initialize the project creator."""
        self.validator = ProjectValidator()

    def create_project_structure(
        self,
        project_path: Path,
        project_name: str,
        **kwargs,  # noqa: ARG002
    ) -> bool:
        """
        Create the basic project structure.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            **kwargs: Additional configuration options

        Returns:
            True if structure creation was successful, False otherwise
        """
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)

            # Create basic directory structure
            self._create_basic_directories(project_path)

            # Create basic files
            self._create_basic_files(project_path, project_name)

            return True

        except Exception as e:
            print_error(f"Error creating project structure: {e}")
            return False

    def _create_basic_directories(self, project_path: Path) -> None:
        """Create basic directory structure."""
        directories = [
            "src",
            "tests",
            "docs",
            "scripts",
            ".vscode",
        ]

        for directory in directories:
            (project_path / directory).mkdir(exist_ok=True)

    def _create_basic_files(self, project_path: Path, project_name: str) -> None:
        """Create basic project files."""
        # Create README.md
        readme_content = f"""# {project_name}

## Description

{project_name} - A new project created with WOMM CLI.

## Getting Started

### Prerequisites

- Python 3.8+ (for Python projects)
- Node.js 16+ (for JavaScript projects)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
# For Python projects:
pip install -r requirements.txt

# For JavaScript projects:
npm install
```

### Usage

```bash
# Run the project
# For Python projects:
python src/main.py

# For JavaScript projects:
npm start
```

## Development

### Running Tests

```bash
# For Python projects:
pytest

# For JavaScript projects:
npm test
```

### Code Quality

```bash
# For Python projects:
black .
flake8 .
isort .

# For JavaScript projects:
npm run lint
npm run format
```

## License

This project is licensed under the MIT License.
"""

        readme_path = project_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")

        # Create .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm.fming.dev/#use-with-ide
.pdm.toml

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can
#  be added to the global gitignore or merged into this project gitignore.  For a PyCharm
#  project, it is recommended to include the following files:
#  .idea/
#  *.iml
#  *.ipr
#  *.iws

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# nyc test coverage
.nyc_output

# Grunt intermediate storage (https://gruntjs.com/creating-plugins#storing-task-files)
.grunt

# Bower dependency directory (https://bower.io/)
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons (https://nodejs.org/api/addons.html)
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript v1 declaration files
typings/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env
.env.test
.env.production
.env.local
.env.development.local
.env.test.local
.env.production.local

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt
dist

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
*.lcov

# Dependency directories
node_modules/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
"""

        gitignore_path = project_path / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding="utf-8")

    def validate_project_config(
        self, project_name: str, project_path: Path, project_type: str
    ) -> bool:
        """
        Validate project configuration.

        Args:
            project_name: Name of the project
            project_path: Path where to create the project
            project_type: Type of project

        Returns:
            True if configuration is valid, False otherwise
        """
        # Validate project name
        is_valid, error = self.validator.validate_project_name(project_name)
        if not is_valid:
            print_error(f"Invalid project name: {error}")
            return False

        # Validate project path
        is_valid, error = self.validator.validate_project_path(project_path)
        if not is_valid:
            print_error(f"Invalid project path: {error}")
            return False

        # Validate project type
        is_valid, error = self.validator.validate_project_type(project_type)
        if not is_valid:
            print_error(f"Invalid project type: {error}")
            return False

        return True

    def generate_template_file(
        self,
        template_path: Path,
        output_path: Path,
        template_vars: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Generate a file from a template.

        Args:
            template_path: Path to the template file
            output_path: Path where to save the generated file
            template_vars: Variables to substitute in the template

        Returns:
            True if generation was successful, False otherwise
        """
        try:
            if template_vars is None:
                template_vars = {}

            generate_cross_platform_template(template_path, output_path, template_vars)
            return True

        except Exception as e:
            print_error(f"Error generating template file: {e}")
            return False

    def copy_template_directory(
        self, source_dir: Path, target_dir: Path, **kwargs
    ) -> bool:
        """
        Copy a template directory to the target location.

        Args:
            source_dir: Source template directory
            target_dir: Target directory
            **kwargs: Additional options

        Returns:
            True if copy was successful, False otherwise
        """
        try:
            if not source_dir.exists():
                print_error(f"Template directory not found: {source_dir}")
                return False

            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy directory contents
            shutil.copytree(source_dir, target_dir, dirs_exist_ok=True, **kwargs)

            return True

        except Exception as e:
            print_error(f"Error copying template directory: {e}")
            return False

    def setup_git_repository(self, project_path: Path) -> bool:
        """
        Initialize a Git repository for the project.

        Args:
            project_path: Path to the project

        Returns:
            True if Git setup was successful, False otherwise
        """
        try:
            # Check if git is available
            if not shutil.which("git"):
                print_info("Git not found, skipping repository initialization")
                return True

            # Initialize git repository
            result = run_command(
                ["git", "init"],
                cwd=project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True
            else:
                print_error(f"Failed to initialize Git repository: {result.stderr}")
                return False

        except Exception as e:
            print_error(f"Error setting up Git repository: {e}")
            return False
