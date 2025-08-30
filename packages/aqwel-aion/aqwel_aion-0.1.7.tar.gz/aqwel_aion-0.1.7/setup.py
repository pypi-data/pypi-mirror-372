#!/usr/bin/env python3
"""
Setup script for Aqwel-Aion v0.1.7
Professional AI Research & Development Library

Author: Aksel Aghajanyan
Copyright: 2025 Aqwel AI
License: Apache-2.0
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aqwel-aion",
    version="0.1.7",
    author="Aksel Aghajanyan",
    author_email="aqwelaiofficial@gmail.com",
    description="🚀 Complete AI Research & Development Library with Advanced Mathematics and ML Tools",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://aqwelai.com/#aqwel-aion",
    project_urls={
        "Homepage": "https://aqwelai.com/#aqwel-aion",
        "Documentation": "https://aqwelai.com/docs/aion",
        "Repository": "https://github.com/aqwelai/aion",
        "Bug Tracker": "https://github.com/aqwelai/aion/issues",
        "PyPI": "https://pypi.org/project/aqwel-aion/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords=[
        "ai-research", "machine-learning", "mathematics", "statistics", 
        "data-science", "embeddings", "neural-networks", "deep-learning",
        "scientific-computing", "research-tools", "aqwel-ai"
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "watchdog>=2.1.0",
        "gitpython>=3.1.0",
    ],
    extras_require={
        "ai": [
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0",
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "sentence-transformers>=2.2.0",
        ],
        "docs": [
            "reportlab>=3.6.0",
            "pillow>=8.0.0",
        ],
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "full": [
            "scipy>=1.7.0",
            "scikit-learn>=1.0.0", 
            "pandas>=1.3.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "openai>=1.0.0",
            "faiss-cpu>=1.7.0",
            "sentence-transformers>=2.2.0",
            "reportlab>=3.6.0",
            "pillow>=8.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "aion=aion.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license="Apache-2.0",
)