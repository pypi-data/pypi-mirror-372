#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 - Complete AI Research & Development Library
==============================================================

A comprehensive Python utility library by Aqwel AI for AI research,
machine learning development, and advanced data science workflows.

This package provides:
- Complete mathematical and statistical operations (71+ functions)
- Advanced machine learning utilities and model evaluation
- Text embeddings and AI prompt engineering tools
- Professional documentation generation system
- Code analysis and quality assessment tools
- File management and real-time monitoring
- Git integration and version control utilities

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI

For documentation and examples, visit:
https://aqwelai.com/#aqwel-aion
"""

# Define the current version of the package
__version__ = "0.1.7"

# Define the author information
__author__ = "Aksel Aghajanyan"

# Define the contact email for the package
__email__ = "aqwelaiofficial@gmail.com"

# Define the license type for the package
__license__ = "Apache-2.0"

# Define the copyright information
__copyright__ = "2025 Aqwel AI"

# Import the text processing module for text analysis and manipulation
from . import text

# Import the file management module for file operations and organization
from . import files

# Import the code parsing module for language detection and code analysis
from . import parser

# Import the file watching module for real-time file monitoring
from . import watcher

# Import the utilities module for general helper functions
from . import utils

# Import the command-line interface module for CLI functionality
from . import cli

# Import the Git integration module for repository management
from . import git

# Import the mathematics and statistics module for numerical computations
from . import maths

# Import additional AI/ML modules
from . import code
from . import embed
from . import evaluate
from . import prompt
from . import snippets
from . import pdf

# Define the public API exports for the package
__all__ = [
    "__version__",      # Version information
    "__author__",       # Author information
    "__email__",        # Contact email
    "__license__",      # License information
    "__copyright__",    # Copyright information
    "text",             # Text processing module
    "files",            # File management module
    "parser",           # Code parsing module
    "watcher",          # File watching module
    "utils",            # Utilities module
    "cli",              # Command-line interface module
    "git",              # Git integration module
    "maths",            # Mathematics and statistics module
    "code",             # Code analysis module
    "embed",            # Embedding utilities module
    "evaluate",         # Evaluation metrics module
    "prompt",           # Prompt management module
    "snippets",         # Code snippets module
    "pdf"               # PDF documentation module
]