#!/bin/bash

# SysPilot Installation Script
# This script installs SysPilot using pipx for proper package management

set -e

echo "SysPilot Installation Script"
echo "==============================="
echo

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root for security reasons."
   echo "Please run as a regular user."
   exit 1
fi

echo "Installing dependencies..."

# Install pipx if not already installed
if ! command -v pipx &> /dev/null; then
    echo "Installing pipx..."
    sudo apt update
    sudo apt install -y pipx
    pipx ensurepath
else
    echo "pipx is already installed"
fi

# Install SysPilot
echo "Installing SysPilot..."
if pipx list | grep -q "syspilot"; then
    echo "SysPilot is already installed. Reinstalling..."
    pipx reinstall syspilot
else
    pipx install .
fi

# Add pipx bin directory to PATH
echo "Configuring PATH..."
pipx ensurepath

# Add to shell configuration files
for shell_config in ~/.bashrc ~/.zshrc ~/.profile; do
    if [ -f "$shell_config" ]; then
        if ! grep -q "export PATH.*\.local/bin" "$shell_config"; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"
            echo "Added PATH to $shell_config"
        fi
    fi
done

echo
echo "Installation completed successfully! ✨"
echo
echo "To use SysPilot, run one of the following commands:"
echo "  syspilot           # Launch GUI mode"
echo "  syspilot --cli     # Launch CLI mode"
echo "  syspilot --daemon  # Run as background daemon"
echo "  syspilot --help    # Show all options"
echo
echo "Note: You may need to restart your terminal or run:"
echo "  source ~/.bashrc"
echo "  # or"
echo "  source ~/.zshrc"
echo "to make the 'syspilot' command available in your current session."
echo
echo "Test the installation by running: syspilot --help"
