"""
Tests for cleanup service
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from syspilot.services.cleanup_service import CleanupService


class TestCleanupService:
    """Test cases for CleanupService"""
    
    def test_init(self, config_manager):
        """Test CleanupService initialization"""
        service = CleanupService(config_manager)
        assert service is not None
        assert service.config == config_manager
    
    def test_format_bytes(self, config_manager):
        """Test _format_bytes method"""
        service = CleanupService(config_manager)
        
        assert service._format_bytes(0) == "0.00 B"
        assert service._format_bytes(1024) == "1.00 KB"
        assert service._format_bytes(1048576) == "1.00 MB"
        assert service._format_bytes(1073741824) == "1.00 GB"
    
    def test_should_exclude(self, config_manager):
        """Test _should_exclude method"""
        service = CleanupService(config_manager)
        
        exclude_patterns = ['important', 'config', 'settings']
        
        assert service._should_exclude('important_file.txt', exclude_patterns) is True
        assert service._should_exclude('config.json', exclude_patterns) is True
        assert service._should_exclude('settings.ini', exclude_patterns) is True
        assert service._should_exclude('regular_file.txt', exclude_patterns) is False
    
    def test_is_file_old(self, config_manager, temp_dir):
        """Test _is_file_old method"""
        service = CleanupService(config_manager)
        
        # Create a test file
        test_file = Path(temp_dir) / "test_file.txt"
        test_file.write_text("test content")
        
        # Test with 0 days (should return True)
        assert service._is_file_old(str(test_file), 0) is True
        
        # Test with very high number of days (should return False)
        assert service._is_file_old(str(test_file), 365) is False
        
        # Test with non-existent file
        assert service._is_file_old("/non/existent/file", 30) is False
    
    def test_is_directory_empty(self, config_manager, temp_dir):
        """Test _is_directory_empty method"""
        service = CleanupService(config_manager)
        
        # Create empty directory
        empty_dir = Path(temp_dir) / "empty"
        empty_dir.mkdir()
        
        # Create non-empty directory
        non_empty_dir = Path(temp_dir) / "non_empty"
        non_empty_dir.mkdir()
        (non_empty_dir / "file.txt").write_text("content")
        
        assert service._is_directory_empty(str(empty_dir)) is True
        assert service._is_directory_empty(str(non_empty_dir)) is False
        assert service._is_directory_empty("/non/existent/dir") is False
    
    def test_remove_file(self, config_manager, temp_dir):
        """Test _remove_file method"""
        service = CleanupService(config_manager)
        
        # Create test file
        test_file = Path(temp_dir) / "test_file.txt"
        test_file.write_text("test content")
        
        initial_files_cleaned = service.stats['files_cleaned']
        initial_space_freed = service.stats['space_freed']
        
        service._remove_file(str(test_file))
        
        assert not test_file.exists()
        assert service.stats['files_cleaned'] == initial_files_cleaned + 1
        assert service.stats['space_freed'] > initial_space_freed
    
    def test_remove_directory(self, config_manager, temp_dir):
        """Test _remove_directory method"""
        service = CleanupService(config_manager)
        
        # Create test directory
        test_dir = Path(temp_dir) / "test_dir"
        test_dir.mkdir()
        
        initial_dirs_cleaned = service.stats['directories_cleaned']
        
        service._remove_directory(str(test_dir))
        
        assert not test_dir.exists()
        assert service.stats['directories_cleaned'] == initial_dirs_cleaned + 1
    
    def test_get_files_to_clean(self, config_manager, temp_dir):
        """Test _get_files_to_clean method"""
        service = CleanupService(config_manager)
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = Path(temp_dir) / f"test_file_{i}.txt"
            file_path.write_text(f"test content {i}")
            test_files.append(str(file_path))
        
        # Create a file that should be excluded
        excluded_file = Path(temp_dir) / "important_file.txt"
        excluded_file.write_text("important content")
        
        files_to_clean = service._get_files_to_clean(temp_dir, 0, ['important'])
        
        assert len(files_to_clean) == 3
        assert str(excluded_file) not in files_to_clean
        
        for test_file in test_files:
            assert test_file in files_to_clean
    
    def test_clean_directory(self, config_manager, temp_dir):
        """Test _clean_directory method"""
        service = CleanupService(config_manager)
        
        # Create test structure
        sub_dir = Path(temp_dir) / "subdir"
        sub_dir.mkdir()
        
        # Create files
        file1 = Path(temp_dir) / "file1.txt"
        file1.write_text("content1")
        
        file2 = sub_dir / "file2.txt"
        file2.write_text("content2")
        
        # Create excluded file
        excluded_file = Path(temp_dir) / "important.txt"
        excluded_file.write_text("important content")
        
        initial_stats = service.stats.copy()
        
        service._clean_directory(temp_dir, 0, ['important'])
        
        # Check that non-excluded files were cleaned
        assert not file1.exists()
        assert not file2.exists()
        assert excluded_file.exists()  # Should still exist
        
        # Check stats were updated
        assert service.stats['files_cleaned'] > initial_stats['files_cleaned']
        assert service.stats['space_freed'] > initial_stats['space_freed']
    
    def test_get_cleanup_preview(self, config_manager):
        """Test get_cleanup_preview method"""
        service = CleanupService(config_manager)
        
        # Mock the config to return test directories
        with patch.object(service.config, 'get_temp_dirs', return_value=['/tmp']):
            with patch.object(service.config, 'get_cache_dirs', return_value=[]):
                with patch.object(service.config, 'get_max_age_days', return_value=30):
                    with patch.object(service.config, 'get_exclude_patterns', return_value=[]):
                        with patch.object(service, '_get_files_to_clean', return_value=['/tmp/file1.txt']):
                            with patch('os.path.exists', return_value=True):
                                with patch('os.path.getsize', return_value=1024):
                                    preview = service.get_cleanup_preview()
                                    
                                    assert isinstance(preview, dict)
                                    assert 'temp_files' in preview
                                    assert 'cache_files' in preview
                                    assert 'estimated_space' in preview
    
    @patch('subprocess.run')
    def test_clean_package_cache(self, mock_run, config_manager):
        """Test _clean_package_cache method"""
        service = CleanupService(config_manager)
        
        # Mock successful subprocess calls
        mock_run.return_value.returncode = 0
        
        service._clean_package_cache()
        
        # Verify subprocess calls were made
        assert mock_run.call_count == 3  # clean, autoremove, autoclean
    
    @patch('subprocess.run')
    def test_clean_package_cache_error(self, mock_run, config_manager):
        """Test _clean_package_cache method with error"""
        service = CleanupService(config_manager)
        
        # Mock failed subprocess call
        mock_run.side_effect = Exception("Command failed")
        
        # Should not raise exception
        service._clean_package_cache()
    
    def test_full_cleanup_with_callbacks(self, config_manager):
        """Test full_cleanup method with callbacks"""
        service = CleanupService(config_manager)
        
        progress_calls = []
        status_calls = []
        
        def progress_callback(progress):
            progress_calls.append(progress)
        
        def status_callback(status):
            status_calls.append(status)
        
        # Mock all cleanup methods to avoid actual file operations
        with patch.object(service, '_clean_temp_files'):
            with patch.object(service, '_clean_cache_files'):
                with patch.object(service, '_clean_log_files'):
                    with patch.object(service, '_clean_package_cache'):
                        with patch.object(service, '_clean_trash'):
                            with patch.object(service, '_clean_browser_cache'):
                                with patch.object(service, '_clean_system_cache'):
                                    with patch.object(service, '_update_package_database'):
                                        result = service.full_cleanup(
                                            progress_callback=progress_callback,
                                            status_callback=status_callback
                                        )
                                        
                                        assert isinstance(result, dict)
                                        assert 'temp_files_cleaned' in result
                                        assert 'space_freed' in result
                                        assert 'time_taken' in result
                                        assert len(progress_calls) > 0
                                        assert len(status_calls) > 0
    
    def test_full_cleanup_error_handling(self, config_manager):
        """Test full_cleanup method error handling"""
        service = CleanupService(config_manager)
        
        # Mock one method to raise an exception
        with patch.object(service, '_clean_temp_files', side_effect=Exception("Test error")):
            with patch.object(service, '_clean_cache_files'):
                with patch.object(service, '_clean_log_files'):
                    with patch.object(service, '_clean_package_cache'):
                        with patch.object(service, '_clean_trash'):
                            with patch.object(service, '_clean_browser_cache'):
                                with patch.object(service, '_clean_system_cache'):
                                    with patch.object(service, '_update_package_database'):
                                        result = service.full_cleanup()
                                        
                                        assert isinstance(result, dict)
                                        assert len(result['errors']) > 0
                                        assert 'Test error' in result['errors'][0]
