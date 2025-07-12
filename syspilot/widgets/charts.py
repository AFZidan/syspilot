"""
Chart Widgets for SysPilot
Provides various chart widgets for system monitoring
"""

import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class BaseChartWidget(QWidget):
    """Base class for chart widgets"""

    def __init__(self, title="Chart"):
        super().__init__()
        self.title = title
        self.setup_ui()

    def setup_ui(self):
        """Setup the basic UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # Create matplotlib figure
        self.figure = Figure(figsize=(6, 4), dpi=80)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Set transparent background
        self.figure.patch.set_facecolor("none")
        self.canvas.setStyleSheet("background-color: transparent;")


class PieChartWidget(BaseChartWidget):
    """Pie chart widget for showing usage percentages"""

    def __init__(self, title="Usage", colors=None):
        self.colors = colors or ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"]
        super().__init__(title)

    def update_data(self, used_percent, label="Used"):
        """Update pie chart with new data"""
        self.figure.clear()

        # Create pie chart
        ax = self.figure.add_subplot(111)

        # Data for pie chart
        sizes = [used_percent, 100 - used_percent]
        labels = [f"{label} ({used_percent:.1f}%)", f"Free ({100 - used_percent:.1f}%)"]
        colors = [self.colors[0], self.colors[1]]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            textprops={"fontsize": 10},
        )

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis("equal")

        # Style the chart
        ax.set_title(self.title, fontsize=12, fontweight="bold")

        # Refresh canvas
        self.canvas.draw()


class LineChartWidget(BaseChartWidget):
    """Line chart widget for showing trends over time"""

    def __init__(self, title="Trend", max_points=50):
        self.max_points = max_points
        self.data_points = []
        super().__init__(title)

    def add_data_point(self, value):
        """Add a new data point"""
        self.data_points.append(value)

        # Keep only the last max_points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)

        self.update_chart()

    def update_chart(self):
        """Update the line chart"""
        if not self.data_points:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Plot the data
        x = range(len(self.data_points))
        ax.plot(x, self.data_points, "b-", linewidth=2)
        ax.fill_between(x, self.data_points, alpha=0.3)

        # Style the chart
        ax.set_title(self.title, fontsize=12, fontweight="bold")
        ax.set_ylabel("Percentage (%)")
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)

        # Remove x-axis labels for cleaner look
        ax.set_xticks([])

        # Refresh canvas
        self.canvas.draw()


class BarChartWidget(BaseChartWidget):
    """Bar chart widget for showing multiple values"""

    def __init__(self, title="Bar Chart", colors=None):
        self.colors = colors or ["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#ff99cc"]
        super().__init__(title)

    def update_data(self, data_dict):
        """Update bar chart with new data"""
        if not data_dict:
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Prepare data
        labels = list(data_dict.keys())
        values = list(data_dict.values())
        colors = self.colors[: len(labels)]

        # Create bar chart
        bars = ax.bar(labels, values, color=colors)

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.5,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Style the chart
        ax.set_title(self.title, fontsize=12, fontweight="bold")
        ax.set_ylabel("Percentage (%)")
        ax.set_ylim(0, 100)

        # Rotate x-axis labels if needed
        if len(labels) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        # Refresh canvas
        self.canvas.draw()


class GaugeWidget(BaseChartWidget):
    """Gauge widget for showing single values"""

    def __init__(self, title="Gauge", max_value=100):
        self.max_value = max_value
        super().__init__(title)

    def update_data(self, value, label="Value"):
        """Update gauge with new value"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Create gauge
        theta = np.linspace(0, np.pi, 100)

        # Background arc
        ax.plot(np.cos(theta), np.sin(theta), "k-", linewidth=10, alpha=0.3)

        # Value arc
        value_angle = (value / self.max_value) * np.pi
        theta_value = np.linspace(0, value_angle, int(100 * value / self.max_value))

        # Color based on value
        if value < 50:
            color = "green"
        elif value < 80:
            color = "orange"
        else:
            color = "red"

        ax.plot(np.cos(theta_value), np.sin(theta_value), color=color, linewidth=10)

        # Add center text
        ax.text(
            0,
            -0.3,
            f"{value:.1f}%",
            ha="center",
            va="center",
            fontsize=20,
            fontweight="bold",
        )
        ax.text(0, -0.5, label, ha="center", va="center", fontsize=12)

        # Style
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(self.title, fontsize=12, fontweight="bold", pad=20)

        # Refresh canvas
        self.canvas.draw()


class ThermometerWidget(BaseChartWidget):
    """Thermometer widget for showing CPU temperature"""

    def __init__(self, title="CPU Temperature", min_temp=0, max_temp=100):
        self.min_temp = min_temp
        self.max_temp = max_temp
        super().__init__(title)

    def update_data(self, temperature):
        """Update thermometer with new temperature"""
        if temperature is None:
            temperature = 0

        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Thermometer dimensions
        bulb_radius = 0.15
        tube_width = 0.08
        tube_height = 0.7

        # Draw thermometer tube (background)
        tube_x = [
            -tube_width / 2,
            tube_width / 2,
            tube_width / 2,
            -tube_width / 2,
            -tube_width / 2,
        ]
        tube_y = [
            bulb_radius,
            bulb_radius,
            bulb_radius + tube_height,
            bulb_radius + tube_height,
            bulb_radius,
        ]
        ax.plot(tube_x, tube_y, "k-", linewidth=2)
        ax.fill(tube_x, tube_y, color="lightgray", alpha=0.5)

        # Draw bulb (background)
        bulb_circle = plt.Circle((0, 0), bulb_radius, color="lightgray", alpha=0.5)
        ax.add_patch(bulb_circle)
        ax.plot(
            np.cos(np.linspace(0, 2 * np.pi, 100)) * bulb_radius,
            np.sin(np.linspace(0, 2 * np.pi, 100)) * bulb_radius,
            "k-",
            linewidth=2,
        )

        # Calculate mercury level
        temp_ratio = (temperature - self.min_temp) / (self.max_temp - self.min_temp)
        temp_ratio = max(0, min(1, temp_ratio))  # Clamp between 0 and 1
        mercury_height = temp_ratio * tube_height

        # Determine mercury color based on temperature
        if temperature <= 30:
            mercury_color = "#0066cc"  # Blue for cold
        elif temperature <= 50:
            mercury_color = "#00cc00"  # Green for normal
        elif temperature <= 70:
            mercury_color = "#ffcc00"  # Yellow for warm
        elif temperature <= 80:
            mercury_color = "#ff6600"  # Orange for hot
        else:
            mercury_color = "#cc0000"  # Red for very hot

        # Draw mercury in bulb
        mercury_bulb = plt.Circle((0, 0), bulb_radius * 0.8, color=mercury_color)
        ax.add_patch(mercury_bulb)

        # Draw mercury in tube
        if mercury_height > 0:
            mercury_tube_x = [
                -tube_width / 2 * 0.7,
                tube_width / 2 * 0.7,
                tube_width / 2 * 0.7,
                -tube_width / 2 * 0.7,
            ]
            mercury_tube_y = [
                bulb_radius,
                bulb_radius,
                bulb_radius + mercury_height,
                bulb_radius + mercury_height,
            ]
            ax.fill(mercury_tube_x, mercury_tube_y, color=mercury_color)

        # Add temperature scale markings
        for i in range(0, 101, 10):
            y_pos = bulb_radius + (i / 100) * tube_height
            # Right side markings
            ax.plot(
                [tube_width / 2, tube_width / 2 + 0.03],
                [y_pos, y_pos],
                "k-",
                linewidth=1,
            )
            if i % 20 == 0:  # Major markings
                ax.text(
                    tube_width / 2 + 0.06,
                    y_pos,
                    f"{i}°",
                    ha="left",
                    va="center",
                    fontsize=8,
                )

        # Add temperature value display
        ax.text(
            0,
            -0.35,
            f"{temperature:.1f}°C",
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold",
            color=mercury_color,
        )

        # Add status text
        if temperature <= 30:
            status = "Very Cool"
        elif temperature <= 50:
            status = "Normal"
        elif temperature <= 70:
            status = "Warm"
        elif temperature <= 80:
            status = "Hot"
        else:
            status = "Very Hot"

        ax.text(
            0,
            -0.45,
            status,
            ha="center",
            va="center",
            fontsize=10,
            style="italic",
            color=mercury_color,
        )

        # Set axis properties
        ax.set_xlim(-0.3, 0.3)
        ax.set_ylim(-0.5, bulb_radius + tube_height + 0.1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(self.title, fontsize=12, fontweight="bold", pad=20)

        # Refresh canvas
        self.canvas.draw()


class SystemMonitoringWidget(QWidget):
    """Complete system monitoring widget with multiple charts"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the monitoring UI"""
        layout = QVBoxLayout(self)

        # Top row - CPU and Memory pie charts
        top_row = QHBoxLayout()

        self.cpu_pie = PieChartWidget("CPU Usage", ["#ff6b6b", "#4ecdc4"])
        self.memory_pie = PieChartWidget("Memory Usage", ["#45b7d1", "#96ceb4"])

        top_row.addWidget(self.cpu_pie)
        top_row.addWidget(self.memory_pie)

        layout.addLayout(top_row)

        # Middle row - CPU Temperature Thermometer
        middle_row = QHBoxLayout()

        self.cpu_thermometer = ThermometerWidget(
            "CPU Temperature", min_temp=0, max_temp=100
        )

        # Add some spacing widgets to center the thermometer
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        middle_row.addItem(spacer_left)
        middle_row.addWidget(self.cpu_thermometer)
        middle_row.addItem(spacer_right)

        layout.addLayout(middle_row)

        # Bottom row - Disk gauge and Network bar chart
        bottom_row = QHBoxLayout()

        self.disk_gauge = GaugeWidget("Disk Usage")
        self.network_bar = BarChartWidget("Network I/O", ["#ffeaa7", "#fdcb6e"])

        bottom_row.addWidget(self.disk_gauge)
        bottom_row.addWidget(self.network_bar)

        layout.addLayout(bottom_row)

    def update_data(self, system_data):
        """Update all charts with new system data"""
        try:
            # Update CPU pie chart
            cpu_percent = system_data.get("cpu_percent", 0)
            self.cpu_pie.update_data(cpu_percent, "CPU")

            # Update Memory pie chart
            memory_percent = system_data.get("memory_percent", 0)
            self.memory_pie.update_data(memory_percent, "Memory")

            # Update CPU Temperature thermometer
            cpu_temperature = system_data.get("cpu_temperature", 0)
            self.cpu_thermometer.update_data(cpu_temperature)

            # Update Disk gauge
            disk_percent = system_data.get("disk_percent", 0)
            self.disk_gauge.update_data(disk_percent, "Disk")

            # Update Network bar chart
            network_io = system_data.get("network_io", {})
            if network_io:
                bytes_sent = network_io.get("bytes_sent", 0) / 1024  # Convert to KB
                bytes_recv = network_io.get("bytes_recv", 0) / 1024  # Convert to KB
                max_speed = max(
                    bytes_sent, bytes_recv, 100
                )  # Minimum scale of 100 KB/s

                network_data = {
                    "Upload": (bytes_sent / max_speed) * 100,
                    "Download": (bytes_recv / max_speed) * 100,
                }
                self.network_bar.update_data(network_data)

        except Exception as e:
            import logging

            logging.error(f"Error updating chart data: {e}")


class TrendMonitoringWidget(QWidget):
    """Trend monitoring widget with line charts"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the trend monitoring UI"""
        layout = QVBoxLayout(self)

        # CPU trend
        self.cpu_trend = LineChartWidget("CPU Usage Trend")
        layout.addWidget(self.cpu_trend)

        # Memory trend
        self.memory_trend = LineChartWidget("Memory Usage Trend")
        layout.addWidget(self.memory_trend)

    def update_data(self, system_data):
        """Update trend charts with new data"""
        try:
            cpu_percent = system_data.get("cpu_percent", 0)
            memory_percent = system_data.get("memory_percent", 0)

            self.cpu_trend.add_data_point(cpu_percent)
            self.memory_trend.add_data_point(memory_percent)

        except Exception as e:
            import logging

            logging.error(f"Error updating trend data: {e}")


# Set matplotlib style for better looking charts
plt.style.use("seaborn-v0_8")
plt.rcParams["font.size"] = 10
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
