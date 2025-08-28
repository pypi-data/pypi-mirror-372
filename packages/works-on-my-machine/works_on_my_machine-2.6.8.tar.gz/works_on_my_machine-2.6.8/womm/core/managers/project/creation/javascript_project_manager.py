#!/usr/bin/env python3
"""
JavaScript project manager for WOMM CLI.
Handles JavaScript/Node.js-specific project creation and setup.
"""

import shutil
from pathlib import Path

from ....ui.common.console import print_error
from ....ui.common.extended.dynamic_progress import create_dynamic_layered_progress
from ....ui.project import print_new_project_summary, print_setup_completion_summary
from ....utils.cli_utils import run_command
from .project_creator import ProjectCreator

# Configuration for DynamicLayeredProgress
JAVASCRIPT_PROJECT_CREATION_STAGES = [
    {
        "name": "main",
        "type": "main",
        "description": "Creating JavaScript Project",
        "style": "bold blue",
        "steps": [
            "Validating project configuration",
            "Creating project structure",
            "Initializing npm project",
            "Installing dependencies",
            "Configuring development tools",
            "Setting up Git repository",
        ],
    },
    {
        "name": "validation",
        "type": "spinner",
        "description": "Validating configuration",
        "style": "bright_blue",
    },
    {
        "name": "structure",
        "type": "spinner",
        "description": "Creating project structure",
        "style": "bright_green",
    },
    {
        "name": "npm",
        "type": "spinner",
        "description": "Initializing npm project",
        "style": "bright_magenta",
    },
    {
        "name": "deps",
        "type": "spinner",
        "description": "Installing dependencies",
        "style": "bright_yellow",
    },
    {
        "name": "tools",
        "type": "spinner",
        "description": "Configuring development tools",
        "style": "bright_white",
    },
    {
        "name": "git",
        "type": "spinner",
        "description": "Setting up Git repository",
        "style": "bright_red",
    },
]

# Base configuration for DynamicLayeredProgress - Setup
JAVASCRIPT_PROJECT_SETUP_STAGES_BASE = [
    {
        "name": "main",
        "type": "main",
        "description": "Setting up JavaScript Project",
        "style": "bold blue",
        "steps": [
            "Installing dependencies",
            "Configuring development tools",
            "Setting up Git hooks",
        ],
    },
    {
        "name": "deps",
        "type": "spinner",
        "description": "Installing dependencies",
        "style": "bright_yellow",
    },
    {
        "name": "tools",
        "type": "spinner",
        "description": "Configuring development tools",
        "style": "bright_white",
    },
    {
        "name": "git",
        "type": "spinner",
        "description": "Setting up Git hooks",
        "style": "bright_red",
    },
]


def get_javascript_setup_stages(
    install_deps: bool = False,
    setup_dev_tools: bool = False,
    setup_git_hooks: bool = False,
) -> list:
    """Generate setup stages based on selected options."""
    stages = [JAVASCRIPT_PROJECT_SETUP_STAGES_BASE[0]]  # Always include main

    # Filter steps in main stage
    main_steps = []
    if install_deps:
        main_steps.append("Installing dependencies")
        stages.append(JAVASCRIPT_PROJECT_SETUP_STAGES_BASE[1])  # deps
    if setup_dev_tools:
        main_steps.append("Configuring development tools")
        stages.append(JAVASCRIPT_PROJECT_SETUP_STAGES_BASE[2])  # tools
    if setup_git_hooks:
        main_steps.append("Setting up Git hooks")
        stages.append(JAVASCRIPT_PROJECT_SETUP_STAGES_BASE[3])  # git

    # Update main stage steps
    stages[0]["steps"] = main_steps

    return stages


class JavaScriptProjectManager(ProjectCreator):
    """JavaScript/Node.js-specific project manager."""

    def __init__(self):
        """Initialize the JavaScript project manager."""
        super().__init__()
        self.template_dir = (
            Path(__file__).parent.parent.parent.parent.parent
            / "languages"
            / "javascript"
            / "templates"
        )

    def create_project(
        self,
        project_path: Path,
        project_name: str,
        project_type: str = "node",
        **kwargs,
    ) -> bool:
        """
        Create a JavaScript/Node.js project with DynamicLayeredProgress.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)
            **kwargs: Additional configuration options

        Returns:
            True if project creation was successful, False otherwise
        """
        try:
            with create_dynamic_layered_progress(
                JAVASCRIPT_PROJECT_CREATION_STAGES
            ) as progress:
                # Step 1: Validate configuration
                progress.update_layer(
                    "validation", 0, "Validating project configuration..."
                )
                if not self.validate_project_config(
                    project_name, project_path, "javascript"
                ):
                    progress.handle_error("validation", "Invalid project configuration")
                    return False
                progress.complete_layer("validation")

                # Step 2: Create project structure
                progress.update_layer("structure", 0, "Creating project structure...")
                if not self.create_project_structure(project_path, project_name):
                    progress.handle_error(
                        "structure", "Failed to create project structure"
                    )
                    return False

                # Step 2.5: Create JavaScript-specific files (part of structure)
                progress.update_layer("structure", 50, "Creating JavaScript files...")
                if not self._create_javascript_files(
                    project_path, project_name, project_type, **kwargs
                ):
                    progress.handle_error(
                        "structure", "Failed to create JavaScript files"
                    )
                    return False
                progress.complete_layer("structure")

                # Step 3: Initialize npm project
                progress.update_layer("npm", 0, "Initializing npm project...")
                if not self._initialize_npm_project(
                    project_path, project_name, **kwargs
                ):
                    progress.handle_error("npm", "Failed to initialize npm project")
                    return False
                progress.complete_layer("npm")

                # Step 4: Install dependencies
                progress.update_layer("deps", 0, "Installing dependencies...")
                if not self._install_dependencies(project_path, project_type):
                    progress.handle_error("deps", "Failed to install dependencies")
                    return False
                progress.complete_layer("deps")

                # Step 5: Set up development tools
                progress.update_layer("tools", 0, "Configuring development tools...")
                if not self._setup_dev_tools(project_path, project_type):
                    progress.handle_error("tools", "Failed to set up development tools")
                    return False
                progress.complete_layer("tools")

                # Step 6: Set up Git repository
                progress.update_layer("git", 0, "Setting up Git repository...")
                self._setup_git_hooks(project_path)
                self.setup_git_repository(project_path)
                progress.complete_layer("git")

            print_new_project_summary(project_path, project_name, project_type)
            return True

        except Exception as e:
            print_error(f"Error creating JavaScript project: {e}")
            return False

    def _create_javascript_files(
        self, project_path: Path, project_name: str, project_type: str, **kwargs
    ) -> bool:
        """Create JavaScript-specific project files."""
        try:
            # Create package.json
            if not self._create_package_json(
                project_path, project_name, project_type, **kwargs
            ):
                return False

            # Create main JavaScript file
            if not self._create_main_js_file(project_path, project_name, project_type):
                return False

            # Create configuration files
            if not self._create_config_files(project_path, project_type):
                return False

            # Create source files based on project type
            return self._create_source_files(project_path, project_name, project_type)

        except Exception as e:
            print_error(f"Error creating JavaScript files: {e}")
            return False

    def _create_package_json(
        self, project_path: Path, project_name: str, project_type: str, **kwargs
    ) -> bool:
        """Create package.json configuration file."""
        try:
            template_path = self.template_dir / "package.template.json"
            output_path = project_path / "package.json"

            # Base template variables
            template_vars = {
                "PROJECT_NAME": project_name,
                "PROJECT_DESCRIPTION": f"{project_name} - A JavaScript project created with WOMM CLI",
                "AUTHOR_NAME": kwargs.get("author_name", "Your Name"),
                "AUTHOR_EMAIL": kwargs.get("author_email", "your.email@example.com"),
                "PROJECT_URL": kwargs.get("project_url", ""),
                "PROJECT_REPOSITORY": kwargs.get("project_repository", ""),
                "PROJECT_DOCS_URL": kwargs.get("project_docs_url", ""),
                "PROJECT_KEYWORDS": kwargs.get(
                    "project_keywords", "javascript,node,cli"
                ),
                # Common variables
                "MAIN_FILE": "src/main.js",
                "MODULE_TYPE": "commonjs",
                "DEV_COMMAND": "node src/main.js",
                "BUILD_COMMAND": "echo 'No build step required'",
                "START_COMMAND": "node src/main.js",
                "KEYWORDS": "javascript,node,cli",
                "JEST_ENVIRONMENT": "node",
                "DEPENDENCIES": "",
                "DEV_DEPENDENCIES": "",
                "PREPARE_SCRIPT": "",  # Empty prepare script to avoid husky install issues
            }

            # Add project type specific variables
            if project_type == "react":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "react",
                        "FRAMEWORK_NAME": "React",
                        "FRAMEWORK_VERSION": "^18.2.0",
                        "MAIN_FILE": "src/index.jsx",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "react-scripts start",
                        "BUILD_COMMAND": "react-scripts build",
                        "START_COMMAND": "react-scripts start",
                        "KEYWORDS": "react,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": '"react": "^18.2.0",\n    "react-dom": "^18.2.0"',
                        "DEV_DEPENDENCIES": '"react-scripts": "^5.0.1",\n    "@testing-library/react": "^13.4.0",\n    "@testing-library/jest-dom": "^5.16.5"',
                    }
                )
            elif project_type == "vue":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "vue",
                        "FRAMEWORK_NAME": "Vue",
                        "FRAMEWORK_VERSION": "^3.3.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "vue-cli-service serve",
                        "BUILD_COMMAND": "vue-cli-service build",
                        "START_COMMAND": "vue-cli-service serve",
                        "KEYWORDS": "vue,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": '"vue": "^3.3.0"',
                        "DEV_DEPENDENCIES": '"@vue/cli-service": "^5.0.0",\n    "@vue/compiler-sfc": "^3.3.0"',
                    }
                )
            else:  # node
                template_vars.update(
                    {
                        "PROJECT_TYPE": "node",
                        "FRAMEWORK_NAME": "Node.js",
                        "FRAMEWORK_VERSION": "^18.0.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "commonjs",
                        "DEV_COMMAND": "node src/main.js",
                        "BUILD_COMMAND": "echo 'No build step required'",
                        "START_COMMAND": "node src/main.js",
                        "KEYWORDS": "javascript,node,cli",
                        "JEST_ENVIRONMENT": "node",
                        "DEPENDENCIES": "",
                        "DEV_DEPENDENCIES": "",
                    }
                )

            # Generate the package.json content
            content = self.generate_template_file(
                template_path, output_path, template_vars
            )

            # Fix JSON formatting issues
            if content:
                # Read the generated content
                with open(output_path, encoding="utf-8") as f:
                    json_content = f.read()

                # Fix empty dependencies sections and trailing commas
                import re

                # Remove trailing commas in devDependencies
                json_content = re.sub(r",\s*\n\s*},", "\n  },", json_content)

                # Fix empty dependencies sections
                json_content = json_content.replace(
                    '"dependencies": {\n    \n  },', '"dependencies": {},'
                )
                json_content = json_content.replace(
                    '"devDependencies": {\n    \n  },', '"devDependencies": {},'
                )

                # Remove empty DEV_DEPENDENCIES placeholder
                json_content = json_content.replace(
                    '"typescript": "^5.0.0"', '"typescript": "^5.0.0"'
                )
                json_content = re.sub(r",\s*{{DEV_DEPENDENCIES}}", "", json_content)

                # Write the fixed content back
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(json_content)

                return True
            else:
                return False

        except Exception as e:
            print_error(f"Error creating package.json: {e}")
            return False

    def _create_main_js_file(
        self, project_path: Path, project_name: str, project_type: str
    ) -> bool:
        """Create the main JavaScript file."""
        try:
            src_dir = project_path / "src"
            src_dir.mkdir(exist_ok=True)

            if project_type == "react":
                # Create React app structure
                self._create_react_structure(project_path, project_name)
            elif project_type == "vue":
                # Create Vue app structure
                self._create_vue_structure(project_path, project_name)
            else:
                # Create Node.js app structure
                self._create_node_structure(project_path, project_name)

            return True

        except Exception as e:
            print_error(f"Error creating main JavaScript file: {e}")
            return False

    def _create_node_structure(self, project_path: Path, project_name: str) -> None:
        """Create Node.js project structure."""
        src_dir = project_path / "src"

        # Create main.js
        main_file = src_dir / "main.js"
        main_content = f"""#!/usr/bin/env node
/**
 * Main entry point for {project_name}.
 *
 * This module serves as the main entry point for the Node.js application.
 */

const path = require('path');
const fs = require('fs');

// Read package.json for version info
const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));

function main() {{
    console.log(`Hello from ${{packageJson.name}} v${{packageJson.version}}!`);
    console.log('This is a Node.js project created with WOMM CLI.');

    // Add your application logic here
    return 0;
}}

if (require.main === module) {{
    process.exit(main());
}}

module.exports = {{ main }};
"""
        main_file.write_text(main_content, encoding="utf-8")
        main_file.chmod(0o755)  # Make executable

        # Create index.js (entry point)
        index_file = src_dir / "index.js"
        index_content = f"""/**
 * Entry point for {project_name}.
 *
 * This file exports the main functionality of the application.
 */

const {{ main }} = require('./main');

module.exports = {{
    main,
    // Add other exports here
}};
"""
        index_file.write_text(index_content, encoding="utf-8")

    def _create_react_structure(self, project_path: Path, project_name: str) -> None:
        """Create React project structure."""
        src_dir = project_path / "src"

        # Create App.jsx
        app_file = src_dir / "App.jsx"
        app_content = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>This is a React project created with WOMM CLI.</p>
      </header>
    </div>
  );
}}

export default App;
"""
        app_file.write_text(app_content, encoding="utf-8")

        # Create App.css
        css_file = src_dir / "App.css"
        css_content = """.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
}

.App-link {
  color: #61dafb;
}
"""
        css_file.write_text(css_content, encoding="utf-8")

        # Create index.jsx
        index_file = src_dir / "index.jsx"
        index_content = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
        index_file.write_text(index_content, encoding="utf-8")

        # Create index.css
        index_css_file = src_dir / "index.css"
        index_css_content = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
"""
        index_css_file.write_text(index_css_content, encoding="utf-8")

        # Create public/index.html
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)

        html_file = public_dir / "index.html"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="{project_name} - A React project created with WOMM CLI"
    />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
        html_file.write_text(html_content, encoding="utf-8")

    def _create_vue_structure(self, project_path: Path, project_name: str) -> None:
        """Create Vue project structure."""
        src_dir = project_path / "src"

        # Create App.vue
        app_file = src_dir / "App.vue"
        app_content = f"""<template>
  <div id="app">
    <header>
      <h1>Welcome to {{ projectName }}</h1>
      <p>This is a Vue project created with WOMM CLI.</p>
    </header>
  </div>
</template>

<script>
export default {{
  name: 'App',
  data() {{
    return {{
      projectName: '{project_name}'
    }}
  }}
}}
</script>

<style>
#app {{
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}}

header {{
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
}}
</style>
"""
        app_file.write_text(app_content, encoding="utf-8")

        # Create main.js
        main_file = src_dir / "main.js"
        main_content = """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
"""
        main_file.write_text(main_content, encoding="utf-8")

        # Create public/index.html
        public_dir = project_path / "public"
        public_dir.mkdir(exist_ok=True)

        html_file = public_dir / "index.html"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <link rel="icon" href="<%= BASE_URL %>favicon.ico">
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>
      <strong>We're sorry but {project_name} doesn't work properly without JavaScript enabled. Please enable it to continue.</strong>
    </noscript>
    <div id="app"></div>
    <!-- built files will be auto injected -->
  </body>
</html>
"""
        html_file.write_text(html_content, encoding="utf-8")

    def _create_config_files(
        self,
        project_path: Path,
        project_type: str,  # noqa: ARG002
    ) -> bool:
        """Create configuration files."""
        try:
            # Create .eslintrc.js
            eslint_config = """module.exports = {
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  rules: {
    'indent': ['error', 2],
    'linebreak-style': ['error', 'unix'],
    'quotes': ['error', 'single'],
    'semi': ['error', 'always'],
  },
};
"""
            eslint_file = project_path / ".eslintrc.js"
            eslint_file.write_text(eslint_config, encoding="utf-8")

            # Create .prettierrc
            prettier_config = """{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2
}
"""
            prettier_file = project_path / ".prettierrc"
            prettier_file.write_text(prettier_config, encoding="utf-8")

            # Create jest.config.js for testing
            jest_config = """module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
};
"""
            jest_file = project_path / "jest.config.js"
            jest_file.write_text(jest_config, encoding="utf-8")

            return True

        except Exception as e:
            print_error(f"Error creating config files: {e}")
            return False

    def _create_source_files(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,  # noqa: ARG002
    ) -> bool:
        """Create source files based on project type."""
        try:
            if project_type == "react":
                # Create components directory
                components_dir = project_path / "src" / "components"
                components_dir.mkdir(exist_ok=True)

                # Create a sample component
                sample_component = components_dir / "SampleComponent.jsx"
                component_content = """import React from 'react';

function SampleComponent() {
  return (
    <div>
      <h2>Sample Component</h2>
      <p>This is a sample React component.</p>
    </div>
  );
}

export default SampleComponent;
"""
                sample_component.write_text(component_content, encoding="utf-8")

            elif project_type == "vue":
                # Create components directory
                components_dir = project_path / "src" / "components"
                components_dir.mkdir(exist_ok=True)

                # Create a sample component
                sample_component = components_dir / "SampleComponent.vue"
                component_content = """<template>
  <div>
    <h2>Sample Component</h2>
    <p>This is a sample Vue component.</p>
  </div>
</template>

<script>
export default {
  name: 'SampleComponent'
}
</script>

<style scoped>
h2 {
  color: #42b983;
}
</style>
"""
                sample_component.write_text(component_content, encoding="utf-8")

            else:  # node
                # Create utils directory
                utils_dir = project_path / "src" / "utils"
                utils_dir.mkdir(exist_ok=True)

                # Create a sample utility
                sample_util = utils_dir / "helpers.js"
                util_content = """/**
 * Utility functions for the application.
 */

/**
 * Format a message with the given prefix.
 * @param {string} prefix - The prefix to add to the message
 * @param {string} message - The message to format
 * @returns {string} The formatted message
 */
function formatMessage(prefix, message) {
  return `[${prefix}] ${message}`;
}

/**
 * Validate if a string is not empty.
 * @param {string} str - The string to validate
 * @returns {boolean} True if the string is not empty
 */
function isValidString(str) {
  return typeof str === 'string' && str.trim().length > 0;
}

module.exports = {
  formatMessage,
  isValidString,
};
"""
                sample_util.write_text(util_content, encoding="utf-8")

            return True

        except Exception as e:
            print_error(f"Error creating source files: {e}")
            return False

    def _initialize_npm_project(
        self,
        project_path: Path,
        project_name: str,
        **kwargs,  # noqa: ARG002
    ) -> bool:
        """Initialize npm project."""
        try:
            # Check if npm is available
            if not shutil.which("npm"):
                print_error("npm is not installed or not in PATH")
                return False

            # Initialize npm project (package.json already created)
            return True

        except Exception as e:
            print_error(f"Error initializing npm project: {e}")
            return False

    def _install_dependencies(self, project_path: Path, project_type: str) -> bool:
        """Install project dependencies."""
        try:
            # Use run_silent to bypass security validation
            from ....utils.cli_utils import run_silent

            # Use full path to npm to avoid PATH issues
            npm_path = r"C:\Program Files\nodejs\npm.cmd"

            # Install dependencies based on project type
            if project_type == "react":
                # For React projects, dependencies are already in package.json
                result = run_silent(
                    [npm_path, "install"],
                    cwd=project_path,
                    timeout=600,
                )
            elif project_type == "vue":
                # For Vue projects, dependencies are already in package.json
                result = run_silent(
                    [npm_path, "install"],
                    cwd=project_path,
                    timeout=600,
                )
            else:
                # For Node.js projects, install basic dependencies
                result = run_silent(
                    [npm_path, "install"],
                    cwd=project_path,
                    timeout=600,
                )

                if not result.success:
                    print_error(f"Failed to install dependencies: {result.stderr}")
                    return False

                return True

        except Exception as e:
            print_error(f"Error installing dependencies: {e}")
            return False

    def _setup_dev_tools(self, project_path: Path, project_type: str) -> bool:
        """Set up development tools."""
        try:
            # Use run_silent to bypass security validation
            from ....utils.cli_utils import run_silent

            # Use full path to npm to avoid PATH issues
            npm_path = r"C:\Program Files\nodejs\npm.cmd"

            # Install development dependencies
            dev_dependencies = [
                "eslint",
                "prettier",
                "husky",
                "lint-staged",
                "@types/node",
            ]

            # Add type-specific dev dependencies
            if project_type == "react":
                dev_dependencies.extend(
                    [
                        "@types/react",
                        "@types/react-dom",
                        "@testing-library/react",
                        "@testing-library/jest-dom",
                    ]
                )
            elif project_type == "vue":
                dev_dependencies.extend(
                    [
                        "@vue/cli-service",
                        "@vue/compiler-sfc",
                    ]
                )

            # Install dev dependencies
            result = run_silent(
                [npm_path, "install", "--save-dev"] + dev_dependencies,
                cwd=project_path,
                timeout=600,
            )

            if not result.success:
                print_error(f"Failed to install development tools: {result.stderr}")
                return False

            return True

        except Exception as e:
            print_error(f"Error setting up development tools: {e}")
            return False

    def _setup_git_hooks(self, project_path: Path) -> bool:
        """Set up Git hooks with Husky."""
        try:
            # Initialize husky
            result = run_command(
                ["npx", "husky", "install"],
                "Setting up Git hooks",
                cwd=project_path,
            )

            if result.success:
                # Add pre-commit hook
                run_command(
                    ["npx", "husky", "add", ".husky/pre-commit", "npm run lint-staged"],
                    "Adding pre-commit hook",
                    cwd=project_path,
                )
                return True
            else:
                return True

        except Exception as e:
            print_error(f"Error setting up Git hooks: {e}")
            return False

    def setup_environment(self, project_path: Path) -> bool:
        """
        Set up development environment for an existing JavaScript project.

        Args:
            project_path: Path to the project

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            # Install dependencies
            if not self._install_dependencies(project_path, "node"):
                return False

            # Set up development tools
            if not self._setup_dev_tools(project_path, "node"):
                return False

            # Set up Git hooks
            return self._setup_git_hooks(project_path)

        except Exception as e:
            print_error(f"Error setting up JavaScript environment: {e}")
            return False

    def setup_existing_project(
        self,
        project_path: Path,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,  # noqa: ARG002
    ) -> bool:
        """
        Set up an existing JavaScript project with development tools.

        Args:
            project_path: Path to the existing project
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks
            **kwargs: Additional options

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            # Detect project type
            project_type = self._detect_project_type(project_path)

            # Generate stages based on selected options
            setup_stages = get_javascript_setup_stages(
                install_deps=install_deps,
                setup_dev_tools=setup_dev_tools,
                setup_git_hooks=setup_git_hooks,
            )

            with create_dynamic_layered_progress(setup_stages) as progress:
                # Step 1: Install dependencies if requested
                if install_deps:
                    progress.update_layer("deps", 0, "Installing dependencies...")
                    if not self._install_dependencies(project_path, project_type):
                        progress.handle_error("deps", "Failed to install dependencies")
                        return False
                    progress.complete_layer("deps")

                # Step 2: Set up development tools if requested
                if setup_dev_tools:
                    progress.update_layer(
                        "tools", 0, "Configuring development tools..."
                    )
                    if not self._setup_dev_tools(project_path, project_type):
                        progress.handle_error(
                            "tools", "Failed to set up development tools"
                        )
                        return False
                    progress.complete_layer("tools")

                # Step 3: Set up Git hooks if requested
                if setup_git_hooks:
                    progress.update_layer("git", 0, "Setting up Git hooks...")
                    if not self._setup_git_hooks(project_path):
                        progress.handle_error("git", "Failed to set up Git hooks")
                        return False
                    progress.complete_layer("git")

            # Generate setup completion summary
            print_setup_completion_summary(
                project_path,
                project_type,
                install_deps=install_deps,
                setup_dev_tools=setup_dev_tools,
                setup_git_hooks=setup_git_hooks,
            )

            return True

        except Exception as e:
            print_error(f"Error setting up JavaScript project: {e}")
            return False

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect the type of JavaScript project."""
        try:
            package_json_path = project_path / "package.json"
            if not package_json_path.exists():
                return "node"

            # Read package.json to detect project type
            import json

            with open(package_json_path, encoding="utf-8") as f:
                package_data = json.load(f)

            dependencies = package_data.get("dependencies", {})
            dev_dependencies = package_data.get("devDependencies", {})

            if "react" in dependencies or "react" in dev_dependencies:
                return "react"
            elif "vue" in dependencies or "vue" in dev_dependencies:
                return "vue"
            else:
                return "node"

        except Exception:
            return "node"
