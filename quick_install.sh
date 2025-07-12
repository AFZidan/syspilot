#!/bin/bash

echo "SysPilot - Quick Installation Fix"
echo "==================================="
echo

# Get the current directory
CURRENT_DIR="$(pwd)"
APP_DIR="$HOME/.local/share/syspilot"

echo "Current directory: $CURRENT_DIR"
echo "Target app directory: $APP_DIR"
echo

# Create necessary directories
echo "Creating directories..."
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/syspilot"
mkdir -p "$HOME/.config/syspilot"

# Copy application files
echo "Copying application files..."
cp -r "$CURRENT_DIR"/* "$APP_DIR/"

# Create virtual environment
echo "Creating virtual environment..."
cd "$APP_DIR"
python3 -m venv venv

# Install requirements if pip is available
if command -v pip &> /dev/null || python3 -m pip --version &> /dev/null; then
    echo "Installing Python dependencies..."
    source venv/bin/activate
    
    # Try to install requirements
    if [ -f requirements.txt ]; then
        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt || echo "Warning: Some dependencies failed to install"
    fi
    
    deactivate
else
    echo "Warning: pip not available, skipping Python dependencies"
fi

# Create wrapper script
echo "Creating command wrapper..."
WRAPPER_SCRIPT="$HOME/.local/bin/syspilot"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
# SysPilot wrapper script

APP_DIR="$HOME/.local/share/syspilot"
cd "\$APP_DIR"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
    python main.py "\$@"
else
    # Fallback to system Python
    echo "Warning: Virtual environment not found, using system Python"
    python3 main.py "\$@"
fi
EOF

chmod +x "$WRAPPER_SCRIPT"

# Add to PATH
echo "Updating PATH..."
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    # Add to multiple shell configs
    for config_file in ~/.bashrc ~/.zshrc ~/.profile; do
        if [ -f "$config_file" ]; then
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$config_file"
            echo "Updated $config_file"
        fi
    done
    
    # Update current session
    export PATH="$HOME/.local/bin:$PATH"
    echo "PATH updated for current session"
fi

# Create desktop entry
echo "Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/syspilot.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SysPilot
GenericName=System Cleanup Tool
Comment=Clean temporary files and monitor system performance
Exec=$WRAPPER_SCRIPT
Icon=$APP_DIR/assets/syspilot.png
Terminal=false
StartupNotify=true
Categories=System;Utility;
Keywords=clean;cleanup;system;performance;monitor;
EOF

# Make main.py executable
chmod +x "$APP_DIR/main.py"

echo
echo "================================="
echo "Installation Complete!"
echo "================================="
echo
echo "Testing installation..."

# Test the command
if command -v syspilot &> /dev/null; then
    echo "✓ syspilot command is available"
    echo "Testing: syspilot --help"
    if syspilot --help 2>/dev/null | head -3; then
        echo "✓ SysPilot is working!"
    else
        echo "! Command runs but may have dependency issues"
    fi
else
    echo "! syspilot command not found in PATH"
    echo "  You can run directly: $WRAPPER_SCRIPT"
    echo "  Or restart your terminal"
fi

echo
echo "Usage:"
echo "  syspilot           # GUI mode"
echo "  syspilot --cli     # CLI mode"
echo "  syspilot --help    # Show help"
echo
echo "If command not found, try:"
echo "  source ~/.bashrc      # Reload bash config"
echo "  $WRAPPER_SCRIPT       # Run directly"
echo
