# SysPilot - Professional System Automation & Cleanup Tool
# Makefile for building, testing, and packaging

# Project variables
PROJECT_NAME = syspilot
VERSION = 1.0.0
PYTHON = python3
PIP = pip3
VENV_DIR = venv
BUILD_DIR = build
DIST_DIR = dist
DEB_DIR = $(BUILD_DIR)/deb
PACKAGE_DIR = $(DEB_DIR)/$(PROJECT_NAME)_$(VERSION)
DEBIAN_DIR = $(PACKAGE_DIR)/DEBIAN

# System paths
PREFIX = /usr/local
BINDIR = $(PREFIX)/bin
LIBDIR = $(PREFIX)/lib/$(PROJECT_NAME)
SHAREDIR = $(PREFIX)/share
APPDIR = $(SHAREDIR)/applications
ICONDIR = $(SHAREDIR)/pixmaps
DOCDIR = $(SHAREDIR)/doc/$(PROJECT_NAME)

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help setup clean test run run-cli run-daemon install uninstall deb package lint format check-deps dev-setup install-deps install-deb uninstall-deb

# Default target
all: setup test package

# Help target
help:
	@echo "$(GREEN)SysPilot Makefile$(NC)"
	@echo "=================="
	@echo ""
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  help         - Show this help message"
	@echo "  setup        - Set up development environment"
	@echo "  dev-setup    - Set up development environment with pre-commit"
	@echo "  clean        - Clean build artifacts"
	@echo "  test         - Run test suite"
	@echo "  run          - Run application in GUI mode"
	@echo "  run-cli      - Run application in CLI mode"
	@echo "  run-daemon   - Run application in daemon mode"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  check-deps   - Check for missing dependencies"
	@echo "  install-deps - Install system dependencies"
	@echo "  install      - Install system-wide"
	@echo "  uninstall    - Uninstall system-wide"
	@echo "  deb          - Build .deb package"
	@echo "  package      - Build all packages"
	@echo "  install-deb  - Install .deb package with dependencies"
	@echo "  uninstall-deb - Uninstall .deb package"
	@echo "  dist-clean   - Clean distribution files"
	@echo ""

# Setup development environment
setup:
	@echo "$(GREEN)Setting up development environment...$(NC)"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "Installing dependencies..."
	@. $(VENV_DIR)/bin/activate && \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r requirements.txt && \
		$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)Development environment setup complete!$(NC)"

# Enhanced development setup with pre-commit
dev-setup: setup
	@echo "$(GREEN)Setting up pre-commit hooks...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		pre-commit install
	@echo "$(GREEN)Development setup complete with pre-commit hooks!$(NC)"

# Clean build artifacts
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(NC)"
	@rm -rf $(BUILD_DIR) $(DIST_DIR)
	@rm -rf *.egg-info
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*~" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@echo "$(GREEN)Clean complete!$(NC)"

# Complete clean including virtual environment
dist-clean: clean
	@echo "$(GREEN)Cleaning distribution files...$(NC)"
	@rm -rf $(VENV_DIR)
	@rm -rf .venv
	@echo "$(GREEN)Distribution clean complete!$(NC)"

# Run tests
test:
	@echo "$(GREEN)Running test suite...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m pytest tests/ -v --tb=short
	@echo "$(GREEN)Tests complete!$(NC)"

# Run tests with coverage
test-coverage:
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) -m pytest tests/ -v --cov=syspilot --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

# Run application in GUI mode
run:
	@echo "$(GREEN)Starting SysPilot in GUI mode...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) main.py

# Run application in CLI mode
run-cli:
	@echo "$(GREEN)Starting SysPilot in CLI mode...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) main.py --cli

# Run application in daemon mode
run-daemon:
	@echo "$(GREEN)Starting SysPilot in daemon mode...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) main.py --daemon

# Show system information
system-info:
	@echo "$(GREEN)Showing system information...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) main.py --system-info

# Clean temporary files only
clean-temp:
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PYTHON) main.py --clean-temp

# Check dependencies
check-deps:
	@echo "$(GREEN)Checking dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		$(PIP) check
	@echo "$(GREEN)Dependency check complete!$(NC)"

# Lint code
lint:
	@echo "$(GREEN)Running linting checks...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		flake8 syspilot/ tests/ && \
		pylint syspilot/ && \
		mypy syspilot/
	@echo "$(GREEN)Linting complete!$(NC)"

# Format code
format:
	@echo "$(GREEN)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && \
		black syspilot/ tests/ && \
		isort syspilot/ tests/
	@echo "$(GREEN)Code formatting complete!$(NC)"

# Install system-wide
install:
	@echo "$(GREEN)Installing SysPilot system-wide...$(NC)"
	@# Check if running as root
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)Error: Installation requires root privileges. Use 'sudo make install'$(NC)"; \
		exit 1; \
	fi
	@# Create directories
	@mkdir -p $(BINDIR) $(LIBDIR) $(APPDIR) $(ICONDIR) $(DOCDIR)
	@# Copy application files
	@cp -r syspilot/ $(LIBDIR)/
	@cp main.py $(LIBDIR)/
	@cp requirements.txt $(LIBDIR)/
	@# Copy assets
	@cp assets/syspilot_logo.png $(ICONDIR)/syspilot.png
	@cp assets/syspilot_icon.png $(ICONDIR)/syspilot-icon.png
	@cp assets/syspilot.desktop $(APPDIR)/
	@# Copy documentation
	@cp README.md CHANGELOG.md LICENSE $(DOCDIR)/
	@# Create wrapper script
	@echo '#!/bin/bash' > $(BINDIR)/syspilot
	@echo 'cd $(LIBDIR)' >> $(BINDIR)/syspilot
	@echo 'exec $(PYTHON) main.py "$$@"' >> $(BINDIR)/syspilot
	@chmod +x $(BINDIR)/syspilot
	@# Update desktop database
	@if command -v update-desktop-database >/dev/null 2>&1; then \
		update-desktop-database $(APPDIR); \
	fi
	@echo "$(GREEN)Installation complete! You can now run 'syspilot' from anywhere.$(NC)"

# Uninstall system-wide
uninstall:
	@echo "$(GREEN)Uninstalling SysPilot...$(NC)"
	@# Check if running as root
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "$(RED)Error: Uninstallation requires root privileges. Use 'sudo make uninstall'$(NC)"; \
		exit 1; \
	fi
	@# Remove files
	@rm -rf $(LIBDIR)
	@rm -f $(BINDIR)/syspilot
	@rm -f $(APPDIR)/syspilot.desktop
	@rm -f $(ICONDIR)/syspilot.png
	@rm -f $(ICONDIR)/syspilot-icon.png
	@rm -rf $(DOCDIR)
	@# Update desktop database
	@if command -v update-desktop-database >/dev/null 2>&1; then \
		update-desktop-database $(APPDIR); \
	fi
	@echo "$(GREEN)Uninstallation complete!$(NC)"

# Build .deb package
deb: clean
	@echo "$(GREEN)Building .deb package...$(NC)"
	@mkdir -p $(DEBIAN_DIR)
	@mkdir -p $(PACKAGE_DIR)$(LIBDIR)
	@mkdir -p $(PACKAGE_DIR)$(BINDIR)
	@mkdir -p $(PACKAGE_DIR)$(APPDIR)
	@mkdir -p $(PACKAGE_DIR)$(ICONDIR)
	@mkdir -p $(PACKAGE_DIR)$(DOCDIR)
	@# Copy application files
	@cp -r syspilot/ $(PACKAGE_DIR)$(LIBDIR)/
	@cp main.py $(PACKAGE_DIR)$(LIBDIR)/
	@cp requirements.txt $(PACKAGE_DIR)$(LIBDIR)/
	@# Copy assets
	@cp assets/syspilot_logo.png $(PACKAGE_DIR)$(ICONDIR)/syspilot.png
	@cp assets/syspilot_icon.png $(PACKAGE_DIR)$(ICONDIR)/syspilot-icon.png
	@cp assets/syspilot.desktop $(PACKAGE_DIR)$(APPDIR)/
	@# Copy documentation
	@cp README.md CHANGELOG.md LICENSE $(PACKAGE_DIR)$(DOCDIR)/
	@# Create wrapper script
	@echo '#!/bin/bash' > $(PACKAGE_DIR)$(BINDIR)/syspilot
	@echo 'cd $(LIBDIR)' >> $(PACKAGE_DIR)$(BINDIR)/syspilot
	@echo 'exec $(PYTHON) main.py "$$@"' >> $(PACKAGE_DIR)$(BINDIR)/syspilot
	@chmod +x $(PACKAGE_DIR)$(BINDIR)/syspilot
	@# Create DEBIAN control file
	@echo 'Package: $(PROJECT_NAME)' > $(DEBIAN_DIR)/control
	@echo 'Version: $(VERSION)' >> $(DEBIAN_DIR)/control
	@echo 'Section: utils' >> $(DEBIAN_DIR)/control
	@echo 'Priority: optional' >> $(DEBIAN_DIR)/control
	@echo 'Architecture: all' >> $(DEBIAN_DIR)/control
	@echo 'Depends: python3 (>= 3.8), python3-pip, python3-venv, python3-psutil, python3-pyqt5, python3-pil' >> $(DEBIAN_DIR)/control
	@echo 'Maintainer: SysPilot Team <contact@syspilot.org>' >> $(DEBIAN_DIR)/control
	@echo 'Description: Professional System Automation & Cleanup Tool' >> $(DEBIAN_DIR)/control
	@echo ' SysPilot is a comprehensive desktop application for Ubuntu and Debian systems' >> $(DEBIAN_DIR)/control
	@echo ' that provides system cleanup and performance monitoring capabilities.' >> $(DEBIAN_DIR)/control
	@echo ' .' >> $(DEBIAN_DIR)/control
	@echo ' Features include:' >> $(DEBIAN_DIR)/control
	@echo ' - System cleanup and optimization' >> $(DEBIAN_DIR)/control
	@echo ' - Performance monitoring and analysis' >> $(DEBIAN_DIR)/control
	@echo ' - Automated maintenance scheduling' >> $(DEBIAN_DIR)/control
	@echo ' - Modern GUI with dark/light themes' >> $(DEBIAN_DIR)/control
	@echo ' - Command-line interface for automation' >> $(DEBIAN_DIR)/control
	@echo ' - Background daemon for continuous monitoring' >> $(DEBIAN_DIR)/control
	@# Create postinst script
	@echo '#!/bin/bash' > $(DEBIAN_DIR)/postinst
	@echo 'set -e' >> $(DEBIAN_DIR)/postinst
	@echo 'if [ "$$1" = "configure" ]; then' >> $(DEBIAN_DIR)/postinst
	@echo '    # Install Python dependencies' >> $(DEBIAN_DIR)/postinst
	@echo '    cd $(LIBDIR)' >> $(DEBIAN_DIR)/postinst
	@echo '    # Try different methods to install Python dependencies' >> $(DEBIAN_DIR)/postinst
	@echo '    if command -v pipx >/dev/null 2>&1; then' >> $(DEBIAN_DIR)/postinst
	@echo '        # Use pipx if available (recommended for externally managed environments)' >> $(DEBIAN_DIR)/postinst
	@echo '        pipx install -e . --force 2>/dev/null || echo "Note: pipx installation failed, using fallback method"' >> $(DEBIAN_DIR)/postinst
	@echo '    elif python3 -m pip install --user -r requirements.txt 2>/dev/null; then' >> $(DEBIAN_DIR)/postinst
	@echo '        echo "Python dependencies installed with pip --user"' >> $(DEBIAN_DIR)/postinst
	@echo '    elif python3 -m pip install --break-system-packages -r requirements.txt 2>/dev/null; then' >> $(DEBIAN_DIR)/postinst
	@echo '        echo "Python dependencies installed with --break-system-packages"' >> $(DEBIAN_DIR)/postinst
	@echo '    else' >> $(DEBIAN_DIR)/postinst
	@echo '        echo "Warning: Could not install Python dependencies automatically"' >> $(DEBIAN_DIR)/postinst
	@echo '        echo "Please install manually with: pip3 install -r $(LIBDIR)/requirements.txt"' >> $(DEBIAN_DIR)/postinst
	@echo '    fi' >> $(DEBIAN_DIR)/postinst
	@echo '    # Update desktop database' >> $(DEBIAN_DIR)/postinst
	@echo '    if command -v update-desktop-database >/dev/null 2>&1; then' >> $(DEBIAN_DIR)/postinst
	@echo '        update-desktop-database $(APPDIR)' >> $(DEBIAN_DIR)/postinst
	@echo '    fi' >> $(DEBIAN_DIR)/postinst
	@echo 'fi' >> $(DEBIAN_DIR)/postinst
	@chmod +x $(DEBIAN_DIR)/postinst
	@# Create prerm script
	@echo '#!/bin/bash' > $(DEBIAN_DIR)/prerm
	@echo 'set -e' >> $(DEBIAN_DIR)/prerm
	@echo 'if [ "$$1" = "remove" ]; then' >> $(DEBIAN_DIR)/prerm
	@echo '    # Stop daemon if running' >> $(DEBIAN_DIR)/prerm
	@echo '    if pgrep -f "syspilot.*daemon" >/dev/null; then' >> $(DEBIAN_DIR)/prerm
	@echo '        pkill -f "syspilot.*daemon" || true' >> $(DEBIAN_DIR)/prerm
	@echo '    fi' >> $(DEBIAN_DIR)/prerm
	@echo 'fi' >> $(DEBIAN_DIR)/prerm
	@chmod +x $(DEBIAN_DIR)/prerm
	@# Create postrm script
	@echo '#!/bin/bash' > $(DEBIAN_DIR)/postrm
	@echo 'set -e' >> $(DEBIAN_DIR)/postrm
	@echo 'if [ "$$1" = "remove" ]; then' >> $(DEBIAN_DIR)/postrm
	@echo '    # Update desktop database (ignore errors)' >> $(DEBIAN_DIR)/postrm
	@echo '    if command -v update-desktop-database >/dev/null 2>&1; then' >> $(DEBIAN_DIR)/postrm
	@echo '        update-desktop-database $(APPDIR) 2>/dev/null || true' >> $(DEBIAN_DIR)/postrm
	@echo '    fi' >> $(DEBIAN_DIR)/postrm
	@echo 'fi' >> $(DEBIAN_DIR)/postrm
	@chmod +x $(DEBIAN_DIR)/postrm
	@# Build the package
	@mkdir -p $(DIST_DIR)
	@fakeroot dpkg-deb --build $(PACKAGE_DIR) $(DIST_DIR)/$(PROJECT_NAME)_$(VERSION)_all.deb
	@echo "$(GREEN).deb package created: $(DIST_DIR)/$(PROJECT_NAME)_$(VERSION)_all.deb$(NC)"

# Build all packages
package: deb
	@echo "$(GREEN)All packages built successfully!$(NC)"
	@ls -la $(DIST_DIR)/

# Install system dependencies
install-deps:
	@echo "$(GREEN)Installing system dependencies...$(NC)"
	@sudo apt-get update
	@sudo apt-get install -f -y  # Fix any broken dependencies first
	@sudo apt-get install -y python3 python3-pip python3-venv python3-dev \
		python3-psutil python3-pyqt5 python3-pil build-essential \
		fakeroot dpkg-dev
	@echo "$(GREEN)System dependencies installed!$(NC)"

# Install .deb package
install-deb: deb install-deps
	@echo "$(GREEN)Installing .deb package...$(NC)"
	@sudo dpkg -i $(DIST_DIR)/$(PROJECT_NAME)_$(VERSION)_all.deb || true
	@sudo apt-get install -f -y  # Fix any dependency issues
	@echo "$(GREEN).deb package installed successfully!$(NC)"

# Uninstall .deb package
uninstall-deb:
	@echo "$(GREEN)Uninstalling .deb package...$(NC)"
	@sudo dpkg -r $(PROJECT_NAME)
	@echo "$(GREEN).deb package uninstalled successfully!$(NC)"

# Show package information
package-info:
	@echo "$(GREEN)Package Information:$(NC)"
	@echo "===================="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Python: $(PYTHON)"
	@echo "Build Dir: $(BUILD_DIR)"
	@echo "Dist Dir: $(DIST_DIR)"
	@echo ""
	@if [ -f "$(DIST_DIR)/$(PROJECT_NAME)_$(VERSION)_all.deb" ]; then \
		echo "$(GREEN)Available packages:$(NC)"; \
		ls -la $(DIST_DIR)/; \
	else \
		echo "$(YELLOW)No packages built yet. Run 'make package' to build.$(NC)"; \
	fi

# Development workflow
dev: dev-setup format lint test
	@echo "$(GREEN)Development workflow complete!$(NC)"

# Release workflow
release: clean setup test package
	@echo "$(GREEN)Release workflow complete!$(NC)"
	@echo "$(GREEN)Package ready for distribution: $(DIST_DIR)/$(PROJECT_NAME)_$(VERSION)_all.deb$(NC)"
