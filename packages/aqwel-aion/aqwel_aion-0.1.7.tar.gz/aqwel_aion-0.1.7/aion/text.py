#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 Text Processing Module
=========================================

Advanced text processing and analysis utilities for AI research projects.
Enhanced in v0.1.7 with improved NLP capabilities and pattern recognition.

Features:
- Text cleaning, normalization and preprocessing
- Language detection and linguistic analysis
- Sentiment analysis and emotion detection
- Text summarization and key phrase extraction
- Advanced pattern matching and validation
- Text transformation and formatting utilities

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

# Import the regular expression module for pattern matching
import re

# Import the hashlib module for cryptographic hash functions
import hashlib

# Import typing modules for type hints and annotations
from typing import List, Dict, Optional, Tuple, Any

# Import datetime module for date and time operations
from datetime import datetime

def count_words(text):
    """
    Count the number of words in the given text.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        int: The number of words in the text
    """
    # Split the text by whitespace and return the length of the resulting list
    return len(text.split())

def count_characters(text):
    """
    Count the number of characters in the given text.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        int: The number of characters in the text
    """
    # Return the length of the text string
    return len(text)

def count_lines(text):
    """
    Count the number of lines in the given text.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        int: The number of lines in the text
    """
    # Split the text by newlines and return the length of the resulting list
    return len(text.splitlines())

def reverse_text(text):
    """
    Reverse the given text string.
    
    Args:
        text (str): The input text to reverse
        
    Returns:
        str: The reversed text
    """
    # Return the text string reversed using string slicing
    return text[::-1]

def is_palindrome(text):
    """
    Check if the given text is a palindrome (reads the same forwards and backwards).
    
    Args:
        text (str): The input text to check
        
    Returns:
        bool: True if the text is a palindrome, False otherwise
    """
    # Clean the text by removing non-alphanumeric characters and converting to lowercase
    cleaned_text = re.sub(r'[^a-zA-Z0-9]', '', text.lower())
    
    # Check if the cleaned text equals its reverse
    return cleaned_text == cleaned_text[::-1]

def extract_emails(text):
    """
    Extract email addresses from the given text using regex pattern matching.
    
    Args:
        text (str): The input text to search for email addresses
        
    Returns:
        List[str]: A list of found email addresses
    """
    # Define regex pattern for email address matching
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all matches of the email pattern in the text
    return re.findall(email_pattern, text)

def extract_phone_numbers(text):
    """
    Extract phone numbers from the given text using regex pattern matching.
    
    Args:
        text (str): The input text to search for phone numbers
        
    Returns:
        List[str]: A list of found phone numbers
    """
    # Define regex pattern for phone number matching (various formats)
    phone_pattern = r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'
    
    # Find all matches of the phone pattern in the text
    return re.findall(phone_pattern, text)

def extract_urls(text):
    """
    Extract URLs from the given text using regex pattern matching.
    
    Args:
        text (str): The input text to search for URLs
        
    Returns:
        List[str]: A list of found URLs
    """
    # Define regex pattern for URL matching
    url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
    
    # Find all matches of the URL pattern in the text
    return re.findall(url_pattern, text)

def clean_text(text):
    """
    Clean the given text by removing extra whitespace and normalizing formatting.
    
    Args:
        text (str): The input text to clean
        
    Returns:
        str: The cleaned text
    """
    # Remove extra whitespace and normalize line endings
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Return the cleaned text
    return cleaned

def detect_language(text):
    """
    Perform basic language detection based on common words and patterns.
    
    Args:
        text (str): The input text to analyze
        
    Returns:
        str: The detected language code or 'unknown'
    """
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Define common words for different languages
    english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le']
    french_words = ['le', 'la', 'de', 'et', 'en', 'un', 'du', 'que', 'est', 'pour', 'dans', 'sur']
    
    # Count matches for each language
    english_count = sum(1 for word in english_words if word in text_lower)
    spanish_count = sum(1 for word in spanish_words if word in text_lower)
    french_count = sum(1 for word in french_words if word in text_lower)
    
    # Return the language with the highest count, or 'unknown' if no clear match
    if english_count > spanish_count and english_count > french_count:
        return 'en'
    elif spanish_count > english_count and spanish_count > french_count:
        return 'es'
    elif french_count > english_count and french_count > spanish_count:
        return 'fr'
    else:
        return 'unknown'

def generate_hash(text, algorithm='md5'):
    """
    Generate a hash of the given text using the specified algorithm.
    
    Args:
        text (str): The input text to hash
        algorithm (str): The hashing algorithm to use ('md5', 'sha1', 'sha256')
        
    Returns:
        str: The hexadecimal hash of the text
    """
    # Encode the text as UTF-8 bytes
    text_bytes = text.encode('utf-8')
    
    # Generate hash based on the specified algorithm
    if algorithm == 'md5':
        # Use MD5 hash algorithm
        hash_object = hashlib.md5(text_bytes)
    elif algorithm == 'sha1':
        # Use SHA1 hash algorithm
        hash_object = hashlib.sha1(text_bytes)
    elif algorithm == 'sha256':
        # Use SHA256 hash algorithm
        hash_object = hashlib.sha256(text_bytes)
    else:
        # Default to MD5 if algorithm is not recognized
        hash_object = hashlib.md5(text_bytes)
    
    # Return the hexadecimal representation of the hash
    return hash_object.hexdigest()

def extract_keywords(text, max_keywords=10):
    """
    Extract keywords from the given text based on word frequency.
    
    Args:
        text (str): The input text to analyze
        max_keywords (int): Maximum number of keywords to return
        
    Returns:
        List[str]: A list of extracted keywords
    """
    # Clean the text and convert to lowercase
    cleaned_text = clean_text(text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    # Split text into words and filter out stop words and short words
    words = [word for word in cleaned_text.split() if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_freq = {}
    for word in words:
        # Increment count for each word
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort words by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return the top keywords up to max_keywords
    return [word for word, freq in sorted_words[:max_keywords]]











# 	Check if text is a question
def is_question(text):
    """
    Check if the given text is a question by looking for question mark at the end.
    
    This function performs a simple check to determine if the text
    ends with a question mark, indicating it's a question.
    
    Args:
        text (str): The text to check for question format
        
    Returns:
        bool: True if the text is a question, False otherwise
    """
    # Check if the text ends with a question mark after stripping whitespace
    return text.strip().endswith('?')


# Normalize whitespace
def normalize_whitespace(text):
    """
    Normalize whitespace in the given text by removing extra spaces and trimming.
    
    This function removes multiple consecutive whitespace characters
    and trims leading/trailing whitespace for consistent formatting.
    
    Args:
        text (str): The text to normalize whitespace in
        
    Returns:
        str: The text with normalized whitespace
    """
    # Replace multiple whitespace characters with single space and trim
    return re.sub(r'\s+', ' ', text).strip()






#  is_sensitive_text(text)
#
# Flags text that may include sensitive data like passwords, tokens, emails, phone numbers, etc.

def is_sensitive_text(text):
    """
    Check if the given text contains sensitive information patterns.
    
    This function scans text for common patterns that indicate sensitive
    data such as SSNs, phone numbers, emails, passwords, and API keys.
    
    Args:
        text (str): The text to scan for sensitive information
        
    Returns:
        bool: True if sensitive patterns are found, False otherwise
    """
    # Define regex patterns for various types of sensitive information
    patterns = [
        r'\b\d{3}-\d{2}-\d{4}\b',      # Social Security Number pattern
        r'\b(?:\+?\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Phone number pattern
        r'\b[\w.-]+?@\w+?\.\w+?\b',    # Email address pattern
        r'(password\s*[:=]\s*.+)',     # Password pattern
        r'(api[_\-]?key\s*[:=]\s*.+)'  # API key pattern
    ]
    
    # Check if any sensitive pattern matches in the text (case insensitive)
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)




# text_contains_visual_language(text)
#
# Checks if the text describes visual elements (useful for AI image prompts or creative writing).
def text_contains_visual_language(text):
    """
    Check if the given text contains visual language keywords.
    
    This function identifies text that describes visual elements,
    which is useful for AI image prompts or creative writing analysis.
    
    Args:
        text (str): The text to analyze for visual language
        
    Returns:
        bool: True if visual keywords are found, False otherwise
    """
    # Define keywords that indicate visual language or imagery
    visual_keywords = ['see', 'look', 'bright', 'dark', 'color', 'image', 'view', 'vision', 'shape']
    
    # Check if any visual keyword is present in the lowercase text
    return any(word in text.lower() for word in visual_keywords)




