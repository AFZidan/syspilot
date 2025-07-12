"""
Platform-specific implementations for SysPilot
"""

import os
import platform
from typing import Optional


def get_platform() -> str:
    """
    Get the current platform string

    Returns:
        str: Platform identifier ('linux', 'windows', 'macos')
    """
    system = platform.system().lower()

    if system == "linux":
        return "linux"
    elif system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "unknown"


def get_platform_module(module_name: str):
    """
    Import platform-specific module

    Args:
        module_name: Name of the module to import (e.g., 'cleanup_service')

    Returns:
        The platform-specific module or None if not found
    """
    current_platform = get_platform()

    try:
        if current_platform == "linux":
            from .linux import cleanup_service as linux_cleanup
            from .linux import monitoring_service as linux_monitoring
            from .linux import system_info_service as linux_system_info

            modules = {
                "cleanup_service": linux_cleanup,
                "monitoring_service": linux_monitoring,
                "system_info_service": linux_system_info,
            }

        elif current_platform == "windows":
            from .windows import cleanup_service as windows_cleanup
            from .windows import monitoring_service as windows_monitoring
            from .windows import system_info_service as windows_system_info

            modules = {
                "cleanup_service": windows_cleanup,
                "monitoring_service": windows_monitoring,
                "system_info_service": windows_system_info,
            }

        elif current_platform == "macos":
            from .macos import cleanup_service as macos_cleanup
            from .macos import monitoring_service as macos_monitoring
            from .macos import system_info_service as macos_system_info

            modules = {
                "cleanup_service": macos_cleanup,
                "monitoring_service": macos_monitoring,
                "system_info_service": macos_system_info,
            }
        else:
            return None

        return modules.get(module_name)

    except ImportError:
        return None


def is_platform_supported() -> bool:
    """Check if current platform is supported"""
    return get_platform() in ["linux", "windows", "macos"]
