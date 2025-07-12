# SysPilot Cross-Platform Project Structure

## Overview

SysPilot has been reorganized to support multiple operating systems using a platform-specific architecture.

## Project Structure

```
syspilot/
├── core/                    # Core application logic
│   ├── app.py              # Main Qt application
│   └── __init__.py
├── platforms/              # Platform-specific implementations
│   ├── __init__.py         # Platform detection utilities
│   ├── factory.py          # Platform factory for service creation
│   ├── linux/              # Linux-specific implementations (COMPLETE)
│   │   ├── __init__.py
│   │   ├── cleanup_service.py       # Linux cleanup operations
│   │   ├── monitoring_service.py    # Linux system monitoring
│   │   └── system_info_service.py   # Linux system information
│   ├── windows/            # Windows-specific implementations (PLANNED)
│   │   ├── __init__.py
│   │   ├── cleanup_service.py       # Windows cleanup (TODO)
│   │   ├── monitoring_service.py    # Windows monitoring (TODO)
│   │   └── system_info_service.py   # Windows system info (TODO)
│   └── macos/              # macOS-specific implementations (PLANNED)
│       ├── __init__.py
│       ├── cleanup_service.py       # macOS cleanup (TODO)
│       ├── monitoring_service.py    # macOS monitoring (TODO)
│       └── system_info_service.py   # macOS system info (TODO)
├── services/               # Shared/legacy services
│   ├── autostart_service.py        # Auto-start functionality
│   ├── scheduling_service.py       # Cleanup scheduling
│   └── __init__.py
├── utils/                  # Shared utilities
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging utilities
│   └── __init__.py
└── widgets/                # GUI widgets
    ├── charts.py           # Chart widgets (thermometer, pie, etc.)
    └── __init__.py
```

## Platform Support Status

### ✅ Linux (Ubuntu/Debian) - COMPLETE

- Full system cleanup functionality
- Real-time monitoring with CPU temperature
- Interactive charts and thermometer display
- Background operation and system tray
- All features working and tested

### 🚧 Windows - IN PROGRESS (Target: v2.0)

- Basic structure created
- Placeholder implementations with psutil fallbacks
- TODO: Windows-specific APIs (WMI, Performance Counters)
- TODO: Registry cleanup, Windows Services, etc.

### 📋 macOS - PLANNED (Target: v3.0)

- Basic structure created
- Placeholder implementations with psutil fallbacks
- TODO: macOS-specific APIs (IOKit, system_profiler)
- TODO: LaunchAgents, APFS, App Store integration

## Architecture Benefits

1. **Platform Isolation**: Each platform has its own implementation
2. **Factory Pattern**: Automatic platform detection and service creation
3. **Shared Core**: GUI and utilities work across all platforms
4. **Incremental Development**: Can develop one platform at a time
5. **Testability**: Each platform can be tested independently

## Development Workflow

### Adding New Platform Support

1. Create platform directory under `syspilot/platforms/`
2. Implement the three core services:
   - `cleanup_service.py`
   - `monitoring_service.py`
   - `system_info_service.py`
3. Update `platforms/__init__.py` if needed
4. Test with `PlatformFactory.create_*_service()`

### Adding New Features

1. Design the interface in the base/shared location
2. Implement in each platform directory
3. Update the factory if needed
4. Add cross-platform tests

## Testing

Run cross-platform tests:

```bash
# Test platform detection
python -c "from syspilot.platforms import get_platform; print(get_platform())"

# Test service creation
python -c "from syspilot.platforms.factory import PlatformFactory; print(PlatformFactory.create_cleanup_service())"

# Run cross-platform test suite
python -m pytest tests/test_platforms.py -v
```

## Build System

Cross-platform build targets:

```bash
# Linux (current)
make build-linux

# Windows (future)
make build-windows

# macOS (future)
make build-macos
```

## Migration Notes

- The original services have been moved to `platforms/linux/`
- The main app now uses `PlatformFactory` for service creation
- Import paths have been updated for the new structure
- All existing functionality continues to work on Linux
- Windows and macOS have placeholder implementations that will be enhanced
