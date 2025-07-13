"""
System monitoring service
"""

import os
import time
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional

import psutil

from ...utils.config import ConfigManager
from ...utils.logger import get_logger


class MonitoringService:
    """Service for system monitoring and performance tracking"""

    def __init__(self, config: ConfigManager):
        """
        Initialize monitoring service

        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = get_logger(__name__)

        # History storage
        history_size = 100
        if config:
            history_size = config.get("monitoring", "history_size", 100)
        self.history_size = history_size
        self.cpu_history = deque(maxlen=self.history_size)
        self.memory_history = deque(maxlen=self.history_size)
        self.disk_history = deque(maxlen=self.history_size)
        self.network_history = deque(maxlen=self.history_size)

        # Network counters for rate calculation
        self.prev_network_io = None
        self.prev_network_time = None

        # Alert thresholds
        if config:
            self.alert_thresholds = config.get_alert_thresholds()
        else:
            self.alert_thresholds = {"cpu": 80, "memory": 80, "disk": 85}

        self.logger.info("Monitoring service initialized")

    def get_system_stats(self) -> Dict:
        """
        Get current system statistics

        Returns:
            Dictionary with system statistics
        """
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": self._get_cpu_percent(),
                "cpu_temperature": self._get_cpu_temperature(),
                "memory_percent": self._get_memory_percent(),
                "memory_info": self._get_memory_info(),
                "disk_percent": self._get_disk_percent(),
                "disk_info": self._get_disk_info(),
                "network_io": self._get_network_io(),
                "top_processes": self._get_top_processes(),
                "system_load": self._get_system_load(),
                "boot_time": self._get_boot_time(),
                "alerts": self._check_alerts(),
            }

            # Update history
            self._update_history(stats)

            return stats

        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {}

    def _get_cpu_percent(self) -> float:
        """Get CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception as e:
            self.logger.error(f"Error getting CPU percent: {e}")
            return 0.0

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature in Celsius"""
        try:
            # Try to get temperature from psutil sensors
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()

                # Look for common temperature sensor names
                temp_sources = [
                    "coretemp",  # Intel processors
                    "k10temp",  # AMD processors
                    "cpu_thermal",  # ARM processors
                    "acpi",  # ACPI thermal zones
                ]

                for source in temp_sources:
                    if source in temps and temps[source]:
                        # Get the first (usually main) temperature sensor
                        temp_sensor = temps[source][0]
                        if hasattr(temp_sensor, "current"):
                            self.logger.debug(
                                f"CPU temperature from {source}: {temp_sensor.current}°C"
                            )
                            return round(temp_sensor.current, 1)

                # If specific sources not found, try the first available temperature
                for source_name, sensors in temps.items():
                    if sensors and len(sensors) > 0:
                        temp_sensor = sensors[0]
                        if hasattr(temp_sensor, "current"):
                            self.logger.debug(
                                f"CPU temperature from {source_name}: {temp_sensor.current}°C"
                            )
                            return round(temp_sensor.current, 1)

            # Fallback: try to read from /sys/class/thermal directly
            try:
                thermal_zones = [
                    "/sys/class/thermal/thermal_zone0/temp",
                    "/sys/class/thermal/thermal_zone1/temp",
                    "/sys/class/thermal/thermal_zone2/temp",
                ]

                for zone_path in thermal_zones:
                    if os.path.exists(zone_path):
                        with open(zone_path, "r") as f:
                            temp_millidegrees = int(f.read().strip())
                            temp_celsius = temp_millidegrees / 1000.0
                            if 0 < temp_celsius < 150:  # Reasonable temperature range
                                self.logger.debug(
                                    f"CPU temperature from {zone_path}: {temp_celsius}°C"
                                )
                                return round(temp_celsius, 1)
            except (OSError, ValueError, FileNotFoundError):
                pass

            # If all methods fail, return None
            self.logger.debug("CPU temperature not available")
            return None

        except Exception as e:
            self.logger.error(f"Error getting CPU temperature: {e}")
            return None

    def _get_memory_percent(self) -> float:
        """Get memory usage percentage"""
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            self.logger.error(f"Error getting memory percent: {e}")
            return 0.0

    def _get_memory_info(self) -> Dict:
        """Get detailed memory information"""
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "percent": mem.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": swap.percent,
            }
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            return {}

    def _get_disk_percent(self) -> float:
        """Get disk usage percentage for root partition"""
        try:
            return psutil.disk_usage("/").percent
        except Exception as e:
            self.logger.error(f"Error getting disk percent: {e}")
            return 0.0

    def _get_disk_info(self) -> Dict:
        """Get detailed disk information"""
        try:
            disk_usage = psutil.disk_usage("/")
            disk_io = psutil.disk_io_counters()

            info = {
                "total": disk_usage.total,
                "used": disk_usage.used,
                "free": disk_usage.free,
                "percent": disk_usage.percent,
            }

            if disk_io:
                info.update(
                    {
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                    }
                )

            return info
        except Exception as e:
            self.logger.error(f"Error getting disk info: {e}")
            return {}

    def _get_network_io(self) -> Dict:
        """Get network I/O statistics"""
        try:
            current_time = time.time()
            network_io = psutil.net_io_counters()

            if network_io is None:
                return {}

            result = {
                "bytes_sent": network_io.bytes_sent,
                "bytes_recv": network_io.bytes_recv,
                "packets_sent": network_io.packets_sent,
                "packets_recv": network_io.packets_recv,
            }

            # Calculate rates if we have previous data
            if self.prev_network_io and self.prev_network_time:
                time_diff = current_time - self.prev_network_time
                if time_diff > 0:
                    bytes_sent_rate = (
                        (network_io.bytes_sent - self.prev_network_io.bytes_sent)
                        / time_diff
                        / 1024
                    )  # KB/s
                    bytes_recv_rate = (
                        (network_io.bytes_recv - self.prev_network_io.bytes_recv)
                        / time_diff
                        / 1024
                    )  # KB/s

                    result.update(
                        {
                            "bytes_sent_rate": round(bytes_sent_rate, 2),
                            "bytes_recv_rate": round(bytes_recv_rate, 2),
                        }
                    )

            # Update previous values
            self.prev_network_io = network_io
            self.prev_network_time = current_time

            return result

        except Exception as e:
            self.logger.error(f"Error getting network I/O: {e}")
            return {}

    def _get_top_processes(self, limit: int = 10) -> List[Dict]:
        """
        Get top processes by CPU usage

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of process information dictionaries
        """
        try:
            processes = []

            for proc in psutil.process_iter(
                ["pid", "name", "cpu_percent", "memory_percent", "username"]
            ):
                try:
                    proc_info = proc.info
                    if proc_info["cpu_percent"] is not None:
                        processes.append(
                            {
                                "pid": proc_info["pid"],
                                "name": proc_info["name"],
                                "cpu_percent": proc_info["cpu_percent"],
                                "memory_percent": proc_info["memory_percent"],
                                "username": proc_info["username"],
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Sort by CPU usage and return top processes
            processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            return processes[:limit]

        except Exception as e:
            self.logger.error(f"Error getting top processes: {e}")
            return []

    def _get_system_load(self) -> Dict:
        """Get system load averages"""
        try:
            load_avg = psutil.getloadavg()
            cpu_count = psutil.cpu_count()

            return {
                "load_1min": load_avg[0],
                "load_5min": load_avg[1],
                "load_15min": load_avg[2],
                "cpu_count": cpu_count,
                "load_1min_percent": (
                    (load_avg[0] / cpu_count) * 100 if cpu_count > 0 else 0
                ),
                "load_5min_percent": (
                    (load_avg[1] / cpu_count) * 100 if cpu_count > 0 else 0
                ),
                "load_15min_percent": (
                    (load_avg[2] / cpu_count) * 100 if cpu_count > 0 else 0
                ),
            }
        except Exception as e:
            self.logger.error(f"Error getting system load: {e}")
            return {}

    def _get_boot_time(self) -> Dict:
        """Get system boot time information"""
        try:
            boot_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_timestamp)
            current_time = datetime.now()
            uptime = current_time - boot_time

            return {
                "boot_time": boot_time.isoformat(),
                "uptime_seconds": uptime.total_seconds(),
                "uptime_days": uptime.days,
                "uptime_hours": uptime.seconds // 3600,
                "uptime_minutes": (uptime.seconds % 3600) // 60,
            }
        except Exception as e:
            self.logger.error(f"Error getting boot time: {e}")
            return {}

    def _check_alerts(self) -> List[Dict]:
        """Check for system alerts based on thresholds"""
        alerts = []

        try:
            # CPU alert
            cpu_percent = self._get_cpu_percent()
            if cpu_percent > self.alert_thresholds.get("cpu_percent", 80):
                alerts.append(
                    {
                        "type": "cpu",
                        "level": "warning",
                        "message": f"High CPU usage: {cpu_percent:.1f}%",
                        "value": cpu_percent,
                        "threshold": self.alert_thresholds.get("cpu_percent", 80),
                    }
                )

            # Memory alert
            memory_percent = self._get_memory_percent()
            if memory_percent > self.alert_thresholds.get("memory_percent", 85):
                alerts.append(
                    {
                        "type": "memory",
                        "level": "warning",
                        "message": f"High memory usage: {memory_percent:.1f}%",
                        "value": memory_percent,
                        "threshold": self.alert_thresholds.get("memory_percent", 85),
                    }
                )

            # Disk alert
            disk_percent = self._get_disk_percent()
            if disk_percent > self.alert_thresholds.get("disk_percent", 90):
                alerts.append(
                    {
                        "type": "disk",
                        "level": "critical",
                        "message": f"High disk usage: {disk_percent:.1f}%",
                        "value": disk_percent,
                        "threshold": self.alert_thresholds.get("disk_percent", 90),
                    }
                )

            return alerts

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
            return []

    def _update_history(self, stats: Dict):
        """Update historical data"""
        try:
            timestamp = stats.get("timestamp", datetime.now().isoformat())

            self.cpu_history.append(
                {"timestamp": timestamp, "value": stats.get("cpu_percent", 0)}
            )

            self.memory_history.append(
                {"timestamp": timestamp, "value": stats.get("memory_percent", 0)}
            )

            self.disk_history.append(
                {"timestamp": timestamp, "value": stats.get("disk_percent", 0)}
            )

            network_io = stats.get("network_io", {})
            self.network_history.append(
                {
                    "timestamp": timestamp,
                    "bytes_sent": network_io.get("bytes_sent", 0),
                    "bytes_recv": network_io.get("bytes_recv", 0),
                }
            )

        except Exception as e:
            self.logger.error(f"Error updating history: {e}")

    def get_history(self, metric: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get historical data for a specific metric

        Args:
            metric: Metric name (cpu, memory, disk, network)
            limit: Maximum number of entries to return

        Returns:
            List of historical data points
        """
        try:
            history_map = {
                "cpu": self.cpu_history,
                "memory": self.memory_history,
                "disk": self.disk_history,
                "network": self.network_history,
            }

            if metric not in history_map:
                return []

            history = list(history_map[metric])

            if limit:
                history = history[-limit:]

            return history

        except Exception as e:
            self.logger.error(f"Error getting history for {metric}: {e}")
            return []

    def get_process_info(self, pid: int) -> Dict:
        """
        Get detailed information about a specific process

        Args:
            pid: Process ID

        Returns:
            Dictionary with process information
        """
        try:
            proc = psutil.Process(pid)

            return {
                "pid": proc.pid,
                "name": proc.name(),
                "cmdline": proc.cmdline(),
                "cpu_percent": proc.cpu_percent(),
                "memory_percent": proc.memory_percent(),
                "memory_info": proc.memory_info()._asdict(),
                "status": proc.status(),
                "create_time": proc.create_time(),
                "username": proc.username(),
                "num_threads": proc.num_threads(),
                "connections": (
                    len(proc.connections()) if hasattr(proc, "connections") else 0
                ),
            }

        except psutil.NoSuchProcess:
            return {}
        except Exception as e:
            self.logger.error(f"Error getting process info for PID {pid}: {e}")
            return {}

    def get_system_info(self) -> Dict:
        """Get general system information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                "memory_total": psutil.virtual_memory().total,
                "disk_total": psutil.disk_usage("/").total,
                "platform": psutil.LINUX,
                "python_version": psutil.version_info,
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
