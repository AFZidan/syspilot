# SysPilot - Cross-Platform System Automation & Cleanup Tool

![SysPilot Logo](assets/syspilot_banner.png)

A powerful, open-source desktop application for Linux, Windows, and macOS that helps keep your system clean and monitors performance.

## Platform Support

🐧 **Linux (Ubuntu/Debian)** - ✅ **Fully Implemented**

- Complete system cleanup functionality
- Real-time monitoring with CPU temperature
- Interactive charts and graphs
- Background operation and system tray

🪟 **Windows** - 🚧 **Coming Soon** (Planned for v2.0)

- Windows-specific cleanup operations
- Performance monitoring
- Registry cleanup
- Service management

🍎 **macOS** - 🚧 **Coming Soon** (Planned for v3.0)

- macOS-specific cleanup operations
- System monitoring
- Application cleanup
- Privacy file management

## Features

🧹 **System Cleanup**

- Clean temporary files and directories
- Remove unnecessary cache files
- Free up disk space efficiently
- Background cleaning operations
- Scheduled automatic cleanup

📊 **System Monitoring**

- Real-time system performance indicators
- CPU, Memory, and Disk usage monitoring
- Top 3 resource-consuming processes
- System health dashboard
- Interactive charts and graphs (pie charts, line charts, gauges)
- Historical trend analysis

🚀 **Background Operation**

- Runs silently in the background
- System tray icon for easy access
- Non-intrusive notifications
- Scheduled cleanup tasks
- Auto-start capability

⚙️ **Advanced Features**

- Auto-start on system boot
- Customizable cleanup schedules
- Multiple monitoring views
- Configuration management
- Enhanced graphical interface

## Quick Start with Makefile

For developers and advanced users, we provide a comprehensive Makefile:

```bash
# Set up development environment
make setup

# Run tests
make test

# Build .deb package
make deb

# Install the .deb package
make install-deb

# See all available commands
make help
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Ubuntu 18.04+ or Debian 10+
- Required system packages (automatically installed)

### Recommended Installation (using pipx)

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
chmod +x install_pipx.sh
./install_pipx.sh
```

This method uses `pipx` to install SysPilot in an isolated environment, which is the recommended approach for Python applications.

### Alternative Installation (legacy)

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
chmod +x install.sh
./install.sh
```

### Manual Installation

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv python3-tk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install desktop entry
sudo python3 setup.py install
```

## Usage

### GUI Mode

```bash
syspilot
```

### CLI Mode

```bash
syspilot --cli
syspilot --clean-temp
syspilot --system-info
```

### Background Service

```bash
syspilot --daemon
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=syspilot --cov-report=html

# Run specific test file
python -m pytest tests/test_cleanup.py
```

### Code Quality

```bash
# Format code
black syspilot/
isort syspilot/

# Lint code
flake8 syspilot/
pylint syspilot/
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure tests pass and coverage is maintained
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/AFZidan/syspilot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AFZidan/syspilot/discussions)
- **Wiki**: [Project Wiki](https://github.com/AFZidan/syspilot/wiki)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Acknowledgments

- Thanks to all contributors
- Built with Python and Tkinter
- Uses system monitoring libraries
- Inspired by system maintenance tools

## 🗺️ Roadmap & TODO List

### Phase 1: Linux Foundation (✅ COMPLETED)

- [x] ✅ System cleanup service (temp files, cache, logs)
- [x] ✅ Real-time system monitoring (CPU, Memory, Disk, Network)
- [x] ✅ CPU temperature monitoring with sensors support
- [x] ✅ Interactive charts and visualization widgets
- [x] ✅ Thermometer-style CPU temperature display
- [x] ✅ System tray integration and background operation
- [x] ✅ Qt-based GUI with multiple monitoring views
- [x] ✅ Cross-platform project structure setup
- [x] ✅ Platform factory pattern implementation

### Phase 2: Windows Support (🚧 IN PROGRESS - Target: v2.0)

#### Core Windows Implementation

- [ ] 🔄 Windows-specific cleanup operations
  - [ ] Windows Temp folder (%TEMP%, %TMP%) cleanup
  - [ ] Windows Update cache cleanup
  - [ ] Recycle Bin management
  - [ ] Windows Store cache cleanup
  - [ ] Browser cache cleanup (Edge, Chrome, Firefox)
  - [ ] System file cleanup (prefetch, logs)

- [ ] 🔄 Windows Performance Monitoring
  - [ ] WMI (Windows Management Instrumentation) integration
  - [ ] Performance Counters for CPU, Memory, Disk
  - [ ] Windows-specific temperature monitoring
  - [ ] Process monitoring and management
  - [ ] Windows Services monitoring

- [ ] 🔄 Windows-Specific Features
  - [ ] Registry cleanup and optimization
  - [ ] Windows Services management
  - [ ] Startup programs management
  - [ ] Windows Defender integration
  - [ ] Event Log management

#### Windows GUI & Integration

- [ ] 🔄 Windows native look and feel
- [ ] 🔄 Windows system tray integration
- [ ] 🔄 Windows notifications
- [ ] 🔄 Windows auto-start integration
- [ ] 🔄 Windows installer (MSI/NSIS)

### Phase 3: macOS Support (📋 PLANNED - Target: v3.0)

#### Core macOS Implementation

- [ ] 📋 macOS-specific cleanup operations
  - [ ] ~/Library/Caches cleanup
  - [ ] ~/Library/Logs cleanup
  - [ ] Trash management
  - [ ] Application support files cleanup
  - [ ] Downloads folder organization
  - [ ] macOS system cache cleanup

- [ ] 📋 macOS Performance Monitoring
  - [ ] IOKit framework integration for hardware info
  - [ ] Activity Monitor style process information
  - [ ] macOS-specific temperature monitoring
  - [ ] Memory pressure monitoring
  - [ ] Disk usage with APFS specifics

- [ ] 📋 macOS-Specific Features
  - [ ] LaunchAgents/LaunchDaemons management
  - [ ] Spotlight cache management
  - [ ] Application uninstallation
  - [ ] Privacy file management
  - [ ] Time Machine exclusions

#### macOS GUI & Integration

- [ ] 📋 macOS native look and feel (Cocoa styling)
- [ ] 📋 Menu bar integration
- [ ] 📋 macOS notifications
- [ ] 📋 Login items integration
- [ ] 📋 macOS app bundle (.app) distribution
- [ ] 📋 Mac App Store compatibility

### Phase 4: Enhanced Cross-Platform Features (📋 FUTURE)

#### Advanced Monitoring

- [ ] 📋 Historical data persistence and analysis
- [ ] 📋 Performance benchmarking
- [ ] 📋 System health scoring
- [ ] 📋 Predictive maintenance alerts
- [ ] 📋 Custom monitoring thresholds

#### Smart Cleanup Features

- [ ] 📋 Machine learning-based cleanup recommendations
- [ ] 📋 Duplicate file detection and removal
- [ ] 📋 Large file analysis and management
- [ ] 📋 Automated cleanup scheduling with AI
- [ ] 📋 Cloud storage integration for backups

#### Advanced GUI Features

- [ ] 📋 Dark/Light theme support
- [ ] 📋 Customizable dashboard layouts
- [ ] 📋 Plugin architecture for extensions
- [ ] 📋 Multi-language internationalization
- [ ] 📋 Accessibility improvements

#### Enterprise Features

- [ ] 📋 Multi-system management dashboard
- [ ] 📋 Network deployment capabilities
- [ ] 📋 Centralized configuration management
- [ ] 📋 Reporting and analytics
- [ ] 📋 Policy-based cleanup rules

### Phase 5: Cloud & Connectivity (📋 FUTURE)

- [ ] 📋 Cloud backup integration
- [ ] 📋 Remote monitoring capabilities
- [ ] 📋 Telemetry and usage analytics
- [ ] 📋 Automatic updates system
- [ ] 📋 Community cleanup rule sharing

## 🎯 Current Focus

**Currently Working On:** Linux platform completion and Windows foundation
**Next Milestone:** Windows v2.0 release with full Windows support
**Long-term Goal:** Universal cross-platform system utility

## 📈 Progress Tracking

- **Linux Support:** 100% Complete ✅
- **Windows Support:** 15% Complete (Structure + Basic Services) 🚧
- **macOS Support:** 10% Complete (Structure Only) 📋
- **Cross-Platform Architecture:** 80% Complete ✅

## 📁 Project Structure

SysPilot now features a **cross-platform architecture** designed for Linux, Windows, and macOS support:

```
syspilot/
├── core/                    # Core Qt application
├── platforms/              # Platform-specific implementations
│   ├── linux/              # ✅ Linux support (complete)
│   ├── windows/            # 🚧 Windows support (planned v2.0)
│   └── macos/              # 📋 macOS support (planned v3.0)
├── services/               # Shared services
├── utils/                  # Configuration & utilities
└── widgets/                # GUI components & charts
```

---
