#!/usr/bin/env python3
"""
Setup script for LRDBench package
"""

import os
import re
from setuptools import setup, find_packages

def get_version():
    """Extract version from pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        content = f.read()
        match = re.search(r'version = "([^"]+)"', content)
        if match:
            return match.group(1)
    return "1.5.1"  # fallback

def get_long_description():
    """Read README.md for long description"""
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

setup(
    name="lrdbench",
    version=get_version(),
    description="Long-Range Dependence Benchmarking Toolkit",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="LRDBench Development Team",
    author_email="lrdbench@example.com",
    url="https://github.com/dave2k77/LRDBenchmark",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "torch>=1.9.0",
        "jax>=0.3.0",
        "jaxlib>=0.3.0",
        "numba>=0.56.0",
        "pywavelets>=1.3.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "psutil>=5.8.0",
        "networkx>=2.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.12",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "lrdbench=lrdbench.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
