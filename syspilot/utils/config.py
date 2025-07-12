"""
Configuration management
"""

import configparser
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import get_logger


class ConfigManager:
    """Configuration manager for SysPilot"""

    DEFAULT_CONFIG = {
        "cleanup": {
            "temp_dirs": [
                "/tmp",
                "/var/tmp",
                "~/.cache",
                "~/.local/share/Trash",
            ],
            "cache_dirs": [
                "~/.cache/thumbnails",
                "~/.cache/mozilla",
                "~/.cache/google-chrome",
                "~/.cache/chromium",
            ],
            "log_files": [
                "/var/log/*.log",
                "~/.xsession-errors*",
            ],
            "package_cache": [
                "/var/cache/apt",
                "/var/cache/debconf",
            ],
            "exclude_patterns": [
                "important*",
                "config*",
                "settings*",
            ],
            "max_age_days": 30,
            "min_free_space_mb": 1000,
        },
        "monitoring": {
            "update_interval": 2,
            "history_size": 100,
            "alert_thresholds": {
                "cpu_percent": 80,
                "memory_percent": 85,
                "disk_percent": 90,
            },
        },
        "ui": {
            "theme": "system",
            "window_geometry": "800x600+100+100",
            "minimize_to_tray": True,
            "show_notifications": True,
        },
        "daemon": {
            "auto_cleanup": False,
            "cleanup_schedule": "0 2 * * *",  # 2 AM daily
            "monitoring_enabled": True,
        },
        "advanced": {
            "debug_mode": False,
            "max_log_size_mb": 10,
            "backup_before_cleanup": True,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)

        # Set config directory and file
        self.config_dir = Path.home() / ".config" / "syspilot"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if config_path:
            self.config_file = Path(config_path)
        else:
            self.config_file = self.config_dir / "config.json"

        # Load configuration
        self._config = self._load_config()

        # Validate configuration
        self._validate_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.logger.info(f"Configuration loaded from {self.config_file}")
                    return self._merge_config(self.DEFAULT_CONFIG, config)
            else:
                self.logger.info("No configuration file found, using defaults")
                return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            return self.DEFAULT_CONFIG.copy()

    def _merge_config(
        self, default: Dict[str, Any], user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge user configuration with defaults"""
        merged = default.copy()

        for key, value in user.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value

        return merged

    def _validate_config(self):
        """Validate configuration values"""
        try:
            # Validate cleanup section
            cleanup = self._config.get("cleanup", {})
            if cleanup.get("max_age_days", 0) < 0:
                cleanup["max_age_days"] = 30

            if cleanup.get("min_free_space_mb", 0) < 0:
                cleanup["min_free_space_mb"] = 1000

            # Validate monitoring section
            monitoring = self._config.get("monitoring", {})
            if monitoring.get("update_interval", 0) < 1:
                monitoring["update_interval"] = 2

            if monitoring.get("history_size", 0) < 10:
                monitoring["history_size"] = 100

            # Validate alert thresholds
            thresholds = monitoring.get("alert_thresholds", {})
            for key in ["cpu_percent", "memory_percent", "disk_percent"]:
                if thresholds.get(key, 0) < 0 or thresholds.get(key, 0) > 100:
                    thresholds[key] = 80

            self.logger.info("Configuration validation completed")
        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            section: Configuration section
            key: Configuration key (optional)
            default: Default value if not found

        Returns:
            Configuration value
        """
        section_config = self._config.get(section, {})

        if key is None:
            return section_config

        return section_config.get(key, default)

    def set(self, section: str, key: str, value: Any):
        """
        Set configuration value

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self._config:
            self._config[section] = {}

        self._config[section][key] = value
        self.logger.debug(f"Configuration updated: {section}.{key} = {value}")

    def get_temp_dirs(self) -> list:
        """Get list of temporary directories to clean"""
        temp_dirs = self.get("cleanup", "temp_dirs", [])
        return [os.path.expanduser(d) for d in temp_dirs]

    def get_cache_dirs(self) -> list:
        """Get list of cache directories to clean"""
        cache_dirs = self.get("cleanup", "cache_dirs", [])
        return [os.path.expanduser(d) for d in cache_dirs]

    def get_log_files(self) -> list:
        """Get list of log files to clean"""
        log_files = self.get("cleanup", "log_files", [])
        return [os.path.expanduser(f) for f in log_files]

    def get_package_cache(self) -> list:
        """Get list of package cache directories to clean"""
        package_cache = self.get("cleanup", "package_cache", [])
        return [os.path.expanduser(d) for d in package_cache]

    def get_exclude_patterns(self) -> list:
        """Get list of exclude patterns"""
        return self.get("cleanup", "exclude_patterns", [])

    def get_max_age_days(self) -> int:
        """Get maximum age for files to be cleaned"""
        return self.get("cleanup", "max_age_days", 30)

    def get_min_free_space_mb(self) -> int:
        """Get minimum free space threshold"""
        return self.get("cleanup", "min_free_space_mb", 1000)

    def get_monitoring_interval(self) -> int:
        """Get monitoring update interval"""
        return self.get("monitoring", "update_interval", 2)

    def get_alert_thresholds(self) -> dict:
        """Get alert thresholds"""
        return self.get("monitoring", "alert_thresholds", {})

    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("advanced", "debug_mode", False)

    def should_backup_before_cleanup(self) -> bool:
        """Check if backup should be created before cleanup"""
        return self.get("advanced", "backup_before_cleanup", True)

    def should_minimize_to_tray(self) -> bool:
        """Check if app should minimize to tray"""
        return self.get("ui", "minimize_to_tray", True)

    def should_show_notifications(self) -> bool:
        """Check if notifications should be shown"""
        return self.get("ui", "show_notifications", True)
