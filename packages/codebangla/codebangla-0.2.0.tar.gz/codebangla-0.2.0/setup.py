#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for CodeBangla - Advanced Python transpiler for Bangla keywords.

This setup script provides backward compatibility for environments that don't
support pyproject.toml. For modern Python packaging, prefer using pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
README_PATH = Path(__file__).parent / "README.md"
with open(README_PATH, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from package
def get_version():
    """Get version from the package."""
    version_file = Path(__file__).parent / "codebangla" / "__init__.py"
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    return "0.2.0"

# Development dependencies
dev_requires = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-benchmark>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "isort>=5.0.0",
    "pre-commit>=2.20.0",
]

# Documentation dependencies
docs_requires = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0",
]

# Performance dependencies
perf_requires = [
    "chardet>=5.0.0",
    "unicodedata2>=14.0.0",
]

setup(
    name="codebangla",
    version=get_version(),
    author="CodeBangla Team",
    author_email="team@codebangla.org",
    description="Advanced Python transpiler for writing Python code using Bangla keywords",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saky-semicolon/codebangla",
    project_urls={
        "Bug Reports": "https://github.com/saky-semicolon/codebangla/issues",
        "Source": "https://github.com/saky-semicolon/codebangla",
        "Documentation": "https://codebangla.readthedocs.io",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    package_data={
        "codebangla": ["py.typed"],
    },
    classifiers=[
        # Development status
        "Development Status :: 4 - Beta",
        
        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Operating system
        "Operating System :: OS Independent",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        
        # Programming language versions
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Topics
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Localization",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        
        # Natural language
        "Natural Language :: Bengali",
        "Natural Language :: English",
        
        # Typing
        "Typing :: Typed",
    ],
    keywords=[
        "bangla", "python", "transpiler", "programming", "education", 
        "localization", "bengali", "compiler", "language", "learning"
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "dev": dev_requires,
        "docs": docs_requires,
        "perf": perf_requires,
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "coverage>=6.0.0",
        ],
        "format": [
            "black>=22.0.0",
            "isort>=5.0.0",
        ],
        "lint": [
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "all": dev_requires + docs_requires + perf_requires,
    },
    entry_points={
        "console_scripts": [
            "codebangla=codebangla.cli:main",
            "bp=codebangla.cli:main",  # Short alias
        ],
    },
    zip_safe=False,  # Required for mypy to find py.typed
    include_package_data=True,
)