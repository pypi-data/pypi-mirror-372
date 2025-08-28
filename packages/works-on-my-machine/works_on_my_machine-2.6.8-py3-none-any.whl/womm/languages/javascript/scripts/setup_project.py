#!/usr/bin/env python3
"""
JavaScript/Node.js development environment initialization script.

Usage:
    python setup_project.py [project_name] [--type=node|react|vue|vanilla]
    python setu        try:
            from ....core.tools.cspell_utils import setup_project_cspell

            success = setup_project_cspell(
                project_path, "javascript", project_name
            )
            if success:
                print("   [OK] CSpell configuration created")
            else:
                print("   [WARN] CSpell configuration failed")
        except ImportError:
            print("   [WARN] cspell_utils module not found") --current-dir

Features:
    - Copy development configurations
    - Initialize Git with appropriate .gitignore
    - Configure pre-commit hooks
    - Create basic project structure
    - Configure VSCode and NPM
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

# Import security validator if available
try:
    from ....core.utils.security.security_validator import SecurityValidator

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


class JavaScriptProjectSetup:
    """Class to configure a JavaScript development environment."""

    PROJECT_TYPES = {
        "node": {
            "description": "Backend Node.js with Express",
            "main_file": "src/index.js",
            "module_type": "module",
            "dev_command": "nodemon src/index.js",
            "build_command": 'echo "No build needed for Node.js"',
            "start_command": "node src/index.js",
            "jest_environment": "node",
            "dependencies": '"express": "^4.18.0"',
            "dev_dependencies": '"nodemon": "^3.0.0", "supertest": "^6.3.0"',
            "keywords": "nodejs, express, api",
        },
        "react": {
            "description": "Frontend React with Vite",
            "main_file": "src/main.tsx",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": '"react": "^18.2.0", "react-dom": "^18.2.0"',
            "dev_dependencies": '"@vitejs/plugin-react": "^4.0.0", "vite": "^4.4.0", "@testing-library/react": "^13.4.0", "@testing-library/jest-dom": "^6.0.0"',
            "keywords": "react, frontend, vite",
        },
        "vue": {
            "description": "Frontend Vue.js with Vite",
            "main_file": "src/main.ts",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": '"vue": "^3.3.0"',
            "dev_dependencies": '"@vitejs/plugin-vue": "^4.3.0", "vite": "^4.4.0", "@vue/test-utils": "^2.4.0"',
            "keywords": "vue, frontend, vite",
        },
        "vanilla": {
            "description": "Vanilla JavaScript with bundler",
            "main_file": "src/index.js",
            "module_type": "module",
            "dev_command": "vite",
            "build_command": "vite build",
            "start_command": "vite preview",
            "jest_environment": "jsdom",
            "dependencies": "",
            "dev_dependencies": '"vite": "^4.4.0"',
            "keywords": "javascript, vanilla, vite",
        },
    }

    def __init__(
        self, project_path: Path, project_name: str, project_type: str = "node"
    ):
        """Initialize the JavaScript project configuration script."""
        self.project_path = project_path
        self.project_name = project_name
        self.project_type = project_type
        self.js_tools_path = Path(__file__).parent.parent
        self.devtools_path = self.js_tools_path.parent.parent

    def setup_all(self):
        """Configure the complete development environment."""
        print(f"[JS] Setting up JavaScript environment for '{self.project_name}'")
        print(f"[DIR] Directory: {self.project_path}")
        print(f"[TYPE] Type: {self.PROJECT_TYPES[self.project_type]['description']}")

        self.create_directory_structure()
        self.copy_configs()
        self.setup_git()
        self.setup_cspell()
        self.create_package_json()
        self.create_project_files()
        self.setup_vscode()
        self.setup_development_environment()
        self.install_dependencies()

        print("\n[SUCCESS] JavaScript configuration completed!")
        self.print_next_steps()

    def create_directory_structure(self):
        """Create the basic directory structure."""
        print("\n[DIRS] Creating directory structure...")

        directories = [
            self.project_path / "src",
            self.project_path / "tests",
            self.project_path / "docs",
            self.project_path / ".vscode",
        ]

        # Type-specific directories
        if self.project_type in ["react", "vue"]:
            directories.extend(
                [
                    self.project_path / "public",
                    self.project_path / "src" / "components",
                    self.project_path / "src" / "assets",
                ]
            )

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"   [OK] {directory}")

    def copy_configs(self):
        """Copy configuration files."""
        print("\n[CONFIG] Copying JavaScript configurations...")

        configs = [
            ("configs/.eslintrc.json", ".eslintrc.json"),
            ("configs/prettier.config.js", "prettier.config.js"),
            ("templates/gitignore-node.txt", ".gitignore"),
        ]

        for source, dest in configs:
            source_path = self.js_tools_path / source
            dest_path = self.project_path / dest

            if source_path.exists():
                shutil.copy2(source_path, dest_path)
                print(f"   [OK] {dest}")
            else:
                print(f"   [WARN] Missing file: {source}")

    def setup_git(self):
        """Initialize Git and configure .gitignore."""
        print("\n[GIT] Configuring Git...")

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
                self.project_path, "javascript", self.project_name
            )
            if success:
                print("   [OK] CSpell configuration created")
            else:
                print("   [WARN] Error during CSpell configuration")
        except ImportError:
            print("   [WARN] cspell_utils module not found")

    def setup_development_environment(self):
        """Configure the JavaScript development environment."""
        print("[ENV] Setting up development environment...")

        # Importer le gestionnaire d'environnement
        devtools_path = Path.home() / ".womm"
        sys.path.insert(0, str(devtools_path))

        print("   [INFO] Development environment setup skipped (legacy)")
        return True

    def create_package_json(self):
        """Create the package.json file."""
        print("\n[PACKAGE] Creating package.json...")

        template_path = self.js_tools_path / "templates" / "package.template.json"
        if not template_path.exists():
            print("   [WARN] package.json template missing")
            return

        # Read template
        template_content = template_path.read_text(encoding="utf-8")

        # Replace placeholders
        config = self.PROJECT_TYPES[self.project_type]
        replacements = {
            "{{PROJECT_NAME}}": self.project_name,
            "{{MAIN_FILE}}": config["main_file"],
            "{{MODULE_TYPE}}": config["module_type"],
            "{{DEV_COMMAND}}": config["dev_command"],
            "{{BUILD_COMMAND}}": config["build_command"],
            "{{START_COMMAND}}": config["start_command"],
            "{{JEST_ENVIRONMENT}}": config["jest_environment"],
            "{{DEPENDENCIES}}": config["dependencies"],
            "{{DEV_DEPENDENCIES}}": config["dev_dependencies"],
            "{{KEYWORDS}}": config["keywords"],
        }

        for placeholder, value in replacements.items():
            template_content = template_content.replace(placeholder, value)

        # Clean up extra commas
        template_content = template_content.replace(",\n    \n  }", "\n  }")
        template_content = template_content.replace(",\n    {{", "\n    {{")

        # Write file
        (self.project_path / "package.json").write_text(
            template_content, encoding="utf-8"
        )
        print("   [OK] package.json")

    def create_project_files(self):
        """Create basic project files based on type."""
        print("\n[FILES] Creating basic files...")

        # README.md
        readme_content = f"""# {self.project_name}

{self.PROJECT_TYPES[self.project_type]["description"]}

## 🚀 Installation

```bash
npm install
```

## [DEV] Development

```bash
# Development server
npm run dev

# Production build
npm run build

# Tests
npm test
npm run test:coverage

# Linting and formatting
npm run lint
npm run format
```

## [SCRIPTS] Available Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm run start` - Production server
- `npm run lint` - ESLint checking
- `npm run format` - Prettier formatting
- `npm test` - Jest tests

## [DOCS] Documentation

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the complete development guide.
"""
        (self.project_path / "README.md").write_text(readme_content, encoding="utf-8")
        print("   [OK] README.md")

        # Create type-specific files
        self._create_type_specific_files()

        # TypeScript config (if needed)
        if self.project_type != "vanilla":
            self._create_typescript_config()

        # Test example
        self._create_test_files()

    def _create_type_specific_files(self):
        """Create type-specific project files."""
        if self.project_type == "node":
            # src/index.js
            index_content = """import express from 'express';

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Hello World! 🚀' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});

export default app;
"""
            (self.project_path / "src" / "index.js").write_text(
                index_content, encoding="utf-8"
            )

        elif self.project_type == "react":
            # src/main.tsx
            main_content = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
"""
            (self.project_path / "src" / "main.tsx").write_text(
                main_content, encoding="utf-8"
            )

            # src/App.tsx
            app_content = f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 Welcome to {self.project_name}</h1>
        <p>Your React app is ready!</p>
      </header>
    </div>
  );
}}

export default App;
"""
            (self.project_path / "src" / "App.tsx").write_text(
                app_content, encoding="utf-8"
            )

            # index.html
            html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{self.project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""
            (self.project_path / "index.html").write_text(
                html_content, encoding="utf-8"
            )

        elif self.project_type == "vue":
            # src/main.ts
            main_content = """import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
"""
            (self.project_path / "src" / "main.ts").write_text(
                main_content, encoding="utf-8"
            )

        print(f"   [OK] {self.project_type} files created")

    def _create_typescript_config(self):
        """Create TypeScript configuration."""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True,
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}],
        }

        if self.project_type == "react":
            tsconfig["compilerOptions"]["jsx"] = "react-jsx"

        (self.project_path / "tsconfig.json").write_text(
            json.dumps(tsconfig, indent=2), encoding="utf-8"
        )
        print("   [OK] tsconfig.json")

    def _create_test_files(self):
        """Create example test files."""
        if self.project_type == "node":
            test_content = """import request from 'supertest';
import app from '../src/index.js';

describe('API Tests', () => {
  test('GET / should return welcome message', async () => {
    const response = await request(app)
      .get('/')
      .expect(200);

    expect(response.body.message).toBe('Hello World! 🚀');
  });

  test('GET /health should return status OK', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);

    expect(response.body.status).toBe('OK');
  });
});
"""
        else:
            test_content = f"""import {{ render, screen }} from '@testing-library/react';
import App from '../src/App';

describe('App Component', () => {{
  test('renders welcome message', () => {{
    render(<App />);
    const linkElement = screen.getByText(/Welcome to {self.project_name}/i);
    expect(linkElement).toBeInTheDocument();
  }});
}});
"""

        (self.project_path / "tests" / f"{self.project_name}.test.js").write_text(
            test_content, encoding="utf-8"
        )
        print("   [OK] Test files")

    def setup_vscode(self):
        """Configure VSCode."""
        print("\n[VSCODE] Configuring VSCode...")

        vscode_files = ["settings.json", "extensions.json"]

        for file in vscode_files:
            source = self.js_tools_path / "vscode" / file
            dest = self.project_path / ".vscode" / file

            if source.exists():
                shutil.copy2(source, dest)
                print(f"   [OK] .vscode/{file}")
            else:
                print(f"   [WARN] Missing VSCode file: {file}")

    def install_dependencies(self):
        """Install NPM dependencies."""
        print("\n[INSTALL] Installing dependencies...")

        try:
            # Check npm
            npm_path = shutil.which("npm")
            if npm_path is None:
                print("   [WARN] npm not found. Install Node.js/npm")
                return

            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command(
                    [npm_path, "--version"]
                )
                if not is_valid:
                    print(f"   [WARN] Security validation failed: {error_msg}")
                    return

            subprocess.run(  # noqa: S603
                [npm_path, "--version"], capture_output=True, check=True
            )

            # Install dependencies
            print("   [PROGRESS] Installing...")
            # Security validation
            if SECURITY_AVAILABLE:
                validator = SecurityValidator()
                is_valid, error_msg = validator.validate_command([npm_path, "install"])
                if not is_valid:
                    print(f"   [WARN] Security validation failed: {error_msg}")
                    return

            result = subprocess.run(  # noqa: S603
                [npm_path, "install"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("   [OK] Dependencies installed")

                # Install husky
                npx_path = shutil.which("npx")
                if npx_path is not None:
                    # Security validation
                    if SECURITY_AVAILABLE:
                        validator = SecurityValidator()
                        is_valid, error_msg = validator.validate_command(
                            [npx_path, "husky", "install"]
                        )
                        if not is_valid:
                            print(f"   [WARN] Security validation failed: {error_msg}")
                            return

                    subprocess.run(  # noqa: S603
                        [npx_path, "husky", "install"],
                        cwd=self.project_path,
                        capture_output=True,
                    )
                    print("   [OK] Husky hooks configured")
                else:
                    print("   [WARN] npx not found, skipping husky installation")
            else:
                print(f"   [WARN] Installation error: {result.stderr}")

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   [WARN] npm not found. Install Node.js/npm")

    def print_next_steps(self):
        """Display next steps."""
        print(
            f"""
[SUCCESS] JavaScript project '{self.project_name}' configured successfully!

[NEXT] Next steps:
1. cd {self.project_path}
2. npm install  # If not already done
3. npm run dev  # Start development server
4. git add .
5. git commit -m "Initial commit with JS dev environment"

[TOOLS] Useful commands:
- npm run dev              # Development server
- npm run build            # Production build
- npm run lint             # ESLint check
- npm run format           # Prettier formatting
- npm test                 # Jest tests

[DOCS] Documentation:
- docs/DEVELOPMENT.md      # Development guide
- {self.js_tools_path}/JAVASCRIPT.md  # Complete JavaScript documentation

[END] Happy JavaScript coding!
"""
        )
