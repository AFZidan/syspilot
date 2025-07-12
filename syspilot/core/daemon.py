"""
Background daemon service
"""

import os
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Optional

import schedule

from ..services.cleanup_service import CleanupService
from ..services.monitoring_service import MonitoringService
from ..services.scheduling_service import SchedulingService
from ..utils.config import ConfigManager
from ..utils.logger import get_logger


class SysPilotDaemon:
    """Background daemon for SysPilot"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize daemon

        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigManager(config_path)
        self.logger = get_logger(__name__)

        # Services
        self.cleanup_service = CleanupService(self.config)
        self.monitoring_service = MonitoringService(self.config)
        self.scheduling_service = SchedulingService(self.config, self.cleanup_service)

        # Daemon state
        self.is_running = False
        self.monitoring_thread = None
        self.scheduler_thread = None

        # PID file
        self.pid_file = Path.home() / ".config" / "syspilot" / "daemon.pid"

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def run(self):
        """Run the daemon"""
        try:
            self.logger.info("Starting SysPilot daemon")

            # Check if daemon is already running
            if self._is_daemon_running():
                self.logger.error("Daemon is already running")
                return

            # Create PID file
            self._create_pid_file()

            # Start daemon
            self.is_running = True

            # Schedule cleanup tasks
            self._schedule_cleanup_tasks()

            # Start scheduling service
            self.scheduling_service.start_scheduler()

            # Start monitoring thread
            if self.config.get("daemon", "monitoring_enabled", True):
                self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
                self.monitoring_thread.daemon = True
                self.monitoring_thread.start()

            # Start scheduler thread
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()

            self.logger.info("SysPilot daemon started successfully")

            # Main daemon loop
            while self.is_running:
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"Daemon error: {e}")
            raise
        finally:
            self._cleanup_daemon()

    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping SysPilot daemon")
        self.is_running = False

        # Stop scheduling service
        self.scheduling_service.stop_scheduler()

        # Wait for threads to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)

        self._cleanup_daemon()
        self.logger.info("SysPilot daemon stopped")

    def _is_daemon_running(self) -> bool:
        """Check if daemon is already running"""
        try:
            if not self.pid_file.exists():
                return False

            with open(self.pid_file, "r") as f:
                pid = int(f.read().strip())

            # Check if process is still running
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                # Process not running, remove stale PID file
                self.pid_file.unlink()
                return False

        except Exception:
            return False

    def _create_pid_file(self):
        """Create PID file"""
        try:
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file, "w") as f:
                f.write(str(os.getpid()))
        except Exception as e:
            self.logger.error(f"Error creating PID file: {e}")
            raise

    def _cleanup_daemon(self):
        """Cleanup daemon resources"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            self.logger.error(f"Error cleaning up daemon: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down")
        self.stop()

    def _schedule_cleanup_tasks(self):
        """Schedule automatic cleanup tasks"""
        try:
            if self.config.get("daemon", "auto_cleanup", False):
                cleanup_schedule = self.config.get(
                    "daemon", "cleanup_schedule", "0 2 * * *"
                )

                # Parse cron-like schedule (simplified)
                if cleanup_schedule == "0 2 * * *":  # Daily at 2 AM
                    schedule.every().day.at("02:00").do(self._scheduled_cleanup)
                elif cleanup_schedule == "0 2 * * 0":  # Weekly on Sunday at 2 AM
                    schedule.every().sunday.at("02:00").do(self._scheduled_cleanup)
                else:
                    # Default to daily
                    schedule.every().day.at("02:00").do(self._scheduled_cleanup)

                self.logger.info(f"Scheduled cleanup: {cleanup_schedule}")

        except Exception as e:
            self.logger.error(f"Error scheduling cleanup tasks: {e}")

    def _scheduled_cleanup(self):
        """Run scheduled cleanup"""
        try:
            self.logger.info("Running scheduled cleanup")

            result = self.cleanup_service.full_cleanup()

            self.logger.info(f"Scheduled cleanup completed: {result}")

        except Exception as e:
            self.logger.error(f"Scheduled cleanup failed: {e}")

    def _monitoring_loop(self):
        """Monitoring loop"""
        try:
            self.logger.info("Starting monitoring loop")

            while self.is_running:
                try:
                    # Get system stats
                    stats = self.monitoring_service.get_system_stats()

                    # Check for alerts
                    alerts = stats.get("alerts", [])
                    for alert in alerts:
                        self.logger.warning(f"System alert: {alert['message']}")

                        # Could send notifications here
                        self._send_alert_notification(alert)

                    # Sleep for monitoring interval
                    time.sleep(self.config.get_monitoring_interval())

                except Exception as e:
                    self.logger.error(f"Monitoring loop error: {e}")
                    time.sleep(10)  # Wait before retrying

        except Exception as e:
            self.logger.error(f"Monitoring loop failed: {e}")

    def _scheduler_loop(self):
        """Scheduler loop"""
        try:
            self.logger.info("Starting scheduler loop")

            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute

                except Exception as e:
                    self.logger.error(f"Scheduler loop error: {e}")
                    time.sleep(60)

        except Exception as e:
            self.logger.error(f"Scheduler loop failed: {e}")

    def _send_alert_notification(self, alert: dict):
        """Send alert notification"""
        try:
            # Could implement desktop notifications here
            # For now, just log
            self.logger.info(f"Alert notification: {alert['message']}")

        except Exception as e:
            self.logger.error(f"Error sending alert notification: {e}")

    def get_daemon_status(self) -> dict:
        """Get daemon status"""
        try:
            status = {
                "running": self.is_running,
                "pid": os.getpid() if self.is_running else None,
                "monitoring_enabled": self.config.get(
                    "daemon", "monitoring_enabled", True
                ),
                "auto_cleanup_enabled": self.config.get(
                    "daemon", "auto_cleanup", False
                ),
                "cleanup_schedule": self.config.get(
                    "daemon", "cleanup_schedule", "0 2 * * *"
                ),
                "uptime": None,  # Could track uptime
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting daemon status: {e}")
            return {}

    @staticmethod
    def is_running():
        """Check if daemon is running (static method)"""
        pid_file = Path.home() / ".config" / "syspilot" / "daemon.pid"

        try:
            if not pid_file.exists():
                return False

            with open(pid_file, "r") as f:
                pid = int(f.read().strip())

            # Check if process is still running
            try:
                os.kill(pid, 0)
                return True
            except OSError:
                return False

        except Exception:
            return False

    @staticmethod
    def stop_daemon():
        """Stop running daemon (static method)"""
        pid_file = Path.home() / ".config" / "syspilot" / "daemon.pid"

        try:
            if not pid_file.exists():
                return False

            with open(pid_file, "r") as f:
                pid = int(f.read().strip())

            # Send SIGTERM to daemon
            try:
                os.kill(pid, signal.SIGTERM)
                return True
            except OSError:
                return False

        except Exception:
            return False
