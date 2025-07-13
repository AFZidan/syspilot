"""
Tests for cross-platform functionality
"""

import platform
import unittest
from unittest.mock import MagicMock, patch

from syspilot.platforms import get_platform, is_platform_supported
from syspilot.platforms.factory import PlatformFactory


class TestCrossPlatform(unittest.TestCase):
    """Test cross-platform functionality"""

    def test_platform_detection(self):
        """Test platform detection"""
        detected_platform = get_platform()
        expected_platforms = ["linux", "windows", "macos", "unknown"]
        self.assertIn(detected_platform, expected_platforms)

    def test_platform_support(self):
        """Test platform support detection"""
        is_supported = is_platform_supported()
        self.assertIsInstance(is_supported, bool)

    def test_current_platform_supported(self):
        """Test that current platform support check works"""
        is_supported = PlatformFactory.is_current_platform_supported()
        self.assertIsInstance(is_supported, bool)

    def test_supported_platforms_list(self):
        """Test supported platforms list"""
        platforms = PlatformFactory.get_supported_platforms()
        expected = ["linux", "windows", "macos"]
        self.assertEqual(platforms, expected)

    @patch("syspilot.platforms.factory.get_platform")
    def test_linux_service_creation(self, mock_get_platform):
        """Test Linux service creation"""
        mock_get_platform.return_value = "linux"

        # Test cleanup service
        cleanup_service = PlatformFactory.create_cleanup_service()
        self.assertIsNotNone(cleanup_service)

        # Test monitoring service
        monitoring_service = PlatformFactory.create_monitoring_service()
        self.assertIsNotNone(monitoring_service)

        # Test system info service
        system_info_service = PlatformFactory.create_system_info_service()
        self.assertIsNotNone(system_info_service)

    @patch("syspilot.platforms.factory.get_platform")
    def test_windows_service_creation(self, mock_get_platform):
        """Test Windows service creation"""
        mock_get_platform.return_value = "windows"

        # Test cleanup service
        cleanup_service = PlatformFactory.create_cleanup_service()
        self.assertIsNotNone(cleanup_service)

        # Test monitoring service
        monitoring_service = PlatformFactory.create_monitoring_service()
        self.assertIsNotNone(monitoring_service)

        # Test system info service
        system_info_service = PlatformFactory.create_system_info_service()
        self.assertIsNotNone(system_info_service)

    @patch("syspilot.platforms.factory.get_platform")
    def test_macos_service_creation(self, mock_get_platform):
        """Test macOS service creation"""
        mock_get_platform.return_value = "macos"

        # Test cleanup service
        cleanup_service = PlatformFactory.create_cleanup_service()
        self.assertIsNotNone(cleanup_service)

        # Test monitoring service
        monitoring_service = PlatformFactory.create_monitoring_service()
        self.assertIsNotNone(monitoring_service)

        # Test system info service
        system_info_service = PlatformFactory.create_system_info_service()
        self.assertIsNotNone(system_info_service)

    @patch("syspilot.platforms.factory.get_platform")
    def test_unsupported_platform_error(self, mock_get_platform):
        """Test unsupported platform raises error"""
        mock_get_platform.return_value = "unknown"

        with self.assertRaises(NotImplementedError):
            PlatformFactory.create_cleanup_service()

        with self.assertRaises(NotImplementedError):
            PlatformFactory.create_monitoring_service()

        with self.assertRaises(NotImplementedError):
            PlatformFactory.create_system_info_service()


class TestWindowsPlaceholders(unittest.TestCase):
    """Test Windows placeholder implementations"""

    @patch("syspilot.platforms.factory.get_platform")
    def test_windows_cleanup_placeholder(self, mock_get_platform):
        """Test Windows cleanup service placeholder"""
        mock_get_platform.return_value = "windows"

        cleanup_service = PlatformFactory.create_cleanup_service()

        # Test that methods return placeholder results
        result = cleanup_service.run_cleanup()
        self.assertIn("errors", result)
        self.assertIn("Windows cleanup not yet implemented", result["errors"])

    @patch("syspilot.platforms.factory.get_platform")
    def test_windows_monitoring_placeholder(self, mock_get_platform):
        """Test Windows monitoring service placeholder"""
        mock_get_platform.return_value = "windows"

        monitoring_service = PlatformFactory.create_monitoring_service()

        # Test that temperature monitoring returns None (not implemented)
        temp = monitoring_service.get_cpu_temperature()
        self.assertIsNone(temp)

        # Test that basic monitoring works (using psutil)
        stats = monitoring_service.get_system_stats()
        self.assertIn("platform", stats)
        self.assertEqual(stats["platform"], "windows")


class TestMacOSPlaceholders(unittest.TestCase):
    """Test macOS placeholder implementations"""

    @patch("syspilot.platforms.factory.get_platform")
    def test_macos_cleanup_placeholder(self, mock_get_platform):
        """Test macOS cleanup service placeholder"""
        mock_get_platform.return_value = "macos"

        cleanup_service = PlatformFactory.create_cleanup_service()

        # Test that methods return placeholder results
        result = cleanup_service.run_cleanup()
        self.assertIn("errors", result)
        self.assertIn("macOS cleanup not yet implemented", result["errors"])

    @patch("syspilot.platforms.factory.get_platform")
    def test_macos_monitoring_placeholder(self, mock_get_platform):
        """Test macOS monitoring service placeholder"""
        mock_get_platform.return_value = "macos"

        monitoring_service = PlatformFactory.create_monitoring_service()

        # Test that temperature monitoring returns None (not implemented)
        temp = monitoring_service.get_cpu_temperature()
        self.assertIsNone(temp)

        # Test that basic monitoring works (using psutil)
        stats = monitoring_service.get_system_stats()
        self.assertIn("platform", stats)
        self.assertEqual(stats["platform"], "macos")


if __name__ == "__main__":
    unittest.main()
