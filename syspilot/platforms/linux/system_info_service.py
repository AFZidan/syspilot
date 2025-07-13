"""
System information service
"""

import os
import platform
import shutil
import subprocess
from typing import Dict, List

from ...utils.logger import get_logger


class SystemInfoService:
    """Service for gathering system information"""

    def __init__(self):
        """Initialize system info service"""
        self.logger = get_logger(__name__)

    def get_system_info(self) -> Dict:
        """
        Get comprehensive system information

        Returns:
            Dictionary with system information
        """
        try:
            info = {
                "os_name": self._get_os_name(),
                "os_version": self._get_os_version(),
                "kernel_version": self._get_kernel_version(),
                "architecture": self._get_architecture(),
                "hostname": self._get_hostname(),
                "total_memory": self._get_total_memory(),
                "available_disk": self._get_available_disk(),
                "cpu_info": self._get_cpu_info(),
                "desktop_environment": self._get_desktop_environment(),
                "python_version": self._get_python_version(),
                "installed_packages": self._get_package_count(),
                "disk_partitions": self._get_disk_partitions(),
                "network_interfaces": self._get_network_interfaces(),
                "graphics_info": self._get_graphics_info(),
                "system_services": self._get_system_services_count(),
            }

            return info

        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}

    def _get_os_name(self) -> str:
        """Get operating system name"""
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip('"')
            return platform.system()
        except Exception:
            return platform.system()

    def _get_os_version(self) -> str:
        """Get operating system version"""
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("VERSION="):
                        return line.split("=")[1].strip('"')
            return platform.release()
        except Exception:
            return platform.release()

    def _get_kernel_version(self) -> str:
        """Get kernel version"""
        try:
            return platform.release()
        except Exception:
            return "Unknown"

    def _get_architecture(self) -> str:
        """Get system architecture"""
        try:
            return platform.machine()
        except Exception:
            return "Unknown"

    def _get_hostname(self) -> str:
        """Get system hostname"""
        try:
            return platform.node()
        except Exception:
            return "Unknown"

    def _get_total_memory(self) -> str:
        """Get total system memory"""
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        mem_kb = int(line.split()[1])
                        mem_gb = mem_kb / (1024 * 1024)
                        return f"{mem_gb:.2f} GB"
            return "Unknown"
        except Exception:
            return "Unknown"

    def _get_available_disk(self) -> str:
        """Get available disk space"""
        try:
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024 * 1024 * 1024)
            return f"{free_gb:.2f} GB"
        except Exception:
            return "Unknown"

    def _get_cpu_info(self) -> Dict:
        """Get CPU information"""
        try:
            cpu_info = {}

            # Get CPU model name
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        cpu_info["model"] = line.split(":")[1].strip()
                        break

            # Get CPU count
            cpu_info["cores"] = os.cpu_count()

            # Get CPU frequency
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("cpu MHz"):
                            cpu_info["frequency"] = (
                                f"{float(line.split(':')[1].strip()):.0f} MHz"
                            )
                            break
            except Exception:
                pass

            return cpu_info

        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            return {}

    def _get_desktop_environment(self) -> str:
        """Get desktop environment"""
        try:
            # Check common desktop environment variables
            desktop_env = os.environ.get("XDG_CURRENT_DESKTOP", "")
            if desktop_env:
                return desktop_env

            desktop_env = os.environ.get("DESKTOP_SESSION", "")
            if desktop_env:
                return desktop_env

            # Check for specific desktop environments
            if os.environ.get("GNOME_DESKTOP_SESSION_ID"):
                return "GNOME"
            elif os.environ.get("KDE_FULL_SESSION"):
                return "KDE"
            elif os.environ.get("XFCE4_SESSION"):
                return "XFCE"

            return "Unknown"

        except Exception:
            return "Unknown"

    def _get_python_version(self) -> str:
        """Get Python version"""
        try:
            return platform.python_version()
        except Exception:
            return "Unknown"

    def _get_package_count(self) -> int:
        """Get number of installed packages"""
        try:
            # Count APT packages
            result = subprocess.run(
                ["dpkg", "--get-selections"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return len(result.stdout.strip().split("\n"))
            return 0
        except Exception:
            return 0

    def _get_disk_partitions(self) -> List[Dict]:
        """Get disk partition information"""
        try:
            partitions = []

            # Read from /proc/mounts
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        device, mountpoint, fstype = parts[0], parts[1], parts[2]

                        # Filter out non-disk filesystems
                        if fstype in [
                            "ext4",
                            "ext3",
                            "ext2",
                            "btrfs",
                            "xfs",
                            "ntfs",
                            "fat32",
                            "vfat",
                        ]:
                            try:
                                total, used, free = shutil.disk_usage(mountpoint)
                                partitions.append(
                                    {
                                        "device": device,
                                        "mountpoint": mountpoint,
                                        "fstype": fstype,
                                        "total": total,
                                        "used": used,
                                        "free": free,
                                        "percent": (
                                            (used / total) * 100 if total > 0 else 0
                                        ),
                                    }
                                )
                            except Exception:
                                pass

            return partitions

        except Exception as e:
            self.logger.error(f"Error getting disk partitions: {e}")
            return []

    def _get_network_interfaces(self) -> List[Dict]:
        """Get network interface information"""
        try:
            interfaces = []

            # Read from /proc/net/dev
            with open("/proc/net/dev", "r") as f:
                lines = f.readlines()[2:]  # Skip header lines

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 10:
                        interface = parts[0].rstrip(":")
                        rx_bytes = int(parts[1])
                        tx_bytes = int(parts[9])

                        interfaces.append(
                            {
                                "name": interface,
                                "rx_bytes": rx_bytes,
                                "tx_bytes": tx_bytes,
                            }
                        )

            return interfaces

        except Exception as e:
            self.logger.error(f"Error getting network interfaces: {e}")
            return []

    def _get_graphics_info(self) -> Dict:
        """Get graphics card information"""
        try:
            graphics_info = {}

            # Try to get GPU info using lspci
            try:
                result = subprocess.run(["lspci", "-v"], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "VGA compatible controller" in line:
                            graphics_info["gpu"] = (
                                line.split(": ")[1] if ": " in line else line
                            )
                            break
            except Exception:
                pass

            # Try to get display info
            try:
                display = os.environ.get("DISPLAY", "")
                if display:
                    graphics_info["display"] = display
            except Exception:
                pass

            return graphics_info

        except Exception as e:
            self.logger.error(f"Error getting graphics info: {e}")
            return {}

    def _get_system_services_count(self) -> int:
        """Get number of system services"""
        try:
            # Count systemd services
            result = subprocess.run(
                ["systemctl", "list-units", "--type=service"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                # Filter out header and footer lines
                service_lines = [line for line in lines if ".service" in line]
                return len(service_lines)
            return 0
        except Exception:
            return 0

    def get_disk_usage_by_directory(self, directory: str = "/") -> List[Dict]:
        """
        Get disk usage by directory

        Args:
            directory: Directory to analyze

        Returns:
            List of directories with their sizes
        """
        try:
            directories = []

            # Use du command to get directory sizes
            result = subprocess.run(
                ["du", "-h", "--max-depth=1", directory], capture_output=True, text=True
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "\t" in line:
                        size, path = line.split("\t")
                        directories.append({"path": path, "size": size})

            return directories

        except Exception as e:
            self.logger.error(f"Error getting disk usage by directory: {e}")
            return []

    def get_largest_files(self, directory: str = "/", limit: int = 10) -> List[Dict]:
        """
        Get largest files in a directory

        Args:
            directory: Directory to search
            limit: Maximum number of files to return

        Returns:
            List of largest files
        """
        try:
            files = []

            # Use find command to get largest files
            result = subprocess.run(
                ["find", directory, "-type", "f", "-exec", "ls", "-la", "{}", "+"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                file_info = []

                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 9:
                            size = int(parts[4])
                            filename = " ".join(parts[8:])
                            file_info.append(
                                {
                                    "filename": filename,
                                    "size": size,
                                    "size_human": self._format_bytes(size),
                                }
                            )

                # Sort by size and return top files
                file_info.sort(key=lambda x: x["size"], reverse=True)
                files = file_info[:limit]

            return files

        except Exception as e:
            self.logger.error(f"Error getting largest files: {e}")
            return []

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes count to human readable string"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"
