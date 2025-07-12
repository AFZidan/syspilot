"""
Scheduling Service for SysPilot
Handles scheduled cleanup operations
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Event, Thread
from typing import Callable, Dict, List, Optional

import schedule


class SchedulingService:
    """Service to manage scheduled cleanup operations"""

    def __init__(self, config_manager, cleanup_service):
        self.config = config_manager
        self.cleanup_service = cleanup_service
        self.logger = logging.getLogger(__name__)
        self.config_file = Path.home() / ".config" / "syspilot" / "schedule.json"
        self.is_running = False
        self.scheduler_thread = None
        self.stop_event = Event()

        # Load existing schedules
        self.schedules = self._load_schedules()

    def _load_schedules(self) -> Dict:
        """Load schedules from configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"Error loading schedules: {e}")
            return {}

    def _save_schedules(self) -> bool:
        """Save schedules to configuration file"""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, "w") as f:
                json.dump(self.schedules, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")
            return False

    def add_schedule(
        self,
        schedule_id: str,
        schedule_type: str,
        frequency: str,
        time_str: str = None,
        cleanup_types: List[str] = None,
    ) -> bool:
        """
        Add a new cleanup schedule

        Args:
            schedule_id: Unique identifier for the schedule
            schedule_type: Type of schedule (daily, weekly, etc.)
            frequency: Frequency specification
            time_str: Time to run (HH:MM format)
            cleanup_types: List of cleanup types to run

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if cleanup_types is None:
                cleanup_types = ["temp", "cache", "logs"]

            schedule_config = {
                "id": schedule_id,
                "type": schedule_type,
                "frequency": frequency,
                "time": time_str,
                "cleanup_types": cleanup_types,
                "enabled": True,
                "created": datetime.now().isoformat(),
                "last_run": None,
                "next_run": None,
            }

            self.schedules[schedule_id] = schedule_config

            # Add to schedule library
            self._add_to_scheduler(schedule_config)

            # Save configuration
            if self._save_schedules():
                self.logger.info(f"Added schedule: {schedule_id}")
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(f"Error adding schedule: {e}")
            return False

    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a schedule"""
        try:
            if schedule_id in self.schedules:
                del self.schedules[schedule_id]

                # Clear and rebuild scheduler
                schedule.clear()
                for sched_config in self.schedules.values():
                    if sched_config.get("enabled", False):
                        self._add_to_scheduler(sched_config)

                if self._save_schedules():
                    self.logger.info(f"Removed schedule: {schedule_id}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error removing schedule: {e}")
            return False

    def enable_schedule(self, schedule_id: str) -> bool:
        """Enable a schedule"""
        try:
            if schedule_id in self.schedules:
                self.schedules[schedule_id]["enabled"] = True
                self._add_to_scheduler(self.schedules[schedule_id])
                return self._save_schedules()
            return False
        except Exception as e:
            self.logger.error(f"Error enabling schedule: {e}")
            return False

    def disable_schedule(self, schedule_id: str) -> bool:
        """Disable a schedule"""
        try:
            if schedule_id in self.schedules:
                self.schedules[schedule_id]["enabled"] = False
                # Clear and rebuild scheduler
                schedule.clear()
                for sched_config in self.schedules.values():
                    if sched_config.get("enabled", False):
                        self._add_to_scheduler(sched_config)
                return self._save_schedules()
            return False
        except Exception as e:
            self.logger.error(f"Error disabling schedule: {e}")
            return False

    def _add_to_scheduler(self, schedule_config: Dict) -> None:
        """Add a schedule configuration to the scheduler"""
        try:
            schedule_type = schedule_config.get("type", "daily")
            time_str = schedule_config.get("time", "02:00")
            cleanup_types = schedule_config.get(
                "cleanup_types", ["temp", "cache", "logs"]
            )

            # Create the job function
            def job():
                self._run_scheduled_cleanup(schedule_config["id"], cleanup_types)

            # Add to scheduler based on type
            if schedule_type == "daily":
                schedule.every().day.at(time_str).do(job)
            elif schedule_type == "weekly":
                frequency = schedule_config.get("frequency", "monday")
                getattr(schedule.every(), frequency.lower()).at(time_str).do(job)
            elif schedule_type == "hourly":
                schedule.every().hour.do(job)
            elif schedule_type == "startup":
                # Run on startup (handled differently)
                pass

        except Exception as e:
            self.logger.error(f"Error adding schedule to scheduler: {e}")

    def _run_scheduled_cleanup(
        self, schedule_id: str, cleanup_types: List[str]
    ) -> None:
        """Run a scheduled cleanup operation"""
        try:
            self.logger.info(f"Running scheduled cleanup: {schedule_id}")

            # Update last run time
            if schedule_id in self.schedules:
                self.schedules[schedule_id]["last_run"] = datetime.now().isoformat()
                self._save_schedules()

            # Create a custom cleanup based on types
            if "temp" in cleanup_types:
                self.cleanup_service._clean_temp_files()
            if "cache" in cleanup_types:
                self.cleanup_service._clean_cache_files()
            if "logs" in cleanup_types:
                self.cleanup_service._clean_log_files()
            if "packages" in cleanup_types:
                self.cleanup_service._clean_package_cache()

            self.logger.info(f"Completed scheduled cleanup: {schedule_id}")

        except Exception as e:
            self.logger.error(f"Error running scheduled cleanup {schedule_id}: {e}")

    def start_scheduler(self) -> bool:
        """Start the background scheduler"""
        try:
            if self.is_running:
                return True

            # Clear existing schedules
            schedule.clear()

            # Add enabled schedules
            for schedule_config in self.schedules.values():
                if schedule_config.get("enabled", False):
                    self._add_to_scheduler(schedule_config)

            # Start scheduler thread
            self.is_running = True
            self.stop_event.clear()
            self.scheduler_thread = Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()

            self.logger.info("Scheduler started")
            return True

        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            return False

    def stop_scheduler(self) -> bool:
        """Stop the background scheduler"""
        try:
            if not self.is_running:
                return True

            self.is_running = False
            self.stop_event.set()

            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=5)

            schedule.clear()
            self.logger.info("Scheduler stopped")
            return True

        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
            return False

    def _scheduler_loop(self) -> None:
        """Main scheduler loop"""
        while self.is_running and not self.stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)

    def get_schedules(self) -> Dict:
        """Get all configured schedules"""
        return self.schedules.copy()

    def get_next_run_times(self) -> Dict[str, str]:
        """Get next run times for all schedules"""
        next_runs = {}

        for job in schedule.jobs:
            # This is a simplified version - in practice you'd need to track
            # which job corresponds to which schedule
            next_run = job.next_run
            if next_run:
                next_runs["next_scheduled"] = next_run.strftime("%Y-%m-%d %H:%M:%S")
                break

        return next_runs

    def create_default_schedules(self) -> bool:
        """Create default cleanup schedules"""
        try:
            # Daily cleanup at 2 AM
            self.add_schedule(
                "daily_cleanup", "daily", "daily", "02:00", ["temp", "cache"]
            )

            # Weekly full cleanup on Sunday at 3 AM
            self.add_schedule(
                "weekly_full_cleanup",
                "weekly",
                "sunday",
                "03:00",
                ["temp", "cache", "logs", "packages"],
            )

            self.logger.info("Created default schedules")
            return True

        except Exception as e:
            self.logger.error(f"Error creating default schedules: {e}")
            return False
