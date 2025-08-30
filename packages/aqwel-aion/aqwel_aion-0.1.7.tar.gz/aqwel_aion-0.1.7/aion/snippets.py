#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 Code Snippets Module
======================================

Advanced code snippet extraction and analysis utilities for AI research projects.
Enhanced in v0.1.7 with improved parsing and code structure analysis.

Features:
- Code comment extraction and intelligent analysis
- Function definition parsing and signature extraction
- Class definition parsing and method extraction
- Code structure analysis and documentation generation
- Snippet organization and intelligent categorization
- Code element identification and extraction tools

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

# Import the regular expression module for pattern matching
import re

def extract_comments(code):
    """
    Extract all comments from the given code using regex pattern matching.
    
    This function searches for Python-style comments (lines starting with #)
    and returns a list of all found comments.
    
    Args:
        code (str): The source code to extract comments from
        
    Returns:
        List[str]: A list of all found comments
    """
    # Use regex to find all lines that start with # (Python comments)
    return re.findall(r'#.*', code)

def extract_functions(code):
    """
    Extract function definitions from the given code using regex pattern matching.
    
    This function searches for Python function definitions (def statements)
    and returns a list of function names.
    
    Args:
        code (str): The source code to extract functions from
        
    Returns:
        List[str]: A list of function names found in the code
    """
    # Use regex to find all function definitions (def function_name(...))
    return re.findall(r'def (.+?)\(', code)

def extract_class_defs(code):
    """
    Extract class definitions from the given code using regex pattern matching.
    
    This function searches for Python class definitions (class statements)
    and returns a list of class names.
    
    Args:
        code (str): The source code to extract classes from
        
    Returns:
        List[str]: A list of class names found in the code
    """
    # Use regex to find all class definitions (class class_name(...))
    return re.findall(r'class (.+?)\(', code)