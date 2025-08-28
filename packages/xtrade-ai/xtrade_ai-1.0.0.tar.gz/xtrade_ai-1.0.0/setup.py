#!/usr/bin/env python3
"""
Setup script for XTrade-AI Framework
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def read_readme():
    """Read README.md file."""
    readme_path = project_root / "README.md"
    if readme_path.exists():
        return readme_path.read_text(encoding="utf-8")
    return ""

def read_requirements(filename):
    """Read requirements file."""
    requirements_path = project_root / "requirements" / filename
    if requirements_path.exists():
        return [
            line.strip()
            for line in requirements_path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        ]
    return []

if __name__ == "__main__":
    # Read README
    long_description = read_readme()
    
    # Read base requirements
    install_requires = read_requirements("base.txt")
    
    setup(
        name="xtrade-ai",
        version="1.0.0",
        description="A comprehensive reinforcement learning framework for algorithmic trading",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="Anas Amu",
        author_email="anasamu7@gmail.com",
        url="https://github.com/anasamu/xtrade-ai-framework",
        project_urls={
            "Bug Tracker": "https://github.com/anasamu/xtrade-ai-framework/issues",
            "Documentation": "https://xtrade-ai-framework.readthedocs.io/en/latest/",
            "Source Code": "https://github.com/anasamu/xtrade-ai-framework",
        },
        packages=["xtrade_ai"],
        package_dir={"": "."},
        include_package_data=True,
        python_requires=">=3.8",
        install_requires=install_requires,
        extras_require={
            "ta": read_requirements("ta.txt") if (project_root / "requirements" / "ta.txt").exists() else [],
            "dev": read_requirements("dev.txt") if (project_root / "requirements" / "dev.txt").exists() else [],
            "viz": read_requirements("viz.txt") if (project_root / "requirements" / "viz.txt").exists() else [],
            "monitor": read_requirements("monitor.txt") if (project_root / "requirements" / "monitor.txt").exists() else [],
            "performance": read_requirements("performance.txt") if (project_root / "requirements" / "performance.txt").exists() else [],
            "database": read_requirements("database.txt") if (project_root / "requirements" / "database.txt").exists() else [],
            "api": read_requirements("api.txt") if (project_root / "requirements" / "api.txt").exists() else [],
        },
        entry_points={
            "console_scripts": [
                "xtrade-ai=xtrade_ai.cli:cli",
            ],
        },
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Financial and Insurance Industry",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Office/Business :: Financial :: Investment",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        keywords=[
            "trading", "ai", "machine-learning", "reinforcement-learning", 
            "algorithmic-trading", "finance", "investment"
        ],
        license="MIT",
        zip_safe=False,
    )
