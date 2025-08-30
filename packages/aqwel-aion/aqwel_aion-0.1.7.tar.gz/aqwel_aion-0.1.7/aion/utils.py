#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 Utilities Module
===================================

Advanced utility functions and helper tools for AI research projects.
Enhanced in v0.1.7 with additional data processing and validation capabilities.

Features:
- Data formatting and conversion utilities
- String manipulation and validation functions
- Random data generation and UUID creation
- Hash generation and cryptographic functions
- Number processing and mathematical utilities
- Data validation and sanitization tools

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

# Import the regular expression module for pattern matching
import re

# Import the uuid module for generating unique identifiers
import uuid

# Import the hashlib module for cryptographic hash functions
import hashlib

def format_bytes(size):
    """
    Format a byte size into a human-readable string with appropriate units.
    
    This function converts bytes into KB, MB, GB, etc. with proper
    formatting and rounding to 2 decimal places.
    
    Args:
        size (int): The size in bytes to format
        
    Returns:
        str: A formatted string with the size and appropriate unit
    """
    # Define the units for byte conversion
    for unit in ['B', 'KB', 'MB', 'GB']:
        # Check if the size is less than 1024 (next unit threshold)
        if size < 1024:
            # Return the formatted size with the current unit
            return f"{size:.2f} {unit}"
        # Divide by 1024 to convert to the next unit
        size /= 1024

def format_duration(seconds):
    """
    Format a duration in seconds into a human-readable string.
    
    This function converts seconds into minutes and seconds format
    for better readability.
    
    Args:
        seconds (int): The duration in seconds to format
        
    Returns:
        str: A formatted string showing minutes and seconds
    """
    # Convert seconds to minutes and remaining seconds
    minutes, seconds = divmod(seconds, 60)
    
    # Return the formatted duration string
    return f"{minutes} min {seconds} sec"

def random_string(length=8):
    """
    Generate a random string of specified length using letters and digits.
    
    This function creates a cryptographically secure random string
    that can be used for temporary identifiers or tokens.
    
    Args:
        length (int): The length of the random string to generate (default: 8)
        
    Returns:
        str: A random string of the specified length
    """
    # Import required modules for random string generation
    import random, string
    
    # Generate random string using letters and digits
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def slugify(text):
    """
    Convert text into a URL-friendly slug format.
    
    This function converts text to lowercase, removes extra whitespace,
    and replaces spaces with hyphens for use in URLs or filenames.
    
    Args:
        text (str): The text to convert to slug format
        
    Returns:
        str: A URL-friendly slug version of the text
    """
    # Convert to lowercase, strip whitespace, and replace spaces with hyphens
    return text.strip().lower().replace(" ", "-")

def is_valid_email(email):
    """
    Validate if the given string is a properly formatted email address.
    
    This function uses regex pattern matching to check if the email
    follows the basic email format (local@domain).
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if the email is valid, False otherwise
    """
    # Use regex to check if the email matches the basic email pattern
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def generate_uuid():
    """
    Generate a new UUID (Universally Unique Identifier).
    
    This function creates a new UUID4 which is cryptographically
    random and suitable for unique identifiers.
    
    Args:
        None
        
    Returns:
        str: A new UUID string
    """
    # Generate and return a new UUID4 as a string
    return str(uuid.uuid4())

def md5_hash(text):
    """
    Generate an MD5 hash of the given text.
    
    This function creates an MD5 hash of the input text, which can be
    used for data integrity checks or as a simple fingerprint.
    
    Args:
        text (str): The text to hash
        
    Returns:
        str: The hexadecimal MD5 hash of the text
    """
    # Encode text as UTF-8 bytes and generate MD5 hash
    return hashlib.md5(text.encode()).hexdigest()

def get_even_numbers(numbers):
    """
    Filter a list of numbers to return only even numbers.
    
    This function uses list comprehension to filter out odd numbers
    and return only the even numbers from the input list.
    
    Args:
        numbers (List[int]): The list of numbers to filter
        
    Returns:
        List[int]: A list containing only the even numbers
    """
    # Use list comprehension to filter even numbers (divisible by 2)
    return [n for n in numbers if n % 2 == 0]

def get_odd_numbers(numbers):
    """
    Filter a list of numbers to return only odd numbers.
    
    This function uses list comprehension to filter out even numbers
    and return only the odd numbers from the input list.
    
    Args:
        numbers (List[int]): The list of numbers to filter
        
    Returns:
        List[int]: A list containing only the odd numbers
    """
    # Use list comprehension to filter odd numbers (not divisible by 2)
    return [n for n in numbers if n % 2 != 0]