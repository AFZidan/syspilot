#!/usr/bin/env python3
"""
SysPilot - Professional System Automation & Cleanup Tool
Main entry point for the package
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from syspilot.core.app import SysPilotApp
from syspilot.core.cli import SysPilotCLI
from syspilot.core.daemon import SysPilotDaemon
from syspilot.utils.logger import setup_logging


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="SysPilot - Professional System Automation & Cleanup Tool"
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    parser.add_argument(
        "--daemon", action="store_true", help="Run as background daemon"
    )
    parser.add_argument(
        "--clean-temp", action="store_true", help="Clean temporary files only"
    )
    parser.add_argument(
        "--system-info", action="store_true", help="Show system information"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--config", type=str, help="Path to configuration file")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)

    try:
        if args.daemon:
            # Run as daemon
            daemon = SysPilotDaemon(config_path=args.config)
            daemon.run()
        elif args.cli or args.clean_temp or args.system_info:
            # Run in CLI mode
            cli = SysPilotCLI(config_path=args.config)
            if args.clean_temp:
                cli.clean_temp()
            elif args.system_info:
                cli.show_system_info()
            else:
                cli.run()
        else:
            # Run GUI mode
            app = SysPilotApp(config_path=args.config)
            app.run()
    except KeyboardInterrupt:
        logging.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
