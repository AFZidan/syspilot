# Git Setup Guide for SysPilot

## Quick Git Setup

### 1. Initialize Repository (if not already done)

```bash
git init
```

### 2. Configure Git (if first time)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. Add All Files

```bash
git add .
```

### 4. Initial Commit

```bash
git commit -m "Initial commit: SysPilot cross-platform system tool

- Complete Linux implementation with Qt GUI
- CPU temperature monitoring with thermometer chart
- Cross-platform architecture for Windows/macOS support
- System cleanup and monitoring services
- Platform factory pattern for service creation
- Comprehensive test suite
- Documentation and build system"
```

### 5. Add Remote Repository (optional)

```bash
git remote add origin https://github.com/yourusername/syspilot.git
git branch -M main
git push -u origin main
```

## What's Tracked

✅ **Source Code**

- All Python files (`syspilot/`, `tests/`)
- Configuration files (`setup.py`, `requirements.txt`, etc.)
- Documentation (`.md` files)
- Assets (`assets/` directory)
- Build configurations (`Makefile`, `setup.cfg`, etc.)

❌ **Ignored Files/Directories**

- Virtual environments (`.venv/`, `venv/`)
- Python bytecode (`__pycache__/`, `*.pyc`)
- Build artifacts (`build/`, `dist/`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Log files (`*.log`, `logs/`)
- Temporary files (`*.tmp`, `temp/`)
- Configuration instances (`config.json`)

## File Summary

**Total tracked files:** ~68 files
**Key components:**

- Cross-platform source code
- Documentation and guides
- Build and packaging files
- Test suite
- Assets and icons

## Recommended Workflow

1. **Feature Development:**

   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git add .
   git commit -m "Add new feature"
   git push origin feature/new-feature
   ```

2. **Platform Development:**

   ```bash
   git checkout -b platform/windows-support
   # Implement Windows features
   git add syspilot/platforms/windows/
   git commit -m "Implement Windows platform support"
   ```

3. **Bug Fixes:**

   ```bash
   git checkout -b bugfix/issue-description
   # Fix the issue
   git add .
   git commit -m "Fix: description of the fix"
   ```

## Branch Strategy Recommendation

- `main` - Stable Linux version
- `develop` - Integration branch
- `platform/windows` - Windows development
- `platform/macos` - macOS development
- `feature/*` - New features
- `bugfix/*` - Bug fixes

## Pre-commit Hooks (Optional)

The project includes `.pre-commit-config.yaml`. To use:

```bash
pip install pre-commit
pre-commit install
```

This will run code formatting and linting before commits.
