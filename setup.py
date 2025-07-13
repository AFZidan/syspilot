#!/usr/bin/env python3
"""
SysPilot Setup Script
"""

import os

from setuptools import find_packages, setup

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
requirements = []
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    # Fallback to minimal requirements if file not found during build
    requirements = [
        "psutil>=5.9.0",
        "PyQt5>=5.15.9",
        "matplotlib>=3.7.0",
        "Pillow>=10.0.0",
        "schedule>=1.2.0",
        "requests>=2.31.0",
    ]

setup(
    name="syspilot",
    version="1.0.0",
    author="SysPilot Team",
    author_email="contact@syspilot.org",
    description="Professional System Automation & Cleanup Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AFZidan/syspilot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "syspilot=syspilot.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "syspilot": ["assets/*", "config/*", "scripts/*"],
    },
    data_files=[
        ("share/applications", ["assets/syspilot.desktop"]),
        ("share/icons/hicolor/48x48/apps", ["assets/syspilot_icon.png"]),
        ("share/icons/hicolor/scalable/apps", ["assets/syspilot_logo.png"]),
    ],
)
