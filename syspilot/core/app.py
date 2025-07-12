"""
Main GUI Application
"""

import logging
import os
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ..platforms.factory import PlatformFactory
from ..utils.config import ConfigManager
from ..utils.logger import get_logger

# Optional services
try:
    from ..services.autostart_service import AutoStartService
except ImportError:
    AutoStartService = None

try:
    from ..services.scheduling_service import SchedulingService
except ImportError:
    SchedulingService = None

# Optional chart widgets
try:
    from ..widgets.charts import SystemMonitoringWidget, TrendMonitoringWidget
except ImportError:
    SystemMonitoringWidget = None
    TrendMonitoringWidget = None


class CleanupWorker(QThread):
    """Worker thread for cleanup operations"""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, cleanup_service):
        super().__init__()
        self.cleanup_service = cleanup_service
        self.is_running = False

    def run(self):
        """Run cleanup operation"""
        try:
            self.is_running = True
            result = self.cleanup_service.full_cleanup(
                progress_callback=self.progress.emit, status_callback=self.status.emit
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.is_running = False


class MonitoringWorker(QThread):
    """Worker thread for system monitoring"""

    data_updated = pyqtSignal(dict)

    def __init__(self, monitoring_service):
        super().__init__()
        self.monitoring_service = monitoring_service
        self.is_running = False

    def run(self):
        """Run monitoring loop"""
        self.is_running = True
        self.logger = logging.getLogger(__name__)
        self.logger.info("MonitoringWorker thread started")

        while self.is_running:
            try:
                data = self.monitoring_service.get_system_stats()
                if data:  # Only emit if we have data
                    self.data_updated.emit(data)
                else:
                    self.logger.warning("No monitoring data received")
                self.msleep(2000)  # Update every 2 seconds
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                self.msleep(5000)  # Wait longer on error

        self.logger.info("MonitoringWorker thread stopped")

    def stop(self):
        """Stop the monitoring loop"""
        self.is_running = False
        self.wait()  # Wait for thread to finish


class ScheduleDialog(QDialog):
    """Dialog for creating/editing cleanup schedules"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Cleanup Schedule")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Schedule ID
        self.schedule_id_edit = QLineEdit()
        self.schedule_id_edit.setPlaceholderText("e.g., daily_cleanup")
        form_layout.addRow("Schedule ID:", self.schedule_id_edit)

        # Schedule type
        self.schedule_type_combo = QComboBox()
        self.schedule_type_combo.addItems(["daily", "weekly", "hourly"])
        form_layout.addRow("Schedule Type:", self.schedule_type_combo)

        # Frequency (for weekly)
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(
            [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ]
        )
        form_layout.addRow("Day (for weekly):", self.frequency_combo)

        # Time
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(2, 0))  # Default to 2:00 AM
        form_layout.addRow("Time:", self.time_edit)

        # Cleanup types
        cleanup_group = QGroupBox("Cleanup Types")
        cleanup_layout = QVBoxLayout(cleanup_group)

        self.temp_checkbox = QCheckBox("Temporary files")
        self.temp_checkbox.setChecked(True)
        cleanup_layout.addWidget(self.temp_checkbox)

        self.cache_checkbox = QCheckBox("Cache files")
        self.cache_checkbox.setChecked(True)
        cleanup_layout.addWidget(self.cache_checkbox)

        self.logs_checkbox = QCheckBox("Log files")
        self.logs_checkbox.setChecked(False)
        cleanup_layout.addWidget(self.logs_checkbox)

        self.packages_checkbox = QCheckBox("Package cache")
        self.packages_checkbox.setChecked(False)
        cleanup_layout.addWidget(self.packages_checkbox)

        form_layout.addRow(cleanup_group)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect signals
        self.schedule_type_combo.currentTextChanged.connect(self.on_type_changed)
        self.on_type_changed()

    def on_type_changed(self):
        """Handle schedule type change"""
        schedule_type = self.schedule_type_combo.currentText()
        self.frequency_combo.setEnabled(schedule_type == "weekly")

    def get_schedule_data(self):
        """Get schedule data from dialog"""
        cleanup_types = []
        if self.temp_checkbox.isChecked():
            cleanup_types.append("temp")
        if self.cache_checkbox.isChecked():
            cleanup_types.append("cache")
        if self.logs_checkbox.isChecked():
            cleanup_types.append("logs")
        if self.packages_checkbox.isChecked():
            cleanup_types.append("packages")

        return {
            "id": self.schedule_id_edit.text().strip(),
            "type": self.schedule_type_combo.currentText(),
            "frequency": self.frequency_combo.currentText(),
            "time": self.time_edit.time().toString("HH:mm"),
            "cleanup_types": cleanup_types,
        }


class SysPilotApp:
    """Main application class"""

    def __init__(self, config_path=None):
        self.config = ConfigManager(config_path)
        self.logger = get_logger(__name__)
        self.app = None
        self.main_window = None
        self.tray_icon = None

        # Check platform support
        if not PlatformFactory.is_current_platform_supported():
            from syspilot.platforms import get_platform

            platform = get_platform()
            self.logger.error(f"Platform '{platform}' is not supported")
            raise NotImplementedError(f"Platform '{platform}' is not supported")

        # Services - use platform factory
        self.cleanup_service = PlatformFactory.create_cleanup_service(self.config)
        self.monitoring_service = PlatformFactory.create_monitoring_service(self.config)
        self.system_info_service = PlatformFactory.create_system_info_service()

        # Optional services
        self.autostart_service = AutoStartService() if AutoStartService else None
        self.scheduling_service = (
            SchedulingService(self.config, self.cleanup_service)
            if SchedulingService
            else None
        )

        # Workers
        self.cleanup_worker = None
        self.monitoring_worker = None
        self.monitoring_timer = None

        # UI Components
        self.progress_bar = None
        self.status_label = None
        self.clean_button = None
        self.monitoring_widgets = {}

        # Chart widgets
        self.system_charts = None
        self.trend_charts = None

    def run(self):
        """Run the application"""
        try:
            self.logger.info("Creating QApplication...")
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("SysPilot")
            self.app.setApplicationVersion("1.0.0")

            # Set application icon
            # Try to find icon in multiple possible locations
            possible_paths = [
                Path(__file__).parent.parent
                / "assets"
                / "syspilot_icon.png",  # Development
                Path(
                    "/usr/local/lib/syspilot/syspilot/assets/syspilot_icon.png"
                ),  # System install
                Path(
                    "/usr/share/syspilot/assets/syspilot_icon.png"
                ),  # Alternative system location
            ]

            icon_path = None
            for path in possible_paths:
                if path.exists():
                    icon_path = path
                    break

            self.logger.info(f"Looking for icon, found at: {icon_path}")
            if icon_path:
                self.logger.info("Setting application icon...")
                self.app.setWindowIcon(QIcon(str(icon_path)))

            self.logger.info("Setting up UI...")
            self.setup_ui()
            self.logger.info("Setting up system tray...")
            self.setup_system_tray()
            self.logger.info("Starting monitoring...")
            self.start_monitoring()

            self.logger.info("Starting Qt event loop...")
            sys.exit(self.app.exec_())
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            raise

    def setup_ui(self):
        """Setup the main user interface"""
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("SysPilot - System Cleanup Tool")
        self.main_window.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Cleanup tab
        cleanup_tab = self.create_cleanup_tab()
        tab_widget.addTab(cleanup_tab, "System Cleanup")

        # Monitoring tab
        monitoring_tab = self.create_monitoring_tab()
        tab_widget.addTab(monitoring_tab, "System Monitor")

        # Settings tab
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "Settings")

        self.main_window.show()

    def create_cleanup_tab(self):
        """Create the cleanup tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title = QLabel("System Cleanup")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # System info summary
        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)

        system_info = self.system_info_service.get_system_info()
        info_text = f"""
        System: {system_info['os_name']} {system_info['os_version']}
        Architecture: {system_info['architecture']}
        Total Memory: {system_info['total_memory']}
        Available Disk: {system_info['available_disk']}
        """
        info_label = QLabel(info_text)
        info_layout.addWidget(info_label)
        layout.addWidget(info_group)

        # Cleanup options
        cleanup_group = QGroupBox("Cleanup Options")
        cleanup_layout = QVBoxLayout(cleanup_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        cleanup_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to clean")
        cleanup_layout.addWidget(self.status_label)

        # Clean button
        self.clean_button = QPushButton("Start Cleanup")
        self.clean_button.clicked.connect(self.start_cleanup)
        cleanup_layout.addWidget(self.clean_button)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        cleanup_layout.addWidget(self.results_text)

        layout.addWidget(cleanup_group)

        return tab

    def create_monitoring_tab(self):
        """Create the monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title = QLabel("System Monitor")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Create tab widget for different monitoring views
        monitoring_tabs = QTabWidget()
        layout.addWidget(monitoring_tabs)

        # Charts view
        charts_tab = QWidget()
        charts_layout = QVBoxLayout(charts_tab)

        if SystemMonitoringWidget:
            self.system_charts = SystemMonitoringWidget()
            charts_layout.addWidget(self.system_charts)
        else:
            charts_layout.addWidget(QLabel("Charts require matplotlib to be installed"))

        monitoring_tabs.addTab(charts_tab, "Charts")

        # Trends view
        trends_tab = QWidget()
        trends_layout = QVBoxLayout(trends_tab)

        if TrendMonitoringWidget:
            self.trend_charts = TrendMonitoringWidget()
            trends_layout.addWidget(self.trend_charts)
        else:
            trends_layout.addWidget(QLabel("Trends require matplotlib to be installed"))

        monitoring_tabs.addTab(trends_tab, "Trends")

        # Traditional view
        traditional_tab = QWidget()
        traditional_layout = QVBoxLayout(traditional_tab)

        # Splitter for layout
        splitter = QSplitter(Qt.Horizontal)
        traditional_layout.addWidget(splitter)

        # Left side - System stats
        stats_group = QGroupBox("System Statistics")
        stats_layout = QVBoxLayout(stats_group)

        # CPU usage
        self.monitoring_widgets["cpu_label"] = QLabel("CPU Usage: Loading...")
        stats_layout.addWidget(self.monitoring_widgets["cpu_label"])

        # CPU temperature
        self.monitoring_widgets["cpu_temp_label"] = QLabel(
            "CPU Temperature: Loading..."
        )
        stats_layout.addWidget(self.monitoring_widgets["cpu_temp_label"])

        # Memory usage
        self.monitoring_widgets["memory_label"] = QLabel("Memory Usage: Loading...")
        stats_layout.addWidget(self.monitoring_widgets["memory_label"])

        # Disk usage
        self.monitoring_widgets["disk_label"] = QLabel("Disk Usage: Loading...")
        stats_layout.addWidget(self.monitoring_widgets["disk_label"])

        # Network
        self.monitoring_widgets["network_label"] = QLabel("Network: Loading...")
        stats_layout.addWidget(self.monitoring_widgets["network_label"])

        splitter.addWidget(stats_group)

        # Right side - Top processes
        processes_group = QGroupBox("Top Processes (CPU Usage)")
        processes_layout = QVBoxLayout(processes_group)

        self.monitoring_widgets["processes_list"] = QListWidget()
        processes_layout.addWidget(self.monitoring_widgets["processes_list"])

        splitter.addWidget(processes_group)

        monitoring_tabs.addTab(traditional_tab, "Details")

        return tab

    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        # Scroll area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Auto-start settings
        autostart_group = QGroupBox("Auto-start Settings")
        autostart_layout = QVBoxLayout(autostart_group)

        # Auto-start status
        self.autostart_status_label = QLabel("Checking auto-start status...")
        autostart_layout.addWidget(self.autostart_status_label)

        # Auto-start buttons
        autostart_buttons = QHBoxLayout()

        self.enable_autostart_btn = QPushButton("Enable Auto-start")
        self.enable_autostart_btn.clicked.connect(self.enable_autostart)
        autostart_buttons.addWidget(self.enable_autostart_btn)

        self.disable_autostart_btn = QPushButton("Disable Auto-start")
        self.disable_autostart_btn.clicked.connect(self.disable_autostart)
        autostart_buttons.addWidget(self.disable_autostart_btn)

        autostart_layout.addLayout(autostart_buttons)
        scroll_layout.addWidget(autostart_group)

        # Scheduling settings
        scheduling_group = QGroupBox("Scheduled Cleanup")
        scheduling_layout = QVBoxLayout(scheduling_group)

        # Current schedules
        self.schedules_label = QLabel("Current Schedules:")
        scheduling_layout.addWidget(self.schedules_label)

        self.schedules_list = QListWidget()
        self.schedules_list.setMaximumHeight(100)
        scheduling_layout.addWidget(self.schedules_list)

        # Schedule controls
        schedule_controls = QHBoxLayout()

        add_schedule_btn = QPushButton("Add Schedule")
        add_schedule_btn.clicked.connect(self.add_schedule_dialog)
        schedule_controls.addWidget(add_schedule_btn)

        remove_schedule_btn = QPushButton("Remove Schedule")
        remove_schedule_btn.clicked.connect(self.remove_selected_schedule)
        schedule_controls.addWidget(remove_schedule_btn)

        default_schedules_btn = QPushButton("Create Default Schedules")
        default_schedules_btn.clicked.connect(self.create_default_schedules)
        schedule_controls.addWidget(default_schedules_btn)

        scheduling_layout.addLayout(schedule_controls)
        scroll_layout.addWidget(scheduling_group)

        # Application settings
        app_settings_group = QGroupBox("Application Settings")
        app_settings_layout = QVBoxLayout(app_settings_group)

        # Monitoring interval
        monitoring_layout = QHBoxLayout()
        monitoring_layout.addWidget(QLabel("Monitoring Interval:"))

        self.monitoring_interval_spin = QSpinBox()
        self.monitoring_interval_spin.setRange(1, 60)
        self.monitoring_interval_spin.setValue(self.config.get_monitoring_interval())
        self.monitoring_interval_spin.setSuffix(" seconds")
        monitoring_layout.addWidget(self.monitoring_interval_spin)

        app_settings_layout.addLayout(monitoring_layout)

        # Auto cleanup threshold
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Auto Cleanup Threshold:"))

        self.cleanup_threshold_spin = QSpinBox()
        self.cleanup_threshold_spin.setRange(1, 365)
        self.cleanup_threshold_spin.setValue(self.config.get_max_age_days())
        self.cleanup_threshold_spin.setSuffix(" days")
        threshold_layout.addWidget(self.cleanup_threshold_spin)

        app_settings_layout.addLayout(threshold_layout)

        # Apply settings button
        apply_settings_btn = QPushButton("Apply Settings")
        apply_settings_btn.clicked.connect(self.apply_settings)
        app_settings_layout.addWidget(apply_settings_btn)

        scroll_layout.addWidget(app_settings_group)

        # About section
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)

        about_btn = QPushButton("About SysPilot")
        about_btn.clicked.connect(self.show_about)
        about_layout.addWidget(about_btn)

        scroll_layout.addWidget(about_group)

        # Set up scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Update UI with current status
        self.update_settings_ui()

        return tab

    def find_icon_path(self):
        """Find the icon path, checking multiple possible locations"""
        icon_filename = "syspilot_icon.png"

        # Possible icon locations
        possible_paths = [
            # Development environment - relative to this file
            Path(__file__).parent.parent / "assets" / icon_filename,
            # Development environment - relative to project root
            Path(__file__).parent.parent.parent / "assets" / icon_filename,
            # Installed location (pip install)
            Path("/usr/local/lib/syspilot/syspilot/assets") / icon_filename,
            # Alternative system locations
            Path("/usr/share/syspilot/assets") / icon_filename,
            Path("/opt/syspilot/assets") / icon_filename,
        ]

        self.logger.info("Searching for icon in the following locations:")
        for path in possible_paths:
            self.logger.info(f"  - {path} (exists: {path.exists()})")
            if path.exists():
                self.logger.info(f"Found icon at: {path}")
                return path

        self.logger.error(f"Icon '{icon_filename}' not found in any location")
        return None

    def setup_system_tray(self):
        """Setup system tray icon"""
        self.logger.info("Checking system tray availability...")
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray not available")
            return

        self.logger.info("Creating system tray icon...")
        self.tray_icon = QSystemTrayIcon(self.app)

        # Set icon - search multiple possible locations
        icon_path = self.find_icon_path()
        self.logger.info(f"Setting tray icon from: {icon_path}")
        if icon_path and icon_path.exists():
            icon = QIcon(str(icon_path))
            self.logger.info(f"Icon loaded, null: {icon.isNull()}")
            self.tray_icon.setIcon(icon)
        else:
            self.logger.error("Tray icon file not found!")

        # Create context menu
        tray_menu = QMenu()

        show_action = QAction("Show SysPilot", self.main_window)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)

        cleanup_action = QAction("Quick Cleanup", self.main_window)
        cleanup_action.triggered.connect(self.start_cleanup)
        tray_menu.addAction(cleanup_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self.main_window)
        quit_action.triggered.connect(self.app.quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # Double-click to show main window
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window()

    def show_main_window(self):
        """Show the main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def start_cleanup(self):
        """Start the cleanup process"""
        if self.cleanup_worker and self.cleanup_worker.is_running:
            return

        self.clean_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting cleanup...")

        # Start cleanup worker
        self.cleanup_worker = CleanupWorker(self.cleanup_service)
        self.cleanup_worker.progress.connect(self.update_progress)
        self.cleanup_worker.status.connect(self.update_status)
        self.cleanup_worker.finished.connect(self.cleanup_finished)
        self.cleanup_worker.error.connect(self.cleanup_error)
        self.cleanup_worker.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """Update status label"""
        self.status_label.setText(status)

    def cleanup_finished(self, result):
        """Handle cleanup completion"""
        self.clean_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Cleanup completed")

        # Show results
        results_text = f"""
        Cleanup Results:
        - Temporary files cleaned: {result.get('temp_files_cleaned', 0)}
        - Cache files cleaned: {result.get('cache_files_cleaned', 0)}
        - Space freed: {result.get('space_freed', '0 MB')}
        - Time taken: {result.get('time_taken', '0 seconds')}
        """
        self.results_text.setText(results_text)

        # Show notification
        if self.tray_icon:
            self.tray_icon.showMessage(
                "SysPilot",
                f"Cleanup completed! Freed {result.get('space_freed', '0 MB')}",
                QSystemTrayIcon.Information,
                3000,
            )

    def cleanup_error(self, error):
        """Handle cleanup error"""
        self.clean_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Cleanup failed")

        QMessageBox.critical(
            self.main_window, "Cleanup Error", f"Cleanup failed: {error}"
        )

    def start_monitoring(self):
        """Start system monitoring"""
        self.logger.info("Creating monitoring worker...")
        self.monitoring_worker = MonitoringWorker(self.monitoring_service)
        self.monitoring_worker.data_updated.connect(self.update_monitoring_data)
        self.logger.info("Starting monitoring worker thread...")
        self.monitoring_worker.start()
        self.logger.info("Monitoring worker started successfully")

        # Also set up a timer as backup to ensure updates happen
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self.manual_monitoring_update)
        self.monitoring_timer.start(3000)  # Every 3 seconds
        self.logger.info("Backup monitoring timer started")

    def manual_monitoring_update(self):
        """Manual monitoring update as backup"""
        try:
            data = self.monitoring_service.get_system_stats()
            if data:
                self.update_monitoring_data(data)
        except Exception as e:
            self.logger.error(f"Manual monitoring update error: {e}")

    def update_monitoring_data(self, data):
        """Update monitoring widgets with new data"""
        # Update traditional monitoring widgets
        if "cpu_percent" in data:
            cpu_text = f"CPU Usage: {data['cpu_percent']:.1f}%"
            self.monitoring_widgets["cpu_label"].setText(cpu_text)

        if "cpu_temperature" in data and data["cpu_temperature"] is not None:
            temp_text = f"CPU Temperature: {data['cpu_temperature']:.1f}°C"
            self.monitoring_widgets["cpu_temp_label"].setText(temp_text)
            # Add color coding for temperature levels
            if data["cpu_temperature"] > 80:
                self.monitoring_widgets["cpu_temp_label"].setStyleSheet(
                    "color: red; font-weight: bold;"
                )
            elif data["cpu_temperature"] > 70:
                self.monitoring_widgets["cpu_temp_label"].setStyleSheet(
                    "color: orange; font-weight: bold;"
                )
            elif data["cpu_temperature"] > 60:
                self.monitoring_widgets["cpu_temp_label"].setStyleSheet(
                    "color: #FFA500;"
                )  # Dark orange
            else:
                self.monitoring_widgets["cpu_temp_label"].setStyleSheet("color: green;")
        elif "cpu_temperature" in data and data["cpu_temperature"] is None:
            self.monitoring_widgets["cpu_temp_label"].setText("CPU Temperature: N/A")

        if "memory_percent" in data:
            memory_text = f"Memory Usage: {data['memory_percent']:.1f}%"
            self.monitoring_widgets["memory_label"].setText(memory_text)

        if "disk_percent" in data:
            disk_text = f"Disk Usage: {data['disk_percent']:.1f}%"
            self.monitoring_widgets["disk_label"].setText(disk_text)

        if "network_io" in data and data["network_io"]:
            network_text = f"Network: {data['network_io'].get('bytes_sent', 0)} KB/s up, {data['network_io'].get('bytes_recv', 0)} KB/s down"
            self.monitoring_widgets["network_label"].setText(network_text)

        if "top_processes" in data and data["top_processes"]:
            processes_list = self.monitoring_widgets["processes_list"]
            processes_list.clear()

            for proc in data["top_processes"][:3]:  # Top 3 processes
                item_text = f"{proc['name']} - CPU: {proc['cpu_percent']:.1f}% - Memory: {proc['memory_percent']:.1f}%"
                processes_list.addItem(item_text)

        # Update chart widgets
        if self.system_charts:
            self.system_charts.update_data(data)

        if self.trend_charts:
            self.trend_charts.update_data(data)

    def enable_autostart(self):
        """Enable auto-start"""
        if not self.autostart_service:
            QMessageBox.warning(
                self.main_window,
                "Feature Unavailable",
                "Auto-start feature requires additional dependencies.\n"
                "Please install the complete package.",
            )
            return

        try:
            if self.autostart_service.enable_autostart("desktop"):
                QMessageBox.information(
                    self.main_window,
                    "Auto-start Enabled",
                    "Auto-start has been enabled successfully.\n"
                    "SysPilot will now start automatically when you log in.",
                )
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Auto-start Failed",
                    "Failed to enable auto-start. Please check the logs for more information.",
                )
            self.update_settings_ui()
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Auto-start Error",
                f"Error enabling auto-start: {str(e)}",
            )

    def disable_autostart(self):
        """Disable auto-start"""
        if not self.autostart_service:
            QMessageBox.warning(
                self.main_window,
                "Feature Unavailable",
                "Auto-start feature requires additional dependencies.",
            )
            return

        try:
            if self.autostart_service.disable_autostart():
                QMessageBox.information(
                    self.main_window,
                    "Auto-start Disabled",
                    "Auto-start has been disabled successfully.",
                )
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Auto-start Failed",
                    "Failed to disable auto-start. Please check the logs for more information.",
                )
            self.update_settings_ui()
        except Exception as e:
            QMessageBox.critical(
                self.main_window,
                "Auto-start Error",
                f"Error disabling auto-start: {str(e)}",
            )

    def add_schedule_dialog(self):
        """Show dialog to add new schedule"""
        dialog = ScheduleDialog(self.main_window)
        if dialog.exec_() == QDialog.Accepted:
            schedule_data = dialog.get_schedule_data()

            success = self.scheduling_service.add_schedule(
                schedule_data["id"],
                schedule_data["type"],
                schedule_data["frequency"],
                schedule_data["time"],
                schedule_data["cleanup_types"],
            )

            if success:
                QMessageBox.information(
                    self.main_window,
                    "Schedule Added",
                    f"Schedule '{schedule_data['id']}' has been added successfully.",
                )
                self.update_schedules_list()
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Schedule Failed",
                    "Failed to add schedule. Please check the logs for more information.",
                )

    def remove_selected_schedule(self):
        """Remove selected schedule"""
        current_item = self.schedules_list.currentItem()
        if current_item:
            schedule_id = current_item.text().split(" - ")[0]

            reply = QMessageBox.question(
                self.main_window,
                "Remove Schedule",
                f"Are you sure you want to remove the schedule '{schedule_id}'?",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                if self.scheduling_service.remove_schedule(schedule_id):
                    QMessageBox.information(
                        self.main_window,
                        "Schedule Removed",
                        f"Schedule '{schedule_id}' has been removed successfully.",
                    )
                    self.update_schedules_list()
                else:
                    QMessageBox.warning(
                        self.main_window,
                        "Remove Failed",
                        "Failed to remove schedule. Please check the logs for more information.",
                    )

    def create_default_schedules(self):
        """Create default schedules"""
        reply = QMessageBox.question(
            self.main_window,
            "Create Default Schedules",
            "This will create default daily and weekly cleanup schedules.\n"
            "Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            if self.scheduling_service.create_default_schedules():
                QMessageBox.information(
                    self.main_window,
                    "Default Schedules Created",
                    "Default schedules have been created successfully:\n"
                    "• Daily cleanup at 2:00 AM\n"
                    "• Weekly full cleanup on Sunday at 3:00 AM",
                )
                self.update_schedules_list()
            else:
                QMessageBox.warning(
                    self.main_window,
                    "Creation Failed",
                    "Failed to create default schedules. Please check the logs for more information.",
                )

    def apply_settings(self):
        """Apply settings changes"""
        try:
            # Update monitoring interval
            interval = self.monitoring_interval_spin.value()
            self.config.set("monitoring", "interval", interval)

            # Update cleanup threshold
            threshold = self.cleanup_threshold_spin.value()
            self.config.set("cleanup", "max_age_days", threshold)

            # Save configuration
            self.config.save_config()

            QMessageBox.information(
                self.main_window,
                "Settings Applied",
                "Settings have been applied successfully.\n"
                "Some changes may require restarting the application.",
            )

        except Exception as e:
            QMessageBox.critical(
                self.main_window, "Settings Error", f"Error applying settings: {str(e)}"
            )

    def update_settings_ui(self):
        """Update settings UI with current status"""
        try:
            # Update autostart status
            if self.autostart_service:
                status = self.autostart_service.get_autostart_status()
                if status["enabled"]:
                    self.autostart_status_label.setText(
                        "Auto-start is currently ENABLED"
                    )
                    self.enable_autostart_btn.setEnabled(False)
                    self.disable_autostart_btn.setEnabled(True)
                else:
                    self.autostart_status_label.setText(
                        "Auto-start is currently DISABLED"
                    )
                    self.enable_autostart_btn.setEnabled(True)
                    self.disable_autostart_btn.setEnabled(False)
            else:
                self.autostart_status_label.setText(
                    "Auto-start feature not available (missing dependencies)"
                )
                self.enable_autostart_btn.setEnabled(False)
                self.disable_autostart_btn.setEnabled(False)

            # Update schedules list
            self.update_schedules_list()

        except Exception as e:
            self.logger.error(f"Error updating settings UI: {e}")

    def update_schedules_list(self):
        """Update the schedules list widget"""
        try:
            self.schedules_list.clear()

            if not self.scheduling_service:
                self.schedules_list.addItem(
                    "Scheduling feature not available (missing dependencies)"
                )
                return

            schedules = self.scheduling_service.get_schedules()

            if not schedules:
                self.schedules_list.addItem("No schedules configured")
                return

            for schedule_id, schedule_data in schedules.items():
                status = (
                    "Enabled" if schedule_data.get("enabled", False) else "Disabled"
                )
                schedule_type = schedule_data.get("type", "unknown")
                time_str = schedule_data.get("time", "N/A")

                item_text = (
                    f"{schedule_id} - {schedule_type.title()} at {time_str} ({status})"
                )
                self.schedules_list.addItem(item_text)

        except Exception as e:
            self.logger.error(f"Error updating schedules list: {e}")

    def setup_scheduled_cleanup(self):
        """Setup scheduled cleanup (deprecated - use add_schedule_dialog)"""
        self.add_schedule_dialog()

    def toggle_auto_start(self):
        """Toggle auto-start setting (deprecated - use enable/disable_autostart)"""
        if self.autostart_service.is_autostart_enabled():
            self.disable_autostart()
        else:
            self.enable_autostart()

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self.main_window,
            "About SysPilot",
            """
            SysPilot v1.0.0

            A powerful system cleanup and monitoring tool for Ubuntu and Debian systems.

            Features:
            • System cleanup and optimization
            • Real-time system monitoring
            • Background operation with system tray
            • Scheduled maintenance

            Built with Python and PyQt5

            © 2025 SysPilot Team
            """,
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.main_window.hide()
            event.ignore()
        else:
            if self.monitoring_worker:
                self.monitoring_worker.stop()
            event.accept()
