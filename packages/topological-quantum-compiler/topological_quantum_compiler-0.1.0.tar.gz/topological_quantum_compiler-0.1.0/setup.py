#!/usr/bin/env python3
"""Setup script for Topological Quantum Compiler (TQC)."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from _version.py
version_file = os.path.join(this_directory, 'src', 'tqc', '_version.py')
version_dict = {}
with open(version_file) as f:
    exec(f.read(), version_dict)

setup(
    name="topological-quantum-compiler",
    version=version_dict['__version__'],
    author="Krishna Bajpai",
    author_email="krishna@krishnabajpai.me",
    description="A universal compiler for quantum computers based on topological principles and anyonic braiding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krish567366/TQC",
    project_urls={
        "Bug Tracker": "https://github.com/krish567366/TQC/issues",
        "Documentation": "https://krish567366.github.io/TQC",
        "Source Code": "https://github.com/krish567366/TQC",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.9.0",
        "networkx>=2.8",
        "matplotlib>=3.5.0",
        "qiskit>=0.40.0",
        "sympy>=1.10",
        "pydantic>=1.10.0",
    ],
    extras_require={
        "jax": ["jax[cpu]>=0.4.0", "jaxlib>=0.4.0"],
        "simulation": ["jax[cpu]>=0.4.0", "jaxlib>=0.4.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs-material>=9.2.0",
            "mkdocstrings[python]>=0.22.0",
            "mkdocs-git-revision-date-localized-plugin>=1.2.0",
        ],
        "all": [
            "jax[cpu]>=0.4.0",
            "jaxlib>=0.4.0",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "mypy>=1.5.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "pre-commit>=3.3.0",
            "mkdocs-material>=9.2.0",
            "mkdocstrings[python]>=0.22.0",
            "mkdocs-git-revision-date-localized-plugin>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tqc=tqc.cli:main",
        ],
    },
    keywords="quantum topological compiler anyons braids fault-tolerant",
    include_package_data=True,
    zip_safe=False,
)
