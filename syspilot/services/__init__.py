"""
Service modules
"""

from .cleanup_service import CleanupService
from .monitoring_service import MonitoringService
from .system_info import SystemInfoService

# Optional services that require additional dependencies
try:
    from .autostart_service import AutoStartService

    __all_autostart = ["AutoStartService"]
except ImportError:
    __all_autostart = []

try:
    from .scheduling_service import SchedulingService

    __all_scheduling = ["SchedulingService"]
except ImportError:
    __all_scheduling = []

__all__ = (
    [
        "CleanupService",
        "MonitoringService",
        "SystemInfoService",
    ]
    + __all_autostart
    + __all_scheduling
)
