"""
AutoStart Service for SysPilot
Handles enabling/disabling auto-start functionality
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional


class AutoStartService:
    """Service to manage auto-start functionality"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.desktop_file_path = (
            Path.home() / ".config" / "autostart" / "syspilot.desktop"
        )
        self.systemd_service_path = (
            Path.home() / ".config" / "systemd" / "user" / "syspilot.service"
        )

    def is_autostart_enabled(self) -> bool:
        """Check if auto-start is enabled"""
        return self.desktop_file_path.exists() or self.systemd_service_path.exists()

    def enable_autostart(self, method: str = "desktop") -> bool:
        """
        Enable auto-start

        Args:
            method: "desktop" for desktop entry, "systemd" for systemd service

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if method == "desktop":
                return self._enable_desktop_autostart()
            elif method == "systemd":
                return self._enable_systemd_autostart()
            else:
                self.logger.error(f"Unknown auto-start method: {method}")
                return False
        except Exception as e:
            self.logger.error(f"Error enabling auto-start: {e}")
            return False

    def disable_autostart(self) -> bool:
        """Disable auto-start"""
        try:
            success = True

            # Remove desktop entry
            if self.desktop_file_path.exists():
                self.desktop_file_path.unlink()
                self.logger.info("Removed desktop auto-start entry")

            # Remove systemd service
            if self.systemd_service_path.exists():
                # Stop and disable service first
                subprocess.run(
                    ["systemctl", "--user", "stop", "syspilot.service"],
                    capture_output=True,
                    check=False,
                )
                subprocess.run(
                    ["systemctl", "--user", "disable", "syspilot.service"],
                    capture_output=True,
                    check=False,
                )

                self.systemd_service_path.unlink()
                self.logger.info("Removed systemd auto-start service")

            return success

        except Exception as e:
            self.logger.error(f"Error disabling auto-start: {e}")
            return False

    def _enable_desktop_autostart(self) -> bool:
        """Enable auto-start using desktop entry"""
        try:
            # Create autostart directory if it doesn't exist
            self.desktop_file_path.parent.mkdir(parents=True, exist_ok=True)

            # Get the syspilot command path
            syspilot_path = self._get_syspilot_path()
            if not syspilot_path:
                self.logger.error("Could not find syspilot command")
                return False

            # Create desktop entry content
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=SysPilot
GenericName=System Cleanup Tool
Comment=Clean temporary files and monitor system performance
Exec={syspilot_path} --daemon
Icon=syspilot
Terminal=false
StartupNotify=false
Categories=System;Utility;
Keywords=clean;cleanup;system;performance;monitor;
Hidden=false
X-GNOME-Autostart-enabled=true
"""

            # Write desktop entry
            with open(self.desktop_file_path, "w") as f:
                f.write(desktop_content)

            # Make it executable
            self.desktop_file_path.chmod(0o755)

            self.logger.info(
                f"Created desktop auto-start entry: {self.desktop_file_path}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error creating desktop auto-start entry: {e}")
            return False

    def _enable_systemd_autostart(self) -> bool:
        """Enable auto-start using systemd service"""
        try:
            # Create systemd user directory if it doesn't exist
            self.systemd_service_path.parent.mkdir(parents=True, exist_ok=True)

            # Get the syspilot command path
            syspilot_path = self._get_syspilot_path()
            if not syspilot_path:
                self.logger.error("Could not find syspilot command")
                return False

            # Create systemd service content
            service_content = f"""[Unit]
Description=SysPilot System Cleanup Tool
After=graphical-session.target

[Service]
Type=simple
ExecStart={syspilot_path} --daemon
Restart=on-failure
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
"""

            # Write systemd service
            with open(self.systemd_service_path, "w") as f:
                f.write(service_content)

            # Reload systemd and enable service
            subprocess.run(
                ["systemctl", "--user", "daemon-reload"],
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["systemctl", "--user", "enable", "syspilot.service"],
                capture_output=True,
                check=True,
            )

            self.logger.info(
                f"Created systemd auto-start service: {self.systemd_service_path}"
            )
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error creating systemd service: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating systemd auto-start service: {e}")
            return False

    def _get_syspilot_path(self) -> Optional[str]:
        """Get the path to syspilot command"""
        try:
            # Try to find syspilot in PATH
            result = subprocess.run(
                ["which", "syspilot"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            # Try common locations
            common_paths = [
                Path.home() / ".local" / "bin" / "syspilot",
                Path("/usr/local/bin/syspilot"),
                Path("/usr/bin/syspilot"),
            ]

            for path in common_paths:
                if path.exists() and os.access(path, os.X_OK):
                    return str(path)

            return None

    def get_autostart_status(self) -> dict:
        """Get detailed auto-start status"""
        return {
            "enabled": self.is_autostart_enabled(),
            "desktop_entry": self.desktop_file_path.exists(),
            "systemd_service": self.systemd_service_path.exists(),
            "desktop_path": str(self.desktop_file_path),
            "systemd_path": str(self.systemd_service_path),
        }
