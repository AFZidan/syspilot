"""
Platform Factory for SysPilot
Automatically loads platform-specific service implementations
"""

from syspilot.platforms import get_platform, is_platform_supported


class PlatformFactory:
    """Factory for creating platform-specific service instances"""

    @staticmethod
    def create_cleanup_service(config=None):
        """Create platform-specific cleanup service"""
        platform = get_platform()

        if platform == "linux":
            from syspilot.platforms.linux.cleanup_service import CleanupService

            return CleanupService(config)
        elif platform == "windows":
            from syspilot.platforms.windows.cleanup_service import CleanupService

            return CleanupService(config)
        elif platform == "macos":
            from syspilot.platforms.macos.cleanup_service import CleanupService

            return CleanupService(config)
        else:
            raise NotImplementedError(f"Platform '{platform}' is not supported")

    @staticmethod
    def create_monitoring_service(config=None):
        """Create platform-specific monitoring service"""
        platform = get_platform()

        if platform == "linux":
            from syspilot.platforms.linux.monitoring_service import MonitoringService

            return MonitoringService(config)
        elif platform == "windows":
            from syspilot.platforms.windows.monitoring_service import MonitoringService

            return MonitoringService(config)
        elif platform == "macos":
            from syspilot.platforms.macos.monitoring_service import MonitoringService

            return MonitoringService(config)
        else:
            raise NotImplementedError(f"Platform '{platform}' is not supported")

    @staticmethod
    def create_system_info_service():
        """Create platform-specific system info service"""
        platform = get_platform()

        if platform == "linux":
            from syspilot.platforms.linux.system_info_service import SystemInfoService

            return SystemInfoService()
        elif platform == "windows":
            from syspilot.platforms.windows.system_info_service import SystemInfoService

            return SystemInfoService()
        elif platform == "macos":
            from syspilot.platforms.macos.system_info_service import SystemInfoService

            return SystemInfoService()
        else:
            raise NotImplementedError(f"Platform '{platform}' is not supported")

    @staticmethod
    def get_supported_platforms():
        """Get list of supported platforms"""
        return ["linux", "windows", "macos"]

    @staticmethod
    def is_current_platform_supported():
        """Check if current platform is supported"""
        return is_platform_supported()
