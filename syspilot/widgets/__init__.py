"""
Widgets package for SysPilot
Contains custom widgets and chart components
"""

# Optional chart widgets that require matplotlib
try:
    from .charts import (
        BarChartWidget,
        GaugeWidget,
        LineChartWidget,
        PieChartWidget,
        SystemMonitoringWidget,
        TrendMonitoringWidget,
    )

    __all__ = [
        "PieChartWidget",
        "LineChartWidget",
        "BarChartWidget",
        "GaugeWidget",
        "SystemMonitoringWidget",
        "TrendMonitoringWidget",
    ]
except ImportError:
    # Charts not available without matplotlib
    __all__ = []
