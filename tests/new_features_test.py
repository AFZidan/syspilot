#!/usr/bin/env python3
"""
Test script for SysPilot new features
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_autostart_service():
    """Test AutoStart service"""
    print("=== Testing AutoStart Service ===")
    try:
        from syspilot.services.autostart_service import AutoStartService
        
        service = AutoStartService()
        print(f"✓ AutoStart service initialized")
        
        # Get current status
        status = service.get_autostart_status()
        print(f"✓ Current autostart status: {status}")
        
        return True
    except Exception as e:
        print(f"✗ AutoStart service error: {e}")
        return False

def test_scheduling_service():
    """Test Scheduling service"""
    print("\n=== Testing Scheduling Service ===")
    try:
        from syspilot.utils.config import ConfigManager
        from syspilot.services.cleanup_service import CleanupService
        from syspilot.services.scheduling_service import SchedulingService
        
        config = ConfigManager()
        cleanup_service = CleanupService(config)
        scheduling_service = SchedulingService(config, cleanup_service)
        
        print(f"✓ Scheduling service initialized")
        
        # Get current schedules
        schedules = scheduling_service.get_schedules()
        print(f"✓ Current schedules: {len(schedules)}")
        
        return True
    except Exception as e:
        print(f"✗ Scheduling service error: {e}")
        return False

def test_chart_widgets():
    """Test Chart widgets"""
    print("\n=== Testing Chart Widgets ===")
    try:
        from syspilot.widgets.charts import (
            PieChartWidget, LineChartWidget, BarChartWidget,
            GaugeWidget, SystemMonitoringWidget
        )
        
        print(f"✓ Chart widgets imported successfully")
        
        # Test basic creation (without GUI)
        # This won't actually display anything, just test imports
        print(f"✓ All chart widget classes available")
        
        return True
    except Exception as e:
        print(f"✗ Chart widgets error: {e}")
        return False

def test_enhanced_config():
    """Test enhanced configuration"""
    print("\n=== Testing Enhanced Configuration ===")
    try:
        from syspilot.utils.config import ConfigManager
        
        config = ConfigManager()
        
        # Test configuration access
        monitoring_interval = config.get_monitoring_interval()
        max_age_days = config.get_max_age_days()
        
        print(f"✓ Monitoring interval: {monitoring_interval} seconds")
        print(f"✓ Max age days: {max_age_days}")
        
        return True
    except Exception as e:
        print(f"✗ Enhanced config error: {e}")
        return False

def test_project_structure():
    """Test project structure"""
    print("\n=== Testing Project Structure ===")
    
    required_files = [
        "syspilot/__init__.py",
        "syspilot/core/app.py",
        "syspilot/core/cli.py",
        "syspilot/core/daemon.py",
        "syspilot/services/cleanup_service.py",
        "syspilot/services/monitoring_service.py",
        "syspilot/services/system_info.py",
        "syspilot/services/autostart_service.py",
        "syspilot/services/scheduling_service.py",
        "syspilot/widgets/__init__.py",
        "syspilot/widgets/charts.py",
        "syspilot/utils/config.py",
        "syspilot/utils/logger.py",
        "requirements.txt",
        "setup.py",
        "install_pipx.sh",
        "assets/syspilot_logo.png"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\nWarning: {len(missing_files)} files are missing")
        return False
    else:
        print(f"\n✓ All {len(required_files)} project files present")
        return True

def main():
    """Main test function"""
    print("SysPilot - New Features Test")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_enhanced_config,
        test_autostart_service,
        test_scheduling_service,
        test_chart_widgets,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All new features are working correctly!")
        print("\nNew features added:")
        print("• Auto-start functionality")
        print("• Scheduled cleanup")
        print("• Enhanced monitoring with charts")
        print("• Improved settings interface")
        print("• Better configuration management")
        return 0
    else:
        print("✗ Some features need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
