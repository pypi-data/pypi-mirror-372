"""
Setup script for DevOpsForge
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

import os
from pathlib import Path

# Get the directory containing setup.py
setup_dir = Path(__file__).parent
requirements_file = setup_dir / "requirements.txt"

if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = []

setup(
    name="devopsforge",
    version="0.1.0",
    author="DevOpsForge Team",
    author_email="kumarn7570@gmail.com",
    description="Professional DevOps automation tool that automatically generates CI/CD pipelines, Dockerfiles, and Kubernetes configurations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devopsforge/devopsforge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "devopsforge=devopsforge.cli.main:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
