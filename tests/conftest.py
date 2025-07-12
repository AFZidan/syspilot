"""
Test configuration for pytest
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Add the project root to Python path
project_root = Path(__file__).parent.parent
import sys

sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def config_manager():
    """Create a ConfigManager instance for testing"""
    from syspilot.utils.config import ConfigManager

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_path = f.name

    try:
        config = ConfigManager(config_path)
        yield config
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


@pytest.fixture
def sample_files(temp_dir):
    """Create sample files for testing"""
    files = []

    # Create some temporary files
    for i in range(5):
        file_path = Path(temp_dir) / f"temp_file_{i}.txt"
        file_path.write_text(f"Test content {i}")
        files.append(str(file_path))

    # Create some cache files
    cache_dir = Path(temp_dir) / "cache"
    cache_dir.mkdir()

    for i in range(3):
        file_path = cache_dir / f"cache_file_{i}.cache"
        file_path.write_text(f"Cache content {i}")
        files.append(str(file_path))

    return files
