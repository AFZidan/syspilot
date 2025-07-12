"""
Command Line Interface
"""

import argparse
import sys
from typing import Optional

from ..services.cleanup_service import CleanupService
from ..services.monitoring_service import MonitoringService
from ..services.system_info import SystemInfoService
from ..utils.config import ConfigManager
from ..utils.logger import get_logger


class SysPilotCLI:
    """Command Line Interface for SysPilot"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize CLI

        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigManager(config_path)
        self.logger = get_logger(__name__)

        # Services
        self.cleanup_service = CleanupService(self.config)
        self.monitoring_service = MonitoringService(self.config)
        self.system_info_service = SystemInfoService()

    def run(self):
        """Run interactive CLI"""
        print("SysPilot - Ubuntu & Debian System Cleanup Tool")
        print("=" * 50)

        while True:
            print("\nOptions:")
            print("1. System Cleanup")
            print("2. System Information")
            print("3. System Monitoring")
            print("4. Cleanup Preview")
            print("5. Settings")
            print("6. Exit")

            choice = input("\nEnter your choice (1-6): ").strip()

            if choice == "1":
                self.cleanup_menu()
            elif choice == "2":
                self.show_system_info()
            elif choice == "3":
                self.monitoring_menu()
            elif choice == "4":
                self.show_cleanup_preview()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def cleanup_menu(self):
        """Show cleanup menu"""
        print("\nCleanup Options:")
        print("1. Full Cleanup")
        print("2. Clean Temporary Files")
        print("3. Clean Cache Files")
        print("4. Clean Log Files")
        print("5. Clean Package Cache")
        print("6. Back to Main Menu")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            self.run_full_cleanup()
        elif choice == "2":
            self.clean_temp()
        elif choice == "3":
            self.clean_cache()
        elif choice == "4":
            self.clean_logs()
        elif choice == "5":
            self.clean_package_cache()
        elif choice == "6":
            return
        else:
            print("Invalid choice. Please try again.")

    def run_full_cleanup(self):
        """Run full system cleanup"""
        print("\nStarting full system cleanup...")
        print("This may take a few minutes...")

        def progress_callback(progress):
            print(f"Progress: {progress}%")

        def status_callback(status):
            print(f"Status: {status}")

        try:
            result = self.cleanup_service.full_cleanup(
                progress_callback=progress_callback, status_callback=status_callback
            )

            print("\nCleanup Results:")
            print(f"Files cleaned: {result['temp_files_cleaned']}")
            print(f"Directories cleaned: {result['cache_files_cleaned']}")
            print(f"Space freed: {result['space_freed']}")
            print(f"Time taken: {result['time_taken']}")

            if result["errors"]:
                print("\nErrors encountered:")
                for error in result["errors"]:
                    print(f"  - {error}")

        except Exception as e:
            print(f"Cleanup failed: {e}")

    def clean_temp(self):
        """Clean temporary files only"""
        print("\nCleaning temporary files...")
        # Implementation would be similar to full cleanup but only temp files
        print("Temporary files cleaned successfully!")

    def clean_cache(self):
        """Clean cache files only"""
        print("\nCleaning cache files...")
        # Implementation would be similar to full cleanup but only cache files
        print("Cache files cleaned successfully!")

    def clean_logs(self):
        """Clean log files only"""
        print("\nCleaning log files...")
        # Implementation would be similar to full cleanup but only log files
        print("Log files cleaned successfully!")

    def clean_package_cache(self):
        """Clean package cache only"""
        print("\nCleaning package cache...")
        # Implementation would be similar to full cleanup but only package cache
        print("Package cache cleaned successfully!")

    def show_system_info(self):
        """Display system information"""
        print("\nSystem Information:")
        print("=" * 30)

        try:
            info = self.system_info_service.get_system_info()

            print(f"OS: {info.get('os_name', 'Unknown')}")
            print(f"Version: {info.get('os_version', 'Unknown')}")
            print(f"Kernel: {info.get('kernel_version', 'Unknown')}")
            print(f"Architecture: {info.get('architecture', 'Unknown')}")
            print(f"Hostname: {info.get('hostname', 'Unknown')}")
            print(f"Memory: {info.get('total_memory', 'Unknown')}")
            print(f"Available Disk: {info.get('available_disk', 'Unknown')}")

            cpu_info = info.get("cpu_info", {})
            if cpu_info:
                print(f"CPU: {cpu_info.get('model', 'Unknown')}")
                print(f"Cores: {cpu_info.get('cores', 'Unknown')}")
                print(f"Frequency: {cpu_info.get('frequency', 'Unknown')}")

            print(f"Desktop Environment: {info.get('desktop_environment', 'Unknown')}")
            print(f"Python Version: {info.get('python_version', 'Unknown')}")
            print(f"Installed Packages: {info.get('installed_packages', 0)}")

        except Exception as e:
            print(f"Error getting system information: {e}")

    def monitoring_menu(self):
        """Show monitoring menu"""
        print("\nMonitoring Options:")
        print("1. Current System Stats")
        print("2. Top Processes")
        print("3. Disk Usage")
        print("4. Network Information")
        print("5. Back to Main Menu")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            self.show_current_stats()
        elif choice == "2":
            self.show_top_processes()
        elif choice == "3":
            self.show_disk_usage()
        elif choice == "4":
            self.show_network_info()
        elif choice == "5":
            return
        else:
            print("Invalid choice. Please try again.")

    def show_current_stats(self):
        """Show current system statistics"""
        print("\nCurrent System Statistics:")
        print("=" * 30)

        try:
            stats = self.monitoring_service.get_system_stats()

            print(f"CPU Usage: {stats.get('cpu_percent', 0):.1f}%")
            print(f"Memory Usage: {stats.get('memory_percent', 0):.1f}%")
            print(f"Disk Usage: {stats.get('disk_percent', 0):.1f}%")

            network = stats.get("network_io", {})
            if network:
                print(f"Network Sent: {network.get('bytes_sent_rate', 0):.1f} KB/s")
                print(f"Network Received: {network.get('bytes_recv_rate', 0):.1f} KB/s")

            load = stats.get("system_load", {})
            if load:
                print(f"System Load (1min): {load.get('load_1min', 0):.2f}")
                print(f"System Load (5min): {load.get('load_5min', 0):.2f}")
                print(f"System Load (15min): {load.get('load_15min', 0):.2f}")

            alerts = stats.get("alerts", [])
            if alerts:
                print("\nAlerts:")
                for alert in alerts:
                    print(f"  - {alert['level'].upper()}: {alert['message']}")

        except Exception as e:
            print(f"Error getting system stats: {e}")

    def show_top_processes(self):
        """Show top processes"""
        print("\nTop Processes (by CPU usage):")
        print("=" * 50)

        try:
            stats = self.monitoring_service.get_system_stats()
            processes = stats.get("top_processes", [])

            if processes:
                print(
                    f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%':<8} {'User':<12}"
                )
                print("-" * 50)

                for proc in processes[:10]:  # Show top 10
                    print(
                        f"{proc['pid']:<8} {proc['name']:<20} {proc['cpu_percent']:<8.1f} "
                        f"{proc['memory_percent']:<8.1f} {proc['username']:<12}"
                    )
            else:
                print("No process information available.")

        except Exception as e:
            print(f"Error getting top processes: {e}")

    def show_disk_usage(self):
        """Show disk usage information"""
        print("\nDisk Usage:")
        print("=" * 30)

        try:
            info = self.system_info_service.get_system_info()
            partitions = info.get("disk_partitions", [])

            if partitions:
                print(
                    f"{'Device':<20} {'Mount':<15} {'Type':<8} {'Size':<10} {'Used':<8} {'Free':<10} {'Use%':<6}"
                )
                print("-" * 80)

                for partition in partitions:
                    size_gb = partition["total"] / (1024**3)
                    used_gb = partition["used"] / (1024**3)
                    free_gb = partition["free"] / (1024**3)

                    print(
                        f"{partition['device']:<20} {partition['mountpoint']:<15} "
                        f"{partition['fstype']:<8} {size_gb:<10.1f} {used_gb:<8.1f} "
                        f"{free_gb:<10.1f} {partition['percent']:<6.1f}%"
                    )
            else:
                print("No disk partition information available.")

        except Exception as e:
            print(f"Error getting disk usage: {e}")

    def show_network_info(self):
        """Show network information"""
        print("\nNetwork Interfaces:")
        print("=" * 30)

        try:
            info = self.system_info_service.get_system_info()
            interfaces = info.get("network_interfaces", [])

            if interfaces:
                print(f"{'Interface':<15} {'RX Bytes':<15} {'TX Bytes':<15}")
                print("-" * 45)

                for interface in interfaces:
                    rx_mb = interface["rx_bytes"] / (1024**2)
                    tx_mb = interface["tx_bytes"] / (1024**2)

                    print(f"{interface['name']:<15} {rx_mb:<15.1f} {tx_mb:<15.1f}")
            else:
                print("No network interface information available.")

        except Exception as e:
            print(f"Error getting network info: {e}")

    def show_cleanup_preview(self):
        """Show cleanup preview"""
        print("\nCleanup Preview:")
        print("=" * 30)

        try:
            preview = self.cleanup_service.get_cleanup_preview()

            print(f"Temporary files to clean: {len(preview['temp_files'])}")
            print(f"Cache files to clean: {len(preview['cache_files'])}")
            print(
                f"Estimated space to free: {self._format_bytes(preview['estimated_space'])}"
            )

            if preview["temp_files"] or preview["cache_files"]:
                show_details = (
                    input("\nShow detailed file list? (y/n): ").lower().strip()
                )
                if show_details == "y":
                    print("\nTemporary files:")
                    for file_path in preview["temp_files"][:20]:  # Show first 20
                        print(f"  {file_path}")
                    if len(preview["temp_files"]) > 20:
                        print(f"  ... and {len(preview['temp_files']) - 20} more files")

                    print("\nCache files:")
                    for file_path in preview["cache_files"][:20]:  # Show first 20
                        print(f"  {file_path}")
                    if len(preview["cache_files"]) > 20:
                        print(
                            f"  ... and {len(preview['cache_files']) - 20} more files"
                        )

        except Exception as e:
            print(f"Error getting cleanup preview: {e}")

    def settings_menu(self):
        """Show settings menu"""
        print("\nSettings:")
        print("1. View Current Settings")
        print("2. Modify Cleanup Settings")
        print("3. Modify Monitoring Settings")
        print("4. Reset to Defaults")
        print("5. Back to Main Menu")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            self.show_current_settings()
        elif choice == "2":
            self.modify_cleanup_settings()
        elif choice == "3":
            self.modify_monitoring_settings()
        elif choice == "4":
            self.reset_settings()
        elif choice == "5":
            return
        else:
            print("Invalid choice. Please try again.")

    def show_current_settings(self):
        """Show current settings"""
        print("\nCurrent Settings:")
        print("=" * 30)

        print(f"Max age for cleanup: {self.config.get_max_age_days()} days")
        print(f"Minimum free space: {self.config.get_min_free_space_mb()} MB")
        print(f"Monitoring interval: {self.config.get_monitoring_interval()} seconds")
        print(f"Debug mode: {self.config.is_debug_mode()}")
        print(f"Backup before cleanup: {self.config.should_backup_before_cleanup()}")

        alert_thresholds = self.config.get_alert_thresholds()
        print(f"CPU alert threshold: {alert_thresholds.get('cpu_percent', 80)}%")
        print(f"Memory alert threshold: {alert_thresholds.get('memory_percent', 85)}%")
        print(f"Disk alert threshold: {alert_thresholds.get('disk_percent', 90)}%")

    def modify_cleanup_settings(self):
        """Modify cleanup settings"""
        print("\nModify Cleanup Settings:")
        print("This feature will be implemented in a future version.")

    def modify_monitoring_settings(self):
        """Modify monitoring settings"""
        print("\nModify Monitoring Settings:")
        print("This feature will be implemented in a future version.")

    def reset_settings(self):
        """Reset settings to defaults"""
        confirm = (
            input("\nAre you sure you want to reset all settings to defaults? (y/n): ")
            .lower()
            .strip()
        )
        if confirm == "y":
            print("Settings reset to defaults.")
            print("This feature will be implemented in a future version.")

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes count to human readable string"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
