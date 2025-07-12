"""
Tests for configuration management
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from syspilot.utils.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager"""

    def test_init_with_default_config(self, temp_dir):
        """Test ConfigManager initialization with default config"""
        config_path = Path(temp_dir) / "config.json"
        config = ConfigManager(str(config_path))

        assert config is not None
        assert config.get("cleanup", "max_age_days") == 30
        assert config.get("monitoring", "update_interval") == 2

    def test_init_with_custom_config(self, temp_dir):
        """Test ConfigManager initialization with custom config"""
        config_path = Path(temp_dir) / "config.json"

        # Create custom config file
        custom_config = {
            "cleanup": {"max_age_days": 7, "min_free_space_mb": 2000},
            "monitoring": {"update_interval": 5},
        }

        with open(config_path, "w") as f:
            json.dump(custom_config, f)

        config = ConfigManager(str(config_path))

        assert config.get("cleanup", "max_age_days") == 7
        assert config.get("cleanup", "min_free_space_mb") == 2000
        assert config.get("monitoring", "update_interval") == 5

    def test_get_method(self, config_manager):
        """Test get method"""
        # Test getting section
        cleanup_config = config_manager.get("cleanup")
        assert isinstance(cleanup_config, dict)
        assert "max_age_days" in cleanup_config

        # Test getting specific key
        max_age = config_manager.get("cleanup", "max_age_days")
        assert max_age == 30

        # Test getting with default
        non_existent = config_manager.get("cleanup", "non_existent", "default")
        assert non_existent == "default"

    def test_set_method(self, config_manager):
        """Test set method"""
        config_manager.set("cleanup", "max_age_days", 15)
        assert config_manager.get("cleanup", "max_age_days") == 15

        # Test setting new section
        config_manager.set("new_section", "new_key", "new_value")
        assert config_manager.get("new_section", "new_key") == "new_value"

    def test_save_config(self, temp_dir):
        """Test saving configuration"""
        config_path = Path(temp_dir) / "config.json"
        config = ConfigManager(str(config_path))

        config.set("cleanup", "max_age_days", 20)
        config.save_config()

        # Verify file was created and contains correct data
        assert config_path.exists()

        with open(config_path, "r") as f:
            saved_config = json.load(f)

        assert saved_config["cleanup"]["max_age_days"] == 20

    def test_get_temp_dirs(self, config_manager):
        """Test get_temp_dirs method"""
        temp_dirs = config_manager.get_temp_dirs()
        assert isinstance(temp_dirs, list)
        assert len(temp_dirs) > 0

    def test_get_cache_dirs(self, config_manager):
        """Test get_cache_dirs method"""
        cache_dirs = config_manager.get_cache_dirs()
        assert isinstance(cache_dirs, list)
        assert len(cache_dirs) > 0

    def test_get_max_age_days(self, config_manager):
        """Test get_max_age_days method"""
        max_age = config_manager.get_max_age_days()
        assert isinstance(max_age, int)
        assert max_age > 0

    def test_get_alert_thresholds(self, config_manager):
        """Test get_alert_thresholds method"""
        thresholds = config_manager.get_alert_thresholds()
        assert isinstance(thresholds, dict)
        assert "cpu_percent" in thresholds
        assert "memory_percent" in thresholds
        assert "disk_percent" in thresholds

    def test_boolean_getters(self, config_manager):
        """Test boolean getter methods"""
        assert isinstance(config_manager.is_debug_mode(), bool)
        assert isinstance(config_manager.should_backup_before_cleanup(), bool)
        assert isinstance(config_manager.should_minimize_to_tray(), bool)
        assert isinstance(config_manager.should_show_notifications(), bool)

    def test_config_validation(self, temp_dir):
        """Test configuration validation"""
        config_path = Path(temp_dir) / "config.json"

        # Create invalid config
        invalid_config = {
            "cleanup": {
                "max_age_days": -5,  # Invalid negative value
                "min_free_space_mb": -1000,
            },
            "monitoring": {
                "update_interval": 0,  # Invalid zero value
                "alert_thresholds": {"cpu_percent": 150},  # Invalid percentage
            },
        }

        with open(config_path, "w") as f:
            json.dump(invalid_config, f)

        config = ConfigManager(str(config_path))

        # Verify invalid values were corrected
        assert config.get("cleanup", "max_age_days") == 30
        assert config.get("cleanup", "min_free_space_mb") == 1000
        assert config.get("monitoring", "update_interval") == 2
        assert config.get("monitoring", "alert_thresholds", {}).get("cpu_percent") == 80

    def test_merge_config(self, temp_dir):
        """Test configuration merging"""
        config_path = Path(temp_dir) / "config.json"

        # Create partial config
        partial_config = {"cleanup": {"max_age_days": 60}}

        with open(config_path, "w") as f:
            json.dump(partial_config, f)

        config = ConfigManager(str(config_path))

        # Verify partial config was merged with defaults
        assert config.get("cleanup", "max_age_days") == 60
        assert config.get("cleanup", "min_free_space_mb") == 1000  # Default value
        assert config.get("monitoring", "update_interval") == 2  # Default value
