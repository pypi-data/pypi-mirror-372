# 🟨 JavaScript/Node.js Development Tools

[🏠 Main](../../README.md) > [🟨 JavaScript](JAVASCRIPT.md)

[← Back to Main Documentation](../../README.md)

> **Modern and complete JavaScript development environment**  
> ESLint + Prettier + TypeScript + Jest + Husky + VSCode

## 📚 Documentation Navigation

**🏠 [Main Documentation](../../README.md)**  
**🐍 [Python Development](../python/PYTHON.md)**  
**🟨 [JavaScript Development](JAVASCRIPT.md)** (You are here)  
**⚙️ [Environment Setup](../../ENVIRONMENT_SETUP.md)**  
**🔧 [Prerequisites Installation](../../PREREQUISITE_INSTALLER.md)**

## Table of Contents
- [Quick Usage](#-quick-usage)
- [JavaScript Tools Structure](#-javascript-tools-structure)
- [Included Configuration](#️-included-configuration)
- [Supported Project Types](#-supported-project-types)
- [Available Scripts](#️-available-scripts)
- [Integrated Configurations](#️-integrated-configurations)
- [Provided Templates](#-provided-templates)
- [Recommended Workflow](#-recommended-workflow)
- [Customization](#-customization)
- [Troubleshooting](#-troubleshooting)
- [Supported Types](#-supported-types)

## Related Documentation
- [Python Tools](../python/PYTHON.md) - Alternative language setup
- [Main README](../../README.md) - Project overview
- [Environment Setup](../../ENVIRONMENT_SETUP.md) - Development environment management
- [Common Commands](../../COMMON_COMMANDS.md) - Standard commands and workflows

## 🚀 Quick Usage

> **For complete command reference, see [Common Commands](../../COMMON_COMMANDS.md)**

```bash
# Create a new JavaScript/Node.js project
womm new javascript my-project

# In an existing project
cd my-existing-project
womm new javascript --current-dir

# Linting and formatting
womm lint javascript  # Auto-detection if in a JS project
npm run lint      # ESLint checking
npm run format    # Prettier formatting
```

## 📁 JavaScript Tools Structure

```
languages/javascript/
├── 📋 JAVASCRIPT.md             # This file
├── 📜 scripts/
│   └── setup_project.py         # JavaScript project initialization
├── ⚙️ configs/
│   ├── .eslintrc.json           # ESLint configuration
│   └── prettier.config.js       # Prettier configuration
├── 📝 templates/
│   ├── package.template.json    # package.json template
│   ├── gitignore-node.txt       # Node.js .gitignore
│   ├── cspell.json.template     # Spell checking template
│   └── DEVELOPMENT.md.template  # Development guide
└── 🔧 vscode/
    ├── settings.json            # VSCode configuration
    └── extensions.json          # Recommended extensions
```

## ⚙️ Included Configuration

### 🎨 **Formatting (Prettier)**
- **Modern standards** JavaScript/TypeScript
- **Automatic formatting** on save (VSCode)
- **Consistent rules** with ESLint
- **Support** for React, Vue, Angular

### 🔍 **Linting (ESLint)**
- **Recommended rules** + customized
- **TypeScript** integrated support
- **React/Vue** rules if applicable
- **Security** and best practices

### 🧪 **Testing (Jest)**
- **Modern framework** with mocking
- **Automatic code coverage**
- **TypeScript support** integrated
- **Snapshot testing** for React

### 🔒 **Git Hooks (Husky)**
- **Automatic formatting** before commit
- **Mandatory linting** pre-commit
- **Tests** before push
- **Conventional** messages

## 📦 Supported Project Types

### 🌐 **Node.js Backend**
- Express, Koa, Fastify
- REST and GraphQL APIs
- Microservices
- TypeScript ready

### ⚛️ **React Frontend**
- Create React App
- Next.js
- Vite + React
- TypeScript support

### 💚 **Vue.js Applications**
- Vue CLI
- Nuxt.js
- Vite + Vue
- Composition API

### 📱 **Universal Applications**
- Vanilla JavaScript
- Webpack/Vite
- TypeScript
- Progressive Web Apps

## 🛠️ Available Scripts

### 🆕 **Project Creation**
```bash
# Interactive assistant
womm new javascript my-app

# Specific types
womm new javascript my-api --type=node
womm new javascript my-front --type=react
womm new javascript my-vue --type=vue
```

### 🔧 **Development**
```bash
# Complete linting
npm run lint
# or directly
eslint src/

# Formatting
npm run format
# or directly
prettier --write .

# Tests
npm test
npm run test:coverage
```

### 📋 **Standard NPM Scripts**
```json
{
  "scripts": {
    "dev": "vite", // or other dev server
    "build": "vite build",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "format": "prettier --write .",
    "format:check": "prettier --check .",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

## ⚙️ Integrated Configurations

### 📄 **ESLint (.eslintrc.json)**
```json
{
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### 🎨 **Prettier (prettier.config.js)**
```javascript
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
  useTabs: false
};
```

### 🧪 **Jest (jest.config.js)**
```javascript
module.exports = {
  testEnvironment: 'node', // or 'jsdom' for React
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

## 🎯 Provided Templates

### 📦 **package.json**
Adaptive template based on type:
- Modern dependencies
- Standard NPM scripts
- Tool configuration
- Project metadata

### 📝 **.gitignore**
Complete Node.js exclusions:
- `node_modules/`
- Build outputs (`dist/`, `build/`)
- Environment files (`.env.*`)
- IDE and OS files
- Logs and cache

### 🔧 **VSCode**
Specialized configuration:
- JavaScript/TypeScript extensions
- Automatic Prettier formatting
- Real-time ESLint
- Node.js/Browser debugging

## 💡 Recommended Workflow

### 1. **Initialization**
```bash
womm new javascript my-project --type=react
cd my-project
npm install
```

### 2. **Development**
```bash
npm run dev          # Development server
npm run lint         # Continuous verification
npm test             # Tests in watch mode
```

### 3. **Before Commit**
```bash
npm run lint:fix     # Auto correction
npm run format       # Formatting
npm test             # Complete tests
git add . && git commit -m "feat: new feature"
```

## 🔧 Customization

### ⚙️ **Local Configuration**
Override in your project:
- `.eslintrc.json` - Specific ESLint rules
- `prettier.config.js` - Custom formatting
- `jest.config.js` - Test configuration

### 🎨 **VSCode Extensions**
Auto-installed:
- ESLint
- Prettier
- TypeScript
- Jest Runner
- Bracket Pair Colorizer

## 🚨 Troubleshooting

### ❓ **Node.js Not Found**
```bash
# Check Node.js
node --version
npm --version

# Install Node.js via nvm (recommended)
nvm install --lts
nvm use --lts
```

### ❓ **ESLint/Prettier Conflicts**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# ESLint + Prettier configuration
npm install --save-dev eslint-config-prettier
```

### ❓ **Jest Tests Failing**
```bash
# Clear cache
npm test -- --clearCache

# Verbose mode
npm test -- --verbose

# Specific tests
npm test -- --testNamePattern="my test"
```

## 🎯 Supported Types

### 📱 **Frontend Frameworks**
- ✅ React (CRA, Next.js, Vite)
- ✅ Vue.js (CLI, Nuxt.js, Vite)
- ✅ Angular (CLI)
- ✅ Svelte (Kit)

### 🖥️ **Backend Frameworks**
- ✅ Express.js
- ✅ Koa.js
- ✅ Fastify
- ✅ NestJS

### 🛠️ **Build Tools**
- ✅ Vite
- ✅ Webpack
- ✅ Rollup
- ✅ Parcel

---

🟨 **Happy JavaScript coding!** For other languages, see the [📋 Main README](../../README.md)