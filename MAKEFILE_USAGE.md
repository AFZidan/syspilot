# SysPilot Makefile Usage Guide

This Makefile provides a comprehensive set of commands for developing, testing, building, and packaging the SysPilot application.

## Quick Start

```bash
# Set up development environment
make setup

# Run tests
make test

# Build .deb package
make deb

# Show all available commands
make help
```

## Available Commands

### Development

- `make setup` - Set up development environment with virtual environment and dependencies
- `make dev-setup` - Enhanced setup with pre-commit hooks for development
- `make check-deps` - Check for missing or incompatible dependencies
- `make clean` - Clean build artifacts and temporary files
- `make dist-clean` - Complete clean including virtual environment

### Code Quality

- `make lint` - Run linting checks (flake8, pylint, mypy)
- `make format` - Format code with black and isort
- `make test` - Run the complete test suite
- `make test-coverage` - Run tests with coverage reporting

### Running the Application

- `make run` - Run application in GUI mode
- `make run-cli` - Run application in CLI mode
- `make run-daemon` - Run application in daemon mode
- `make system-info` - Show system information
- `make clean-temp` - Clean temporary files only

### Installation

- `make install` - Install system-wide (requires sudo)
- `make uninstall` - Uninstall system-wide (requires sudo)

### Packaging

- `make deb` - Build .deb package for Debian/Ubuntu
- `make package` - Build all available packages
- `make package-info` - Show package information and status
- `make install-deb` - Install the built .deb package
- `make uninstall-deb` - Uninstall the .deb package

### Workflows

- `make dev` - Complete development workflow (setup, format, lint, test)
- `make release` - Complete release workflow (clean, setup, test, package)

## Prerequisites

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev \
                    python3-psutil python3-pyqt5 python3-pil \
                    build-essential fakeroot dpkg-dev
```

### For .deb Package Creation

The Makefile automatically handles .deb package creation, but you need:
- `fakeroot` - For building packages without root
- `dpkg-dev` - Debian package development tools

## Usage Examples

### 1. First-time Setup

```bash
# Clone the repository
git clone <repository-url>
cd SysPilot

# Set up development environment
make dev-setup

# Run tests to verify everything works
make test
```

### 2. Development Workflow

```bash
# Make your changes to the code

# Format and lint your code
make format
make lint

# Run tests
make test

# If tests pass, commit your changes
git add .
git commit -m "Your changes"
```

### 3. Building and Installing

```bash
# Build .deb package
make deb

# Install the package
make install-deb

# Test the installed application
syspilot --help

# Uninstall if needed
make uninstall-deb
```

### 4. Release Process

```bash
# Clean everything and build release
make release

# The .deb package will be in dist/
ls -la dist/
```

## Package Details

The built .deb package includes:

- **Application files**: `/usr/local/lib/syspilot/`
- **Executable**: `/usr/local/bin/syspilot`
- **Desktop file**: `/usr/local/share/applications/syspilot.desktop`
- **Icons**: `/usr/local/share/pixmaps/syspilot*.png`
- **Documentation**: `/usr/local/share/doc/syspilot/`

### Dependencies

The .deb package automatically handles these dependencies:
- `python3 (>= 3.8)`
- `python3-pip`
- `python3-venv`
- `python3-psutil`
- `python3-pyqt5`
- `python3-pil`

### Post-installation

After installing the .deb package:
1. Python dependencies are automatically installed
2. Desktop database is updated
3. The application is available as `syspilot` command
4. Desktop entry is available in application menu

## Configuration

### Makefile Variables

You can customize the build by setting these variables:

```bash
# Change installation prefix
make install PREFIX=/opt/syspilot

# Use different Python version
make setup PYTHON=python3.11
```

### Build Directories

- `build/` - Temporary build files
- `dist/` - Final packages and distributions
- `venv/` - Python virtual environment

## Troubleshooting

### Common Issues

1. **Permission denied during install**
   ```bash
   sudo make install
   ```

2. **Missing dependencies**
   ```bash
   make check-deps
   sudo apt install python3-dev build-essential
   ```

3. **Virtual environment issues**
   ```bash
   make dist-clean
   make setup
   ```

4. **Package build fails**
   ```bash
   sudo apt install fakeroot dpkg-dev
   make clean
   make deb
   ```

### Getting Help

- Run `make help` for available commands
- Check `make package-info` for build status
- Ensure all system dependencies are installed

## Development Notes

- The Makefile uses colors for better readability
- All Python operations use the virtual environment
- Build artifacts are automatically cleaned between builds
- Package scripts handle daemon lifecycle during install/remove

## Contributing

When contributing to the project:

1. Always run `make dev` before submitting
2. Ensure all tests pass with `make test`
3. Format code with `make format`
4. Test package creation with `make deb`

For more information, see the main project documentation.
