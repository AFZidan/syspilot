#!/bin/bash

# SysPilot Installation Script
# This script installs SysPilot on Ubuntu and Debian systems

set -e

echo "=================================="
echo "SysPilot Installation Script"
echo "=================================="
echo

# Check if running on Ubuntu or Debian
if ! command -v apt-get &> /dev/null; then
    echo "Error: This script is designed for Ubuntu/Debian systems with apt-get"
    exit 1
fi

# Check if running as root for system packages
if [[ $EUID -eq 0 ]]; then
    echo "Warning: Running as root. This is not recommended."
    echo "Please run as a normal user. The script will ask for sudo when needed."
    exit 1
fi

echo "Checking system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✓ Python 3.8+ found: $(python3 --version)"
else
    echo "✗ Python 3.8+ required. Please install Python 3.8 or higher."
    exit 1
fi

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-tk \
    build-essential \
    libgtk-3-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config \
    gir1.2-gtk-3.0

# Install additional tools
echo "Installing additional tools..."
sudo apt-get install -y \
    curl \
    git \
    htop \
    tree \
    mlocate

# Create application directory
APP_DIR="$HOME/.local/share/syspilot"
echo "Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Copy application files
echo "Copying application files..."
cp -r . "$APP_DIR/"

# Create virtual environment
echo "Creating Python virtual environment..."
cd "$APP_DIR"
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create desktop entry
echo "Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/syspilot.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SysPilot
GenericName=System Cleanup Tool
Comment=Clean temporary files and monitor system performance
Exec=$APP_DIR/venv/bin/python $APP_DIR/main.py
Icon=$APP_DIR/assets/syspilot.png
Terminal=false
StartupNotify=true
Categories=System;Utility;
Keywords=clean;cleanup;system;performance;monitor;
StartupWMClass=SysPilot
EOF

# Create command-line wrapper
echo "Creating command-line wrapper..."
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
WRAPPER_SCRIPT="$BIN_DIR/syspilot"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
cd "$APP_DIR"
source venv/bin/activate
python main.py "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding $HOME/.local/bin to PATH..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    echo "PATH updated in ~/.bashrc"
    
    # Also add to current session
    export PATH="$HOME/.local/bin:$PATH"
    echo "PATH updated for current session"
    
    # Update other shell profiles if they exist
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
        echo "PATH updated in ~/.zshrc"
    fi
    
    if [ -f "$HOME/.profile" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.profile"
        echo "PATH updated in ~/.profile"
    fi
fi

# Create systemd service for daemon mode
echo "Creating systemd user service..."
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"

cat > "$SYSTEMD_DIR/syspilot.service" << EOF
[Unit]
Description=SysPilot Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=$APP_DIR/venv/bin/python $APP_DIR/main.py --daemon
Restart=on-failure
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
EOF

# Reload systemd and enable service
systemctl --user daemon-reload

# Create configuration directory
echo "Creating configuration directory..."
CONFIG_DIR="$HOME/.config/syspilot"
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/logs"

# Set permissions
echo "Setting permissions..."
chmod +x "$APP_DIR/main.py"
chmod +x "$WRAPPER_SCRIPT"

# Create PNG icon from SVG (if available)
if command -v convert &> /dev/null; then
    echo "Creating PNG icon..."
    convert "$APP_DIR/assets/syspilot.svg" -resize 48x48 "$APP_DIR/assets/syspilot.png"
else
    echo "ImageMagick not found. Using SVG icon directly."
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    echo "Updating desktop database..."
    update-desktop-database "$HOME/.local/share/applications/"
fi

echo
echo "=================================="
echo "Installation completed successfully!"
echo "=================================="
echo
echo "You can now run SysPilot in several ways:"
echo "1. GUI mode: syspilot"
echo "2. CLI mode: syspilot --cli"
echo "3. Quick cleanup: syspilot --clean-temp"
echo "4. System info: syspilot --system-info"
echo "5. Daemon mode: syspilot --daemon"
echo "6. From application menu: Search for 'SysPilot'"
echo
echo "If 'syspilot' command is not found, try:"
echo "- Close and reopen your terminal"
echo "- Run: source ~/.bashrc"
echo "- Or run directly: $WRAPPER_SCRIPT"
echo
echo "To enable auto-start: systemctl --user enable syspilot.service"
echo
echo "Configuration files: $CONFIG_DIR"
echo "Application files: $APP_DIR"
echo "To uninstall: $APP_DIR/uninstall.sh"
echo

# Create uninstall script
cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash

echo "Uninstalling SysPilot..."

# Stop daemon if running
systemctl --user stop syspilot.service 2>/dev/null || true
systemctl --user disable syspilot.service 2>/dev/null || true

# Remove files
rm -rf "$HOME/.local/share/syspilot"
rm -f "$HOME/.local/share/applications/syspilot.desktop"
rm -f "$HOME/.local/bin/syspilot"
rm -f "$HOME/.config/systemd/user/syspilot.service"

# Reload systemd
systemctl --user daemon-reload

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications/"
fi

echo "SysPilot has been uninstalled."
echo "Configuration files in $HOME/.config/syspilot have been preserved."
echo "To remove them, run: rm -rf $HOME/.config/syspilot"
EOF

chmod +x "$APP_DIR/uninstall.sh"

echo "Installation script completed!"
echo "You can now start using SysPilot!"
