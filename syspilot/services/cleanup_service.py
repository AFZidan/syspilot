"""
System cleanup service
"""

import glob
import os
import shutil
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

from ..utils.config import ConfigManager
from ..utils.logger import get_logger


class CleanupService:
    """Service for system cleanup operations"""

    def __init__(self, config: ConfigManager):
        """
        Initialize cleanup service

        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.stats = {
            "files_cleaned": 0,
            "directories_cleaned": 0,
            "space_freed": 0,
            "errors": [],
        }

    def full_cleanup(
        self,
        progress_callback: Optional[Callable[[int], None]] = None,
        status_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        """
        Perform full system cleanup

        Args:
            progress_callback: Progress update callback
            status_callback: Status update callback

        Returns:
            Dictionary with cleanup results
        """
        start_time = time.time()
        self.stats = {
            "files_cleaned": 0,
            "directories_cleaned": 0,
            "space_freed": 0,
            "errors": [],
        }

        try:
            self.logger.info("Starting full system cleanup")

            # Define cleanup tasks
            cleanup_tasks = [
                ("Cleaning temporary files", self._clean_temp_files),
                ("Cleaning cache files", self._clean_cache_files),
                ("Cleaning log files", self._clean_log_files),
                ("Cleaning package cache", self._clean_package_cache),
                ("Cleaning trash", self._clean_trash),
                ("Cleaning browser cache", self._clean_browser_cache),
                ("Cleaning system cache", self._clean_system_cache),
            ]

            total_tasks = len(cleanup_tasks)

            for i, (task_name, task_func) in enumerate(cleanup_tasks):
                if status_callback:
                    status_callback(task_name)

                self.logger.info(f"Executing task: {task_name}")

                try:
                    task_func()
                except Exception as e:
                    error_msg = f"Error in {task_name}: {str(e)}"
                    self.logger.error(error_msg)
                    self.stats["errors"].append(error_msg)

                # Update progress
                if progress_callback:
                    progress = int((i + 1) / total_tasks * 100)
                    progress_callback(progress)

            # Final cleanup tasks
            if status_callback:
                status_callback("Finalizing cleanup")

            self._update_package_database()

            # Calculate results
            end_time = time.time()
            time_taken = end_time - start_time

            results = {
                "temp_files_cleaned": self.stats["files_cleaned"],
                "cache_files_cleaned": self.stats["directories_cleaned"],
                "space_freed": self._format_bytes(self.stats["space_freed"]),
                "time_taken": f"{time_taken:.2f} seconds",
                "errors": self.stats["errors"],
            }

            self.logger.info(f"Cleanup completed in {time_taken:.2f} seconds")
            self.logger.info(f"Files cleaned: {self.stats['files_cleaned']}")
            self.logger.info(
                f"Space freed: {self._format_bytes(self.stats['space_freed'])}"
            )

            return results

        except Exception as e:
            self.logger.error(f"Full cleanup failed: {e}")
            raise

    def _clean_temp_files(self):
        """Clean temporary files"""
        temp_dirs = self.config.get_temp_dirs()
        max_age_days = self.config.get_max_age_days()
        exclude_patterns = self.config.get_exclude_patterns()

        for temp_dir in temp_dirs:
            if not os.path.exists(temp_dir):
                continue

            self.logger.debug(f"Cleaning temp directory: {temp_dir}")
            self._clean_directory(temp_dir, max_age_days, exclude_patterns)

    def _clean_cache_files(self):
        """Clean cache files"""
        cache_dirs = self.config.get_cache_dirs()
        max_age_days = self.config.get_max_age_days()
        exclude_patterns = self.config.get_exclude_patterns()

        for cache_dir in cache_dirs:
            if not os.path.exists(cache_dir):
                continue

            self.logger.debug(f"Cleaning cache directory: {cache_dir}")
            self._clean_directory(cache_dir, max_age_days, exclude_patterns)

    def _clean_log_files(self):
        """Clean log files"""
        log_patterns = self.config.get_log_files()
        max_age_days = self.config.get_max_age_days()

        for pattern in log_patterns:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if self._is_file_old(file_path, max_age_days):
                        self._remove_file(file_path)
            except Exception as e:
                self.logger.error(
                    f"Error cleaning log files with pattern {pattern}: {e}"
                )

    def _clean_package_cache(self):
        """Clean package cache"""
        try:
            # Clean apt cache
            self.logger.debug("Cleaning apt cache")
            subprocess.run(
                ["sudo", "apt-get", "clean"], check=True, capture_output=True
            )

            # Clean apt auto-remove
            subprocess.run(
                ["sudo", "apt-get", "autoremove", "-y"], check=True, capture_output=True
            )

            # Clean apt auto-clean
            subprocess.run(
                ["sudo", "apt-get", "autoclean"], check=True, capture_output=True
            )

            self.logger.info("Package cache cleaned successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error cleaning package cache: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error cleaning package cache: {e}")

    def _clean_trash(self):
        """Clean trash directories"""
        trash_dirs = [
            os.path.expanduser("~/.local/share/Trash"),
            os.path.expanduser("~/.Trash"),
        ]

        for trash_dir in trash_dirs:
            if os.path.exists(trash_dir):
                self.logger.debug(f"Cleaning trash directory: {trash_dir}")
                self._clean_directory(trash_dir, 0, [])  # Clean all trash

    def _clean_browser_cache(self):
        """Clean browser cache files"""
        browser_cache_dirs = [
            os.path.expanduser("~/.cache/google-chrome"),
            os.path.expanduser("~/.cache/chromium"),
            os.path.expanduser("~/.cache/mozilla"),
            os.path.expanduser("~/.mozilla/firefox/*/Cache"),
        ]

        for cache_dir in browser_cache_dirs:
            if "*" in cache_dir:
                # Handle glob patterns
                for expanded_dir in glob.glob(cache_dir):
                    if os.path.exists(expanded_dir):
                        self.logger.debug(f"Cleaning browser cache: {expanded_dir}")
                        self._clean_directory(expanded_dir, 7, [])
            else:
                if os.path.exists(cache_dir):
                    self.logger.debug(f"Cleaning browser cache: {cache_dir}")
                    self._clean_directory(cache_dir, 7, [])

    def _clean_system_cache(self):
        """Clean system cache"""
        system_cache_dirs = [
            "/var/cache/fontconfig",
            "/var/cache/man",
            os.path.expanduser("~/.cache/fontconfig"),
            os.path.expanduser("~/.cache/thumbnails"),
        ]

        for cache_dir in system_cache_dirs:
            if os.path.exists(cache_dir):
                self.logger.debug(f"Cleaning system cache: {cache_dir}")
                self._clean_directory(cache_dir, 30, [])

    def _clean_directory(
        self, directory: str, max_age_days: int, exclude_patterns: List[str]
    ):
        """
        Clean files in a directory

        Args:
            directory: Directory path to clean
            max_age_days: Maximum age of files to keep
            exclude_patterns: Patterns to exclude from cleaning
        """
        try:
            if not os.path.exists(directory):
                return

            cutoff_date = datetime.now() - timedelta(days=max_age_days)

            for root, dirs, files in os.walk(directory):
                # Clean files
                for file in files:
                    file_path = os.path.join(root, file)

                    # Check exclude patterns
                    if self._should_exclude(file, exclude_patterns):
                        continue

                    # Check file age
                    if max_age_days > 0 and not self._is_file_old(
                        file_path, max_age_days
                    ):
                        continue

                    self._remove_file(file_path)

                # Clean empty directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if self._is_directory_empty(dir_path):
                        self._remove_directory(dir_path)

        except Exception as e:
            self.logger.error(f"Error cleaning directory {directory}: {e}")

    def _should_exclude(self, filename: str, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        for pattern in exclude_patterns:
            if pattern.lower() in filename.lower():
                return True
        return False

    def _is_file_old(self, file_path: str, max_age_days: int) -> bool:
        """Check if file is older than max_age_days"""
        try:
            file_mtime = os.path.getmtime(file_path)
            cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
            return file_mtime < cutoff_time
        except OSError:
            return False

    def _is_directory_empty(self, directory: str) -> bool:
        """Check if directory is empty"""
        try:
            return not os.listdir(directory)
        except OSError:
            return False

    def _remove_file(self, file_path: str):
        """Remove a file and update statistics"""
        try:
            file_size = os.path.getsize(file_path)
            os.remove(file_path)
            self.stats["files_cleaned"] += 1
            self.stats["space_freed"] += file_size
            self.logger.debug(f"Removed file: {file_path}")
        except OSError as e:
            self.logger.debug(f"Could not remove file {file_path}: {e}")

    def _remove_directory(self, dir_path: str):
        """Remove a directory and update statistics"""
        try:
            shutil.rmtree(dir_path)
            self.stats["directories_cleaned"] += 1
            self.logger.debug(f"Removed directory: {dir_path}")
        except OSError as e:
            self.logger.debug(f"Could not remove directory {dir_path}: {e}")

    def _update_package_database(self):
        """Update package database"""
        try:
            self.logger.debug("Updating package database")
            subprocess.run(["sudo", "updatedb"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.logger.debug(
                "Could not update package database (updatedb not available)"
            )
        except Exception as e:
            self.logger.error(f"Error updating package database: {e}")

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes count to human readable string"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_count < 1024.0:
                return f"{bytes_count:.2f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.2f} PB"

    def get_cleanup_preview(self) -> Dict:
        """
        Get preview of what would be cleaned without actually cleaning

        Returns:
            Dictionary with preview information
        """
        preview = {
            "temp_files": [],
            "cache_files": [],
            "log_files": [],
            "estimated_space": 0,
        }

        try:
            # Preview temp files
            temp_dirs = self.config.get_temp_dirs()
            max_age_days = self.config.get_max_age_days()
            exclude_patterns = self.config.get_exclude_patterns()

            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    files = self._get_files_to_clean(
                        temp_dir, max_age_days, exclude_patterns
                    )
                    preview["temp_files"].extend(files)

            # Preview cache files
            cache_dirs = self.config.get_cache_dirs()
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    files = self._get_files_to_clean(
                        cache_dir, max_age_days, exclude_patterns
                    )
                    preview["cache_files"].extend(files)

            # Calculate estimated space
            all_files = preview["temp_files"] + preview["cache_files"]
            for file_path in all_files:
                try:
                    preview["estimated_space"] += os.path.getsize(file_path)
                except OSError:
                    pass

            return preview

        except Exception as e:
            self.logger.error(f"Error getting cleanup preview: {e}")
            return preview

    def _get_files_to_clean(
        self, directory: str, max_age_days: int, exclude_patterns: List[str]
    ) -> List[str]:
        """Get list of files that would be cleaned"""
        files_to_clean = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)

                    if self._should_exclude(file, exclude_patterns):
                        continue

                    if max_age_days > 0 and not self._is_file_old(
                        file_path, max_age_days
                    ):
                        continue

                    files_to_clean.append(file_path)

        except Exception as e:
            self.logger.error(f"Error getting files to clean from {directory}: {e}")

        return files_to_clean
