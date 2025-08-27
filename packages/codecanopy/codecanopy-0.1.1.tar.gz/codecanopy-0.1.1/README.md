# CodeCanopy 🌳

[![PyPI version](https://badge.fury.io/py/codecanopy.svg)](https://badge.fury.io/py/codecanopy)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/codecanopy)](https://pepy.tech/project/codecanopy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Give LLMs perfect context about your codebase**

CodeCanopy solves the pain of manually copying file contents for LLM conversations. Get clean directory structures and file contents in one command - optimized for pasting into ChatGPT, Claude, or any LLM.

## ⚡ Quick Start

```bash
pip install codecanopy
```

```bash
# Get project structure
codecanopy tree --focus src --ignore node_modules,dist

# Get file contents for LLM
codecanopy cat "src/**/*.js" --exclude "**/*.test.js"
```

## 🎯 Why CodeCanopy?

**Before CodeCanopy:**
```bash
# Manual, tedious process
tree -I node_modules
cat src/utils.js
cat src/components/Header.js  
cat src/api/users.js
# ...repeat for 20+ files
```

**With CodeCanopy:**
```bash
# One command, perfect output
codecanopy tree --focus src --ignore node_modules,dist
codecanopy cat "src/**/*.js" --exclude "**/*.test.js"
```

## 🚀 Installation

```bash
# Install via pip
pip install codecanopy

# Install via pipx (recommended)
pipx install codecanopy

# Development install
git clone https://github.com/sawradip/CodeCanopy
cd CodeCanopy
pip install -e .
```

## 🌳 Tree Command - Smart Directory Structure

### Selective Depth Control
```bash
# Focus on src/, shallow everything else
codecanopy tree --focus src --depth 1

# Multiple focused directories  
codecanopy tree --focus src,lib --ignore node_modules,dist
```

**Example Output:**
```
project/
├── src/                    [focused]
│   ├── components/
│   │   ├── Header.js
│   │   ├── Footer.js
│   │   └── Navigation.js
│   ├── utils/
│   │   ├── api.js
│   │   └── helpers.js
│   └── index.js
├── tests/                  [depth: 1]
│   ├── unit/
│   └── integration/
├── docs/                   [depth: 1]
│   └── ...
└── package.json
```

### Advanced Tree Options
```bash
# Show files and directories
codecanopy tree --focus src

# Custom depth and ignore patterns
codecanopy tree --depth 2 --ignore "*.log,tmp,cache"

# Analyze different directory
codecanopy tree /path/to/project --focus app,lib
```

## 📄 Cat Command - Smart File Contents

### Glob Pattern Matching
```bash
# All JavaScript files
codecanopy cat "src/**/*.js"

# Multiple file types
codecanopy cat "src/**/*.{js,ts,jsx}"

# Specific files only
codecanopy cat src/index.js src/app.js config/database.js
```

### Smart Filtering
```bash
# Exclude test files
codecanopy cat "src/**/*.js" --exclude "**/*.test.js,**/*.spec.js"

# Size limits to avoid token overflow
codecanopy cat "src/**/*.py" --max-size 50KB

# Custom headers for better LLM context
codecanopy cat "src/**/*.js" --header "// File: {path}"
```

**Example Output:**
```
=== src/utils/api.js ===
export const fetchUser = async (id) => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};

=== src/components/Header.js ===
import React from 'react';

const Header = ({ title }) => {
  return <h1>{title}</h1>;
};

export default Header;
```

## ⚙️ Configuration

Create `.codecanopy.json` in your project root:

```json
{
  "ignore": [
    "node_modules",
    ".git", 
    "dist",
    "build",
    ".next",
    "__pycache__"
  ],
  "default_depth": 3,
  "header_format": "=== {path} ===",
  "max_file_size": "100KB",
  "focus_dirs": ["src", "lib"]
}
```

## 🎨 Real-World Examples

### Frontend React Project
```bash
# Project structure
codecanopy tree --focus src/components,src/hooks --depth 2

# Component code for LLM review
codecanopy cat "src/components/**/*.{js,jsx}" --exclude "**/*.test.*"
```

### Backend API Project
```bash
# API structure
codecanopy tree --focus src/routes,src/models --ignore node_modules

# All API code
codecanopy cat "src/{routes,models,middleware}/**/*.js"
```

### Python Django Project
```bash
# Project overview
codecanopy tree --focus myapp --ignore "__pycache__,migrations"

# Models and views
codecanopy cat "myapp/**/*.py" --exclude "**/tests/**"
```

### Full Stack Project Context
```bash
# Complete project for LLM
codecanopy tree --focus src,api --ignore node_modules,dist
codecanopy cat "src/**/*.{js,ts}" "api/**/*.py" --max-size 20KB
```

## 🛠️ Advanced Usage

### Debug Specific Feature
```bash
# Focus on auth module
codecanopy tree --focus src/auth
codecanopy cat "src/auth/**/*.js" "src/middleware/auth.js"
```

### Prepare for Code Review
```bash
# Clean overview
codecanopy tree --ignore node_modules,dist,coverage

# Recent changes only (requires git)
codecanopy cat $(git diff --name-only HEAD~5 | grep -E '\.(js|py|go))
```

### Documentation Generation
```bash
# Project structure for docs
codecanopy tree --files > STRUCTURE.md

# Code samples for documentation
codecanopy cat "examples/**/*.js" --header "### {filename}" > EXAMPLES.md
```

## 📊 Command Reference

### Tree Command
```bash
codecanopy tree [PATH] [OPTIONS]

Options:
  --focus TEXT     Focus directories (full depth). Can be used multiple times.
  --ignore TEXT    Ignore directories/files. Can be used multiple times.
  --depth INTEGER  Global depth limit (default: 3)
  --no-files       Hide files, show only directories
  --config TEXT    Config file path (default: .codecanopy.json)
  --help           Show this message and exit.
```

### Cat Command  
```bash
codecanopy cat PATTERNS [OPTIONS]

Arguments:
  PATTERNS            File patterns (supports globs)

Options:
  --exclude PATTERNS  Exclude file patterns
  --header FORMAT     Header format ({path}, {filename}, {dir})
  --no-headers       Skip file headers
  --max-size SIZE    Skip files larger than size (e.g., 100KB)
  --base-path PATH   Base path for relative paths
  --config FILE      Custom config file path
```

## 💡 Pro Tips for LLM Usage

### Optimal File Selection
```bash
# ✅ Focused and clean
codecanopy tree --focus src --ignore node_modules
codecanopy cat "src/**/*.js" --exclude "**/*.test.js" --max-size 20KB

# ❌ Too much noise
codecanopy tree
codecanopy cat "**/*"
```

### Token Management
```bash
# Large codebase strategy
codecanopy tree --focus src --depth 2  # Structure overview
codecanopy cat "src/index.js" "src/app.js"  # Entry points only

# Feature-specific context
codecanopy tree --focus src/features/auth
codecanopy cat "src/features/auth/**/*.js"
```

### Custom Headers for Context
```bash
# Better LLM understanding
codecanopy cat "src/**/*.py" --header "# File: {path}\n# Purpose: {dir}"

# Markdown-friendly output
codecanopy cat "src/**/*.js" --header "## {filename}\n\`\`\`javascript"
```

## 🔧 Integration Examples

### VS Code Task
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "CodeCanopy: Full Context",
      "type": "shell",
      "command": "codecanopy tree --focus src && codecanopy cat 'src/**/*.js'",
      "group": "build"
    }
  ]
}
```

### Git Hook (Pre-commit)
```bash
#!/bin/sh
# Generate project context for commit messages
codecanopy tree --focus src --depth 2 > .git/PROJECT_CONTEXT
codecanopy cat $(git diff --cached --name-only | head -5) >> .git/PROJECT_CONTEXT
```

### Shell Alias
```bash
# Add to .bashrc or .zshrc
alias llm-context="codecanopy tree --focus src --ignore node_modules && codecanopy cat 'src/**/*.{js,py}' --exclude '**/*.test.*' --max-size 30KB"
```

## 🆚 Comparison

| Tool | Selective Depth | Custom Headers | LLM Optimized | Pattern Matching | Size Control |
|------|----------------|----------------|---------------|------------------|--------------|
| `tree` | ❌ | ❌ | ❌ | ❌ | ❌ |
| `cat` | ❌ | ❌ | ❌ | ❌ | ❌ |  
| `find + cat` | ❌ | ⚠️ | ❌ | ✅ | ❌ |
| **CodeCanopy** | ✅ | ✅ | ✅ | ✅ | ✅ |

## 🤝 Contributing

We welcome contributions! CodeCanopy is built for developers who work with LLMs daily.

```bash
# Development setup
git clone https://github.com/yourusername/codecanopy
cd codecanopy
pip install -e .

# Run tests
python test_codecanopy.py

# Format code
black codecanopy/
```

### Feature Requests
- 🔄 Git integration (show only changed files)
- 📊 Token counting for different LLM models
- 🎨 Syntax highlighting in output
- 📦 Export to different formats (JSON, Markdown)

## 📝 License

MIT License - use it, modify it, ship it.

---

**Made with ❤️ for the AI-assisted development community**

*Stop copying files manually. Start using CodeCanopy.* 🚀