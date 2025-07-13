# SysPilot

<div align="center">

![SysPilot Logo](assets/syspilot_banner.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)](https://github.com/AFZidan/syspilot)
[![CI/CD](https://github.com/AFZidan/syspilot/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/AFZidan/syspilot/actions)
[![Quality Gate Status](https://img.shields.io/badge/Quality%20Gate-passing-brightgreen.svg)](https://github.com/AFZidan/syspilot/actions)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-green.svg)](https://codecov.io/gh/AFZidan/syspilot)
[![GitHub release](https://img.shields.io/github/release/AFZidan/syspilot.svg)](https://github.com/AFZidan/syspilot/releases)
[![GitHub issues](https://img.shields.io/github/issues/AFZidan/syspilot.svg)](https://github.com/AFZidan/syspilot/issues)
[![GitHub stars](https://img.shields.io/github/stars/AFZidan/syspilot.svg)](https://github.com/AFZidan/syspilot/stargazers)
[![Downloads](https://img.shields.io/github/downloads/AFZidan/syspilot/total.svg)](https://github.com/AFZidan/syspilot/releases)

## A powerful, cross-platform system cleanup and performance monitoring tool

[📥 Download](https://github.com/AFZidan/syspilot/releases) • [📖 Documentation](https://github.com/AFZidan/syspilot/wiki) • [🐛 Report Issues](https://github.com/AFZidan/syspilot/issues) • [💬 Discussions](https://github.com/AFZidan/syspilot/discussions)

</div>

---

## Overview

SysPilot is a modern system utility that helps keep your computer clean and running efficiently. It provides real-time system monitoring, automated cleanup, and intuitive visualization through both GUI and CLI interfaces.

## Key Features

- **System Cleanup** - Remove temporary files, cache, and free up disk space
- **Real-time Monitoring** - Track CPU, memory, disk usage with interactive charts
- **Temperature Monitoring** - Monitor CPU temperature with visual indicators
- **Background Operation** - System tray integration and scheduled tasks
- **Cross-Platform Ready** - Linux (complete), Windows & macOS (in development)

## Platform Support

| Platform | Status | Features |
|----------|--------|----------|
| Linux | ✅ Ready | Full cleanup, monitoring, GUI |
| Windows | 🚧 In Progress | Basic structure, planned features |
| macOS | 📋 Planned | Architecture ready |

## Quick Start

### Installation

**Recommended method (using pipx):**

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
chmod +x install_pipx.sh
./install_pipx.sh
```

**Alternative method:**

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
chmod +x install.sh
./install.sh
```

### Usage

```bash
# Launch GUI
syspilot

# CLI mode
syspilot --cli

# Background service
syspilot --daemon
```

## Requirements

- Python 3.8 or higher
- Linux (Ubuntu 18.04+, Debian 10+)
- Required system packages (auto-installed)

## Development

### Setup Environment

```bash
git clone https://github.com/AFZidan/syspilot.git
cd syspilot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Running Tests

```bash
python -m pytest
python -m pytest --cov=syspilot --cov-report=html
```

### Code Quality

```bash
black syspilot/
flake8 syspilot/
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass
5. Submit a pull request

## Roadmap

- **v1.x** - ✅ Linux support (Complete)
- **v2.x** - 🚧 Windows support (In Progress)
- **v3.x** - 📋 macOS support (Planned)

## Project Structure

```text
syspilot/
├── core/                    # Core Qt application
├── platforms/              # Platform-specific implementations
│   ├── linux/              # ✅ Linux support (complete)
│   ├── windows/            # 🚧 Windows support (in progress)
│   └── macos/              # 📋 macOS support (planned)
├── services/               # Shared services
├── utils/                  # Configuration & utilities
└── widgets/                # GUI components & charts
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support & Links

- [📥 Download](https://github.com/AFZidan/syspilot/releases)
- [🐛 Issues](https://github.com/AFZidan/syspilot/issues)
- [💬 Discussions](https://github.com/AFZidan/syspilot/discussions)
- [📖 Wiki](https://github.com/AFZidan/syspilot/wiki)
- [📝 Changelog](CHANGELOG.md)
